#!/usr/bin/env python
"""Analyze secondary-layer density masks for Mitsuba target regions."""

import argparse
import csv
import os
import shutil
from datetime import datetime, timezone

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None

from analyze_mitsuba_region_mask_candidates import (
    binary_image,
    copy_asset,
    copy_json,
    labeled_strip,
    merge_stats,
    top_by_region,
)
from analyze_mitsuba_target_gap_regions import actual_path
from apply_mitsuba_target_region_response import (
    layer_path,
    luminance_from_rgb,
    output_frame_map,
    resolve_path,
    target_path,
)
from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    write_json,
    write_text,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze secondary layer density masks")


def parse_int_list(value, label):
    try:
        items = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must contain comma-separated integers") from exc
    if not items:
        raise argparse.ArgumentTypeError(f"{label} cannot be empty")
    return items


def parse_float_list(value, label):
    try:
        items = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must contain comma-separated numbers") from exc
    if not items:
        raise argparse.ArgumentTypeError(f"{label} cannot be empty")
    return items


def parse_luma_ranges(value):
    ranges = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "-" not in item:
            raise argparse.ArgumentTypeError("luma ranges must look like low-high")
        low_text, high_text = item.split("-", 1)
        low = float(low_text)
        high = float(high_text)
        if low > high:
            raise argparse.ArgumentTypeError("luma range low cannot exceed high")
        ranges.append((low, high))
    if not ranges:
        raise argparse.ArgumentTypeError("luma ranges cannot be empty")
    return ranges


def luma_array(image):
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    return 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]


def bool_list(mask):
    return [bool(value) for value in np.ravel(mask)]


def stat_for_np(region_name, candidate_name, target_mask, candidate_mask):
    target_pixels = int(target_mask.sum())
    candidate_pixels = int(candidate_mask.sum())
    intersection = int(np.logical_and(target_mask, candidate_mask).sum())
    total = int(target_mask.size)
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


def feature_specs(args):
    specs = [("alpha", threshold) for threshold in args.alpha_thresholds]
    for blur in args.density_blurs:
        for threshold in args.density_thresholds:
            specs.append((f"density_b{blur:g}", threshold))
    return specs


def feature_arrays(layer_alpha_img, args):
    alpha = np.asarray(layer_alpha_img, dtype=np.uint8)
    result = {"alpha": alpha}
    for blur in args.density_blurs:
        blurred = layer_alpha_img.filter(ImageFilter.GaussianBlur(blur))
        result[f"density_b{blur:g}"] = np.asarray(blurred, dtype=np.uint8)
    return result


def candidate_masks(features, source_luma, args):
    masks = {
        "source_highlight_120": source_luma >= 120.0,
    }
    alpha = features["alpha"]
    masks["source_highlight_120_nonsecondary"] = np.logical_and(source_luma >= 120.0, alpha < args.secondary_alpha_threshold)
    for feature_name, threshold in feature_specs(args):
        feature = features[feature_name]
        base = feature >= threshold
        for low, high in args.luma_ranges:
            name = f"{feature_name}_ge_{threshold:g}_source_luma_{low:g}_{high:g}"
            masks[name] = np.logical_and(base, np.logical_and(source_luma >= low, source_luma <= high))
    return masks


def target_regions(target_luma, alpha, args):
    return {
        "target_highlight": target_luma >= args.highlight_luma_threshold,
        "target_dark_secondary": np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold),
    }


def write_csv_file(path, rows):
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
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def density_rows(rows, region):
    return [
        row for row in rows
        if row["region"] == region and (row["candidate"].startswith("alpha_") or row["candidate"].startswith("density_"))
    ]


def best_density_row(rows, region):
    candidates = density_rows(rows, region)
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: (-row["f1"], -row["recall"], -row["precision"], row["candidate"]))[0]


