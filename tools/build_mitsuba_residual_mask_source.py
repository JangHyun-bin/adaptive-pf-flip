#!/usr/bin/env python
"""Promote secondary residual-mask analysis into a reusable mask source."""

import argparse
import os
import shutil
from datetime import datetime, timezone
from types import SimpleNamespace

import numpy as np

try:
    from PIL import Image, ImageFilter, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageFilter = None
    ImageDraw = None

from analyze_mitsuba_contact_particle_masks import particle_rows
from analyze_mitsuba_secondary_channel_residual_masks import residual_candidates
from apply_mitsuba_target_region_response import write_gif
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
from build_mitsuba_secondary_channel_aov_package import draw_channel_density
from build_mitsuba_water_material_aov_package import luma_array, overlay_masks


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build residual mask sources")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def frame_map(frames):
    return {
        int(frame.get("output_frame")): frame
        for frame in frames
        if frame.get("output_frame") is not None
    }


def candidate_from_summary(summary, requested):
    if requested and requested != "best":
        return requested
    best = summary.get("best_target_dark_secondary") or {}
    candidate = best.get("candidate")
    if not candidate:
        raise SystemExit("analysis summary does not include best_target_dark_secondary.candidate")
    return candidate


def analysis_settings(summary, args):
    settings = summary.get("settings") or {}
    return SimpleNamespace(
        secondary_alpha_threshold=int(settings.get("secondary_alpha_threshold", 4)),
        radius_scale=float(settings.get("radius_scale", 1.0)),
        density_blur_radius=float(settings.get("density_blur_radius", 2.0)),
        dilate_radii=[int(item) for item in settings.get("dilate_radii", [])],
        band_ranges=[tuple(float(value) for value in item) for item in settings.get("band_ranges", [])],
        full_ranges=[float(item) for item in settings.get("full_ranges", [])],
        dark_luma_threshold=float(settings.get("dark_luma_threshold", 55.0)),
    )


def mask_rgba(mask, alpha_value, blur_radius):
    alpha = Image.fromarray((mask.astype(np.uint8) * int(alpha_value)), "L")
    if blur_radius > 0.0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
    rgba = Image.new("RGBA", alpha.size, (255, 255, 255, 0))
    rgba.putalpha(alpha)
    return rgba


def mask_rgb(mask, on=(210, 140, 255), off=(8, 12, 16)):
    h, w = mask.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    out[:, :] = off
    out[mask] = on
    return Image.fromarray(out, "RGB")


