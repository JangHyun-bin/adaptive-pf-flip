#!/usr/bin/env python
"""Consume visual-cache AOVs and reconstruct a standard composite summary."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
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
from validate_mitsuba_visual_cache_bundle import diff_stats, resolve_path


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to consume visual-cache AOVs")


def aov_path(frame, name):
    entry = ((frame.get("aovs") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
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


def reconstruct(base, response):
    return ImageChops.add(base.convert("RGB"), response.convert("RGB"))


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
    return strip


def html_page(title, summary, assets):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "AOV Consumer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("AOV Consumer Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Requests", checks.get("applied_requests")),
            ("Max diff", checks.get("max_import_abs_diff")),
            ("Mean diff", f"{checks.get('max_import_mean_abs_diff', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="AOV Consumer GIF"></section>' if gif else ""
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
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; }}
    p {{ margin: 0 0 16px; color: var(--muted); }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 18px; }}
    .hero {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; margin-bottom: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 6px; background: #0d1820; overflow: hidden; }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{title}</h1>
  <p>Reconstructs composites from imported visual-cache AOVs: base_rgb plus response_rgb.</p>
  <section class="tiles">{tiles}</section>
  {hero}
  <section class="grid">{figures}</section>
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
        f"- Applied requests: `{checks.get('applied_requests')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max import absolute diff: `{checks.get('max_import_abs_diff')}`",
        f"- Max import mean absolute diff: `{checks.get('max_import_mean_abs_diff')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Requests | Import Max Diff | Composite | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('applied_requests')} | "
            f"{frame.get('import_max_abs_diff')} | `{frame.get('composite_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def consume(args):
    require_pillow()
    root = os.getcwd()
    package_path = require_file(args.aov_summary, "visual-cache AOV summary")
    package = read_json(package_path)
    if package.get("schema") != "lsfs_mitsuba_visual_cache_aov_package":
        raise SystemExit(f"{args.aov_summary}: expected lsfs_mitsuba_visual_cache_aov_package schema")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    strip_dir = os.path.join(out_dir, "strips")
    frames = []
    strips = []
    missing = []
    for index, frame in enumerate(package.get("frames") or []):
        paths = {
            name: resolve_path(aov_path(frame, name), root)
            for name in ("base_rgb", "response_rgb", "composite_rgb", "target_rgb")
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        base = Image.open(paths["base_rgb"]).convert("RGB")
        response = Image.open(paths["response_rgb"]).convert("RGB")
        expected = Image.open(paths["composite_rgb"]).convert("RGB")
        target = Image.open(paths["target_rgb"]).convert("RGB")
        if any(img.size != base.size for img in (response, expected, target)):
            raise SystemExit(f"frame {index}: AOV dimensions differ")
        composite = reconstruct(base, response)
        stats = diff_stats(composite, expected)
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        os.makedirs(os.path.dirname(composite_path), exist_ok=True)
        composite.save(composite_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        labeled_strip([base, response, composite, expected, target, stats["diff_image"]], ["base", "response", "import", "expected", "target", "diff x8"], strip_path)
        strips.append(strip_path)
        response_stats = (frame.get("stats") or {})
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "source_repo_path": posix_rel(paths["base_rgb"], root),
            "response_repo_path": posix_rel(paths["response_rgb"], root),
            "target_repo_path": posix_rel(paths["target_rgb"], root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "applied_requests": frame.get("applied_requests"),
            "response": {
                "changed_coverage": response_stats.get("response_mask_coverage"),
                "max_layer_delta": response_stats.get("response_luma_max"),
                "requests": frame.get("applied_requests"),
            },
            "import_mean_abs_diff": stats["mean_abs_diff"],
            "import_max_abs_diff": stats["max_abs_diff"],
            "import_mismatched_coverage": stats["mismatched_coverage"],
        })

    if not frames:
        raise SystemExit("no AOV frames were consumed")
    gif_path = os.path.join(out_dir, "visual_cache_aov_consumer.gif")
    strip_images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in strips]
    strip_images[0].save(gif_path, save_all=True, append_images=strip_images[1:], duration=int(1000 / args.fps), loop=0)

    status = "ready"
    if missing:
        status = "failed"
    if max(frame["import_max_abs_diff"] for frame in frames) > args.max_abs_tolerance:
        status = "failed"
    if max(frame["import_mean_abs_diff"] for frame in frames) > args.mean_abs_tolerance:
        status = "failed"

    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    key_indices = sorted(set([0, len(strips) // 2, len(strips) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "visual_cache_aov_consumer.gif", "AOV Consumer GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"aov_consumer_strip_{out_index:02d}.png", f"AOV Consumer Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_visual_cache_aov_consumer",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "visual_cache_aov_package": {
            "path": package_path,
            "repo_path": posix_rel(package_path, root),
            "sha256": sha256_file(package_path),
            "schema": package.get("schema"),
            "status": package.get("status"),
        },
        "checks": {
            "frames": len(frames),
            "applied_requests": sum(int(frame.get("applied_requests") or 0) for frame in frames),
            "missing_references": len(missing),
            "max_import_abs_diff": max(frame["import_max_abs_diff"] for frame in frames),
            "max_import_mean_abs_diff": max(frame["import_mean_abs_diff"] for frame in frames),
            "max_import_mismatched_coverage": max(frame["import_mismatched_coverage"] for frame in frames),
            "max_changed_coverage": max((frame.get("response") or {}).get("changed_coverage") or 0.0 for frame in frames),
            "composite_bytes": sum(frame["size"] for frame in frames),
            "gif_bytes": os.path.getsize(gif_path),
            "max_abs_tolerance": args.max_abs_tolerance,
            "mean_abs_tolerance": args.mean_abs_tolerance,
        },
        "frames": frames,
        "missing_references": missing,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_visual_cache_aov_consumer_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={len(frames)} max_abs={summary['checks']['max_import_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consume visual-cache AOVs")
    parser.add_argument("aov_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="Mitsuba Visual Cache AOV Consumer")
    parser.add_argument(
        "--next",
        default="Use this AOV consumer as the import gate before moving the response contract into renderer-native controls.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    consume(args)


if __name__ == "__main__":
    main()
