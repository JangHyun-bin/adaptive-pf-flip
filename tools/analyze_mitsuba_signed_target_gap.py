#!/usr/bin/env python
"""Analyze signed target gaps for frame-aware Mitsuba response calibration."""

import argparse
import math
import os
import shutil
from collections import deque
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze signed target gaps")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def luma_from_rgb(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def mask_layer_ref(frame):
    if not frame:
        return None
    return frame.get("layer_path") or frame.get("layer_repo_path")


def parse_mask_source(value):
    if "=" in value:
        name, path = value.split("=", 1)
        name = name.strip()
        if not name:
            raise argparse.ArgumentTypeError("mask-source name cannot be empty")
        return name, path.strip()
    path = value.strip()
    name = os.path.splitext(os.path.basename(path))[0] or "mask"
    return name, path


def signed_luma_deltas(actual, target):
    actual_bytes = actual.convert("RGB").tobytes()
    target_bytes = target.convert("RGB").tobytes()
    deltas = []
    for index in range(0, len(actual_bytes), 3):
        actual_luma = luma_from_rgb(actual_bytes[index], actual_bytes[index + 1], actual_bytes[index + 2])
        target_luma = luma_from_rgb(target_bytes[index], target_bytes[index + 1], target_bytes[index + 2])
        deltas.append(target_luma - actual_luma)
    return deltas


def mask_bytes(mask_image, size, threshold):
    if mask_image is None:
        return None
    if mask_image.size != size:
        mask_image = mask_image.resize(size, Image.Resampling.BICUBIC)
    if mask_image.mode == "RGBA":
        alpha = mask_image.split()[3]
        return bytes(1 if value >= threshold else 0 for value in alpha.tobytes())
    return bytes(1 if value >= threshold else 0 for value in mask_image.convert("L").tobytes())


def region_stats(name, deltas, mask, total_pixels, args):
    pixels = 0
    abs_sum = 0.0
    signed_sum = 0.0
    positive_pixels = 0
    positive_sum = 0.0
    negative_pixels = 0
    negative_sum = 0.0
    max_positive = 0.0
    max_negative_abs = 0.0
    for index, delta in enumerate(deltas):
        if mask is not None and not mask[index]:
            continue
        pixels += 1
        abs_delta = abs(delta)
        abs_sum += abs_delta
        signed_sum += delta
        if delta >= args.positive_threshold:
            positive_pixels += 1
            positive_sum += delta
            max_positive = max(max_positive, delta)
        elif delta <= -args.negative_threshold:
            negative_pixels += 1
            neg = -delta
            negative_sum += neg
            max_negative_abs = max(max_negative_abs, neg)
    return {
        "region": name,
        "pixels": pixels,
        "coverage": pixels / float(max(1, total_pixels)),
        "mean_abs_luma_diff": abs_sum / float(max(1, pixels)),
        "signed_luma_mean": signed_sum / float(max(1, pixels)),
        "positive_pixels": positive_pixels,
        "positive_coverage": positive_pixels / float(max(1, total_pixels)),
        "positive_mean": positive_sum / float(max(1, positive_pixels)),
        "max_positive": max_positive,
        "negative_pixels": negative_pixels,
        "negative_coverage": negative_pixels / float(max(1, total_pixels)),
        "negative_mean_abs": negative_sum / float(max(1, negative_pixels)),
        "max_negative_abs": max_negative_abs,
        "total_pixels": total_pixels,
    }


