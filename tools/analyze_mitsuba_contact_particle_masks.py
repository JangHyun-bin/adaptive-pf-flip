#!/usr/bin/env python
"""Analyze projected contact-particle masks for Mitsuba target regions."""

import argparse
import csv
import math
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
from composite_mitsuba_secondary_layer import parse_camera, project


LUMA_RANGES = (
    (0, 75),
    (0, 85),
    (20, 75),
    (20, 105),
    (55, 95),
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze contact-particle masks")


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


def hash01(index, salt):
    value = math.sin(index * 12.9898 + salt * 78.233) * 43758.5453
    return value - math.floor(value)


def as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def secondary_channel(row):
    kind = row.get("kind", "")
    channel = row.get("render_channel", "")
    if channel in ("droplet", "spray", "foam", "bubble"):
        return channel
    if kind == "secondary_bubble":
        return "bubble"
    if kind == "secondary_droplet":
        return "droplet"
    return ""


def export_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def path_from_entry(entry):
    return (entry or {}).get("path") or (entry or {}).get("repo_path")


def particle_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row_index, row in enumerate(csv.DictReader(handle)):
            channel = secondary_channel(row)
            if channel not in ("spray", "foam", "bubble", "droplet"):
                continue
            rows.append({
                "row_index": row_index,
                "channel": channel,
                "x": as_float(row.get("x")),
                "y": as_float(row.get("y")),
                "z": as_float(row.get("z")),
                "vx": as_float(row.get("vx")),
                "vz": as_float(row.get("vz")),
                "volume": max(0.05, as_float(row.get("volume"), 1.0)),
            })
    return rows


def direction_for_particle(particle, flow_center):
    vx = particle["vx"]
    vz = particle["vz"]
    horizontal_speed = math.sqrt(vx * vx + vz * vz)
    if horizontal_speed > 1.0e-5:
        return vx / horizontal_speed, vz / horizontal_speed
    dx = particle["x"] - float(flow_center[0])
    dz = particle["z"] - float(flow_center[2])
    radial = math.sqrt(dx * dx + dz * dz)
    if radial > 1.0e-5:
        return dx / radial, dz / radial
    return 1.0, 0.0


def project_polygon(points, camera, width, height):
    projected = []
    for point in points:
        projected_point = project(point, camera, width, height)
        if projected_point is None:
            return None
        px, py, _depth = projected_point
        projected.append((px, py))
    return projected if len(projected) >= 3 else None


def draw_projected_polygon(draw, camera, width, height, points):
    projected = project_polygon(points, camera, width, height)
    if not projected:
        return False
    draw.polygon(projected, fill=255)
    return True


def ellipse_points(center, direction, radius_x, radius_z, segments):
    dx, dz = direction
    sx, sz = -dz, dx
    points = []
    for index in range(max(6, segments)):
        theta = 2.0 * math.pi * index / float(max(6, segments))
        c = math.cos(theta)
        s = math.sin(theta)
        points.append((
            center[0] + dx * c * radius_x + sx * s * radius_z,
            center[1],
            center[2] + dz * c * radius_x + sz * s * radius_z,
        ))
    return points


def arc_strip_points(center, direction, radius, width, sweep, segments):
    dx, dz = direction
    sx, sz = -dz, dx
    inner = max(0.001, radius - width * 0.5)
    outer = max(inner + 0.001, radius + width * 0.5)
    left = []
    right = []
    segments = max(4, segments)
    for index in range(segments + 1):
        t = -sweep * 0.5 + sweep * index / float(segments)
        c = math.cos(t)
        s = math.sin(t)
        left.append((
            center[0] + dx * c * inner + sx * s * inner,
            center[1],
            center[2] + dz * c * inner + sz * s * inner,
        ))
        right.append((
            center[0] + dx * c * outer + sx * s * outer,
            center[1],
            center[2] + dz * c * outer + sz * s * outer,
        ))
    return left + list(reversed(right))


def select_contact_particles(particles, pass_cfg):
    if not pass_cfg.get("enabled", False):
        return []
    max_count = max(0, as_int(pass_cfg.get("max_count"), 0))
    foam_scale = as_float((pass_cfg.get("channels") or {}).get("foam"), 0.0)
    keep_ratio = max(0.0, min(1.0, as_float(pass_cfg.get("keep_ratio"), 1.0)))
    if max_count <= 0 or foam_scale <= 0.0:
        return []
    selected = []
    for particle in particles:
        if len(selected) >= max_count:
            break
        if particle["channel"] != "foam":
            continue
        if keep_ratio < 1.0 and hash01(particle["row_index"], 151.0) > keep_ratio:
            continue
        selected.append(particle)
    return selected


def select_ripple_particles(particles, pass_cfg):
    if not pass_cfg.get("enabled", False):
        return []
    max_count = max(0, as_int(pass_cfg.get("max_count"), 0))
    channels = pass_cfg.get("channels") if isinstance(pass_cfg.get("channels"), dict) else {}
    if max_count <= 0:
        return []
    selected = []
    for particle in particles:
        if len(selected) >= max_count:
            break
        if particle["channel"] not in ("foam", "spray"):
            continue
        if as_float(channels.get(particle["channel"]), 0.0) <= 0.0:
            continue
        selected.append(particle)
    return selected


def draw_contact_masks(particles, xml_path, size, bridge_summary, args):
    camera = parse_camera(xml_path)
    width, height = size
    contact_pass = bridge_summary.get("surface_contact_foam_pass") or {}
    ripple_pass = bridge_summary.get("water_impact_ripple_pass") or {}
    masks = {
        "contact_foam": Image.new("L", size, 0),
        "impact_ripple": Image.new("L", size, 0),
        "impact_ripple_foam": Image.new("L", size, 0),
        "impact_ripple_spray": Image.new("L", size, 0),
    }
    draws = {name: ImageDraw.Draw(mask) for name, mask in masks.items()}
    counts = {name: 0 for name in masks}
    contact_particles = select_contact_particles(particles, contact_pass)
    contact_flow_center = contact_pass.get("flow_center", (14.0, 0.0, 11.0))
    contact_vertical_offset = as_float(contact_pass.get("vertical_offset"), -1.2)
    contact_radius_x = as_float(contact_pass.get("radius_x"), 0.7) * args.contact_radius_scale
    contact_radius_z = as_float(contact_pass.get("radius_z"), 0.22) * args.contact_radius_scale
    contact_foam_scale = as_float((contact_pass.get("channels") or {}).get("foam"), 1.0)
    for particle in contact_particles:
        volume_scale = max(0.45, min(1.35, math.sqrt(particle["volume"]) * 0.55)) * contact_foam_scale
        center = (particle["x"], particle["y"] + contact_vertical_offset, particle["z"])
        direction = direction_for_particle(particle, contact_flow_center)
        points = ellipse_points(
            center,
            direction,
            contact_radius_x * volume_scale,
            contact_radius_z * volume_scale,
            args.contact_segments,
        )
        if draw_projected_polygon(draws["contact_foam"], camera, width, height, points):
            counts["contact_foam"] += 1

    ripple_particles = select_ripple_particles(particles, ripple_pass)
    ripple_flow_center = ripple_pass.get("flow_center", (14.0, 0.0, 11.0))
    ripple_vertical_offset = as_float(ripple_pass.get("vertical_offset"), -1.78)
    base_radius = as_float(ripple_pass.get("radius"), 0.48) * args.ripple_radius_scale
    radius_step = as_float(ripple_pass.get("radius_step"), 0.28) * args.ripple_radius_scale
    width_value = as_float(ripple_pass.get("width"), 0.035) * args.ripple_width_scale
    ring_count = max(1, as_int(ripple_pass.get("ring_count"), 2))
    arc_fraction = max(0.05, min(1.0, as_float(ripple_pass.get("arc_fraction"), 0.62)))
    segments = max(4, as_int(ripple_pass.get("segments"), 18))
    channels = ripple_pass.get("channels") if isinstance(ripple_pass.get("channels"), dict) else {}
    for particle in ripple_particles:
        channel_scale = as_float(channels.get(particle["channel"]), 1.0)
        center = (particle["x"], particle["y"] + ripple_vertical_offset, particle["z"])
        direction = direction_for_particle(particle, ripple_flow_center)
        volume_scale = 0.72 + min(0.9, math.sqrt(particle["volume"]) * 0.12)
        drew_any = False
        for ring in range(ring_count):
            ring_radius = (base_radius + radius_step * ring) * volume_scale * channel_scale
            ring_width = width_value * (1.0 + ring * 0.18)
            sweep = max(0.2, min(2.0 * math.pi, 2.0 * math.pi * arc_fraction * (1.0 - ring * 0.08)))
            points = arc_strip_points(center, direction, ring_radius, ring_width, sweep, segments)
            if draw_projected_polygon(draws["impact_ripple"], camera, width, height, points):
                drew_any = True
                channel_name = f"impact_ripple_{particle['channel']}"
                if channel_name in draws:
                    draw_projected_polygon(draws[channel_name], camera, width, height, points)
        if drew_any:
            counts["impact_ripple"] += 1
            channel_name = f"impact_ripple_{particle['channel']}"
            if channel_name in counts:
                counts[channel_name] += 1

    if args.blur_radius > 0.0:
        for name, mask in list(masks.items()):
            masks[name] = mask.filter(ImageFilter.GaussianBlur(args.blur_radius))
    combined = Image.new("L", size, 0)
    combined.paste(masks["contact_foam"])
    combined = Image.fromarray(np.maximum(np.asarray(combined, dtype=np.uint8), np.asarray(masks["impact_ripple"], dtype=np.uint8)))
    masks["contact_foam_or_ripple"] = combined
    counts["contact_foam_or_ripple"] = counts["contact_foam"] + counts["impact_ripple"]
    return {
        name: np.asarray(mask, dtype=np.uint8) >= args.mask_threshold
        for name, mask in masks.items()
    }, counts


def target_regions(target_luma, alpha, args):
    return {
        "target_highlight": target_luma >= args.highlight_luma_threshold,
        "target_dark_secondary": np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold),
    }


