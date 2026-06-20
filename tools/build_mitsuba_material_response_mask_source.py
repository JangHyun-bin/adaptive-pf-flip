#!/usr/bin/env python
"""Build projected material-response masks from fitted response controls."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None

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
from validate_mitsuba_visual_cache_bundle import resolve_path


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build material-response masks")


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def controls_by_output(controls):
    grouped = {}
    for control in controls or []:
        grouped.setdefault(control.get("output_frame"), []).append(control)
    return grouped


def aov_path(frame, name):
    entry = ((frame.get("aovs") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


def source_entry(path, root, label, payload=None):
    resolved = require_file(path, label)
    entry = {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["status"] = payload.get("status")
        entry["version"] = payload.get("version")
    return entry


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def control_alpha(control, args):
    strength = float(control.get("fit_strength") or 0.0)
    response = control.get("native_response") or {}
    scattering = float(response.get("scattering_scale") or 0.0)
    albedo = float(response.get("albedo_lift") or 0.0)
    value = args.base_alpha + strength * args.strength_alpha_gain + scattering * args.scattering_alpha_gain + albedo * args.albedo_alpha_gain
    return int(round(clamp(value, 0.0, 1.0) * 255.0))


def padded_bbox(control, args):
    x0, y0, x1, y1 = [float(item) for item in (control.get("bbox_px") or [0, 0, -1, -1])]
    response = control.get("native_response") or {}
    pad = args.bbox_pad + float(response.get("mask_blur_px") or 0.0) * args.blur_pad_scale
    return [x0 - pad, y0 - pad, x1 + pad, y1 + pad]


def draw_control(mask, control, args):
    draw = ImageDraw.Draw(mask)
    width, height = mask.size
    x0, y0, x1, y1 = padded_bbox(control, args)
    x0 = int(round(clamp(x0, 0, width - 1)))
    x1 = int(round(clamp(x1, 0, width - 1)))
    y0 = int(round(clamp(y0, 0, height - 1)))
    y1 = int(round(clamp(y1, 0, height - 1)))
    if x1 < x0 or y1 < y0:
        return
    alpha = control_alpha(control, args)
    if args.shape == "ellipse":
        draw.ellipse([x0, y0, x1, y1], fill=alpha)
    else:
        draw.rectangle([x0, y0, x1, y1], fill=alpha)


def mask_coverage(mask, threshold):
    values = mask.tobytes()
    if not values:
        return 0.0
    active = sum(1 for value in values if value >= threshold)
    return active / float(len(values))


def mask_preview(mask):
    preview = Image.new("RGB", mask.size, (8, 12, 16))
    pix = preview.load()
    mpix = mask.load()
    width, height = mask.size
    for y in range(height):
        for x in range(width):
            value = mpix[x, y]
            if value:
                pix[x, y] = (80 + value // 3, 150 + value // 4, 210)
    return preview


def overlay_source(source, mask):
    base = source.convert("RGBA")
    tint = Image.new("RGBA", source.size, (100, 190, 255, 0))
    tint.putalpha(mask.point(lambda value: min(180, int(value * 0.75))))
    return Image.alpha_composite(base, tint).convert("RGB")


def labeled_strip(panels, labels, out_path):
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


def write_gif(paths, gif_path, fps):
    images = [Image.open(path).convert("RGB") for path in paths]
    if not images:
        return
    duration = int(round(1000.0 / max(0.1, fps)))
    os.makedirs(os.path.dirname(gif_path), exist_ok=True)
    images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration, loop=0)


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        with open(src, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
    item = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        item["dimensions"] = dims
    return item


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Mask GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Controls", checks.get("controls")),
            ("Max coverage", f"{checks.get('max_mask_coverage', 0.0):.6f}"),
            ("Mask bytes", format_bytes(checks.get("mask_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Mask GIF"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
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
    settings = summary.get("settings") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Settings",
        "",
        f"- Shape: `{settings.get('shape')}`",
        f"- Base alpha: `{settings.get('base_alpha')}`",
        f"- Blur radius: `{settings.get('blur_radius')}`",
        f"- Dilate radius: `{settings.get('dilate_radius')}`",
        f"- BBox pad: `{settings.get('bbox_pad')}`",
        f"- Blur pad scale: `{settings.get('blur_pad_scale')}`",
        f"- Coverage threshold: `{settings.get('coverage_threshold')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Controls: `{checks.get('controls')}`",
        f"- Frames with controls: `{checks.get('frames_with_controls')}`",
        f"- Max mask coverage: `{checks.get('max_mask_coverage')}`",
        f"- Mean mask coverage: `{checks.get('mean_mask_coverage')}`",
        f"- Mask bytes: `{format_bytes(checks.get('mask_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frames",
        "",
        "| Output | Controls | Coverage | Mask | Strip |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('control_count')} | {frame.get('layer_coverage'):.6f} | "
            f"`{frame.get('layer_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    contract_path = require_file(args.material_response_contract, "material response contract")
    aov_path_arg = require_file(args.aov_summary, "visual-cache AOV summary")
    contract = read_json(contract_path)
    aovs = read_json(aov_path_arg)
    if contract.get("schema") != "lsfs_mitsuba_material_response_contract":
        raise SystemExit(f"{args.material_response_contract}: expected lsfs_mitsuba_material_response_contract schema")
    if contract.get("status") != "ready":
        raise SystemExit(f"{args.material_response_contract}: contract status is {contract.get('status')!r}")
    if aovs.get("schema") != "lsfs_mitsuba_visual_cache_aov_package":
        raise SystemExit(f"{args.aov_summary}: expected lsfs_mitsuba_visual_cache_aov_package schema")

    out_dir = os.path.abspath(args.out_dir)
    mask_dir = os.path.join(out_dir, "masks")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(mask_dir, exist_ok=True)
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    controls_map = controls_by_output(contract.get("controls") or [])
    frames = []
    strip_paths = []
    total_coverage = 0.0
    max_coverage = 0.0
    mask_bytes = 0
    for frame_index, aov_frame in enumerate(aovs.get("frames") or []):
        output_frame = aov_frame.get("output_frame")
        src_ref = aov_path(aov_frame, args.source_aov)
        if not src_ref:
            src_ref = aov_path(aov_frame, "base_rgb") or aov_path(aov_frame, "composite_rgb") or aov_path(aov_frame, "target_rgb")
        source_path = resolve_path(src_ref, root)
        if not source_path or not os.path.isfile(source_path):
            raise SystemExit(f"missing source image for output_frame={output_frame}: {src_ref}")
        source = Image.open(source_path).convert("RGB")
        mask = Image.new("L", source.size, 0)
        controls = controls_map.get(output_frame, [])
        for control in controls:
            draw_control(mask, control, args)
        if args.dilate_radius > 0:
            mask = mask.filter(ImageFilter.MaxFilter(args.dilate_radius * 2 + 1))
        if args.blur_radius > 0.0:
            mask = mask.filter(ImageFilter.GaussianBlur(args.blur_radius))
        mask_path = os.path.join(mask_dir, f"frame_{frame_index:04d}.png")
        strip_path = os.path.join(strip_dir, f"frame_{frame_index:04d}.png")
        mask.save(mask_path)
        labeled_strip(
            [source, overlay_source(source, mask), mask_preview(mask)],
            ["source", "material mask overlay", "mask"],
            strip_path,
        )
        strip_paths.append(strip_path)
        coverage = mask_coverage(mask, args.coverage_threshold)
        total_coverage += coverage
        max_coverage = max(max_coverage, coverage)
        mask_bytes += os.path.getsize(mask_path)
        frames.append({
            "frame": aov_frame.get("frame"),
            "output_frame": output_frame,
            "control_count": len(controls),
            "controls": [control.get("control_id") for control in controls],
            "layer_path": os.path.abspath(mask_path),
            "layer_repo_path": posix_rel(mask_path, root),
            "layer_sha256": sha256_file(mask_path),
            "layer_size": os.path.getsize(mask_path),
            "layer_dimensions": list(mask.size),
            "layer_coverage": coverage,
            "source_path": os.path.abspath(source_path),
            "source_repo_path": posix_rel(source_path, root),
            "source_sha256": sha256_file(source_path),
            "strip_repo_path": posix_rel(strip_path, root),
            "strip_sha256": sha256_file(strip_path),
        })

    gif_path = os.path.join(assets_dir, "material_response_mask.gif")
    write_gif(strip_paths, gif_path, args.fps)
    summary_path = os.path.join(out_dir, "material_response_mask_source_summary.json")
    assets = [copy_asset(gif_path, assets_dir, "material_response_mask.gif", "Mask GIF", root)]
    for out_index, frame_index in enumerate(sorted(set([0, len(strip_paths) // 2, len(strip_paths) - 1])) if strip_paths else []):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"frame_{out_index:02d}.png", f"Frame {frame_index}", root))
    metadata_files = [
        copy_asset(contract_path, assets_dir, "material_response_contract.json", "Material contract", root),
        copy_asset(aov_path_arg, assets_dir, "visual_cache_aov_summary.json", "AOV summary", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_source_response_mask_source",
        "subschema": "lsfs_mitsuba_material_response_mask_source",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if frames else "review",
        "sources": {
            "material_response_contract": source_entry(contract_path, root, "material response contract", contract),
            "visual_cache_aov_summary": source_entry(aov_path_arg, root, "visual-cache AOV summary", aovs),
        },
        "mask_kind": "material_response_bbox",
        "settings": {
            "source_aov": args.source_aov,
            "shape": args.shape,
            "base_alpha": args.base_alpha,
            "strength_alpha_gain": args.strength_alpha_gain,
            "scattering_alpha_gain": args.scattering_alpha_gain,
            "albedo_alpha_gain": args.albedo_alpha_gain,
            "blur_radius": args.blur_radius,
            "dilate_radius": args.dilate_radius,
            "bbox_pad": args.bbox_pad,
            "blur_pad_scale": args.blur_pad_scale,
            "coverage_threshold": args.coverage_threshold,
        },
        "checks": {
            "frames": len(frames),
            "controls": sum(len(item.get("controls") or []) for item in frames),
            "frames_with_controls": sum(1 for item in frames if item.get("control_count")),
            "max_mask_coverage": max_coverage,
            "mean_mask_coverage": total_coverage / float(max(1, len(frames))),
            "mask_bytes": mask_bytes,
            "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        },
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    index_path = os.path.join(gallery_dir, "index.html")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "material_response_mask_source_summary.json", "Mask source summary", root)
    metadata_files.append(summary_asset)
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_material_response_mask_source_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} frames={summary['checks']['frames']} controls={summary['checks']['controls']} "
        f"max_coverage={summary['checks']['max_mask_coverage']:.6f} summary={summary_path}"
    )
    if summary["status"] != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build material-response mask sources from fitted controls")
    parser.add_argument("material_response_contract")
    parser.add_argument("aov_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--source-aov", default="base_rgb")
    parser.add_argument("--shape", choices=["rectangle", "ellipse"], default="ellipse")
    parser.add_argument("--base-alpha", type=float, default=0.12)
    parser.add_argument("--strength-alpha-gain", type=float, default=2.2)
    parser.add_argument("--scattering-alpha-gain", type=float, default=1.2)
    parser.add_argument("--albedo-alpha-gain", type=float, default=1.0)
    parser.add_argument("--bbox-pad", type=float, default=2.0)
    parser.add_argument("--blur-pad-scale", type=float, default=1.0)
    parser.add_argument("--blur-radius", type=float, default=4.0)
    parser.add_argument("--dilate-radius", type=int, default=2)
    parser.add_argument("--coverage-threshold", type=int, default=8)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S483 Mitsuba Material Response Mask Source")
    parser.add_argument("--next", default="Feed this mask source into split_mitsuba_water_mask_material.py with empty-mask no-op frames enabled.")
    args = parser.parse_args(argv)
    if args.coverage_threshold < 0 or args.coverage_threshold > 255:
        parser.error("coverage-threshold must be in [0, 255]")
    if args.dilate_radius < 0:
        parser.error("dilate-radius must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    build(args)


if __name__ == "__main__":
    main()
