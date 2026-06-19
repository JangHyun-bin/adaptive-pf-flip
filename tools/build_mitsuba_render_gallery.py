#!/usr/bin/env python
"""Build a static gallery for actual Mitsuba XML render probe outputs."""

import argparse
import html
import os
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
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a Mitsuba render gallery")


def copy_asset(src, assets_dir, asset_name, label, root):
    dest = os.path.join(assets_dir, asset_name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    dims = image_dimensions(dest)
    entry = {
        "label": label,
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{asset_name}",
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    if dims:
        entry["dimensions"] = dims
    return entry


def preview_path(frame):
    item = frame.get("preview") or {}
    return item.get("path") or item.get("repo_path")


def select_keyframes(frames, count):
    if count <= 0 or len(frames) <= count:
        return list(frames)
    return [
        frames[round(index * (len(frames) - 1) / float(max(1, count - 1)))]
        for index in range(count)
    ]


def write_gif(preview_paths, out_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in preview_paths]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    try:
        images[0].save(
            out_path,
            save_all=True,
            append_images=images[1:],
            duration=duration_ms,
            loop=0,
            optimize=False,
        )
    finally:
        for image in images:
            image.close()


def html_page(title, render, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Shot GIF"), None)
    keyframes = [item for item in assets if item["label"].startswith("Keyframe")]
    runtime = render.get("runtime") or {}
    checks = render.get("checks") or {}
    supervisor = render.get("supervisor") or {}
    metadata_links = "\n".join(
        f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>'
        for item in metadata_files
    )
    tiles = [
        ("Status", render.get("status")),
        ("Renderer", "Mitsuba Python API"),
        ("Frames", checks.get("frames_rendered")),
        ("SPP", runtime.get("spp")),
        ("Variant", runtime.get("variant")),
        ("Worker Exit", supervisor.get("worker_exit_code", "n/a")),
    ]
    metric_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in tiles
    )
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{html.escape(item['href'])}"><img src="{html.escape(item['href'])}" alt="{html.escape(item['label'])}"></a>
          <figcaption>{html.escape(item['label'])}</figcaption>
        </figure>"""
        for item in keyframes
    )
    hero = ""
    if gif:
        hero = f'<section class="hero"><img src="{html.escape(gif["href"])}" alt="Mitsuba render GIF"></section>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #091016; --panel: #121b23; --ink: #e9f4fb; --muted: #9db1bf; --line: #2b3b47; --accent: #93d5ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #c1ccd8; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
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
      <nav>{metadata_links}</nav>
    </header>
    {hero}
    <section class="metrics">{metric_html}</section>
    <section class="grid">{frame_html}</section>
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
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.render_manifest, "mitsuba render manifest")
    render = read_json(render_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.render_manifest}: render status is {render.get('status')!r}")

    out_dir = os.path.abspath(args.out)
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    frames = render.get("frames") or []
    preview_paths = [os.path.abspath(preview_path(frame)) for frame in frames if preview_path(frame)]
    for path in preview_paths:
        require_file(path, "render preview")
    if not preview_paths:
        raise SystemExit("render manifest does not contain PNG previews")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(preview_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Shot GIF", root)]
    selected = select_keyframes(list(zip(frames, preview_paths)), args.keyframes)
    for index, (frame, path) in enumerate(selected):
        label = f"Keyframe {index + 1} output {frame.get('output_frame')}"
        assets.append(copy_asset(path, assets_dir, f"keyframe_{index:02d}.png", label, root))

    render_asset = copy_asset(render_path, assets_dir, "mitsuba_render.json", "Mitsuba render manifest", root)
    metadata_files = [render_asset]
    export_path = (render.get("mitsuba_export") or {}).get("path") or (render.get("mitsuba_export") or {}).get("repo_path")
    if export_path:
        metadata_files.append(copy_asset(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export manifest", root))

    index_path = os.path.join(out_dir, "index.html")
    manifest_path = os.path.join(out_dir, "gallery_manifest.json")
    manifest = {
        "schema": "lsfs_mitsuba_render_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "gallery_path": out_dir,
        "gallery_repo_path": posix_rel(out_dir, root),
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
        "render": {
            "status": render.get("status"),
            "frames_rendered": (render.get("checks") or {}).get("frames_rendered"),
            "spp": (render.get("runtime") or {}).get("spp"),
            "variant": (render.get("runtime") or {}).get("variant"),
            "worker_exit_code": (render.get("supervisor") or {}).get("worker_exit_code"),
        },
    }
    write_text(index_path, html_page(args.title, render, assets, metadata_files))
    write_json(manifest_path, manifest)
    if args.report:
        write_text(args.report, markdown_report(args.title, manifest, manifest_path, root, args.next))
    print(f"status=ok gallery={out_dir} manifest={manifest_path} gif={gif_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a gallery from actual Mitsuba render outputs")
    parser.add_argument("render_manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="Mitsuba Render Probe Gallery")
    parser.add_argument("--keyframes", type=int, default=3)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--report")
    parser.add_argument("--next", default="Publish this gallery through cftunnel for external review.")
    args = parser.parse_args(argv)
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    build_gallery(args)


if __name__ == "__main__":
    main()