def labeled_strip(panels, labels, out_path):
    if not panels:
        raise ValueError("no panels")
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = width * index
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
        strip.paste(panel.convert("RGB"), (x, label_h))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
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
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def copy_json(src, assets_dir, name, label, root):
    return copy_asset(src, assets_dir, name, label, root)


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Mask GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Frame")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Candidate", summary.get("candidate")),
            ("Max coverage", f"{checks.get('max_mask_coverage', 0.0):.6f}"),
            ("Masks", format_bytes(checks.get("mask_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Mask GIF"></section>' if gif else ""
    figures = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
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
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; width: 100%; min-width: 960px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; word-break: break-word; }}
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
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Mask Source",
        "",
        f"- Candidate: `{summary.get('candidate')}`",
        f"- Frames: `{checks.get('frames')}`",
        f"- Max mask coverage: `{checks.get('max_mask_coverage')}`",
        f"- Mean mask coverage: `{checks.get('mean_mask_coverage')}`",
        f"- Mask bytes: `{format_bytes(checks.get('mask_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Coverage | Mask | Strip |",
        "| ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames", []):
        lines.append(
            f"| {frame['output_frame']} | {frame['layer_coverage']:.6f} | "
            f"`{frame['layer_repo_path']}` | `{frame['strip_repo_path']}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    analysis_path = require_file(args.analysis_summary, "residual mask analysis summary")
    analysis = read_json(analysis_path)
    if analysis.get("schema") != "lsfs_mitsuba_secondary_channel_residual_mask_analysis":
        raise SystemExit(f"{args.analysis_summary}: expected lsfs_mitsuba_secondary_channel_residual_mask_analysis")
    candidate = candidate_from_summary(analysis, args.candidate)
    settings = analysis_settings(analysis, args)

    out_dir = os.path.abspath(args.out_dir)
    mask_dir = os.path.join(out_dir, "masks")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(mask_dir, exist_ok=True)
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frames = []
    strip_paths = []
    mask_bytes = 0
    coverages = []
    for index, frame in enumerate(analysis.get("frames") or []):
        output_frame = int(frame["output_frame"])
        target_path = require_file(frame.get("target_repo_path"), "target image")
        actual_path = require_file(frame.get("actual_repo_path"), "actual image")
        layer_path = require_file(frame.get("layer_repo_path"), "secondary layer image")
        particles_path = require_file(frame.get("particles_repo_path"), "particles")
        xml_path = require_file(frame.get("xml_scene_repo_path"), "xml scene")

        target_img = Image.open(target_path).convert("RGB")
        actual_img = Image.open(actual_path).convert("RGB")
        layer_img = Image.open(layer_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")

        source_luma = luma_array(actual_img)
        alpha = np.asarray(layer_img.split()[3], dtype=np.uint8)
        ds6 = np.logical_and(alpha >= settings.secondary_alpha_threshold, source_luma <= 75.0)
        particles = particle_rows(particles_path)
        _channel_masks, _density, channel_union, _density_union, projected_counts = draw_channel_density(
            particles, xml_path, target_img.size, settings
        )
        candidates = residual_candidates(ds6, channel_union, source_luma, alpha, settings)
        if candidate not in candidates:
            available = ", ".join(sorted(candidates))
            raise SystemExit(f"candidate {candidate!r} not available; available: {available}")
        mask = candidates[candidate]
        rgba = mask_rgba(mask, args.mask_alpha, args.mask_blur_radius)
        mask_path = os.path.join(mask_dir, f"frame_{index:04d}_residual_mask.png")
        rgba.save(mask_path)

        overlay = overlay_masks(actual_img, [(mask, (210, 140, 255), 0.45)])
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_residual_mask_strip.png")
        labeled_strip(
            [target_img, actual_img, mask_rgb(mask), overlay],
            ["Target", "Actual", "Residual Mask", "Overlay"],
            strip_path,
        )
        strip_paths.append(strip_path)
        mask_size = os.path.getsize(mask_path)
        mask_bytes += mask_size
        coverage = float(mask.sum()) / float(max(1, mask.size))
        coverages.append(coverage)
        frames.append({
            "frame": index,
            "output_frame": output_frame,
            "sequence_frame": frame.get("sequence_frame"),
            "layer_repo_path": posix_rel(mask_path, root),
            "layer_path": mask_path,
            "layer_sha256": sha256_file(mask_path),
            "layer_size": mask_size,
            "layer_coverage": coverage,
            "source_layer_repo_path": posix_rel(layer_path, root),
            "target_repo_path": posix_rel(target_path, root),
            "actual_repo_path": posix_rel(actual_path, root),
            "particles_repo_path": posix_rel(particles_path, root),
            "xml_scene_repo_path": posix_rel(xml_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "strip_sha256": sha256_file(strip_path),
            "strip_size": os.path.getsize(strip_path),
            "projected_counts": projected_counts,
        })

    if not frames:
        raise SystemExit("no frames in analysis summary")

    gif_path = os.path.join(assets_dir, "residual_masks.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "residual_masks.gif", "Mask GIF", root)]
    for index, strip_path in enumerate(strip_paths):
        assets.append(copy_asset(strip_path, assets_dir, f"frame_{index:02d}_residual_mask_strip.png", f"Frame {index + 1} Strip", root))

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "residual_mask_source_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_json(analysis_path, assets_dir, "residual_mask_analysis_summary.json", "Residual analysis", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "candidate": candidate,
        "source": {
            "analysis_summary": posix_rel(analysis_path, root),
            "analysis_schema": analysis.get("schema"),
        },
        "settings": {
            "mask_alpha": args.mask_alpha,
            "mask_blur_radius": args.mask_blur_radius,
            "fps": args.fps,
            "analysis": {
                "secondary_alpha_threshold": settings.secondary_alpha_threshold,
                "radius_scale": settings.radius_scale,
                "density_blur_radius": settings.density_blur_radius,
                "dilate_radii": settings.dilate_radii,
                "band_ranges": settings.band_ranges,
                "full_ranges": settings.full_ranges,
            },
        },
        "checks": {
            "frames": len(frames),
            "mask_bytes": mask_bytes,
            "gif_bytes": os.path.getsize(gif_path),
            "max_mask_coverage": max(coverages),
            "mean_mask_coverage": sum(coverages) / float(len(coverages)),
        },
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
    summary_asset = copy_json(summary_path, assets_dir, "residual_mask_source_summary.json", "Mask source summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_residual_mask_source_gallery",
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
        f"status=ready frames={len(frames)} candidate={candidate} "
        f"max_coverage={summary['checks']['max_mask_coverage']:.6f} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", default="best")
    parser.add_argument("--mask-alpha", type=int, default=255)
    parser.add_argument("--mask-blur-radius", type=float, default=0.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Residual Mask Source")
    parser.add_argument("--next", default="Use this residual mask source in a localized native renderer candidate.")
    args = parser.parse_args(argv)
    if not (1 <= args.mask_alpha <= 255):
        parser.error("mask-alpha must be in [1, 255]")
    if args.mask_blur_radius < 0.0:
        parser.error("mask-blur-radius must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    build(args)


if __name__ == "__main__":
    main()
