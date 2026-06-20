#!/usr/bin/env python
"""Apply bounded image-space response from signed Mitsuba target-gap requests."""

import argparse
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
        raise SystemExit("Pillow is required to apply signed gap response")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def render_preview_path(frame):
    preview = (frame or {}).get("preview") or {}
    return preview.get("path") or preview.get("repo_path")


def parse_csv(value):
    return {item.strip() for item in value.split(",") if item.strip()}


def clamp_channel(value):
    return max(0, min(255, int(round(value))))


def request_strength(request, args):
    response = request.get("suggested_response") or {}
    base = float(response.get("strength") or 0.0)
    return max(0.0, min(args.max_strength, base * args.strength_scale))


def request_weight(x, y, bbox, power):
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    rx = max(1.0, (x1 - x0 + 1) * 0.5)
    ry = max(1.0, (y1 - y0 + 1) * 0.5)
    nx = (x - cx) / rx
    ny = (y - cy) / ry
    dist2 = nx * nx + ny * ny
    if dist2 >= 1.0:
        return 0.0
    return (1.0 - dist2) ** power


def apply_response(actual_img, target_img, requests, args):
    width, height = target_img.size
    actual = bytearray(actual_img.convert("RGB").tobytes())
    target = target_img.convert("RGB").tobytes()
    stats = {
        "requests": len(requests),
        "changed_pixels": 0,
        "changed_samples": 0,
        "max_channel_delta": 0,
        "mean_applied_abs_delta": 0.0,
    }
    changed = bytearray(width * height)
    applied_abs_sum = 0.0
    for request in requests:
        bbox = [int(value) for value in request.get("bbox")]
        x0, y0, x1, y1 = bbox
        x0 = max(0, min(width - 1, x0))
        x1 = max(0, min(width - 1, x1))
        y0 = max(0, min(height - 1, y0))
        y1 = max(0, min(height - 1, y1))
        if x1 < x0 or y1 < y0:
            continue
        strength = request_strength(request, args)
        if strength <= 0.0:
            continue
        direction = request.get("direction")
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                weight = request_weight(x, y, [x0, y0, x1, y1], args.feather_power)
                if weight <= 0.0:
                    continue
                pixel = y * width + x
                base = pixel * 3
                touched = False
                for channel in range(3):
                    current = actual[base + channel]
                    target_value = target[base + channel]
                    diff = target_value - current
                    if direction == "brighten" and diff <= 0:
                        continue
                    if direction == "dim" and diff >= 0:
                        continue
                    delta = diff * strength * weight
                    if args.max_channel_delta > 0.0:
                        delta = max(-args.max_channel_delta, min(args.max_channel_delta, delta))
                    if abs(delta) < 0.01:
                        continue
                    new_value = clamp_channel(current + delta)
                    channel_delta = abs(new_value - current)
                    if channel_delta <= 0:
                        continue
                    actual[base + channel] = new_value
                    stats["changed_samples"] += 1
                    stats["max_channel_delta"] = max(stats["max_channel_delta"], channel_delta)
                    applied_abs_sum += channel_delta
                    touched = True
                if touched:
                    changed[pixel] = 1
    stats["changed_pixels"] = sum(1 for value in changed if value)
    stats["changed_coverage"] = stats["changed_pixels"] / float(max(1, width * height))
    stats["mean_applied_abs_delta"] = applied_abs_sum / float(max(1, stats["changed_samples"]))
    return Image.frombytes("RGB", target_img.size, bytes(actual)), stats


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
    gif = next((item for item in assets if item["label"] == "Response GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Response Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Requests", checks.get("applied_requests")),
            ("Changed", f"{checks.get('max_changed_coverage', 0.0):.6f}"),
            ("Max delta", checks.get("max_channel_delta")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Response GIF"></section>' if gif else ""
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
        f"- Applied requests: `{checks.get('applied_requests')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Max channel delta: `{checks.get('max_channel_delta')}`",
        f"- Mean applied abs delta: `{checks.get('mean_applied_abs_delta')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Settings",
        "",
    ]
    for key, value in summary.get("settings", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Requests | Changed | Max Delta | Source | Response |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ])
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('applied_requests')} | "
            f"{frame.get('response', {}).get('changed_coverage')} | "
            f"{frame.get('response', {}).get('max_channel_delta')} | "
            f"`{frame.get('source_repo_path')}` | `{frame.get('graded_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def select_requests(analysis, args):
    allowed_regions = parse_csv(args.regions)
    allowed_directions = parse_csv(args.directions)
    selected = []
    for request in analysis.get("requests") or []:
        if request.get("region") not in allowed_regions:
            continue
        if request.get("direction") not in allowed_directions:
            continue
        if float(request.get("score") or 0.0) < args.min_score:
            continue
        selected.append(request)
        if len(selected) >= args.max_requests:
            break
    by_output = {}
    for request in selected:
        by_output.setdefault(request.get("output_frame"), []).append(request)
    return selected, by_output


