#!/usr/bin/env python
"""Apply a bounded low-frequency proxy/native parity correction to native frames."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageFilter = None
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to apply low-frequency parity")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def clamp_int(value, lo=0, hi=255):
    return max(lo, min(hi, int(round(value))))


def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def encode_delta(proxy, native, max_delta):
    proxy_bytes = proxy.convert("RGB").tobytes()
    native_bytes = native.convert("RGB").tobytes()
    encoded = bytearray(len(proxy_bytes))
    max_delta = float(max_delta)
    for index, (p, n) in enumerate(zip(proxy_bytes, native_bytes)):
        delta = max(-max_delta, min(max_delta, float(p) - float(n)))
        encoded[index] = clamp_int(128.0 + delta)
    return Image.frombytes("RGB", proxy.size, bytes(encoded))


def apply_delta(native, target, delta_image, args):
    native_bytes = native.convert("RGB").tobytes()
    target_bytes = target.convert("RGB").tobytes()
    delta_bytes = delta_image.convert("RGB").tobytes()
    out = bytearray(len(native_bytes))
    layer = bytearray(len(native_bytes) // 3)
    for pix, index in enumerate(range(0, len(native_bytes), 3)):
        target_luma = luma(target_bytes[index], target_bytes[index + 1], target_bytes[index + 2])
        damping = args.dark_damping if target_luma <= args.target_dark_luma else 1.0
        local_gain = args.gain * damping
        max_abs = 0.0
        for channel in range(3):
            delta = (float(delta_bytes[index + channel]) - 128.0) * local_gain
            max_abs = max(max_abs, abs(delta))
            out[index + channel] = clamp_int(float(native_bytes[index + channel]) + delta)
        layer[pix] = clamp_int(max_abs * args.layer_gain)
    return Image.frombytes("RGB", native.size, bytes(out)), Image.frombytes("L", native.size, bytes(layer))


def mean_abs_diff(a, b):
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    hist = diff.histogram()
    total = 0
    count = 0
    for channel in range(3):
        offset = channel * 256
        for value in range(256):
            samples = hist[offset + value]
            total += value * samples
            count += samples
    return total / float(max(1, count))


def max_abs_diff(a, b):
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return max(channel[1] for channel in diff.getextrema())


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), fill=(230, 242, 248), text=labels[index])
        strip.paste(panel.convert("RGB"), (x, label_h))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    item = {
        "label": label,
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        item["dimensions"] = dims
    return item


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Low Frequency Parity GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Parity Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Mean target MAD", f"{checks.get('mean_target_mean_abs_diff', 0.0):.4f}"),
            ("Max target MAD", f"{checks.get('max_target_mean_abs_diff', 0.0):.4f}"),
            ("Max target diff", checks.get("max_target_max_abs_diff")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Low-frequency parity GIF"></section>' if gif else ""
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
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #eaf5fb; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; width: 100%; min-width: 960px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
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
    return entry


def markdown_report(summary, summary_path, root):
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
    ]
    for key, value in (summary.get("settings") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend([
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Mean target MAD: `{checks.get('mean_target_mean_abs_diff')}`",
        f"- Max target MAD: `{checks.get('max_target_mean_abs_diff')}`",
        f"- Max target diff: `{checks.get('max_target_max_abs_diff')}`",
        f"- Mean proxy parity MAD: `{checks.get('mean_proxy_mean_abs_diff')}`",
        f"- Max proxy parity MAD: `{checks.get('max_proxy_mean_abs_diff')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Target MAD | Proxy MAD | Layer Max | Composite | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ])
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('target_mean_abs_diff')} | {frame.get('proxy_mean_abs_diff')} | "
            f"{frame.get('layer_max')} | `{frame.get('composite_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    native_path = require_file(args.native_gap_summary, "native target-gap summary")
    proxy_path = require_file(args.proxy_gap_summary, "proxy target-gap summary")
    native = read_json(native_path)
    proxy = read_json(proxy_path)
    for path, payload in ((native_path, native), (proxy_path, proxy)):
        if payload.get("schema") != "lsfs_mitsuba_renderer_target_gap":
            raise SystemExit(f"{path}: expected lsfs_mitsuba_renderer_target_gap schema")

    native_frames = output_frame_map(native.get("frames") or [])
    proxy_frames = output_frame_map(proxy.get("frames") or [])
    output_frames = sorted(set(native_frames) & set(proxy_frames))
    if not output_frames:
        raise SystemExit("no overlapping output frames")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    layer_dir = os.path.join(out_dir, "layers")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (composite_dir, layer_dir, strip_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    frames = []
    strip_paths = []
    target_mads = []
    proxy_mads = []
    target_max_diffs = []
    proxy_max_diffs = []
    for frame_index, output_frame in enumerate(output_frames):
        native_frame = native_frames[output_frame]
        proxy_frame = proxy_frames[output_frame]
        target_path = require_file(resolve_path(native_frame.get("target_repo_path")), "target frame")
        native_actual_path = require_file(resolve_path(native_frame.get("actual_repo_path")), "native frame")
        proxy_actual_path = require_file(resolve_path(proxy_frame.get("actual_repo_path")), "proxy frame")
        target = Image.open(target_path).convert("RGB")
        native_actual = Image.open(native_actual_path).convert("RGB")
        proxy_actual = Image.open(proxy_actual_path).convert("RGB")
        if native_actual.size != target.size:
            native_actual = native_actual.resize(target.size, Image.Resampling.BICUBIC)
        if proxy_actual.size != target.size:
            proxy_actual = proxy_actual.resize(target.size, Image.Resampling.BICUBIC)

        encoded_delta = encode_delta(proxy_actual, native_actual, args.max_delta)
        low_delta = encoded_delta.filter(ImageFilter.GaussianBlur(radius=args.blur_radius))
        composite, layer = apply_delta(native_actual, target, low_delta, args)
        composite_path = os.path.join(composite_dir, f"frame_{frame_index:04d}.png")
        layer_path = os.path.join(layer_dir, f"frame_{frame_index:04d}_parity_layer.png")
        strip_path = os.path.join(strip_dir, f"frame_{frame_index:04d}_low_frequency_parity.png")
        composite.save(composite_path)
        layer.save(layer_path)
        layer_rgb = ImageOps.colorize(layer, black=(6, 12, 18), white=(96, 220, 255))
        labeled_strip(
            [target, native_actual, proxy_actual, composite, layer_rgb],
            ["Target", "Native", "Proxy", "Low-Frequency Parity", "Correction Layer"],
            strip_path,
        )
        strip_paths.append(strip_path)
        target_mad = mean_abs_diff(composite, target)
        proxy_mad = mean_abs_diff(composite, proxy_actual)
        target_max = max_abs_diff(composite, target)
        proxy_max = max_abs_diff(composite, proxy_actual)
        target_mads.append(target_mad)
        proxy_mads.append(proxy_mad)
        target_max_diffs.append(target_max)
        proxy_max_diffs.append(proxy_max)
        frames.append({
            "frame": native_frame.get("frame"),
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_path, root),
            "native_repo_path": posix_rel(native_actual_path, root),
            "proxy_repo_path": posix_rel(proxy_actual_path, root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "layer_path": layer_path,
            "layer_repo_path": posix_rel(layer_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "target_mean_abs_diff": target_mad,
            "target_max_abs_diff": target_max,
            "proxy_mean_abs_diff": proxy_mad,
            "proxy_max_abs_diff": proxy_max,
            "layer_max": max(layer.getextrema()),
        })

    gif_path = os.path.join(assets_dir, "low_frequency_parity.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "low_frequency_parity.gif", "Low Frequency Parity GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"low_frequency_parity_{out_index:02d}.png", f"Parity Strip {out_index + 1}", root))
    metadata_files = [
        copy_asset(native_path, assets_dir, "native_gap_summary.json", "Native gap summary", root),
        copy_asset(proxy_path, assets_dir, "proxy_gap_summary.json", "Proxy gap summary", root),
    ]
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "low_frequency_parity_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_low_frequency_parity",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "sources": {
            "native_gap_summary": source_entry(native_path, root, "native target-gap summary", native),
            "proxy_gap_summary": source_entry(proxy_path, root, "proxy target-gap summary", proxy),
        },
        "settings": {
            "gain": args.gain,
            "blur_radius": args.blur_radius,
            "max_delta": args.max_delta,
            "target_dark_luma": args.target_dark_luma,
            "dark_damping": args.dark_damping,
            "layer_gain": args.layer_gain,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frames),
            "mean_target_mean_abs_diff": sum(target_mads) / float(max(1, len(target_mads))),
            "max_target_mean_abs_diff": max(target_mads),
            "max_target_max_abs_diff": max(target_max_diffs),
            "mean_proxy_mean_abs_diff": sum(proxy_mads) / float(max(1, len(proxy_mads))),
            "max_proxy_mean_abs_diff": max(proxy_mads),
            "max_proxy_max_abs_diff": max(proxy_max_diffs),
            "composite_bytes": sum(frame.get("size", 0) for frame in frames),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": index_path,
            "index_repo_path": posix_rel(index_path, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_parity_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "summary_repo_path": posix_rel(summary_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status=ready frames={len(frames)} mean_target_mad={summary['checks']['mean_target_mean_abs_diff']:.6f} "
        f"max_target_mad={summary['checks']['max_target_mean_abs_diff']:.6f} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply a bounded low-frequency proxy/native parity correction")
    parser.add_argument("native_gap_summary")
    parser.add_argument("proxy_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--gain", type=float, default=0.65)
    parser.add_argument("--blur-radius", type=float, default=10.0)
    parser.add_argument("--max-delta", type=float, default=36.0)
    parser.add_argument("--target-dark-luma", type=float, default=55.0)
    parser.add_argument("--dark-damping", type=float, default=0.25)
    parser.add_argument("--layer-gain", type=float, default=5.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S487 Mitsuba Low Frequency Parity")
    parser.add_argument("--next", default="Compare this parity preview against target and decide whether to port it into a renderer-native texture/tone representation.")
    args = parser.parse_args(argv)
    if args.gain < 0.0:
        parser.error("gain must be non-negative")
    if args.blur_radius < 0.0:
        parser.error("blur-radius must be non-negative")
    if args.max_delta <= 0.0 or args.max_delta > 127.0:
        parser.error("max-delta must be in (0, 127]")
    if not (0.0 <= args.target_dark_luma <= 255.0):
        parser.error("target-dark-luma must be in [0, 255]")
    if not (0.0 <= args.dark_damping <= 1.0):
        parser.error("dark-damping must be in [0, 1]")
    if args.layer_gain <= 0.0:
        parser.error("layer-gain must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    build(args)


if __name__ == "__main__":
    main()
