#!/usr/bin/env python
"""Build reusable mask sources from Mitsuba source-response evidence."""

import argparse
import os
import shutil
from datetime import datetime, timezone
from types import SimpleNamespace

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None

from apply_mitsuba_source_region_response import (
    SOURCE_RESPONSE_PROFILES,
    apply_profile,
    channel_union_mask,
    classify_response_pixels,
    export_frame_map,
)
from apply_mitsuba_target_region_response import (
    composite_path,
    layer_path,
    output_frame_map,
    resolve_path,
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


MASK_KINDS = (
    "highlight",
    "dark-secondary",
    "dark-secondary-primary",
    "channel-band",
    "response-union",
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build source-response masks")


def mask_union(*masks):
    if not masks:
        return []
    return [any(values) for values in zip(*masks)]


def enabled_mask(mask, enabled):
    return mask if enabled else [False for _value in mask]


def select_mask(masks, kind, args):
    if kind == "highlight":
        return enabled_mask(masks["highlight"], args.highlight_strength > 0.0)
    if kind == "dark-secondary-primary":
        return enabled_mask(masks["dark_secondary_primary"], args.dark_secondary_strength > 0.0)
    if kind == "channel-band":
        return enabled_mask(masks["dark_secondary_channel_band"], args.channel_band_strength > 0.0)
    dark_secondary = mask_union(
        enabled_mask(masks["dark_secondary_primary"], args.dark_secondary_strength > 0.0),
        enabled_mask(masks["dark_secondary_ring"], args.dark_secondary_ring_strength > 0.0),
        enabled_mask(masks["dark_secondary_channel_band"], args.channel_band_strength > 0.0),
        enabled_mask(masks["dark_secondary_soft"], args.dark_secondary_soft_strength > 0.0),
    )
    if kind == "dark-secondary":
        return dark_secondary
    if kind == "response-union":
        return mask_union(enabled_mask(masks["highlight"], args.highlight_strength > 0.0), dark_secondary)
    raise ValueError(f"unknown mask kind {kind!r}")


def mask_image(mask, size, alpha_value, blur_radius, dilate_radius):
    alpha = Image.frombytes("L", size, bytes(255 if value else 0 for value in mask))
    if dilate_radius > 0:
        alpha = alpha.filter(ImageFilter.MaxFilter(dilate_radius * 2 + 1))
    if blur_radius > 0.0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
    if alpha_value != 255:
        alpha = alpha.point(lambda value: max(0, min(255, int(value * alpha_value / 255.0))))
    rgba = Image.new("RGBA", size, (255, 255, 255, 0))
    rgba.putalpha(alpha)
    return rgba


def mask_preview(mask, size):
    img = Image.new("RGB", size, (8, 12, 16))
    pixels = img.load()
    width, height = size
    for index, value in enumerate(mask):
        if value:
            x = index % width
            y = index // width
            if y < height:
                pixels[x, y] = (180, 225, 255)
    return img


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


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    item = {
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
            ("Mask kind", summary.get("mask_kind")),
            ("Frames", checks.get("frames")),
            ("Max coverage", f"{checks.get('max_mask_coverage', 0.0):.6f}"),
            ("Mask bytes", format_bytes(checks.get("mask_bytes", 0))),
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
        "## Settings",
        "",
        f"- Profile: `{summary['settings']['profile']}`",
        f"- Mask kind: `{summary['mask_kind']}`",
        f"- Alpha value: `{summary['settings']['alpha_value']}`",
        f"- Blur radius: `{summary['settings']['blur_radius']}`",
        f"- Dilate radius: `{summary['settings']['dilate_radius']}`",
        f"- Channel mask channels: `{summary['settings'].get('channel_mask_channels')}`",
        f"- Secondary alpha threshold: `{summary['settings'].get('secondary_alpha_threshold')}`",
        f"- Highlight source luma threshold: `{summary['settings'].get('highlight_source_luma_threshold')}`",
        f"- Highlight alpha max: `{summary['settings'].get('highlight_alpha_max')}`",
        f"- Channel band source luma: `{summary['settings'].get('channel_band_source_luma_min')}..{summary['settings'].get('channel_band_source_luma_max')}`",
        f"- Channel band strength: `{summary['settings'].get('channel_band_strength')}`",
        f"- Channel band max delta: `{summary['settings'].get('channel_band_max_delta')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Max mask coverage: `{checks.get('max_mask_coverage')}`",
        f"- Mean mask coverage: `{checks.get('mean_mask_coverage')}`",
        f"- Mask bytes: `{format_bytes(checks.get('mask_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frames",
        "",
        "| Output | Coverage | Mask | Strip |",
        "| ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame['output_frame']} | {frame['layer_coverage']:.6f} | "
            f"`{frame['layer_repo_path']}` | `{frame['strip_repo_path']}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def args_namespace(args):
    values = vars(args).copy()
    return SimpleNamespace(**values)


def build(args):
    require_pillow()
    root = os.getcwd()
    composite_summary_path = require_file(args.composite_summary, "composite summary")
    composite_summary = read_json(composite_summary_path)
    if composite_summary.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.composite_summary}: expected secondary composite or composite grade schema")
    composite_frames = output_frame_map(composite_summary.get("frames") or [])

    export_summary_path = None
    export_frames = {}
    if args.mitsuba_export:
        export_summary_path = require_file(args.mitsuba_export, "Mitsuba export")
        export_summary = read_json(export_summary_path)
        if export_summary.get("schema") != "lsfs_mitsuba_xml_export":
            raise SystemExit(f"{args.mitsuba_export}: expected lsfs_mitsuba_xml_export schema")
        export_frames = export_frame_map(export_summary)

    response_args = args_namespace(args)
    apply_profile(response_args)

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
    mask_paths = []
    coverages = []
    for index, output_frame in enumerate(sorted(composite_frames)):
        frame = composite_frames[output_frame]
        source_path = require_file(composite_path(frame), "source/composite frame")
        layer_img_path = require_file(layer_path(frame), "secondary layer")
        source_img = Image.open(source_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if source_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        channel_mask = None
        channel_metadata = None
        if args.mask_kind in ("channel-band", "dark-secondary", "response-union"):
            if response_args.channel_band_strength > 0.0:
                if output_frame not in export_frames:
                    raise SystemExit(f"missing Mitsuba export frame for output_frame={output_frame}")
                channel_mask, channel_metadata = channel_union_mask(
                    export_frames[output_frame],
                    source_img.size,
                    response_args,
                )
        _actual_bytes, _alpha_bytes, _source_luma, masks = classify_response_pixels(
            source_img,
            layer_img,
            response_args,
            channel_mask=channel_mask,
        )
        selected = select_mask(masks, args.mask_kind, response_args)
        coverage = sum(1 for value in selected if value) / float(max(1, len(selected)))
        mask = mask_image(selected, source_img.size, args.alpha_value, args.blur_radius, args.dilate_radius)
        mask_path = os.path.join(mask_dir, f"frame_{index:04d}.png")
        mask.save(mask_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_source_response_mask.png")
        labeled_strip(
            [source_img, layer_img.convert("RGB"), mask_preview(selected, source_img.size), mask.convert("RGB")],
            ["Source", "Secondary Layer", "Selected Mask", "RGBA Mask"],
            strip_path,
        )
        strip_paths.append(strip_path)
        mask_paths.append(mask_path)
        coverages.append(coverage)
        frame_item = {
            "frame": index,
            "output_frame": output_frame,
            "composite_repo_path": posix_rel(source_path, root),
            "source_repo_path": posix_rel(source_path, root),
            "source_sha256": sha256_file(source_path),
            "secondary_layer_repo_path": posix_rel(layer_img_path, root),
            "layer_repo_path": posix_rel(mask_path, root),
            "layer_path": mask_path,
            "layer_sha256": sha256_file(mask_path),
            "layer_size": os.path.getsize(mask_path),
            "layer_dimensions": image_dimensions(mask_path),
            "layer_coverage": coverage,
            "strip_repo_path": posix_rel(strip_path, root),
            "strip_sha256": sha256_file(strip_path),
        }
        if channel_metadata:
            frame_item["channel_band"] = channel_metadata
        frames.append(frame_item)

    if not frames:
        raise SystemExit("no source-response mask frames generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(mask_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Mask GIF", root)]
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"strip_{out_index:02d}.png", f"Frame {out_index + 1} Strip", root))

    summary_path = os.path.join(out_dir, "source_response_mask_source_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_source_response_mask_source",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "mask_kind": args.mask_kind,
        "candidate": f"{args.profile}_{args.mask_kind}",
        "compat_schema": "lsfs_mitsuba_secondary_composite",
        "source": {
            "composite_summary": posix_rel(composite_summary_path, root),
            "mitsuba_export": posix_rel(export_summary_path, root) if export_summary_path else None,
        },
        "settings": {
            "profile": args.profile,
            "alpha_value": args.alpha_value,
            "blur_radius": args.blur_radius,
            "dilate_radius": args.dilate_radius,
            "fps": args.fps,
            "keyframes": args.keyframes,
            "channel_mask_channels": sorted(args.channel_mask_channels_set),
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_source_luma_threshold": args.highlight_source_luma_threshold,
            "highlight_alpha_max": args.highlight_alpha_max,
            "highlight_strength": args.highlight_strength,
            "highlight_max_delta": args.highlight_max_delta,
            "dark_secondary_source_luma_min": args.dark_secondary_source_luma_min,
            "dark_secondary_source_luma_max": args.dark_secondary_source_luma_max,
            "dark_secondary_strength": args.dark_secondary_strength,
            "dark_secondary_max_delta": args.dark_secondary_max_delta,
            "channel_band_source_luma_min": args.channel_band_source_luma_min,
            "channel_band_source_luma_max": args.channel_band_source_luma_max,
            "channel_band_strength": args.channel_band_strength,
            "channel_band_max_delta": args.channel_band_max_delta,
            "channel_band_dilate_radius": args.channel_band_dilate_radius,
        },
        "checks": {
            "frames": len(frames),
            "max_mask_coverage": max(coverages),
            "mean_mask_coverage": sum(coverages) / len(coverages),
            "mask_bytes": sum(os.path.getsize(path) for path in mask_paths),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "source_response_mask_source_summary.json", "Mask source summary", root)
    source_asset = copy_asset(composite_summary_path, assets_dir, "composite_summary.json", "Composite summary", root)
    metadata_files = [summary_asset, source_asset]
    if export_summary_path:
        metadata_files.append(copy_asset(export_summary_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root))
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
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_source_response_mask_source_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "index_repo_path": posix_rel(index_path, root),
        "summary_repo_path": posix_rel(summary_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready kind={args.mask_kind} frames={len(frames)} "
        f"max_coverage={summary['checks']['max_mask_coverage']:.6f} summary={summary_path}"
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build source-response evidence mask sources for Mitsuba")
    parser.add_argument("composite_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--mask-kind", choices=MASK_KINDS, default="response-union")
    parser.add_argument("--profile", choices=("default", *sorted(SOURCE_RESPONSE_PROFILES)), default="default")
    parser.add_argument("--mitsuba-export")
    parser.add_argument("--alpha-value", type=int, default=255)
    parser.add_argument("--blur-radius", type=float, default=0.0)
    parser.add_argument("--dilate-radius", type=int, default=0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Source-Response Mask Source")
    parser.add_argument("--next", default="Use this mask source in a renderer-side response candidate.")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-source-luma-threshold", type=float, default=145.0)
    parser.add_argument("--highlight-alpha-max", type=int, default=255)
    parser.add_argument("--highlight-strength", type=float, default=0.35)
    parser.add_argument("--highlight-max-delta", type=float, default=55.0)
    parser.add_argument("--dark-secondary-source-luma-min", type=float, default=20.0)
    parser.add_argument("--dark-secondary-source-luma-max", type=float, default=105.0)
    parser.add_argument("--dark-secondary-strength", type=float, default=0.35)
    parser.add_argument("--dark-secondary-max-delta", type=float, default=55.0)
    parser.add_argument("--dark-secondary-ring-radius", type=int, default=0)
    parser.add_argument("--dark-secondary-ring-source-luma-min", type=float, default=0.0)
    parser.add_argument("--dark-secondary-ring-source-luma-max", type=float, default=95.0)
    parser.add_argument("--dark-secondary-ring-strength", type=float, default=0.0)
    parser.add_argument("--dark-secondary-ring-max-delta", type=float, default=35.0)
    parser.add_argument("--channel-band-source-luma-min", type=float, default=75.0)
    parser.add_argument("--channel-band-source-luma-max", type=float, default=85.0)
    parser.add_argument("--channel-band-strength", type=float, default=0.0)
    parser.add_argument("--channel-band-max-delta", type=float, default=48.0)
    parser.add_argument("--channel-band-dilate-radius", type=int, default=0)
    parser.add_argument("--channel-mask-channels", default="spray,foam,bubble,droplet",
                        help="comma-separated projected secondary channels used by channel-band response")
    parser.add_argument("--channel-radius-scale", type=float, default=1.0)
    parser.add_argument("--channel-density-blur-radius", type=float, default=2.0)
    parser.add_argument("--dark-secondary-soft-source-luma-min", type=float, default=75.0)
    parser.add_argument("--dark-secondary-soft-source-luma-max", type=float, default=95.0)
    parser.add_argument("--dark-secondary-soft-strength", type=float, default=0.0)
    parser.add_argument("--dark-secondary-soft-max-delta", type=float, default=35.0)
    parser.add_argument("--nonsecondary-lift", type=float, default=0.0)
    args = parser.parse_args(argv)
    if not (0 <= args.alpha_value <= 255):
        parser.error("alpha-value must be in [0, 255]")
    if args.blur_radius < 0.0:
        parser.error("blur-radius must be non-negative")
    if args.dilate_radius < 0:
        parser.error("dilate-radius must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.highlight_alpha_max < 0 or args.highlight_alpha_max > 255:
        parser.error("highlight-alpha-max must be in [0, 255]")
    valid_channels = {"spray", "foam", "bubble", "droplet"}
    args.channel_mask_channels_set = {
        item.strip().lower()
        for item in str(args.channel_mask_channels).split(",")
        if item.strip()
    }
    if not args.channel_mask_channels_set:
        parser.error("channel-mask-channels must contain at least one channel")
    invalid_channels = sorted(args.channel_mask_channels_set - valid_channels)
    if invalid_channels:
        parser.error(f"unknown channel-mask-channels: {', '.join(invalid_channels)}")
    return args


def main(argv=None):
    build(parse_args(argv))


if __name__ == "__main__":
    main()
