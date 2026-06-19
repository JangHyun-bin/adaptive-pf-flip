#!/usr/bin/env python
"""Build a static gallery for direct Blender bridge cinematic outputs."""

import argparse
import html
import json
import os
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def posix_rel(path, root):
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def format_bytes(size):
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"


def image_dimensions(path):
    with open(path, "rb") as f:
        header = f.read(24)
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        return struct.unpack(">II", header[16:24])
    if header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
        return struct.unpack("<HH", header[6:10])
    return None


def require_file(path, label):
    resolved = os.path.abspath(path)
    if not os.path.isfile(resolved):
        raise SystemExit(f"Missing {label}: {resolved}")
    return resolved


def copy_asset(src, out_dir, name, label):
    src = require_file(src, label)
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    dest = os.path.join(assets_dir, name)
    shutil.copy2(src, dest)
    return {
        "label": label,
        "source": src,
        "asset": dest,
        "href": f"assets/{name}",
        "size": os.path.getsize(dest),
        "dimensions": image_dimensions(dest),
    }


def frame_paths(frames_dir):
    root = Path(frames_dir)
    if not root.is_dir():
        raise SystemExit(f"Missing frame directory: {frames_dir}")
    frames = sorted(root.glob("*.png"))
    if not frames:
        raise SystemExit(f"No PNG frames found: {frames_dir}")
    return [str(path) for path in frames]


def select_keyframes(frames, count):
    count = max(1, min(int(count), len(frames)))
    if count == len(frames):
        return frames
    if count == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(count - 1)) for i in range(count)))
    return [frames[index] for index in indices]


def metric_value(summary, *keys):
    value = summary
    for key in keys:
        if not isinstance(value, dict):
            return "n/a"
        value = value.get(key)
    return "n/a" if value is None else value


def metric_tiles(bridge_summary, comparison_summary):
    attenuation = bridge_summary.get("metadata_depth_attenuation", {})
    deltas = comparison_summary.get("metric_deltas", {})
    return [
        ("Status", bridge_summary.get("status", "n/a")),
        ("Frames", bridge_summary.get("frame_count", "n/a")),
        ("Preset", bridge_summary.get("render_preset_name", "n/a")),
        ("Min Contrast", bridge_summary.get("min_contrast", "n/a")),
        ("Mean Luma", metric_value(bridge_summary, "visual_qa", "mean_luminance", "mean")),
        ("Bright Delta", metric_value(deltas, "bright_ratio", "delta")),
        ("Highlight Delta", metric_value(deltas, "highlight_ratio", "delta")),
        ("Attenuation", attenuation.get("status", "n/a")),
        ("Water Alpha", attenuation.get("water_alpha_multiplier", "n/a")),
        ("Secondary Cap", attenuation.get("secondary_particle_cap_scale", "n/a")),
    ]


def image_block(item):
    dims = item.get("dimensions")
    dims_text = f"{dims[0]} x {dims[1]}" if dims else "n/a"
    return f"""
      <figure>
        <a href="{html.escape(item['href'])}"><img src="{html.escape(item['href'])}" alt="{html.escape(item['label'])}"></a>
        <figcaption><strong>{html.escape(item['label'])}</strong><span>{html.escape(dims_text)} / {html.escape(format_bytes(item['size']))}</span></figcaption>
      </figure>"""


