#!/usr/bin/env python
"""Convert low-frequency correction masks into Mitsuba response mask sources."""

import argparse
import html
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

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


EXPECTED_SCHEMA = "lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter"
OUTPUT_SCHEMA = "lsfs_mitsuba_source_response_mask_source"


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build low-frequency response mask sources")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def frame_path(frame, *keys):
    for key in keys:
        value = frame.get(key)
        if value:
            return value
    bindings = frame.get("runtime_bindings") or {}
    for key in keys:
        value = bindings.get(key)
        if value:
            return value
    return None


def alpha_from_mask(mask_img, scale):
    alpha = mask_img.convert("L")
    if scale != 1.0:
        alpha = alpha.point(lambda value: max(0, min(255, int(round(value * scale)))))
    return alpha


def alpha_coverage(alpha):
    width, height = alpha.size
    hist = alpha.histogram()
    nonzero = width * height - hist[0]
    strong = sum(hist[128:])
    weighted = sum(index * count for index, count in enumerate(hist)) / float(max(1, width * height * 255))
    return {
        "coverage": nonzero / float(max(1, width * height)),
        "strong_coverage": strong / float(max(1, width * height)),
        "mean": weighted,
        "max": max((index for index, count in enumerate(hist) if count), default=0),
    }


def rgba_layer(alpha):
    layer = Image.new("RGBA", alpha.size, (255, 255, 255, 0))
    layer.putalpha(alpha)
    return layer


