#!/usr/bin/env python
"""Compare current Mitsuba renderer frames against the accepted target preview."""

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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to compare Mitsuba target gaps")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def reference_path(frame, role):
    ref = ((frame.get("references") or {}).get(role) or {})
    return ref.get("repo_path") or ref.get("source_repo_path")


def frame_map(frames):
    return {frame.get("frame"): frame for frame in frames if frame.get("frame") is not None}


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def render_preview_path(frame):
    preview = (frame or {}).get("preview") or {}
    return preview.get("path") or preview.get("repo_path")


def composite_preview_path(frame):
    return (frame or {}).get("composite_path") or (frame or {}).get("composite_repo_path")


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    dims = image_dimensions(dest)
    entry = {
        "label": label,
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    if dims:
        entry["dimensions"] = dims
    return entry


def mean_abs_diff(a, b):
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    hist = diff.histogram()
    total = 0
    count = 0
    for channel in range(3):
        offset = channel * 256
        for value in range(256):
            samples = hist[offset + value]
            total += value * samples
            count += samples
    return total / float(max(1, count))


def max_abs_diff(a, b):
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return max(channel[1] for channel in diff.getextrema())


def diff_image(a, b):
    return ImageOps.autocontrast(ImageChops.difference(a.convert("RGB"), b.convert("RGB")))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (10, 16, 22))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        strip.paste(panel.convert("RGB"), (x, label_h))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def write_gif(frame_paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    try:
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Gap GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Gap Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Mean MAD", f"{checks.get('mean_gap_mean_abs_diff', 0.0):.3f}"),
        ("Max MAD", f"{checks.get('max_gap_mean_abs_diff', 0.0):.3f}"),
        ("Max Diff", checks.get("max_gap_max_abs_diff")),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Mitsuba target gap GIF"></section>' if gif else ""
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
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Mean gap mean abs diff: `{checks.get('mean_gap_mean_abs_diff')}`",
        f"- Max gap mean abs diff: `{checks.get('max_gap_mean_abs_diff')}`",
        f"- Max gap max abs diff: `{checks.get('max_gap_max_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Gap MAD | Gap Max | Strip |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('gap_mean_abs_diff'):.4f} | {frame.get('gap_max_abs_diff')} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def actual_frame_source(args, root):
    if args.actual_render_manifest:
        render_path = require_file(args.actual_render_manifest, "actual render manifest")
        render = read_json(render_path)
        if render.get("schema") != "lsfs_mitsuba_xml_render":
            raise SystemExit(f"{args.actual_render_manifest}: expected lsfs_mitsuba_xml_render schema")
        if render.get("status") != "ready":
            raise SystemExit(f"{args.actual_render_manifest}: render status is {render.get('status')!r}")
        return {
            "kind": "mitsuba_render_manifest",
            "path": render_path,
            "repo_path": posix_rel(render_path, root),
            "sha256": sha256_file(render_path),
            "frames": output_frame_map(render.get("frames") or []),
        }
    if args.actual_composite_summary:
        composite_path = require_file(args.actual_composite_summary, "actual composite summary")
        composite = read_json(composite_path)
        if composite.get("schema") != "lsfs_mitsuba_secondary_composite":
            raise SystemExit(f"{args.actual_composite_summary}: expected lsfs_mitsuba_secondary_composite schema")
        return {
            "kind": "secondary_composite_summary",
            "path": composite_path,
            "repo_path": posix_rel(composite_path, root),
            "sha256": sha256_file(composite_path),
            "frames": output_frame_map(composite.get("frames") or []),
        }
    return {"kind": "handoff_base_preview", "frames": None}


def compare(args):
    require_pillow()
    root = os.getcwd()
    handoff_path = require_file(args.handoff_manifest, "handoff bundle")
    target_path = require_file(args.target_summary, "target preview summary")
    handoff = read_json(handoff_path)
    target = read_json(target_path)
    if handoff.get("schema") != "lsfs_mitsuba_renderer_handoff_bundle":
        raise SystemExit(f"{args.handoff_manifest}: expected lsfs_mitsuba_renderer_handoff_bundle schema")
    if target.get("schema") != "lsfs_mitsuba_renderer_target_preview":
        raise SystemExit(f"{args.target_summary}: expected lsfs_mitsuba_renderer_target_preview schema")
    actual_source = actual_frame_source(args, root)

    out_dir = os.path.abspath(args.out_dir)
    diff_dir = os.path.join(out_dir, "diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    handoff_frames = frame_map(handoff.get("frames") or [])
    target_frames = target.get("frames") or []
    results = []
    missing = []
    strip_paths = []
    for index, target_frame in enumerate(target_frames):
        frame_id = target_frame.get("frame")
        handoff_frame = handoff_frames.get(frame_id)
        if actual_source["kind"] == "mitsuba_render_manifest":
            actual_render_frame = actual_source["frames"].get(target_frame.get("output_frame"))
            actual_path = resolve_path(render_preview_path(actual_render_frame))
        elif actual_source["kind"] == "secondary_composite_summary":
            actual_render_frame = actual_source["frames"].get(target_frame.get("output_frame"))
            actual_path = resolve_path(composite_preview_path(actual_render_frame))
        else:
            actual_path = resolve_path(reference_path(handoff_frame or {}, "base_preview"))
        target_image_path = resolve_path(target_frame.get("renderer_target_repo_path"))
        if not actual_path or not os.path.isfile(actual_path) or not target_image_path or not os.path.isfile(target_image_path):
            missing.append({"frame": frame_id, "actual": actual_path, "target": target_image_path})
            continue
        actual = Image.open(actual_path).convert("RGB")
        target_img = Image.open(target_image_path).convert("RGB")
        if actual.size != target_img.size:
            actual = actual.resize(target_img.size, Image.Resampling.BICUBIC)
        diff = diff_image(actual, target_img)
        base_name = f"frame_{index:04d}.png"
        diff_path = os.path.join(diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        diff.save(diff_path)
        labeled_strip([actual, target_img, diff], ["actual Mitsuba", "accepted target", "gap diff"], strip_path)
        strip_paths.append(strip_path)
        results.append({
            "frame": frame_id,
            "output_frame": target_frame.get("output_frame"),
            "actual_repo_path": posix_rel(actual_path, root),
            "target_repo_path": posix_rel(target_image_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "actual_sha256": sha256_file(actual_path),
            "target_sha256": sha256_file(target_image_path),
            "gap_mean_abs_diff": mean_abs_diff(actual, target_img),
            "gap_max_abs_diff": max_abs_diff(actual, target_img),
        })

    if not results:
        raise SystemExit("no comparable frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Gap GIF", root)]
    key_indices = sorted(set(round(i * (len(results) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"gap_strip_{out_index:02d}.png", f"Gap Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "renderer_target_gap_summary.json")
    summary = {
        "schema": "lsfs_mitsuba_renderer_target_gap",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if not missing else "review",
        "source": {
            "handoff_manifest": posix_rel(handoff_path, root),
            "target_summary": posix_rel(target_path, root),
            "actual_source": {
                "kind": actual_source["kind"],
                "repo_path": actual_source.get("repo_path"),
                "sha256": actual_source.get("sha256"),
            },
            "public_target_url": ((target.get("source") or {}).get("public_reference") or {}).get("url"),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(results),
            "missing_references": len(missing),
            "mean_gap_mean_abs_diff": sum(item["gap_mean_abs_diff"] for item in results) / len(results),
            "max_gap_mean_abs_diff": max(item["gap_mean_abs_diff"] for item in results),
            "max_gap_max_abs_diff": max(item["gap_max_abs_diff"] for item in results),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "missing_references": missing,
        "frames": results,
        "gallery": {},
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "renderer_target_gap_summary.json", "Gap summary", root)
    handoff_asset = copy_asset(handoff_path, assets_dir, "handoff_manifest.json", "Handoff manifest", root)
    target_asset = copy_asset(target_path, assets_dir, "renderer_target_preview_summary.json", "Target preview summary", root)
    metadata_files = [summary_asset, handoff_asset, target_asset]
    index_path = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_renderer_target_gap_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} frames={summary['checks']['frames']} "
        f"max_gap_mad={summary['checks']['max_gap_mean_abs_diff']:.6f} "
        f"gif={gif_path} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare actual Mitsuba frames against a target preview")
    parser.add_argument("handoff_manifest")
    parser.add_argument("target_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--actual-render-manifest",
                        help="optional lsfs_mitsuba_xml_render manifest to compare instead of the handoff base previews")
    parser.add_argument("--actual-composite-summary",
                        help="optional lsfs_mitsuba_secondary_composite summary to compare instead of the handoff base previews")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Renderer Target Gap")
    parser.add_argument("--report")
    parser.add_argument(
        "--next",
        default="Use this gap baseline to judge renderer-native secondary and grade improvements.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.actual_render_manifest and args.actual_composite_summary:
        parser.error("actual-render-manifest and actual-composite-summary are mutually exclusive")
    compare(args)


if __name__ == "__main__":
    main()
