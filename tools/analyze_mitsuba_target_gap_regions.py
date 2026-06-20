#!/usr/bin/env python
"""Analyze Mitsuba target gaps by simple image regions."""

import argparse
import csv
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
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


REGIONS = ("all", "secondary", "nonsecondary", "highlight", "secondary_dark_target")


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze Mitsuba target gap regions")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def target_path(frame):
    return frame.get("renderer_target_path") or frame.get("renderer_target_repo_path")


def composite_path(frame):
    return frame.get("composite_path") or frame.get("composite_repo_path")


def layer_path(frame):
    return frame.get("layer_path") or frame.get("layer_repo_path")


def luminance(pixel):
    return 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]


def rgb_pixels(image):
    data = image.convert("RGB").tobytes()
    return list(zip(data[0::3], data[1::3], data[2::3]))


def alpha_pixels(image):
    return list(image.convert("L").tobytes())


def empty_stats(name, total_pixels):
    return {
        "region": name,
        "pixels": 0,
        "coverage": 0.0,
        "mean_abs_diff": 0.0,
        "max_abs_diff": 0,
        "target_luma_mean": 0.0,
        "actual_luma_mean": 0.0,
        "signed_luma_mean": 0.0,
        "total_pixels": total_pixels,
    }


def region_stats(name, target_pixels, actual_pixels, alpha_pixels, args, predicate):
    total_pixels = len(target_pixels)
    count = 0
    abs_sum = 0.0
    max_diff = 0
    target_luma_sum = 0.0
    actual_luma_sum = 0.0
    signed_luma_sum = 0.0
    for target, actual, alpha in zip(target_pixels, actual_pixels, alpha_pixels):
        target_luma = luminance(target)
        actual_luma = luminance(actual)
        if not predicate(target_luma, actual_luma, alpha):
            continue
        diffs = [abs(actual[i] - target[i]) for i in range(3)]
        count += 1
        abs_sum += sum(diffs) / 3.0
        max_diff = max(max_diff, max(diffs))
        target_luma_sum += target_luma
        actual_luma_sum += actual_luma
        signed_luma_sum += actual_luma - target_luma
    if count <= 0:
        return empty_stats(name, total_pixels)
    return {
        "region": name,
        "pixels": count,
        "coverage": count / float(max(1, total_pixels)),
        "mean_abs_diff": abs_sum / float(count),
        "max_abs_diff": max_diff,
        "target_luma_mean": target_luma_sum / float(count),
        "actual_luma_mean": actual_luma_sum / float(count),
        "signed_luma_mean": signed_luma_sum / float(count),
        "total_pixels": total_pixels,
    }


def analyze_regions(target_img, actual_img, layer_img, args):
    target_rgb = target_img.convert("RGB")
    actual_rgb = actual_img.convert("RGB")
    alpha = layer_img.convert("RGBA").split()[3]
    target_pixels = rgb_pixels(target_rgb)
    actual_pixels = rgb_pixels(actual_rgb)
    alpha_values = alpha_pixels(alpha)
    secondary_threshold = args.secondary_alpha_threshold
    highlight_threshold = args.highlight_luma_threshold
    dark_threshold = args.dark_luma_threshold
    return [
        region_stats("all", target_pixels, actual_pixels, alpha_values, args, lambda _t, _a, _alpha: True),
        region_stats(
            "secondary",
            target_pixels,
            actual_pixels,
            alpha_values,
            args,
            lambda _t, _a, alpha_value: alpha_value >= secondary_threshold,
        ),
        region_stats(
            "nonsecondary",
            target_pixels,
            actual_pixels,
            alpha_values,
            args,
            lambda _t, _a, alpha_value: alpha_value < secondary_threshold,
        ),
        region_stats(
            "highlight",
            target_pixels,
            actual_pixels,
            alpha_values,
            args,
            lambda target_luma, _a, _alpha: target_luma >= highlight_threshold,
        ),
        region_stats(
            "secondary_dark_target",
            target_pixels,
            actual_pixels,
            alpha_values,
            args,
            lambda target_luma, _a, alpha_value: alpha_value >= secondary_threshold and target_luma <= dark_threshold,
        ),
    ]


def aggregate_region_stats(frames):
    aggregate = {}
    for name in REGIONS:
        rows = [frame["regions"][name] for frame in frames]
        pixels = sum(row["pixels"] for row in rows)
        total_pixels = sum(row["total_pixels"] for row in rows)
        if pixels <= 0:
            aggregate[name] = empty_stats(name, total_pixels)
            continue
        aggregate[name] = {
            "region": name,
            "pixels": pixels,
            "coverage": pixels / float(max(1, total_pixels)),
            "mean_abs_diff": sum(row["mean_abs_diff"] * row["pixels"] for row in rows) / float(pixels),
            "max_abs_diff": max(row["max_abs_diff"] for row in rows),
            "target_luma_mean": sum(row["target_luma_mean"] * row["pixels"] for row in rows) / float(pixels),
            "actual_luma_mean": sum(row["actual_luma_mean"] * row["pixels"] for row in rows) / float(pixels),
            "signed_luma_mean": sum(row["signed_luma_mean"] * row["pixels"] for row in rows) / float(pixels),
            "total_pixels": total_pixels,
        }
    return aggregate


def mask_image(layer_img, threshold):
    alpha = layer_img.convert("RGBA").split()[3]
    return alpha.point(lambda value: 255 if value >= threshold else 0).convert("RGB")


def diff_image(target_img, actual_img):
    return ImageChops.difference(target_img.convert("RGB"), actual_img.convert("RGB"))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (10, 16, 22))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        strip.paste(panel.convert("RGB"), (x, label_h))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


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


