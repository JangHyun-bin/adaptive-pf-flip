#!/usr/bin/env python
"""Apply a lightweight cinematic grade to Mitsuba composite review frames."""

import argparse
import math
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageEnhance = None
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
        raise SystemExit("Pillow is required to grade Mitsuba composites")


def resolve_path(path):
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def parse_rgb(value):
    parts = [part.strip() for part in value.split(",")] if value else []
    if len(parts) != 3:
        raise ValueError("tone-rgb must contain three comma-separated integers")
    rgb = [int(part) for part in parts]
    if any(item < 0 or item > 255 for item in rgb):
        raise ValueError("tone-rgb values must be in [0, 255]")
    return tuple(rgb)


def luminance_mask(img, threshold, blur_radius):
    gray = ImageOps.grayscale(img)
    mask = gray.point(lambda value: max(0, min(255, int((value - threshold) * 255 / max(1, 255 - threshold)))))
    return mask.filter(ImageFilter.GaussianBlur(blur_radius))


def add_bloom(img, threshold, blur_radius, strength):
    if strength <= 0.0:
        return img
    mask = luminance_mask(img, threshold, blur_radius)
    glow = Image.new("RGB", img.size, (255, 255, 255))
    glow.putalpha(mask.point(lambda value: int(value * strength)))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def apply_tone(img, tone_rgb, strength):
    if strength <= 0.0:
        return img
    tone = Image.new("RGB", img.size, tone_rgb)
    toned = ImageChops.multiply(img, tone)
    return Image.blend(img, toned, strength)


