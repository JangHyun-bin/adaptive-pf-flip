#!/usr/bin/env python
"""Build renderer-side target previews from a Mitsuba handoff bundle."""

import argparse
import math
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageEnhance = None
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
        raise SystemExit("Pillow is required to build renderer target previews")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def reference_path(frame, role):
    ref = ((frame.get("references") or {}).get(role) or {})
    return ref.get("repo_path") or ref.get("source_repo_path")


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


def parse_rgb(value, default):
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(max(0, min(255, int(item))) for item in value)
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
        if len(parts) == 3:
            return tuple(max(0, min(255, int(part))) for part in parts)
    return default


def luminance_mask(img, threshold, blur_radius):
    gray = ImageOps.grayscale(img)
    mask = gray.point(lambda value: max(0, min(255, int((value - threshold) * 255 / max(1, 255 - threshold)))))
    return mask.filter(ImageFilter.GaussianBlur(blur_radius))


def add_bloom(img, threshold, blur_radius, strength):
    if strength <= 0.0:
        return img
    mask = luminance_mask(img, threshold, blur_radius)
    glow = Image.new("RGB", img.size, (255, 255, 255))
    glow.putalpha(mask.point(lambda value: int(value * strength)))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def apply_tone(img, tone_rgb, strength):
    if strength <= 0.0:
        return img
    tone = Image.new("RGB", img.size, tone_rgb)
    toned = ImageChops.multiply(img, tone)
    return Image.blend(img, toned, strength)


def apply_vignette(img, strength, power):
    if strength <= 0.0:
        return img
    width, height = img.size
    mask = Image.new("L", img.size, 0)
    pixels = mask.load()
    cx = (width - 1) * 0.5
    cy = (height - 1) * 0.5
    max_dist = math.sqrt(cx * cx + cy * cy)
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max(1.0, max_dist)
            pixels[x, y] = int(max(0.0, min(1.0, dist ** power * strength)) * 255)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay.putalpha(mask.filter(ImageFilter.GaussianBlur(max(1, int(min(width, height) * 0.035)))))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def grade_image(img, settings):
    out = img.convert("RGB")
    cutoff = float(settings.get("autocontrast_cutoff", 0.0) or 0.0)
    if cutoff > 0.0:
        out = ImageOps.autocontrast(out, cutoff=cutoff)
    out = ImageEnhance.Brightness(out).enhance(float(settings.get("exposure", 1.0) or 1.0))
    out = ImageEnhance.Contrast(out).enhance(float(settings.get("contrast", 1.0) or 1.0))
    out = ImageEnhance.Color(out).enhance(float(settings.get("saturation", 1.0) or 1.0))
    out = apply_tone(out, parse_rgb(settings.get("tone_rgb"), (255, 255, 255)), float(settings.get("tone_strength", 0.0) or 0.0))
    out = add_bloom(
        out,
        int(settings.get("bloom_threshold", 255) or 255),
        float(settings.get("bloom_radius", 0.0) or 0.0),
        float(settings.get("bloom_strength", 0.0) or 0.0),
    )
    out = apply_vignette(
        out,
        float(settings.get("vignette_strength", 0.0) or 0.0),
        float(settings.get("vignette_power", 1.0) or 1.0),
    )
    return ImageEnhance.Sharpness(out).enhance(float(settings.get("sharpness", 1.0) or 1.0))


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


def diff_image(a, b):
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return ImageOps.autocontrast(diff)


