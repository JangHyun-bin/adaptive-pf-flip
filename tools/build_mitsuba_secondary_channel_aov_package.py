#!/usr/bin/env python
"""Build secondary-channel AOVs for Mitsuba residual localization."""

import argparse
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
from composite_mitsuba_secondary_layer import CHANNEL_STYLE, parse_camera, project


CHANNELS = ("spray", "foam", "bubble", "droplet")


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build secondary-channel AOVs")


def export_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def particle_path(frame):
    return (frame.get("sidecar_assets") or {}).get("particles")


def draw_channel_density(particles, xml_path, size, args):
    camera = parse_camera(xml_path)
    masks = {channel: Image.new("L", size, 0) for channel in CHANNELS}
    projected_counts = {channel: 0 for channel in CHANNELS}
    width, height = size
    for particle in particles:
        channel = particle["channel"]
        if channel not in masks:
            continue
        projected = project((particle["x"], particle["y"], particle["z"]), camera, width, height)
        if projected is None:
            continue
        px, py, _depth = projected
        style = CHANNEL_STYLE.get(channel, {})
        radius = float(style.get("radius", 4.0)) * args.radius_scale
        radius *= max(0.75, min(2.5, particle.get("volume", 1.0) ** (1.0 / 3.0)))
        draw = ImageDraw.Draw(masks[channel])
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=255)
        projected_counts[channel] += 1

    density = {}
    for channel, image in masks.items():
        density[channel] = image.filter(ImageFilter.GaussianBlur(args.density_blur_radius))
    masks_np = {channel: np.asarray(image, dtype=np.uint8) for channel, image in masks.items()}
    density_np = {channel: np.asarray(image, dtype=np.uint8) for channel, image in density.items()}
    union = np.zeros((size[1], size[0]), dtype=bool)
    for channel in CHANNELS:
        union = np.logical_or(union, masks_np[channel] > 0)
    density_union = np.maximum.reduce([density_np[channel] for channel in CHANNELS])
    return masks_np, density_np, union, density_union, projected_counts


def channel_candidates(masks, density, union, density_union, source_luma, alpha, args):
    secondary = alpha >= args.secondary_alpha_threshold
    masks_out = {
        "ds6_secondary_source_luma_0_75": np.logical_and(secondary, source_luma <= 75.0),
        "secondary_channel_union_source_luma_0_75": np.logical_and.reduce((union, secondary, source_luma <= 75.0)),
        "secondary_channel_union_source_luma_0_95": np.logical_and.reduce((union, secondary, source_luma <= 95.0)),
    }
    groups = {
        "spray": masks["spray"] > 0,
        "foam": masks["foam"] > 0,
        "bubble": masks["bubble"] > 0,
        "spray_or_foam": np.logical_or(masks["spray"] > 0, masks["foam"] > 0),
        "foam_or_bubble": np.logical_or(masks["foam"] > 0, masks["bubble"] > 0),
        "all_secondary_channels": union,
    }
    densities = {
        "spray": density["spray"],
        "foam": density["foam"],
        "bubble": density["bubble"],
        "spray_or_foam": np.maximum(density["spray"], density["foam"]),
        "foam_or_bubble": np.maximum(density["foam"], density["bubble"]),
        "all_secondary_channels": density_union,
    }
    for name, mask in groups.items():
        masks_out[f"{name}_source_luma_0_75"] = np.logical_and.reduce((mask, secondary, source_luma <= 75.0))
        masks_out[f"{name}_source_luma_0_95"] = np.logical_and.reduce((mask, secondary, source_luma <= 95.0))
        for threshold in (8, 16, 32, 64, 96):
            masks_out[f"{name}_density_ge_{threshold}_source_luma_0_95"] = np.logical_and.reduce((
                densities[name] >= threshold,
                secondary,
                source_luma <= 95.0,
            ))
    return masks_out


