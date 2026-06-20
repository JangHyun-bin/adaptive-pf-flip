#!/usr/bin/env python
"""Build water-material AOVs for Mitsuba visual tuning."""

import argparse
import csv
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None

from analyze_mitsuba_region_mask_candidates import copy_asset, copy_json, merge_stats, top_by_region
from analyze_mitsuba_target_gap_regions import actual_path
from analyze_water_mesh_quality import face_geometry, parse_obj, vec_sub
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
from composite_mitsuba_secondary_layer import parse_camera, project, vec_dot, vec_norm


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build water-material AOVs")


def export_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def path_from_entry(entry):
    return (entry or {}).get("path") or (entry or {}).get("repo_path")


def selected_outputs(outputs, count):
    outputs = sorted(set(outputs))
    if count <= 0 or len(outputs) <= count:
        return outputs
    if count == 1:
        return [outputs[len(outputs) // 2]]
    return [outputs[round(i * (len(outputs) - 1) / float(count - 1))] for i in range(count)]


def luma_array(image):
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    return 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]


def grayscale_image(values):
    arr = np.clip(values, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "L").convert("RGB")


def mask_image(mask, on=(235, 245, 250), off=(8, 12, 16)):
    h, w = mask.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    out[:, :] = off
    out[mask] = on
    return Image.fromarray(out, "RGB")


def overlay_masks(base, entries):
    rgb = np.asarray(base.convert("RGB"), dtype=np.float32).copy()
    for mask, color, alpha in entries:
        color_arr = np.asarray(color, dtype=np.float32)
        rgb[mask] = rgb[mask] * (1.0 - alpha) + color_arr * alpha
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


def labeled_grid(panels, labels, out_path, columns=4):
    if not panels:
        raise ValueError("no panels")
    width, height = panels[0].size
    label_h = 28
    columns = max(1, int(columns))
    rows = (len(panels) + columns - 1) // columns
    grid = Image.new("RGB", (width * columns, (height + label_h) * rows), (8, 13, 18))
    draw = ImageDraw.Draw(grid)
    for index, panel in enumerate(panels):
        col = index % columns
        row = index // columns
        x = col * width
        y = row * (height + label_h)
        draw.rectangle((x, y, x + width, y + label_h), fill=(18, 28, 36))
        draw.text((x + 8, y + 8), labels[index], fill=(230, 242, 248))
        grid.paste(panel.convert("RGB"), (x, y + label_h))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    grid.save(out_path)
    return grid.size


def face_center(vertices, face):
    count = max(1, len(face))
    return (
        sum(vertices[index][0] for index in face) / count,
        sum(vertices[index][1] for index in face) / count,
        sum(vertices[index][2] for index in face) / count,
    )


def camera_facing_score(camera, center, normal):
    to_camera = vec_norm(vec_sub(camera["origin"], center))
    return abs(vec_dot(normal, to_camera))


def normalize_to_u8(values, lo=None, hi=None):
    arr = np.asarray(values, dtype=np.float32)
    if lo is None:
        lo = float(np.nanmin(arr)) if arr.size else 0.0
    if hi is None:
        hi = float(np.nanmax(arr)) if arr.size else 1.0
    span = max(1.0e-6, hi - lo)
    return np.clip((arr - lo) / span * 255.0, 0, 255).astype(np.uint8)


def screen_thickness_proxy(water_img, iterations):
    current = water_img.convert("L").point(lambda value: 255 if value > 0 else 0)
    accum = np.zeros((water_img.size[1], water_img.size[0]), dtype=np.float32)
    for _index in range(max(1, iterations)):
        mask = np.asarray(current, dtype=np.uint8) > 0
        if not mask.any():
            break
        accum[mask] += 1.0
        current = current.filter(ImageFilter.MinFilter(3))
    if accum.max() <= 0.0:
        return np.zeros_like(accum, dtype=np.uint8)
    return np.clip(accum / accum.max() * 255.0, 0, 255).astype(np.uint8)


def build_water_material_aovs(mesh_path, xml_path, size, args):
    vertices, _normals, faces = parse_obj(Path(mesh_path))
    camera = parse_camera(xml_path)
    width, height = size
    face_items = []
    skipped = 0
    for face in faces:
        if len(face) < 3:
            skipped += 1
            continue
        projected = []
        depths = []
        valid = True
        for vertex_index in face:
            if vertex_index < 0 or vertex_index >= len(vertices):
                valid = False
                break
            projected_point = project(vertices[vertex_index], camera, width, height)
            if projected_point is None:
                valid = False
                break
            px, py, depth = projected_point
            projected.append((px, py))
            depths.append(depth)
        if not valid or len(projected) < 3:
            skipped += 1
            continue
        area, normal = face_geometry(vertices, face)
        if area <= args.min_face_area:
            skipped += 1
            continue
        center = face_center(vertices, face)
        face_items.append({
            "projected": projected,
            "center_depth": sum(depths) / float(len(depths)),
            "abs_normal_y": abs(normal[1]),
            "facing": camera_facing_score(camera, center, normal),
        })

    water_img = Image.new("L", size, 0)
    depth_img = Image.new("L", size, 0)
    flatness_img = Image.new("L", size, 0)
    facing_img = Image.new("L", size, 0)
    water_draw = ImageDraw.Draw(water_img)
    depth_draw = ImageDraw.Draw(depth_img)
    flatness_draw = ImageDraw.Draw(flatness_img)
    facing_draw = ImageDraw.Draw(facing_img)
    depths = [item["center_depth"] for item in face_items]
    depth_min = min(depths) if depths else 0.0
    depth_max = max(depths) if depths else 1.0
    depth_span = max(1.0e-6, depth_max - depth_min)

    # Draw far surfaces first so nearer faces win where projected faces overlap.
    for item in sorted(face_items, key=lambda value: value["center_depth"], reverse=True):
        depth_near = 1.0 - (item["center_depth"] - depth_min) / depth_span
        water_draw.polygon(item["projected"], fill=255)
        depth_draw.polygon(item["projected"], fill=int(np.clip(depth_near * 255.0, 0, 255)))
        flatness_draw.polygon(item["projected"], fill=int(np.clip(item["abs_normal_y"] * 255.0, 0, 255)))
        facing_draw.polygon(item["projected"], fill=int(np.clip(item["facing"] * 255.0, 0, 255)))

    water = np.asarray(water_img, dtype=np.uint8)
    depth = np.asarray(depth_img, dtype=np.uint8)
    flatness = np.asarray(flatness_img, dtype=np.uint8)
    facing = np.asarray(facing_img, dtype=np.uint8)
    edge_img = water_img.filter(ImageFilter.FIND_EDGES)
    if args.edge_dilate > 0:
        edge_img = edge_img.filter(ImageFilter.MaxFilter(args.edge_dilate * 2 + 1))
    edge = np.asarray(edge_img, dtype=np.uint8)
    thickness = screen_thickness_proxy(water_img, args.thickness_iterations)
    absorption_proxy = np.clip((thickness.astype(np.float32) * (0.35 + depth.astype(np.float32) / 255.0 * 0.65)), 0, 255).astype(np.uint8)
    return {
        "water": water,
        "depth_near": depth,
        "flatness": flatness,
        "facing": facing,
        "edge": edge,
        "thickness": thickness,
        "absorption_proxy": absorption_proxy,
    }, {
        "vertices": len(vertices),
        "faces": len(faces),
        "projected_faces": len(face_items),
        "skipped_faces": skipped,
        "depth_min": depth_min,
        "depth_max": depth_max,
    }


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


def material_candidates(aovs, source_luma, alpha, args):
    secondary = alpha >= args.secondary_alpha_threshold
    water = aovs["water"] > 0
    masks = {
        "ds6_secondary_source_luma_0_75": np.logical_and(secondary, source_luma <= 75.0),
        "water_secondary_source_luma_0_75": np.logical_and(np.logical_and(water, secondary), source_luma <= 75.0),
        "water_secondary_source_luma_0_95": np.logical_and(np.logical_and(water, secondary), source_luma <= 95.0),
    }
    for threshold in (32, 64, 96, 128, 160):
        masks[f"water_edge_ge_{threshold}_secondary_source_luma_0_95"] = np.logical_and.reduce((
            aovs["edge"] >= threshold,
            water,
            secondary,
            source_luma <= 95.0,
        ))
        masks[f"water_thickness_ge_{threshold}_secondary_source_luma_0_95"] = np.logical_and.reduce((
            aovs["thickness"] >= threshold,
            water,
            secondary,
            source_luma <= 95.0,
        ))
        masks[f"water_absorption_ge_{threshold}_secondary_source_luma_0_95"] = np.logical_and.reduce((
            aovs["absorption_proxy"] >= threshold,
            water,
            secondary,
            source_luma <= 95.0,
        ))
        masks[f"water_depth_near_ge_{threshold}_secondary_source_luma_0_95"] = np.logical_and.reduce((
            aovs["depth_near"] >= threshold,
            water,
            secondary,
            source_luma <= 95.0,
        ))
        masks[f"water_facing_ge_{threshold}_secondary_source_luma_0_95"] = np.logical_and.reduce((
            aovs["facing"] >= threshold,
            water,
            secondary,
            source_luma <= 95.0,
        ))
        masks[f"water_flatness_ge_{threshold}_secondary_source_luma_0_95"] = np.logical_and.reduce((
            aovs["flatness"] >= threshold,
            water,
            secondary,
            source_luma <= 95.0,
        ))
    return masks


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


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Water Material AOV GIF"), None)
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
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Water Material AOV GIF"></section>' if gif else ""
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
        "Water Mask",
        "Depth Near",
        "Facing",
        "Flatness",
        "Silhouette Edge",
        "Thickness Proxy",
        "Absorption Proxy",
        "DS6 Mask",
        "Target Dark",
        "Overlay",
    ]
    for frame_index, output_frame in enumerate(outputs):
        target_frame = target_frames[output_frame]
        actual_frame = actual_frames[output_frame]
        export_frame = export_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target image")
        actual_img_path = require_file(actual_path(actual_frame), "actual image")
        layer_img_path = require_file(layer_path(actual_frame), "secondary layer image")
        mesh_path = require_file(path_from_entry(export_frame.get("water_mesh")), "water mesh")
        xml_path = require_file(path_from_entry(export_frame.get("xml_scene")), "xml scene")

        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")

        target_luma = luma_array(target_img)
        source_luma = luma_array(actual_img)
        alpha = np.asarray(layer_img.split()[3], dtype=np.uint8)
        ds6_mask = np.logical_and(alpha >= args.secondary_alpha_threshold, source_luma <= 75.0)
        target_dark = np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold)
        aovs, mesh_stats = build_water_material_aovs(mesh_path, xml_path, target_img.size, args)
        candidates = material_candidates(aovs, source_luma, alpha, args)
        for candidate_name, candidate_mask in candidates.items():
            row = stat_for_np("target_dark_secondary", candidate_name, target_dark, candidate_mask)
            row["output_frame"] = output_frame
            all_rows.append(row)

        overlay = overlay_masks(
            actual_img,
            [
                (aovs["water"] > 0, (60, 120, 210), 0.18),
                (aovs["edge"] >= 32, (255, 210, 70), 0.40),
                (aovs["absorption_proxy"] >= 96, (40, 210, 235), 0.25),
                (ds6_mask, (60, 235, 245), 0.42),
                (target_dark, (255, 75, 85), 0.42),
            ],
        )
        panels = [
            target_img,
            actual_img,
            grayscale_image(alpha),
            grayscale_image(source_luma),
            mask_image(aovs["water"] > 0, on=(70, 140, 220)),
            grayscale_image(aovs["depth_near"]),
            grayscale_image(aovs["facing"]),
            grayscale_image(aovs["flatness"]),
            grayscale_image(aovs["edge"]),
            grayscale_image(aovs["thickness"]),
            grayscale_image(aovs["absorption_proxy"]),
            mask_image(ds6_mask, on=(90, 235, 245)),
            mask_image(target_dark, on=(250, 80, 90)),
            overlay,
        ]
        grid_path = os.path.join(grid_dir, f"frame_{frame_index:04d}_water_material_aov.png")
        grid_size = labeled_grid(panels, aov_names, grid_path, columns=4)
        grid_paths.append(grid_path)
        frame_records.append({
            "frame": frame_index,
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "water_mesh_repo_path": posix_rel(mesh_path, root),
            "xml_scene_repo_path": posix_rel(xml_path, root),
            "grid_repo_path": posix_rel(grid_path, root),
            "grid_sha256": sha256_file(grid_path),
            "grid_size": os.path.getsize(grid_path),
            "grid_dimensions": list(grid_size),
            "mesh_stats": mesh_stats,
            "coverage": {
                "water": float((aovs["water"] > 0).sum()) / float(max(1, aovs["water"].size)),
                "edge_ge_32": float((aovs["edge"] >= 32).sum()) / float(max(1, aovs["edge"].size)),
                "thickness_ge_96": float((aovs["thickness"] >= 96).sum()) / float(max(1, aovs["thickness"].size)),
                "absorption_ge_96": float((aovs["absorption_proxy"] >= 96).sum()) / float(max(1, aovs["absorption_proxy"].size)),
                "ds6": float(ds6_mask.sum()) / float(max(1, ds6_mask.size)),
                "target_dark": float(target_dark.sum()) / float(max(1, target_dark.size)),
            },
        })

    aggregate = merge_stats(all_rows)
    aggregate = sorted(aggregate, key=lambda row: (row["region"], -row["f1"], -row["recall"], -row["precision"], row["candidate"]))
    top_dark = top_by_region(aggregate, "target_dark_secondary", 8)
    best_dark = top_dark[0] if top_dark else {}
    status = "ready"
    if best_dark.get("candidate") == "ds6_secondary_source_luma_0_75":
        status = "baseline_still_best"

    csv_path = os.path.join(out_dir, "water_material_aov_candidates.csv")
    write_csv_file(csv_path, aggregate)
    gif_path = os.path.join(assets_dir, "water_material_aov.gif")
    write_gif(grid_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "water_material_aov.gif", "Water Material AOV GIF", root)]
    for index, grid_path in enumerate(grid_paths):
        assets.append(copy_asset(grid_path, assets_dir, f"frame_{index:02d}_water_material_aov.png", f"Frame {index + 1} AOV", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "water_material_aov_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_json(csv_path, assets_dir, "water_material_aov_candidates.csv", "Candidate CSV", root),
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
        copy_json(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_water_material_aov_package",
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
            "min_face_area": args.min_face_area,
            "edge_dilate": args.edge_dilate,
            "thickness_iterations": args.thickness_iterations,
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
    summary_asset = copy_json(summary_path, assets_dir, "water_material_aov_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_water_material_aov_gallery",
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
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--min-face-area", type=float, default=1.0e-12)
    parser.add_argument("--edge-dilate", type=int, default=1)
    parser.add_argument("--thickness-iterations", type=int, default=16)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Water Material AOV Package")
    parser.add_argument("--next", default="Use the water-material AOVs to decide whether the next renderer pass should tune absorption, foam, or specular response.")
    args = parser.parse_args()
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.min_face_area < 0.0:
        parser.error("min-face-area must be non-negative")
    if args.edge_dilate < 0:
        parser.error("edge-dilate must be non-negative")
    if args.thickness_iterations <= 0:
        parser.error("thickness-iterations must be positive")
    return args


if __name__ == "__main__":
    build(parse_args())
