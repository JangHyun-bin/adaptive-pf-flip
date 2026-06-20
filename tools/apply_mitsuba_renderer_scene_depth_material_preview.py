#!/usr/bin/env python
"""Apply a bounded scene-depth material preview over a renderer handoff."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None
    ImageOps = None

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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to apply scene-depth material previews")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def clamp_byte(value):
    return max(0, min(255, int(round(value))))


def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def finite(value):
    return isinstance(value, (int, float))


def metric_bounds(frames, key):
    values = [float(frame.get(key)) for frame in frames if finite(frame.get(key))]
    if not values:
        return (0.0, 1.0)
    lo = min(values)
    hi = max(values)
    if hi <= lo:
        hi = lo + 1.0
    return (lo, hi)


def normalized(value, bounds):
    if not finite(value):
        return 0.0
    lo, hi = bounds
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (float(value) - lo) / (hi - lo)))


def texture_ref(frame, role):
    return ((frame.get("textures") or {}).get(role) or {}).get("path") or ((frame.get("textures") or {}).get(role) or {}).get("repo_path")


def consumer_ref(frame, role):
    return (((frame.get("consumer") or {}).get(role) or {}).get("path") or
            ((frame.get("consumer") or {}).get(role) or {}).get("repo_path"))


def render_data_by_output(render_data):
    return {frame.get("output_frame"): frame for frame in render_data.get("frames") or []}


def preview_image(base, magnitude, strength):
    base = base.convert("RGB")
    mask = magnitude.convert("L").filter(ImageFilter.GaussianBlur(radius=2.0))
    base_bytes = base.tobytes()
    mask_bytes = mask.tobytes()
    out = bytearray(len(base_bytes))
    max_delta = 0
    total_delta = 0
    changed = 0
    for pixel, idx in enumerate(range(0, len(base_bytes), 3)):
        r = base_bytes[idx]
        g = base_bytes[idx + 1]
        b = base_bytes[idx + 2]
        lum = luma(r, g, b) / 255.0
        mask_weight = (mask_bytes[pixel] / 255.0) ** 0.7
        shadow_weight = 0.35 + 0.65 * (1.0 - lum)
        f = strength * mask_weight * shadow_weight
        nr = clamp_byte(r * (1.0 - 0.22 * f))
        ng = clamp_byte(g * (1.0 - 0.07 * f) + 5.0 * f)
        nb = clamp_byte(b * (1.0 + 0.10 * f) + 18.0 * f)
        out[idx] = nr
        out[idx + 1] = ng
        out[idx + 2] = nb
        delta = max(abs(nr - r), abs(ng - g), abs(nb - b))
        if delta:
            changed += 1
        max_delta = max(max_delta, delta)
        total_delta += abs(nr - r) + abs(ng - g) + abs(nb - b)
    pixels = max(1, len(mask_bytes))
    return Image.frombytes("RGB", base.size, bytes(out)), {
        "max_abs_delta": max_delta,
        "mean_abs_delta": total_delta / float(max(1, len(base_bytes))),
        "changed_coverage": changed / float(pixels),
    }


def diff_image(a, b):
    a_bytes = a.convert("RGB").tobytes()
    b_bytes = b.convert("RGB").tobytes()
    out = bytearray(len(a_bytes))
    for idx in range(0, len(a_bytes), 3):
        out[idx] = min(255, abs(a_bytes[idx] - b_bytes[idx]) * 16)
        out[idx + 1] = min(255, abs(a_bytes[idx + 1] - b_bytes[idx + 1]) * 16)
        out[idx + 2] = min(255, abs(a_bytes[idx + 2] - b_bytes[idx + 2]) * 16)
    return Image.frombytes("RGB", a.size, bytes(out))


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


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def copy_asset(src, assets_dir, name, label, root):
    resolved = require_file(src, label)
    os.makedirs(assets_dir, exist_ok=True)
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(resolved) != os.path.abspath(dest):
        with open(resolved, "rb") as f_in, open(dest, "wb") as f_out:
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


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item["label"] == "Depth Material Preview GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Depth Material Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Max delta", checks.get("max_abs_delta")),
            ("Mean delta", f"{checks.get('max_mean_abs_delta', 0.0):.4f}"),
            ("Coverage", f"{checks.get('max_changed_coverage', 0.0):.4f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="depth material preview gif"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 16px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; overflow-x: auto; margin: 0 0 12px; }}
    img {{ display: block; max-width: none; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Bounded post-tonemap probe driven by S580 water-depth profile and localized with the S578 low-frequency magnitude texture.</p>
  <section class="tiles">{tiles}</section>
  {hero}
  <section>{figures}</section>
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
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max absolute delta: `{checks.get('max_abs_delta')}`",
        f"- Max mean absolute delta: `{checks.get('max_mean_abs_delta')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        f"- Max abs tolerance: `{checks.get('max_abs_tolerance')}`",
        f"- Mean abs tolerance: `{checks.get('mean_abs_tolerance')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Strength | Z Factor | Max Delta | Mean Delta | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('strength')} | "
            f"{frame.get('water_z_factor')} | {frame.get('max_abs_delta')} | {frame.get('mean_abs_delta')} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def apply_preview(args):
    require_pillow()
    root = os.getcwd()
    handoff_path = require_file(args.handoff_manifest, "renderer scene-cache handoff")
    render_data_path = require_file(args.render_data_summary, "render data summary")
    handoff = read_json(handoff_path)
    render_data = read_json(render_data_path)
    if handoff.get("schema") != "lsfs_mitsuba_renderer_scene_cache_handoff":
        raise SystemExit(f"{args.handoff_manifest}: expected lsfs_mitsuba_renderer_scene_cache_handoff schema")
    if render_data.get("schema") != "lsfs_render_data_summary":
        raise SystemExit(f"{args.render_data_summary}: expected lsfs_render_data_summary schema")

    out_dir = os.path.abspath(args.out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    strips_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (frames_dir, strips_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    data_by_output = render_data_by_output(render_data)
    data_frames = render_data.get("frames") or []
    y_bounds = metric_bounds(data_frames, "water_depth_y_span")
    z_bounds = metric_bounds(data_frames, "water_depth_z_span")
    frames = []
    missing = []
    preview_paths = []
    strip_paths = []
    for index, frame in enumerate(handoff.get("frames") or []):
        output = frame.get("output_frame")
        data = data_by_output.get(output, {})
        composite_path = resolve_path(consumer_ref(frame, "composite"), root)
        magnitude_path = resolve_path(texture_ref(frame, "applied_magnitude_luma"), root)
        absent = []
        if not composite_path or not os.path.isfile(composite_path):
            absent.append("consumer_composite")
        if not magnitude_path or not os.path.isfile(magnitude_path):
            absent.append("applied_magnitude_luma")
        if absent:
            missing.append({"frame": index, "output_frame": output, "missing": absent})
            continue
        base = Image.open(composite_path).convert("RGB")
        magnitude = Image.open(magnitude_path).convert("L")
        if base.size != magnitude.size:
            raise SystemExit(f"frame {index}: base and magnitude dimensions differ")
        y_factor = normalized(data.get("water_depth_y_span"), y_bounds)
        z_factor = normalized(data.get("water_depth_z_span"), z_bounds)
        strength = args.max_strength * (0.30 + 0.45 * z_factor + 0.25 * y_factor)
        preview, stats = preview_image(base, magnitude, strength)
        preview_path = os.path.join(frames_dir, f"frame_{index:04d}.png")
        preview.save(preview_path)
        mask_visual = ImageOps.colorize(magnitude, black=(6, 12, 18), white=(255, 218, 120))
        diff = diff_image(preview, base)
        strip_path = os.path.join(strips_dir, f"frame_{index:04d}_depth_material_preview.png")
        labeled_strip(
            [base, mask_visual, preview, diff],
            ["accepted input", "lf magnitude mask", "depth material preview", "preview diff x16"],
            strip_path,
        )
        preview_paths.append(preview_path)
        strip_paths.append(strip_path)
        frames.append({
            "frame": index,
            "output_frame": output,
            "source_composite_repo_path": posix_rel(composite_path, root),
            "magnitude_repo_path": posix_rel(magnitude_path, root),
            "preview_repo_path": posix_rel(preview_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "strength": strength,
            "water_y_factor": y_factor,
            "water_z_factor": z_factor,
            "max_abs_delta": stats["max_abs_delta"],
            "mean_abs_delta": stats["mean_abs_delta"],
            "changed_coverage": stats["changed_coverage"],
            "sha256": sha256_file(preview_path),
            "size": os.path.getsize(preview_path),
        })

    if not frames:
        raise SystemExit("no depth material preview frames were produced")
    gif_path = os.path.join(out_dir, "depth_material_preview.gif")
    write_gif(preview_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "depth_material_preview.gif", "Depth Material Preview GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"depth_material_strip_{out_index:02d}.png", f"Depth Material Strip {out_index + 1}", root))
    metadata_files = [
        copy_asset(handoff_path, assets_dir, "renderer_scene_cache_handoff_summary.json", "Renderer scene-cache handoff", root),
        copy_asset(render_data_path, assets_dir, "render_data_summary.json", "Render data summary", root),
    ]
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "max_abs_delta": max((frame["max_abs_delta"] for frame in frames), default=0),
        "max_mean_abs_delta": max((frame["mean_abs_delta"] for frame in frames), default=0.0),
        "max_changed_coverage": max((frame["changed_coverage"] for frame in frames), default=0.0),
        "gif_bytes": os.path.getsize(gif_path),
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
    status = "ready"
    if missing:
        status = "failed"
    if checks["max_abs_delta"] > args.max_abs_tolerance:
        status = "failed"
    if checks["max_mean_abs_delta"] > args.mean_abs_tolerance:
        status = "failed"
    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_preview",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "inputs": {
            "handoff_manifest": posix_rel(handoff_path, root),
            "render_data_summary": posix_rel(render_data_path, root),
        },
        "settings": {
            "max_strength": args.max_strength,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "depth_material_preview_summary.json", "Depth material preview summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_preview_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} max_delta={checks['max_abs_delta']} "
        f"max_mean={checks['max_mean_abs_delta']:.6f} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply a bounded scene-depth material preview")
    parser.add_argument("handoff_manifest")
    parser.add_argument("render_data_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--max-strength", type=float, default=0.22)
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=8)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.8)
    parser.add_argument("--title", default="S582 Mitsuba Renderer Scene Depth Material Preview")
    parser.add_argument(
        "--next",
        default="Compare this bounded preview against the accepted S577 composite; only promote settings if the visual gain is visible without increasing accepted-reference gap beyond tolerance.",
    )
    args = parser.parse_args(argv)
    if args.max_strength <= 0.0 or args.max_strength > 1.0:
        parser.error("max-strength must be in (0, 1.0]")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    apply_preview(args)


if __name__ == "__main__":
    main()