def aggregate_region_stats(frame_results):
    names = []
    for frame in frame_results:
        for name in frame.get("regions", {}):
            if name not in names:
                names.append(name)
    aggregate = {}
    for name in names:
        rows = [frame["regions"][name] for frame in frame_results if name in frame.get("regions", {})]
        pixels = sum(row["pixels"] for row in rows)
        total_pixels = sum(row["total_pixels"] for row in rows)
        positive_pixels = sum(row["positive_pixels"] for row in rows)
        negative_pixels = sum(row["negative_pixels"] for row in rows)
        aggregate[name] = {
            "region": name,
            "pixels": pixels,
            "coverage": pixels / float(max(1, total_pixels)),
            "mean_abs_luma_diff": sum(row["mean_abs_luma_diff"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "signed_luma_mean": sum(row["signed_luma_mean"] * row["pixels"] for row in rows) / float(max(1, pixels)),
            "positive_pixels": positive_pixels,
            "positive_coverage": positive_pixels / float(max(1, total_pixels)),
            "positive_mean": sum(row["positive_mean"] * row["positive_pixels"] for row in rows) / float(max(1, positive_pixels)),
            "max_positive": max((row["max_positive"] for row in rows), default=0.0),
            "negative_pixels": negative_pixels,
            "negative_coverage": negative_pixels / float(max(1, total_pixels)),
            "negative_mean_abs": sum(row["negative_mean_abs"] * row["negative_pixels"] for row in rows) / float(max(1, negative_pixels)),
            "max_negative_abs": max((row["max_negative_abs"] for row in rows), default=0.0),
            "total_pixels": total_pixels,
        }
    return aggregate


def selected_mask(deltas, source_mask, direction, args):
    selected = bytearray(len(deltas))
    if direction == "brighten":
        threshold = args.positive_threshold
        for index, delta in enumerate(deltas):
            if source_mask is not None and not source_mask[index]:
                continue
            if delta >= threshold:
                selected[index] = 1
    else:
        threshold = args.negative_threshold
        for index, delta in enumerate(deltas):
            if source_mask is not None and not source_mask[index]:
                continue
            if delta <= -threshold:
                selected[index] = 1
    return selected


def component_stats(indices, width, deltas, direction, frame_weight):
    count = len(indices)
    sum_x = 0.0
    sum_y = 0.0
    sum_wx = 0.0
    sum_wy = 0.0
    sum_signed = 0.0
    sum_abs = 0.0
    max_abs = 0.0
    x0 = width
    y0 = 10**9
    x1 = 0
    y1 = 0
    for index in indices:
        y, x = divmod(index, width)
        delta = deltas[index]
        abs_delta = abs(delta)
        weight = max(1.0, abs_delta)
        sum_x += x
        sum_y += y
        sum_wx += x * weight
        sum_wy += y * weight
        sum_signed += delta
        sum_abs += abs_delta
        max_abs = max(max_abs, abs_delta)
        x0 = min(x0, x)
        y0 = min(y0, y)
        x1 = max(x1, x)
        y1 = max(y1, y)
    mean_abs = sum_abs / float(max(1, count))
    score = mean_abs * math.sqrt(float(count)) * frame_weight
    return {
        "direction": direction,
        "area_px": count,
        "bbox": [int(x0), int(y0), int(x1), int(y1)],
        "center_px": [sum_x / count, sum_y / count],
        "weighted_center_px": [sum_wx / max(1.0, sum_abs), sum_wy / max(1.0, sum_abs)],
        "mean_signed_luma": sum_signed / float(max(1, count)),
        "mean_abs_luma": mean_abs,
        "max_abs_luma": max_abs,
        "frame_weight": frame_weight,
        "score": score,
    }


def connected_components(selected, deltas, width, height, direction, frame_weight, args):
    visited = bytearray(width * height)
    components = []
    offsets = (-width, width, -1, 1)
    for start, value in enumerate(selected):
        if not value or visited[start]:
            continue
        queue = deque([start])
        visited[start] = 1
        indices = []
        while queue:
            current = queue.popleft()
            indices.append(current)
            x = current % width
            for offset in offsets:
                nxt = current + offset
                if nxt < 0 or nxt >= width * height:
                    continue
                if offset == -1 and x == 0:
                    continue
                if offset == 1 and x == width - 1:
                    continue
                if selected[nxt] and not visited[nxt]:
                    visited[nxt] = 1
                    queue.append(nxt)
        if len(indices) >= args.min_component_pixels:
            components.append(component_stats(indices, width, deltas, direction, frame_weight))
    components.sort(key=lambda item: item["score"], reverse=True)
    return components[:args.max_components_per_frame]


def response_request(frame, region, component, args):
    x0, y0, x1, y1 = component["bbox"]
    radius_px = max(1.0, math.sqrt(component["area_px"] / math.pi))
    strength = min(
        args.max_response_strength,
        max(args.min_response_strength, component["mean_abs_luma"] / 255.0 * args.response_gain),
    )
    return {
        "frame": frame.get("frame"),
        "output_frame": frame.get("output_frame"),
        "region": region,
        "direction": component["direction"],
        "bbox": component["bbox"],
        "center_px": component["center_px"],
        "weighted_center_px": component["weighted_center_px"],
        "radius_px": radius_px,
        "width_px": x1 - x0 + 1,
        "height_px": y1 - y0 + 1,
        "area_px": component["area_px"],
        "mean_signed_luma": component["mean_signed_luma"],
        "mean_abs_luma": component["mean_abs_luma"],
        "max_abs_luma": component["max_abs_luma"],
        "frame_weight": component["frame_weight"],
        "score": component["score"],
        "suggested_response": {
            "screen_center_px": component["weighted_center_px"],
            "screen_radius_px": radius_px,
            "direction": component["direction"],
            "strength": strength,
            "max_luma_delta": min(args.max_luma_delta, component["max_abs_luma"]),
        },
    }


def signed_heatmap(deltas, size, scale):
    pixels = bytearray()
    for delta in deltas:
        if abs(delta) < 0.5:
            pixels.extend((6, 11, 16))
            continue
        t = min(1.0, abs(delta) / max(1.0, scale))
        if delta > 0.0:
            pixels.extend((int(24 + 231 * t), int(26 + 196 * t), int(20 + 54 * t)))
        else:
            pixels.extend((int(18 + 38 * t), int(62 + 142 * t), int(96 + 159 * t)))
    return Image.frombytes("RGB", size, bytes(pixels))


def mask_preview(masks, size):
    if not masks:
        return Image.new("RGB", size, (6, 11, 16))
    pixels = bytearray()
    values = list(masks.values())
    count = len(values[0]) if values else size[0] * size[1]
    for index in range(count):
        enabled = sum(1 for mask in values if mask is not None and mask[index])
        if enabled <= 0:
            pixels.extend((6, 11, 16))
        elif enabled == 1:
            pixels.extend((96, 164, 214))
        else:
            pixels.extend((235, 210, 96))
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
    gif = next((item for item in assets if item["label"] == "Signed Gap GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Signed Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Requests", checks.get("requests")),
            ("Max +", f"{checks.get('max_positive', 0.0):.3f}"),
            ("Max -", f"{checks.get('max_negative_abs', 0.0):.3f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Signed gap GIF"></section>' if gif else ""
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
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 40px; }}
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
    checks = summary.get("checks") or {}
    aggregate = summary.get("aggregate_regions") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary.get('gallery', {}).get('index_repo_path')}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Requests: `{checks.get('requests')}`",
        f"- Max positive luma gap: `{checks.get('max_positive')}`",
        f"- Max negative luma gap abs: `{checks.get('max_negative_abs')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Aggregate Regions",
        "",
        "| Region | Coverage | Mean Abs Luma | Signed Luma | Positive Px | Positive Mean | Negative Px | Negative Mean Abs |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, item in aggregate.items():
        lines.append(
            f"| `{name}` | {item.get('coverage', 0.0):.6f} | {item.get('mean_abs_luma_diff', 0.0):.6f} | "
            f"{item.get('signed_luma_mean', 0.0):.6f} | {item.get('positive_pixels', 0)} | "
            f"{item.get('positive_mean', 0.0):.6f} | {item.get('negative_pixels', 0)} | "
            f"{item.get('negative_mean_abs', 0.0):.6f} |"
        )
    lines.extend([
        "",
        "## Top Response Requests",
        "",
        "| Rank | Output | Region | Direction | Score | Mean Abs | Max Abs | Area | BBox | Strength |",
        "| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ])
    for rank, item in enumerate(summary.get("requests") or [], start=1):
        response = item.get("suggested_response") or {}
        lines.append(
            f"| {rank} | {item.get('output_frame')} | `{item.get('region')}` | `{item.get('direction')}` | "
            f"{item.get('score', 0.0):.3f} | {item.get('mean_abs_luma', 0.0):.3f} | "
            f"{item.get('max_abs_luma', 0.0):.3f} | {item.get('area_px')} | `{item.get('bbox')}` | "
            f"{response.get('strength', 0.0):.4f} |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def load_mask_sources(mask_args, root):
    sources = []
    for value in mask_args or []:
        name, path = parse_mask_source(value)
        abs_path = require_file(path, f"mask source {name}")
        summary = read_json(abs_path)
        sources.append({
            "name": name,
            "path": abs_path,
            "repo_path": posix_rel(abs_path, root),
            "sha256": sha256_file(abs_path),
            "schema": summary.get("schema"),
            "candidate": summary.get("candidate"),
            "frames": output_frame_map(summary.get("frames") or []),
        })
    return sources


def analyze(args):
    require_pillow()
    root = os.getcwd()
    gap_path = require_file(args.target_gap_summary, "target gap summary")
    gap = read_json(gap_path)
    if gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{args.target_gap_summary}: expected lsfs_mitsuba_renderer_target_gap schema")

    mask_sources = load_mask_sources(args.mask_source, root)
    frames = gap.get("frames") or []
    max_frame_mad = max((float(frame.get("gap_mean_abs_diff") or 0.0) for frame in frames), default=1.0)

    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_results = []
    requests = []
    strip_paths = []
    max_positive = 0.0
    max_negative_abs = 0.0
    for frame_index, frame in enumerate(frames):
        actual_path = require_file(resolve_path(frame.get("actual_repo_path")), "actual frame")
        target_path = require_file(resolve_path(frame.get("target_repo_path")), "target frame")
        actual = Image.open(actual_path).convert("RGB")
        target = Image.open(target_path).convert("RGB")
        if actual.size != target.size:
            actual = actual.resize(target.size, Image.Resampling.BICUBIC)
        deltas = signed_luma_deltas(actual, target)
        width, height = target.size
        total_pixels = width * height
        region_masks = {"all": None}
        source_entries = []
        for source in mask_sources:
            mask_frame = source["frames"].get(frame.get("output_frame"))
            layer_path = resolve_path(mask_layer_ref(mask_frame))
            mask_image = Image.open(require_file(layer_path, f"mask frame {source['name']}")).convert("RGBA")
            region_masks[source["name"]] = mask_bytes(mask_image, target.size, args.mask_threshold)
            source_entries.append({
                "name": source["name"],
                "mask_repo_path": posix_rel(layer_path, root),
                "mask_coverage": sum(region_masks[source["name"]]) / float(max(1, total_pixels)),
            })

        frame_weight = 0.5 + 0.5 * (float(frame.get("gap_mean_abs_diff") or 0.0) / max(1.0, max_frame_mad))
        frame_regions = {}
        frame_requests = []
        component_regions = set(region_masks) if args.include_all_components or not mask_sources else {
            source["name"] for source in mask_sources
        }
        for region, mask in region_masks.items():
            stats = region_stats(region, deltas, mask, total_pixels, args)
            frame_regions[region] = stats
            max_positive = max(max_positive, stats["max_positive"])
            max_negative_abs = max(max_negative_abs, stats["max_negative_abs"])
            if region not in component_regions:
                continue
            for direction in ("brighten", "dim"):
                selected = selected_mask(deltas, mask, direction, args)
                components = connected_components(selected, deltas, width, height, direction, frame_weight, args)
                for component in components:
                    request = response_request(frame, region, component, args)
                    frame_requests.append(request)
                    requests.append(request)

        heat = signed_heatmap(deltas, target.size, args.heatmap_scale)
        mask_panel = mask_preview({key: value for key, value in region_masks.items() if key != "all"}, target.size)
        strip_path = os.path.join(strip_dir, f"frame_{frame_index:04d}_signed_gap.png")
        labeled_strip(
            [target, actual, heat, mask_panel],
            ["Target", "Actual", "Signed Gap (+brighten/-dim)", "Mask Sources"],
            strip_path,
        )
        strip_paths.append(strip_path)
        frame_results.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "gap_mean_abs_diff": frame.get("gap_mean_abs_diff"),
            "gap_max_abs_diff": frame.get("gap_max_abs_diff"),
            "frame_weight": frame_weight,
            "target_repo_path": posix_rel(target_path, root),
            "actual_repo_path": posix_rel(actual_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "mask_sources": source_entries,
            "regions": frame_regions,
            "request_count": len(frame_requests),
        })

    if not frame_results:
        raise SystemExit("no frames to analyze")

    requests.sort(key=lambda item: item["score"], reverse=True)
    requests = requests[:args.max_requests]
    gif_path = os.path.join(assets_dir, "signed_gap.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "signed_gap.gif", "Signed Gap GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"signed_strip_{out_index:02d}.png", f"Signed Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "signed_target_gap_analysis.json")
    metadata_files = [
        copy_asset(gap_path, assets_dir, "renderer_target_gap_summary.json", "Target gap summary", root),
    ]
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_signed_target_gap_analysis",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "sources": {
            "target_gap_summary": {
                "path": gap_path,
                "repo_path": posix_rel(gap_path, root),
                "sha256": sha256_file(gap_path),
            },
            "mask_sources": [
                {key: value for key, value in source.items() if key != "frames"}
                for source in mask_sources
            ],
        },
        "settings": {
            "positive_threshold": args.positive_threshold,
            "negative_threshold": args.negative_threshold,
            "mask_threshold": args.mask_threshold,
            "min_component_pixels": args.min_component_pixels,
            "max_components_per_frame": args.max_components_per_frame,
            "max_requests": args.max_requests,
            "response_gain": args.response_gain,
            "min_response_strength": args.min_response_strength,
            "max_response_strength": args.max_response_strength,
            "max_luma_delta": args.max_luma_delta,
            "heatmap_scale": args.heatmap_scale,
        },
        "checks": {
            "frames": len(frame_results),
            "requests": len(requests),
            "max_positive": max_positive,
            "max_negative_abs": max_negative_abs,
            "gif_bytes": os.path.getsize(gif_path),
        },
        "aggregate_regions": aggregate_region_stats(frame_results),
        "requests": requests,
        "frames": frame_results,
        "gallery": {},
        "next": args.next,
    }
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
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_signed_target_gap_gallery",
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
        f"status=ready frames={len(frame_results)} requests={len(requests)} "
        f"max_positive={max_positive:.3f} max_negative_abs={max_negative_abs:.3f} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze signed target gaps from a Mitsuba target-gap summary")
    parser.add_argument("target_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--mask-source", action="append", default=[], help="Optional name=summary.json mask source")
    parser.add_argument("--positive-threshold", type=float, default=8.0)
    parser.add_argument("--negative-threshold", type=float, default=8.0)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--min-component-pixels", type=int, default=12)
    parser.add_argument("--max-components-per-frame", type=int, default=3)
    parser.add_argument("--max-requests", type=int, default=20)
    parser.add_argument("--include-all-components", action="store_true")
    parser.add_argument("--response-gain", type=float, default=1.5)
    parser.add_argument("--min-response-strength", type=float, default=0.02)
    parser.add_argument("--max-response-strength", type=float, default=0.85)
    parser.add_argument("--max-luma-delta", type=float, default=64.0)
    parser.add_argument("--heatmap-scale", type=float, default=80.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Signed Target Gap Analysis")
    parser.add_argument("--next", default="Use the signed response requests to build the next frame-aware render candidate.")
    args = parser.parse_args(argv)
    if args.positive_threshold < 0.0 or args.negative_threshold < 0.0:
        parser.error("thresholds must be non-negative")
    if not (0 <= args.mask_threshold <= 255):
        parser.error("mask-threshold must be in [0, 255]")
    if args.min_component_pixels <= 0:
        parser.error("min-component-pixels must be positive")
    if args.max_components_per_frame <= 0:
        parser.error("max-components-per-frame must be positive")
    if args.max_requests <= 0:
        parser.error("max-requests must be positive")
    if args.response_gain <= 0.0:
        parser.error("response-gain must be positive")
    if args.min_response_strength < 0.0 or args.max_response_strength <= 0.0:
        parser.error("response strength bounds must be non-negative and positive")
    if args.min_response_strength > args.max_response_strength:
        parser.error("min-response-strength cannot exceed max-response-strength")
    if args.max_luma_delta <= 0.0:
        parser.error("max-luma-delta must be positive")
    if args.heatmap_scale <= 0.0:
        parser.error("heatmap-scale must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    analyze(args)


if __name__ == "__main__":
    main()