def candidate_masks(contact_masks, source_luma, alpha, args):
    secondary = alpha >= args.secondary_alpha_threshold
    masks = {
        "source_highlight_120": source_luma >= 120.0,
        "source_highlight_120_nonsecondary": np.logical_and(source_luma >= 120.0, alpha < args.secondary_alpha_threshold),
        "secondary_source_luma_0_75": np.logical_and(secondary, np.logical_and(source_luma >= 0.0, source_luma <= 75.0)),
    }
    for contact_name, contact_mask in contact_masks.items():
        masks[contact_name] = contact_mask
        masks[f"{contact_name}_secondary"] = np.logical_and(contact_mask, secondary)
        for low, high in LUMA_RANGES:
            masks[f"{contact_name}_source_luma_{low:g}_{high:g}"] = np.logical_and(
                contact_mask,
                np.logical_and(source_luma >= low, source_luma <= high),
            )
            masks[f"{contact_name}_secondary_source_luma_{low:g}_{high:g}"] = np.logical_and(
                np.logical_and(contact_mask, secondary),
                np.logical_and(source_luma >= low, source_luma <= high),
            )
    return masks


def contact_rows(rows, region):
    prefixes = ("contact_foam", "impact_ripple")
    return [row for row in rows if row["region"] == region and row["candidate"].startswith(prefixes)]


