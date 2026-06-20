#!/usr/bin/env python
"""Analyze secondary-channel residual masks for Mitsuba dark-detail recovery."""

import argparse
import os
import shutil
from datetime import datetime, timezone

import numpy as np

try:
    from PIL import Image, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageFilter = None

from analyze_mitsuba_contact_particle_masks import particle_rows
from analyze_mitsuba_region_mask_candidates import copy_asset, copy_json, merge_stats, top_by_region
from analyze_mitsuba_target_gap_regions import actual_path
from apply_mitsuba_target_region_response import (
    layer_path,
    output_frame_map,
    target_path,
    write_gif,
)
from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from build_mitsuba_secondary_channel_aov_package import draw_channel_density
from build_mitsuba_water_material_aov_package import (
    grayscale_image,
    labeled_grid,
    luma_array,
    mask_image,
    overlay_masks,
    selected_outputs,
    stat_for_np,
    write_csv_file,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze secondary-channel residual masks")


def export_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def particle_path(frame):
    return (frame.get("sidecar_assets") or {}).get("particles")


def xml_path(frame):
    return (frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")


def dilate_mask(mask, radius):
    if radius <= 0:
        return mask
    image = Image.fromarray((mask.astype(np.uint8) * 255), "L")
    dilated = image.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    return np.asarray(dilated, dtype=np.uint8) > 0


def residual_candidates(ds6, channel_union, source_luma, alpha, args):
    secondary = alpha >= args.secondary_alpha_threshold
    masks = {
        "ds6_secondary_source_luma_0_75": ds6,
    }
    for radius in args.dilate_radii:
        expanded = dilate_mask(channel_union, radius)
        for low, high in args.band_ranges:
            band = np.logical_and.reduce((expanded, secondary, source_luma > low, source_luma <= high))
            masks[f"channel_union_r{radius}_source_luma_{low:g}_{high:g}"] = band
            masks[f"ds6_or_channel_union_r{radius}_source_luma_{low:g}_{high:g}"] = np.logical_or(ds6, band)
        for high in args.full_ranges:
            masks[f"channel_union_r{radius}_source_luma_0_{high:g}"] = np.logical_and.reduce((
                expanded,
                secondary,
                source_luma <= high,
            ))
    return masks


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Residual Mask GIF"), None)
    grids = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks", {})
    best = summary.get("best_target_dark_secondary", {})
    baseline = summary.get("baseline_ds6", {})
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Candidates", checks.get("candidate_masks")),
            ("Best", f"{best.get('candidate')} f1={best.get('f1', 0.0):.4f}"),
            ("DS6", f"f1={baseline.get('f1', 0.0):.4f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Residual Mask GIF"></section>' if gif else ""
    figures = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in grids
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #081015; --panel: #111b22; --ink: #eef8fc; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; max-width: none; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    figure {{ margin: 0 0 12px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section>{figures}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks", {})
    best = summary.get("best_target_dark_secondary", {})
    baseline = summary.get("baseline_ds6", {})
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{summary.get('csv_repo_path')}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Candidate masks: `{checks.get('candidate_masks')}`",
        f"- DS6 baseline F1: `{baseline.get('f1')}`",
        f"- Best target-dark-secondary candidate: `{best.get('candidate')}` F1 `{best.get('f1')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Top Target-Dark Secondary Candidates",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for index, row in enumerate(summary.get("top_target_dark_secondary", []), start=1):
        lines.append(
            f"| {index} | `{row['candidate']}` | {row['precision']:.6f} | "
            f"{row['recall']:.6f} | {row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
        )
    lines.extend(["", "## Frame Samples", "", "| Output | Grid |", "| ---: | --- |"])
    for frame in summary.get("frames", []):
        lines.append(f"| {frame['output_frame']} | `{frame['grid_repo_path']}` |")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def parse_ranges(values):
    result = []
    for value in values:
        parts = value.split(":", 1)
        if len(parts) != 2:
            raise argparse.ArgumentTypeError(f"range must be LOW:HIGH, got {value!r}")
        low = float(parts[0])
        high = float(parts[1])
        if low > high:
            raise argparse.ArgumentTypeError(f"range low exceeds high: {value!r}")
        result.append((low, high))
    return result


def build(args):
    require_pillow()
    root = os.getcwd()
    target_summary_path = require_file(args.target_summary, "target summary")
    actual_summary_path = require_file(args.actual_summary, "actual summary")
    export_path = require_file(args.mitsuba_export, "Mitsuba export")
    target_summary = read_json(target_summary_path)
    actual_summary = read_json(actual_summary_path)
    export_summary = read_json(export_path)
    if actual_summary.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.actual_summary}: unsupported actual schema {actual_summary.get('schema')!r}")
    if export_summary.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.mitsuba_export}: expected lsfs_mitsuba_xml_export schema")

    target_frames = output_frame_map(target_summary.get("frames") or [])
    actual_frames = output_frame_map(actual_summary.get("frames") or [])
    export_frames = export_frame_map(export_summary)
    outputs_all = sorted(set(target_frames) & set(actual_frames) & set(export_frames))
    if not outputs_all:
        raise SystemExit("no overlapping target/actual/export output frames")

    out_dir = os.path.abspath(args.out_dir)
    grid_dir = os.path.join(out_dir, "grids")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(grid_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_cache = {}
    all_rows = []
    for output_frame in outputs_all:
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        export_frame = export_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        particles_path = require_file(particle_path(export_frame), "particle stream")
        scene_path = require_file(xml_path(export_frame), "xml scene")
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        target_luma = luma_array(target_img)
        source_luma = luma_array(actual_img)
        alpha = np.asarray(layer_img.split()[3], dtype=np.uint8)
        target_dark = np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold)
        ds6 = np.logical_and(alpha >= args.secondary_alpha_threshold, source_luma <= 75.0)
        particles = particle_rows(particles_path)
        channel_masks, _density, channel_union, _density_union, projected_counts = draw_channel_density(
            particles, scene_path, target_img.size, args
        )
        candidates = residual_candidates(ds6, channel_union, source_luma, alpha, args)
        for candidate_name, candidate_mask in candidates.items():
            row = stat_for_np("target_dark_secondary", candidate_name, target_dark, candidate_mask)
            row["output_frame"] = output_frame
            all_rows.append(row)
        frame_cache[output_frame] = {
            "target_img": target_img,
            "actual_img": actual_img,
            "layer_img": layer_img,
            "target_luma": target_luma,
            "source_luma": source_luma,
            "alpha": alpha,
            "target_dark": target_dark,
            "ds6": ds6,
            "channel_union": channel_union,
            "channel_masks": channel_masks,
            "projected_counts": projected_counts,
            "paths": {
                "target": target_img_path,
                "actual": actual_img_path,
                "layer": layer_img_path,
                "particles": particles_path,
                "xml": scene_path,
            },
        }

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    top_dark = top_by_region(aggregate, "target_dark_secondary", 12)
    baseline = next(row for row in aggregate if row["candidate"] == "ds6_secondary_source_luma_0_75")
    best = top_dark[0] if top_dark else {}
    status = "ready"
    if best.get("f1", 0.0) > baseline.get("f1", 0.0) + 1.0e-9:
        status = "beats_ds6"

    selected = selected_outputs(outputs_all, args.keyframes)
    grid_paths = []
    frame_records = []
    for frame_index, output_frame in enumerate(selected):
        item = frame_cache[output_frame]
        best_mask = residual_candidates(item["ds6"], item["channel_union"], item["source_luma"], item["alpha"], args)[best["candidate"]]
        added_mask = np.logical_and(best_mask, np.logical_not(item["ds6"]))
        miss_mask = np.logical_and(item["target_dark"], np.logical_not(item["ds6"]))
        overlay = overlay_masks(
            item["actual_img"],
            [
                (item["channel_union"], (255, 210, 80), 0.35),
                (item["ds6"], (70, 235, 245), 0.40),
                (added_mask, (210, 120, 255), 0.42),
                (miss_mask, (255, 75, 85), 0.45),
            ],
        )
        panels = [
            item["target_img"],
            item["actual_img"],
            grayscale_image(item["alpha"]),
            grayscale_image(item["source_luma"]),
            mask_image(item["target_dark"], on=(250, 80, 90)),
            mask_image(miss_mask, on=(255, 110, 80)),
            mask_image(item["channel_union"], on=(245, 220, 90)),
            mask_image(item["ds6"], on=(90, 235, 245)),
            mask_image(best_mask, on=(210, 140, 255)),
            mask_image(added_mask, on=(220, 150, 255)),
            overlay,
        ]
        labels = [
            "Target",
            "Actual",
            "Layer Alpha",
            "Source Luma",
            "Target Dark",
            "DS6 Miss",
            "Channel Union",
            "DS6",
            "Best Mask",
            "Added Band",
            "Overlay",
        ]
        grid_path = os.path.join(grid_dir, f"frame_{frame_index:04d}_secondary_channel_residual_mask.png")
        grid_size = labeled_grid(panels, labels, grid_path, columns=4)
        grid_paths.append(grid_path)
        frame_records.append({
            "frame": frame_index,
            "output_frame": output_frame,
            "target_repo_path": posix_rel(item["paths"]["target"], root),
            "actual_repo_path": posix_rel(item["paths"]["actual"], root),
            "layer_repo_path": posix_rel(item["paths"]["layer"], root),
            "particles_repo_path": posix_rel(item["paths"]["particles"], root),
            "xml_scene_repo_path": posix_rel(item["paths"]["xml"], root),
            "grid_repo_path": posix_rel(grid_path, root),
            "grid_sha256": sha256_file(grid_path),
            "grid_size": os.path.getsize(grid_path),
            "grid_dimensions": list(grid_size),
            "projected_counts": item["projected_counts"],
            "coverage": {
                "target_dark": float(item["target_dark"].sum()) / float(max(1, item["target_dark"].size)),
                "ds6": float(item["ds6"].sum()) / float(max(1, item["ds6"].size)),
                "channel_union": float(item["channel_union"].sum()) / float(max(1, item["channel_union"].size)),
                "best_mask": float(best_mask.sum()) / float(max(1, best_mask.size)),
                "added_band": float(added_mask.sum()) / float(max(1, added_mask.size)),
                "ds6_miss": float(miss_mask.sum()) / float(max(1, miss_mask.size)),
            },
        })

    csv_path = os.path.join(out_dir, "secondary_channel_residual_mask_candidates.csv")
    write_csv_file(csv_path, aggregate)
    gif_path = os.path.join(assets_dir, "secondary_channel_residual_masks.gif")
    write_gif(grid_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "secondary_channel_residual_masks.gif", "Residual Mask GIF", root)]
    for index, grid_path in enumerate(grid_paths):
        assets.append(copy_asset(grid_path, assets_dir, f"frame_{index:02d}_secondary_channel_residual_mask.png", f"Frame {index + 1} Residual Mask", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "secondary_channel_residual_mask_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_json(csv_path, assets_dir, "secondary_channel_residual_mask_candidates.csv", "Candidate CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
        copy_json(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_secondary_channel_residual_mask_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_summary": posix_rel(actual_summary_path, root),
            "mitsuba_export": posix_rel(export_path, root),
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "radius_scale": args.radius_scale,
            "density_blur_radius": args.density_blur_radius,
            "dilate_radii": args.dilate_radii,
            "band_ranges": args.band_ranges,
            "full_ranges": args.full_ranges,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(outputs_all),
            "keyframes": len(frame_records),
            "candidate_masks": len({row["candidate"] for row in aggregate}),
            "gif_bytes": os.path.getsize(gif_path),
            "grid_bytes": sum(os.path.getsize(path) for path in grid_paths),
        },
        "baseline_ds6": baseline,
        "best_target_dark_secondary": best,
        "top_target_dark_secondary": top_dark,
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "aggregate": aggregate,
        "frames": frame_records,
        "gallery": {},
        "next": args.next,
    }
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    summary_asset = copy_json(summary_path, assets_dir, "secondary_channel_residual_mask_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_secondary_channel_residual_mask_gallery",
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
        f"status={status} frames={len(outputs_all)} candidates={summary['checks']['candidate_masks']} "
        f"baseline={baseline.get('f1', 0.0):.6f} best={best.get('candidate')}:{best.get('f1', 0.0):.6f} "
        f"summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_summary")
    parser.add_argument("actual_summary")
    parser.add_argument("mitsuba_export")
    parser.add_argument("out_dir")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--density-blur-radius", type=float, default=2.0)
    parser.add_argument("--dilate-radii", type=int, nargs="+", default=[0, 2, 4, 6, 8, 12, 16, 24, 32])
    parser.add_argument("--band-range", action="append", default=["75:85", "75:95", "75:105", "85:105"])
    parser.add_argument("--full-range", type=float, nargs="+", default=[75.0, 85.0, 95.0, 105.0])
    parser.add_argument("--keyframes", type=int, default=8)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Channel Residual Mask Analysis")
    parser.add_argument("--next", default="Promote the best target-free channel residual mask into a bounded visual response and compare target gap against DS6.")
    args = parser.parse_args()
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.radius_scale <= 0.0:
        parser.error("radius-scale must be positive")
    if args.density_blur_radius < 0.0:
        parser.error("density-blur-radius must be non-negative")
    if any(radius < 0 for radius in args.dilate_radii):
        parser.error("dilate radii must be non-negative")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    args.band_ranges = parse_ranges(args.band_range)
    args.full_ranges = args.full_range
    return args


if __name__ == "__main__":
    build(parse_args())
