#!/usr/bin/env python
"""Build a screen-evidence AOV review package for Mitsuba composite tuning."""

import argparse
import os
import shutil
from datetime import datetime, timezone

import numpy as np

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

from analyze_mitsuba_contact_particle_masks import draw_contact_masks, particle_rows
from analyze_mitsuba_region_mask_candidates import copy_asset, copy_json
from analyze_mitsuba_target_gap_regions import actual_path
from analyze_mitsuba_water_mesh_screen_masks import draw_water_masks
from apply_mitsuba_target_region_response import (
    layer_path,
    output_frame_map,
    resolve_path,
    target_path,
    write_gif,
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
        raise SystemExit("Pillow is required to build the AOV package")


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


def labeled_grid(panels, labels, out_path, columns=3):
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


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "AOV GIF"), None)
    grids = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("AOVs", checks.get("aovs_per_frame")),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in metrics
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="AOV GIF"></section>' if gif else ""
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
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #eaf5fb; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
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
        f"- AOVs per frame: `{checks.get('aovs_per_frame')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## AOVs",
        "",
    ]
    for aov in summary.get("aovs", []):
        lines.append(f"- `{aov}`")
    lines.extend(["", "## Frame Samples", "", "| Output | Grid |", "| ---: | --- |"])
    for frame in summary.get("frames", []):
        lines.append(f"| {frame.get('output_frame')} | `{frame.get('grid_repo_path')}` |")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
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
    outputs = selected_outputs(sorted(set(target_frames) & set(actual_frames) & set(export_frames)), args.frames)
    if not outputs:
        raise SystemExit("no overlapping target/actual/export output frames")

    out_dir = os.path.abspath(args.out_dir)
    grid_dir = os.path.join(out_dir, "grids")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(grid_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_records = []
    grid_paths = []
    aov_names = [
        "Target",
        "Actual",
        "Layer Alpha",
        "Source Luma",
        "DS6 Mask",
        "Target Dark Diagnostic",
        "Water Mask",
        "Contact Mask",
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
        ds6_mask = np.logical_and(alpha >= args.secondary_alpha_threshold, source_luma <= 75.0)
        target_dark = np.logical_and(alpha >= args.secondary_alpha_threshold, target_luma <= args.dark_luma_threshold)
        water_masks, _mesh_stats = draw_water_masks(mesh_path, xml_path, target_img.size, args)
        particles = particle_rows(particles_path)
        contact_masks, _contact_counts = draw_contact_masks(particles, xml_path, target_img.size, bridge_summary, args)
        water_mask = water_masks["water_all"]
        contact_mask = contact_masks["contact_foam_or_ripple"]
        overlay = overlay_masks(
            actual_img,
            [
                (water_mask, (70, 120, 180), 0.18),
                (contact_mask, (255, 220, 80), 0.55),
                (ds6_mask, (70, 230, 240), 0.42),
                (target_dark, (255, 70, 80), 0.42),
            ],
        )
        panels = [
            target_img,
            actual_img,
            grayscale_image(alpha),
            grayscale_image(source_luma),
            mask_image(ds6_mask, on=(90, 235, 245)),
            mask_image(target_dark, on=(250, 80, 90)),
            mask_image(water_mask, on=(90, 150, 220)),
            mask_image(contact_mask, on=(245, 210, 70)),
            overlay,
        ]
        grid_path = os.path.join(grid_dir, f"frame_{frame_index:04d}_screen_evidence_aov.png")
        grid_size = labeled_grid(panels, aov_names, grid_path, columns=3)
        grid_paths.append(grid_path)
        frame_records.append({
            "frame": frame_index,
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_img_path, root),
            "actual_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "water_mesh_repo_path": posix_rel(mesh_path, root),
            "particles_repo_path": posix_rel(particles_path, root),
            "xml_scene_repo_path": posix_rel(xml_path, root),
            "grid_repo_path": posix_rel(grid_path, root),
            "grid_sha256": sha256_file(grid_path),
            "grid_size": os.path.getsize(grid_path),
            "grid_dimensions": list(grid_size),
            "ds6_coverage": float(ds6_mask.sum()) / float(max(1, ds6_mask.size)),
            "target_dark_coverage": float(target_dark.sum()) / float(max(1, target_dark.size)),
            "water_coverage": float(water_mask.sum()) / float(max(1, water_mask.size)),
            "contact_coverage": float(contact_mask.sum()) / float(max(1, contact_mask.size)),
        })

    gif_path = os.path.join(assets_dir, "screen_evidence_aov.gif")
    write_gif(grid_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "screen_evidence_aov.gif", "AOV GIF", root)]
    for asset_index, grid_path in enumerate(grid_paths):
        assets.append(copy_asset(grid_path, assets_dir, f"frame_{asset_index:02d}_aov.png", f"Frame {asset_index + 1} AOV", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "screen_evidence_aov_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_json(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
        copy_json(actual_summary_path, assets_dir, "actual_summary.json", "Actual summary", root),
        copy_json(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root),
        copy_json(bridge_summary_path, assets_dir, "bridge_summary.json", "Bridge summary", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_screen_evidence_aov_package",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "actual_summary": posix_rel(actual_summary_path, root),
            "mitsuba_export": posix_rel(export_path, root),
            "bridge_summary": posix_rel(bridge_summary_path, root),
        },
        "settings": {
            "frames": args.frames,
            "fps": args.fps,
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
        },
        "aovs": aov_names,
        "checks": {
            "frames": len(frame_records),
            "aovs_per_frame": len(aov_names),
            "gif_bytes": os.path.getsize(gif_path),
            "grid_bytes": sum(os.path.getsize(path) for path in grid_paths),
        },
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
    summary_asset = copy_json(summary_path, assets_dir, "screen_evidence_aov_summary.json", "Summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_screen_evidence_aov_gallery",
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
        f"status=ready frames={len(frame_records)} aovs={len(aov_names)} "
        f"gif={os.path.getsize(gif_path)} summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Build Mitsuba screen evidence AOV package")
    parser.add_argument("target_summary")
    parser.add_argument("actual_summary")
    parser.add_argument("mitsuba_export")
    parser.add_argument("bridge_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--mask-threshold", type=int, default=1)
    parser.add_argument("--min-face-area", type=float, default=1.0e-12)
    parser.add_argument("--blur-radius", type=float, default=1.2)
    parser.add_argument("--contact-radius-scale", type=float, default=1.0)
    parser.add_argument("--contact-segments", type=int, default=16)
    parser.add_argument("--ripple-radius-scale", type=float, default=1.0)
    parser.add_argument("--ripple-width-scale", type=float, default=1.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Screen Evidence AOV Package")
    parser.add_argument("--next", default="Use this AOV package to choose the next bounded visual response or renderer AOV export.")
    args = parser.parse_args()
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
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
    return args


if __name__ == "__main__":
    build(parse_args())
