#!/usr/bin/env python
"""Build a comparison gallery for Mitsuba render sequence variants."""

import argparse
import html
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - reported at runtime.
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
    if Image is None or ImageDraw is None or ImageFont is None:
        raise SystemExit("Pillow is required to build a sequence comparison gallery")


def resolve_path(path):
    if not path:
        return None
    text = str(path).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(text)


def parse_labeled_path(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("candidate must be LABEL=PATH")
    label, path = value.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise argparse.ArgumentTypeError("candidate must be LABEL=PATH")
    return label, path


def slug_label(value):
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_") or "candidate"


def frame_map_from_render(payload):
    frames = {}
    for frame in payload.get("frames") or []:
        output = frame.get("output_frame")
        preview = frame.get("preview") or {}
        path = resolve_path(preview.get("path") or preview.get("repo_path"))
        if output is not None and path:
            frames[int(output)] = {"path": path, "source": "render_preview"}
    return frames


def frame_map_from_sequence_adapter(payload):
    frames = {}
    for frame in payload.get("frames") or []:
        output = frame.get("output_frame")
        path = resolve_path(frame.get("corrected_path") or frame.get("corrected_repo_path"))
        if output is not None and path:
            frames[int(output)] = {
                "path": path,
                "source": "runtime_render_sequence_adapter",
                "mask": frame.get("mask"),
            }
    return frames


def frame_map_from_candidate(payload, path):
    schema = payload.get("schema")
    if schema == "lsfs_mitsuba_xml_render":
        return frame_map_from_render(payload)
    if schema in {
        "lsfs_mitsuba_low_frequency_runtime_render_adapter",
        "lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter",
    }:
        return frame_map_from_sequence_adapter(payload)
    raise SystemExit(f"{path}: unsupported candidate schema {schema!r}")


def select_outputs(outputs, value):
    outputs = sorted(set(outputs))
    text = str(value or "").strip()
    if not text:
        return outputs
    if "," in text:
        wanted = {int(part.strip()) for part in text.split(",") if part.strip()}
        return [output for output in outputs if output in wanted]
    count = int(text)
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
        "source_repo_path": posix_rel(os.path.abspath(src), root),
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
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
        ("Candidates", checks.get("candidates")),
        ("Common frames", checks.get("common_frames")),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tile_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in tiles
    )
    hero = f'<section class="hero"><img src="{html.escape(gif["href"])}" alt="Comparison GIF"></section>' if gif else ""
    strip_html = "\n".join(
        f'<figure><a href="{html.escape(item["href"])}"><img src="{html.escape(item["href"])}" alt="{html.escape(item["label"])}"></a><figcaption>{html.escape(item["label"])}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071015; --panel: #101a22; --line: #2a3b46; --ink: #eff8fb; --muted: #9eb0ba; --accent: #91dcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px 18px 42px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111; margin-bottom: 14px; overflow: auto; }}
    .hero img {{ display: block; width: 100%; min-width: 1200px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
    figure {{ margin: 0 0 12px; border: 1px solid var(--line); background: var(--panel); overflow: auto; }}
    figure img {{ display: block; width: 100%; min-width: 1200px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tile_html}</section>
    <section>{strip_html}</section>
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
        f"- Candidates: `{checks.get('candidates')}`",
        f"- Common frames: `{checks.get('common_frames')}`",
        f"- Selected frames: `{checks.get('frames')}`",
        f"- Missing frame references: `{checks.get('missing_frame_references')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Candidates",
        "",
        "| Label | Schema | Frames | Source |",
        "| --- | --- | ---: | --- |",
    ]
    for candidate in summary.get("candidates") or []:
        lines.append(
            f"| `{candidate['label']}` | `{candidate['schema']}` | "
            f"{candidate['frames']} | `{candidate['repo_path']}` |"
        )
    lines.extend([
        "",
        "## Selected Frames",
        "",
        "| Output | Strip |",
        "| ---: | --- |",
    ])
    for frame in summary.get("frames") or []:
        lines.append(f"| {frame['output_frame']} | `{frame['strip_repo_path']}` |")
    lines.extend(["", "## Next", "", summary.get("next") or "Use this comparison to choose the next render correction path.", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    candidates = []
    frame_maps = []
    for label, path in args.candidate:
        manifest_path = require_file(resolve_path(path), f"{label} candidate")
        payload = read_json(manifest_path)
        frames = frame_map_from_candidate(payload, manifest_path)
        if not frames:
            raise SystemExit(f"{path}: candidate has no comparable frames")
        candidates.append({
            "label": label,
            "path": manifest_path,
            "repo_path": posix_rel(manifest_path, root),
            "schema": payload.get("schema"),
            "status": payload.get("status"),
            "frames": len(frames),
        })
        frame_maps.append((label, frames))

    common_outputs = sorted(set.intersection(*(set(frames.keys()) for _label, frames in frame_maps)))
    selected_outputs = select_outputs(common_outputs, args.frames)
    if not selected_outputs:
        raise SystemExit("no common frames selected")

    out_dir = os.path.abspath(args.out_dir)
    strips_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(strips_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    missing = []
    frames = []
    strip_paths = []
    for output in selected_outputs:
        columns = []
        for label, frame_map in frame_maps:
            item = frame_map.get(output)
            path = item.get("path") if item else None
            if not path or not os.path.isfile(path):
                missing.append({"output_frame": output, "candidate": label, "path": path})
                continue
            columns.append((label, path))
        if len(columns) != len(frame_maps):
            continue
        strip_path = os.path.join(strips_dir, f"frame_{output:04d}_sequence_compare.png")
        make_strip(columns, strip_path)
        strip_paths.append(strip_path)
        frames.append({
            "output_frame": output,
            "strip_repo_path": posix_rel(strip_path, root),
            "columns": [{"label": label, "repo_path": posix_rel(path, root)} for label, path in columns],
        })

    if not frames:
        raise SystemExit("no comparison strips were produced")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Comparison GIF", root)]
    for index, frame in enumerate(frames):
        assets.append(copy_asset(resolve_path(frame["strip_repo_path"]), assets_dir, f"frame_{index:04d}.png", f"Frame {frame['output_frame']}", root))

    summary_path = os.path.abspath(args.summary)
    summary = {
        "schema": "lsfs_mitsuba_sequence_compare_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if not missing else "review",
        "candidates": candidates,
        "checks": {
            "candidates": len(candidates),
            "common_frames": len(common_outputs),
            "frames": len(frames),
            "missing_frame_references": len(missing),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "missing": missing,
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        copy_asset(summary_path, assets_dir, "sequence_compare_summary.json", "Sequence Compare Summary", root),
    ]
    for candidate in candidates:
        metadata_files.append(copy_asset(candidate["path"], assets_dir, f"{slug_label(candidate['label'])}_manifest.json", f"{candidate['label']} Manifest", root))

    gallery_index = os.path.join(gallery_dir, "index.html")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": gallery_index,
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, resolve_path(metadata_files[0]["repo_path"]))
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_sequence_compare_gallery_manifest",
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
        f"status={summary['status']} candidates={len(candidates)} frames={len(frames)} "
        f"summary={summary_path}"
    )
    if summary["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a comparison gallery for Mitsuba render sequence variants")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", action="append", type=parse_labeled_path, required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--frames", default="12", help="frame count or comma-separated output frame list")
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Sequence Comparison")
    parser.add_argument("--next", default="Use this comparison to choose the next render correction path.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if len(args.candidate) < 2:
        parser.error("at least two candidates are required")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    run(args)


if __name__ == "__main__":
    main()