def alpha_preview(alpha):
    preview = Image.new("RGB", alpha.size, (8, 12, 16))
    pix_out = preview.load()
    pix_alpha = alpha.load()
    width, height = alpha.size
    for y in range(height):
        for x in range(width):
            value = pix_alpha[x, y]
            if value:
                pix_out[x, y] = (
                    min(255, 32 + value // 3),
                    min(255, 92 + value // 2),
                    min(255, 150 + value // 2),
                )
    return preview


def overlay_preview(source, alpha):
    base = source.convert("RGBA")
    tint = Image.new("RGBA", source.size, (80, 190, 255, 0))
    tint.putalpha(alpha.point(lambda value: min(170, int(value * 0.65))))
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


def write_gif(frame_paths, out_path, fps):
    if not frame_paths:
        return
    frames = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    duration = max(1, int(round(1000.0 / max(0.001, fps))))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=False,
    )


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


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Mask GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Mean coverage", f"{checks.get('mean_mask_coverage', 0.0):.6f}"),
            ("Max coverage", f"{checks.get('max_mask_coverage', 0.0):.6f}"),
            ("Mask bytes", format_bytes(checks.get("mask_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{html.escape(gif["href"])}" alt="Mask GIF"></section>' if gif else ""
    figures = "\n".join(
        f"""
        <figure>
          <a href="{html.escape(item['href'])}"><img src="{html.escape(item['href'])}" alt="{html.escape(item['label'])}"></a>
          <figcaption>{html.escape(item['label'])}</figcaption>
        </figure>"""
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
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
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
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
        "## Inputs",
        "",
        f"- Sequence summary: `{summary['sources']['sequence_summary']['repo_path']}`",
        f"- Source schema: `{summary['sources']['sequence_summary'].get('schema')}`",
        f"- Mask kind: `{summary['mask_kind']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Dimension mismatches: `{checks.get('dimension_mismatches')}`",
        f"- Mean mask coverage: `{checks.get('mean_mask_coverage')}`",
        f"- Max mask coverage: `{checks.get('max_mask_coverage')}`",
        f"- Mean strong coverage: `{checks.get('mean_strong_mask_coverage')}`",
        f"- Mask bytes: `{format_bytes(checks.get('mask_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frames",
        "",
        "| Output | Render Seq | Coverage | Strong | Layer | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('render_sequence_frame')} | "
            f"{frame.get('layer_coverage'):.6f} | {frame.get('layer_strong_coverage'):.6f} | "
            f"`{frame.get('layer_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def source_entry(path, root, label, payload=None):
    entry = {
        "label": label,
        "path": os.path.abspath(path),
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
    return entry


def build(args):
    require_pillow()
    root = os.getcwd()
    sequence_summary_path = require_file(args.sequence_summary, "low-frequency sequence summary")
    sequence_summary = read_json(sequence_summary_path)
    if sequence_summary.get("schema") != EXPECTED_SCHEMA:
        raise SystemExit(f"{args.sequence_summary}: expected {EXPECTED_SCHEMA} schema")
    if sequence_summary.get("status") != "ready":
        raise SystemExit(f"{args.sequence_summary}: sequence summary status is {sequence_summary.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    mask_dir = os.path.join(out_dir, "masks")
    preview_dir = os.path.join(out_dir, "previews")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (mask_dir, preview_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    frames = []
    layer_paths = []
    preview_paths = []
    strip_paths = []
    coverages = []
    strong_coverages = []
    for index, frame in enumerate(sequence_summary.get("frames") or []):
        source_ref = frame_path(frame, "raw_repo_path", "base_rgb")
        corrected_ref = frame_path(frame, "corrected_repo_path")
        mask_ref = frame_path(frame, "mask_repo_path", "correction_mask")
        source_path = require_file(resolve_path(source_ref), "source frame")
        corrected_path = require_file(resolve_path(corrected_ref), "corrected frame") if corrected_ref else None
        mask_path = require_file(resolve_path(mask_ref), "correction mask")

        source_img = Image.open(source_path).convert("RGB")
        mask_img = Image.open(mask_path)
        alpha = alpha_from_mask(mask_img, args.alpha_scale)
        if alpha.size != source_img.size:
            raise SystemExit(f"image size mismatch for output_frame={frame.get('output_frame')}")
        corrected_img = Image.open(corrected_path).convert("RGB") if corrected_path else source_img
        if corrected_img.size != source_img.size:
            raise SystemExit(f"corrected/source image size mismatch for output_frame={frame.get('output_frame')}")

        metrics = alpha_coverage(alpha)
        coverages.append(metrics["coverage"])
        strong_coverages.append(metrics["strong_coverage"])

        layer = rgba_layer(alpha)
        layer_path = os.path.join(mask_dir, f"frame_{index:04d}_low_frequency_response_mask.png")
        layer.save(layer_path)
        preview_path = os.path.join(preview_dir, f"frame_{index:04d}_low_frequency_response_preview.png")
        alpha_panel = alpha_preview(alpha)
        alpha_panel.save(preview_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_low_frequency_response_mask_source.png")
        labeled_strip(
            [source_img, corrected_img, alpha_panel, overlay_preview(source_img, alpha)],
            ["Source", "Corrected", "Mask Alpha", "Source Overlay"],
            strip_path,
        )
        layer_paths.append(layer_path)
        preview_paths.append(preview_path)
        strip_paths.append(strip_path)

        frames.append({
            "frame": index,
            "output_frame": frame.get("output_frame", index),
            "sequence_frame": frame.get("render_sequence_frame"),
            "render_sequence_frame": frame.get("render_sequence_frame"),
            "composite_repo_path": posix_rel(source_path, root),
            "source_repo_path": posix_rel(source_path, root),
            "source_sha256": sha256_file(source_path),
            "corrected_repo_path": posix_rel(corrected_path, root) if corrected_path else None,
            "corrected_sha256": sha256_file(corrected_path) if corrected_path else None,
            "input_mask_repo_path": posix_rel(mask_path, root),
            "input_mask_sha256": sha256_file(mask_path),
            "layer_path": layer_path,
            "layer_repo_path": posix_rel(layer_path, root),
            "layer_sha256": sha256_file(layer_path),
            "layer_size": os.path.getsize(layer_path),
            "layer_dimensions": image_dimensions(layer_path),
            "layer_coverage": metrics["coverage"],
            "layer_strong_coverage": metrics["strong_coverage"],
            "layer_mean": metrics["mean"],
            "layer_max": metrics["max"],
            "mask_metric": frame.get("mask"),
            "corrected_change": frame.get("corrected_change"),
            "runtime_bindings": frame.get("runtime_bindings"),
            "strip_repo_path": posix_rel(strip_path, root),
            "strip_sha256": sha256_file(strip_path),
        })

    if not frames:
        raise SystemExit("no low-frequency response mask frames generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(preview_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Mask GIF", root)]
    key_count = min(args.keyframes, len(strip_paths))
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, key_count - 1))) for i in range(key_count)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"strip_{out_index:02d}.png", f"Frame {out_index + 1} Strip", root))

    summary_path = os.path.abspath(args.summary) if args.summary else os.path.join(out_dir, "source_response_mask_source_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": OUTPUT_SCHEMA,
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "mask_kind": "low-frequency-correction",
        "candidate": "s515_full48_t4_low_frequency_correction_mask",
        "compat_schema": EXPECTED_SCHEMA,
        "sources": {
            "sequence_summary": source_entry(sequence_summary_path, root, "low-frequency sequence summary", sequence_summary),
        },
        "source": {
            "sequence_summary": posix_rel(sequence_summary_path, root),
        },
        "settings": {
            "alpha_scale": args.alpha_scale,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frames),
            "missing_references": 0,
            "dimension_mismatches": 0,
            "max_mask_coverage": max(coverages),
            "mean_mask_coverage": sum(coverages) / float(len(coverages)),
            "max_strong_mask_coverage": max(strong_coverages),
            "mean_strong_mask_coverage": sum(strong_coverages) / float(len(strong_coverages)),
            "mask_bytes": sum(os.path.getsize(path) for path in layer_paths),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "source_response_mask_source_summary.json", "Mask source summary", root)
    source_asset = copy_asset(sequence_summary_path, assets_dir, "sequence_summary.json", "Sequence summary", root)
    metadata_files = [summary_asset, source_asset]
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
        "schema": "lsfs_mitsuba_low_frequency_response_mask_source_gallery",
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
        f"status=ready kind={summary['mask_kind']} frames={len(frames)} "
        f"max_coverage={summary['checks']['max_mask_coverage']:.6f} summary={summary_path}"
    )
    if args.fail_on_review and summary["status"] != "ready":
        raise SystemExit(1)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build low-frequency correction response mask sources for Mitsuba")
    parser.add_argument("sequence_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary")
    parser.add_argument("--alpha-scale", type=float, default=1.0)
    parser.add_argument("--fps", type=float, default=8.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Low-Frequency Response Mask Source")
    parser.add_argument("--next", default="Build a renderer-native light/material response contract from this low-frequency correction mask source.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.alpha_scale <= 0.0:
        parser.error("alpha-scale must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    return args


def main(argv=None):
    build(parse_args(argv))


if __name__ == "__main__":
    main()
