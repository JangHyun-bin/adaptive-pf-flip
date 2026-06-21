#!/usr/bin/env python
"""Build response delta buffers from a full Mitsuba render and a base-only render."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageOps = None

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
from build_mitsuba_reference_gap import frame_map_from_sequence
from compare_mitsuba_renderer_target_gap import max_abs_diff, mean_abs_diff, write_gif


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a response delta buffer")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def preview_frame_map(render, role):
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{role}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{role}: render status is {render.get('status')!r}")
    frames = {}
    for frame in render.get("frames") or []:
        output = frame.get("output_frame")
        preview = frame.get("preview") or {}
        path = resolve_path(preview.get("path") or preview.get("repo_path"))
        frames[output] = {
            "output_frame": output,
            "sequence_frame": frame.get("sequence_frame"),
            "path": path,
        }
    return frames


def parse_scales(value):
    scales = []
    for item in str(value).split(","):
        item = item.strip()
        if not item:
            continue
        scales.append(float(item))
    if not scales:
        raise argparse.ArgumentTypeError("at least one scale is required")
    return scales


def copy_asset(src, assets_dir, name, label, root):
    dst = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)
    entry = {
        "label": label,
        "asset": dst,
        "repo_path": posix_rel(dst, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dst),
        "sha256": sha256_file(dst),
    }
    dims = image_dimensions(dst)
    if dims:
        entry["dimensions"] = dims
    return entry


def signed_delta_stats(full_img, base_img):
    full = full_img.convert("RGB")
    base = base_img.convert("RGB")
    fp = full.load()
    bp = base.load()
    width, height = full.size
    total_abs = 0
    max_abs = 0
    changed = 0
    count = width * height * 3
    for y in range(height):
        for x in range(width):
            fv = fp[x, y]
            bv = bp[x, y]
            for channel in range(3):
                diff = int(fv[channel]) - int(bv[channel])
                adiff = abs(diff)
                total_abs += adiff
                max_abs = max(max_abs, adiff)
                if adiff:
                    changed += 1
    return {
        "mean_abs_delta": total_abs / float(max(1, count)),
        "max_abs_delta": max_abs,
        "changed_channel_fraction": changed / float(max(1, count)),
    }


def delta_preview(full_img, base_img, sign, gain):
    full = full_img.convert("RGB")
    base = base_img.convert("RGB")
    out = Image.new("RGB", full.size)
    fp = full.load()
    bp = base.load()
    op = out.load()
    scale = max(0.0, float(gain))
    for y in range(full.size[1]):
        for x in range(full.size[0]):
            fv = fp[x, y]
            bv = bp[x, y]
            values = []
            for channel in range(3):
                delta = int(fv[channel]) - int(bv[channel])
                if sign == "negative":
                    delta = -delta
                values.append(max(0, min(255, int(round(max(0, delta) * scale)))))
            op[x, y] = tuple(values)
    return out


def scaled_response(base_img, full_img, scale):
    base = base_img.convert("RGB")
    full = full_img.convert("RGB")
    out = Image.new("RGB", base.size)
    bp = base.load()
    fp = full.load()
    op = out.load()
    for y in range(base.size[1]):
        for x in range(base.size[0]):
            bv = bp[x, y]
            fv = fp[x, y]
            values = []
            for channel in range(3):
                delta = int(fv[channel]) - int(bv[channel])
                values.append(max(0, min(255, int(round(int(bv[channel]) + float(scale) * delta)))))
            op[x, y] = tuple(values)
    return out


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (10, 16, 22))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        strip.paste(panel.convert("RGB"), (x, label_h))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def source_entry(path, root, payload):
    return {
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def aggregate_scale(scale, frames):
    rows = [item for item in frames if item.get("scale") == scale and "gap_mean_abs_diff" in item]
    if not rows:
        return None
    return {
        "scale": scale,
        "frames": len(rows),
        "mean_gap_mean_abs_diff": sum(item["gap_mean_abs_diff"] for item in rows) / len(rows),
        "max_gap_mean_abs_diff": max(item["gap_mean_abs_diff"] for item in rows),
        "max_gap_max_abs_diff": max(item["gap_max_abs_diff"] for item in rows),
    }


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Response Buffer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Response Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks") or {}
    best = (summary.get("scale_sweep") or {}).get("best") or {}
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Mean Delta", f"{checks.get('mean_abs_delta', 0.0):.3f}"),
        ("Max Delta", checks.get("max_abs_delta")),
        ("Best Scale", best.get("scale", "n/a")),
        ("Best Max MAD", f"{best.get('max_gap_mean_abs_diff', 0.0):.3f}" if best else "n/a"),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="response buffer GIF"></section>' if gif else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #111a21; --ink: #edf7fb; --muted: #a2b5bf; --line: #2e3d47; --accent: #9fd9ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111820; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section class="grid">{frame_html}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    sweep = summary.get("scale_sweep") or {}
    best = sweep.get("best") or {}
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
        f"- Full render: `{summary['sources']['full_render']['repo_path']}`",
        f"- Base render: `{summary['sources']['base_render']['repo_path']}`",
        f"- Target: `{(summary['sources'].get('target') or {}).get('repo_path', 'n/a')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Mean abs delta: `{checks.get('mean_abs_delta')}`",
        f"- Max abs delta: `{checks.get('max_abs_delta')}`",
        f"- Changed channel fraction: `{checks.get('changed_channel_fraction')}`",
        f"- Reconstruction max abs diff: `{checks.get('reconstruction_max_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Scale Sweep",
        "",
        f"- Best scale: `{best.get('scale', 'n/a')}`",
        f"- Best mean MAD: `{best.get('mean_gap_mean_abs_diff', 'n/a')}`",
        f"- Best max MAD: `{best.get('max_gap_mean_abs_diff', 'n/a')}`",
        "",
        "| Scale | Mean MAD | Max MAD | Max Abs |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for item in sweep.get("scales") or []:
        lines.append(
            f"| {item.get('scale')} | {item.get('mean_gap_mean_abs_diff')} | "
            f"{item.get('max_gap_mean_abs_diff')} | {item.get('max_gap_max_abs_diff')} |"
        )
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Mean Delta | Max Delta | Strip |",
        "| ---: | ---: | ---: | --- |",
    ])
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('mean_abs_delta')} | "
            f"{frame.get('max_abs_delta')} | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Use the response buffer to drive renderer-native AOV correction.", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    full_path = require_file(args.full_render, "full render manifest")
    base_path = require_file(args.base_render, "base render manifest")
    full = read_json(full_path)
    base = read_json(base_path)
    full_frames = preview_frame_map(full, "full render")
    base_frames = preview_frame_map(base, "base render")
    target = None
    target_frames = {}
    if args.target_summary:
        target_path = require_file(args.target_summary, "target summary")
        target = read_json(target_path)
        target_frames = frame_map_from_sequence(target, "target summary")
    else:
        target_path = None

    out_dir = os.path.abspath(args.out_dir)
    pos_dir = os.path.join(out_dir, "positive_delta")
    neg_dir = os.path.join(out_dir, "negative_delta")
    mag_dir = os.path.join(out_dir, "delta_magnitude")
    scaled_dir = os.path.join(out_dir, "scaled")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (pos_dir, neg_dir, mag_dir, scaled_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    scales = args.scales
    frames = []
    scale_rows = []
    missing = []
    strips = []
    reconstruction_max_abs = 0
    for index, output in enumerate(sorted(set(full_frames) & set(base_frames))):
        full_frame = full_frames[output]
        base_frame = base_frames[output]
        full_img_path = full_frame.get("path")
        base_img_path = base_frame.get("path")
        if not full_img_path or not os.path.isfile(full_img_path) or not base_img_path or not os.path.isfile(base_img_path):
            missing.append({"output_frame": output, "full": full_img_path, "base": base_img_path})
            continue
        full_img = Image.open(full_img_path).convert("RGB")
        base_img = Image.open(base_img_path).convert("RGB")
        if base_img.size != full_img.size:
            base_img = base_img.resize(full_img.size, Image.Resampling.BICUBIC)
        reconstructed = scaled_response(base_img, full_img, 1.0)
        reconstruction_max_abs = max(reconstruction_max_abs, max_abs_diff(reconstructed, full_img))
        stats = signed_delta_stats(full_img, base_img)
        base_name = f"frame_{index:04d}.png"
        pos_path = os.path.join(pos_dir, base_name)
        neg_path = os.path.join(neg_dir, base_name)
        mag_path = os.path.join(mag_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        pos = delta_preview(full_img, base_img, "positive", args.preview_gain)
        neg = delta_preview(full_img, base_img, "negative", args.preview_gain)
        mag = ImageOps.autocontrast(ImageChops.difference(full_img, base_img))
        pos.save(pos_path)
        neg.save(neg_path)
        mag.save(mag_path)

        best_frame_path = None
        target_frame = target_frames.get(output) if target_frames else None
        target_img = None
        if target_frame:
            target_img_path = target_frame.get("path")
            if target_img_path and os.path.isfile(target_img_path):
                target_img = Image.open(target_img_path).convert("RGB")
                if target_img.size != full_img.size:
                    target_img = target_img.resize(full_img.size, Image.Resampling.BICUBIC)
            else:
                missing.append({"output_frame": output, "target": target_img_path})

        for scale in scales:
            scaled = scaled_response(base_img, full_img, scale)
            scaled_frame_dir = os.path.join(scaled_dir, f"scale_{scale:.3f}".replace(".", "p"))
            os.makedirs(scaled_frame_dir, exist_ok=True)
            scaled_path = os.path.join(scaled_frame_dir, base_name)
            scaled.save(scaled_path)
            row = {
                "output_frame": output,
                "scale": scale,
                "scaled_repo_path": posix_rel(scaled_path, root),
                "scaled_sha256": sha256_file(scaled_path),
            }
            if target_img is not None:
                row["gap_mean_abs_diff"] = mean_abs_diff(scaled, target_img)
                row["gap_max_abs_diff"] = max_abs_diff(scaled, target_img)
            scale_rows.append(row)

        if target_img is not None:
            per_frame = [row for row in scale_rows if row.get("output_frame") == output and "gap_mean_abs_diff" in row]
            if per_frame:
                best_row = min(per_frame, key=lambda item: (item["gap_max_abs_diff"], item["gap_mean_abs_diff"]))
                best_frame_path = resolve_path(best_row["scaled_repo_path"])
                best_panel = Image.open(best_frame_path).convert("RGB")
                labeled_strip(
                    [base_img, full_img, best_panel, target_img, pos, neg],
                    ["base", "full", f"scaled {best_row['scale']}", "target", "+delta", "-delta"],
                    strip_path,
                )
        if best_frame_path is None:
            labeled_strip([base_img, full_img, pos, neg, mag], ["base", "full", "+delta", "-delta", "magnitude"], strip_path)

        strips.append(strip_path)
        frames.append({
            "output_frame": output,
            "sequence_frame": full_frame.get("sequence_frame"),
            "full_repo_path": posix_rel(full_img_path, root),
            "base_repo_path": posix_rel(base_img_path, root),
            "positive_delta_repo_path": posix_rel(pos_path, root),
            "negative_delta_repo_path": posix_rel(neg_path, root),
            "delta_magnitude_repo_path": posix_rel(mag_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "mean_abs_delta": stats["mean_abs_delta"],
            "max_abs_delta": stats["max_abs_delta"],
            "changed_channel_fraction": stats["changed_channel_fraction"],
        })

    if not frames:
        raise SystemExit("no comparable full/base frames were generated")

    scale_summaries = [aggregate_scale(scale, scale_rows) for scale in scales]
    scale_summaries = [item for item in scale_summaries if item is not None]
    best = None
    if scale_summaries:
        best = min(scale_summaries, key=lambda item: (item["max_gap_mean_abs_diff"], item["mean_gap_mean_abs_diff"]))

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(strips, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Response Buffer GIF", root)]
    key_indices = sorted(set(round(i * (len(strips) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"response_strip_{out_index:02d}.png", f"Response Strip {out_index + 1}", root))

    sources = {
        "full_render": source_entry(full_path, root, full),
        "base_render": source_entry(base_path, root, base),
    }
    if target:
        sources["target"] = source_entry(target_path, root, target)
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "mean_abs_delta": sum(item["mean_abs_delta"] for item in frames) / len(frames),
        "max_abs_delta": max(item["max_abs_delta"] for item in frames),
        "changed_channel_fraction": sum(item["changed_channel_fraction"] for item in frames) / len(frames),
        "reconstruction_max_abs_diff": reconstruction_max_abs,
        "scale_rows": len(scale_rows),
        "gif_bytes": os.path.getsize(gif_path),
    }
    summary_path = os.path.join(out_dir, "response_delta_buffer_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_response_delta_buffer",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready" if not missing else "review",
        "sources": sources,
        "settings": {
            "preview_gain": args.preview_gain,
            "fps": args.fps,
            "keyframes": args.keyframes,
            "scales": scales,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": frames,
        "scale_sweep": {
            "scales": scale_summaries,
            "best": best,
            "rows": scale_rows,
        },
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [copy_asset(summary_path, assets_dir, "response_delta_buffer_summary.json", "Response summary", root)]
    if target:
        metadata_files.append(copy_asset(target_path, assets_dir, "target_summary.json", "Target summary", root))
    index_path = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, metadata_files[0]["asset"])
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_response_delta_buffer_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={summary['status']} frames={checks['frames']} "
        f"mean_delta={checks['mean_abs_delta']:.6f} max_delta={checks['max_abs_delta']} "
        f"best_scale={(best or {}).get('scale', 'n/a')} out={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a response delta buffer from full/base Mitsuba renders")
    parser.add_argument("full_render")
    parser.add_argument("base_render")
    parser.add_argument("out_dir")
    parser.add_argument("--target-summary")
    parser.add_argument("--scales", type=parse_scales, default=parse_scales("0,0.25,0.5,0.75,1,1.25,1.5"))
    parser.add_argument("--preview-gain", type=float, default=4.0)
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Response Delta Buffer")
    parser.add_argument(
        "--next",
        default="Promote the best response scale into a renderer-native compositing or AOV-controlled render path.",
    )
    args = parser.parse_args(argv)
    if args.preview_gain < 0.0:
        parser.error("preview-gain must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
