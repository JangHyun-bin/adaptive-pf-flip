"""Patch a Mitsuba XML export with source-response material modulation."""

import argparse
import copy
import os
import re
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


MASK_SCHEMAS = {
    "lsfs_mitsuba_secondary_composite",
    "lsfs_mitsuba_source_response_mask_source",
}
SECONDARY_SUFFIXES = ("", "_billboard", "_halo", "_mist")


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


def parse_vec3(value, label):
    parts = [part.strip() for part in str(value).split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{label} must be r,g,b")
    return [float(part) for part in parts]


def csv3(values):
    return ", ".join(fmt(item) for item in values)


def coverage(frame):
    return float((frame or {}).get("layer_coverage") or 0.0)


def normalized(value, maximum):
    if maximum <= 0.0:
        return 0.0
    return clamp(value / maximum, 0.0, 1.0)


def scale_rgb_text(value, scale):
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 3:
        return value
    return csv3([clamp(part * scale, 0.0, 4.0) for part in parts])


def read_water_alpha(xml_text, fallback):
    match = re.search(
        r'<bsdf\s+type="roughdielectric"\s+id="lsfs_water_surface">.*?'
        r'<float\s+name="alpha"\s+value="([^"]+)"',
        xml_text,
        flags=re.DOTALL,
    )
    if not match:
        return fallback
    try:
        return float(match.group(1))
    except ValueError:
        return fallback


def replace_water_alpha(xml_text, water_alpha):
    pattern = (
        r'(<bsdf\s+type="roughdielectric"\s+id="lsfs_water_surface">.*?'
        r'<float\s+name="alpha"\s+value=")([^"]+)(")'
    )

    def repl(match):
        return f"{match.group(1)}{fmt(water_alpha)}{match.group(3)}"

    return re.subn(pattern, repl, xml_text, count=1, flags=re.DOTALL)


def scale_secondary_reflectance(xml_text, channels, scale):
    replacements = 0
    for channel in channels:
        for suffix in SECONDARY_SUFFIXES:
            bsdf_id = f"lsfs_secondary_{channel}{suffix}"
            pattern = (
                rf'(<bsdf\s+type="(?:mask|diffuse)"\s+id="{re.escape(bsdf_id)}">.*?'
                r'<rgb\s+name="reflectance"\s+value=")([^"]+)(")'
            )

            def repl(match):
                return f"{match.group(1)}{scale_rgb_text(match.group(2), scale)}{match.group(3)}"

            xml_text, count = re.subn(pattern, repl, xml_text, count=1, flags=re.DOTALL)
            replacements += count
    return xml_text, replacements


def scale_secondary_opacity(xml_text, channels, scale):
    replacements = 0
    for channel in channels:
        for suffix in SECONDARY_SUFFIXES:
            bsdf_id = f"lsfs_secondary_{channel}{suffix}"
            pattern = (
                rf'(<bsdf\s+type="mask"\s+id="{re.escape(bsdf_id)}">.*?'
                r'<float\s+name="opacity"\s+value=")([^"]+)(")'
            )

            def repl(match):
                try:
                    opacity = float(match.group(2))
                except ValueError:
                    return match.group(0)
                return f"{match.group(1)}{fmt(clamp(opacity * scale, 0.0, 1.0))}{match.group(3)}"

            xml_text, count = re.subn(pattern, repl, xml_text, count=1, flags=re.DOTALL)
            replacements += count
    return xml_text, replacements


def key_light_block(args, radiance):
    if max(radiance) <= 0.0:
        return ""
    return "\n".join([
        "  <shape type=\"rectangle\" id=\"lsfs_s412_material_response_key_light\">",
        "    <transform name=\"to_world\">",
        f"      <lookat origin=\"{csv3(args.key_light_position_vec)}\" target=\"{csv3(args.key_light_target_vec)}\" up=\"0, 1, 0\"/>",
        f"      <scale x=\"{fmt(args.key_light_scale_vec[0])}\" y=\"{fmt(args.key_light_scale_vec[1])}\"/>",
        "    </transform>",
        "    <emitter type=\"area\">",
        f"      <rgb name=\"radiance\" value=\"{csv3(radiance)}\"/>",
        "    </emitter>",
        "  </shape>",
    ])


def insert_key_light(xml_text, block):
    if not block:
        return xml_text, 0
    marker = '<bsdf type="roughdielectric" id="lsfs_water_surface">'
    index = xml_text.find(marker)
    if index < 0:
        marker = "</scene>"
        index = xml_text.rfind(marker)
    if index < 0:
        raise ValueError("missing scene insertion point")
    return xml_text[:index] + block + "\n" + xml_text[index:], 1


def add_response_comment(xml_text, comment):
    prefix = "<?xml"
    if xml_text.startswith(prefix):
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


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    settings = export.get("material_response") or {}
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
        f"- Channel mask source: `{export['sources']['channel_mask_source']['repo_path']}`",
        f"- Highlight mask source: `{export['sources']['highlight_mask_source']['repo_path']}`",
        "",
        "## Material Response",
        "",
        f"- Secondary channels: `{settings.get('secondary_channels')}`",
        f"- Secondary reflectance drop: `{settings.get('secondary_reflectance_drop')}`",
        f"- Secondary opacity drop: `{settings.get('secondary_opacity_drop')}`",
        f"- Water alpha drop: `{settings.get('water_alpha_drop')}`",
        f"- Water alpha min: `{settings.get('water_alpha_min')}`",
        f"- Highlight key light max radiance: `{settings.get('highlight_key_light_radiance')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        f"- Water alpha replacements: `{checks.get('water_alpha_replacements')}`",
        f"- Secondary reflectance replacements: `{checks.get('secondary_reflectance_replacements')}`",
        f"- Secondary opacity replacements: `{checks.get('secondary_opacity_replacements')}`",
        f"- Key lights inserted: `{checks.get('key_lights_inserted')}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        response = frame.get("material_response") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {response.get('channel_coverage')} | "
            f"{response.get('highlight_coverage')} | {response.get('water_alpha')} | "
            f"{response.get('secondary_reflectance_scale')} | {response.get('secondary_opacity_scale')} | "
            f"`{response.get('highlight_key_light_radiance')}` | "
            f"`{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def modulate(args):
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    channel_path = require_file(args.channel_mask_source, "channel mask source")
    highlight_path = require_file(args.highlight_mask_source, "highlight mask source")
    base = read_json(base_export_path)
    channel_source = read_json(channel_path)
    highlight_source = read_json(highlight_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    for label, payload, path in (
        ("channel", channel_source, channel_path),
        ("highlight", highlight_source, highlight_path),
    ):
        if payload.get("schema") not in MASK_SCHEMAS:
            expected = ", ".join(sorted(MASK_SCHEMAS))
            raise SystemExit(f"{path}: expected one of {expected} for {label} mask")
        if payload.get("status") and payload.get("status") != "ready":
            raise SystemExit(f"{path}: {label} mask status is {payload.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    channel_frames = output_frame_map(channel_source.get("frames") or [])
    highlight_frames = output_frame_map(highlight_source.get("frames") or [])
    max_channel = float(((channel_source.get("checks") or {}).get("max_mask_coverage")) or 0.0)
    max_highlight = float(((highlight_source.get("checks") or {}).get("max_mask_coverage")) or 0.0)
    if max_channel <= 0.0:
        max_channel = max((coverage(frame) for frame in channel_frames.values()), default=0.0)
    if max_highlight <= 0.0:
        max_highlight = max((coverage(frame) for frame in highlight_frames.values()), default=0.0)

    frames = []
    failures = []
    xml_bytes = 0
    water_replacements = 0
    reflectance_replacements = 0
    opacity_replacements = 0
    key_lights = 0
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        channel_frame = channel_frames.get(output_frame)
        highlight_frame = highlight_frames.get(output_frame)
        missing = []
        if not source_xml or not os.path.isfile(source_xml):
            missing.append({"role": "source_xml", "path": source_xml})
        if channel_frame is None:
            missing.append({"role": "channel_mask_frame", "output_frame": output_frame})
        if highlight_frame is None:
            missing.append({"role": "highlight_mask_frame", "output_frame": output_frame})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        channel_cov = coverage(channel_frame)
        highlight_cov = coverage(highlight_frame)
        channel_norm = normalized(channel_cov, max_channel)
        highlight_norm = normalized(highlight_cov, max_highlight)
        base_alpha = read_water_alpha(xml_text, args.water_alpha_base)
        water_alpha = max(args.water_alpha_min, base_alpha * (1.0 - args.water_alpha_drop * highlight_norm))
        secondary_reflectance_scale = 1.0 - args.secondary_reflectance_drop * channel_norm
        secondary_opacity_scale = 1.0 - args.secondary_opacity_drop * channel_norm
        secondary_reflectance_scale = clamp(secondary_reflectance_scale, args.secondary_scale_min, args.secondary_scale_max)
        secondary_opacity_scale = clamp(secondary_opacity_scale, args.secondary_opacity_scale_min, args.secondary_opacity_scale_max)
        key_radiance = [
            value * args.highlight_key_light_strength * highlight_norm
            for value in args.highlight_key_light_radiance_vec
        ]

        patched, count = replace_water_alpha(xml_text, water_alpha)
        water_replacements += count
        patched, count = scale_secondary_reflectance(patched, args.secondary_channels_set, secondary_reflectance_scale)
        reflectance_replacements += count
        patched, count = scale_secondary_opacity(patched, args.secondary_channels_set, secondary_opacity_scale)
        opacity_replacements += count
        patched, count = insert_key_light(patched, key_light_block(args, key_radiance))
        key_lights += count
        patched = add_response_comment(
            patched,
            f"<!-- S412 material_response channel_norm={channel_norm:.6f} "
            f"highlight_norm={highlight_norm:.6f} -->",
        )

        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
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
        out_frame["material_response"] = {
            "enabled": True,
            "channel_mask_layer_repo_path": channel_frame.get("layer_repo_path"),
            "highlight_mask_layer_repo_path": highlight_frame.get("layer_repo_path"),
            "channel_coverage": channel_cov,
            "highlight_coverage": highlight_cov,
            "channel_norm": channel_norm,
            "highlight_norm": highlight_norm,
            "base_water_alpha": base_alpha,
            "water_alpha": water_alpha,
            "secondary_reflectance_scale": secondary_reflectance_scale,
            "secondary_opacity_scale": secondary_opacity_scale,
            "highlight_key_light_radiance": key_radiance,
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
            "channel_mask_source": source_entry(channel_path, root, "channel source-response mask", channel_source),
            "highlight_mask_source": source_entry(highlight_path, root, "highlight source-response mask", highlight_source),
        },
        "frames": frames,
        "failures": failures,
        "material_response": {
            "enabled": True,
            "secondary_channels": sorted(args.secondary_channels_set),
            "secondary_reflectance_drop": args.secondary_reflectance_drop,
            "secondary_opacity_drop": args.secondary_opacity_drop,
            "secondary_scale_min": args.secondary_scale_min,
            "secondary_scale_max": args.secondary_scale_max,
            "secondary_opacity_scale_min": args.secondary_opacity_scale_min,
            "secondary_opacity_scale_max": args.secondary_opacity_scale_max,
            "water_alpha_base": args.water_alpha_base,
            "water_alpha_drop": args.water_alpha_drop,
            "water_alpha_min": args.water_alpha_min,
            "highlight_key_light_strength": args.highlight_key_light_strength,
            "highlight_key_light_radiance": args.highlight_key_light_radiance_vec,
            "key_light_position": args.key_light_position_vec,
            "key_light_target": args.key_light_target_vec,
            "key_light_scale": args.key_light_scale_vec,
            "max_channel_coverage": max_channel,
            "max_highlight_coverage": max_highlight,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["material_response_enabled"] = True
    export["render_settings"]["material_response_secondary_channels"] = sorted(args.secondary_channels_set)
    export["checks"] = copy.deepcopy(base.get("checks") or {})
    export["checks"].update({
        "frames_exported": len(frames),
        "missing_references": len(failures),
        "xml_scene_bytes": xml_bytes,
        "water_alpha_replacements": water_replacements,
        "secondary_reflectance_replacements": reflectance_replacements,
        "secondary_opacity_replacements": opacity_replacements,
        "key_lights_inserted": key_lights,
    })

    export_path = os.path.join(out_dir, "mitsuba_export.json")
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root, args.next))
    print(
        f"status={export['status']} frames={len(frames)} "
        f"key_lights={key_lights} xml_bytes={xml_bytes} export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply S410-style source masks as Mitsuba material/light modulation")
    parser.add_argument("base_export")
    parser.add_argument("channel_mask_source")
    parser.add_argument("highlight_mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--secondary-channels", default="spray,foam")
    parser.add_argument("--secondary-reflectance-drop", type=float, default=0.45)
    parser.add_argument("--secondary-opacity-drop", type=float, default=0.30)
    parser.add_argument("--secondary-scale-min", type=float, default=0.45)
    parser.add_argument("--secondary-scale-max", type=float, default=1.25)
    parser.add_argument("--secondary-opacity-scale-min", type=float, default=0.45)
    parser.add_argument("--secondary-opacity-scale-max", type=float, default=1.0)
    parser.add_argument("--water-alpha-base", type=float, default=0.014)
    parser.add_argument("--water-alpha-drop", type=float, default=0.45)
    parser.add_argument("--water-alpha-min", type=float, default=0.006)
    parser.add_argument("--highlight-key-light-radiance", default="0.10,0.13,0.17")
    parser.add_argument("--highlight-key-light-strength", type=float, default=1.0)
    parser.add_argument("--key-light-position", default="18,30,36")
    parser.add_argument("--key-light-target", default="18,8,14")
    parser.add_argument("--key-light-scale", default="12,6")
    parser.add_argument("--report")
    parser.add_argument("--title", default="S412 Mitsuba Material Response")
    parser.add_argument("--next", default="Render and compare this material/export-side response against SS1, S409 SF12_H18, and S401 CR21.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)

    args.secondary_channels_set = {
        item.strip().lower()
        for item in str(args.secondary_channels).split(",")
        if item.strip()
    }
    valid_channels = {"spray", "foam", "bubble", "droplet"}
    if not args.secondary_channels_set:
        parser.error("secondary-channels must contain at least one channel")
    unknown = args.secondary_channels_set - valid_channels
    if unknown:
        parser.error(f"unknown secondary channels: {', '.join(sorted(unknown))}")
    for name in (
        "secondary_reflectance_drop",
        "secondary_opacity_drop",
        "water_alpha_drop",
        "highlight_key_light_strength",
    ):
        if getattr(args, name) < 0.0:
            parser.error(f"{name.replace('_', '-')} must be non-negative")
    if args.water_alpha_base <= 0.0 or args.water_alpha_min <= 0.0:
        parser.error("water alpha values must be positive")
    if args.water_alpha_min > args.water_alpha_base:
        parser.error("water-alpha-min cannot exceed water-alpha-base")
    if args.secondary_scale_min < 0.0 or args.secondary_scale_max <= 0.0:
        parser.error("secondary reflectance scale bounds must be non-negative")
    if args.secondary_scale_min > args.secondary_scale_max:
        parser.error("secondary-scale-min cannot exceed secondary-scale-max")
    if args.secondary_opacity_scale_min < 0.0 or args.secondary_opacity_scale_max > 1.0:
        parser.error("secondary opacity scale bounds must stay in [0, 1]")
    if args.secondary_opacity_scale_min > args.secondary_opacity_scale_max:
        parser.error("secondary-opacity-scale-min cannot exceed secondary-opacity-scale-max")
    args.highlight_key_light_radiance_vec = parse_vec3(args.highlight_key_light_radiance, "highlight-key-light-radiance")
    args.key_light_position_vec = parse_vec3(args.key_light_position, "key-light-position")
    args.key_light_target_vec = parse_vec3(args.key_light_target, "key-light-target")
    args.key_light_scale_vec = [float(part.strip()) for part in str(args.key_light_scale).split(",")]
    if len(args.key_light_scale_vec) != 2 or min(args.key_light_scale_vec) <= 0.0:
        parser.error("key-light-scale must be two positive comma-separated numbers")
    if min(args.highlight_key_light_radiance_vec) < 0.0:
        parser.error("highlight-key-light-radiance values must be non-negative")
    modulate(args)


if __name__ == "__main__":
    main()
