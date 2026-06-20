#!/usr/bin/env python
"""Analyze where a proxy Mitsuba response improves over a native render."""

import argparse
import csv
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


REGION_ORDER = (
    "all",
    "response_mask",
    "outside_response_mask",
    "response_alpha",
    "response_luma",
    "target_highlight",
    "target_dark",
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze proxy/native parity")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def aov_path(frame, name):
    entry = ((frame.get("aovs") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


def luma_triplet(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def luma_values(image):
    data = image.convert("RGB").tobytes()
    return [
        luma_triplet(data[index], data[index + 1], data[index + 2])
        for index in range(0, len(data), 3)
    ]


def mask_from_luma(image, size, threshold, mode="ge"):
    if image.size != size:
        image = image.resize(size, Image.Resampling.BICUBIC)
    values = image.convert("L").tobytes()
    if mode == "le":
        return bytearray(1 if value <= threshold else 0 for value in values)
    return bytearray(1 if value >= threshold else 0 for value in values)


def invert_mask(mask):
    return bytearray(0 if value else 1 for value in mask)


def full_mask(size):
    return bytearray([1]) * (size[0] * size[1])


def stats_for_region(name, mask, native_error, proxy_error, proxy_minus_native, target_luma, args):
    pixels = 0
    native_sum = 0.0
    proxy_sum = 0.0
    improvement_sum = 0.0
    positive_pixels = 0
    positive_sum = 0.0
    regression_pixels = 0
    regression_sum = 0.0
    shift_sum = 0.0
    target_sum = 0.0
    max_improvement = 0.0
    max_regression = 0.0
    for index, enabled in enumerate(mask):
        if not enabled:
            continue
        pixels += 1
        native = native_error[index]
        proxy = proxy_error[index]
        improvement = native - proxy
        native_sum += native
        proxy_sum += proxy
        improvement_sum += improvement
        shift_sum += proxy_minus_native[index]
        target_sum += target_luma[index]
        if improvement >= args.improvement_threshold:
            positive_pixels += 1
            positive_sum += improvement
            max_improvement = max(max_improvement, improvement)
        elif improvement <= -args.regression_threshold:
            regression_pixels += 1
            amount = -improvement
            regression_sum += amount
            max_regression = max(max_regression, amount)
    total_pixels = len(mask)
    return {
        "region": name,
        "pixels": pixels,
        "coverage": pixels / float(max(1, total_pixels)),
        "native_error_mean": native_sum / float(max(1, pixels)),
        "proxy_error_mean": proxy_sum / float(max(1, pixels)),
        "mean_improvement": improvement_sum / float(max(1, pixels)),
        "total_improvement": improvement_sum,
        "positive_improvement_pixels": positive_pixels,
        "positive_improvement_coverage": positive_pixels / float(max(1, total_pixels)),
        "positive_improvement_mean": positive_sum / float(max(1, positive_pixels)),
        "max_improvement": max_improvement,
        "regression_pixels": regression_pixels,
        "regression_coverage": regression_pixels / float(max(1, total_pixels)),
        "regression_mean": regression_sum / float(max(1, regression_pixels)),
        "max_regression": max_regression,
        "proxy_minus_native_luma_mean": shift_sum / float(max(1, pixels)),
        "target_luma_mean": target_sum / float(max(1, pixels)),
        "total_pixels": total_pixels,
    }


def aggregate_regions(frame_rows):
    aggregate = {}
    for name in REGION_ORDER:
        rows = [frame["regions"][name] for frame in frame_rows if name in frame.get("regions", {})]
        pixels = sum(row["pixels"] for row in rows)
        total_pixels = sum(row["total_pixels"] for row in rows)
        positive_pixels = sum(row["positive_improvement_pixels"] for row in rows)
        regression_pixels = sum(row["regression_pixels"] for row in rows)
        aggregate[name] = {
            "region": name,
            "pixels": pixels,
            "coverage": pixels / float(max(1, total_pixels)),
            "native_error_mean": sum(row["native_error_mean"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "proxy_error_mean": sum(row["proxy_error_mean"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "mean_improvement": sum(row["mean_improvement"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "total_improvement": sum(row["total_improvement"] for row in rows),
            "positive_improvement_pixels": positive_pixels,
            "positive_improvement_coverage": positive_pixels / float(max(1, total_pixels)),
            "positive_improvement_mean": sum(row["positive_improvement_mean"] * row["positive_improvement_pixels"] for row in rows) / float(max(1, positive_pixels)),
            "max_improvement": max((row["max_improvement"] for row in rows), default=0.0),
            "regression_pixels": regression_pixels,
            "regression_coverage": regression_pixels / float(max(1, total_pixels)),
            "regression_mean": sum(row["regression_mean"] * row["regression_pixels"] for row in rows) / float(max(1, regression_pixels)),
            "max_regression": max((row["max_regression"] for row in rows), default=0.0),
            "proxy_minus_native_luma_mean": sum(row["proxy_minus_native_luma_mean"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "target_luma_mean": sum(row["target_luma_mean"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "total_pixels": total_pixels,
        }
    return aggregate


def improvement_heatmap(improvements, size, scale):
    pixels = bytearray()
    for value in improvements:
        if abs(value) < 0.5:
            pixels.extend((7, 12, 17))
            continue
        t = min(1.0, abs(value) / max(1.0, scale))
        if value > 0.0:
            pixels.extend((int(22 + 84 * t), int(72 + 176 * t), int(44 + 92 * t)))
        else:
            pixels.extend((int(80 + 175 * t), int(38 + 42 * t), int(58 + 42 * t)))
    return Image.frombytes("RGB", size, bytes(pixels))


def mask_panel(masks, size):
    pixels = bytearray()
    response = masks.get("response_mask")
    alpha = masks.get("response_alpha")
    luma = masks.get("response_luma")
    count = size[0] * size[1]
    for index in range(count):
        r = 18
        g = 24
        b = 32
        if response and response[index]:
            b = 220
            g = 150
        if alpha and alpha[index]:
            r = max(r, 95)
            g = max(g, 220)
        if luma and luma[index]:
            r = 240
            g = max(g, 210)
            b = max(b, 80)
        pixels.extend((r, g, b))
    return Image.frombytes("RGB", size, bytes(pixels))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
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


def write_csv(path, frames, aggregate):
    fieldnames = [
        "scope",
        "frame",
        "output_frame",
        "region",
        "pixels",
        "coverage",
        "native_error_mean",
        "proxy_error_mean",
        "mean_improvement",
        "total_improvement",
        "positive_improvement_pixels",
        "positive_improvement_coverage",
        "positive_improvement_mean",
        "max_improvement",
        "regression_pixels",
        "regression_coverage",
        "regression_mean",
        "max_regression",
        "proxy_minus_native_luma_mean",
        "target_luma_mean",
    ]
    rows = []
    for region, item in aggregate.items():
        rows.append({"scope": "aggregate", "frame": "", "output_frame": "", **{key: item.get(key) for key in fieldnames if key not in {"scope", "frame", "output_frame"}}})
    for frame in frames:
        for region, item in frame.get("regions", {}).items():
            row = {"scope": "frame", "frame": frame.get("frame"), "output_frame": frame.get("output_frame")}
            row.update({key: item.get(key) for key in fieldnames if key not in {"scope", "frame", "output_frame"}})
            rows.append(row)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Parity GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Parity Strip")]
    checks = summary.get("checks") or {}
    aggregate = summary.get("aggregate_regions") or {}
    response = aggregate.get("response_mask") or {}
    outside = aggregate.get("outside_response_mask") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("All improvement", f"{(aggregate.get('all') or {}).get('mean_improvement', 0.0):.4f}"),
            ("Response improvement", f"{response.get('mean_improvement', 0.0):.4f}"),
            ("Outside improvement", f"{outside.get('mean_improvement', 0.0):.4f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Parity GIF"></section>' if gif else ""
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


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{summary.get('csv_repo_path')}`",
        f"Gallery: `{summary.get('gallery', {}).get('index_repo_path')}`",
        f"Status: `{summary['status']}`",
        "",
        "## Aggregate Regions",
        "",
        "| Region | Coverage | Native Err | Proxy Err | Mean Improvement | Positive Coverage | Regression Coverage | Proxy-Native Luma |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in REGION_ORDER:
        item = (summary.get("aggregate_regions") or {}).get(name) or {}
        lines.append(
            f"| `{name}` | {item.get('coverage', 0.0):.6f} | {item.get('native_error_mean', 0.0):.6f} | "
            f"{item.get('proxy_error_mean', 0.0):.6f} | {item.get('mean_improvement', 0.0):.6f} | "
            f"{item.get('positive_improvement_coverage', 0.0):.6f} | {item.get('regression_coverage', 0.0):.6f} | "
            f"{item.get('proxy_minus_native_luma_mean', 0.0):.6f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
    ])
    lines.extend(summary.get("interpretation") or [])
    lines.extend(["", "## Next", "", next_text, ""])
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
        entry["status"] = payload.get("status")
    return entry


def path_from_frame(frame, key):
    return resolve_path(frame.get(key))


def analyze(args):
    require_pillow()
    root = os.getcwd()
    proxy_path = require_file(args.proxy_gap_summary, "proxy target-gap summary")
    native_path = require_file(args.native_gap_summary, "native target-gap summary")
    aov_path_arg = require_file(args.aov_summary, "AOV summary")
    proxy = read_json(proxy_path)
    native = read_json(native_path)
    aovs = read_json(aov_path_arg)
    for path, payload in ((proxy_path, proxy), (native_path, native)):
        if payload.get("schema") != "lsfs_mitsuba_renderer_target_gap":
            raise SystemExit(f"{path}: expected lsfs_mitsuba_renderer_target_gap schema")
    if aovs.get("schema") != "lsfs_mitsuba_visual_cache_aov_package":
        raise SystemExit(f"{aov_path_arg}: expected lsfs_mitsuba_visual_cache_aov_package schema")

    proxy_frames = output_frame_map(proxy.get("frames") or [])
    native_frames = output_frame_map(native.get("frames") or [])
    aov_frames = output_frame_map(aovs.get("frames") or [])
    output_frames = sorted(set(proxy_frames) & set(native_frames) & set(aov_frames))
    if not output_frames:
        raise SystemExit("no overlapping output frames")

    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_rows = []
    strip_paths = []
    for frame_index, output_frame in enumerate(output_frames):
        proxy_frame = proxy_frames[output_frame]
        native_frame = native_frames[output_frame]
        aov_frame = aov_frames[output_frame]
        target_path = require_file(path_from_frame(proxy_frame, "target_repo_path"), "target frame")
        proxy_actual_path = require_file(path_from_frame(proxy_frame, "actual_repo_path"), "proxy actual frame")
        native_actual_path = require_file(path_from_frame(native_frame, "actual_repo_path"), "native actual frame")
        target = Image.open(target_path).convert("RGB")
        proxy_actual = Image.open(proxy_actual_path).convert("RGB")
        native_actual = Image.open(native_actual_path).convert("RGB")
        if proxy_actual.size != target.size:
            proxy_actual = proxy_actual.resize(target.size, Image.Resampling.BICUBIC)
        if native_actual.size != target.size:
            native_actual = native_actual.resize(target.size, Image.Resampling.BICUBIC)

        target_luma = luma_values(target)
        proxy_luma = luma_values(proxy_actual)
        native_luma = luma_values(native_actual)
        proxy_error = [abs(t - p) for t, p in zip(target_luma, proxy_luma)]
        native_error = [abs(t - n) for t, n in zip(target_luma, native_luma)]
        improvements = [n - p for n, p in zip(native_error, proxy_error)]
        proxy_minus_native = [p - n for p, n in zip(proxy_luma, native_luma)]

        size = target.size
        response_mask_path = require_file(resolve_path(aov_path(aov_frame, "response_mask")), "response mask")
        response_alpha_path = require_file(resolve_path(aov_path(aov_frame, "response_alpha")), "response alpha")
        response_luma_path = require_file(resolve_path(aov_path(aov_frame, "response_luma")), "response luma")
        target_luma_path = require_file(resolve_path(aov_path(aov_frame, "target_luma")), "target luma")
        masks = {
            "all": full_mask(size),
            "response_mask": mask_from_luma(Image.open(response_mask_path), size, args.mask_threshold),
            "response_alpha": mask_from_luma(Image.open(response_alpha_path), size, args.mask_threshold),
            "response_luma": mask_from_luma(Image.open(response_luma_path), size, args.mask_threshold),
            "target_highlight": mask_from_luma(Image.open(target_luma_path), size, args.target_highlight_luma),
            "target_dark": mask_from_luma(Image.open(target_luma_path), size, args.target_dark_luma, mode="le"),
        }
        masks["outside_response_mask"] = invert_mask(masks["response_mask"])
        regions = {
            name: stats_for_region(name, masks[name], native_error, proxy_error, proxy_minus_native, target_luma, args)
            for name in REGION_ORDER
        }

        strip_path = os.path.join(strip_dir, f"frame_{frame_index:04d}_proxy_native_parity.png")
        labeled_strip(
            [
                target,
                native_actual,
                proxy_actual,
                improvement_heatmap(improvements, size, args.heatmap_scale),
                mask_panel(masks, size),
            ],
            ["Target", "Native", "Proxy", "Improvement (+green/-red)", "AOV Response Masks"],
            strip_path,
        )
        strip_paths.append(strip_path)
        frame_rows.append({
            "frame": proxy_frame.get("frame"),
            "output_frame": output_frame,
            "target_repo_path": posix_rel(target_path, root),
            "proxy_actual_repo_path": posix_rel(proxy_actual_path, root),
            "native_actual_repo_path": posix_rel(native_actual_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "proxy_gap_mean_abs_diff": proxy_frame.get("gap_mean_abs_diff"),
            "native_gap_mean_abs_diff": native_frame.get("gap_mean_abs_diff"),
            "regions": regions,
        })

    aggregate = aggregate_regions(frame_rows)
    csv_path = os.path.join(out_dir, "proxy_native_parity_regions.csv")
    write_csv(csv_path, frame_rows, aggregate)
    gif_path = os.path.join(assets_dir, "proxy_native_parity.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "proxy_native_parity.gif", "Parity GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"proxy_native_parity_{out_index:02d}.png", f"Parity Strip {out_index + 1}", root))

    metadata_files = [
        copy_asset(csv_path, assets_dir, "proxy_native_parity_regions.csv", "Region CSV", root),
        copy_asset(proxy_path, assets_dir, "proxy_gap_summary.json", "Proxy gap summary", root),
        copy_asset(native_path, assets_dir, "native_gap_summary.json", "Native gap summary", root),
        copy_asset(aov_path_arg, assets_dir, "visual_cache_aov_summary.json", "AOV summary", root),
    ]
    response = aggregate["response_mask"]
    outside = aggregate["outside_response_mask"]
    all_region = aggregate["all"]
    interpretation = [
        (
            f"Proxy mean improvement over native is `{all_region['mean_improvement']:.6f}` "
            f"luma over all pixels."
        ),
        (
            f"Inside response_mask the mean improvement is `{response['mean_improvement']:.6f}` "
            f"at coverage `{response['coverage']:.6f}`."
        ),
        (
            f"Outside response_mask the mean improvement is `{outside['mean_improvement']:.6f}` "
            f"at coverage `{outside['coverage']:.6f}`."
        ),
    ]
    if abs(outside["total_improvement"]) > abs(response["total_improvement"]):
        interpretation.append("Most total improvement is outside the sparse response mask; this points toward low-frequency tone/texture parity, not another tiny localized glint.")
    else:
        interpretation.append("Most total improvement is concentrated inside the sparse response mask; this supports a tighter localized response representation.")

    generated_utc = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "proxy_native_parity_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_proxy_native_parity_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "sources": {
            "proxy_gap_summary": source_entry(proxy_path, root, "proxy target-gap summary", proxy),
            "native_gap_summary": source_entry(native_path, root, "native target-gap summary", native),
            "aov_summary": source_entry(aov_path_arg, root, "AOV summary", aovs),
        },
        "settings": {
            "mask_threshold": args.mask_threshold,
            "improvement_threshold": args.improvement_threshold,
            "regression_threshold": args.regression_threshold,
            "target_highlight_luma": args.target_highlight_luma,
            "target_dark_luma": args.target_dark_luma,
            "heatmap_scale": args.heatmap_scale,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_rows),
            "gif_bytes": os.path.getsize(gif_path),
            "csv_bytes": os.path.getsize(csv_path),
            "all_mean_improvement": all_region["mean_improvement"],
            "response_mask_mean_improvement": response["mean_improvement"],
            "outside_response_mask_mean_improvement": outside["mean_improvement"],
        },
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "aggregate_regions": aggregate,
        "frames": frame_rows,
        "interpretation": interpretation,
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
        "schema": "lsfs_mitsuba_proxy_native_parity_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "summary_repo_path": posix_rel(summary_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(frame_rows)} all_improvement={all_region['mean_improvement']:.6f} "
        f"response_improvement={response['mean_improvement']:.6f} outside_improvement={outside['mean_improvement']:.6f} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze proxy/native Mitsuba target-gap parity by AOV region")
    parser.add_argument("proxy_gap_summary")
    parser.add_argument("native_gap_summary")
    parser.add_argument("aov_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--improvement-threshold", type=float, default=2.0)
    parser.add_argument("--regression-threshold", type=float, default=2.0)
    parser.add_argument("--target-highlight-luma", type=float, default=150.0)
    parser.add_argument("--target-dark-luma", type=float, default=55.0)
    parser.add_argument("--heatmap-scale", type=float, default=24.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S486 Mitsuba Proxy Native Parity Analysis")
    parser.add_argument("--next", default="Use this parity analysis to choose the next renderer-native representation.")
    args = parser.parse_args(argv)
    if not (0 <= args.mask_threshold <= 255):
        parser.error("mask-threshold must be in [0, 255]")
    if args.improvement_threshold < 0.0 or args.regression_threshold < 0.0:
        parser.error("improvement/regression thresholds must be non-negative")
    if not (0.0 <= args.target_highlight_luma <= 255.0):
        parser.error("target-highlight-luma must be in [0, 255]")
    if not (0.0 <= args.target_dark_luma <= 255.0):
        parser.error("target-dark-luma must be in [0, 255]")
    if args.heatmap_scale <= 0.0:
        parser.error("heatmap-scale must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    analyze(args)


if __name__ == "__main__":
    main()
