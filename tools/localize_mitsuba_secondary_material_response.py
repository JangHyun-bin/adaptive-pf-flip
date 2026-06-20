"""Localize Mitsuba secondary BSDF response using a projected mask source."""

import argparse
import copy
import os
import re
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
CHANNELS = {"spray", "foam", "bubble", "droplet"}
SHAPE_RE = re.compile(r'(<shape\s+type="(?P<type>disk|sphere)">.*?</shape>)', re.DOTALL)
REF_RE = re.compile(r'<ref\s+name="bsdf"\s+id="(?P<id>lsfs_secondary_(?P<channel>spray|foam|bubble|droplet)(?P<suffix>_billboard|_halo|_mist)?)"\s*/>')
LOOKAT_RE = re.compile(r'<lookat\s+[^>]*origin="(?P<origin>[^"]+)"')
POINT_RE = re.compile(r'<point\s+name="center"\s+x="(?P<x>[^"]+)"\s+y="(?P<y>[^"]+)"\s+z="(?P<z>[^"]+)"\s*/>')


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to localize Mitsuba material response")


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


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def fmt(value):
    return f"{float(value):.8g}"


def parse_csv3(value):
    parts = [float(part.strip()) for part in str(value).split(",")]
    if len(parts) != 3:
        raise ValueError(f"expected 3 values, got {value!r}")
    return parts


def csv3(values):
    return ", ".join(fmt(item) for item in values)


def parse_center(block, shape_type):
    if shape_type == "disk":
        match = LOOKAT_RE.search(block)
        if not match:
            return None
        return parse_csv3(match.group("origin"))
    match = POINT_RE.search(block)
    if not match:
        return None
    return [float(match.group("x")), float(match.group("y")), float(match.group("z"))]


def sample_mask(mask, px, py, camera_width, camera_height, radius, threshold):
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
        return False, 0
    max_value = 0
    pix = mask.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            value = int(pix[x, y])
            if value > max_value:
                max_value = value
            if value >= threshold:
                return True, max_value
    return False, max_value


def sample_luma(image, px, py, camera_width, camera_height):
    if image is None:
        return None
    width, height = image.size
    sx = px * width / float(max(1, camera_width))
    sy = py * height / float(max(1, camera_height))
    x = int(round(sx))
    y = int(round(sy))
    if x < 0 or x >= width or y < 0 or y >= height:
        return None
    r, g, b = image.getpixel((x, y))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def scale_rgb_text(value, scale):
    values = parse_csv3(value)
    return csv3([clamp(item * scale, 0.0, 4.0) for item in values])


def find_bsdf_block(xml_text, bsdf_id):
    start_match = re.search(rf'<bsdf\s+[^>]*id="{re.escape(bsdf_id)}"[^>]*>', xml_text)
    if not start_match:
        return None
    depth = 0
    token_re = re.compile(r'<bsdf\b|</bsdf>')
    for token in token_re.finditer(xml_text, start_match.start()):
        if token.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return xml_text[start_match.start():token.end()]
        else:
            depth += 1
    return None


def localized_bsdf_block(xml_text, base_id, args):
    block = find_bsdf_block(xml_text, base_id)
    if not block:
        return None
    localized_id = f"{base_id}_localized"
    block = block.replace(f'id="{base_id}"', f'id="{localized_id}"', 1)

    def rgb_repl(match):
        return f'{match.group(1)}{scale_rgb_text(match.group(2), args.localized_reflectance_scale)}{match.group(3)}'

    block = re.sub(r'(<rgb\s+name="reflectance"\s+value=")([^"]+)(")', rgb_repl, block)

    def opacity_repl(match):
        value = float(match.group(2))
        return f'{match.group(1)}{fmt(clamp(value * args.localized_opacity_scale, 0.0, 1.0))}{match.group(3)}'

    block = re.sub(r'(<float\s+name="opacity"\s+value=")([^"]+)(")', opacity_repl, block)
    return block


def insert_localized_bsdfs(xml_text, bsdf_blocks):
    if not bsdf_blocks:
        return xml_text
    marker = '  <shape type="obj">'
    index = xml_text.find(marker)
    if index < 0:
        marker = "</scene>"
        index = xml_text.rfind(marker)
    if index < 0:
        raise ValueError("missing scene insertion point")
    block = "\n".join(["  <!-- S414 localized secondary BSDFs -->", *bsdf_blocks, ""])
    return xml_text[:index] + block + xml_text[index:]


def add_response_comment(xml_text, comment):
    if xml_text.startswith("<?xml"):
        line_end = xml_text.find("\n")
        if line_end >= 0:
            return xml_text[:line_end + 1] + comment + "\n" + xml_text[line_end + 1:]
    return comment + "\n" + xml_text


