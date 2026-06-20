#!/usr/bin/env python
"""Build a visual comparison gallery for Mitsuba native candidate renders."""

import argparse
import html
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None

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
        raise SystemExit("Pillow is required to build a comparison gallery")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def parse_labeled_path(value, label):
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"{label} must be LABEL=PATH")
    name, path = value.split("=", 1)
    name = name.strip()
    path = path.strip()
    if not name or not path:
        raise argparse.ArgumentTypeError(f"{label} must be LABEL=PATH")
    return name, path


def slug_label(value):
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_") or "candidate"


def frame_map_from_render(manifest):
    result = {}
    for frame in manifest.get("frames", []):
        output = frame.get("output_frame")
        preview = frame.get("preview") or {}
        path = resolve_path(preview.get("path") or preview.get("repo_path"))
        if output is not None and path:
            result[int(output)] = {
                "path": path,
                "sequence_frame": frame.get("sequence_frame"),
                "source": "render_preview",
            }
    return result


def frame_map_from_secondary_composite(summary):
    result = {}
    for frame in summary.get("frames", []):
        output = frame.get("output_frame")
        if output is None:
            continue
        composite_path = resolve_path(frame.get("composite_path") or frame.get("composite_repo_path"))
        if composite_path:
            result[int(output)] = {
                "path": composite_path,
                "sequence_frame": frame.get("sequence_frame"),
                "source": "secondary_composite",
            }
    return result


def frame_map_from_candidate(payload, label, path):
    schema = payload.get("schema")
    if schema == "lsfs_mitsuba_xml_render":
        return frame_map_from_render(payload)
    if schema == "lsfs_mitsuba_secondary_composite":
        return frame_map_from_secondary_composite(payload)
    raise SystemExit(f"{path}: unsupported {label} candidate schema {schema!r}")


def frame_map_from_composite(summary):
    target = {}
    composite = {}
    for frame in summary.get("frames", []):
        output = frame.get("output_frame")
        if output is None:
            continue
        target_path = resolve_path(frame.get("target_repo_path"))
        composite_path = resolve_path(frame.get("composite_repo_path"))
        if target_path:
            target[int(output)] = {"path": target_path, "source": "target"}
        if composite_path:
            composite[int(output)] = {"path": composite_path, "source": "depth_aware_composite"}
    return target, composite


