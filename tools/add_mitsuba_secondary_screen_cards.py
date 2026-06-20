#!/usr/bin/env python
"""Add secondary alpha screen cards to an existing Mitsuba XML export."""

import argparse
import copy
import math
import os
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from build_mitsuba_renderer_target_preview import (
    Image,
    ImageFilter,
    ImageOps,
    require_pillow,
)


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def xml_path(path):
    return escape(os.path.abspath(path).replace(os.sep, "/"))


def vec_sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def vec_add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def vec_scale(a, value):
    return [float(a[i]) * float(value) for i in range(3)]


def vec_norm(a):
    length = math.sqrt(sum(float(item) * float(item) for item in a))
    if length <= 1e-9:
        raise ValueError("zero-length vector")
    return [float(item) / length for item in a]


def csv3(values):
    return ", ".join(f"{float(values[i]):.8g}" for i in range(3))


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
    return {frame.get("output_frame"): frame for frame in frames}


def build_mask(layer_path, out_path, args):
    layer = Image.open(layer_path).convert("RGBA")
    alpha = layer.getchannel("A")
    if args.mask_blur_radius > 0.0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(args.mask_blur_radius))
    if args.mask_gain != 1.0:
        alpha = alpha.point(lambda value: max(0, min(255, int(value * args.mask_gain))))
    if args.flip_y:
        alpha = ImageOps.flip(alpha)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    alpha.save(out_path)
    return {
        "path": out_path,
        "sha256": sha256_file(out_path),
        "size": os.path.getsize(out_path),
        "dimensions": list(alpha.size),
    }


def screen_card_block(mask_path, card_id, args, camera_position, camera_target, camera_up):
    view_dir = vec_norm(vec_sub(camera_target, camera_position))
    center = vec_add(camera_position, vec_scale(view_dir, args.card_distance))
    fov_y = math.radians(args.camera_fov)
    half_height = math.tan(fov_y * 0.5) * args.card_distance * args.card_scale
    aspect = float(args.film_width) / float(args.film_height)
    half_width = half_height * aspect
    reflectance = ", ".join(str(item).strip() for item in args.reflectance.split(","))
    lines = [
        f'  <bsdf type="mask" id="{card_id}_bsdf">',
        '    <texture type="bitmap" name="opacity">',
        f'      <string name="filename" value="{xml_path(mask_path)}"/>',
        '      <boolean name="raw" value="true"/>',
        '    </texture>',
        '    <bsdf type="diffuse">',
        f'      <rgb name="reflectance" value="{escape(reflectance)}"/>',
        '    </bsdf>',
        '  </bsdf>',
        '  <shape type="rectangle">',
        '    <transform name="to_world">',
        f'      <lookat origin="{csv3(center)}" target="{csv3(camera_position)}" up="{csv3(camera_up)}"/>',
        f'      <scale x="{half_width:.8g}" y="{half_height:.8g}" z="1"/>',
        '    </transform>',
        f'    <ref name="bsdf" id="{card_id}_bsdf"/>',
        '  </shape>',
    ]
    return "\n".join(lines), center, half_width, half_height


def insert_before_scene_end(xml_text, block):
    marker = "</scene>"
    index = xml_text.rfind(marker)
    if index < 0:
        raise ValueError("missing </scene> marker")
    return xml_text[:index] + block + "\n" + xml_text[index:]


