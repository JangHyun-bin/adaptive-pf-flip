#!/usr/bin/env python
"""Consume an LSFS Mitsuba light-response contract into XML area emitters."""

import argparse
import copy
import math
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from composite_mitsuba_secondary_layer import parse_camera, project


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def selected_frames(frames, requested=None):
    if not frames:
        return []
    if requested is None or requested <= 0 or requested >= len(frames):
        return frames
    if requested == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(requested - 1)) for i in range(requested)))
    return [frames[index] for index in indices]


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def fmt(value):
    return f"{float(value):.8g}"


def csv3(values):
    return ", ".join(fmt(item) for item in values)


def parse_vec3(value, label):
    parts = [float(part.strip()) for part in str(value).split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{label} must be r,g,b")
    return parts


def read_obj_vertices(path, stride):
    vertices = []
    stride = max(1, int(stride))
    seen = 0
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("v "):
                continue
            seen += 1
            if (seen - 1) % stride != 0:
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return vertices


def frame_path(frame, key):
    entry = frame.get(key) or {}
    return entry.get("path") or entry.get("repo_path")


def localize_anchor(anchor, vertices, camera, args):
    width = int(camera.get("width") or 960)
    height = int(camera.get("height") or 540)
    cx, cy = anchor.get("centroid_px") or [width * 0.5, height * 0.5]
    x0, y0, x1, y1 = anchor.get("bbox_px") or [cx, cy, cx, cy]
    pad = float(args.bbox_pad)
    x0 -= pad
    y0 -= pad
    x1 += pad
    y1 += pad
    candidates = []
    nearest = None
    for vertex in vertices:
        projected = project(vertex, camera, width, height)
        if projected is None:
            continue
        px, py, depth = projected
        dist = math.hypot(px - cx, py - cy)
        inside = x0 <= px <= x1 and y0 <= py <= y1
        score = dist + (0.0 if inside else args.outside_bbox_penalty)
        item = {
            "position": vertex,
            "screen": [px, py],
            "depth": depth,
            "screen_distance": dist,
            "inside_bbox": inside,
            "score": score,
        }
        if nearest is None or item["screen_distance"] < nearest["screen_distance"]:
            nearest = item
        if inside or dist <= args.max_nearest_screen_distance:
            candidates.append(item)
    if not candidates and nearest and nearest["screen_distance"] <= args.max_nearest_screen_distance:
        candidates.append(nearest)
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item["score"], item["screen_distance"], item["depth"]))
    chosen = candidates[:max(1, args.world_average_count)]
    weight_sum = 0.0
    center = [0.0, 0.0, 0.0]
    for item in chosen:
        weight = 1.0 / max(1.0, item["screen_distance"])
        weight_sum += weight
        for axis in range(3):
            center[axis] += item["position"][axis] * weight
    center = [value / max(1.0e-12, weight_sum) for value in center]
    response = anchor.get("suggested_response") or {}
    anchor_weight = float(response.get("weight") or 0.0)
    luma_scale = float(response.get("luma_scale") or 1.0)
    radius = args.radius * (args.radius_weight_base + args.radius_weight_scale * anchor_weight)
    radius = max(args.min_radius, min(args.max_radius, radius))
    radiance_scale = args.radiance_scale * max(0.0, luma_scale) * (
        args.radiance_weight_base + args.radiance_weight_scale * anchor_weight
    )
    return {
        "position": [center[0], center[1] + args.y_lift, center[2]],
        "radius": radius,
        "radiance": [channel * radiance_scale for channel in args.radiance_vec],
        "anchor_weight": anchor_weight,
        "luma_scale": luma_scale,
        "candidate_vertices": len(candidates),
        "nearest_screen_distance": candidates[0]["screen_distance"],
        "inside_bbox": any(item["inside_bbox"] for item in candidates),
        "source_anchor": {
            "centroid_px": anchor.get("centroid_px"),
            "bbox_px": anchor.get("bbox_px"),
            "coverage": anchor.get("coverage"),
            "source_luma_mean": anchor.get("source_luma_mean"),
            "source_luma_max": anchor.get("source_luma_max"),
        },
    }


def emitter_block(lights, frame_index):
    lines = []
    for index, light in enumerate(lights):
        x, y, z = light["position"]
        lines.extend([
            f'  <shape type="sphere" id="lsfs_s442_light_response_{frame_index:04d}_{index:03d}">',
            f'    <point name="center" x="{fmt(x)}" y="{fmt(y)}" z="{fmt(z)}"/>',
            f'    <float name="radius" value="{fmt(light["radius"])}"/>',
            '    <emitter type="area">',
            f'      <rgb name="radiance" value="{csv3(light["radiance"])}"/>',
            '    </emitter>',
            '  </shape>',
        ])
    return "\n".join(lines)


