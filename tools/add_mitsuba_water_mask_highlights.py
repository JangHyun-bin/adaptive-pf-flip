"""Add world-space water-surface highlight emitters from a projected mask."""

import argparse
import copy
import math
import os
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

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


MASK_SCHEMAS = {
    "lsfs_mitsuba_secondary_composite",
    "lsfs_mitsuba_source_response_mask_source",
}


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to add water mask highlights")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def selected_frames(frames, requested=None):
    if not frames:
        return []
    if requested is None or requested <= 0 or requested >= len(frames):
        return frames
    if requested == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(requested - 1)) for i in range(requested)))
    return [frames[index] for index in indices]


def parse_vec3(value, label):
    parts = [float(part.strip()) for part in str(value).split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{label} must be r,g,b")
    return parts


def fmt(value):
    return f"{float(value):.8g}"


def csv3(values):
    return ", ".join(fmt(item) for item in values)


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


def mask_value(mask, px, py, camera_width, camera_height, radius):
    width, height = mask.size
    sx = px * width / float(max(1, camera_width))
    sy = py * height / float(max(1, camera_height))
    cx = int(round(sx))
    cy = int(round(sy))
    r = max(0, int(radius))
    x0 = max(0, cx - r)
    y0 = max(0, cy - r)
    x1 = min(width - 1, cx + r)
    y1 = min(height - 1, cy + r)
    if x0 > x1 or y0 > y1:
        return 0
    pix = mask.load()
    best = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            best = max(best, int(pix[x, y]))
    return best


def source_luma(source, px, py, camera_width, camera_height):
    if source is None:
        return None
    width, height = source.size
    x = int(round(px * width / float(max(1, camera_width))))
    y = int(round(py * height / float(max(1, camera_height))))
    if x < 0 or x >= width or y < 0 or y >= height:
        return None
    r, g, b = source.getpixel((x, y))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def select_vertices(vertices, camera, mask, source, args):
    candidates = []
    width = int(camera.get("width") or mask.size[0])
    height = int(camera.get("height") or mask.size[1])
    for vertex in vertices:
        projected = project(vertex, camera, width, height)
        if projected is None:
            continue
        px, py, depth = projected
        value = mask_value(mask, px, py, width, height, args.mask_sample_radius)
        if value < args.mask_threshold:
            continue
        luma = source_luma(source, px, py, width, height)
        if luma is not None and (luma < args.source_luma_min or luma > args.source_luma_max):
            continue
        score = value + max(0.0, (luma or 0.0) - args.source_luma_min) * 0.01 - depth * args.depth_penalty
        candidates.append({
            "position": vertex,
            "screen": (px, py),
            "depth": depth,
            "mask_value": value,
            "source_luma": luma,
            "score": score,
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    selected = []
    min_dist2 = args.min_screen_distance * args.min_screen_distance
    for item in candidates:
        if len(selected) >= args.emitter_limit:
            break
        px, py = item["screen"]
        if any((px - other["screen"][0]) ** 2 + (py - other["screen"][1]) ** 2 < min_dist2 for other in selected):
            continue
        selected.append(item)
    return selected, len(candidates)


def emitter_block(items, args, frame_index):
    lines = []
    radiance = csv3(args.radiance_vec)
    for index, item in enumerate(items):
        x, y, z = item["position"]
        y += args.y_lift
        radius = args.radius
        if args.depth_radius_scale > 0.0:
            radius *= max(0.5, min(2.0, args.reference_depth / max(1.0, item["depth"]))) ** args.depth_radius_scale
        lines.extend([
            f'  <shape type="sphere" id="lsfs_s415_water_highlight_{frame_index:04d}_{index:03d}">',
            f'    <point name="center" x="{fmt(x)}" y="{fmt(y)}" z="{fmt(z)}"/>',
            f'    <float name="radius" value="{fmt(radius)}"/>',
            '    <emitter type="area">',
            f'      <rgb name="radiance" value="{radiance}"/>',
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
        "path": path,
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
    return entry


def mask_layer_ref(frame):
    if not frame:
        return None
    return frame.get("layer_path") or frame.get("layer_repo_path")


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    response = export.get("water_mask_highlights") or {}
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
        f"- Mask source: `{export['sources']['mask_source']['repo_path']}`",
        "",
        "## Water Highlight Emitters",
        "",
        f"- Emitter limit: `{response.get('emitter_limit')}`",
        f"- Radius: `{response.get('radius')}`",
        f"- Radiance: `{response.get('radiance')}`",
        f"- Mask threshold: `{response.get('mask_threshold')}`",
        f"- Source luma gate: `{response.get('source_luma_min')}..{response.get('source_luma_max')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Candidate vertices: `{checks.get('candidate_vertices')}`",
        f"- Emitters inserted: `{checks.get('emitters_inserted')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Vertices | Candidates | Emitters | Mask | XML Scene |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("water_mask_highlights") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('vertices_tested')} | "
            f"{item.get('candidate_vertices')} | {item.get('emitters_inserted')} | "
            f"`{item.get('mask_layer_repo_path')}` | `{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def add_highlights(args):
    require_pillow()
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    mask_source_path = require_file(args.mask_source, "mask source")
    base = read_json(base_export_path)
    mask_source = read_json(mask_source_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if mask_source.get("schema") not in MASK_SCHEMAS:
        expected = ", ".join(sorted(MASK_SCHEMAS))
        raise SystemExit(f"{args.mask_source}: expected one of {expected}")
    if mask_source.get("status") and mask_source.get("status") != "ready":
        raise SystemExit(f"{args.mask_source}: mask source status is {mask_source.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    mask_frames = output_frame_map(mask_source.get("frames") or [])
    frames = []
    failures = []
    totals = {
        "xml_scene_bytes": 0,
        "vertices_tested": 0,
        "candidate_vertices": 0,
        "emitters_inserted": 0,
    }
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        water_mesh = resolve_path(((frame.get("water_mesh") or {}).get("path") or (frame.get("water_mesh") or {}).get("repo_path")))
        mask_frame = mask_frames.get(output_frame)
        mask_path = resolve_path(mask_layer_ref(mask_frame))
        source_path = resolve_path((mask_frame or {}).get("source_path") or (mask_frame or {}).get("source_repo_path"))
        missing = []
        for role, path in (("source_xml", source_xml), ("water_mesh", water_mesh), ("mask_layer", mask_path)):
            if not path or not os.path.isfile(path):
                missing.append({"role": role, "path": path})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        vertices = read_obj_vertices(water_mesh, args.vertex_stride)
        mask = Image.open(mask_path).convert("L")
        source = Image.open(source_path).convert("RGB") if source_path and os.path.isfile(source_path) else None
        camera = parse_camera(source_xml)
        selected, candidate_count = select_vertices(vertices, camera, mask, source, args)
        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        block = emitter_block(selected, args, index)
        patched = insert_before_scene_end(xml_text, block)
        patched = add_response_comment(
            patched,
            f"<!-- S415 water_mask_highlights emitters={len(selected)} candidates={candidate_count} -->",
        )
        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["vertices_tested"] += len(vertices)
        totals["candidate_vertices"] += candidate_count
        totals["emitters_inserted"] += len(selected)

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
        out_frame["water_mask_highlights"] = {
            "enabled": True,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "mask_layer_path": mask_path,
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "source_repo_path": posix_rel(source_path, root) if source_path else None,
            "vertices_tested": len(vertices),
            "candidate_vertices": candidate_count,
            "emitters_inserted": len(selected),
            "emitter_samples": [
                {
                    "position": [float(v) for v in item["position"]],
                    "screen": [float(item["screen"][0]), float(item["screen"][1])],
                    "depth": float(item["depth"]),
                    "mask_value": int(item["mask_value"]),
                    "source_luma": item["source_luma"],
                }
                for item in selected[:8]
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
        "status": "ready" if frames and not failures and totals["emitters_inserted"] > 0 else "review",
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "mask_source": source_entry(mask_source_path, root, "water highlight mask source", mask_source),
        },
        "frames": frames,
        "failures": failures,
        "water_mask_highlights": {
            "enabled": True,
            "emitter_limit": args.emitter_limit,
            "radius": args.radius,
            "y_lift": args.y_lift,
            "radiance": args.radiance_vec,
            "mask_threshold": args.mask_threshold,
            "mask_sample_radius": args.mask_sample_radius,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
            "vertex_stride": args.vertex_stride,
            "min_screen_distance": args.min_screen_distance,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["water_mask_highlights_enabled"] = True
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
        f"status={export['status']} frames={len(frames)} "
        f"emitters={totals['emitters_inserted']} candidates={totals['candidate_vertices']} "
        f"export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Add world-space water-surface Mitsuba highlight emitters from a mask")
    parser.add_argument("base_export")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--emitter-limit", type=int, default=48)
    parser.add_argument("--vertex-stride", type=int, default=1)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--mask-sample-radius", type=int, default=5)
    parser.add_argument("--source-luma-min", type=float, default=0.0)
    parser.add_argument("--source-luma-max", type=float, default=255.0)
    parser.add_argument("--min-screen-distance", type=float, default=10.0)
    parser.add_argument("--radius", type=float, default=0.035)
    parser.add_argument("--y-lift", type=float, default=0.025)
    parser.add_argument("--radiance", default="0.35,0.45,0.60")
    parser.add_argument("--reference-depth", type=float, default=45.0)
    parser.add_argument("--depth-radius-scale", type=float, default=0.0)
    parser.add_argument("--depth-penalty", type=float, default=0.01)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S415 Mitsuba Water Mask Highlights")
    parser.add_argument("--next", default="Render and compare this water-surface localized highlight candidate against SS1, S409 SF12_H18, and S401 CR21.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.emitter_limit < 0:
        parser.error("emitter-limit must be non-negative")
    if args.vertex_stride <= 0:
        parser.error("vertex-stride must be positive")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.mask_sample_radius < 0:
        parser.error("mask-sample-radius must be non-negative")
    if args.source_luma_min < 0.0 or args.source_luma_max > 255.0:
        parser.error("source luma bounds must be in [0, 255]")
    if args.source_luma_min > args.source_luma_max:
        parser.error("source-luma-min cannot exceed source-luma-max")
    if args.min_screen_distance < 0.0:
        parser.error("min-screen-distance must be non-negative")
    if args.radius <= 0.0:
        parser.error("radius must be positive")
    if args.reference_depth <= 0.0:
        parser.error("reference-depth must be positive")
    if args.depth_radius_scale < 0.0:
        parser.error("depth-radius-scale must be non-negative")
    if args.depth_penalty < 0.0:
        parser.error("depth-penalty must be non-negative")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    if min(args.radiance_vec) < 0.0:
        parser.error("radiance values must be non-negative")
    add_highlights(args)


if __name__ == "__main__":
    main()
