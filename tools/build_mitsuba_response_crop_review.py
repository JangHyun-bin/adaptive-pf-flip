#!/usr/bin/env python
"""Build crop/zoom review strips for Mitsuba response candidates."""

import argparse
import html
import os
import shutil
from datetime import datetime, timezone

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None

from apply_mitsuba_target_region_response import layer_path, output_frame_map, target_path, write_gif
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
from build_mitsuba_candidate_compare_gallery import (
    copy_asset,
    frame_map_from_candidate,
    parse_labeled_path,
    resolve_path,
    select_outputs,
    slug_label,
)
from build_mitsuba_water_material_aov_package import luma_array, mask_image


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a crop review")


def label_font(size=18):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def copy_json(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    return {
        "label": label,
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }


def target_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def crop_box_from_mask(mask, image_size, padding, min_width, min_height):
    height, width = mask.shape
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        cx, cy = width // 2, height // 2
        half_w, half_h = max(1, min_width // 2), max(1, min_height // 2)
        return (
            max(0, cx - half_w),
            max(0, cy - half_h),
            min(width, cx + half_w),
            min(height, cy + half_h),
        )
    left = max(0, int(xs.min()) - padding)
    right = min(width, int(xs.max()) + padding + 1)
    top = max(0, int(ys.min()) - padding)
    bottom = min(height, int(ys.max()) + padding + 1)
    if right - left < min_width:
        extra = min_width - (right - left)
        left = max(0, left - extra // 2)
        right = min(width, right + extra - extra // 2)
    if bottom - top < min_height:
        extra = min_height - (bottom - top)
        top = max(0, top - extra // 2)
        bottom = min(height, bottom + extra - extra // 2)
    if right - left < min_width:
        left = max(0, right - min_width)
    if bottom - top < min_height:
        top = max(0, bottom - min_height)
    return (left, top, right, bottom)


def crop_and_zoom(image, box, zoom):
    crop = image.crop(box)
    if zoom <= 1.0:
        return crop.convert("RGB")
    width, height = crop.size
    return crop.resize((int(round(width * zoom)), int(round(height * zoom))), Image.Resampling.NEAREST).convert("RGB")


def make_strip(columns, box, zoom, out_path):
    images = []
    for label, image in columns:
        images.append((label, crop_and_zoom(image, box, zoom)))
    width, height = images[0][1].size
    label_h = 34
    gap = 6
    strip = Image.new("RGB", (len(images) * width + (len(images) - 1) * gap, height + label_h), (10, 15, 19))
    draw = ImageDraw.Draw(strip)
    font = label_font()
    x = 0
    for label, image in images:
        draw.rectangle((x, 0, x + width, label_h), fill=(20, 30, 38))
        draw.text((x + 10, 8), label, fill=(232, 242, 248), font=font)
        strip.paste(image, (x, label_h))
        x += width + gap
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)
    for _label, image in images:
        image.close()
    return strip.size


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Crop Review GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks", {})
    tiles = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Columns", checks.get("columns")),
            ("Zoom", checks.get("zoom")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{html.escape(gif["href"])}" alt="Crop Review GIF"></section>' if gif else ""
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{html.escape(item['href'])}"><img src="{html.escape(item['href'])}" alt="{html.escape(item['label'])}"></a>
          <figcaption>{html.escape(item['label'])}</figcaption>
        </figure>"""
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #121b22; --ink: #edf7fb; --muted: #9fb2bf; --line: #2b3b47; --accent: #9ed8ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; max-width: none; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    figure {{ margin: 0 0 12px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section>{frame_html}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks", {})
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
        f"- Columns: `{checks.get('columns')}`",
        f"- Zoom: `{checks.get('zoom')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Columns",
        "",
    ]
    for column in summary.get("columns", []):
        lines.append(f"- `{column}`")
    lines.extend(["", "## Crops", "", "| Output | Box | Target dark coverage | Strip |", "| ---: | --- | ---: | --- |"])
    for frame in summary.get("frames", []):
        lines.append(
            f"| {frame['output_frame']} | `{frame['crop_box']}` | "
            f"{frame['target_dark_coverage']:.6f} | `{frame['strip']['repo_path']}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    target_summary_path = require_file(args.target_summary, "target summary")
    reference_summary_path = require_file(args.reference_summary, "reference summary")
    target_summary = read_json(target_summary_path)
    reference_summary = read_json(reference_summary_path)
    target_frames = target_frame_map(target_summary)
    reference_frames = output_frame_map(reference_summary.get("frames") or [])
    candidate_maps = []
    metadata_files = []

    out_dir = os.path.abspath(args.out_dir)
    assets_dir = os.path.join(out_dir, "gallery", "assets")
    strips_dir = os.path.join(out_dir, "strips")
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(strips_dir, exist_ok=True)

    for item in args.candidate:
        label, path = parse_labeled_path(item, "--candidate")
        candidate_path = require_file(path, f"{label} candidate summary")
        payload = read_json(candidate_path)
        candidate_maps.append((label, frame_map_from_candidate(payload, label, candidate_path), candidate_path))
        metadata_files.append(copy_json(candidate_path, assets_dir, f"{slug_label(label)}_candidate_summary.json", f"{label} candidate summary", root))
    metadata_files.append(copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root))
    metadata_files.append(copy_json(reference_summary_path, assets_dir, "reference_summary.json", "Reference summary", root))

    common_outputs = set(target_frames) & set(reference_frames)
    for _label, frame_map, _path in candidate_maps:
        common_outputs &= set(frame_map)
    outputs = select_outputs(common_outputs, args.frames)
    if not outputs:
        raise SystemExit("no common frames across target/reference/candidates")

    frame_records = []
    strip_paths = []
    columns = ["Target"] + [label for label, _frame_map, _path in candidate_maps] + ["Target Dark"]
    for index, output_frame in enumerate(outputs):
        target_frame = target_frames[output_frame]
        reference_frame = reference_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        layer_img_path = require_file(layer_path(reference_frame), "secondary layer")
        target_img = Image.open(target_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        target_luma = luma_array(target_img)
        alpha = np.asarray(layer_img.split()[3], dtype=np.uint8)
        target_dark = np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold)
        box = crop_box_from_mask(target_dark, target_img.size, args.padding, args.min_width, args.min_height)
        target_dark_img = mask_image(target_dark, on=(250, 80, 90))
        strip_columns = [("Target", target_img)]
        for label, frame_map, _path in candidate_maps:
            image = Image.open(require_file(frame_map[output_frame]["path"], f"{label} image")).convert("RGB")
            if image.size != target_img.size:
                image = image.resize(target_img.size, Image.Resampling.LANCZOS)
            strip_columns.append((label, image))
        strip_columns.append(("Target Dark", target_dark_img))
        strip_path = os.path.join(strips_dir, f"frame_{index:04d}_crop_review.png")
        strip_size = make_strip(strip_columns, box, args.zoom, strip_path)
        strip_paths.append(strip_path)
        for _label, image in strip_columns:
            image.close()
        frame_records.append({
            "frame": index,
            "output_frame": output_frame,
            "crop_box": list(box),
            "target_repo_path": posix_rel(target_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "target_dark_coverage": float(target_dark.sum()) / float(max(1, target_dark.size)),
            "strip": {
                "path": strip_path,
                "repo_path": posix_rel(strip_path, root),
                "sha256": sha256_file(strip_path),
                "size": os.path.getsize(strip_path),
                "dimensions": list(strip_size),
            },
        })

    gif_path = os.path.join(assets_dir, "crop_review.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "crop_review.gif", "Crop Review GIF", root)]
    for index, strip_path in enumerate(strip_paths):
        assets.append(copy_asset(strip_path, assets_dir, f"frame_{index:02d}_crop_review.png", f"Frame {index + 1} Crop", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "response_crop_review_summary.json")
    index_path = os.path.join(out_dir, "gallery", "index.html")
    summary = {
        "schema": "lsfs_mitsuba_response_crop_review",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "reference_summary": posix_rel(reference_summary_path, root),
        },
        "settings": {
            "frames": args.frames,
            "fps": args.fps,
            "zoom": args.zoom,
            "padding": args.padding,
            "min_width": args.min_width,
            "min_height": args.min_height,
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
        },
        "columns": columns,
        "checks": {
            "frames": len(frame_records),
            "columns": len(columns),
            "zoom": args.zoom,
            "gif_bytes": os.path.getsize(gif_path),
            "strip_bytes": sum(os.path.getsize(path) for path in strip_paths),
        },
        "frames": frame_records,
        "gallery": {},
        "next": args.next,
    }
    summary["gallery"] = {
        "path": os.path.dirname(index_path),
        "repo_path": posix_rel(os.path.dirname(index_path), root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "response_crop_review_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(out_dir, "gallery", "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_crop_review_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": summary["gallery"]["metadata_files"],
        "summary_repo_path": posix_rel(summary_path, root),
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(frame_records)} columns={len(columns)} "
        f"gif={os.path.getsize(gif_path)} gallery={summary['gallery']['index_repo_path']}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_summary")
    parser.add_argument("reference_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", action="append", required=True,
                        help="LABEL=summary.json for a secondary composite or composite-grade candidate")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--zoom", type=float, default=2.0)
    parser.add_argument("--padding", type=int, default=28)
    parser.add_argument("--min-width", type=int, default=220)
    parser.add_argument("--min-height", type=int, default=120)
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Response Crop Review")
    parser.add_argument("--next", default="Use crop review to decide whether the latest response should remain the visual baseline.")
    args = parser.parse_args()
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.zoom <= 0.0:
        parser.error("zoom must be positive")
    if args.padding < 0:
        parser.error("padding must be non-negative")
    if args.min_width <= 0 or args.min_height <= 0:
        parser.error("min crop dimensions must be positive")
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    return args


if __name__ == "__main__":
    build(parse_args())
