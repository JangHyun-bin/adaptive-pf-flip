#!/usr/bin/env python
"""Apply a bounded target-region response to Mitsuba composite frames."""

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
        raise SystemExit("Pillow is required to apply target-region response")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def target_path(frame):
    return frame.get("renderer_target_path") or frame.get("renderer_target_repo_path")


def composite_path(frame):
    return frame.get("composite_path") or frame.get("composite_repo_path")


def layer_path(frame):
    return frame.get("layer_path") or frame.get("layer_repo_path")


def luminance_from_rgb(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def clamp(value):
    return max(0, min(255, int(round(value))))


def blend_to_target(value, target, strength, max_delta):
    delta = (target - value) * strength
    if max_delta > 0.0:
        delta = max(-max_delta, min(max_delta, delta))
    return value + delta


def apply_response(actual_img, target_img, layer_img, args):
    actual_bytes = actual_img.convert("RGB").tobytes()
    target_bytes = target_img.convert("RGB").tobytes()
    alpha_bytes = layer_img.convert("RGBA").split()[3].tobytes()
    out = bytearray(len(actual_bytes))
    stats = {
        "pixels": len(alpha_bytes),
        "highlight_pixels": 0,
        "dark_secondary_pixels": 0,
        "nonsecondary_pixels": 0,
        "changed_pixels": 0,
    }
    for pixel_index, alpha in enumerate(alpha_bytes):
        base = pixel_index * 3
        ar, ag, ab = actual_bytes[base], actual_bytes[base + 1], actual_bytes[base + 2]
        tr, tg, tb = target_bytes[base], target_bytes[base + 1], target_bytes[base + 2]
        nr, ng, nb = float(ar), float(ag), float(ab)
        target_luma = luminance_from_rgb(tr, tg, tb)
        is_secondary = alpha >= args.secondary_alpha_threshold
        is_highlight = target_luma >= args.highlight_luma_threshold
        is_dark_secondary = is_secondary and target_luma <= args.dark_luma_threshold
        if not is_secondary and args.nonsecondary_lift != 0.0:
            nr += args.nonsecondary_lift
            ng += args.nonsecondary_lift
            nb += args.nonsecondary_lift
            stats["nonsecondary_pixels"] += 1
        if is_highlight and args.highlight_strength > 0.0:
            nr = blend_to_target(nr, tr, args.highlight_strength, args.highlight_max_delta)
            ng = blend_to_target(ng, tg, args.highlight_strength, args.highlight_max_delta)
            nb = blend_to_target(nb, tb, args.highlight_strength, args.highlight_max_delta)
            stats["highlight_pixels"] += 1
        if is_dark_secondary and args.dark_secondary_strength > 0.0:
            nr = blend_to_target(nr, tr, args.dark_secondary_strength, args.dark_secondary_max_delta)
            ng = blend_to_target(ng, tg, args.dark_secondary_strength, args.dark_secondary_max_delta)
            nb = blend_to_target(nb, tb, args.dark_secondary_strength, args.dark_secondary_max_delta)
            stats["dark_secondary_pixels"] += 1
        rr, gg, bb = clamp(nr), clamp(ng), clamp(nb)
        out[base], out[base + 1], out[base + 2] = rr, gg, bb
        if rr != ar or gg != ag or bb != ab:
            stats["changed_pixels"] += 1
    image = Image.frombytes("RGB", actual_img.size, bytes(out))
    stats["highlight_coverage"] = stats["highlight_pixels"] / float(max(1, stats["pixels"]))
    stats["dark_secondary_coverage"] = stats["dark_secondary_pixels"] / float(max(1, stats["pixels"]))
    stats["nonsecondary_coverage"] = stats["nonsecondary_pixels"] / float(max(1, stats["pixels"]))
    stats["changed_coverage"] = stats["changed_pixels"] / float(max(1, stats["pixels"]))
    return image, stats


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    dims = image_dimensions(dest)
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
    if dims:
        entry["dimensions"] = dims
    return entry


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


def write_gif(frame_paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    try:
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def html_page(title, assets, metadata_files, summary):
    gif = next((item for item in assets if item["label"] == "Shot GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary["checks"]
    metrics = [
        ("Frames", checks.get("frames")),
        ("Changed", f"{checks.get('max_changed_coverage', 0.0):.4f}"),
        ("Highlight", f"{checks.get('max_highlight_coverage', 0.0):.4f}"),
        ("Dark Sec", f"{checks.get('max_dark_secondary_coverage', 0.0):.4f}"),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    figures = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Response GIF"></section>' if gif else ""
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
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 16px 0; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ font-size: 18px; }}
    .grid {{ display: grid; gap: 12px; margin-top: 14px; }}
    figure {{ margin: 0; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 9px 10px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section class="grid">{figures}</section>
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
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Settings",
        "",
    ]
    for key, value in summary.get("settings", {}).items():
        lines.append(f"- {key}: `{value}`")
    checks = summary.get("checks", {})
    lines.extend([
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Max highlight coverage: `{checks.get('max_highlight_coverage')}`",
        f"- Max dark secondary coverage: `{checks.get('max_dark_secondary_coverage')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Changed | Highlight | Dark Secondary | Graded |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        response = frame.get("response", {})
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {response.get('changed_coverage')} | "
            f"{response.get('highlight_coverage')} | {response.get('dark_secondary_coverage')} | "
            f"`{frame.get('graded_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def apply_target_response(args):
    require_pillow()
    root = os.getcwd()
    target_summary_path = require_file(args.target_summary, "target summary")
    composite_summary_path = require_file(args.composite_summary, "composite summary")
    target_summary = read_json(target_summary_path)
    composite_summary = read_json(composite_summary_path)
    if composite_summary.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.composite_summary}: expected lsfs_mitsuba_secondary_composite schema")
    target_frames = output_frame_map(target_summary.get("frames") or [])
    composite_frames = output_frame_map(composite_summary.get("frames") or [])
    out_dir = os.path.abspath(args.out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    results = []
    frame_paths = []
    strip_paths = []
    for index, output_frame in enumerate(sorted(set(target_frames) & set(composite_frames))):
        target_frame = target_frames[output_frame]
        composite_frame = composite_frames[output_frame]
        target_img_path = require_file(target_path(target_frame), "target frame")
        actual_img_path = require_file(composite_path(composite_frame), "composite frame")
        layer_img_path = require_file(layer_path(composite_frame), "secondary layer")
        target_img = Image.open(target_img_path).convert("RGB")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if target_img.size != actual_img.size or target_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        graded_img, response = apply_response(actual_img, target_img, layer_img, args)
        out_path = os.path.join(frames_dir, f"frame_{index:04d}.png")
        graded_img.save(out_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_response.png")
        labeled_strip([target_img, actual_img, graded_img, layer_img.convert("RGB")], ["Target", "Source", "Response", "Layer"], strip_path)
        frame_paths.append(out_path)
        strip_paths.append(strip_path)
        results.append({
            "frame": index,
            "output_frame": output_frame,
            "source_repo_path": posix_rel(actual_img_path, root),
            "target_repo_path": posix_rel(target_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "graded_repo_path": posix_rel(out_path, root),
            "graded_sha256": sha256_file(out_path),
            "size": os.path.getsize(out_path),
            "response": response,
        })

    if not results:
        raise SystemExit("no overlapping output frames to process")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(frame_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Shot GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"strip_{out_index:02d}.png", f"Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "target_region_response_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_composite_grade",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "target_summary": posix_rel(target_summary_path, root),
            "composite_summary": posix_rel(composite_summary_path, root),
        },
        "settings": {
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_luma_threshold": args.highlight_luma_threshold,
            "dark_luma_threshold": args.dark_luma_threshold,
            "nonsecondary_lift": args.nonsecondary_lift,
            "highlight_strength": args.highlight_strength,
            "highlight_max_delta": args.highlight_max_delta,
            "dark_secondary_strength": args.dark_secondary_strength,
            "dark_secondary_max_delta": args.dark_secondary_max_delta,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(results),
            "gif_bytes": os.path.getsize(gif_path),
            "max_changed_coverage": max((item["response"].get("changed_coverage") or 0.0 for item in results), default=0.0),
            "max_highlight_coverage": max((item["response"].get("highlight_coverage") or 0.0 for item in results), default=0.0),
            "max_dark_secondary_coverage": max((item["response"].get("dark_secondary_coverage") or 0.0 for item in results), default=0.0),
        },
        "frames": results,
        "gallery": {},
        "next": args.next,
    }
    metadata_files = [
        copy_asset(composite_summary_path, assets_dir, "composite_summary.json", "Composite summary", root),
        copy_asset(target_summary_path, assets_dir, "target_summary.json", "Target summary", root),
    ]
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
    summary_asset = copy_asset(summary_path, assets_dir, "target_region_response_summary.json", "Response summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, summary["gallery"]["metadata_files"], summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_target_region_response_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": summary["gallery"]["metadata_files"],
        "summary_repo_path": posix_rel(summary_path, root),
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(results)} changed={summary['checks']['max_changed_coverage']:.6f} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply target-informed bounded region response to Mitsuba composites")
    parser.add_argument("target_summary")
    parser.add_argument("composite_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-luma-threshold", type=float, default=150.0)
    parser.add_argument("--dark-luma-threshold", type=float, default=55.0)
    parser.add_argument("--nonsecondary-lift", type=float, default=0.0)
    parser.add_argument("--highlight-strength", type=float, default=0.0)
    parser.add_argument("--highlight-max-delta", type=float, default=80.0)
    parser.add_argument("--dark-secondary-strength", type=float, default=0.0)
    parser.add_argument("--dark-secondary-max-delta", type=float, default=80.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Target Region Response")
    parser.add_argument("--next", default="Compare this target-region response against the renderer target gap.")
    args = parser.parse_args(argv)
    if not (0 <= args.secondary_alpha_threshold <= 255):
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if not (0.0 <= args.highlight_luma_threshold <= 255.0):
        parser.error("highlight-luma-threshold must be in [0, 255]")
    if not (0.0 <= args.dark_luma_threshold <= 255.0):
        parser.error("dark-luma-threshold must be in [0, 255]")
    if not (0.0 <= args.highlight_strength <= 1.0):
        parser.error("highlight-strength must be in [0, 1]")
    if not (0.0 <= args.dark_secondary_strength <= 1.0):
        parser.error("dark-secondary-strength must be in [0, 1]")
    if args.highlight_max_delta < 0.0:
        parser.error("highlight-max-delta must be non-negative")
    if args.dark_secondary_max_delta < 0.0:
        parser.error("dark-secondary-max-delta must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    apply_target_response(args)


if __name__ == "__main__":
    main()