def best_contact_row(rows, region):
    candidates = contact_rows(rows, region)
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: (-row["f1"], -row["recall"], -row["precision"], row["candidate"]))[0]


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


def markdown_report(summary, summary_path, root, next_text):
    aggregate = summary["aggregate"]
    best_dark = top_by_region(aggregate, "target_dark_secondary", 1)[0]
    best_contact_dark = best_contact_row(aggregate, "target_dark_secondary") or {}
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
        f"- Contact candidates: `{summary['checks'].get('contact_candidates')}`",
        f"- Best dark-secondary mask: `{best_dark.get('candidate')}` F1 `{best_dark.get('f1')}`",
        f"- Best contact dark-secondary mask: `{best_contact_dark.get('candidate')}` F1 `{best_contact_dark.get('f1')}`",
        f"- Best highlight mask: `{best_highlight.get('candidate')}` F1 `{best_highlight.get('f1')}`",
        "",
        "## Top Contact Dark Secondary Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(contact_rows(aggregate, "target_dark_secondary")[:12], start=1):
        lines.append(
            f"| {rank} | `{row['candidate']}` | {row['precision']:.6f} | {row['recall']:.6f} | "
            f"{row['f1']:.6f} | {row['candidate_coverage']:.6f} |"
        )
    lines.extend([
        "",
        "## Top Contact Highlight Masks",
        "",
        "| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(contact_rows(aggregate, "target_highlight")[:8], start=1):
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
    best_contact_dark = best_contact_row(summary["aggregate"], "target_dark_secondary") or {}
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
      <div><span>Best contact dark-secondary mask</span><strong>{best_contact_dark.get('candidate')} f1={best_contact_dark.get('f1', 0.0):.4f}</strong></div>
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
    export_path = require_file(args.mitsuba_export, "Mitsuba export")
    bridge_summary_path = require_file(args.bridge_summary, "bridge summary")
    target_summary = read_json(target_summary_path)
    actual_summary = read_json(actual_summary_path)
    export_summary = read_json(export_path)
    bridge_summary = read_json(bridge_summary_path)
    if actual_summary.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.actual_summary}: unsupported actual schema {actual_summary.get('schema')!r}")
    if export_summary.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.mitsuba_export}: expected lsfs_mitsuba_xml_export schema")

    target_frames = output_frame_map(target_summary.get("frames") or [])
    actual_frames = output_frame_map(actual_summary.get("frames") or [])
    export_frames = export_frame_map(export_summary)
    outputs = sorted(set(target_frames) & set(actual_frames) & set(export_frames))
    if not outputs:
        raise SystemExit("no overlapping target/actual/export output frames")

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
    contact_candidate_names = set()
    for index, output_frame in enumerate(outputs):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        export_frame = export_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        particles_path = require_file((export_frame.get("sidecar_assets") or {}).get("particles"), "particle stream")
        xml_path = require_file(path_from_entry(export_frame.get("xml_scene")), "xml scene")
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        target_luma = luma_array(target_img)
        source_luma = luma_array(actual_img)
        alpha = np.asarray(layer_img.split()[3], dtype=np.uint8)
        particles = particle_rows(particles_path)
        contact_masks, contact_counts = draw_contact_masks(particles, xml_path, target_img.size, bridge_summary, args)
        regions = target_regions(target_luma, alpha, args)
        candidates = candidate_masks(contact_masks, source_luma, alpha, args)
        contact_candidate_names.update(
            name for name in candidates if name.startswith(("contact_foam", "impact_ripple"))
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
            "particles_repo_path": posix_rel(particles_path, root),
            "xml_scene_repo_path": posix_rel(xml_path, root),
            "secondary_particles": len(particles),
            "contact_counts": contact_counts,
            "rows": frame_rows,
        })
        if output_frame in gallery_outputs:
            panel_masks = {
                "target_dark_secondary": regions["target_dark_secondary"],
                "secondary_source_luma_0_75": candidates.get("secondary_source_luma_0_75"),
                "contact_foam": candidates.get("contact_foam"),
                "impact_ripple": candidates.get("impact_ripple"),
                "contact_foam_or_ripple": candidates.get("contact_foam_or_ripple"),
                "contact_foam_or_ripple_secondary_source_luma_0_75": candidates.get("contact_foam_or_ripple_secondary_source_luma_0_75"),
            }
            panels = [target_img, actual_img, layer_img.convert("RGB")]
            labels = ["Target", "Actual", "Layer"]
            for name, mask in panel_masks.items():
                if mask is None:
                    continue
                panels.append(binary_image(bool_list(mask), target_img.size))
                labels.append(name)
            strip_path = os.path.join(strip_dir, f"frame_{len(strip_paths):04d}_contact_masks.png")
            labeled_strip(panels, labels, strip_path)
            strip_paths.append(strip_path)

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    csv_path = os.path.join(out_dir, "contact_particle_mask_candidates.csv")
    write_csv_file(csv_path, aggregate)
    assets = []
    for asset_index, strip_path in enumerate(strip_paths):
        assets.append(copy_asset(strip_path, assets_dir, f"strip_{asset_index:02d}.png", f"Strip {asset_index + 1}", root))

    best_dark = top_by_region(aggregate, "target_dark_secondary", 1)[0]
    best_contact_dark = best_contact_row(aggregate, "target_dark_secondary") or {}
    status = "ready"
    if best_contact_dark and best_contact_dark.get("f1", 0.0) < best_dark.get("f1", 0.0):
        status = "contact_candidate_below_best"
    elif best_contact_dark.get("candidate") == best_dark.get("candidate"):
        status = "contact_matches_current_best"

    summary_path = os.path.join(out_dir, "contact_particle_mask_candidate_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_contact_particle_mask_candidate_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_summary": posix_rel(actual_summary_path, root),
            "mitsuba_export": posix_rel(export_path, root),
            "bridge_summary": posix_rel(bridge_summary_path, root),
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_luma_threshold": args.highlight_luma_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "mask_threshold": args.mask_threshold,
            "blur_radius": args.blur_radius,
            "contact_radius_scale": args.contact_radius_scale,
            "ripple_radius_scale": args.ripple_radius_scale,
            "ripple_width_scale": args.ripple_width_scale,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_records),
            "candidates": len({row["candidate"] for row in aggregate}),
            "contact_candidates": len(contact_candidate_names),
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
        copy_json(csv_path, assets_dir, "contact_particle_mask_candidates.csv", "CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
        copy_json(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root),
        copy_json(bridge_summary_path, assets_dir, "bridge_summary.json", "Bridge summary", root),
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
    summary_asset = copy_json(summary_path, assets_dir, "contact_particle_mask_candidate_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, summary["gallery"]["metadata_files"], summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_contact_particle_mask_candidate_gallery",
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
        f"contact_dark={best_contact_dark.get('candidate')}:{best_contact_dark.get('f1', 0.0):.6f} "
        f"highlight={best_highlight.get('candidate')}:{best_highlight.get('f1', 0.0):.6f} "
        f"summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze projected contact particle masks against target regions")
    parser.add_argument("target_summary", help="lsfs_mitsuba_renderer_target_preview summary")
    parser.add_argument("actual_summary", help="actual secondary composite or composite-grade summary")
    parser.add_argument("mitsuba_export", help="lsfs_mitsuba_xml_export manifest")
    parser.add_argument("bridge_summary", help="bridge summary containing contact/ripple pass settings")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-luma-threshold", type=float, default=150.0)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--mask-threshold", type=int, default=1)
    parser.add_argument("--blur-radius", type=float, default=1.2)
    parser.add_argument("--contact-radius-scale", type=float, default=1.0)
    parser.add_argument("--contact-segments", type=int, default=16)
    parser.add_argument("--ripple-radius-scale", type=float, default=1.0)
    parser.add_argument("--ripple-width-scale", type=float, default=1.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Contact Particle Mask Candidate Analysis")
    parser.add_argument("--next", default="Use contact masks only if they exceed the current secondary source-luma baseline.")
    args = parser.parse_args()
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.blur_radius < 0.0:
        parser.error("blur-radius must be non-negative")
    if args.contact_radius_scale <= 0.0 or args.ripple_radius_scale <= 0.0 or args.ripple_width_scale <= 0.0:
        parser.error("radius/width scales must be positive")
    if args.contact_segments < 6:
        parser.error("contact-segments must be at least 6")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    return args


if __name__ == "__main__":
    analyze(parse_args())
