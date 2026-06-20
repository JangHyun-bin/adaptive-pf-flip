#!/usr/bin/env python
"""Analyze projected secondary-sidecar masks for Mitsuba target regions."""

import argparse
import csv
import json
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None

from analyze_mitsuba_region_mask_candidates import (
    alpha_pixels,
    binary_image,
    copy_asset,
    copy_json,
    labeled_strip,
    merge_stats,
    rgb_luma_pixels,
    stat_for,
    top_by_region,
    write_csv,
)
from analyze_mitsuba_target_gap_regions import actual_path
from apply_mitsuba_target_region_response import (
    layer_path,
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


CHANNEL_STYLE = {
    "spray": {"radius": 4.2},
    "foam": {"radius": 6.8},
    "bubble": {"radius": 5.2},
    "droplet": {"radius": 3.5},
}

LUMA_RANGES = (
    (0, 65),
    (0, 75),
    (0, 85),
    (20, 75),
    (20, 105),
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze projected secondary masks")


def sidecar_frame_map(summary):
    mapping = {}
    for frame in summary.get("frames") or []:
        output = frame.get("output_frame")
        sidecar = frame.get("sidecar") or {}
        path = resolve_path(sidecar.get("path") or sidecar.get("repo_path"))
        if output is not None and path:
            mapping[int(output)] = frame
    return mapping


def sidecar_path(frame):
    sidecar = frame.get("sidecar") or {}
    return sidecar.get("path") or sidecar.get("repo_path")


def read_sidecar_particles(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
            camera = row.get("camera") or {}
            if not camera.get("in_frame"):
                continue
            ndc = camera.get("ndc") or []
            if len(ndc) != 2:
                continue
            channel = (row.get("channel") or "").strip().lower()
            if channel not in CHANNEL_STYLE:
                continue
            rows.append({
                "channel": channel,
                "ndc_x": float(ndc[0]),
                "ndc_y": float(ndc[1]),
                "depth": float(camera.get("depth") or 0.0),
                "speed": float(row.get("speed") or 0.0),
                "radius": float(row.get("radius") or 0.0),
                "volume": float(row.get("volume") or 1.0),
            })
    return rows


def quantile(values, fraction):
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = max(0, min(len(sorted_values) - 1, round(fraction * (len(sorted_values) - 1))))
    return sorted_values[index]


def candidate_specs(particles):
    depths = [item["depth"] for item in particles if item["depth"] > 0.0]
    speeds = [item["speed"] for item in particles]
    radii = [item["radius"] for item in particles]
    q_depth_33 = quantile(depths, 0.33)
    q_depth_50 = quantile(depths, 0.50)
    q_depth_67 = quantile(depths, 0.67)
    q_speed_50 = quantile(speeds, 0.50)
    q_radius_67 = quantile(radii, 0.67)
    specs = [
        ("projected_all", lambda _p: True),
        ("projected_spray", lambda p: p["channel"] == "spray"),
        ("projected_foam", lambda p: p["channel"] == "foam"),
        ("projected_bubble", lambda p: p["channel"] == "bubble"),
        ("projected_foam_bubble", lambda p: p["channel"] in ("foam", "bubble")),
        ("projected_spray_foam", lambda p: p["channel"] in ("spray", "foam")),
        ("projected_depth_near_33", lambda p: p["depth"] <= q_depth_33),
        ("projected_depth_near_50", lambda p: p["depth"] <= q_depth_50),
        ("projected_depth_mid_33_67", lambda p: q_depth_33 < p["depth"] < q_depth_67),
        ("projected_depth_far_50", lambda p: p["depth"] >= q_depth_50),
        ("projected_depth_far_33", lambda p: p["depth"] >= q_depth_67),
        ("projected_speed_slow_0_5", lambda p: p["speed"] <= 0.5),
        ("projected_speed_slow_2", lambda p: p["speed"] <= 2.0),
        ("projected_speed_slow_median", lambda p: p["speed"] <= q_speed_50),
        ("projected_speed_fast_8", lambda p: p["speed"] >= 8.0),
        ("projected_speed_fast_12", lambda p: p["speed"] >= 12.0),
        ("projected_radius_large_67", lambda p: p["radius"] >= q_radius_67),
        (
            "projected_foam_bubble_depth_far_50",
            lambda p: p["channel"] in ("foam", "bubble") and p["depth"] >= q_depth_50,
        ),
        (
            "projected_foam_bubble_depth_near_50",
            lambda p: p["channel"] in ("foam", "bubble") and p["depth"] <= q_depth_50,
        ),
        (
            "projected_spray_depth_far_50",
            lambda p: p["channel"] == "spray" and p["depth"] >= q_depth_50,
        ),
        (
            "projected_spray_depth_near_50",
            lambda p: p["channel"] == "spray" and p["depth"] <= q_depth_50,
        ),
    ]
    return specs


def particle_pixel_radius(particle, args):
    style_radius = CHANNEL_STYLE[particle["channel"]]["radius"]
    depth = max(1.0, particle["depth"])
    depth_scale = max(args.depth_scale_min, min(args.depth_scale_max, args.reference_depth / depth))
    volume = particle["volume"]
    volume_scale = max(0.65, min(1.8, volume ** (1.0 / 3.0) if volume > 0.0 else 1.0))
    return max(args.min_pixel_radius, style_radius * args.radius_scale * depth_scale * volume_scale)


def rasterize_mask(size, particles, predicate, args):
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    drawn = 0
    for particle in particles:
        if not predicate(particle):
            continue
        px = particle["ndc_x"] * (width - 1)
        py = particle["ndc_y"] * (height - 1)
        radius = particle_pixel_radius(particle, args)
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=255)
        drawn += 1
    if args.blur_radius > 0.0:
        mask = mask.filter(ImageFilter.GaussianBlur(args.blur_radius))
    values = mask.tobytes()
    return [value >= args.projected_alpha_threshold for value in values], drawn


def mask_and_luma(mask, source_luma, low, high):
    return [value and low <= luma <= high for value, luma in zip(mask, source_luma)]


def target_regions(target_luma, alpha, args):
    return {
        "target_highlight": [value >= args.highlight_luma_threshold for value in target_luma],
        "target_dark_secondary": [
            alpha_value >= args.secondary_alpha_threshold and value <= args.dark_luma_threshold
            for value, alpha_value in zip(target_luma, alpha)
        ],
    }


def candidate_masks(particles, size, source_luma, layer_alpha, args):
    masks = {
        "source_highlight_120": [value >= 120 for value in source_luma],
        "source_highlight_120_nonsecondary": [
            value >= 120 and alpha < args.secondary_alpha_threshold
            for value, alpha in zip(source_luma, layer_alpha)
        ],
        "layer_secondary": [alpha >= args.secondary_alpha_threshold for alpha in layer_alpha],
    }
    for low, high in LUMA_RANGES:
        masks[f"layer_secondary_source_luma_{low}_{high}"] = [
            alpha >= args.secondary_alpha_threshold and low <= luma <= high
            for luma, alpha in zip(source_luma, layer_alpha)
        ]
    drawn_counts = {}
    for name, predicate in candidate_specs(particles):
        mask, drawn = rasterize_mask(size, particles, predicate, args)
        drawn_counts[name] = drawn
        masks[name] = mask
        for low, high in LUMA_RANGES:
            masks[f"{name}_source_luma_{low}_{high}"] = mask_and_luma(mask, source_luma, low, high)
    return masks, drawn_counts


def write_projected_csv(path, rows):
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


def projected_rows(rows, region):
    return [
        row for row in rows
        if row["region"] == region and row["candidate"].startswith("projected_")
    ]


def best_row(rows, region, projected_only=False):
    candidates = projected_rows(rows, region) if projected_only else [row for row in rows if row["region"] == region]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: (-row["f1"], -row["recall"], -row["precision"], row["candidate"]))[0]


def markdown_report(summary, summary_path, root, next_text):
    aggregate = summary["aggregate"]
    best_dark = best_row(aggregate, "target_dark_secondary") or {}
    best_projected_dark = best_row(aggregate, "target_dark_secondary", projected_only=True) or {}
    best_highlight = best_row(aggregate, "target_highlight") or {}
    best_projected_highlight = best_row(aggregate, "target_highlight", projected_only=True) or {}
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
        f"- Projected candidates: `{summary['checks'].get('projected_candidates')}`",
        f"- Best dark-secondary mask: `{best_dark.get('candidate')}` F1 `{best_dark.get('f1')}`",
        f"- Best projected dark-secondary mask: `{best_projected_dark.get('candidate')}` F1 `{best_projected_dark.get('f1')}`",
        f"- Best highlight mask: `{best_highlight.get('candidate')}` F1 `{best_highlight.get('f1')}`",
        f"- Best projected highlight mask: `{best_projected_highlight.get('candidate')}` F1 `{best_projected_highlight.get('f1')}`",
        "",
        "## Top Projected Dark Secondary Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(projected_rows(aggregate, "target_dark_secondary")[:10], start=1):
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
    for rank, row in enumerate([item for item in aggregate if item["region"] == "target_dark_secondary"][:10], start=1):
        lines.append(
            f"| {rank} | `{row['candidate']}` | {row['precision']:.6f} | {row['recall']:.6f} | "
            f"{row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
        )
    lines.extend([
        "",
        "## Top Projected Highlight Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(projected_rows(aggregate, "target_highlight")[:8], start=1):
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
    best_dark = best_row(summary["aggregate"], "target_dark_secondary") or {}
    best_projected_dark = best_row(summary["aggregate"], "target_dark_secondary", projected_only=True) or {}
    best_projected_highlight = best_row(summary["aggregate"], "target_highlight", projected_only=True) or {}
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
      <div><span>Best projected dark-secondary mask</span><strong>{best_projected_dark.get('candidate')} f1={best_projected_dark.get('f1', 0.0):.4f}</strong></div>
      <div><span>Best projected highlight mask</span><strong>{best_projected_highlight.get('candidate')} f1={best_projected_highlight.get('f1', 0.0):.4f}</strong></div>
      <div><span>Frames</span><strong>{summary['checks']['frames']}</strong></div>
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
    sidecar_summary_path = require_file(args.sidecar_summary, "secondary sidecar summary")
    target_summary = read_json(target_summary_path)
    actual_summary = read_json(actual_summary_path)
    sidecar_summary = read_json(sidecar_summary_path)
    if actual_summary.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.actual_summary}: unsupported actual schema {actual_summary.get('schema')!r}")
    if sidecar_summary.get("schema") != "lsfs_mitsuba_secondary_3d_sidecar":
        raise SystemExit(f"{args.sidecar_summary}: expected lsfs_mitsuba_secondary_3d_sidecar schema")

    target_frames = output_frame_map(target_summary.get("frames") or [])
    actual_frames = output_frame_map(actual_summary.get("frames") or [])
    sidecar_frames = sidecar_frame_map(sidecar_summary)
    outputs = sorted(set(target_frames) & set(actual_frames) & set(sidecar_frames))
    if not outputs:
        raise SystemExit("no overlapping target/actual/sidecar output frames")

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
    projected_candidate_names = set()
    for index, output_frame in enumerate(outputs):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        sidecar_frame = sidecar_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        particles_path = require_file(sidecar_path(sidecar_frame), "secondary sidecar JSONL")
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        particles = read_sidecar_particles(particles_path)
        target_luma = rgb_luma_pixels(target_img)
        source_luma = rgb_luma_pixels(actual_img)
        layer_alpha = alpha_pixels(layer_img.split()[3])
        regions = target_regions(target_luma, layer_alpha, args)
        candidates, drawn_counts = candidate_masks(particles, target_img.size, source_luma, layer_alpha, args)
        projected_candidate_names.update(name for name in candidates if name.startswith("projected_"))
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
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "sidecar_repo_path": posix_rel(particles_path, root),
            "particles": len(particles),
            "drawn_counts": drawn_counts,
            "rows": frame_rows,
        })
        if output_frame in gallery_outputs:
            panel_masks = {
                "target_dark_secondary": regions["target_dark_secondary"],
                "layer_secondary_source_luma_0_75": candidates.get("layer_secondary_source_luma_0_75"),
                "projected_all": candidates.get("projected_all"),
                "projected_all_source_luma_0_75": candidates.get("projected_all_source_luma_0_75"),
                "projected_foam_bubble_source_luma_0_75": candidates.get("projected_foam_bubble_source_luma_0_75"),
                "projected_depth_far_33_source_luma_0_75": candidates.get("projected_depth_far_33_source_luma_0_75"),
            }
            panels = [target_img, actual_img, layer_img.convert("RGB")]
            labels = ["Target", "Actual", "Layer"]
            for name, mask in panel_masks.items():
                if mask is None:
                    continue
                panels.append(binary_image(mask, target_img.size))
                labels.append(name)
            strip_path = os.path.join(strip_dir, f"frame_{len(strip_paths):04d}_projected_masks.png")
            labeled_strip(panels, labels, strip_path)
            strip_paths.append(strip_path)

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    csv_path = os.path.join(out_dir, "projected_secondary_mask_candidates.csv")
    write_projected_csv(csv_path, aggregate)
    assets = []
    for asset_index, strip_path in enumerate(strip_paths):
        assets.append(copy_asset(strip_path, assets_dir, f"strip_{asset_index:02d}.png", f"Strip {asset_index + 1}", root))

    summary_path = os.path.join(out_dir, "projected_secondary_mask_candidate_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    generated_utc = datetime.now(timezone.utc).isoformat()
    best_dark = best_row(aggregate, "target_dark_secondary") or {}
    best_projected_dark = best_row(aggregate, "target_dark_secondary", projected_only=True) or {}
    status = "ready"
    if best_projected_dark and best_dark and best_projected_dark.get("candidate") != best_dark.get("candidate"):
        status = "projected_candidate_below_best"
    summary = {
        "schema": "lsfs_mitsuba_projected_secondary_mask_candidate_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_summary": posix_rel(actual_summary_path, root),
            "sidecar_summary": posix_rel(sidecar_summary_path, root),
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "projected_alpha_threshold": args.projected_alpha_threshold,
            "highlight_luma_threshold": args.highlight_luma_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "radius_scale": args.radius_scale,
            "reference_depth": args.reference_depth,
            "blur_radius": args.blur_radius,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_records),
            "candidates": len({row["candidate"] for row in aggregate}),
            "projected_candidates": len(projected_candidate_names),
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
        copy_json(csv_path, assets_dir, "projected_secondary_mask_candidates.csv", "CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
        copy_json(sidecar_summary_path, assets_dir, "secondary_3d_sidecar.json", "Secondary 3D sidecar", root),
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
    summary_asset = copy_json(summary_path, assets_dir, "projected_secondary_mask_candidate_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, summary["gallery"]["metadata_files"], summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_projected_secondary_mask_candidate_gallery",
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
    best_highlight = best_row(aggregate, "target_highlight") or {}
    print(
        f"status={status} frames={len(frame_records)} "
        f"dark={best_dark.get('candidate')}:{best_dark.get('f1', 0.0):.6f} "
        f"projected_dark={best_projected_dark.get('candidate')}:{best_projected_dark.get('f1', 0.0):.6f} "
        f"highlight={best_highlight.get('candidate')}:{best_highlight.get('f1', 0.0):.6f} "
        f"summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze projected secondary sidecar masks against target regions")
    parser.add_argument("target_summary", help="lsfs_mitsuba_renderer_target_preview summary")
    parser.add_argument("actual_summary", help="actual secondary composite or composite-grade summary")
    parser.add_argument("sidecar_summary", help="lsfs_mitsuba_secondary_3d_sidecar summary")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--projected-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-luma-threshold", type=float, default=150.0)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--reference-depth", type=float, default=52.0)
    parser.add_argument("--depth-scale-min", type=float, default=0.55)
    parser.add_argument("--depth-scale-max", type=float, default=2.4)
    parser.add_argument("--min-pixel-radius", type=float, default=1.0)
    parser.add_argument("--blur-radius", type=float, default=2.4)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Projected Secondary Mask Candidate Analysis")
    parser.add_argument("--next", default="Use projected sidecar masks only if they beat the current selective source-luma baseline.")
    args = parser.parse_args()
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.projected_alpha_threshold < 0 or args.projected_alpha_threshold > 255:
        parser.error("projected-alpha-threshold must be in [0, 255]")
    if args.radius_scale <= 0.0 or args.reference_depth <= 0.0:
        parser.error("radius-scale and reference-depth must be positive")
    if args.depth_scale_min <= 0.0 or args.depth_scale_max < args.depth_scale_min:
        parser.error("invalid depth-scale bounds")
    if args.min_pixel_radius <= 0.0 or args.blur_radius < 0.0:
        parser.error("invalid radius values")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    return args


if __name__ == "__main__":
    analyze(parse_args())
