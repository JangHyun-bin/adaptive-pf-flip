#!/usr/bin/env python
"""Join source-response masks with projected Mitsuba secondary channels."""

import argparse
import os
import shutil
from datetime import datetime, timezone

import numpy as np

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from analyze_mitsuba_contact_particle_masks import particle_rows
from analyze_mitsuba_region_mask_candidates import merge_stats, top_by_region
from apply_mitsuba_target_region_response import layer_path, output_frame_map, write_gif
from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from build_mitsuba_secondary_channel_aov_package import CHANNELS, draw_channel_density, particle_path
from build_mitsuba_water_material_aov_package import (
    grayscale_image,
    labeled_grid,
    mask_image,
    overlay_masks,
    stat_for_np,
    write_csv_file,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze source-response mask channels")


def parse_labeled_path(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("--mask-source must be LABEL=PATH")
    label, path = value.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise argparse.ArgumentTypeError("--mask-source must be LABEL=PATH")
    return label, path


def export_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def response_source_path(frame):
    return frame.get("source_repo_path") or frame.get("composite_repo_path")


def mask_alpha(frame, threshold):
    path = require_file(layer_path(frame), "source-response mask layer")
    alpha = Image.open(path).convert("RGBA").split()[3]
    return np.asarray(alpha, dtype=np.uint8) >= threshold, path


def grouped_channel_masks(masks, density, union, density_union):
    groups = {
        "spray": masks["spray"] > 0,
        "foam": masks["foam"] > 0,
        "bubble": masks["bubble"] > 0,
        "droplet": masks["droplet"] > 0,
        "spray_or_foam": np.logical_or(masks["spray"] > 0, masks["foam"] > 0),
        "foam_or_bubble": np.logical_or(masks["foam"] > 0, masks["bubble"] > 0),
        "all_secondary_channels": union,
    }
    densities = {
        "spray": density["spray"],
        "foam": density["foam"],
        "bubble": density["bubble"],
        "droplet": density["droplet"],
        "spray_or_foam": np.maximum(density["spray"], density["foam"]),
        "foam_or_bubble": np.maximum(density["foam"], density["bubble"]),
        "all_secondary_channels": density_union,
    }
    candidates = dict(groups)
    for name, values in densities.items():
        for threshold in (8, 16, 32, 64):
            candidates[f"{name}_density_ge_{threshold}"] = values >= threshold
    return candidates


def copy_asset(src, assets_dir, name, label, root):
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


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Mask Channel GIF"), None)
    grids = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Mask sources", checks.get("mask_sources")),
            ("Candidates", checks.get("candidate_masks")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Mask Channel GIF"></section>' if gif else ""
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
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{summary['csv_repo_path']}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Mask sources: `{checks.get('mask_sources')}`",
        f"- Candidate masks: `{checks.get('candidate_masks')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Top Candidates By Mask",
        "",
    ]
    for label, rows in summary.get("top_by_mask", {}).items():
        lines.extend([
            f"### {label}",
            "",
            "| Rank | Candidate | Precision | Recall | F1 | Coverage |",
            "| ---: | --- | ---: | ---: | ---: | ---: |",
        ])
        for index, row in enumerate(rows, start=1):
            lines.append(
                f"| {index} | `{row['candidate']}` | {row['precision']:.6f} | "
                f"{row['recall']:.6f} | {row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
            )
        lines.append("")
    lines.extend(["## Frame Samples", "", "| Mask | Output | Grid |", "| --- | ---: | --- |"])
    for frame in summary.get("frames") or []:
        lines.append(f"| `{frame['mask_label']}` | {frame['output_frame']} | `{frame['grid_repo_path']}` |")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    export_path = require_file(args.mitsuba_export, "Mitsuba export")
    export_summary = read_json(export_path)
    if export_summary.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.mitsuba_export}: expected lsfs_mitsuba_xml_export schema")
    export_frames = export_frame_map(export_summary)

    mask_sources = []
    for label, path in args.mask_source:
        summary_path = require_file(path, f"{label} mask source")
        summary = read_json(summary_path)
        if summary.get("schema") != "lsfs_mitsuba_secondary_composite":
            raise SystemExit(f"{path}: expected lsfs_mitsuba_secondary_composite schema")
        mask_sources.append((label, summary_path, summary, output_frame_map(summary.get("frames") or [])))

    out_dir = os.path.abspath(args.out_dir)
    grid_dir = os.path.join(out_dir, "grids")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(grid_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frames = []
    grid_paths = []
    all_rows = []
    for label, _summary_path, _summary, source_frames in mask_sources:
        outputs_all = sorted(set(source_frames) & set(export_frames))
        if not outputs_all:
            raise SystemExit(f"{label}: no overlapping mask/export output frames")
        outputs = outputs_all if args.frames <= 0 else outputs_all[:args.frames]
        for index, output_frame in enumerate(outputs):
            mask_frame = source_frames[output_frame]
            export_frame = export_frames[output_frame]
            mask_np, mask_path = mask_alpha(mask_frame, args.mask_alpha_threshold)
            source_path = require_file(response_source_path(mask_frame), "source response image")
            particles_path = require_file(particle_path(export_frame), "particle stream")
            xml_path = require_file((export_frame.get("xml_scene") or {}).get("path") or (export_frame.get("xml_scene") or {}).get("repo_path"), "xml scene")
            source_img = Image.open(source_path).convert("RGB")
            particles = particle_rows(particles_path)
            masks, density, union, density_union, projected_counts = draw_channel_density(particles, xml_path, source_img.size, args)
            candidates = grouped_channel_masks(masks, density, union, density_union)
            for candidate_name, candidate_mask in candidates.items():
                row = stat_for_np(label, candidate_name, mask_np, candidate_mask)
                row["output_frame"] = output_frame
                all_rows.append(row)

            overlay = overlay_masks(
                source_img,
                [
                    (mask_np, (255, 80, 95), 0.45),
                    (masks["spray"] > 0, (160, 205, 255), 0.26),
                    (masks["foam"] > 0, (255, 230, 80), 0.34),
                    (masks["bubble"] > 0, (120, 245, 190), 0.28),
                    (density_union >= 32, (230, 120, 255), 0.18),
                ],
            )
            panels = [
                source_img,
                mask_image(mask_np, on=(255, 90, 105)),
                grayscale_image(density["spray"]),
                grayscale_image(density["foam"]),
                grayscale_image(density["bubble"]),
                grayscale_image(density["droplet"]),
                grayscale_image(density_union),
                overlay,
            ]
            labels = ["Source", f"{label} Mask", "Spray", "Foam", "Bubble", "Droplet", "Union Density", "Overlay"]
            grid_path = os.path.join(grid_dir, f"{label.lower()}_{index:04d}_mask_channel_join.png")
            grid_size = labeled_grid(panels, labels, grid_path, columns=4)
            grid_paths.append(grid_path)
            frames.append({
                "mask_label": label,
                "frame": index,
                "output_frame": output_frame,
                "source_repo_path": posix_rel(source_path, root),
                "mask_repo_path": posix_rel(mask_path, root),
                "particles_repo_path": posix_rel(particles_path, root),
                "xml_scene_repo_path": posix_rel(xml_path, root),
                "grid_repo_path": posix_rel(grid_path, root),
                "grid_sha256": sha256_file(grid_path),
                "grid_size": os.path.getsize(grid_path),
                "grid_dimensions": list(grid_size),
                "mask_coverage": float(mask_np.sum()) / float(max(1, mask_np.size)),
                "projected_counts": projected_counts,
            })

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    top_by_mask = {
        label: top_by_region(aggregate, label, args.top)
        for label, _summary_path, _summary, _frames in mask_sources
    }
    csv_path = os.path.join(out_dir, "source_response_mask_channel_candidates.csv")
    write_csv_file(csv_path, aggregate)
    gif_path = os.path.join(assets_dir, "source_response_mask_channel.gif")
    write_gif(grid_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "source_response_mask_channel.gif", "Mask Channel GIF", root)]
    for index, grid_path in enumerate(grid_paths):
        assets.append(copy_asset(grid_path, assets_dir, f"frame_{index:02d}_mask_channel_join.png", f"Frame {index + 1} Grid", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "source_response_mask_channel_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_asset(csv_path, assets_dir, "source_response_mask_channel_candidates.csv", "Candidate CSV", root),
        copy_asset(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root),
    ]
    for label, summary_path_item, _summary, _frames in mask_sources:
        metadata_files.append(copy_asset(summary_path_item, assets_dir, f"{label.lower()}_mask_source.json", f"{label} mask source", root))
    summary = {
        "schema": "lsfs_mitsuba_source_response_mask_channel_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "mitsuba_export": posix_rel(export_path, root),
            "mask_sources": [
                {"label": label, "repo_path": posix_rel(summary_path_item, root)}
                for label, summary_path_item, _summary, _frames in mask_sources
            ],
        },
        "settings": {
            "frames": args.frames,
            "fps": args.fps,
            "mask_alpha_threshold": args.mask_alpha_threshold,
            "radius_scale": args.radius_scale,
            "density_blur_radius": args.density_blur_radius,
            "top": args.top,
        },
        "checks": {
            "frames": len(frames),
            "mask_sources": len(mask_sources),
            "candidate_masks": len({row["candidate"] for row in aggregate}),
            "gif_bytes": os.path.getsize(gif_path),
            "grid_bytes": sum(os.path.getsize(path) for path in grid_paths),
        },
        "top_by_mask": top_by_mask,
        "aggregate": aggregate,
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "frames": frames,
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
    summary_asset = copy_asset(summary_path, assets_dir, "source_response_mask_channel_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_source_response_mask_channel_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "index_repo_path": posix_rel(index_path, root),
        "summary_repo_path": posix_rel(summary_path, root),
        "assets": assets,
        "metadata_files": summary["gallery"]["metadata_files"],
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(frames)} masks={len(mask_sources)} "
        f"candidates={summary['checks']['candidate_masks']} summary={summary_path}"
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Analyze projected secondary-channel overlap with response masks")
    parser.add_argument("mitsuba_export")
    parser.add_argument("out_dir")
    parser.add_argument("--mask-source", action="append", type=parse_labeled_path, required=True,
                        help="LABEL=source_response_mask_source_summary.json")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--mask-alpha-threshold", type=int, default=16)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--density-blur-radius", type=float, default=2.0)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Source-Response Mask Channel Analysis")
    parser.add_argument("--next", default="Use this channel join to select the next material/AOV response candidate.")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("frames must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if not (0 <= args.mask_alpha_threshold <= 255):
        parser.error("mask-alpha-threshold must be in [0, 255]")
    if args.radius_scale <= 0.0:
        parser.error("radius-scale must be positive")
    if args.density_blur_radius < 0.0:
        parser.error("density-blur-radius must be non-negative")
    if args.top <= 0:
        parser.error("top must be positive")
    return args


def main(argv=None):
    build(parse_args(argv))


if __name__ == "__main__":
    main()
