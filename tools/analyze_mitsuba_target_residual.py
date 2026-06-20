#!/usr/bin/env python
"""Analyze positive target residuals for Mitsuba local-response calibration."""

import argparse
import math
import os
from collections import deque
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze target residuals")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def mask_layer_ref(frame):
    if not frame:
        return None
    return frame.get("layer_path") or frame.get("layer_repo_path")


def luma(pixel):
    return 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]


def residual_field(actual, target, mask_image, args):
    width, height = target.size
    actual_pixels = actual.load()
    target_pixels = target.load()
    mask_pixels = mask_image.load() if mask_image else None
    residual = bytearray(width * height)
    selected = bytearray(width * height)
    selected_count = 0
    positive_sum = 0.0
    for y in range(height):
        row = y * width
        for x in range(width):
            if mask_pixels is not None and mask_pixels[x, y] < args.mask_threshold:
                continue
            target_luma = luma(target_pixels[x, y])
            if target_luma < args.target_luma_min:
                continue
            diff = max(0.0, target_luma - luma(actual_pixels[x, y]))
            if diff <= 0.0:
                continue
            value = min(255, int(round(diff)))
            residual[row + x] = value
            positive_sum += diff
            if diff >= args.residual_threshold:
                selected[row + x] = 1
                selected_count += 1
    return residual, selected, selected_count, positive_sum


def component_stats(indices, width, residual):
    count = len(indices)
    sum_x = 0.0
    sum_y = 0.0
    sum_wx = 0.0
    sum_wy = 0.0
    sum_residual = 0.0
    max_residual = 0
    x0 = width
    y0 = 10**9
    x1 = 0
    y1 = 0
    for index in indices:
        y, x = divmod(index, width)
        value = int(residual[index])
        sum_x += x
        sum_y += y
        sum_wx += x * max(1, value)
        sum_wy += y * max(1, value)
        sum_residual += value
        max_residual = max(max_residual, value)
        x0 = min(x0, x)
        y0 = min(y0, y)
        x1 = max(x1, x)
        y1 = max(y1, y)
    weight = max(1.0, sum_residual)
    mean_residual = sum_residual / float(max(1, count))
    return {
        "area_px": count,
        "bbox": [int(x0), int(y0), int(x1), int(y1)],
        "center_px": [sum_x / count, sum_y / count],
        "weighted_center_px": [sum_wx / weight, sum_wy / weight],
        "mean_residual": mean_residual,
        "max_residual": max_residual,
        "sum_residual": sum_residual,
        "score": mean_residual * math.sqrt(float(count)),
    }


def connected_components(selected, residual, width, height, args):
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
            components.append(component_stats(indices, width, residual))
    components.sort(key=lambda item: item["score"], reverse=True)
    return components[:args.max_components_per_frame]


def residual_heatmap(residual, size):
    gray = Image.frombytes("L", size, bytes(residual))
    return ImageOps.colorize(gray, black=(4, 8, 16), white=(255, 238, 198), mid=(116, 95, 168))


