#!/usr/bin/env python
"""Build a lightweight static gallery from arbitrary image and metadata artifacts."""

import argparse
import html
import os
import re
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from build_bridge_review_package import (
    format_bytes,
    image_dimensions,
    posix_rel,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a static artifact gallery")


def slug(value):
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "artifact"


def parse_labeled_path(value):
    if "=" in value:
        label, path = value.split("=", 1)
        label = label.strip()
        path = path.strip()
    else:
        path = value.strip()
        label = os.path.splitext(os.path.basename(path))[0]
    if not label or not path:
        raise SystemExit(f"invalid labeled path: {value!r}")
    return label, path


def copy_file(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)


def asset_entry(src, dest, label, root, href):
    copy_file(src, dest)
    dims = image_dimensions(dest)
    entry = {
        "label": label,
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(os.path.abspath(src), root),
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": href,
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    if dims:
        entry["dimensions"] = dims
    return entry


def metadata_entry(src, dest, label, root, href):
    copy_file(src, dest)
    return {
        "label": label,
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(os.path.abspath(src), root),
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": href,
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }


def write_single_frame_gif(src, dest):
    require_pillow()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with Image.open(src) as image:
        image.convert("P", palette=Image.ADAPTIVE).save(dest, save_all=True, duration=1000, loop=0, optimize=False)


def html_page(title, assets, metadata_files):
    hero = next((item for item in assets if item.get("label") == "Shot GIF"), None)
    images = [item for item in assets if item.get("label") != "Shot GIF"]
    links = "\n".join(
        f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>'
        for item in metadata_files
    )
    metrics = [
        ("Status", "ready"),
        ("Images", len(images)),
        ("Metadata", len(metadata_files)),
        ("Hero bytes", format_bytes(hero.get("size", 0) if hero else 0)),
    ]
    metric_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metrics
    )
    hero_html = ""
    if hero:
        hero_html = f'<section class="hero"><img src="{html.escape(hero["href"])}" alt="{html.escape(hero["label"])}"></section>'
    image_html = "\n".join(
        f"""
        <figure>
          <a href="{html.escape(item['href'])}"><img src="{html.escape(item['href'])}" alt="{html.escape(item['label'])}"></a>
          <figcaption>{html.escape(item['label'])}</figcaption>
        </figure>"""
        for item in images
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #070c10; --panel: #101820; --line: #2b3942; --ink: #edf7fb; --muted: #9cadb7; --accent: #8bdcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1360px; margin: 0 auto; padding: 24px 18px 42px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111; margin-bottom: 14px; overflow: auto; }}
    .hero img {{ display: block; width: 100%; min-width: 920px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); overflow: auto; }}
    figure img {{ width: 100%; min-width: 920px; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
    {hero_html}
    <section class="metrics">{metric_html}</section>
    <section class="grid">{image_html}</section>
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
    lines.extend(["", "## Metadata Files", ""])
    for item in manifest.get("metadata_files", []):
        lines.append(f"- `{item['repo_path']}` ({format_bytes(item['size'])})")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build_gallery(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out)
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    image_inputs = [parse_labeled_path(value) for value in args.image]
    metadata_inputs = [parse_labeled_path(value) for value in args.metadata]
    if not image_inputs:
        raise SystemExit("at least one --image is required")

    assets = []
    first_label, first_path = image_inputs[0]
    first_image = require_file(first_path, first_label)
    gif_path = os.path.join(assets_dir, "shot.gif")
    write_single_frame_gif(first_image, gif_path)
    assets.append(asset_entry(gif_path, gif_path, "Shot GIF", root, "assets/shot.gif"))

    for index, (label, path) in enumerate(image_inputs):
        src = require_file(path, label)
        _base, ext = os.path.splitext(src)
        name = f"{slug(label)}_{index:02d}{ext.lower() or '.png'}"
        assets.append(asset_entry(src, os.path.join(assets_dir, name), label, root, f"assets/{name}"))

    metadata_files = []
    for index, (label, path) in enumerate(metadata_inputs):
        src = require_file(path, label)
        _base, ext = os.path.splitext(src)
        name = f"{slug(label)}_{index:02d}{ext.lower() or '.txt'}"
        metadata_files.append(metadata_entry(src, os.path.join(assets_dir, name), label, root, f"assets/{name}"))

    index_path = os.path.join(out_dir, "index.html")
    manifest_path = os.path.join(out_dir, "gallery_manifest.json")
    manifest = {
        "schema": "lsfs_static_artifact_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "gallery_path": out_dir,
        "gallery_repo_path": posix_rel(out_dir, root),
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
        "checks": {
            "images": len(image_inputs),
            "metadata_files": len(metadata_files),
            "assets": len(assets),
            "gif_bytes": os.path.getsize(gif_path),
        },
    }
    write_text(index_path, html_page(args.title, assets, metadata_files))
    write_json(manifest_path, manifest)
    if args.report:
        write_text(args.report, markdown_report(args.title, manifest, manifest_path, root, args.next))
    print(f"status=ready gallery={out_dir} manifest={manifest_path} gif={gif_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a static gallery from arbitrary artifacts")
    parser.add_argument("--image", action="append", default=[], help="label=path image artifact; first image becomes shot.gif")
    parser.add_argument("--metadata", action="append", default=[], help="label=path metadata artifact")
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="Static Artifact Gallery")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Publish this static artifact gallery for review.")
    args = parser.parse_args(argv)
    build_gallery(args)


if __name__ == "__main__":
    main()