def patch_shapes(xml_text, mask_image, source_image, args):
    camera = parse_camera(args.current_xml)
    camera_width = camera.get("width", mask_image.size[0])
    camera_height = camera.get("height", mask_image.size[1])
    used_ids = set()
    stats = {
        "secondary_shapes": 0,
        "localized_shapes": 0,
        "localized_disks": 0,
        "localized_spheres": 0,
        "projected_shapes": 0,
        "luma_tested_shapes": 0,
        "luma_rejected_shapes": 0,
        "mask_hits_by_channel": {channel: 0 for channel in sorted(args.channels_set)},
    }

    def repl(match):
        block = match.group(1)
        shape_type = match.group("type")
        ref = REF_RE.search(block)
        if not ref:
            return block
        channel = ref.group("channel")
        if channel not in args.channels_set:
            return block
        stats["secondary_shapes"] += 1
        center = parse_center(block, shape_type)
        if center is None:
            return block
        projected = project(center, camera, camera_width, camera_height)
        if projected is None:
            return block
        stats["projected_shapes"] += 1
        px, py, _depth = projected
        source_luma = sample_luma(source_image, px, py, camera_width, camera_height)
        if source_luma is not None:
            stats["luma_tested_shapes"] += 1
            if source_luma < args.source_luma_min or source_luma > args.source_luma_max:
                stats["luma_rejected_shapes"] += 1
                return block
        hit, _max_value = sample_mask(
            mask_image,
            px,
            py,
            camera_width,
            camera_height,
            args.mask_sample_radius,
            args.mask_threshold,
        )
        if not hit:
            return block
        base_id = ref.group("id")
        used_ids.add(base_id)
        localized_id = f"{base_id}_localized"
        stats["localized_shapes"] += 1
        stats["mask_hits_by_channel"][channel] += 1
        if shape_type == "disk":
            stats["localized_disks"] += 1
        else:
            stats["localized_spheres"] += 1
        return block[:ref.start("id")] + localized_id + block[ref.end("id"):]

    patched = SHAPE_RE.sub(repl, xml_text)
    bsdf_blocks = []
    for base_id in sorted(used_ids):
        block = localized_bsdf_block(xml_text, base_id, args)
        if block:
            bsdf_blocks.append(block)
    patched = insert_localized_bsdfs(patched, bsdf_blocks)
    stats["localized_bsdfs"] = len(bsdf_blocks)
    stats["localized_bsdf_ids"] = sorted(f"{item}_localized" for item in used_ids)
    return patched, stats


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
    return frame.get("layer_path") or frame.get("layer_repo_path") or frame.get("secondary_layer_path") or frame.get("secondary_layer_repo_path")


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    response = export.get("localized_secondary_response") or {}
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
        "## Localized Response",
        "",
        f"- Channels: `{response.get('channels')}`",
        f"- Mask threshold: `{response.get('mask_threshold')}`",
        f"- Mask sample radius: `{response.get('mask_sample_radius')}`",
        f"- Source luma gate: `{response.get('source_luma_min')}..{response.get('source_luma_max')}`",
        f"- Localized reflectance scale: `{response.get('localized_reflectance_scale')}`",
        f"- Localized opacity scale: `{response.get('localized_opacity_scale')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Localized shapes: `{checks.get('localized_shapes')}`",
        f"- Localized disks: `{checks.get('localized_disks')}`",
        f"- Localized spheres: `{checks.get('localized_spheres')}`",
        f"- Localized BSDFs: `{checks.get('localized_bsdfs')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Mask | Localized Shapes | Disks | Spheres | Localized BSDFs | XML Scene |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        local = frame.get("localized_secondary_response") or {}
        lines.append(
            f"| {frame.get('output_frame')} | `{local.get('mask_layer_repo_path')}` | "
            f"{local.get('localized_shapes')} | {local.get('localized_disks')} | "
            f"{local.get('localized_spheres')} | {local.get('localized_bsdfs')} | "
            f"`{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def localize(args):
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
        "localized_shapes": 0,
        "localized_disks": 0,
        "localized_spheres": 0,
        "localized_bsdfs": 0,
        "secondary_shapes": 0,
        "projected_shapes": 0,
        "luma_tested_shapes": 0,
        "luma_rejected_shapes": 0,
    }
    channel_hits = {channel: 0 for channel in sorted(args.channels_set)}
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        mask_frame = mask_frames.get(output_frame)
        mask_path = resolve_path(mask_layer_ref(mask_frame))
        missing = []
        if not source_xml or not os.path.isfile(source_xml):
            missing.append({"role": "source_xml", "path": source_xml})
        if not mask_path or not os.path.isfile(mask_path):
            missing.append({"role": "mask_layer", "path": mask_path})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        args.current_xml = source_xml
        mask_image = Image.open(mask_path).convert("L")
        source_path = resolve_path((mask_frame or {}).get("source_path") or (mask_frame or {}).get("source_repo_path"))
        source_image = Image.open(source_path).convert("RGB") if source_path and os.path.isfile(source_path) else None
        patched, stats = patch_shapes(xml_text, mask_image, source_image, args)
        patched = add_response_comment(
            patched,
            f"<!-- S414 localized_secondary_response localized_shapes={stats['localized_shapes']} -->",
        )
        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        for key in (
            "localized_shapes",
            "localized_disks",
            "localized_spheres",
            "localized_bsdfs",
            "secondary_shapes",
            "projected_shapes",
            "luma_tested_shapes",
            "luma_rejected_shapes",
        ):
            totals[key] += int(stats.get(key, 0))
        for channel, value in (stats.get("mask_hits_by_channel") or {}).items():
            channel_hits[channel] = channel_hits.get(channel, 0) + int(value)

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
        out_frame["localized_secondary_response"] = {
            "enabled": True,
            "mask_layer_path": mask_path,
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "mask_layer_sha256": sha256_file(mask_path),
            "source_repo_path": posix_rel(source_path, root) if source_path else None,
            **stats,
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
        "status": "ready" if frames and not failures and totals["localized_shapes"] > 0 else "review",
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "mask_source": source_entry(mask_source_path, root, "localized response mask source", mask_source),
        },
        "frames": frames,
        "failures": failures,
        "localized_secondary_response": {
            "enabled": True,
            "channels": sorted(args.channels_set),
            "mask_threshold": args.mask_threshold,
            "mask_sample_radius": args.mask_sample_radius,
            "localized_reflectance_scale": args.localized_reflectance_scale,
            "localized_opacity_scale": args.localized_opacity_scale,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
            "mask_source_schema": mask_source.get("schema"),
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["localized_secondary_response_enabled"] = True
    export["render_settings"]["localized_secondary_response_channels"] = sorted(args.channels_set)
    export["checks"] = copy.deepcopy(base.get("checks") or {})
    export["checks"].update({
        "frames_exported": len(frames),
        "missing_references": len(failures),
        "localized_shapes": totals["localized_shapes"],
        "localized_disks": totals["localized_disks"],
        "localized_spheres": totals["localized_spheres"],
        "localized_bsdfs": totals["localized_bsdfs"],
        "secondary_shapes": totals["secondary_shapes"],
        "projected_shapes": totals["projected_shapes"],
        "luma_tested_shapes": totals["luma_tested_shapes"],
        "luma_rejected_shapes": totals["luma_rejected_shapes"],
        "mask_hits_by_channel": channel_hits,
        "xml_scene_bytes": totals["xml_scene_bytes"],
    })

    export_path = os.path.join(out_dir, "mitsuba_export.json")
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root, args.next))
    print(
        f"status={export['status']} frames={len(frames)} "
        f"localized_shapes={totals['localized_shapes']} "
        f"bsdfs={totals['localized_bsdfs']} export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Localize secondary Mitsuba material response to projected mask hits")
    parser.add_argument("base_export")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--channels", default="spray,foam")
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--mask-sample-radius", type=int, default=4)
    parser.add_argument("--source-luma-min", type=float, default=0.0)
    parser.add_argument("--source-luma-max", type=float, default=255.0)
    parser.add_argument("--localized-reflectance-scale", type=float, default=0.45)
    parser.add_argument("--localized-opacity-scale", type=float, default=0.70)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S414 Mitsuba Localized Secondary Response")
    parser.add_argument("--next", default="Render and compare this localized material response against SS1, MR2, S409 SF12_H18, and S401 CR21.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)

    args.channels_set = {
        item.strip().lower()
        for item in str(args.channels).split(",")
        if item.strip()
    }
    if not args.channels_set:
        parser.error("channels must contain at least one channel")
    unknown = args.channels_set - CHANNELS
    if unknown:
        parser.error(f"unknown channels: {', '.join(sorted(unknown))}")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.mask_sample_radius < 0:
        parser.error("mask-sample-radius must be non-negative")
    if args.source_luma_min < 0.0 or args.source_luma_max > 255.0:
        parser.error("source luma bounds must be in [0, 255]")
    if args.source_luma_min > args.source_luma_max:
        parser.error("source-luma-min cannot exceed source-luma-max")
    if args.localized_reflectance_scale < 0.0:
        parser.error("localized-reflectance-scale must be non-negative")
    if args.localized_opacity_scale < 0.0 or args.localized_opacity_scale > 1.0:
        parser.error("localized-opacity-scale must be in [0, 1]")
    localize(args)


if __name__ == "__main__":
    main()