def draw_overlay(target, components, out_path):
    overlay = target.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)
    for index, item in enumerate(components, start=1):
        x0, y0, x1, y1 = item["bbox"]
        color = (255, 214, 92) if index == 1 else (90, 200, 255)
        draw.rectangle([x0, y0, x1, y1], outline=color, width=2)
        draw.text((x0 + 4, max(0, y0 - 14)), f"{index}:{item['mean_residual']:.1f}", fill=color)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    overlay.save(out_path)


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def response_request(frame, component, args):
    x0, y0, x1, y1 = component["bbox"]
    radius_px = max(1.0, math.sqrt(component["area_px"] / math.pi))
    energy = component["mean_residual"] / 255.0
    radiance = min(args.max_suggested_radiance, max(args.min_suggested_radiance, energy * args.radiance_gain))
    return {
        "frame": frame["frame"],
        "output_frame": frame["output_frame"],
        "bbox": component["bbox"],
        "center_px": component["center_px"],
        "weighted_center_px": component["weighted_center_px"],
        "radius_px": radius_px,
        "area_px": component["area_px"],
        "mean_residual": component["mean_residual"],
        "max_residual": component["max_residual"],
        "score": component["score"],
        "suggested_patch": {
            "screen_center_px": component["weighted_center_px"],
            "screen_radius_px": radius_px,
            "radiance_scalar": radiance,
            "radiance_rgb": [radiance * 0.82, radiance, radiance * 1.28],
            "source_luma_min": args.target_luma_min,
        },
        "notes": "positive target residual inside the source-highlight mask" if args.mask_source else "positive target residual",
        "width_px": x1 - x0 + 1,
        "height_px": y1 - y0 + 1,
    }


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames analyzed: `{checks.get('frames_analyzed')}`",
        f"- Requests: `{checks.get('requests')}`",
        f"- Max residual: `{checks.get('max_residual')}`",
        f"- Mean selected residual: `{checks.get('mean_selected_residual')}`",
        f"- Overlay GIF: `{summary['gallery'].get('overlay_gif_repo_path')}`",
        "",
        "## Top Requests",
        "",
        "| Rank | Frame | Output | Score | Mean Residual | Max Residual | Area | BBox | Radiance |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for rank, item in enumerate(summary.get("requests") or [], start=1):
        patch = item.get("suggested_patch") or {}
        lines.append(
            f"| {rank} | {item.get('frame')} | {item.get('output_frame')} | "
            f"{item.get('score'):.3f} | {item.get('mean_residual'):.3f} | "
            f"{item.get('max_residual')} | {item.get('area_px')} | `{item.get('bbox')}` | "
            f"{patch.get('radiance_scalar'):.4f} |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def analyze(args):
    require_pillow()
    root = os.getcwd()
    gap_path = require_file(args.target_gap_summary, "target gap summary")
    gap = read_json(gap_path)
    if gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{args.target_gap_summary}: expected lsfs_mitsuba_renderer_target_gap schema")
    mask_frames = {}
    mask_source = None
    if args.mask_source:
        mask_path = require_file(args.mask_source, "mask source")
        mask_source = read_json(mask_path)
        mask_frames = output_frame_map(mask_source.get("frames") or [])

    out_dir = os.path.abspath(args.out_dir)
    overlay_dir = os.path.join(out_dir, "overlays")
    heat_dir = os.path.join(out_dir, "heatmaps")
    os.makedirs(overlay_dir, exist_ok=True)
    os.makedirs(heat_dir, exist_ok=True)

    frame_results = []
    requests = []
    overlay_paths = []
    selected_residual_sum = 0.0
    selected_pixel_count = 0
    max_residual = 0
    for frame in gap.get("frames") or []:
        actual_path = require_file(resolve_path(frame.get("actual_repo_path")), "actual frame")
        target_path = require_file(resolve_path(frame.get("target_repo_path")), "target frame")
        actual = Image.open(actual_path).convert("RGB")
        target = Image.open(target_path).convert("RGB")
        if actual.size != target.size:
            actual = actual.resize(target.size, Image.Resampling.BICUBIC)
        mask_image = None
        mask_frame = mask_frames.get(frame.get("output_frame"))
        mask_path = resolve_path(mask_layer_ref(mask_frame))
        if mask_path and os.path.isfile(mask_path):
            mask_image = Image.open(mask_path).convert("L")
            if mask_image.size != target.size:
                mask_image = mask_image.resize(target.size, Image.Resampling.BICUBIC)
        residual, selected, selected_count, positive_sum = residual_field(actual, target, mask_image, args)
        components = connected_components(selected, residual, target.size[0], target.size[1], args)
        base = f"frame_{len(frame_results):04d}.png"
        overlay_path = os.path.join(overlay_dir, base)
        heat_path = os.path.join(heat_dir, base)
        draw_overlay(target, components, overlay_path)
        residual_heatmap(residual, target.size).save(heat_path)
        overlay_paths.append(overlay_path)
        selected_residual_sum += sum(residual[index] for index, value in enumerate(selected) if value)
        selected_pixel_count += selected_count
        if residual:
            max_residual = max(max_residual, max(residual))
        frame_requests = [response_request(frame, component, args) for component in components]
        requests.extend(frame_requests)
        frame_results.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "selected_pixels": selected_count,
            "positive_residual_sum": positive_sum,
            "component_count": len(components),
            "requests": frame_requests,
            "overlay_repo_path": posix_rel(overlay_path, root),
            "heatmap_repo_path": posix_rel(heat_path, root),
            "actual_repo_path": posix_rel(actual_path, root),
            "target_repo_path": posix_rel(target_path, root),
            "mask_repo_path": posix_rel(mask_path, root) if mask_path else None,
        })
    requests.sort(key=lambda item: item["score"], reverse=True)
    requests = requests[:args.max_requests]
    gif_path = os.path.join(out_dir, "residual_overlay.gif")
    write_gif(overlay_paths, gif_path, args.fps)
    summary = {
        "schema": "lsfs_mitsuba_target_residual_analysis",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "sources": {
            "target_gap_summary": {
                "path": gap_path,
                "repo_path": posix_rel(gap_path, root),
                "sha256": sha256_file(gap_path),
            },
            "mask_source": {
                "path": resolve_path(args.mask_source),
                "repo_path": posix_rel(resolve_path(args.mask_source), root),
                "sha256": sha256_file(resolve_path(args.mask_source)),
                "schema": (mask_source or {}).get("schema"),
            } if args.mask_source else None,
        },
        "settings": {
            "residual_threshold": args.residual_threshold,
            "target_luma_min": args.target_luma_min,
            "mask_threshold": args.mask_threshold,
            "min_component_pixels": args.min_component_pixels,
            "max_components_per_frame": args.max_components_per_frame,
            "max_requests": args.max_requests,
        },
        "checks": {
            "frames_analyzed": len(frame_results),
            "requests": len(requests),
            "selected_pixels": selected_pixel_count,
            "mean_selected_residual": selected_residual_sum / float(max(1, selected_pixel_count)),
            "max_residual": max_residual,
            "overlay_gif_bytes": os.path.getsize(gif_path),
        },
        "requests": requests,
        "frames": frame_results,
        "gallery": {
            "overlay_gif_path": gif_path,
            "overlay_gif_repo_path": posix_rel(gif_path, root),
            "overlay_gif_sha256": sha256_file(gif_path),
            "overlay_gif_size": os.path.getsize(gif_path),
            "overlay_gif_dimensions": image_dimensions(gif_path),
        },
        "next": args.next,
    }
    summary_path = os.path.join(out_dir, "target_residual_analysis.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(frame_results)} requests={len(requests)} "
        f"max_residual={max_residual} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze positive target residuals from a Mitsuba target-gap summary")
    parser.add_argument("target_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--mask-source")
    parser.add_argument("--residual-threshold", type=float, default=10.0)
    parser.add_argument("--target-luma-min", type=float, default=120.0)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--min-component-pixels", type=int, default=12)
    parser.add_argument("--max-components-per-frame", type=int, default=4)
    parser.add_argument("--max-requests", type=int, default=16)
    parser.add_argument("--min-suggested-radiance", type=float, default=0.05)
    parser.add_argument("--max-suggested-radiance", type=float, default=1.8)
    parser.add_argument("--radiance-gain", type=float, default=3.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S453 Mitsuba Target Residual Analysis")
    parser.add_argument("--next", default="Use these residual requests to generate a target-driven local response candidate.")
    args = parser.parse_args(argv)
    if args.residual_threshold < 0.0:
        parser.error("residual-threshold must be non-negative")
    if args.target_luma_min < 0.0 or args.target_luma_min > 255.0:
        parser.error("target-luma-min must be in [0, 255]")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.min_component_pixels <= 0:
        parser.error("min-component-pixels must be positive")
    if args.max_components_per_frame <= 0:
        parser.error("max-components-per-frame must be positive")
    if args.max_requests <= 0:
        parser.error("max-requests must be positive")
    if args.min_suggested_radiance < 0.0 or args.max_suggested_radiance <= 0.0:
        parser.error("suggested radiance bounds must be non-negative and positive")
    if args.min_suggested_radiance > args.max_suggested_radiance:
        parser.error("min-suggested-radiance cannot exceed max-suggested-radiance")
    if args.radiance_gain <= 0.0:
        parser.error("radiance-gain must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    analyze(args)


if __name__ == "__main__":
    main()
