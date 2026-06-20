#!/usr/bin/env python
"""Apply fitted Mitsuba response controls as a low-dimensional proxy composite."""

import argparse
import math
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

from build_bridge_review_package import (
    format_bytes,
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from validate_mitsuba_visual_cache_bundle import resolve_path


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to apply response controls")


def aov_path(frame, name):
    entry = ((frame.get("aovs") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def controls_by_output(spec):
    result = {}
    for control in spec.get("controls") or []:
        result.setdefault(control.get("output_frame"), []).append(control)
    return result


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        with open(src, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def control_color(control, args):
    strength = float(control.get("fit_strength") or 0.0) * args.gain
    if control.get("control_type") == "localized_light_or_glint":
        scale = strength * 255.0 * args.light_weight
        return (scale, scale * 0.92, scale * 0.72)
    if control.get("control_type") == "volume_or_material_response":
        scale = strength * 255.0 * args.material_weight
        return (scale * 0.70, scale * 0.82, scale)
    scale = strength * 255.0 * args.texture_weight
    return (scale, scale, scale)


def apply_control_pixels(pixels, width, height, control, args):
    x0, y0, x1, y1 = [int(round(value)) for value in (control.get("bbox") or [0, 0, -1, -1])]
    if x1 < x0 or y1 < y0:
        return 0
    x0 = max(0, min(width - 1, x0))
    x1 = max(0, min(width - 1, x1))
    y0 = max(0, min(height - 1, y0))
    y1 = max(0, min(height - 1, y1))
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    rx = max(1.0, (x1 - x0 + 1) * 0.5)
    ry = max(1.0, (y1 - y0 + 1) * 0.5)
    color = control_color(control, args)
    touched = 0
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        row = y * width
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx
            radius2 = dx * dx + dy * dy
            if radius2 > 1.0:
                continue
            falloff = (1.0 - radius2) ** args.falloff_power
            index = (row + x) * 3
            pixels[index] = min(255, int(round(pixels[index] + color[0] * falloff)))
            pixels[index + 1] = min(255, int(round(pixels[index + 1] + color[1] * falloff)))
            pixels[index + 2] = min(255, int(round(pixels[index + 2] + color[2] * falloff)))
            touched += 1
    return touched


def apply_controls(base, controls, args):
    image = base.convert("RGB")
    width, height = image.size
    pixels = bytearray(image.tobytes())
    touched = 0
    for control in controls:
        touched += apply_control_pixels(pixels, width, height, control, args)
    return Image.frombytes("RGB", image.size, bytes(pixels)), touched


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = width * index
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
        strip.paste(panel.convert("RGB"), (x, label_h))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)
    return strip


def html_page(title, summary, assets):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Control Proxy GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Control Proxy Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Controls", checks.get("controls_applied")),
            ("Touched", checks.get("max_touched_pixels")),
            ("Coverage", f"{checks.get('max_touched_coverage', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Control Proxy GIF"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #eaf5fb; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; }}
    p {{ margin: 0 0 16px; color: var(--muted); }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 18px; }}
    .hero {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; margin-bottom: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 6px; background: #0d1820; overflow: hidden; }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{title}</h1>
  <p>Low-dimensional proxy applying fitted response controls over base Mitsuba frames.</p>
  <section class="tiles">{tiles}</section>
  {hero}
  <section class="grid">{figures}</section>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Controls applied: `{checks.get('controls_applied')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max touched pixels: `{checks.get('max_touched_pixels')}`",
        f"- Max touched coverage: `{checks.get('max_touched_coverage')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Controls | Touched | Composite | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('controls_applied')} | "
            f"{frame.get('touched_pixels')} | `{frame.get('composite_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def apply_proxy(args):
    require_pillow()
    root = os.getcwd()
    spec_path = require_file(args.control_spec, "response control spec")
    aov_path_arg = require_file(args.aov_summary, "visual-cache AOV summary")
    spec = read_json(spec_path)
    aovs = read_json(aov_path_arg)
    if spec.get("schema") != "lsfs_mitsuba_response_control_spec":
        raise SystemExit(f"{args.control_spec}: expected lsfs_mitsuba_response_control_spec schema")
    if aovs.get("schema") != "lsfs_mitsuba_visual_cache_aov_package":
        raise SystemExit(f"{args.aov_summary}: expected lsfs_mitsuba_visual_cache_aov_package schema")

    controls_map = controls_by_output(spec)
    frames_by_output = output_frame_map(aovs.get("frames") or [])
    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    strip_dir = os.path.join(out_dir, "strips")
    frames = []
    strips = []
    missing = []
    for output_frame in sorted(frames_by_output):
        frame = frames_by_output[output_frame]
        controls = controls_map.get(output_frame, [])
        paths = {
            name: resolve_path(aov_path(frame, name), root)
            for name in ("base_rgb", "target_rgb")
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": output_frame, "missing": absent})
            continue
        base = Image.open(paths["base_rgb"]).convert("RGB")
        target = Image.open(paths["target_rgb"]).convert("RGB")
        composite, touched = apply_controls(base, controls, args)
        index = len(frames)
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        os.makedirs(os.path.dirname(composite_path), exist_ok=True)
        composite.save(composite_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        labeled_strip([base, composite, target], ["base", "control proxy", "target"], strip_path)
        strips.append(strip_path)
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": output_frame,
            "source_repo_path": posix_rel(paths["base_rgb"], root),
            "target_repo_path": posix_rel(paths["target_rgb"], root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "controls_applied": len(controls),
            "control_ids": [control.get("control_id") for control in controls],
            "touched_pixels": touched,
            "touched_coverage": touched / float(max(1, base.size[0] * base.size[1])),
            "response": {
                "changed_coverage": touched / float(max(1, base.size[0] * base.size[1])),
                "requests": len(controls),
                "max_layer_delta": int(round(max((control.get("fit_strength") or 0.0 for control in controls), default=0.0) * args.gain * 255.0)),
            },
        })

    if not frames:
        raise SystemExit("no frames were produced")
    gif_path = os.path.join(out_dir, "response_control_proxy.gif")
    gif_images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in strips]
    gif_images[0].save(gif_path, save_all=True, append_images=gif_images[1:], duration=int(1000 / args.fps), loop=0)

    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    key_indices = sorted(set([0, len(strips) // 2, len(strips) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "response_control_proxy.gif", "Control Proxy GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"control_proxy_strip_{out_index:02d}.png", f"Control Proxy Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    status = "ready" if not missing else "failed"
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_response_control_proxy",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "response_control_spec": {
            "path": spec_path,
            "repo_path": posix_rel(spec_path, root),
            "sha256": sha256_file(spec_path),
            "schema": spec.get("schema"),
            "status": spec.get("status"),
        },
        "visual_cache_aov_package": {
            "path": aov_path_arg,
            "repo_path": posix_rel(aov_path_arg, root),
            "sha256": sha256_file(aov_path_arg),
            "schema": aovs.get("schema"),
            "status": aovs.get("status"),
        },
        "proxy_settings": {
            "gain": args.gain,
            "light_weight": args.light_weight,
            "material_weight": args.material_weight,
            "texture_weight": args.texture_weight,
            "falloff_power": args.falloff_power,
        },
        "checks": {
            "frames": len(frames),
            "controls_applied": sum(frame.get("controls_applied", 0) for frame in frames),
            "missing_references": len(missing),
            "max_touched_pixels": max(frame.get("touched_pixels", 0) for frame in frames),
            "max_touched_coverage": max(frame.get("touched_coverage", 0.0) for frame in frames),
            "composite_bytes": sum(frame.get("size", 0) for frame in frames),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "frames": frames,
        "missing_references": missing,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_control_proxy_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={len(frames)} controls={summary['checks']['controls_applied']} "
        f"max_touched={summary['checks']['max_touched_pixels']} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply fitted Mitsuba response controls as a proxy")
    parser.add_argument("control_spec")
    parser.add_argument("aov_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--light-weight", type=float, default=1.0)
    parser.add_argument("--material-weight", type=float, default=0.7)
    parser.add_argument("--texture-weight", type=float, default=0.8)
    parser.add_argument("--falloff-power", type=float, default=1.5)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--title", default="Mitsuba Response Control Proxy")
    parser.add_argument(
        "--next",
        default="Compare this low-dimensional control proxy against the S473 AOV import and target-gap gates; then tune or move selected controls into renderer-native XML/materials.",
    )
    args = parser.parse_args(argv)
    for name in ("gain", "light_weight", "material_weight", "texture_weight", "falloff_power", "fps"):
        if getattr(args, name) <= 0.0:
            parser.error(f"{name.replace('_', '-')} must be positive")
    apply_proxy(args)


if __name__ == "__main__":
    main()