def select_outputs(outputs, count):
    outputs = sorted(set(outputs))
    if count <= 0 or len(outputs) <= count:
        return outputs
    if count == 1:
        return [outputs[len(outputs) // 2]]
    return [outputs[round(i * (len(outputs) - 1) / float(count - 1))] for i in range(count)]


def load_image(path, size=None):
    image = Image.open(path).convert("RGB")
    if size and image.size != size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    return image


def label_font(size=18):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def make_strip(columns, out_path):
    images = []
    base_size = None
    for _label, path in columns:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        if base_size is None:
            with Image.open(path) as probe:
                base_size = probe.size
        images.append(load_image(path, base_size))
    label_h = 34
    gap = 6
    width = len(images) * base_size[0] + (len(images) - 1) * gap
    height = base_size[1] + label_h
    strip = Image.new("RGB", (width, height), (10, 15, 19))
    draw = ImageDraw.Draw(strip)
    font = label_font()
    x = 0
    for (label, _path), image in zip(columns, images):
        draw.rectangle((x, 0, x + base_size[0], label_h), fill=(20, 30, 38))
        draw.text((x + 10, 8), label, fill=(232, 242, 248), font=font)
        strip.paste(image, (x, label_h))
        x += base_size[0] + gap
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)
    for image in images:
        image.close()
    return strip.size


def write_gif(image_paths, out_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in image_paths]
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


def copy_asset(src, assets_dir, asset_name, label, root):
    dest = os.path.join(assets_dir, asset_name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
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
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(
        f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>'
        for item in metadata_files
    )
    gif = next((item for item in assets if item["label"] == "Comparison GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Frame")]
    checks = summary.get("checks", {})
    tiles = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Columns", checks.get("columns")),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tile_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in tiles
    )
    hero = f'<section class="hero"><img src="{html.escape(gif["href"])}" alt="Comparison GIF"></section>' if gif else ""
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{html.escape(item['href'])}"><img src="{html.escape(item['href'])}" alt="{html.escape(item['label'])}"></a>
          <figcaption>{html.escape(item['label'])}</figcaption>
        </figure>"""
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #121b22; --ink: #edf7fb; --muted: #9fb2bf; --line: #2b3b47; --accent: #9ed8ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111820; overflow-x: auto; }}
    .hero img {{ display: block; max-width: none; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    figure img {{ display: block; max-width: none; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tile_html}</section>
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
        f"- Columns: `{checks.get('columns')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Columns",
        "",
    ]
    for column in summary.get("columns", []):
        lines.append(f"- `{column}`")
    lines.extend(["", "## Frames", "", "| Output | Strip |", "| ---: | --- |"])
    for frame in summary.get("frames", []):
        lines.append(f"| {frame['output_frame']} | `{frame['strip']['repo_path']}` |")
    lines.extend(["", "## Next", "", next_text])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", action="append", required=True,
                        help="LABEL=render_manifest.json or LABEL=secondary_composite_summary.json")
    parser.add_argument("--depth-aware-composite", required=True)
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Native Candidate Visual Review")
    parser.add_argument("--next", default="Inspect the comparison gallery before increasing sidecar secondary strength.")
    args = parser.parse_args()

    require_pillow()
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")

    root = os.getcwd()
    out_dir = resolve_path(args.out_dir)
    assets_dir = os.path.join(out_dir, "gallery", "assets")
    strips_dir = os.path.join(out_dir, "strips")
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(strips_dir, exist_ok=True)

    composite_path = require_file(args.depth_aware_composite, "depth-aware composite summary")
    composite_summary = read_json(composite_path)
    target_map, c1e_map = frame_map_from_composite(composite_summary)

    render_maps = []
    metadata_files = []
    for item in args.candidate:
        label, path = parse_labeled_path(item, "--candidate")
        render_path = require_file(path, f"{label} candidate manifest")
        render = read_json(render_path)
        render_maps.append((label, frame_map_from_candidate(render, label, render_path), render_path))
        metadata_files.append(copy_asset(render_path, assets_dir, f"{slug_label(label)}_candidate_manifest.json", f"{label} candidate manifest", root))
    metadata_files.append(copy_asset(composite_path, assets_dir, "depth_aware_secondary_composite_summary.json", "C1E composite summary", root))

    common_outputs = set(target_map) & set(c1e_map)
    for _label, frame_map, _path in render_maps:
        common_outputs &= set(frame_map)
    selected = select_outputs(common_outputs, args.frames)
    if not selected:
        raise SystemExit("no common frames across target, C1E, and candidates")

    frame_items = []
    assets = []
    strip_paths = []
    columns = ["Target", "C1E"] + [label for label, _frame_map, _path in render_maps]
    for index, output in enumerate(selected):
        strip_path = os.path.join(strips_dir, f"frame_{index:04d}_compare.png")
        strip_columns = [
            ("Target", target_map[output]["path"]),
            ("C1E", c1e_map[output]["path"]),
        ]
        for label, frame_map, _path in render_maps:
            strip_columns.append((label, frame_map[output]["path"]))
        dims = make_strip(strip_columns, strip_path)
        strip_asset = copy_asset(strip_path, assets_dir, f"frame_{index:04d}_compare.png", f"Frame {output} Compare", root)
        assets.append(strip_asset)
        strip_paths.append(strip_path)
        frame_items.append({
            "output_frame": output,
            "dimensions": dims,
            "strip": {
                "path": strip_path,
                "repo_path": posix_rel(strip_path, root),
                "sha256": sha256_file(strip_path),
                "size": os.path.getsize(strip_path),
            },
        })

    gif_path = os.path.join(out_dir, "gallery", "assets", "comparison.gif")
    write_gif(strip_paths, gif_path, args.fps)
    gif_asset = {
        "label": "Comparison GIF",
        "source": gif_path,
        "source_repo_path": posix_rel(gif_path, root),
        "asset": gif_path,
        "repo_path": posix_rel(gif_path, root),
        "href": "assets/comparison.gif",
        "size": os.path.getsize(gif_path),
        "sha256": sha256_file(gif_path),
        "dimensions": image_dimensions(gif_path),
    }
    assets.insert(0, gif_asset)

    summary_path = os.path.join(out_dir, "candidate_compare_gallery.json")
    gallery_index = os.path.join(out_dir, "gallery", "index.html")
    summary = {
        "schema": "lsfs_mitsuba_candidate_compare_gallery",
        "version": 1,
        "title": args.title,
        "status": "ready",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "columns": columns,
        "checks": {
            "frames": len(frame_items),
            "columns": len(columns),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "gallery": {
            "path": os.path.dirname(gallery_index),
            "repo_path": posix_rel(os.path.dirname(gallery_index), root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "frames": frame_items,
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    report_path = resolve_path(args.report) if args.report else os.path.splitext(summary_path)[0] + ".md"
    write_text(report_path, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} frames={len(frame_items)} columns={len(columns)} "
        f"gallery={summary['gallery']['index_repo_path']}"
    )
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