def build(args):
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.render_manifest, "render manifest")
    analysis_path = require_file(args.signed_gap_analysis, "signed gap analysis")
    render = read_json(render_path)
    analysis = read_json(analysis_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if analysis.get("schema") != "lsfs_mitsuba_signed_target_gap_analysis":
        raise SystemExit(f"{args.signed_gap_analysis}: expected lsfs_mitsuba_signed_target_gap_analysis schema")

    selected_requests, requests_by_output = select_requests(analysis, args)
    analysis_frames = output_frame_map(analysis.get("frames") or [])
    out_dir = os.path.abspath(args.out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (frames_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    graded = []
    strip_paths = []
    for index, frame in enumerate(render.get("frames") or []):
        output_frame = frame.get("output_frame")
        src = require_file(resolve_path(render_preview_path(frame)), "render preview")
        analysis_frame = analysis_frames.get(output_frame)
        target_path = require_file(resolve_path((analysis_frame or {}).get("target_repo_path")), "target frame")
        source_img = Image.open(src).convert("RGB")
        target_img = Image.open(target_path).convert("RGB")
        if source_img.size != target_img.size:
            source_img = source_img.resize(target_img.size, Image.Resampling.BICUBIC)
        frame_requests = requests_by_output.get(output_frame, [])
        response_img, response_stats = apply_response(source_img, target_img, frame_requests, args)
        out_path = os.path.join(frames_dir, f"frame_{index:04d}.png")
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_response.png")
        response_img.save(out_path)
        labeled_strip([source_img, response_img, target_img], ["Source", "Signed Response", "Target"], strip_path)
        strip_paths.append(strip_path)
        graded.append({
            "frame": frame.get("frame", index),
            "output_frame": output_frame,
            "source_repo_path": posix_rel(src, root),
            "target_repo_path": posix_rel(target_path, root),
            "graded_repo_path": posix_rel(out_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "applied_requests": len(frame_requests),
            "response": response_stats,
            "size": os.path.getsize(out_path),
            "sha256": sha256_file(out_path),
        })

    if not graded:
        raise SystemExit("no frames were generated")

    gif_path = os.path.join(assets_dir, "response.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "response.gif", "Response GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"response_strip_{out_index:02d}.png", f"Response Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "signed_gap_response_summary.json")
    metadata_files = [
        copy_asset(analysis_path, assets_dir, "signed_target_gap_analysis.json", "Signed gap analysis", root),
        copy_asset(render_path, assets_dir, "render_manifest.json", "Render manifest", root),
    ]
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_composite_grade",
        "subschema": "lsfs_mitsuba_signed_gap_response",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "render_manifest": posix_rel(render_path, root),
            "signed_gap_analysis": posix_rel(analysis_path, root),
        },
        "settings": {
            "regions": sorted(parse_csv(args.regions)),
            "directions": sorted(parse_csv(args.directions)),
            "max_requests": args.max_requests,
            "min_score": args.min_score,
            "strength_scale": args.strength_scale,
            "max_strength": args.max_strength,
            "max_channel_delta": args.max_channel_delta,
            "feather_power": args.feather_power,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(graded),
            "selected_requests": len(selected_requests),
            "applied_requests": sum(item["applied_requests"] for item in graded),
            "max_changed_coverage": max(item["response"]["changed_coverage"] for item in graded),
            "max_channel_delta": max(item["response"]["max_channel_delta"] for item in graded),
            "mean_applied_abs_delta": (
                sum(item["response"]["mean_applied_abs_delta"] * item["response"]["changed_samples"] for item in graded) /
                float(max(1, sum(item["response"]["changed_samples"] for item in graded)))
            ),
            "gif_bytes": os.path.getsize(gif_path),
            "graded_frame_bytes": sum(item["size"] for item in graded),
        },
        "selected_requests": selected_requests,
        "gallery": {},
        "frames": graded,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "signed_gap_response_summary.json", "Response summary", root)
    metadata_files.insert(0, summary_asset)
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
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_signed_gap_response_gallery",
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
        f"status=ready frames={len(graded)} requests={summary['checks']['applied_requests']} "
        f"max_changed={summary['checks']['max_changed_coverage']:.6f} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply bounded response from signed Mitsuba target-gap requests")
    parser.add_argument("render_manifest")
    parser.add_argument("signed_gap_analysis")
    parser.add_argument("out_dir")
    parser.add_argument("--regions", default="highlight")
    parser.add_argument("--directions", default="brighten")
    parser.add_argument("--max-requests", type=int, default=8)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--strength-scale", type=float, default=0.35)
    parser.add_argument("--max-strength", type=float, default=0.35)
    parser.add_argument("--max-channel-delta", type=float, default=24.0)
    parser.add_argument("--feather-power", type=float, default=1.5)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Signed Gap Response")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Compare this signed response candidate against the target preview.")
    args = parser.parse_args(argv)
    if args.max_requests <= 0:
        parser.error("max-requests must be positive")
    if args.min_score < 0.0:
        parser.error("min-score must be non-negative")
    if args.strength_scale < 0.0:
        parser.error("strength-scale must be non-negative")
    if args.max_strength <= 0.0:
        parser.error("max-strength must be positive")
    if args.max_channel_delta <= 0.0:
        parser.error("max-channel-delta must be positive")
    if args.feather_power <= 0.0:
        parser.error("feather-power must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    build(args)


if __name__ == "__main__":
    main()