def html_page(title, bridge_summary, comparison_summary, assets, metadata_files):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tiles = "\n".join(
        f"<div class=\"metric\"><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metric_tiles(bridge_summary, comparison_summary)
    )
    hero = next(item for item in assets if item["label"] == "Shot GIF")
    comparison = next(item for item in assets if item["label"] != "Shot GIF" and not item["label"].startswith("Keyframe"))
    frames = [item for item in assets if item["label"].startswith("Keyframe")]
    frame_blocks = "\n".join(image_block(item) for item in frames)
    file_links = "\n".join(
        f"<li><a href=\"{html.escape(item['href'])}\">{html.escape(item['label'])}</a> ({html.escape(format_bytes(item['size']))})</li>"
        for item in metadata_files
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f4f6f1;
      --panel: #ffffff;
      --ink: #171c19;
      --muted: #5d665f;
      --line: #d6ded4;
      --accent: #1f6b5d;
      --shadow: 0 10px 24px rgba(23, 28, 25, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    header {{
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 28px min(5vw, 56px) 18px;
    }}
    h1 {{
      margin: 0;
      font-size: 34px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .subhead {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
      overflow-wrap: anywhere;
    }}
    main {{
      width: min(1500px, 100%);
      margin: 0 auto;
      padding: 22px min(5vw, 56px) 48px;
    }}
    .hero, figure {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: hidden;
      box-shadow: var(--shadow);
    }}
    .hero img, figure img {{
      display: block;
      width: 100%;
      height: auto;
      background: #101512;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      margin: 20px 0 24px;
    }}
    .metric {{
      min-height: 76px;
      padding: 13px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .metric strong {{
      display: block;
      margin-top: 8px;
      font-size: 16px;
      overflow-wrap: anywhere;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 430px), 1fr));
      gap: 16px;
    }}
    figure {{
      margin: 0;
    }}
    figcaption {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 13px;
    }}
    figcaption strong {{
      color: var(--ink);
    }}
    .links {{
      margin: 0;
      padding: 14px 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      columns: 2 280px;
    }}
    .links li {{
      margin: 5px 0;
      break-inside: avoid;
    }}
    a {{
      color: var(--accent);
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }}
    @media (max-width: 720px) {{
      h1 {{ font-size: 28px; }}
      figcaption {{ display: block; }}
      figcaption span {{ display: block; margin-top: 4px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <div class="subhead">Generated {html.escape(now)} from direct Blender bridge outputs and S174 comparison data.</div>
  </header>
  <main>
    <section class="hero">
      <img src="{html.escape(hero['href'])}" alt="Shot GIF">
    </section>
    <section class="metrics">
      {tiles}
    </section>
    <h2>Baseline Comparison</h2>
    {image_block(comparison)}
    <h2>Keyframes</h2>
    <section class="grid">
      {frame_blocks}
    </section>
    <h2>Files</h2>
    <ul class="links">
      {file_links}
    </ul>
  </main>
</body>
</html>
"""


def markdown_report(title, out_dir, manifest_path, assets, metadata_files, root):
    lines = [
        f"# {title} Gallery",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Title: `{title}`",
        f"Gallery directory: `{posix_rel(out_dir, root)}`",
        f"Manifest: `{posix_rel(manifest_path, root)}`",
        "",
        "## Assets",
        "",
        "| Asset | Size | Dimensions | Path |",
        "| --- | ---: | --- | --- |",
    ]
    for item in assets:
        dims = item.get("dimensions")
        dims_text = f"{dims[0]} x {dims[1]}" if dims else "n/a"
        lines.append(
            f"| {item['label']} | {format_bytes(item['size'])} | `{dims_text}` | `{posix_rel(item['asset'], root)}` |"
        )
    lines.extend(["", "## Metadata Files", ""])
    for item in metadata_files:
        lines.append(f"- `{posix_rel(item['asset'], root)}` ({format_bytes(item['size'])})")
    lines.extend([
        "",
        "## Next",
        "",
        "Publish this gallery through `tools/publish_cinematic_gallery.py --cftunnel`, then use the public page to select the next visual pass.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a direct bridge cinematic gallery")
    parser.add_argument("shot_dir")
    parser.add_argument("--out", required=True)
    parser.add_argument("--comparison-sheet", required=True)
    parser.add_argument("--comparison-summary", required=True)
    parser.add_argument("--comparison-label", default="Comparison")
    parser.add_argument("--title", default="S173 Metadata Depth Attenuation")
    parser.add_argument("--keyframes", type=int, default=3)
    parser.add_argument("--report")
    args = parser.parse_args(argv)

    root = os.getcwd()
    shot_dir = os.path.abspath(args.shot_dir)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    bridge_summary_path = require_file(os.path.join(shot_dir, "blender", "bridge_summary.json"), "bridge summary")
    gif_path = require_file(os.path.join(shot_dir, "shot.gif"), "shot GIF")
    frames = select_keyframes(frame_paths(os.path.join(shot_dir, "blender", "frames")), args.keyframes)
    comparison_sheet = require_file(args.comparison_sheet, "comparison sheet")
    comparison_summary_path = require_file(args.comparison_summary, "comparison summary")

    assets = [
        copy_asset(gif_path, out_dir, "shot.gif", "Shot GIF"),
        copy_asset(comparison_sheet, out_dir, "comparison.png", args.comparison_label),
    ]
    for index, frame in enumerate(frames):
        assets.append(copy_asset(frame, out_dir, f"keyframe_{index:02d}.png", f"Keyframe {index + 1}"))

    metadata_files = [
        copy_asset(bridge_summary_path, out_dir, "bridge_summary.json", "Bridge summary"),
        copy_asset(comparison_summary_path, out_dir, "comparison_summary.json", "Comparison summary"),
    ]

    bridge_summary = read_json(bridge_summary_path)
    comparison_summary = read_json(comparison_summary_path)
    index_path = os.path.join(out_dir, "index.html")
    write_text(index_path, html_page(args.title, bridge_summary, comparison_summary, assets, metadata_files))
    manifest_path = os.path.join(out_dir, "gallery_manifest.json")
    write_json(manifest_path, {
        "schema": "lsfs_bridge_cinematic_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "shot_dir": shot_dir,
        "index": index_path,
        "assets": assets,
        "metadata_files": metadata_files,
        "bridge_status": bridge_summary.get("status"),
        "comparison_metric_deltas": comparison_summary.get("metric_deltas", {}),
    })
    if args.report:
        report_path = os.path.abspath(args.report)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        write_text(report_path, markdown_report(args.title, out_dir, manifest_path, assets, metadata_files, root))
    print(f"status=ok gallery={index_path} manifest={manifest_path}")
    if args.report:
        print(f"report={args.report}")


if __name__ == "__main__":
    main()
