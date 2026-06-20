#!/usr/bin/env python
"""Add Mitsuba disk emitters from target-residual response requests."""

import argparse
import copy
import math
import os
from datetime import datetime, timezone

from add_mitsuba_water_mask_highlights import (
    add_response_comment,
    csv3,
    fmt,
    insert_before_scene_end,
    parse_vec3,
    read_obj_vertices,
    resolve_path,
    selected_frames,
    source_entry,
    write_command_list,
)
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


def requests_by_output_frame(residual):
    frames = {}
    for request in residual.get("requests") or []:
        output_frame = request.get("output_frame")
        if output_frame is None:
            continue
        frames.setdefault(output_frame, []).append(request)
    for items in frames.values():
        items.sort(key=lambda item: item.get("score") or 0.0, reverse=True)
    return frames


def parse_output_frames(value):
    if not value:
        return None
    frames = set()
    for token in str(value).split(","):
        token = token.strip()
        if not token:
            continue
        frames.add(int(token))
    return frames


def request_center(request):
    patch = request.get("suggested_patch") or {}
    center = patch.get("screen_center_px") or request.get("weighted_center_px") or request.get("center_px")
    if not center or len(center) != 2:
        return None
    return float(center[0]), float(center[1])


def bbox_contains(bbox, px, py, padding):
    x0, y0, x1, y1 = bbox
    return px >= x0 - padding and px <= x1 + padding and py >= y0 - padding and py <= y1 + padding


def screen_world_radius(request, camera, depth, args):
    patch = request.get("suggested_patch") or {}
    screen_radius = float(patch.get("screen_radius_px") or request.get("radius_px") or args.default_screen_radius)
    height = float(max(1, int(camera.get("height") or 540)))
    world_per_px = 2.0 * depth * math.tan(math.radians(float(camera.get("fov") or 45.0)) * 0.5) / height
    radius = screen_radius * world_per_px * args.radius_scale
    return max(args.min_radius, min(args.max_radius, radius))


def collect_projected_vertices(vertices, camera, width, height, request, args):
    bbox = request.get("bbox") or [0, 0, width - 1, height - 1]
    center = request_center(request)
    candidates = []
    nearest = []
    for vertex in vertices:
        projected = project(vertex, camera, width, height)
        if projected is None:
            continue
        px, py, depth = projected
        distance = 0.0
        if center is not None:
            distance = math.hypot(px - center[0], py - center[1])
        inside = bbox_contains(bbox, px, py, args.bbox_padding)
        if inside:
            weight = max(1.0, float(request.get("mean_residual") or 1.0))
            if center is not None:
                radius = max(1.0, float(request.get("radius_px") or args.default_screen_radius))
                weight *= max(0.2, 1.0 - min(1.0, distance / (radius * args.center_falloff)))
            candidates.append({
                "position": vertex,
                "screen": (px, py),
                "depth": depth,
                "weight": weight,
                "distance": distance,
            })
        elif center is not None:
            nearest.append({
                "position": vertex,
                "screen": (px, py),
                "depth": depth,
                "weight": max(1.0, float(request.get("mean_residual") or 1.0)) / (1.0 + distance),
                "distance": distance,
            })
    if candidates:
        candidates.sort(key=lambda item: (item["distance"], item["depth"]))
        return candidates[:args.max_vertices_per_request], False
    nearest.sort(key=lambda item: item["distance"])
    return nearest[:args.nearest_fallback_vertices], True


def make_patch(request, vertices, camera, args):
    width = int(camera.get("width") or 960)
    height = int(camera.get("height") or 540)
    candidates, used_fallback = collect_projected_vertices(vertices, camera, width, height, request, args)
    if len(candidates) < args.min_vertices_per_request:
        return None
    weight_sum = sum(item["weight"] for item in candidates)
    position = [
        sum(item["position"][axis] * item["weight"] for item in candidates) / weight_sum
        for axis in range(3)
    ]
    screen = [
        sum(item["screen"][0] * item["weight"] for item in candidates) / weight_sum,
        sum(item["screen"][1] * item["weight"] for item in candidates) / weight_sum,
    ]
    depth = sum(item["depth"] * item["weight"] for item in candidates) / weight_sum
    patch = request.get("suggested_patch") or {}
    radiance = patch.get("radiance_rgb") or [args.radiance_vec[0], args.radiance_vec[1], args.radiance_vec[2]]
    radiance = [max(0.0, float(value) * args.radiance_scale) for value in radiance]
    radius = screen_world_radius(request, camera, depth, args)
    return {
        "request": request,
        "position": position,
        "screen": screen,
        "depth": depth,
        "radius": radius,
        "candidate_count": len(candidates),
        "used_fallback": used_fallback,
        "radiance": radiance,
    }