def write_csv_rows(frames, csv_path):
    rows = []
    for frame in frames:
        for region in REGIONS:
            rows.append({
                "frame": frame["frame"],
                "output_frame": frame["output_frame"],
                **frame["regions"][region],
            })
    fieldnames = [
        "frame",
        "output_frame",
        "region",
        "pixels",
        "coverage",
        "mean_abs_diff",
        "max_abs_diff",
        "target_luma_mean",
        "actual_luma_mean",
        "signed_luma_mean",
        "total_pixels",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Region GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Region Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    aggregate = summary.get("aggregate_regions", {})
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in [
            ("Frames", checks.get("frames")),
            ("All MAD", f"{aggregate.get('all', {}).get('mean_abs_diff', 0):.4f}"),
            ("Secondary MAD", f"{aggregate.get('secondary', {}).get('mean_abs_diff', 0):.4f}"),
            ("Nonsecondary MAD", f"{aggregate.get('nonsecondary', {}).get('mean_abs_diff', 0):.4f}"),
        ]
    )
    figures = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Region GIF"></section>' if gif else ""
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
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; width: 100%; min-width: 960px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 16px 0; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ font-size: 18px; }}
    .grid {{ display: grid; gap: 12px; margin-top: 14px; }}
    figure {{ margin: 0; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 9px 10px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section class="grid">{figures}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
    aggregate = summary.get("aggregate_regions", {})
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{summary.get('csv_repo_path')}`",
        f"Gallery: `{summary.get('gallery', {}).get('index_repo_path')}`",
        f"Status: `{summary['status']}`",
        "",
        "## Aggregate Regions",
        "",
        "| Region | Coverage | Mean MAD | Max Diff | Target Luma | Actual Luma | Signed Luma |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in REGIONS:
        item = aggregate.get(name, {})
        lines.append(
            f"| `{name}` | {item.get('coverage', 0.0):.6f} | {item.get('mean_abs_diff', 0.0):.6f} | "
            f"{item.get('max_abs_diff', 0)} | {item.get('target_luma_mean', 0.0):.6f} | "
            f"{item.get('actual_luma_mean', 0.0):.6f} | {item.get('signed_luma_mean', 0.0):.6f} |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def analyze(args):
    require_pillow()
    root = os.getcwd()
    target_summary_path = require_file(args.target_summary, "target summary")
    actual_summary_path = require_file(args.actual_composite_summary, "actual composite summary")
    target_summary = read_json(target_summary_path)
    actual_summary = read_json(actual_summary_path)
    if actual_summary.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.actual_composite_summary}: expected lsfs_mitsuba_secondary_composite schema")

    target_frames = output_frame_map(target_summary.get("frames") or [])
    actual_frames = output_frame_map(actual_summary.get("frames") or [])
    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_results = []
    strip_paths = []
    for index, output_frame in enumerate(sorted(set(target_frames) & set(actual_frames))):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(composite_path(actual_frame), "actual composite image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        regions = analyze_regions(target_img, actual_img, layer_img, args)
        region_map = {item["region"]: item for item in regions}
        mask = mask_image(layer_img, args.secondary_alpha_threshold)
        diff = diff_image(target_img, actual_img)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_regions.png")
        labeled_strip(
            [target_img, actual_img, diff, mask],
            ["Target", "Actual", "Diff", "Secondary Mask"],
            strip_path,
        )
        strip_paths.append(strip_path)
        frame_results.append({
            "frame": index,
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "regions": region_map,
        })

    if not frame_results:
        raise SystemExit("no overlapping output frames to analyze")

    csv_path = os.path.join(out_dir, "target_gap_regions.csv")
    write_csv_rows(frame_results, csv_path)
    gif_path = os.path.join(assets_dir, "regions.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "regions.gif", "Region GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"region_strip_{out_index:02d}.png", f"Region Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "target_gap_region_summary.json")
    metadata_files = [
        copy_asset(csv_path, assets_dir, "target_gap_regions.csv", "Region CSV", root),
        copy_asset(actual_summary_path, assets_dir, "actual_composite_summary.json", "Actual composite summary", root),
        copy_asset(target_summary_path, assets_dir, "target_preview_summary.json", "Target preview summary", root),
    ]
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_target_gap_region_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_composite_summary": posix_rel(actual_summary_path, root),
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_luma_threshold": args.highlight_luma_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_results),
            "csv_bytes": os.path.getsize(csv_path),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "aggregate_regions": aggregate_region_stats(frame_results),
        "frames": frame_results,
        "gallery": {},
        "next": args.next,
    }
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
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_target_gap_region_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
        "summary_repo_path": posix_rel(summary_path, root),
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(frame_results)} "
        f"secondary_mad={summary['aggregate_regions']['secondary']['mean_abs_diff']:.6f} "
        f"nonsecondary_mad={summary['aggregate_regions']['nonsecondary']['mean_abs_diff']:.6f} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze Mitsuba target gap by secondary/foreground regions")
    parser.add_argument("target_summary")
    parser.add_argument("actual_composite_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-luma-threshold", type=float, default=150.0)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Target Gap Region Analysis")
    parser.add_argument("--next", default="Use region errors to choose the next renderer/material pass.")
    args = parser.parse_args(argv)
    if not (0 <= args.secondary_alpha_threshold <= 255):
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.highlight_luma_threshold < 0.0 or args.highlight_luma_threshold > 255.0:
        parser.error("highlight-luma-threshold must be in [0, 255]")
    if args.dark_luma_threshold < 0.0 or args.dark_luma_threshold > 255.0:
        parser.error("dark-luma-threshold must be in [0, 255]")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    analyze(args)


if __name__ == "__main__":
    main()