def markdown_report(summary, summary_path, root, next_text):
    aggregate = summary["aggregate"]
    best_dark = top_by_region(aggregate, "target_dark_secondary", 1)[0]
    best_density_dark = best_density_row(aggregate, "target_dark_secondary") or {}
    best_highlight = top_by_region(aggregate, "target_highlight", 1)[0]
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{summary.get('csv_repo_path')}`",
        f"Gallery: `{summary.get('gallery', {}).get('index_repo_path')}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{summary['checks'].get('frames')}`",
        f"- Candidates: `{summary['checks'].get('candidates')}`",
        f"- Density candidates: `{summary['checks'].get('density_candidates')}`",
        f"- Best dark-secondary mask: `{best_dark.get('candidate')}` F1 `{best_dark.get('f1')}`",
        f"- Best density dark-secondary mask: `{best_density_dark.get('candidate')}` F1 `{best_density_dark.get('f1')}`",
        f"- Best highlight mask: `{best_highlight.get('candidate')}` F1 `{best_highlight.get('f1')}`",
        "",
        "## Top Density Dark Secondary Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(density_rows(aggregate, "target_dark_secondary")[:12], start=1):
        lines.append(
            f"| {rank} | `{row['candidate']}` | {row['precision']:.6f} | {row['recall']:.6f} | "
            f"{row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
        )
    lines.extend([
        "",
        "## Top All Dark Secondary Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate([item for item in aggregate if item["region"] == "target_dark_secondary"][:12], start=1):
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
    best_dark = top_by_region(summary["aggregate"], "target_dark_secondary", 1)[0]
    best_density_dark = best_density_row(summary["aggregate"], "target_dark_secondary") or {}
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
    main {{ max-width: 1380px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin: 16px 0; }}
    .metrics div, figure {{ border: 1px solid var(--line); background: var(--panel); }}
    .metrics div {{ padding: 10px 12px; min-height: 64px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ font-size: 16px; word-break: break-word; }}
    figure {{ margin: 0 0 12px; overflow-x: auto; }}
    figure img {{ display: block; width: 100%; min-width: 960px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 9px 10px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    <section class="metrics">
      <div><span>Best dark-secondary mask</span><strong>{best_dark.get('candidate')} f1={best_dark.get('f1', 0.0):.4f}</strong></div>
      <div><span>Best density dark-secondary mask</span><strong>{best_density_dark.get('candidate')} f1={best_density_dark.get('f1', 0.0):.4f}</strong></div>
      <div><span>Frames</span><strong>{summary['checks']['frames']}</strong></div>
      <div><span>Gallery bytes</span><strong>{format_bytes(summary['checks'].get('gallery_bytes', 0))}</strong></div>
    </section>
    {figures}
  </main>
</body>
</html>
"""


def selected_outputs(outputs, count):
    outputs = sorted(set(outputs))
    if count <= 0 or len(outputs) <= count:
        return outputs
    if count == 1:
        return [outputs[len(outputs) // 2]]
    return [outputs[round(i * (len(outputs) - 1) / float(count - 1))] for i in range(count)]


def analyze(args):
    require_pillow()
    root = os.getcwd()
    target_summary_path = require_file(args.target_summary, "target summary")
    actual_summary_path = require_file(args.actual_summary, "actual summary")
    target_summary = read_json(target_summary_path)
    actual_summary = read_json(actual_summary_path)
    if actual_summary.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.actual_summary}: unsupported actual schema {actual_summary.get('schema')!r}")

    target_frames = output_frame_map(target_summary.get("frames") or [])
    actual_frames = output_frame_map(actual_summary.get("frames") or [])
    outputs = sorted(set(target_frames) & set(actual_frames))
    if not outputs:
        raise SystemExit("no overlapping target/actual output frames")

    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    all_rows = []
    frame_records = []
    strip_paths = []
    gallery_outputs = set(selected_outputs(outputs, args.keyframes))
    density_candidate_names = set()
    for index, output_frame in enumerate(outputs):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        alpha_img = layer_img.split()[3]
        target_luma = luma_array(target_img)
        source_luma = luma_array(actual_img)
        features = feature_arrays(alpha_img, args)
        regions = target_regions(target_luma, features["alpha"], args)
        candidates = candidate_masks(features, source_luma, args)
        density_candidate_names.update(
            name for name in candidates if name.startswith("alpha_") or name.startswith("density_")
        )
        frame_rows = []
        for region_name, region_mask in regions.items():
            for candidate_name, candidate_mask in candidates.items():
                row = stat_for_np(region_name, candidate_name, region_mask, candidate_mask)
                row["output_frame"] = output_frame
                frame_rows.append(row)
                all_rows.append(row)
        frame_records.append({
            "frame": index,
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "rows": frame_rows,
        })
        if output_frame in gallery_outputs:
            panel_masks = {
                "target_dark_secondary": regions["target_dark_secondary"],
                "alpha_ge_4_source_luma_0_75": candidates.get("alpha_ge_4_source_luma_0_75"),
                "density_b2_ge_4_source_luma_0_75": candidates.get("density_b2_ge_4_source_luma_0_75"),
                "density_b3_ge_6_source_luma_0_75": candidates.get("density_b3_ge_6_source_luma_0_75"),
                "alpha_ge_4_source_luma_0_85": candidates.get("alpha_ge_4_source_luma_0_85"),
            }
            panels = [target_img, actual_img, layer_img.convert("RGB")]
            labels = ["Target", "Actual", "Layer"]
            for name, mask in panel_masks.items():
                if mask is None:
                    continue
                panels.append(binary_image(bool_list(mask), target_img.size))
                labels.append(name)
            strip_path = os.path.join(strip_dir, f"frame_{len(strip_paths):04d}_density_masks.png")
            labeled_strip(panels, labels, strip_path)
            strip_paths.append(strip_path)

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    csv_path = os.path.join(out_dir, "secondary_layer_density_mask_candidates.csv")
    write_csv_file(csv_path, aggregate)
    assets = []
    for asset_index, strip_path in enumerate(strip_paths):
        assets.append(copy_asset(strip_path, assets_dir, f"strip_{asset_index:02d}.png", f"Strip {asset_index + 1}", root))

    best_dark = top_by_region(aggregate, "target_dark_secondary", 1)[0]
    best_density_dark = best_density_row(aggregate, "target_dark_secondary") or {}
    status = "ready"
    if best_density_dark.get("candidate") == best_dark.get("candidate"):
        status = "density_matches_current_best"
    else:
        status = "density_candidate_below_best"

    summary_path = os.path.join(out_dir, "secondary_layer_density_mask_candidate_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_secondary_layer_density_mask_candidate_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_summary": posix_rel(actual_summary_path, root),
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_luma_threshold": args.highlight_luma_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "alpha_thresholds": args.alpha_thresholds,
            "density_blurs": args.density_blurs,
            "density_thresholds": args.density_thresholds,
            "luma_ranges": [[low, high] for low, high in args.luma_ranges],
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_records),
            "candidates": len({row["candidate"] for row in aggregate}),
            "density_candidates": len(density_candidate_names),
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
        copy_json(csv_path, assets_dir, "secondary_layer_density_mask_candidates.csv", "CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
    ]
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    summary_asset = copy_json(summary_path, assets_dir, "secondary_layer_density_mask_candidate_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, summary["gallery"]["metadata_files"], summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_secondary_layer_density_mask_candidate_gallery",
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
    print(
        f"status={status} frames={len(frame_records)} "
        f"dark={best_dark.get('candidate')}:{best_dark.get('f1', 0.0):.6f} "
        f"density_dark={best_density_dark.get('candidate')}:{best_density_dark.get('f1', 0.0):.6f} "
        f"highlight={best_highlight.get('candidate')}:{best_highlight.get('f1', 0.0):.6f} "
        f"summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze secondary layer density masks against target regions")
    parser.add_argument("target_summary", help="lsfs_mitsuba_renderer_target_preview summary")
    parser.add_argument("actual_summary", help="actual secondary composite or composite-grade summary")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-luma-threshold", type=float, default=150.0)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--alpha-thresholds", type=lambda v: parse_int_list(v, "alpha-thresholds"), default=parse_int_list("4,8,12,16,24,32,48,64,96,128,160", "alpha-thresholds"))
    parser.add_argument("--density-blurs", type=lambda v: parse_float_list(v, "density-blurs"), default=parse_float_list("1,2,3,4,6,8,12,16", "density-blurs"))
    parser.add_argument("--density-thresholds", type=lambda v: parse_int_list(v, "density-thresholds"), default=parse_int_list("1,2,4,6,8,12,16,24,32,48,64,96", "density-thresholds"))
    parser.add_argument("--luma-ranges", type=parse_luma_ranges, default=parse_luma_ranges("0-65,0-75,0-85,0-95,0-105,20-75,20-85,20-95,20-105,40-85,40-95,55-95,65-95,75-105"))
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Layer Density Mask Candidate Analysis")
    parser.add_argument("--next", default="Move to surface-normal or water-contact evidence if density masks do not exceed DS6.")
    args = parser.parse_args()
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    return args


if __name__ == "__main__":
    analyze(parse_args())
