#!/usr/bin/env python
"""Build a lightweight static gallery for preview-render outputs."""

import argparse
import html
import json
import os
import shutil
from datetime import datetime, timezone

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


def frame_paths(preview_dir):
    frames = []
    for name in sorted(os.listdir(preview_dir)):
        if name.lower().endswith(".png") and name.startswith("frame_"):
            frames.append(os.path.join(preview_dir, name))
    return frames


def select_evenly(items, count):
    if not items or count <= 0:
        return []
    if len(items) <= count:
        return list(items)
    selected = []
    for index in range(count):
        src_index = round(index * (len(items) - 1) / max(1, count - 1))
        selected.append(items[src_index])
    return selected


def copy_asset(src, assets_dir, asset_name, label):
    dest = os.path.join(assets_dir, asset_name)
    shutil.copy2(src, dest)
    dims = image_dimensions(dest)
    entry = {
        "label": label,
        "source": os.path.abspath(src),
        "asset": os.path.abspath(dest),
        "href": f"assets/{asset_name}",
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    if dims:
        entry["dimensions"] = dims
    return entry


def metric_tiles(summary):
    return [
        ("Status", "ok"),
        ("Renderer", summary.get("renderer")),
        ("Frames", summary.get("frame_count")),
        ("Resolution", f"{summary.get('width')} x {summary.get('height')}"),
        ("Secondary Channel", summary.get("secondary_channel")),
        ("Min Occupancy", summary.get("min_occupancy")),
        ("Water Reconstruction", bool(summary.get("water_reconstruction"))),
    ]


def html_page(title, summary, assets, metadata_href, manifest_href):
    gif = next((item for item in assets if item["label"] == "Shot GIF"), None)
    keyframes = [item for item in assets if item["label"].startswith("Keyframe")]
    metrics = "\n".join(
        f"<div class=\"metric\"><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metric_tiles(summary)
    )
    hero = ""
    if gif:
        hero = f"""
        <section class=\"hero\">
          <img src=\"{html.escape(gif['href'])}\" alt=\"Shot preview\">
        </section>"""
    frames = "\n".join(
        f"""
        <figure>
          <a href=\"{html.escape(item['href'])}\"><img src=\"{html.escape(item['href'])}\" alt=\"{html.escape(item['label'])}\"></a>
          <figcaption>{html.escape(item['label'])}</figcaption>
        </figure>"""
        for item in keyframes
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071018; --panel: #101922; --ink: #e7f3fb; --muted: #9fb4c3; --line: #263845; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 28px 20px 40px; }}
    header {{ display: flex; justify-content: space-between; gap: 20px; align-items: end; margin-bottom: 18px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    .links {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    a {{ color: #a8dcff; text-decoration: none; }}
    .hero {{ border: 1px solid var(--line); background: #05090d; }}
    .hero img {{ width: 100%; display: block; image-rendering: auto; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 16px 0 20px; }}
    .metric {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 62px; }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metric strong {{ font-size: 16px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{html.escape(title)}</h1>
      <nav class=\"links\">
        <a href=\"{html.escape(metadata_href)}\">Render summary</a>
        <a href=\"{html.escape(manifest_href)}\">Gallery manifest</a>
      </nav>
    </header>
    {hero}
    <section class=\"metrics\">{metrics}</section>
    <section class=\"grid\">{frames}</section>
  </main>
</body>
</html>
"""


def markdown_report(title, manifest, manifest_path, root, next_text):
    lines = [
        f"# {title}",
        "",
        f"Generated UTC: `{manifest['generated_utc']}`",
        f"Gallery directory: `{manifest['gallery_repo_path']}`",
        f"Manifest: `{posix_rel(manifest_path, root)}`",
        "",
        "## Assets",
        "",
        "| Asset | Size | Dimensions | Path |",
        "| --- | ---: | --- | --- |",
    ]
    for item in manifest.get("assets", []):
        dims = item.get("dimensions")
        dims_text = f"{dims[0]} x {dims[1]}" if dims else "n/a"
        lines.append(f"| {item['label']} | {format_bytes(item['size'])} | `{dims_text}` | `{item['repo_path']}` |")
    lines.extend([
        "",
        "## Metadata Files",
        "",
    ])
    for item in manifest.get("metadata_files", []):
        lines.append(f"- `{item['repo_path']}` ({format_bytes(item['size'])})")
    lines.extend([
        "",
        "## Next",
        "",
        next_text,
        "",
    ])
    return "\n".join(lines)


def build_gallery(args):
    root = os.getcwd()
    summary_path = require_file(args.render_summary, "render summary")
    gif_path = require_file(args.gif, "preview gif")
    preview_dir = os.path.abspath(args.preview_dir or os.path.dirname(summary_path))
    out_dir = os.path.abspath(args.out)
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    summary = read_json(summary_path)

    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Shot GIF")]
    for index, frame in enumerate(select_evenly(frame_paths(preview_dir), args.keyframes)):
        assets.append(copy_asset(frame, assets_dir, f"keyframe_{index:02d}.png", f"Keyframe {index + 1}"))

    summary_asset = os.path.join(assets_dir, "render_summary.json")
    shutil.copy2(summary_path, summary_asset)
    metadata = [{
        "label": "Render summary",
        "source": os.path.abspath(summary_path),
        "asset": os.path.abspath(summary_asset),
        "href": "assets/render_summary.json",
        "size": os.path.getsize(summary_asset),
        "sha256": sha256_file(summary_asset),
        "repo_path": posix_rel(summary_asset, root),
    }]
    index_path = os.path.join(out_dir, "index.html")
    manifest_path = os.path.join(out_dir, "gallery_manifest.json")

    manifest = {
        "schema": "lsfs_preview_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "gallery_path": out_dir,
        "gallery_repo_path": posix_rel(out_dir, root),
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": [{**item, "repo_path": posix_rel(item["asset"], root)} for item in assets],
        "metadata_files": metadata,
        "summary": {
            "renderer": summary.get("renderer"),
            "frame_count": summary.get("frame_count"),
            "width": summary.get("width"),
            "height": summary.get("height"),
            "min_occupancy": summary.get("min_occupancy"),
            "secondary_channel": summary.get("secondary_channel"),
        },
    }
    write_text(index_path, html_page(args.title, summary, manifest["assets"], "assets/render_summary.json", "gallery_manifest.json"))
    write_json(manifest_path, manifest)
    if args.report:
        write_text(args.report, markdown_report(args.title, manifest, manifest_path, root, args.next))
    return manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a lightweight preview gallery")
    parser.add_argument("--render-summary", required=True)
    parser.add_argument("--gif", required=True)
    parser.add_argument("--preview-dir")
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="Preview Gallery")
    parser.add_argument("--keyframes", type=int, default=8)
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this gallery for lightweight visual review.")
    args = parser.parse_args(argv)
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    manifest_path = build_gallery(args)
    print(f"status=ok gallery={os.path.dirname(manifest_path)} manifest={manifest_path}")


if __name__ == "__main__":
    main()
