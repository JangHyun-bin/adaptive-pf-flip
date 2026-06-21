#!/usr/bin/env python
"""Promote a response-delta scale candidate into a reusable composite manifest."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
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
from compare_mitsuba_renderer_target_gap import max_abs_diff, mean_abs_diff, write_gif


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to promote a response-scale composite")


def resolve_path(path, root):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(root, str(path).replace("/", os.sep)))


def scale_key(value):
    return f"scale_{float(value):.3f}".replace(".", "p")


def best_scale(summary):
    best = (summary.get("scale_sweep") or {}).get("best") or {}
    if best.get("scale") is None:
        raise SystemExit("response summary does not contain a best scale")
    return float(best["scale"])


def row_map(summary, scale):
    rows = {}
    for row in ((summary.get("scale_sweep") or {}).get("rows") or []):
        if row.get("scale") == scale:
            rows[row.get("output_frame")] = row
    return rows


def copy_asset(src, assets_dir, name, label, root):
    dst = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)
    entry = {
        "label": label,
        "asset": dst,
        "repo_path": posix_rel(dst, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "sha256": sha256_file(dst),
        "size": os.path.getsize(dst),
    }
    dims = image_dimensions(dst)
    if dims:
        entry["dimensions"] = dims
    return entry


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


def diff_image(a, b):
    return ImageOps.autocontrast(ImageChops.difference(a.convert("RGB"), b.convert("RGB")))


def html_page(title, summary, assets, metadata_files):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Response Scale GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Response Scale Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Scale", summary.get("settings", {}).get("response_scale")),
            ("Frames", checks.get("frames")),
            ("Mean Delta", f"{checks.get('mean_abs_delta', 0.0):.3f}"),
            ("Max Delta", checks.get("max_abs_delta")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="response scale GIF"></section>' if gif else ""
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
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #111a21; --ink: #edf7fb; --muted: #a2b5bf; --line: #2e3d47; --accent: #9fd9ff; }}
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
        "## Inputs",
        "",
        f"- Response buffer: `{summary['response_delta_buffer']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Response scale: `{summary['settings']['response_scale']}`",
        f"- Mean abs delta: `{checks.get('mean_abs_delta')}`",
        f"- Max abs delta: `{checks.get('max_abs_delta')}`",
        f"- Changed channel fraction: `{checks.get('changed_channel_fraction')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Mean Delta | Max Delta | Composite | Strip |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        response = frame.get("response") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {response.get('mean_abs_delta')} | "
            f"{response.get('max_abs_delta')} | `{frame.get('composite_repo_path')}` | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    response_path = require_file(args.response_summary, "response delta buffer summary")
    response = read_json(response_path)
    if response.get("schema") != "lsfs_mitsuba_response_delta_buffer":
        raise SystemExit(f"{args.response_summary}: expected lsfs_mitsuba_response_delta_buffer schema")
    if response.get("status") != "ready":
        raise SystemExit(f"{args.response_summary}: response summary status is {response.get('status')!r}")

    scale = best_scale(response) if args.scale is None else float(args.scale)
    rows = row_map(response, scale)
    if not rows:
        raise SystemExit(f"scale {scale} was not found in response summary scale rows")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (composite_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    frames = []
    strips = []
    missing = []
    for index, frame in enumerate(response.get("frames") or []):
        output = frame.get("output_frame")
        row = rows.get(output)
        if not row:
            missing.append({"output_frame": output, "missing": ["scaled_row"]})
            continue
        paths = {
            "base": resolve_path(frame.get("base_repo_path"), root),
            "full": resolve_path(frame.get("full_repo_path"), root),
            "scaled": resolve_path(row.get("scaled_repo_path"), root),
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"output_frame": output, "missing": absent})
            continue
        base = Image.open(paths["base"]).convert("RGB")
        full = Image.open(paths["full"]).convert("RGB")
        scaled = Image.open(paths["scaled"]).convert("RGB")
        if full.size != scaled.size:
            scaled = scaled.resize(full.size, Image.Resampling.BICUBIC)
        if base.size != full.size:
            base = base.resize(full.size, Image.Resampling.BICUBIC)

        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        shutil.copy2(paths["scaled"], composite_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        labeled_strip(
            [base, full, scaled, diff_image(scaled, full)],
            ["base", "full", f"scale {scale:g}", "scaled-full diff"],
            strip_path,
        )
        strips.append(strip_path)
        scaled_full_mean = mean_abs_diff(scaled, full)
        scaled_full_max = max_abs_diff(scaled, full)
        frames.append({
            "frame": frame.get("sequence_frame"),
            "output_frame": output,
            "source_repo_path": frame.get("base_repo_path"),
            "target_repo_path": frame.get("full_repo_path"),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "response_scale": scale,
            "response": {
                "mean_abs_delta": row.get("gap_mean_abs_diff"),
                "max_abs_delta": row.get("gap_max_abs_diff"),
                "changed_coverage": frame.get("changed_channel_fraction"),
                "full_mean_abs_diff": scaled_full_mean,
                "full_max_abs_diff": scaled_full_max,
                "source_buffer_mean_abs_delta": frame.get("mean_abs_delta"),
                "source_buffer_max_abs_delta": frame.get("max_abs_delta"),
            },
        })

    if not frames:
        raise SystemExit("no response scale composites were generated")

    gif_path = os.path.join(out_dir, "response_scale_composite.gif")
    write_gif(strips, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strips) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "response_scale_composite.gif", "Response Scale GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"response_scale_strip_{out_index:02d}.png", f"Response Scale Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, args.summary_name)
    generated_utc = datetime.now(timezone.utc).isoformat()
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "mean_abs_delta": sum((frame.get("response") or {}).get("source_buffer_mean_abs_delta") or 0.0 for frame in frames) / len(frames),
        "max_abs_delta": max((frame.get("response") or {}).get("source_buffer_max_abs_delta") or 0 for frame in frames),
        "changed_channel_fraction": sum((frame.get("response") or {}).get("changed_coverage") or 0.0 for frame in frames) / len(frames),
        "max_scaled_full_mean_abs_diff": max((frame.get("response") or {}).get("full_mean_abs_diff") or 0.0 for frame in frames),
        "max_scaled_full_abs_diff": max((frame.get("response") or {}).get("full_max_abs_diff") or 0 for frame in frames),
        "composite_bytes": sum(frame.get("size", 0) for frame in frames),
        "gif_bytes": os.path.getsize(gif_path),
    }
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_response_scale_composite",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready" if not missing else "review",
        "response_delta_buffer": {
            "path": response_path,
            "repo_path": posix_rel(response_path, root),
            "sha256": sha256_file(response_path),
            "schema": response.get("schema"),
            "status": response.get("status"),
        },
        "settings": {
            "response_scale": scale,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "frames": frames,
        "missing_references": missing,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [copy_asset(summary_path, assets_dir, "secondary_composite_summary.json", "Response scale summary", root)]
    metadata_files.append(copy_asset(response_path, assets_dir, "response_delta_buffer_summary.json", "Response delta buffer", root))
    gallery_index = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": gallery_index,
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, metadata_files[0]["asset"])
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_response_scale_composite_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={summary['status']} frames={checks['frames']} scale={scale:g} "
        f"max_scaled_full_mad={checks['max_scaled_full_mean_abs_diff']:.6f} summary={summary_path}"
    )
    if summary["status"] not in ("ready", "review"):
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Promote a response delta scale to a composite manifest")
    parser.add_argument("response_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--scale", type=float, default=None, help="response scale to promote; defaults to summary best")
    parser.add_argument("--summary-name", default="response_scale_composite_summary.json")
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--title", default="Mitsuba Response Scale Composite")
    parser.add_argument(
        "--next",
        default="Compare this promoted response-scale composite against S577/S585 and then move the same control into an AOV export contract.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
