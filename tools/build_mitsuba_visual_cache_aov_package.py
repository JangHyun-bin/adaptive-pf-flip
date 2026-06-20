#!/usr/bin/env python
"""Export visual-cache signed response layers as renderer-importable AOVs."""

import argparse
import csv
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageStat
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
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
from validate_mitsuba_visual_cache_bundle import reference_path, resolve_path


AOV_NAMES = [
    "base_luma",
    "target_luma",
    "composite_luma",
    "response_rgb",
    "response_alpha",
    "response_luma",
    "response_mask",
    "target_gap_diff",
    "response_overlay",
]


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build visual-cache AOVs")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


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


def layer_mask(alpha):
    return alpha.point(lambda value: 255 if value > 0 else 0)


def response_overlay(base, layer):
    overlay = base.convert("RGB").copy()
    rgb = layer.convert("RGB")
    alpha = layer.getchannel("A")
    bright = ImageChops.add(overlay, rgb)
    return Image.composite(bright, overlay, alpha)


def labeled_grid(panels, labels, out_path, columns=3):
    if not panels:
        raise ValueError("no panels")
    width, height = panels[0].size
    label_h = 28
    columns = max(1, int(columns))
    rows = (len(panels) + columns - 1) // columns
    grid = Image.new("RGB", (width * columns, (height + label_h) * rows), (8, 13, 18))
    draw = ImageDraw.Draw(grid)
    for index, panel in enumerate(panels):
        col = index % columns
        row = index // columns
        x = col * width
        y = row * (height + label_h)
        draw.rectangle((x, y, x + width, y + label_h), fill=(18, 28, 36))
        draw.text((x + 8, y + 8), labels[index], fill=(230, 242, 248))
        grid.paste(panel.convert("RGB"), (x, y + label_h))
    ensure_dir(os.path.dirname(out_path))
    grid.save(out_path)
    return grid.size


def image_stats(gray, mask):
    stat = ImageStat.Stat(gray)
    mask_stat = ImageStat.Stat(mask)
    pixels = max(1, gray.size[0] * gray.size[1])
    covered = int(round(mask_stat.sum[0] / 255.0))
    return {
        "mean": float(stat.mean[0]),
        "max": int(stat.extrema[0][1]),
        "coverage": covered / float(pixels),
        "covered_pixels": covered,
    }