def patch_emitter_block(patches, args, frame_index, camera):
    lines = []
    target = csv3(camera.get("origin") or [0.0, 0.0, 0.0])
    up = csv3(camera.get("up") or [0.0, 1.0, 0.0])
    for index, patch in enumerate(patches):
        x, y, z = patch["position"]
        y += args.y_lift
        radius = patch["radius"]
        lines.extend([
            f'  <shape type="disk" id="lsfs_s454_residual_patch_{frame_index:04d}_{index:03d}">',
            '    <transform name="to_world">',
            f'      <lookat origin="{csv3([x, y, z])}" target="{target}" up="{up}"/>',
            f'      <scale x="{fmt(radius)}" y="{fmt(radius * args.aspect)}" z="1"/>',
            '    </transform>',
            '    <emitter type="area">',
            f'      <rgb name="radiance" value="{csv3(patch["radiance"])}"/>',
            '    </emitter>',
            '  </shape>',
        ])
    return "\n".join(lines)


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks") or {}
    response = export.get("residual_response_patches") or {}
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
        f"- Residual analysis: `{export['sources']['residual_analysis']['repo_path']}`",
        "",
        "## Residual Response Patches",
        "",
        f"- Request limit: `{response.get('request_limit')}`",
        f"- Per-frame request limit: `{response.get('per_frame_request_limit')}`",
        f"- Output frame filter: `{response.get('output_frames')}`",
        f"- Radius range: `{response.get('min_radius')}..{response.get('max_radius')}`",
        f"- Radius scale: `{response.get('radius_scale')}`",
        f"- Radiance scale: `{response.get('radiance_scale')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Residual requests consumed: `{checks.get('residual_requests_consumed')}`",
        f"- Candidate vertices: `{checks.get('candidate_vertices')}`",
        f"- Patches inserted: `{checks.get('patches_inserted')}`",
        f"- Fallback patches: `{checks.get('fallback_patches')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Vertices | Requests | Patches | Fallback | XML Scene |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = export.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("residual_response_patches") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('vertices_tested')} | "
            f"{item.get('requests_consumed')} | {item.get('patches_inserted')} | "
            f"{item.get('fallback_patches')} | `{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def add_patches(args):
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    residual_path = require_file(args.residual_analysis, "target residual analysis")
    base = read_json(base_export_path)
    residual = read_json(residual_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if residual.get("schema") != "lsfs_mitsuba_target_residual_analysis":
        raise SystemExit(f"{args.residual_analysis}: expected lsfs_mitsuba_target_residual_analysis schema")
    if residual.get("status") != "ready":
        raise SystemExit(f"{args.residual_analysis}: residual analysis status is {residual.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    requests = requests_by_output_frame(residual)
    remaining_request_budget = args.request_limit
    frames = []
    failures = []
    totals = {
        "xml_scene_bytes": 0,
        "vertices_tested": 0,
        "candidate_vertices": 0,
        "residual_requests_consumed": 0,
        "patches_inserted": 0,
        "fallback_patches": 0,
    }
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        water_mesh = resolve_path(((frame.get("water_mesh") or {}).get("path") or (frame.get("water_mesh") or {}).get("repo_path")))
        missing = []
        for role, path in (("source_xml", source_xml), ("water_mesh", water_mesh)):
            if not path or not os.path.isfile(path):
                missing.append({"role": role, "path": path})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        frame_requests = [] if args.output_frames and output_frame not in args.output_frames else list(requests.get(output_frame) or [])
        if args.per_frame_request_limit > 0:
            frame_requests = frame_requests[:args.per_frame_request_limit]
        if remaining_request_budget > 0:
            frame_requests = frame_requests[:remaining_request_budget]
            remaining_request_budget -= len(frame_requests)
        elif args.request_limit > 0:
            frame_requests = []

        vertices = read_obj_vertices(water_mesh, args.vertex_stride)
        camera = parse_camera(source_xml)
        patches = []
        for request in frame_requests:
            patch = make_patch(request, vertices, camera, args)
            if patch is not None:
                patches.append(patch)
        if args.patch_limit > 0:
            patches = patches[:args.patch_limit]

        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        block = patch_emitter_block(patches, args, index, camera)
        patched = insert_before_scene_end(xml_text, block)
        patched = add_response_comment(
            patched,
            f"<!-- S454 residual_response_patches patches={len(patches)} requests={len(frame_requests)} -->",
        )
        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        candidate_vertices = sum(patch["candidate_count"] for patch in patches)
        fallback_patches = sum(1 for patch in patches if patch["used_fallback"])
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["vertices_tested"] += len(vertices)
        totals["candidate_vertices"] += candidate_vertices
        totals["residual_requests_consumed"] += len(frame_requests)
        totals["patches_inserted"] += len(patches)
        totals["fallback_patches"] += fallback_patches

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
        out_frame["residual_response_patches"] = {
            "enabled": True,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "vertices_tested": len(vertices),
            "requests_consumed": len(frame_requests),
            "candidate_vertices": candidate_vertices,
            "patches_inserted": len(patches),
            "fallback_patches": fallback_patches,
            "patch_samples": [
                {
                    "position": [float(v) for v in patch["position"]],
                    "screen": [float(patch["screen"][0]), float(patch["screen"][1])],
                    "depth": float(patch["depth"]),
                    "radius": float(patch["radius"]),
                    "candidate_count": int(patch["candidate_count"]),
                    "used_fallback": bool(patch["used_fallback"]),
                    "radiance": [float(v) for v in patch["radiance"]],
                    "request_output_frame": patch["request"].get("output_frame"),
                    "request_bbox": patch["request"].get("bbox"),
                    "request_mean_residual": patch["request"].get("mean_residual"),
                }
                for patch in patches[:8]
            ],
        }
        frames.append(out_frame)

    command_list = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_command_list(
        command_list,
        frames,
        (base.get("render_settings") or {}).get("mitsuba_command") or "mitsuba",
        (base.get("render_settings") or {}).get("mitsuba_mode"),
    )

    export = copy.deepcopy(base)
    export.update({
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if frames and not failures and totals["patches_inserted"] > 0 else "review",
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "residual_analysis": source_entry(residual_path, root, "target residual analysis", residual),
        },
        "frames": frames,
        "failures": failures,
        "residual_response_patches": {
            "enabled": True,
            "request_limit": args.request_limit,
            "per_frame_request_limit": args.per_frame_request_limit,
            "output_frames": sorted(args.output_frames) if args.output_frames else None,
            "patch_limit": args.patch_limit,
            "vertex_stride": args.vertex_stride,
            "bbox_padding": args.bbox_padding,
            "nearest_fallback_vertices": args.nearest_fallback_vertices,
            "min_vertices_per_request": args.min_vertices_per_request,
            "max_vertices_per_request": args.max_vertices_per_request,
            "min_radius": args.min_radius,
            "max_radius": args.max_radius,
            "radius_scale": args.radius_scale,
            "aspect": args.aspect,
            "y_lift": args.y_lift,
            "radiance_scale": args.radiance_scale,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["residual_response_patches_enabled"] = True
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
        f"status={export['status']} frames={len(frames)} patches={totals['patches_inserted']} "
        f"requests={totals['residual_requests_consumed']} candidates={totals['candidate_vertices']} "
        f"fallback={totals['fallback_patches']} export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Add target-residual Mitsuba disk emitters to an XML export")
    parser.add_argument("base_export")
    parser.add_argument("residual_analysis")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--request-limit", type=int, default=16)
    parser.add_argument("--per-frame-request-limit", type=int, default=4)
    parser.add_argument("--output-frames", help="comma-separated output_frame values to receive residual patches")
    parser.add_argument("--patch-limit", type=int, default=32)
    parser.add_argument("--vertex-stride", type=int, default=1)
    parser.add_argument("--bbox-padding", type=float, default=8.0)
    parser.add_argument("--nearest-fallback-vertices", type=int, default=16)
    parser.add_argument("--min-vertices-per-request", type=int, default=1)
    parser.add_argument("--max-vertices-per-request", type=int, default=1800)
    parser.add_argument("--default-screen-radius", type=float, default=24.0)
    parser.add_argument("--center-falloff", type=float, default=1.7)
    parser.add_argument("--min-radius", type=float, default=0.035)
    parser.add_argument("--max-radius", type=float, default=0.34)
    parser.add_argument("--radius-scale", type=float, default=0.16)
    parser.add_argument("--aspect", type=float, default=0.52)
    parser.add_argument("--y-lift", type=float, default=0.026)
    parser.add_argument("--radiance", default="0.82,1.02,1.34")
    parser.add_argument("--radiance-scale", type=float, default=1.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S454 Mitsuba Residual Response Patches")
    parser.add_argument("--next", default="Validate, render, and compare this target-residual response candidate.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("frames must be non-negative")
    if args.request_limit < 0:
        parser.error("request-limit must be non-negative")
    if args.per_frame_request_limit < 0:
        parser.error("per-frame-request-limit must be non-negative")
    if args.patch_limit < 0:
        parser.error("patch-limit must be non-negative")
    if args.vertex_stride <= 0:
        parser.error("vertex-stride must be positive")
    if args.bbox_padding < 0.0:
        parser.error("bbox-padding must be non-negative")
    if args.nearest_fallback_vertices <= 0:
        parser.error("nearest-fallback-vertices must be positive")
    if args.min_vertices_per_request <= 0:
        parser.error("min-vertices-per-request must be positive")
    if args.max_vertices_per_request < args.min_vertices_per_request:
        parser.error("max-vertices-per-request cannot be smaller than min-vertices-per-request")
    if args.default_screen_radius <= 0.0:
        parser.error("default-screen-radius must be positive")
    if args.center_falloff <= 0.0:
        parser.error("center-falloff must be positive")
    if args.min_radius <= 0.0 or args.max_radius <= 0.0:
        parser.error("radius values must be positive")
    if args.min_radius > args.max_radius:
        parser.error("min-radius cannot exceed max-radius")
    if args.radius_scale <= 0.0:
        parser.error("radius-scale must be positive")
    if args.aspect <= 0.0:
        parser.error("aspect must be positive")
    if args.radiance_scale < 0.0:
        parser.error("radiance-scale must be non-negative")
    try:
        args.output_frames = parse_output_frames(args.output_frames)
    except ValueError as exc:
        parser.error(f"output-frames must be comma-separated integers: {exc}")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    if min(args.radiance_vec) < 0.0:
        parser.error("radiance values must be non-negative")
    add_patches(args)


if __name__ == "__main__":
    main()