def insert_before_scene_end(xml_text, block):
    if not block:
        return xml_text
    marker = "</scene>"
    index = xml_text.rfind(marker)
    if index < 0:
        raise ValueError("missing </scene> marker")
    return xml_text[:index] + block + "\n" + xml_text[index:]


def add_response_comment(xml_text, comment):
    if xml_text.startswith("<?xml"):
        line_end = xml_text.find("\n")
        if line_end >= 0:
            return xml_text[:line_end + 1] + comment + "\n" + xml_text[line_end + 1:]
    return comment + "\n" + xml_text


def write_command_list(path, frames, command, mode):
    mode_arg = f" -m {mode}" if mode else ""
    lines = []
    for frame in frames:
        xml_scene = (frame.get("xml_scene") or {}).get("repo_path")
        output = (frame.get("expected_output") or {}).get("repo_path")
        lines.append(f'{command}{mode_arg} "{xml_scene}" -o "{output}"')
    write_text(path, "\n".join(lines) + "\n")


def source_entry(path, root, label, payload=None):
    entry = {
        "label": label,
        "path": os.path.abspath(path),
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
    return entry


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks") or {}
    response = export.get("light_response_contract_consumer") or {}
    lines = [
        f"# {export['title']}",
        "",
        f"Generated UTC: `{export['generated_utc']}`",
        f"Export JSON: `{posix_rel(export_path, root)}`",
        f"Status: `{export['status']}`",
        "",
        "## Inputs",
        "",
        f"- Base export: `{export['sources']['base_export']['repo_path']}`",
        f"- Light contract: `{export['sources']['light_response_contract']['repo_path']}`",
        "",
        "## Light Response",
        "",
        f"- Anchor limit: `{response.get('anchor_limit')}`",
        f"- Radius range: `{response.get('min_radius')}..{response.get('max_radius')}`",
        f"- Base radiance: `{response.get('radiance')}`",
        f"- Radiance scale: `{response.get('radiance_scale')}`",
        f"- Vertex stride: `{response.get('vertex_stride')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Contract frames matched: `{checks.get('contract_frames_matched')}`",
        f"- Anchors consumed: `{checks.get('anchors_consumed')}`",
        f"- Lights inserted: `{checks.get('lights_inserted')}`",
        f"- Localized anchors: `{checks.get('localized_anchors')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Anchors | Lights | Vertices | XML Scene |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("light_response_contract") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('anchors_available')} | "
            f"{item.get('lights_inserted')} | {item.get('vertices_tested')} | "
            f"`{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    contract_path = require_file(args.light_response_contract, "light response contract")
    base = read_json(base_export_path)
    contract = read_json(contract_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if contract.get("schema") != "lsfs_mitsuba_light_response_contract":
        raise SystemExit(f"{args.light_response_contract}: expected lsfs_mitsuba_light_response_contract schema")
    if contract.get("status") != "ready":
        raise SystemExit(f"{args.light_response_contract}: contract status is {contract.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    contract_frames = output_frame_map(contract.get("frames") or [])
    frames = []
    failures = []
    mesh_cache = {}
    totals = {
        "xml_scene_bytes": 0,
        "contract_frames_matched": 0,
        "anchors_consumed": 0,
        "lights_inserted": 0,
        "localized_anchors": 0,
        "vertices_tested": 0,
    }
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        contract_frame = contract_frames.get(output_frame)
        source_xml = resolve_path(frame_path(frame, "xml_scene"))
        water_mesh = resolve_path(frame_path(frame, "water_mesh"))
        missing = []
        for role, path in (("source_xml", source_xml), ("water_mesh", water_mesh)):
            if not path or not os.path.isfile(path):
                missing.append({"role": role, "path": path})
        if contract_frame is None:
            missing.append({"role": "contract_frame", "path": f"output_frame={output_frame}"})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue
        if water_mesh not in mesh_cache:
            mesh_cache[water_mesh] = read_obj_vertices(water_mesh, args.vertex_stride)
        vertices = mesh_cache[water_mesh]
        camera = parse_camera(source_xml)
        anchors = (contract_frame.get("anchors") or [])[:args.anchor_limit]
        lights = []
        for anchor in anchors:
            localized = localize_anchor(anchor, vertices, camera, args)
            totals["anchors_consumed"] += 1
            if not localized:
                continue
            totals["localized_anchors"] += 1
            lights.append(localized)
        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        patched = insert_before_scene_end(xml_text, emitter_block(lights, index))
        patched = add_response_comment(
            patched,
            f"<!-- S442 light_response_contract lights={len(lights)} anchors={len(anchors)} -->",
        )
        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["contract_frames_matched"] += 1
        totals["lights_inserted"] += len(lights)
        totals["vertices_tested"] += len(vertices)
        out_frame = copy.deepcopy(frame)
        out_frame["xml_scene"] = {
            "path": xml_out,
            "repo_path": posix_rel(xml_out, root),
            "sha256": sha256_file(xml_out),
            "size": os.path.getsize(xml_out),
        }
        expected = os.path.join(render_dir, f"{base_name}.exr")
        out_frame["expected_output"] = {
            "path": expected,
            "repo_path": posix_rel(expected, root),
        }
        out_frame["light_response_contract"] = {
            "enabled": True,
            "contract_output_frame": output_frame,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "vertices_tested": len(vertices),
            "anchors_available": len(anchors),
            "lights_inserted": len(lights),
            "lights": lights[:8],
        }
        frames.append(out_frame)

    command_list = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_command_list(
        command_list,
        frames,
        (base.get("render_settings") or {}).get("mitsuba_command") or "mitsuba",
        (base.get("render_settings") or {}).get("mitsuba_mode"),
    )
    status = "ready" if frames and not failures and totals["lights_inserted"] > 0 else "review"
    export = copy.deepcopy(base)
    export.update({
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "light_response_contract": source_entry(contract_path, root, "light response contract", contract),
        },
        "frames": frames,
        "failures": failures,
        "light_response_contract_consumer": {
            "enabled": True,
            "anchor_limit": args.anchor_limit,
            "vertex_stride": args.vertex_stride,
            "bbox_pad": args.bbox_pad,
            "max_nearest_screen_distance": args.max_nearest_screen_distance,
            "world_average_count": args.world_average_count,
            "radius": args.radius,
            "min_radius": args.min_radius,
            "max_radius": args.max_radius,
            "y_lift": args.y_lift,
            "radiance": args.radiance_vec,
            "radiance_scale": args.radiance_scale,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["light_response_contract_enabled"] = True
    export["checks"] = copy.deepcopy(base.get("checks") or {})
    export["checks"].update({
        "frames_exported": len(frames),
        "missing_references": len(failures),
        **totals,
    })
    export_path = os.path.join(out_dir, "mitsuba_export.json")
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root, args.next))
    print(
        f"status={status} frames={len(frames)} lights={totals['lights_inserted']} "
        f"localized={totals['localized_anchors']} export={export_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consume an LSFS Mitsuba light-response contract into XML area emitters")
    parser.add_argument("base_export")
    parser.add_argument("light_response_contract")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--anchor-limit", type=int, default=8)
    parser.add_argument("--vertex-stride", type=int, default=1)
    parser.add_argument("--bbox-pad", type=float, default=18.0)
    parser.add_argument("--max-nearest-screen-distance", type=float, default=48.0)
    parser.add_argument("--outside-bbox-penalty", type=float, default=64.0)
    parser.add_argument("--world-average-count", type=int, default=8)
    parser.add_argument("--radius", type=float, default=0.045)
    parser.add_argument("--min-radius", type=float, default=0.018)
    parser.add_argument("--max-radius", type=float, default=0.13)
    parser.add_argument("--radius-weight-base", type=float, default=0.8)
    parser.add_argument("--radius-weight-scale", type=float, default=1.4)
    parser.add_argument("--y-lift", type=float, default=0.035)
    parser.add_argument("--radiance", default="0.55,0.70,0.95")
    parser.add_argument("--radiance-scale", type=float, default=1.0)
    parser.add_argument("--radiance-weight-base", type=float, default=0.65)
    parser.add_argument("--radiance-weight-scale", type=float, default=1.6)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S442 Mitsuba Light Response Contract Consumer")
    parser.add_argument("--next", default="Validate, render, and compare this contract-driven light response candidate against SS1_Native.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("frames must be non-negative")
    if args.anchor_limit <= 0:
        parser.error("anchor-limit must be positive")
    if args.vertex_stride <= 0:
        parser.error("vertex-stride must be positive")
    if args.world_average_count <= 0:
        parser.error("world-average-count must be positive")
    if args.radius <= 0.0 or args.min_radius <= 0.0 or args.max_radius <= 0.0:
        parser.error("radius values must be positive")
    if args.min_radius > args.max_radius:
        parser.error("min-radius cannot exceed max-radius")
    if args.max_nearest_screen_distance < 0.0:
        parser.error("max-nearest-screen-distance must be non-negative")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    if min(args.radiance_vec) < 0.0:
        parser.error("radiance values must be non-negative")
    build(args)


if __name__ == "__main__":
    main()
