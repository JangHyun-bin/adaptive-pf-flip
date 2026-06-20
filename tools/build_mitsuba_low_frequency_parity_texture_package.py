#!/usr/bin/env python
"""Build renderer-consumable textures for low-frequency parity correction."""

import argparse
import csv
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps, ImageStat
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageFilter = None
    ImageOps = None
    ImageStat = None

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


TEXTURE_NAMES = [
    "base_rgb",
    "target_rgb",
    "proxy_rgb",
    "parity_composite_rgb",
    "raw_low_frequency_delta_rgb",
    "applied_positive_delta_rgb",
    "applied_negative_delta_rgb",
    "applied_signed_offset_rgb",
    "applied_magnitude_luma",
    "applied_mask_luma",
    "dark_damping_mask_luma",
    "dark_damping_weight_luma",
]


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build low-frequency parity texture packages")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def clamp_int(value, lo=0, hi=255):
    return max(lo, min(hi, int(round(value))))


def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def save_image(image, path, root):
    ensure_dir(os.path.dirname(path))
    image.save(path)
    return {
        "path": os.path.abspath(path),
        "repo_path": posix_rel(os.path.abspath(path), root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
        "dimensions": image_dimensions(path),
    }


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    ensure_dir(os.path.dirname(dest))
    if os.path.abspath(src) != os.path.abspath(dest):
        with open(src, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def encode_raw_low_frequency_delta(proxy, native, max_delta, blur_radius):
    proxy_bytes = proxy.convert("RGB").tobytes()
    native_bytes = native.convert("RGB").tobytes()
    encoded = bytearray(len(proxy_bytes))
    max_delta = float(max_delta)
    for index, (proxy_byte, native_byte) in enumerate(zip(proxy_bytes, native_bytes)):
        delta = max(-max_delta, min(max_delta, float(proxy_byte) - float(native_byte)))
        encoded[index] = clamp_int(128.0 + delta)
    return Image.frombytes("RGB", proxy.size, bytes(encoded)).filter(ImageFilter.GaussianBlur(radius=blur_radius))


def dark_damping_maps(target, target_dark_luma, dark_damping):
    target_bytes = target.convert("RGB").tobytes()
    mask = bytearray(len(target_bytes) // 3)
    weight = bytearray(len(target_bytes) // 3)
    dark_byte = clamp_int(float(dark_damping) * 255.0)
    for pix, index in enumerate(range(0, len(target_bytes), 3)):
        is_dark = luma(target_bytes[index], target_bytes[index + 1], target_bytes[index + 2]) <= target_dark_luma
        mask[pix] = 255 if is_dark else 0
        weight[pix] = dark_byte if is_dark else 255
    return Image.frombytes("L", target.size, bytes(mask)), Image.frombytes("L", target.size, bytes(weight))


def applied_delta_textures(base, composite):
    base_bytes = base.convert("RGB").tobytes()
    comp_bytes = composite.convert("RGB").tobytes()
    positive = bytearray(len(base_bytes))
    negative = bytearray(len(base_bytes))
    signed = bytearray(len(base_bytes))
    magnitude = bytearray(len(base_bytes) // 3)
    mask = bytearray(len(base_bytes) // 3)
    signed_clipped = 0
    total_abs = 0
    max_abs = 0
    changed_pixels = 0
    for pix, index in enumerate(range(0, len(base_bytes), 3)):
        pixel_max = 0
        for channel in range(3):
            delta = int(comp_bytes[index + channel]) - int(base_bytes[index + channel])
            if delta > 0:
                positive[index + channel] = min(255, delta)
            elif delta < 0:
                negative[index + channel] = min(255, -delta)
            if delta < -127 or delta > 127:
                signed_clipped += 1
            signed[index + channel] = clamp_int(128 + max(-127, min(127, delta)))
            abs_delta = abs(delta)
            total_abs += abs_delta
            pixel_max = max(pixel_max, abs_delta)
            max_abs = max(max_abs, abs_delta)
        magnitude[pix] = min(255, pixel_max)
        if pixel_max:
            mask[pix] = 255
            changed_pixels += 1
    pixels = max(1, len(mask))
    return {
        "positive": Image.frombytes("RGB", base.size, bytes(positive)),
        "negative": Image.frombytes("RGB", base.size, bytes(negative)),
        "signed": Image.frombytes("RGB", base.size, bytes(signed)),
        "magnitude": Image.frombytes("L", base.size, bytes(magnitude)),
        "mask": Image.frombytes("L", base.size, bytes(mask)),
        "stats": {
            "changed_pixels": changed_pixels,
            "changed_coverage": changed_pixels / float(pixels),
            "max_abs_delta": max_abs,
            "mean_abs_delta": total_abs / float(max(1, len(base_bytes))),
            "signed_offset_clipped_channels": signed_clipped,
        },
    }


def reconstruct(base, positive, negative):
    base_bytes = base.convert("RGB").tobytes()
    pos_bytes = positive.convert("RGB").tobytes()
    neg_bytes = negative.convert("RGB").tobytes()
    out = bytearray(len(base_bytes))
    for index in range(len(base_bytes)):
        out[index] = clamp_int(int(base_bytes[index]) + int(pos_bytes[index]) - int(neg_bytes[index]))
    return Image.frombytes("RGB", base.size, bytes(out))


def diff_stats(actual_img, expected_img):
    actual = actual_img.convert("RGB").tobytes()
    expected = expected_img.convert("RGB").tobytes()
    if len(actual) != len(expected):
        raise ValueError("image byte sizes differ")
    total_abs = 0
    max_abs = 0
    mismatched_pixels = 0
    diff_bytes = bytearray()
    for index in range(0, len(actual), 3):
        dr = abs(actual[index] - expected[index])
        dg = abs(actual[index + 1] - expected[index + 1])
        db = abs(actual[index + 2] - expected[index + 2])
        pixel_max = max(dr, dg, db)
        if pixel_max:
            mismatched_pixels += 1
        total_abs += dr + dg + db
        max_abs = max(max_abs, pixel_max)
        diff_bytes.extend((min(255, dr * 8), min(255, dg * 8), min(255, db * 8)))
    pixels = max(1, len(actual) // 3)
    return {
        "mean_abs_diff": total_abs / float(max(1, len(actual))),
        "max_abs_diff": max_abs,
        "mismatched_pixels": mismatched_pixels,
        "mismatched_coverage": mismatched_pixels / float(pixels),
        "diff_image": Image.frombytes("RGB", actual_img.size, bytes(diff_bytes)),
    }


def gray_stats(gray):
    stat = ImageStat.Stat(gray.convert("L"))
    pixels = max(1, gray.size[0] * gray.size[1])
    nonzero = sum(count for value, count in enumerate(gray.histogram()) if value)
    return {
        "mean": float(stat.mean[0]),
        "max": int(stat.extrema[0][1]),
        "nonzero_coverage": nonzero / float(pixels),
    }


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
    ensure_dir(os.path.dirname(out_path))
    strip.save(out_path)
    return strip


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        ensure_dir(os.path.dirname(gif_path))
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def write_csv_file(path, rows):
    ensure_dir(os.path.dirname(path))
    fields = [
        "frame",
        "output_frame",
        "changed_coverage",
        "max_abs_delta",
        "mean_abs_delta",
        "signed_offset_clipped_channels",
        "dark_damping_coverage",
        "reconstruction_mean_abs_diff",
        "reconstruction_max_abs_diff",
        "reconstruction_mismatched_coverage",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Texture Package GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Texture Package Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Textures", checks.get("textures_per_frame")),
            ("Max delta", checks.get("max_abs_delta")),
            ("Max diff", checks.get("max_reconstruction_abs_diff")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Texture package GIF"></section>' if gif else ""
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
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #eaf5fb; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
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


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
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
        f"- Textures per frame: `{checks.get('textures_per_frame')}`",
        f"- Max applied delta: `{checks.get('max_abs_delta')}`",
        f"- Max signed-offset clipped channels: `{checks.get('max_signed_offset_clipped_channels')}`",
        f"- Max dark damping coverage: `{checks.get('max_dark_damping_coverage')}`",
        f"- Max reconstruction abs diff: `{checks.get('max_reconstruction_abs_diff')}`",
        f"- Max reconstruction mean diff: `{checks.get('max_reconstruction_mean_abs_diff')}`",
        f"- Texture bytes: `{format_bytes(checks.get('texture_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Textures",
        "",
    ]
    for name in summary.get("textures") or []:
        lines.append(f"- `{name}`")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Coverage | Max Delta | Recon Max Diff | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        stats = frame.get("stats") or {}
        recon = frame.get("reconstruction") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {stats.get('changed_coverage')} | "
            f"{stats.get('max_abs_delta')} | {recon.get('max_abs_diff')} | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


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
        entry["subschema"] = payload.get("subschema")
        entry["status"] = payload.get("status")
    return entry


def build(args):
    require_pillow()
    root = os.getcwd()
    parity_path = require_file(args.low_frequency_summary, "low-frequency parity summary")
    parity = read_json(parity_path)
    if parity.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.low_frequency_summary}: expected lsfs_mitsuba_secondary_composite schema")
    if parity.get("subschema") != "lsfs_mitsuba_low_frequency_parity":
        raise SystemExit(f"{args.low_frequency_summary}: expected lsfs_mitsuba_low_frequency_parity subschema")

    settings = parity.get("settings") or {}
    max_delta = float(settings.get("max_delta", args.max_delta))
    blur_radius = float(settings.get("blur_radius", args.blur_radius))
    target_dark_luma = float(settings.get("target_dark_luma", args.target_dark_luma))
    dark_damping = float(settings.get("dark_damping", args.dark_damping))

    out_dir = os.path.abspath(args.out_dir)
    texture_dir = ensure_dir(os.path.join(out_dir, "textures"))
    reconstructed_dir = ensure_dir(os.path.join(out_dir, "reconstructed"))
    strip_dir = ensure_dir(os.path.join(out_dir, "strips"))
    gallery_dir = ensure_dir(os.path.join(out_dir, "gallery"))
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))

    frame_records = []
    csv_rows = []
    strip_paths = []
    missing = []
    for index, frame in enumerate(parity.get("frames") or []):
        paths = {
            "base_rgb": resolve_path(frame.get("native_repo_path"), root),
            "target_rgb": resolve_path(frame.get("target_repo_path"), root),
            "proxy_rgb": resolve_path(frame.get("proxy_repo_path"), root),
            "parity_composite_rgb": resolve_path(frame.get("composite_repo_path"), root),
        }
        absent = [role for role, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue

        base = Image.open(paths["base_rgb"]).convert("RGB")
        target = Image.open(paths["target_rgb"]).convert("RGB")
        proxy = Image.open(paths["proxy_rgb"]).convert("RGB")
        composite = Image.open(paths["parity_composite_rgb"]).convert("RGB")
        if any(img.size != base.size for img in (target, proxy, composite)):
            raise SystemExit(f"frame {index}: source dimensions differ")

        raw_delta = encode_raw_low_frequency_delta(proxy, base, max_delta, blur_radius)
        dark_mask, dark_weight = dark_damping_maps(target, target_dark_luma, dark_damping)
        delta = applied_delta_textures(base, composite)
        reconstructed = reconstruct(base, delta["positive"], delta["negative"])
        recon_stats = diff_stats(reconstructed, composite)

        texture_images = {
            "base_rgb": base,
            "target_rgb": target,
            "proxy_rgb": proxy,
            "parity_composite_rgb": composite,
            "raw_low_frequency_delta_rgb": raw_delta,
            "applied_positive_delta_rgb": delta["positive"],
            "applied_negative_delta_rgb": delta["negative"],
            "applied_signed_offset_rgb": delta["signed"],
            "applied_magnitude_luma": delta["magnitude"],
            "applied_mask_luma": delta["mask"],
            "dark_damping_mask_luma": dark_mask,
            "dark_damping_weight_luma": dark_weight,
        }
        textures = {}
        for name in TEXTURE_NAMES:
            texture_path = os.path.join(texture_dir, name, f"frame_{index:04d}_{name}.png")
            textures[name] = save_image(texture_images[name], texture_path, root)

        reconstructed_path = os.path.join(reconstructed_dir, f"frame_{index:04d}.png")
        save_image(reconstructed, reconstructed_path, root)
        raw_visual = ImageChops.subtract(raw_delta.convert("RGB"), Image.new("RGB", raw_delta.size, (128, 128, 128)))
        raw_visual = ImageOps.colorize(raw_visual.convert("L"), black=(6, 12, 18), white=(120, 224, 255))
        magnitude_visual = ImageOps.colorize(delta["magnitude"], black=(6, 12, 18), white=(255, 218, 120))
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_texture_package.png")
        labeled_strip(
            [target, base, proxy, composite, reconstructed, raw_visual, magnitude_visual, recon_stats["diff_image"]],
            ["target", "base", "proxy", "parity", "reconstruct", "raw low-freq", "applied mag", "recon diff x8"],
            strip_path,
        )
        strip_paths.append(strip_path)

        dark_stats = gray_stats(dark_mask)
        stats = dict(delta["stats"])
        record = {
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "textures": textures,
            "reconstructed_path": reconstructed_path,
            "reconstructed_repo_path": posix_rel(reconstructed_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "source_target_mad": frame.get("target_mean_abs_diff"),
            "source_target_max_abs_diff": frame.get("target_max_abs_diff"),
            "stats": stats,
            "dark_damping": {
                "coverage": dark_stats["nonzero_coverage"],
                "weight_dark_byte": clamp_int(dark_damping * 255.0),
                "target_dark_luma": target_dark_luma,
                "dark_damping": dark_damping,
            },
            "reconstruction": {
                "mean_abs_diff": recon_stats["mean_abs_diff"],
                "max_abs_diff": recon_stats["max_abs_diff"],
                "mismatched_pixels": recon_stats["mismatched_pixels"],
                "mismatched_coverage": recon_stats["mismatched_coverage"],
            },
        }
        frame_records.append(record)
        csv_rows.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "changed_coverage": stats["changed_coverage"],
            "max_abs_delta": stats["max_abs_delta"],
            "mean_abs_delta": stats["mean_abs_delta"],
            "signed_offset_clipped_channels": stats["signed_offset_clipped_channels"],
            "dark_damping_coverage": dark_stats["nonzero_coverage"],
            "reconstruction_mean_abs_diff": recon_stats["mean_abs_diff"],
            "reconstruction_max_abs_diff": recon_stats["max_abs_diff"],
            "reconstruction_mismatched_coverage": recon_stats["mismatched_coverage"],
        })

    if not frame_records:
        raise SystemExit("no low-frequency parity texture frames were built")

    csv_path = os.path.abspath(args.csv or os.path.join(out_dir, "low_frequency_parity_texture_stats.csv"))
    write_csv_file(csv_path, csv_rows)
    gif_path = os.path.join(out_dir, "low_frequency_parity_texture_package.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "low_frequency_parity_texture_package.gif", "Texture Package GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"texture_package_strip_{out_index:02d}.png", f"Texture Package Strip {out_index + 1}", root))
    metadata_files = [
        copy_asset(parity_path, assets_dir, "low_frequency_parity_summary.json", "Low-frequency parity summary", root),
        copy_asset(csv_path, assets_dir, "low_frequency_parity_texture_stats.csv", "Texture stats CSV", root),
    ]

    texture_bytes = sum(
        texture.get("size", 0)
        for frame in frame_records
        for texture in (frame.get("textures") or {}).values()
    )
    checks = {
        "frames": len(frame_records),
        "textures_per_frame": len(TEXTURE_NAMES),
        "missing_references": len(missing),
        "max_abs_delta": max((frame["stats"]["max_abs_delta"] for frame in frame_records), default=0),
        "max_mean_abs_delta": max((frame["stats"]["mean_abs_delta"] for frame in frame_records), default=0.0),
        "max_changed_coverage": max((frame["stats"]["changed_coverage"] for frame in frame_records), default=0.0),
        "max_signed_offset_clipped_channels": max((frame["stats"]["signed_offset_clipped_channels"] for frame in frame_records), default=0),
        "max_dark_damping_coverage": max((frame["dark_damping"]["coverage"] for frame in frame_records), default=0.0),
        "max_reconstruction_abs_diff": max((frame["reconstruction"]["max_abs_diff"] for frame in frame_records), default=0),
        "max_reconstruction_mean_abs_diff": max((frame["reconstruction"]["mean_abs_diff"] for frame in frame_records), default=0.0),
        "max_reconstruction_mismatched_coverage": max((frame["reconstruction"]["mismatched_coverage"] for frame in frame_records), default=0.0),
        "texture_bytes": texture_bytes,
        "gif_bytes": os.path.getsize(gif_path),
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
    status = "ready"
    if missing:
        status = "failed"
    if checks["max_reconstruction_abs_diff"] > args.max_abs_tolerance:
        status = "failed"
    if checks["max_reconstruction_mean_abs_diff"] > args.mean_abs_tolerance:
        status = "failed"

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_low_frequency_parity_texture_package",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "low_frequency_parity_summary": source_entry(parity_path, root, "low-frequency parity summary", parity),
        "settings": {
            "max_delta": max_delta,
            "blur_radius": blur_radius,
            "target_dark_luma": target_dark_luma,
            "dark_damping": dark_damping,
            "source_gain": settings.get("gain"),
            "source_layer_gain": settings.get("layer_gain"),
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "textures": TEXTURE_NAMES,
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "checks": checks,
        "frames": frame_records,
        "missing_references": missing,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "low_frequency_parity_texture_package_summary.json", "Texture package summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_parity_texture_package_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} textures={checks['textures_per_frame']} "
        f"max_delta={checks['max_abs_delta']} max_recon={checks['max_reconstruction_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Mitsuba low-frequency parity texture package")
    parser.add_argument("low_frequency_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--csv")
    parser.add_argument("--report")
    parser.add_argument("--max-delta", type=float, default=48.0)
    parser.add_argument("--blur-radius", type=float, default=6.0)
    parser.add_argument("--target-dark-luma", type=float, default=55.0)
    parser.add_argument("--dark-damping", type=float, default=0.35)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="S489 Mitsuba Low Frequency Parity Texture Package")
    parser.add_argument(
        "--next",
        default="Consume this package through a native post-tonemap texture stage, then compare against S478, S487 LF3, and S485 LRS4 target-gap gates.",
    )
    args = parser.parse_args(argv)
    if args.max_delta <= 0.0 or args.max_delta > 127.0:
        parser.error("max-delta must be in (0, 127]")
    if args.blur_radius < 0.0:
        parser.error("blur-radius must be non-negative")
    if not (0.0 <= args.target_dark_luma <= 255.0):
        parser.error("target-dark-luma must be in [0, 255]")
    if not (0.0 <= args.dark_damping <= 1.0):
        parser.error("dark-damping must be in [0, 1]")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    build(args)


if __name__ == "__main__":
    main()
