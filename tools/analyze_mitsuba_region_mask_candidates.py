#!/usr/bin/env python
"""Analyze source/evidence mask candidates for Mitsuba target regions."""

import argparse
import csv
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

from analyze_mitsuba_target_gap_regions import actual_path
from apply_mitsuba_target_region_response import (
    composite_path,
    layer_path,
    luminance_from_rgb,
    output_frame_map,
    resolve_path,
    target_path,
)
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
        raise SystemExit("Pillow is required to analyze region mask candidates")


def alpha_pixels(image):
    return list(image.convert("L").tobytes())


def rgb_luma_pixels(image):
    data = image.convert("RGB").tobytes()
    return [
        luminance_from_rgb(data[index], data[index + 1], data[index + 2])
        for index in range(0, len(data), 3)
    ]


def binary_image(mask, size, on=(235, 245, 250), off=(8, 12, 16)):
    data = bytearray()
    for value in mask:
        data.extend(on if value else off)
    return Image.frombytes("RGB", size, bytes(data))


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


def copy_json(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    return {
        "label": label,
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }


def target_regions(target_luma, alpha, args):
    highlight = [value >= args.highlight_luma_threshold for value in target_luma]
    dark_secondary = [
        alpha_value >= args.secondary_alpha_threshold and value <= args.dark_luma_threshold
        for value, alpha_value in zip(target_luma, alpha)
    ]
    return {
        "target_highlight": highlight,
        "target_dark_secondary": dark_secondary,
    }


def candidate_masks(source_luma, alpha, native_weight, args):
    masks = {}
    for threshold in (120, 135, 145, 150, 160):
        masks[f"source_highlight_{threshold}"] = [value >= threshold for value in source_luma]
    for threshold in (120, 135, 145):
        masks[f"source_highlight_{threshold}_nonsecondary"] = [
            value >= threshold and alpha_value < args.secondary_alpha_threshold
            for value, alpha_value in zip(source_luma, alpha)
        ]
    for threshold in (4, 16, 32, 64):
        masks[f"secondary_alpha_{threshold}"] = [alpha_value >= threshold for alpha_value in alpha]
    ranges = ((20, 105), (30, 125), (55, 130), (70, 150))
    for low, high in ranges:
        masks[f"secondary_source_luma_{low}_{high}"] = [
            alpha_value >= args.secondary_alpha_threshold and low <= value <= high
            for value, alpha_value in zip(source_luma, alpha)
        ]
    if native_weight is not None:
        for threshold in (8, 16, 32, 64, 96):
            masks[f"native_weight_{threshold}"] = [value >= threshold for value in native_weight]
        for threshold in (16, 32, 64):
            masks[f"native_weight_{threshold}_nonsecondary"] = [
                weight >= threshold and alpha_value < args.secondary_alpha_threshold
                for weight, alpha_value in zip(native_weight, alpha)
            ]
            masks[f"secondary_native_weight_{threshold}"] = [
                weight >= threshold and alpha_value >= args.secondary_alpha_threshold
                for weight, alpha_value in zip(native_weight, alpha)
            ]
    return masks


def stat_for(region_name, candidate_name, target_mask, candidate_mask):
    target_pixels = sum(1 for value in target_mask if value)
    candidate_pixels = sum(1 for value in candidate_mask if value)
    intersection = sum(1 for target, candidate in zip(target_mask, candidate_mask) if target and candidate)
    total = len(target_mask)
    precision = intersection / float(candidate_pixels) if candidate_pixels else 0.0
    recall = intersection / float(target_pixels) if target_pixels else 0.0
    f1 = (2.0 * precision * recall / (precision + recall)) if precision + recall > 0.0 else 0.0
    return {
        "region": region_name,
        "candidate": candidate_name,
        "pixels": total,
        "target_pixels": target_pixels,
        "candidate_pixels": candidate_pixels,
        "intersection_pixels": intersection,
        "target_coverage": target_pixels / float(max(1, total)),
        "candidate_coverage": candidate_pixels / float(max(1, total)),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def merge_stats(rows):
    by_key = {}
    for row in rows:
        key = (row["region"], row["candidate"])
        item = by_key.setdefault(key, {
            "region": row["region"],
            "candidate": row["candidate"],
            "pixels": 0,
            "target_pixels": 0,
            "candidate_pixels": 0,
            "intersection_pixels": 0,
        })
        for field in ("pixels", "target_pixels", "candidate_pixels", "intersection_pixels"):
            item[field] += int(row[field])
    result = []
    for item in by_key.values():
        pixels = item["pixels"]
        target_pixels = item["target_pixels"]
        candidate_pixels = item["candidate_pixels"]
        intersection = item["intersection_pixels"]
        precision = intersection / float(candidate_pixels) if candidate_pixels else 0.0
        recall = intersection / float(target_pixels) if target_pixels else 0.0
        f1 = (2.0 * precision * recall / (precision + recall)) if precision + recall > 0.0 else 0.0
        item.update({
            "target_coverage": target_pixels / float(max(1, pixels)),
            "candidate_coverage": candidate_pixels / float(max(1, pixels)),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })
        result.append(item)
    return sorted(result, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"]))


def write_csv(path, rows):
    fields = [
        "region",
        "candidate",
        "pixels",
        "target_pixels",
        "candidate_pixels",
        "intersection_pixels",
        "target_coverage",
        "candidate_coverage",
        "precision",
        "recall",
        "f1",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def top_by_region(rows, region, limit):
    return [row for row in rows if row["region"] == region][:limit]


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{summary.get('csv_repo_path')}`",
        f"Gallery: `{summary.get('gallery', {}).get('index_repo_path')}`",
        f"Status: `{summary['status']}`",
        "",
        "## Top Target Highlight Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(top_by_region(summary["aggregate"], "target_highlight", 8), start=1):
        lines.append(
            f"| {rank} | `{row['candidate']}` | {row['precision']:.6f} | {row['recall']:.6f} | "
            f"{row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
        )
    lines.extend([
        "",
        "## Top Target Dark Secondary Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(top_by_region(summary["aggregate"], "target_dark_secondary", 8), start=1):
        lines.append(
            f"| {rank} | `{row['candidate']}` | {row['precision']:.6f} | {row['recall']:.6f} | "
            f"{row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def html_page(title, assets, metadata_files, summary):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    figures = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in assets
    )
    best_highlight = top_by_region(summary["aggregate"], "target_highlight", 1)[0]
    best_dark = top_by_region(summary["aggregate"], "target_dark_secondary", 1)[0]
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
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin: 16px 0; }}
    .metrics div, figure {{ border: 1px solid var(--line); background: var(--panel); }}
    .metrics div {{ padding: 10px 12px; min-height: 64px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ font-size: 16px; }}
    figure {{ margin: 0 0 12px; overflow-x: auto; }}
    figure img {{ display: block; width: 100%; min-width: 960px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 9px 10px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    <section class="metrics">
      <div><span>Best highlight mask</span><strong>{best_highlight['candidate']} f1={best_highlight['f1']:.4f}</strong></div>
      <div><span>Best dark-secondary mask</span><strong>{best_dark['candidate']} f1={best_dark['f1']:.4f}</strong></div>
      <div><span>Frames</span><strong>{summary['checks']['frames']}</strong></div>
      <div><span>Gallery bytes</span><strong>{format_bytes(summary['checks']['gallery_bytes'])}</strong></div>
    </section>
    {figures}
  </main>
</body>
</html>
"""


def depth_frame_map(summary):
    if not summary:
        return {}
    return output_frame_map(summary.get("frames") or [])


def analyze(args):
    require_pillow()
    root = os.getcwd()
    target_summary_path = require_file(args.target_summary, "target summary")
    actual_summary_path = require_file(args.actual_summary, "actual summary")
    depth_summary_path = require_file(args.depth_aware_composite, "depth-aware composite") if args.depth_aware_composite else None
    target_summary = read_json(target_summary_path)
    actual_summary = read_json(actual_summary_path)
    depth_summary = read_json(depth_summary_path) if depth_summary_path else None
    if actual_summary.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.actual_summary}: unsupported actual summary schema {actual_summary.get('schema')!r}")

    target_frames = output_frame_map(target_summary.get("frames") or [])
    actual_frames = output_frame_map(actual_summary.get("frames") or [])
    depth_frames = depth_frame_map(depth_summary)
    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    all_rows = []
    frame_records = []
    strip_paths = []
    selected_outputs = select_outputs(sorted(set(target_frames) & set(actual_frames)), args.keyframes)
    for index, output_frame in enumerate(sorted(set(target_frames) & set(actual_frames))):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        depth_frame = depth_frames.get(output_frame) or {}
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        native_weight_path = resolve_path(depth_frame.get("native_weight_mask_repo_path"))
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        native_img = Image.open(native_weight_path).convert("L") if native_weight_path and os.path.isfile(native_weight_path) else None
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        if native_img is not None and native_img.size != target_img.size:
            native_img = native_img.resize(target_img.size, Image.Resampling.LANCZOS)
        target_luma = rgb_luma_pixels(target_img)
        source_luma = rgb_luma_pixels(actual_img)
        alpha = alpha_pixels(layer_img.split()[3])
        native_weight = alpha_pixels(native_img) if native_img is not None else None
        regions = target_regions(target_luma, alpha, args)
        candidates = candidate_masks(source_luma, alpha, native_weight, args)
        frame_rows = []
        for region_name, region_mask in regions.items():
            for candidate_name, candidate_mask in candidates.items():
                row = stat_for(region_name, candidate_name, region_mask, candidate_mask)
                row["output_frame"] = output_frame
                frame_rows.append(row)
                all_rows.append(row)
        frame_records.append({
            "frame": index,
            "output_frame": output_frame,
            "rows": frame_rows,
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "native_weight_repo_path": posix_rel(native_weight_path, root) if native_weight_path and os.path.isfile(native_weight_path) else None,
        })
        if output_frame in selected_outputs:
            masks = {
                "target_highlight": regions["target_highlight"],
                "target_dark_secondary": regions["target_dark_secondary"],
                "source_highlight_135": candidates.get("source_highlight_135"),
                "source_highlight_135_nonsecondary": candidates.get("source_highlight_135_nonsecondary"),
                "native_weight_32": candidates.get("native_weight_32"),
                "secondary_source_luma_20_105": candidates.get("secondary_source_luma_20_105"),
            }
            panels = [target_img, actual_img]
            labels = ["Target", "Actual"]
            for name, mask in masks.items():
                if mask is None:
                    continue
                panels.append(binary_image(mask, target_img.size))
                labels.append(name)
            strip_path = os.path.join(strip_dir, f"frame_{len(strip_paths):04d}_mask_candidates.png")
            labeled_strip(panels, labels, strip_path)
            strip_paths.append(strip_path)

    if not all_rows:
        raise SystemExit("no overlapping frames to analyze")

    aggregate = merge_stats(all_rows)
    csv_path = os.path.join(out_dir, "region_mask_candidates.csv")
    write_csv(csv_path, aggregate)
    assets = []
    for out_index, strip_path in enumerate(strip_paths):
        assets.append(copy_asset(strip_path, assets_dir, f"strip_{out_index:02d}.png", f"Strip {out_index + 1}", root))
    summary_path = os.path.join(out_dir, "region_mask_candidate_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_region_mask_candidate_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_summary": posix_rel(actual_summary_path, root),
            "depth_aware_composite": posix_rel(depth_summary_path, root) if depth_summary_path else None,
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_luma_threshold": args.highlight_luma_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_records),
            "candidates": len({row["candidate"] for row in aggregate}),
            "gallery_bytes": sum(os.path.getsize(path) for path in strip_paths),
        },
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "aggregate": aggregate,
        "frames": frame_records,
        "gallery": {},
        "next": args.next,
    }
    metadata_files = [
        copy_json(csv_path, assets_dir, "region_mask_candidates.csv", "CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
    ]
    if depth_summary_path:
        metadata_files.append(copy_json(depth_summary_path, assets_dir, "depth_aware_composite.json", "Depth-aware summary", root))
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    summary_asset = copy_json(summary_path, assets_dir, "region_mask_candidate_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, summary["gallery"]["metadata_files"], summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_region_mask_candidate_gallery",
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
    best_highlight = top_by_region(aggregate, "target_highlight", 1)[0]
    best_dark = top_by_region(aggregate, "target_dark_secondary", 1)[0]
    print(
        f"status=ready frames={len(frame_records)} highlight={best_highlight['candidate']}:{best_highlight['f1']:.6f} "
        f"dark={best_dark['candidate']}:{best_dark['f1']:.6f} summary={summary_path}"
    )


def select_outputs(outputs, count):
    outputs = sorted(set(outputs))
    if count <= 0 or len(outputs) <= count:
        return outputs
    if count == 1:
        return [outputs[len(outputs) // 2]]
    return [outputs[round(i * (len(outputs) - 1) / float(count - 1))] for i in range(count)]


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze source/evidence masks against target regions")
    parser.add_argument("target_summary", help="lsfs_mitsuba_renderer_target_preview summary")
    parser.add_argument("actual_summary", help="actual secondary composite or composite-grade summary")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--depth-aware-composite")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-luma-threshold", type=float, default=150.0)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Region Mask Candidate Analysis")
    parser.add_argument("--next", default="Use the best masks to drive a renderer-native response candidate.")
    args = parser.parse_args()
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    return args


if __name__ == "__main__":
    analyze(parse_args())