def write_command_list(path, frames, command, mode):
    lines = []
    mode_arg = f" -m {mode}" if mode else ""
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


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    card = export.get("secondary_screen_card") or {}
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
        f"- Depth-aware composite: `{export['sources']['depth_aware_composite']['repo_path']}`",
        "",
        "## Screen Card",
        "",
        f"- Card distance: `{card.get('card_distance')}`",
        f"- Card scale: `{card.get('card_scale')}`",
        f"- Mask gain: `{card.get('mask_gain')}`",
        f"- Mask blur radius: `{card.get('mask_blur_radius')}`",
        f"- Flip Y: `{card.get('flip_y')}`",
        f"- Reflectance: `{card.get('reflectance')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Screen cards emitted: `{checks.get('secondary_screen_card_count')}`",
        f"- Screen card mask bytes: `{format_bytes(checks.get('secondary_screen_card_mask_bytes', 0))}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents |",
        "| ---: | --- | --- | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        card_frame = frame.get("secondary_screen_card") or {}
        lines.append(
            f"| {frame.get('output_frame')} | `{(frame.get('xml_scene') or {}).get('repo_path')}` | "
            f"`{card_frame.get('mask_repo_path')}` | {card_frame.get('mask_size')} | "
            f"`{card_frame.get('center')}` | `{card_frame.get('half_extents')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def add_cards(args):
    require_pillow()
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    bridge_path = require_file(args.depth_aware_composite, "depth-aware composite summary")
    base = read_json(base_export_path)
    bridge = read_json(bridge_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if bridge.get("schema") != "lsfs_mitsuba_depth_aware_secondary_composite":
        raise SystemExit(f"{args.depth_aware_composite}: expected lsfs_mitsuba_depth_aware_secondary_composite schema")
    if bridge.get("status") != "ready":
        raise SystemExit(f"{args.depth_aware_composite}: bridge status is {bridge.get('status')!r}")

    render_settings = base.get("render_settings") or {}
    camera_position = args.camera_position or render_settings.get("camera_position_override")
    camera_target = args.camera_target or render_settings.get("camera_target_override")
    camera_up = args.camera_up or render_settings.get("camera_up_override") or [0.0, 1.0, 0.0]
    camera_fov = args.camera_fov or render_settings.get("camera_fov_override")
    if not camera_position or not camera_target or not camera_fov:
        raise SystemExit("camera position, target, and fov must be available or supplied")
    args.camera_fov = float(camera_fov)

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    mask_dir = os.path.join(out_dir, "secondary_screen_masks")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(mask_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    bridge_frames = output_frame_map(bridge.get("frames") or [])
    frames = []
    failures = []
    mask_bytes = 0
    xml_bytes = 0
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        bridge_frame = bridge_frames.get(output_frame)
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        layer_path = resolve_path((bridge_frame or {}).get("secondary_layer_repo_path"))
        missing = []
        if not source_xml or not os.path.isfile(source_xml):
            missing.append({"role": "source_xml", "path": source_xml})
        if not layer_path or not os.path.isfile(layer_path):
            missing.append({"role": "secondary_layer", "path": layer_path})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        base_name = f"frame_{index:04d}"
        mask_path = os.path.join(mask_dir, f"{base_name}.png")
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        mask = build_mask(layer_path, mask_path, args)
        card_id = f"lsfs_secondary_screen_card_{index:04d}"
        block, center, half_width, half_height = screen_card_block(
            mask_path,
            card_id,
            args,
            [float(item) for item in camera_position],
            [float(item) for item in camera_target],
            [float(item) for item in camera_up],
        )
        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        patched = insert_before_scene_end(xml_text, block)
        with open(xml_out, "w", encoding="utf-8", newline="\n") as f:
            f.write(patched)
        mask_bytes += mask["size"]
        xml_bytes += os.path.getsize(xml_out)
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
        out_frame["secondary_screen_card"] = {
            "enabled": True,
            "source_secondary_layer_repo_path": posix_rel(layer_path, root),
            "mask_path": mask_path,
            "mask_repo_path": posix_rel(mask_path, root),
            "mask_sha256": mask["sha256"],
            "mask_size": mask["size"],
            "mask_dimensions": mask["dimensions"],
            "center": [round(item, 6) for item in center],
            "half_extents": [round(half_width, 6), round(half_height, 6)],
            "card_id": card_id,
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
        "status": "ready" if frames and not failures else "review",
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "depth_aware_composite": source_entry(bridge_path, root, "depth-aware composite summary", bridge),
        },
        "frames": frames,
        "failures": failures,
        "secondary_screen_card": {
            "enabled": True,
            "card_distance": args.card_distance,
            "card_scale": args.card_scale,
            "camera_fov": args.camera_fov,
            "film_width": args.film_width,
            "film_height": args.film_height,
            "mask_gain": args.mask_gain,
            "mask_blur_radius": args.mask_blur_radius,
            "flip_y": args.flip_y,
            "reflectance": args.reflectance,
        },
    })
    export["render_settings"]["secondary_screen_card_enabled"] = True
    export["render_settings"]["secondary_screen_card_distance"] = args.card_distance
    export["render_settings"]["secondary_screen_card_scale"] = args.card_scale
    export["render_settings"]["secondary_screen_card_mask_gain"] = args.mask_gain
    export["checks"] = copy.deepcopy(base.get("checks") or {})
    export["checks"].update({
        "frames_exported": len(frames),
        "missing_references": len(failures),
        "secondary_screen_card_count": len(frames),
        "secondary_screen_card_mask_bytes": mask_bytes,
        "xml_scene_bytes": xml_bytes,
    })
    export["next"] = args.next

    export_path = os.path.join(out_dir, "mitsuba_export.json")
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root, args.next))
    print(
        f"status={export['status']} frames={len(frames)} cards={len(frames)} "
        f"missing={len(failures)} export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def parse_vec3(value):
    if value is None:
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("expected three comma-separated numbers")
    return [float(part) for part in parts]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Add secondary alpha screen cards to a Mitsuba XML export")
    parser.add_argument("base_export")
    parser.add_argument("depth_aware_composite")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--card-distance", type=float, default=18.0)
    parser.add_argument("--card-scale", type=float, default=1.0)
    parser.add_argument("--mask-gain", type=float, default=0.6)
    parser.add_argument("--mask-blur-radius", type=float, default=1.5)
    parser.add_argument("--reflectance", default="0.70,0.84,0.96")
    parser.add_argument("--film-width", type=int, default=960)
    parser.add_argument("--film-height", type=int, default=540)
    parser.add_argument("--camera-position", type=parse_vec3)
    parser.add_argument("--camera-target", type=parse_vec3)
    parser.add_argument("--camera-up", type=parse_vec3)
    parser.add_argument("--camera-fov", type=float)
    parser.add_argument("--flip-y", action="store_true")
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Screen Card Export")
    parser.add_argument("--next", default="Render and compare this screen-card native candidate against the S344 gate.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("frames must be non-negative")
    if args.card_distance <= 0.0:
        parser.error("card-distance must be positive")
    if args.card_scale <= 0.0:
        parser.error("card-scale must be positive")
    if args.mask_gain <= 0.0:
        parser.error("mask-gain must be positive")
    if args.mask_blur_radius < 0.0:
        parser.error("mask-blur-radius must be non-negative")
    if args.film_width <= 0 or args.film_height <= 0:
        parser.error("film dimensions must be positive")
    add_cards(args)


if __name__ == "__main__":
    main()