def apply_vignette(img, strength, power):
    if strength <= 0.0:
        return img
    width, height = img.size
    mask = Image.new("L", img.size, 0)
    pixels = mask.load()
    cx = (width - 1) * 0.5
    cy = (height - 1) * 0.5
    max_dist = math.sqrt(cx * cx + cy * cy)
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max(1.0, max_dist)
            pixels[x, y] = int(max(0.0, min(1.0, dist ** power * strength)) * 255)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay.putalpha(mask.filter(ImageFilter.GaussianBlur(max(1, int(min(width, height) * 0.035)))))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def grade_image(path, out_path, args):
    img = Image.open(path).convert("RGB")
    if args.autocontrast_cutoff > 0.0:
        img = ImageOps.autocontrast(img, cutoff=args.autocontrast_cutoff)
    img = ImageEnhance.Brightness(img).enhance(args.exposure)
    img = ImageEnhance.Contrast(img).enhance(args.contrast)
    img = ImageEnhance.Color(img).enhance(args.saturation)
    img = apply_tone(img, args.tone_rgb, args.tone_strength)
    img = add_bloom(img, args.bloom_threshold, args.bloom_radius, args.bloom_strength)
    img = apply_vignette(img, args.vignette_strength, args.vignette_power)
    img = ImageEnhance.Sharpness(img).enhance(args.sharpness)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    dims = image_dimensions(dest)
    entry = {
        "label": label,
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    if dims:
        entry["dimensions"] = dims
    return entry


def write_gif(frame_paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    try:
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def html_page(title, assets, metadata_files, summary):
    gif = next((item for item in assets if item["label"] == "Shot GIF"), None)
    keyframes = [item for item in assets if item["label"].startswith("Keyframe")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    settings = summary["settings"]
    metrics = [
        ("Frames", summary["checks"].get("frames")),
        ("Contrast", settings.get("contrast")),
        ("Saturation", settings.get("saturation")),
        ("Bloom", settings.get("bloom_strength")),
        ("Vignette", settings.get("vignette_strength")),
        ("GIF", format_bytes(summary["checks"].get("gif_bytes", 0))),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    frames = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in keyframes
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Graded GIF"></section>' if gif else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d12; --panel: #101820; --ink: #ecf6fb; --muted: #a5b5bf; --line: #2d3c46; --accent: #a8dcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #0d1217; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section class="grid">{frames}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{summary['checks'].get('frames')}`",
        f"- GIF bytes: `{format_bytes(summary['checks'].get('gif_bytes', 0))}`",
        "",
        "## Settings",
        "",
    ]
    for key, value in summary.get("settings", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Frame Samples", "", "| Frame | Source | Graded |", "| ---: | --- | --- |"])
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(f"| {frame.get('frame')} | `{frame.get('source_repo_path')}` | `{frame.get('graded_repo_path')}` |")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def grade(args):
    require_pillow()
    root = os.getcwd()
    source_path = require_file(args.composite_summary, "composite summary")
    source = read_json(source_path)
    if source.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.composite_summary}: expected lsfs_mitsuba_secondary_composite schema")
    out_dir = os.path.abspath(args.out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    graded = []
    frame_paths = []
    for frame in source.get("frames") or []:
        src = require_file(frame.get("composite_repo_path"), "composite frame")
        out_path = os.path.join(frames_dir, f"frame_{frame.get('frame', len(graded)):04d}.png")
        grade_image(src, out_path, args)
        frame_paths.append(out_path)
        graded.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "source_repo_path": posix_rel(src, root),
            "graded_repo_path": posix_rel(out_path, root),
            "size": os.path.getsize(out_path),
            "sha256": sha256_file(out_path),
        })

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(frame_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Shot GIF", root)]
    key_indices = sorted(set(round(i * (len(frame_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if frame_paths else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(frame_paths[frame_index], assets_dir, f"keyframe_{out_index:02d}.png", f"Keyframe {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "grade_summary.json")
    source_asset = copy_asset(source_path, assets_dir, "secondary_composite_summary.json", "Composite summary", root)
    metadata_files = [source_asset]
    summary = {
        "schema": "lsfs_mitsuba_composite_grade",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "source": {
            "composite_summary": posix_rel(source_path, root),
        },
        "settings": {
            "exposure": args.exposure,
            "contrast": args.contrast,
            "saturation": args.saturation,
            "sharpness": args.sharpness,
            "autocontrast_cutoff": args.autocontrast_cutoff,
            "tone_rgb": list(args.tone_rgb),
            "tone_strength": args.tone_strength,
            "bloom_threshold": args.bloom_threshold,
            "bloom_radius": args.bloom_radius,
            "bloom_strength": args.bloom_strength,
            "vignette_strength": args.vignette_strength,
            "vignette_power": args.vignette_power,
            "fps": args.fps,
        },
        "checks": {
            "frames": len(graded),
            "gif_bytes": os.path.getsize(gif_path),
            "graded_frame_bytes": sum(item["size"] for item in graded),
        },
        "gallery": {},
        "frames": graded,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "grade_summary.json", "Grade summary", root)
    metadata_files.insert(0, summary_asset)
    index_path = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, metadata_files, summary))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_composite_grade_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(f"status=ok frames={len(graded)} gif={gif_path} summary={summary_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Grade Mitsuba composite review frames")
    parser.add_argument("composite_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--exposure", type=float, default=0.96)
    parser.add_argument("--contrast", type=float, default=1.28)
    parser.add_argument("--saturation", type=float, default=1.16)
    parser.add_argument("--sharpness", type=float, default=1.04)
    parser.add_argument("--autocontrast-cutoff", type=float, default=0.25)
    parser.add_argument("--tone-rgb", default="216,232,242")
    parser.add_argument("--tone-strength", type=float, default=0.12)
    parser.add_argument("--bloom-threshold", type=int, default=205)
    parser.add_argument("--bloom-radius", type=float, default=6.0)
    parser.add_argument("--bloom-strength", type=float, default=0.16)
    parser.add_argument("--vignette-strength", type=float, default=0.32)
    parser.add_argument("--vignette-power", type=float, default=1.9)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Composite Grade")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this grade as a visual review proof.")
    args = parser.parse_args(argv)
    try:
        args.tone_rgb = parse_rgb(args.tone_rgb)
    except ValueError as exc:
        parser.error(str(exc))
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.autocontrast_cutoff < 0.0:
        parser.error("autocontrast-cutoff must be non-negative")
    grade(args)


if __name__ == "__main__":
    main()