def layer_panel(layer, background):
    checker = Image.new("RGBA", layer.size, background)
    return Image.alpha_composite(checker, layer.convert("RGBA")).convert("RGB")


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (12, 18, 24))
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
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Target GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Composite MAD", f"{checks.get('max_composite_mean_abs_diff', 0.0):.4f}"),
        ("Target MAD", f"{checks.get('max_target_mean_abs_diff', 0.0):.4f}"),
        ("Missing", checks.get("missing_references")),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
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
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Renderer target GIF"></section>' if gif else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #10191f; --ink: #ecf7fb; --muted: #9fb2bc; --line: #2d3d47; --accent: #9ed8ff; }}
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


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks", {})
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
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max composite mean abs diff: `{checks.get('max_composite_mean_abs_diff')}`",
        f"- Max target mean abs diff: `{checks.get('max_target_mean_abs_diff')}`",
        f"- Max target max abs diff: `{checks.get('max_target_max_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Composite MAD | Target MAD | Strip |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('composite_mean_abs_diff'):.4f} | {frame.get('target_mean_abs_diff'):.4f} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build_preview(args):
    require_pillow()
    root = os.getcwd()
    bundle_path = require_file(args.handoff_manifest, "handoff bundle")
    bundle = read_json(bundle_path)
    if bundle.get("schema") != "lsfs_mitsuba_renderer_handoff_bundle":
        raise SystemExit(f"{args.handoff_manifest}: expected lsfs_mitsuba_renderer_handoff_bundle schema")
    if bundle.get("status") != "ready":
        raise SystemExit(f"{args.handoff_manifest}: bundle status is {bundle.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    secondary_dir = os.path.join(out_dir, "renderer_secondary")
    target_dir = os.path.join(out_dir, "renderer_target")
    diff_dir = os.path.join(out_dir, "diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (secondary_dir, target_dir, diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    settings = (((bundle.get("look_intent") or {}).get("grade") or {}).get("settings") or {})
    frame_results = []
    target_paths = []
    missing = []
    for index, frame in enumerate(bundle.get("frames") or []):
        refs = {role: resolve_path(reference_path(frame, role)) for role in ("base_preview", "secondary_layer", "composite", "graded")}
        absent = [role for role, path in refs.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "missing_roles": absent})
            continue

        base = Image.open(refs["base_preview"]).convert("RGBA")
        layer = Image.open(refs["secondary_layer"]).convert("RGBA")
        if layer.size != base.size:
            layer = layer.resize(base.size, Image.Resampling.BICUBIC)
        renderer_secondary = Image.alpha_composite(base, layer).convert("RGB")
        renderer_target = grade_image(renderer_secondary, settings)
        composite_reference = Image.open(refs["composite"]).convert("RGB")
        graded_reference = Image.open(refs["graded"]).convert("RGB")
        if composite_reference.size != renderer_secondary.size:
            composite_reference = composite_reference.resize(renderer_secondary.size, Image.Resampling.BICUBIC)
        if graded_reference.size != renderer_target.size:
            graded_reference = graded_reference.resize(renderer_target.size, Image.Resampling.BICUBIC)

        base_name = f"frame_{index:04d}.png"
        secondary_path = os.path.join(secondary_dir, base_name)
        target_path = os.path.join(target_dir, base_name)
        diff_path = os.path.join(diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        renderer_secondary.save(secondary_path)
        renderer_target.save(target_path)
        diff_image(renderer_target, graded_reference).save(diff_path)
        labeled_strip(
            [
                base.convert("RGB"),
                layer_panel(layer, (20, 30, 38, 255)),
                renderer_secondary,
                renderer_target,
                graded_reference,
                Image.open(diff_path).convert("RGB"),
            ],
            ["base", "secondary layer", "renderer secondary", "renderer target", "graded reference", "target diff"],
            strip_path,
        )
        target_paths.append(target_path)
        frame_results.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "particles_projected": frame.get("particles_projected"),
            "layer_coverage": frame.get("layer_coverage"),
            "renderer_secondary_repo_path": posix_rel(secondary_path, root),
            "renderer_target_repo_path": posix_rel(target_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "renderer_target_sha256": sha256_file(target_path),
            "composite_mean_abs_diff": mean_abs_diff(renderer_secondary, composite_reference),
            "composite_max_abs_diff": max_abs_diff(renderer_secondary, composite_reference),
            "target_mean_abs_diff": mean_abs_diff(renderer_target, graded_reference),
            "target_max_abs_diff": max_abs_diff(renderer_target, graded_reference),
        })

    if not frame_results:
        raise SystemExit("no frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(target_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Target GIF", root)]
    key_indices = sorted(set(round(i * (len(frame_results) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        frame = frame_results[frame_index]
        assets.append(copy_asset(frame["strip_repo_path"], assets_dir, f"strip_{out_index:02d}.png", f"Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "renderer_target_preview_summary.json")
    bundle_asset = copy_asset(bundle_path, assets_dir, "handoff_manifest.json", "Handoff manifest", root)
    metadata_files = [bundle_asset]
    checks = {
        "frames": len(frame_results),
        "missing_references": len(missing),
        "gif_bytes": os.path.getsize(gif_path),
        "max_composite_mean_abs_diff": max(item["composite_mean_abs_diff"] for item in frame_results),
        "max_composite_max_abs_diff": max(item["composite_max_abs_diff"] for item in frame_results),
        "max_target_mean_abs_diff": max(item["target_mean_abs_diff"] for item in frame_results),
        "max_target_max_abs_diff": max(item["target_max_abs_diff"] for item in frame_results),
    }
    status = "ready" if not missing and checks["max_target_mean_abs_diff"] <= args.max_mean_abs_diff else "review"
    summary = {
        "schema": "lsfs_mitsuba_renderer_target_preview",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source": {
            "handoff_manifest": posix_rel(bundle_path, root),
            "public_reference": bundle.get("public_reference", {}),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
            "max_mean_abs_diff": args.max_mean_abs_diff,
            "grade": settings,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": frame_results,
        "gallery": {},
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "renderer_target_preview_summary.json", "Target preview summary", root)
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
        "schema": "lsfs_mitsuba_renderer_target_preview_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={status} frames={checks['frames']} max_target_mad={checks['max_target_mean_abs_diff']:.6f} "
        f"gif={gif_path} summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build renderer target previews from a Mitsuba handoff bundle")
    parser.add_argument("handoff_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-mean-abs-diff", type=float, default=0.75)
    parser.add_argument("--fail-on-review", action="store_true")
    parser.add_argument("--title", default="Mitsuba Renderer Target Preview")
    parser.add_argument("--report")
    parser.add_argument(
        "--next",
        default="Use this preview as the target reference while moving secondary and grade work into renderer-side implementations.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_mean_abs_diff < 0.0:
        parser.error("max-mean-abs-diff must be non-negative")
    build_preview(args)


if __name__ == "__main__":
    main()
