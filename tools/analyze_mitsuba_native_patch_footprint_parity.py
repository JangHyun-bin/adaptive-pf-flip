#!/usr/bin/env python
"""Analyze screen-footprint parity between signed requests and native Mitsuba patches."""

import argparse
import math
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to analyze patch footprint parity")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def bbox_center(bbox):
    x0, y0, x1, y1 = [float(v) for v in bbox]
    return [(x0 + x1) * 0.5, (y0 + y1) * 0.5]


def bbox_contains(bbox, point, padding=0.0):
    x0, y0, x1, y1 = [float(v) for v in bbox]
    x, y = point
    return x >= x0 - padding and x <= x1 + padding and y >= y0 - padding and y <= y1 + padding


def request_key(output_frame, bbox):
    return (int(output_frame), tuple(int(round(float(v))) for v in bbox))


def request_map(requests):
    result = {}
    for request in requests:
        bbox = request.get("bbox")
        output_frame = request.get("output_frame")
        if bbox is None or output_frame is None:
            continue
        result[request_key(output_frame, bbox)] = request
    return result


def indexed_requests(requests):
    by_output = {}
    for request in requests:
        output_frame = request.get("output_frame")
        if output_frame is None:
            continue
        by_output.setdefault(output_frame, []).append(request)
    return by_output