def write_csv_file(path, rows):
    ensure_dir(os.path.dirname(path))
    fields = [
        "frame",
        "output_frame",
        "applied_requests",
        "response_alpha_mean",
        "response_alpha_max",
        "response_mask_coverage",
        "response_luma_mean",
        "response_luma_max",
        "response_luma_covered_pixels",
        "source_gap_mad",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Visual Cache AOV GIF"), None)
    grids = [item for item in assets if item["label"].startswith("AOV Grid")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("AOVs", checks.get("aovs_per_frame")),
            ("Coverage", f"{checks.get('max_response_mask_coverage', 0.0):.6f}"),
            ("Alpha", checks.get("max_response_alpha")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Visual Cache AOV GIF"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in grids
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


def markdown_report(summary, summary_path, root, next_text):
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
        f"- AOVs per frame: `{checks.get('aovs_per_frame')}`",
        f"- Max response mask coverage: `{checks.get('max_response_mask_coverage')}`",
        f"- Max response alpha: `{checks.get('max_response_alpha')}`",
        f"- Max response luma: `{checks.get('max_response_luma')}`",
        f"- Max source target-gap MAD: `{checks.get('max_source_gap_mad')}`",
        f"- AOV bytes: `{format_bytes(checks.get('aov_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## AOVs",
        "",
    ]
    for aov in summary.get("aovs") or []:
        lines.append(f"- `{aov}`")
    lines.extend(["", "## Frame Samples", "", "| Frame | Output | Coverage | Alpha Max | Grid |", "| ---: | ---: | ---: | ---: | --- |"])
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        stats = frame.get("stats") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {stats.get('response_mask_coverage')} | "
            f"{stats.get('response_alpha_max')} | `{frame.get('grid_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    bundle_path = require_file(args.bundle_manifest, "visual cache bundle manifest")
    bundle = read_json(bundle_path)
    if bundle.get("schema") != "lsfs_mitsuba_visual_cache_bundle":
        raise SystemExit(f"{args.bundle_manifest}: expected lsfs_mitsuba_visual_cache_bundle schema")

    out_dir = os.path.abspath(args.out_dir)
    aov_dir = ensure_dir(os.path.join(out_dir, "aovs"))
    grid_dir = ensure_dir(os.path.join(out_dir, "grids"))
    gallery_dir = ensure_dir(os.path.join(out_dir, "gallery"))
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    frame_records = []
    csv_rows = []
    grid_paths = []
    missing = []

    for index, frame in enumerate(bundle.get("frames") or []):
        paths = {
            role: resolve_path(reference_path(frame, role), root)
            for role in ("base_render", "signed_response_layer", "signed_composite", "accepted_target", "target_gap_diff")
        }
        absent = [role for role, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue

        base = Image.open(paths["base_render"]).convert("RGB")
        layer = Image.open(paths["signed_response_layer"]).convert("RGBA")
        composite = Image.open(paths["signed_composite"]).convert("RGB")
        target = Image.open(paths["accepted_target"]).convert("RGB")
        diff = Image.open(paths["target_gap_diff"]).convert("RGB")
        if any(img.size != base.size for img in (layer, composite, target, diff)):
            raise SystemExit(f"frame {index}: AOV source dimensions differ")

        alpha = layer.getchannel("A")
        response_rgb = layer.convert("RGB")
        response_luma = response_rgb.convert("L")
        mask = layer_mask(alpha)
        channels = {
            "base_luma": base.convert("L"),
            "target_luma": target.convert("L"),
            "composite_luma": composite.convert("L"),
            "response_rgb": response_rgb,
            "response_alpha": alpha,
            "response_luma": response_luma,
            "response_mask": mask,
            "target_gap_diff": diff,
            "response_overlay": response_overlay(base, layer),
        }
        aovs = {}
        for name in AOV_NAMES:
            path = os.path.join(aov_dir, name, f"frame_{index:04d}_{name}.png")
            aovs[name] = save_image(channels[name], path, root)

        alpha_stats = image_stats(alpha, mask)
        luma_stats = image_stats(response_luma, mask)
        source_gap_mad = (frame.get("gap") or {}).get("gap_mean_abs_diff")
        stats = {
            "response_alpha_mean": alpha_stats["mean"],
            "response_alpha_max": alpha_stats["max"],
            "response_mask_coverage": alpha_stats["coverage"],
            "response_luma_mean": luma_stats["mean"],
            "response_luma_max": luma_stats["max"],
            "response_luma_covered_pixels": luma_stats["covered_pixels"],
            "source_gap_mad": source_gap_mad,
        }
        grid_path = os.path.join(grid_dir, f"frame_{index:04d}_visual_cache_aov.png")
        labeled_grid(
            [base, target, composite, response_rgb, alpha.convert("RGB"), response_luma.convert("RGB"), mask.convert("RGB"), diff, channels["response_overlay"]],
            ["base", "target", "composite", "response rgb", "alpha", "response luma", "mask", "target gap diff", "overlay"],
            grid_path,
            columns=3,
        )
        grid_paths.append(grid_path)
        record = {
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "applied_requests": frame.get("applied_requests"),
            "aovs": aovs,
            "stats": stats,
            "grid_path": grid_path,
            "grid_repo_path": posix_rel(grid_path, root),
        }
        frame_records.append(record)
        csv_rows.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "applied_requests": frame.get("applied_requests"),
            **stats,
        })

    if not frame_records:
        raise SystemExit("no visual-cache AOV frames were built")

    csv_path = os.path.abspath(args.csv or os.path.join(out_dir, "visual_cache_aov_stats.csv"))
    write_csv_file(csv_path, csv_rows)
    gif_path = os.path.join(out_dir, "visual_cache_aov.gif")
    gif_images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in grid_paths]
    gif_images[0].save(gif_path, save_all=True, append_images=gif_images[1:], duration=int(1000 / args.fps), loop=0)

    key_indices = sorted(set([0, len(grid_paths) // 2, len(grid_paths) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "visual_cache_aov.gif", "Visual Cache AOV GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(grid_paths[frame_index], assets_dir, f"aov_grid_{out_index:02d}.png", f"AOV Grid {out_index + 1}", root))
    metadata_files = [
        copy_asset(bundle_path, assets_dir, "visual_cache_bundle_manifest.json", "Visual cache bundle", root),
        copy_asset(csv_path, assets_dir, "visual_cache_aov_stats.csv", "AOV stats CSV", root),
    ]
    status = "ready" if not missing else "failed"
    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    aov_bytes = sum(
        aov.get("size", 0)
        for frame in frame_records
        for aov in (frame.get("aovs") or {}).values()
    )
    checks = {
        "frames": len(frame_records),
        "aovs_per_frame": len(AOV_NAMES),
        "missing_references": len(missing),
        "max_response_mask_coverage": max((frame["stats"]["response_mask_coverage"] for frame in frame_records), default=0.0),
        "max_response_alpha": max((frame["stats"]["response_alpha_max"] for frame in frame_records), default=0),
        "max_response_luma": max((frame["stats"]["response_luma_max"] for frame in frame_records), default=0),
        "max_source_gap_mad": max((frame["stats"]["source_gap_mad"] or 0.0 for frame in frame_records), default=0.0),
        "aov_bytes": aov_bytes,
        "gif_bytes": os.path.getsize(gif_path),
    }
    summary = {
        "schema": "lsfs_mitsuba_visual_cache_aov_package",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "visual_cache_bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "sha256": sha256_file(bundle_path),
            "schema": bundle.get("schema"),
            "status": bundle.get("status"),
            "profile": bundle.get("profile"),
        },
        "aovs": AOV_NAMES,
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
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "visual_cache_aov_summary.json", "AOV summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_visual_cache_aov_package_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={status} frames={checks['frames']} aovs={checks['aovs_per_frame']} "
        f"max_coverage={checks['max_response_mask_coverage']:.6f} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a visual-cache AOV package")
    parser.add_argument("bundle_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--csv")
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--title", default="Mitsuba Visual Cache AOV Package")
    parser.add_argument(
        "--next",
        default="Use these visual-cache AOVs as the renderer/import contract for native response or compositor integration.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    build(args)


if __name__ == "__main__":
    main()
