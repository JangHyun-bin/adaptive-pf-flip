#!/usr/bin/env python
"""Consume low-frequency parity textures and reconstruct standard composites."""

import argparse
import os
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
from build_mitsuba_low_frequency_parity_texture_package import (
    copy_asset,
    diff_stats,
    labeled_strip,
    reconstruct,
    write_gif,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to consume low-frequency parity texture packages")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def texture_path(frame, name):
    entry = ((frame.get("textures") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


def gray_preview(image):
    return ImageOps.colorize(image.convert("L"), black=(6, 12, 18), white=(255, 218, 120))


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Texture Consumer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Texture Consumer Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Max expected diff", checks.get("max_expected_abs_diff")),
            ("Mean expected diff", f"{checks.get('max_expected_mean_abs_diff', 0.0):.6f}"),
            ("Coverage", f"{checks.get('max_changed_coverage', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Texture consumer GIF"></section>' if gif else ""
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
    main {{ max-width: 1500px; margin: 0 auto; padding: 24px 18px 40px; }}
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
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max expected abs diff: `{checks.get('max_expected_abs_diff')}`",
        f"- Max expected mean diff: `{checks.get('max_expected_mean_abs_diff')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Max Delta | Expected Max Diff | Composite | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        response = frame.get("response") or {}
        expected = frame.get("expected") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {response.get('max_layer_delta')} | "
            f"{expected.get('max_abs_diff')} | `{frame.get('composite_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def consume(args):
    require_pillow()
    root = os.getcwd()
    package_path = require_file(args.texture_package_summary, "low-frequency parity texture package")
    package = read_json(package_path)
    if package.get("schema") != "lsfs_mitsuba_low_frequency_parity_texture_package":
        raise SystemExit(f"{args.texture_package_summary}: expected lsfs_mitsuba_low_frequency_parity_texture_package schema")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (composite_dir, strip_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    frames = []
    missing = []
    strip_paths = []
    for index, frame in enumerate(package.get("frames") or []):
        paths = {
            name: resolve_path(texture_path(frame, name), root)
            for name in (
                "base_rgb",
                "target_rgb",
                "parity_composite_rgb",
                "applied_positive_delta_rgb",
                "applied_negative_delta_rgb",
                "applied_magnitude_luma",
                "dark_damping_weight_luma",
            )
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue

        base = Image.open(paths["base_rgb"]).convert("RGB")
        target = Image.open(paths["target_rgb"]).convert("RGB")
        expected = Image.open(paths["parity_composite_rgb"]).convert("RGB")
        positive = Image.open(paths["applied_positive_delta_rgb"]).convert("RGB")
        negative = Image.open(paths["applied_negative_delta_rgb"]).convert("RGB")
        magnitude = Image.open(paths["applied_magnitude_luma"]).convert("L")
        damping = Image.open(paths["dark_damping_weight_luma"]).convert("L")
        if any(img.size != base.size for img in (target, expected, positive, negative, magnitude, damping)):
            raise SystemExit(f"frame {index}: texture dimensions differ")

        composite = reconstruct(base, positive, negative)
        expected_stats = diff_stats(composite, expected)
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        os.makedirs(os.path.dirname(composite_path), exist_ok=True)
        composite.save(composite_path)

        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_texture_consumer.png")
        labeled_strip(
            [base, positive, negative, composite, expected, target, gray_preview(magnitude), gray_preview(damping), expected_stats["diff_image"]],
            ["base", "positive", "negative", "consumer", "expected", "target", "magnitude", "damping", "expected diff x8"],
            strip_path,
        )
        strip_paths.append(strip_path)
        source_stats = frame.get("stats") or {}
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "source_repo_path": posix_rel(paths["base_rgb"], root),
            "target_repo_path": posix_rel(paths["target_rgb"], root),
            "positive_delta_repo_path": posix_rel(paths["applied_positive_delta_rgb"], root),
            "negative_delta_repo_path": posix_rel(paths["applied_negative_delta_rgb"], root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "response": {
                "changed_coverage": source_stats.get("changed_coverage"),
                "max_layer_delta": source_stats.get("max_abs_delta"),
                "mean_layer_delta": source_stats.get("mean_abs_delta"),
            },
            "expected": {
                "mean_abs_diff": expected_stats["mean_abs_diff"],
                "max_abs_diff": expected_stats["max_abs_diff"],
                "mismatched_coverage": expected_stats["mismatched_coverage"],
            },
        })

    if not frames:
        raise SystemExit("no texture package frames were consumed")
    gif_path = os.path.join(out_dir, "low_frequency_parity_texture_consumer.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "low_frequency_parity_texture_consumer.gif", "Texture Consumer GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"texture_consumer_strip_{out_index:02d}.png", f"Texture Consumer Strip {out_index + 1}", root))
    metadata_files = [copy_asset(package_path, assets_dir, "low_frequency_parity_texture_package_summary.json", "Texture package summary", root)]

    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "max_expected_abs_diff": max((frame["expected"]["max_abs_diff"] for frame in frames), default=0),
        "max_expected_mean_abs_diff": max((frame["expected"]["mean_abs_diff"] for frame in frames), default=0.0),
        "max_expected_mismatched_coverage": max((frame["expected"]["mismatched_coverage"] for frame in frames), default=0.0),
        "max_changed_coverage": max(((frame.get("response") or {}).get("changed_coverage") or 0.0 for frame in frames), default=0.0),
        "composite_bytes": sum(frame.get("size", 0) for frame in frames),
        "gif_bytes": os.path.getsize(gif_path),
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
    status = "ready"
    if missing:
        status = "failed"
    if checks["max_expected_abs_diff"] > args.max_abs_tolerance:
        status = "failed"
    if checks["max_expected_mean_abs_diff"] > args.mean_abs_tolerance:
        status = "failed"

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_low_frequency_parity_texture_consumer",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "low_frequency_texture_package": {
            "path": package_path,
            "repo_path": posix_rel(package_path, root),
            "sha256": sha256_file(package_path),
            "schema": package.get("schema"),
            "status": package.get("status"),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "frames": frames,
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
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "secondary_composite_summary.json", "Texture consumer summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_parity_texture_consumer_gallery",
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
        f"status={status} frames={checks['frames']} max_expected={checks['max_expected_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consume a Mitsuba low-frequency parity texture package")
    parser.add_argument("texture_package_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="S490 Mitsuba Low Frequency Parity Texture Consumer")
    parser.add_argument(
        "--next",
        default="Use this consumer as the import gate before moving the same texture contract into a native post-tonemap stage.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    consume(args)


if __name__ == "__main__":
    main()