def patch_request(patch, requests_by_key):
    bbox = patch.get("request_bbox")
    output_frame = patch.get("request_output_frame")
    if bbox is None or output_frame is None:
        return None
    return requests_by_key.get(request_key(output_frame, bbox))


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


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def draw_overlay(base_img, frame_requests, patch_rows, out_path, args):
    image = base_img.convert("RGB").copy()
    draw = ImageDraw.Draw(image)
    for rank, request in enumerate(frame_requests, start=1):
        bbox = request.get("bbox")
        if not bbox:
            continue
        x0, y0, x1, y1 = [int(round(float(v))) for v in bbox]
        draw.rectangle([x0, y0, x1, y1], outline=(255, 218, 86), width=2)
        cx, cy = bbox_center(bbox)
        draw.line([cx - 5, cy, cx + 5, cy], fill=(255, 218, 86), width=1)
        draw.line([cx, cy - 5, cx, cy + 5], fill=(255, 218, 86), width=1)
        draw.text((x0 + 3, max(0, y0 - 13)), f"r{rank}", fill=(255, 218, 86))
    for patch in patch_rows:
        sx, sy = patch["screen"]
        radius = max(args.min_draw_radius, min(args.max_draw_radius, patch.get("request_radius_px") or args.default_draw_radius))
        color = (98, 205, 255) if patch["inside_bbox"] else (255, 88, 88)
        draw.ellipse([sx - radius, sy - radius, sx + radius, sy + radius], outline=color, width=2)
        rcx, rcy = patch["request_center_px"]
        draw.line([rcx, rcy, sx, sy], fill=color, width=1)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    image.save(out_path)


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Parity GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Parity Frame")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Patches", checks.get("patches")),
            ("Inside", f"{checks.get('inside_bbox_ratio', 0.0):.3f}"),
            ("Mean error", f"{checks.get('mean_center_error_px', 0.0):.2f}px"),
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
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px 18px 40px; }}
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
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Requests: `{checks.get('requests')}`",
        f"- Patches: `{checks.get('patches')}`",
        f"- Patches inside request bbox: `{checks.get('inside_bbox')}`",
        f"- Inside bbox ratio: `{checks.get('inside_bbox_ratio')}`",
        f"- Mean center error px: `{checks.get('mean_center_error_px')}`",
        f"- Max center error px: `{checks.get('max_center_error_px')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Requests | Patches | Inside | Mean Error | Max Error | Overlay |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('requests')} | {frame.get('patches')} | "
            f"{frame.get('inside_bbox')} | {frame.get('mean_center_error_px', 0.0):.3f} | "
            f"{frame.get('max_center_error_px', 0.0):.3f} | `{frame.get('overlay_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def analyze(args):
    require_pillow()
    root = os.getcwd()
    native_path = require_file(args.native_export, "native export")
    request_path = require_file(args.residual_requests, "residual request summary")
    target_gap_path = require_file(args.target_gap_summary, "target gap summary")
    native = read_json(native_path)
    requests = read_json(request_path)
    target_gap = read_json(target_gap_path)
    if native.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.native_export}: expected lsfs_mitsuba_xml_export schema")
    if requests.get("schema") != "lsfs_mitsuba_target_residual_analysis":
        raise SystemExit(f"{args.residual_requests}: expected lsfs_mitsuba_target_residual_analysis schema")
    if target_gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{args.target_gap_summary}: expected lsfs_mitsuba_renderer_target_gap schema")

    requests_by_key = request_map(requests.get("requests") or [])
    requests_by_output = indexed_requests(requests.get("requests") or [])
    target_by_output = output_frame_map(target_gap.get("frames") or [])

    out_dir = os.path.abspath(args.out_dir)
    overlay_dir = os.path.join(out_dir, "overlays")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(overlay_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_results = []
    overlay_paths = []
    all_patch_rows = []
    missing_matches = 0
    for frame_index, frame in enumerate(native.get("frames") or []):
        output_frame = frame.get("output_frame")
        gap_frame = target_by_output.get(output_frame)
        if not gap_frame:
            continue
        base_path = require_file(resolve_path(gap_frame.get("actual_repo_path")), "actual target-gap frame")
        base_img = Image.open(base_path).convert("RGB")
        frame_requests = requests_by_output.get(output_frame) or []
        patch_samples = ((frame.get("residual_response_patches") or {}).get("patch_samples") or [])
        patch_rows = []
        for patch in patch_samples:
            request = patch_request(patch, requests_by_key)
            if request is None:
                missing_matches += 1
                continue
            center = bbox_center(request.get("bbox"))
            screen = [float(patch["screen"][0]), float(patch["screen"][1])]
            error = math.hypot(screen[0] - center[0], screen[1] - center[1])
            inside = bbox_contains(request.get("bbox"), screen, args.bbox_padding)
            row = {
                "output_frame": output_frame,
                "request_bbox": request.get("bbox"),
                "request_center_px": center,
                "request_radius_px": request.get("radius_px"),
                "screen": screen,
                "center_error_px": error,
                "inside_bbox": inside,
                "radiance": patch.get("radiance"),
                "world_radius": patch.get("radius"),
                "candidate_count": patch.get("candidate_count"),
                "used_fallback": patch.get("used_fallback"),
            }
            patch_rows.append(row)
            all_patch_rows.append(row)
        overlay_path = os.path.join(overlay_dir, f"frame_{frame_index:04d}_parity.png")
        draw_overlay(base_img, frame_requests, patch_rows, overlay_path, args)
        overlay_paths.append(overlay_path)
        errors = [row["center_error_px"] for row in patch_rows]
        frame_results.append({
            "frame": frame.get("frame", frame_index),
            "output_frame": output_frame,
            "requests": len(frame_requests),
            "patches": len(patch_rows),
            "inside_bbox": sum(1 for row in patch_rows if row["inside_bbox"]),
            "inside_bbox_ratio": sum(1 for row in patch_rows if row["inside_bbox"]) / float(max(1, len(patch_rows))),
            "mean_center_error_px": sum(errors) / float(max(1, len(errors))),
            "max_center_error_px": max(errors) if errors else 0.0,
            "overlay_repo_path": posix_rel(overlay_path, root),
            "patches_detail": patch_rows,
        })

    if not frame_results:
        raise SystemExit("no overlapping frames to analyze")
    gif_path = os.path.join(assets_dir, "parity.gif")
    write_gif(overlay_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(overlay_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "parity.gif", "Parity GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(overlay_paths[frame_index], assets_dir, f"parity_frame_{out_index:02d}.png", f"Parity Frame {out_index + 1}", root))

    errors = [row["center_error_px"] for row in all_patch_rows]
    inside = sum(1 for row in all_patch_rows if row["inside_bbox"])
    summary_path = os.path.join(out_dir, "native_patch_footprint_parity.json")
    metadata_files = [
        copy_asset(native_path, assets_dir, "native_export.json", "Native export", root),
        copy_asset(request_path, assets_dir, "residual_requests.json", "Residual requests", root),
        copy_asset(target_gap_path, assets_dir, "target_gap_summary.json", "Target gap summary", root),
    ]
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_native_patch_footprint_parity",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "sources": {
            "native_export": posix_rel(native_path, root),
            "residual_requests": posix_rel(request_path, root),
            "target_gap_summary": posix_rel(target_gap_path, root),
        },
        "settings": {
            "bbox_padding": args.bbox_padding,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frame_results),
            "requests": sum(frame["requests"] for frame in frame_results),
            "patches": len(all_patch_rows),
            "missing_patch_request_matches": missing_matches,
            "inside_bbox": inside,
            "inside_bbox_ratio": inside / float(max(1, len(all_patch_rows))),
            "mean_center_error_px": sum(errors) / float(max(1, len(errors))),
            "max_center_error_px": max(errors) if errors else 0.0,
            "gif_bytes": os.path.getsize(gif_path),
        },
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
        "schema": "lsfs_mitsuba_native_patch_footprint_parity_gallery",
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
        f"status=ready frames={len(frame_results)} patches={len(all_patch_rows)} "
        f"inside={inside}/{len(all_patch_rows)} mean_error={summary['checks']['mean_center_error_px']:.3f} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze native Mitsuba patch footprint parity")
    parser.add_argument("native_export")
    parser.add_argument("residual_requests")
    parser.add_argument("target_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--bbox-padding", type=float, default=0.0)
    parser.add_argument("--default-draw-radius", type=float, default=16.0)
    parser.add_argument("--min-draw-radius", type=float, default=6.0)
    parser.add_argument("--max-draw-radius", type=float, default=64.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Native Patch Footprint Parity")
    parser.add_argument("--next", default="Use footprint parity to tune native patch placement and response.")
    args = parser.parse_args(argv)
    if args.bbox_padding < 0.0:
        parser.error("bbox-padding must be non-negative")
    if args.default_draw_radius <= 0.0 or args.min_draw_radius <= 0.0 or args.max_draw_radius <= 0.0:
        parser.error("draw radii must be positive")
    if args.min_draw_radius > args.max_draw_radius:
        parser.error("min-draw-radius cannot exceed max-draw-radius")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    analyze(args)


if __name__ == "__main__":
    main()