def channel_overlay(base, masks, density_union, ds6_mask, target_dark):
    return overlay_masks(
        base,
        [
            (masks["spray"] > 0, (160, 205, 255), 0.25),
            (masks["foam"] > 0, (255, 230, 80), 0.35),
            (masks["bubble"] > 0, (120, 245, 190), 0.30),
            (density_union >= 32, (230, 120, 255), 0.18),
            (ds6_mask, (60, 235, 245), 0.40),
            (target_dark, (255, 75, 85), 0.42),
        ],
    )


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Secondary Channel AOV GIF"), None)
    grids = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks", {})
    best_dark = summary.get("best_target_dark_secondary", {})
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("AOVs", checks.get("aovs_per_frame")),
            ("Best dark candidate", f"{best_dark.get('candidate')} f1={best_dark.get('f1', 0.0):.4f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Secondary Channel AOV GIF"></section>' if gif else ""
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
        f"- AOVs per frame: `{checks.get('aovs_per_frame')}`",
        f"- Candidate masks: `{checks.get('candidate_masks')}`",
        f"- Best target-dark-secondary candidate: `{best.get('candidate')}` F1 `{best.get('f1')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## AOVs",
        "",
    ]
    for aov in summary.get("aovs", []):
        lines.append(f"- `{aov}`")
    lines.extend([
        "",
        "## Top Target-Dark Secondary Candidates",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ])
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
    outputs = selected_outputs(outputs_all, args.frames)

    out_dir = os.path.abspath(args.out_dir)
    grid_dir = os.path.join(out_dir, "grids")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(grid_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_records = []
    grid_paths = []
    all_rows = []
    aov_names = [
        "Target",
        "Actual",
        "Layer Alpha",
        "Source Luma",
        "Spray Density",
        "Foam Density",
        "Bubble Density",
        "Union Density",
        "DS6 Mask",
        "Target Dark",
        "Channel Overlay",
    ]
    for frame_index, output_frame in enumerate(outputs):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        export_frame = export_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        particles_path = require_file(particle_path(export_frame), "particle stream")
        xml_path = require_file((export_frame.get("xml_scene") or {}).get("path") or (export_frame.get("xml_scene") or {}).get("repo_path"), "xml scene")

        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")

        particles = particle_rows(particles_path)
        masks, density, union, density_union, projected_counts = draw_channel_density(particles, xml_path, target_img.size, args)
        target_luma = luma_array(target_img)
        source_luma = luma_array(actual_img)
        alpha = np.asarray(layer_img.split()[3], dtype=np.uint8)
        ds6_mask = np.logical_and(alpha >= args.secondary_alpha_threshold, source_luma <= 75.0)
        target_dark = np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold)
        candidates = channel_candidates(masks, density, union, density_union, source_luma, alpha, args)
        for candidate_name, candidate_mask in candidates.items():
            row = stat_for_np("target_dark_secondary", candidate_name, target_dark, candidate_mask)
            row["output_frame"] = output_frame
            all_rows.append(row)

        overlay = channel_overlay(actual_img, masks, density_union, ds6_mask, target_dark)
        panels = [
            target_img,
            actual_img,
            grayscale_image(alpha),
            grayscale_image(source_luma),
            grayscale_image(density["spray"]),
            grayscale_image(density["foam"]),
            grayscale_image(density["bubble"]),
            grayscale_image(density_union),
            mask_image(ds6_mask, on=(90, 235, 245)),
            mask_image(target_dark, on=(250, 80, 90)),
            overlay,
        ]
        grid_path = os.path.join(grid_dir, f"frame_{frame_index:04d}_secondary_channel_aov.png")
        grid_size = labeled_grid(panels, aov_names, grid_path, columns=4)
        grid_paths.append(grid_path)
        frame_records.append({
            "frame": frame_index,
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "particles_repo_path": posix_rel(particles_path, root),
            "xml_scene_repo_path": posix_rel(xml_path, root),
            "grid_repo_path": posix_rel(grid_path, root),
            "grid_sha256": sha256_file(grid_path),
            "grid_size": os.path.getsize(grid_path),
            "grid_dimensions": list(grid_size),
            "projected_counts": projected_counts,
            "coverage": {
                "spray": float((masks["spray"] > 0).sum()) / float(max(1, masks["spray"].size)),
                "foam": float((masks["foam"] > 0).sum()) / float(max(1, masks["foam"].size)),
                "bubble": float((masks["bubble"] > 0).sum()) / float(max(1, masks["bubble"].size)),
                "union": float(union.sum()) / float(max(1, union.size)),
                "density_union_ge_32": float((density_union >= 32).sum()) / float(max(1, density_union.size)),
                "ds6": float(ds6_mask.sum()) / float(max(1, ds6_mask.size)),
                "target_dark": float(target_dark.sum()) / float(max(1, target_dark.size)),
            },
        })

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    top_dark = top_by_region(aggregate, "target_dark_secondary", 10)
    best_dark = top_dark[0] if top_dark else {}
    status = "ready"
    if best_dark.get("candidate") == "ds6_secondary_source_luma_0_75":
        status = "baseline_still_best"

    csv_path = os.path.join(out_dir, "secondary_channel_aov_candidates.csv")
    write_csv_file(csv_path, aggregate)
    gif_path = os.path.join(assets_dir, "secondary_channel_aov.gif")
    write_gif(grid_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "secondary_channel_aov.gif", "Secondary Channel AOV GIF", root)]
    for index, grid_path in enumerate(grid_paths):
        assets.append(copy_asset(grid_path, assets_dir, f"frame_{index:02d}_secondary_channel_aov.png", f"Frame {index + 1} AOV", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "secondary_channel_aov_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_json(csv_path, assets_dir, "secondary_channel_aov_candidates.csv", "Candidate CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
        copy_json(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_secondary_channel_aov_package",
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
            "frames": args.frames,
            "fps": args.fps,
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "radius_scale": args.radius_scale,
            "density_blur_radius": args.density_blur_radius,
        },
        "aovs": aov_names,
        "checks": {
            "frames": len(frame_records),
            "aovs_per_frame": len(aov_names),
            "candidate_masks": len({row["candidate"] for row in aggregate}),
            "gif_bytes": os.path.getsize(gif_path),
            "grid_bytes": sum(os.path.getsize(path) for path in grid_paths),
        },
        "best_target_dark_secondary": best_dark,
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
    summary_asset = copy_json(summary_path, assets_dir, "secondary_channel_aov_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_secondary_channel_aov_gallery",
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
        f"status={status} frames={len(frame_records)} aovs={len(aov_names)} "
        f"best={best_dark.get('candidate')}:{best_dark.get('f1', 0.0):.6f} "
        f"gif={os.path.getsize(gif_path)} summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_summary")
    parser.add_argument("actual_summary")
    parser.add_argument("mitsuba_export")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--density-blur-radius", type=float, default=2.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Channel AOV Package")
    parser.add_argument("--next", default="Use channel AOVs only if they localize target-dark residuals better than DS6.")
    args = parser.parse_args()
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.radius_scale <= 0.0:
        parser.error("radius-scale must be positive")
    if args.density_blur_radius < 0.0:
        parser.error("density-blur-radius must be non-negative")
    return args


if __name__ == "__main__":
    build(parse_args())
