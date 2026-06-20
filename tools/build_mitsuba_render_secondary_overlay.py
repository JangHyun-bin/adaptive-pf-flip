#!/usr/bin/env python
"""Apply handoff secondary layers over an actual Mitsuba render and grade it."""

import argparse
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
from build_mitsuba_renderer_target_preview import (
    Image,
    copy_asset,
    diff_image,
    grade_image,
    labeled_strip,
    layer_panel,
    max_abs_diff,
    mean_abs_diff,
    reference_path,
    require_pillow,
    resolve_path,
    write_gif,
)


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def frame_map(frames):
    return {frame.get("frame"): frame for frame in frames if frame.get("frame") is not None}


def render_preview_path(frame):
    preview = (frame or {}).get("preview") or {}
    return preview.get("path") or preview.get("repo_path")


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Overlay GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Overlay Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Mean MAD", f"{checks.get('mean_overlay_mean_abs_diff', 0.0):.3f}"),
        ("Max MAD", f"{checks.get('max_overlay_mean_abs_diff', 0.0):.3f}"),
        ("Max Diff", checks.get("max_overlay_max_abs_diff")),
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
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Overlay GIF"></section>' if gif else ""
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
        f"- Mean overlay mean abs diff: `{checks.get('mean_overlay_mean_abs_diff')}`",
        f"- Max overlay mean abs diff: `{checks.get('max_overlay_mean_abs_diff')}`",
        f"- Max overlay max abs diff: `{checks.get('max_overlay_max_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Overlay MAD | Overlay Max | Strip |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('overlay_mean_abs_diff'):.4f} | {frame.get('overlay_max_abs_diff')} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build_overlay(args):
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.actual_render_manifest, "actual render manifest")
    handoff_path = require_file(args.handoff_manifest, "handoff manifest")
    target_path = require_file(args.target_summary, "target preview summary")
    render = read_json(render_path)
    handoff = read_json(handoff_path)
    target = read_json(target_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.actual_render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.actual_render_manifest}: render status is {render.get('status')!r}")
    if handoff.get("schema") != "lsfs_mitsuba_renderer_handoff_bundle":
        raise SystemExit(f"{args.handoff_manifest}: expected lsfs_mitsuba_renderer_handoff_bundle schema")
    if target.get("schema") != "lsfs_mitsuba_renderer_target_preview":
        raise SystemExit(f"{args.target_summary}: expected lsfs_mitsuba_renderer_target_preview schema")

    out_dir = os.path.abspath(args.out_dir)
    overlay_dir = os.path.join(out_dir, "overlay_secondary")
    graded_dir = os.path.join(out_dir, "overlay_graded")
    diff_dir = os.path.join(out_dir, "diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (overlay_dir, graded_dir, diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    render_frames = output_frame_map(render.get("frames") or [])
    handoff_frames = frame_map(handoff.get("frames") or [])
    grade_settings = (((target.get("settings") or {}).get("grade")) or {})
    results = []
    missing = []
    graded_paths = []
    for index, target_frame in enumerate(target.get("frames") or []):
        frame_id = target_frame.get("frame")
        output_frame = target_frame.get("output_frame")
        render_frame = render_frames.get(output_frame)
        handoff_frame = handoff_frames.get(frame_id)
        actual_path = resolve_path(render_preview_path(render_frame))
        layer_path = resolve_path(reference_path(handoff_frame or {}, "secondary_layer"))
        target_path_frame = resolve_path(target_frame.get("renderer_target_repo_path"))
        absent = []
        for role, path in (("actual", actual_path), ("secondary_layer", layer_path), ("target", target_path_frame)):
            if not path or not os.path.isfile(path):
                absent.append({"role": role, "path": path})
        if absent:
            missing.append({"frame": frame_id, "output_frame": output_frame, "missing": absent})
            continue

        actual = Image.open(actual_path).convert("RGBA")
        layer = Image.open(layer_path).convert("RGBA")
        if layer.size != actual.size:
            layer = layer.resize(actual.size, Image.Resampling.BICUBIC)
        overlay = Image.alpha_composite(actual, layer).convert("RGB")
        graded = grade_image(overlay, grade_settings)
        target_img = Image.open(target_path_frame).convert("RGB")
        if target_img.size != graded.size:
            target_img = target_img.resize(graded.size, Image.Resampling.BICUBIC)
        diff = diff_image(graded, target_img)

        base_name = f"frame_{index:04d}.png"
        overlay_path = os.path.join(overlay_dir, base_name)
        graded_path = os.path.join(graded_dir, base_name)
        diff_path = os.path.join(diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        overlay.save(overlay_path)
        graded.save(graded_path)
        diff.save(diff_path)
        labeled_strip(
            [
                actual.convert("RGB"),
                layer_panel(layer, (20, 30, 38, 255)),
                overlay,
                graded,
                target_img,
                diff,
            ],
            ["actual Mitsuba", "secondary layer", "overlay", "overlay graded", "accepted target", "diff"],
            strip_path,
        )
        graded_paths.append(graded_path)
        results.append({
            "frame": frame_id,
            "output_frame": output_frame,
            "actual_repo_path": posix_rel(actual_path, root),
            "secondary_layer_repo_path": posix_rel(layer_path, root),
            "target_repo_path": posix_rel(target_path_frame, root),
            "overlay_repo_path": posix_rel(overlay_path, root),
            "overlay_graded_repo_path": posix_rel(graded_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "overlay_graded_sha256": sha256_file(graded_path),
            "overlay_mean_abs_diff": mean_abs_diff(graded, target_img),
            "overlay_max_abs_diff": max_abs_diff(graded, target_img),
        })

    if not results:
        raise SystemExit("no overlay frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(graded_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Overlay GIF", root)]
    key_indices = sorted(set(round(i * (len(results) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(results[frame_index]["strip_repo_path"], assets_dir, f"overlay_strip_{out_index:02d}.png", f"Overlay Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "secondary_overlay_summary.json")
    checks = {
        "frames": len(results),
        "missing_references": len(missing),
        "mean_overlay_mean_abs_diff": sum(item["overlay_mean_abs_diff"] for item in results) / len(results),
        "max_overlay_mean_abs_diff": max(item["overlay_mean_abs_diff"] for item in results),
        "max_overlay_max_abs_diff": max(item["overlay_max_abs_diff"] for item in results),
        "gif_bytes": os.path.getsize(gif_path),
    }
    summary = {
        "schema": "lsfs_mitsuba_render_secondary_overlay",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if not missing else "review",
        "source": {
            "actual_render_manifest": posix_rel(render_path, root),
            "handoff_manifest": posix_rel(handoff_path, root),
            "target_summary": posix_rel(target_path, root),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
            "grade": grade_settings,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": results,
        "gallery": {},
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "secondary_overlay_summary.json", "Overlay summary", root)
    render_asset = copy_asset(render_path, assets_dir, "mitsuba_render.json", "Actual render manifest", root)
    handoff_asset = copy_asset(handoff_path, assets_dir, "handoff_manifest.json", "Handoff manifest", root)
    target_asset = copy_asset(target_path, assets_dir, "renderer_target_preview_summary.json", "Target preview summary", root)
    metadata_files = [summary_asset, render_asset, handoff_asset, target_asset]
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
        "schema": "lsfs_mitsuba_render_secondary_overlay_gallery",
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
        f"status={summary['status']} frames={checks['frames']} "
        f"max_overlay_mad={checks['max_overlay_mean_abs_diff']:.6f} "
        f"gif={gif_path} summary={summary_path}"
    )
    if summary["status"] != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply secondary overlay and grade to an actual Mitsuba render")
    parser.add_argument("actual_render_manifest")
    parser.add_argument("handoff_manifest")
    parser.add_argument("target_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Secondary Overlay")
    parser.add_argument("--report")
    parser.add_argument(
        "--next",
        default="Use this overlay as a visual bridge while replacing screen-space secondary with renderer-native data.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    build_overlay(args)


if __name__ == "__main__":
    main()
