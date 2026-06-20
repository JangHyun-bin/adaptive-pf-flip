#!/usr/bin/env python
"""Build renderer-side low-frequency previews from a runtime import manifest."""

import argparse
import html
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

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
from build_mitsuba_low_frequency_parity_texture_package import diff_stats, write_gif


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build low-frequency renderer runtime previews")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def source_path(item, root):
    return resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)


def clamp_int(value):
    return max(0, min(255, int(round(value))))


def blend_delta(base, positive, negative, gain):
    base_bytes = base.convert("RGB").tobytes()
    pos_bytes = positive.convert("RGB").tobytes()
    neg_bytes = negative.convert("RGB").tobytes()
    out = bytearray(len(base_bytes))
    for index in range(len(base_bytes)):
        out[index] = clamp_int(int(base_bytes[index]) + (int(pos_bytes[index]) - int(neg_bytes[index])) * gain)
    return Image.frombytes("RGB", base.size, bytes(out))


def save_image(image, path, root):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path)
    return {
        "path": os.path.abspath(path),
        "repo_path": posix_rel(os.path.abspath(path), root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
        "dimensions": image_dimensions(path),
    }


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (10, 15, 19))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        strip.paste(panel.convert("RGB"), (x, label_h))
        draw.text((x + 8, 8), labels[index], fill=(232, 244, 248))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def copy_asset(src, assets_dir, name, label, root):
    source = require_file(resolve_path(src, root), label)
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(source) != os.path.abspath(dest):
        shutil.copy2(source, dest)
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "source_repo_path": posix_rel(source, root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def summary_metadata_entry(summary_path, assets_dir, root):
    dest = os.path.join(assets_dir, "renderer_runtime_preview_summary.json")
    return {
        "label": "Renderer Runtime Preview Summary",
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": "assets/renderer_runtime_preview_summary.json",
        "source_repo_path": posix_rel(os.path.abspath(summary_path), root),
    }


def html_page(title, summary, assets, metadata_files):
    shot = next((item for item in assets if item.get("label") == "Renderer Runtime GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Runtime Strip")]
    checks = summary.get("checks") or {}
    links = "\n".join(f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>' for item in metadata_files)
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Missing", checks.get("missing_references")),
        ("Dim mismatches", checks.get("dimension_mismatches")),
        ("Oracle max", checks.get("max_oracle_abs_diff")),
        ("WebGL max", checks.get("max_webgl_abs_diff")),
    ]
    metrics_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metrics
    )
    hero = f'<section class="hero"><img src="{html.escape(shot["href"])}" alt="Renderer runtime GIF"></section>' if shot else ""
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
    :root {{ color-scheme: dark; --bg: #070c10; --panel: #111921; --line: #2a3943; --ink: #edf8fb; --muted: #9caeb8; --accent: #91dcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 42px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111; margin-bottom: 14px; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{metrics_html}</section>
    <section class="grid">{frame_html}</section>
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
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Dimension mismatches: `{checks.get('dimension_mismatches')}`",
        f"- Max oracle abs diff: `{checks.get('max_oracle_abs_diff')}`",
        f"- Max oracle mean diff: `{checks.get('max_oracle_mean_abs_diff')}`",
        f"- Max WebGL abs diff: `{checks.get('max_webgl_abs_diff')}`",
        f"- Max WebGL mean diff: `{checks.get('max_webgl_mean_abs_diff')}`",
        f"- Runtime GIF bytes: `{format_bytes(checks.get('runtime_gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Oracle Max | WebGL Max | Runtime | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('oracle', {}).get('max_abs_diff')} | {frame.get('webgl', {}).get('max_abs_diff')} | "
            f"`{frame.get('renderer_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Use this renderer-side consumer as the production import path gate.", ""])
    return "\n".join(lines)


def build_preview(args):
    require_pillow()
    root = os.getcwd()
    preview_path = require_file(resolve_path(args.import_preview, root), "runtime import preview")
    preview = read_json(preview_path)
    if preview.get("schema") != "lsfs_mitsuba_low_frequency_runtime_import_preview":
        raise SystemExit(f"{args.import_preview}: expected lsfs_mitsuba_low_frequency_runtime_import_preview schema")
    if preview.get("status") != "ready":
        raise SystemExit(f"{args.import_preview}: import preview status is {preview.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    renderer_dir = os.path.join(out_dir, "renderer_runtime")
    diff_dir = os.path.join(out_dir, "diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (renderer_dir, diff_dir, strip_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    contract = preview.get("runtime_contract") or {}
    gain = float((contract.get("parameters") or {}).get("texture_gain", args.texture_gain))
    frames = []
    renderer_paths = []
    strip_paths = []
    missing = []
    dimension_mismatches = []
    for index, frame in enumerate(preview.get("frames") or []):
        bindings = frame.get("runtime_bindings") or {}
        proof = frame.get("proof") or {}
        paths = {
            "base_rgb": source_path(bindings.get("base_rgb"), root),
            "positive_delta_rgb": source_path(bindings.get("positive_delta_rgb"), root),
            "negative_delta_rgb": source_path(bindings.get("negative_delta_rgb"), root),
            "oracle": source_path(frame.get("oracle"), root),
            "webgl_frame": source_path(proof.get("webgl_frame"), root),
        }
        absent = [key for key, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        base = Image.open(paths["base_rgb"]).convert("RGB")
        positive = Image.open(paths["positive_delta_rgb"]).convert("RGB")
        negative = Image.open(paths["negative_delta_rgb"]).convert("RGB")
        oracle = Image.open(paths["oracle"]).convert("RGB")
        webgl = Image.open(paths["webgl_frame"]).convert("RGB")
        if any(image.size != base.size for image in (positive, negative, oracle, webgl)):
            dimension_mismatches.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame")})
            continue
        renderer = blend_delta(base, positive, negative, gain)
        oracle_stats = diff_stats(renderer, oracle)
        webgl_stats = diff_stats(renderer, webgl)
        renderer_path = os.path.join(renderer_dir, f"frame_{index:04d}.png")
        oracle_diff_path = os.path.join(diff_dir, f"frame_{index:04d}_oracle_diff.png")
        webgl_diff_path = os.path.join(diff_dir, f"frame_{index:04d}_webgl_diff.png")
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_runtime_consumer.png")
        renderer.save(renderer_path)
        oracle_stats["diff_image"].save(oracle_diff_path)
        webgl_stats["diff_image"].save(webgl_diff_path)
        labeled_strip(
            [
                base,
                positive,
                negative,
                renderer,
                oracle,
                oracle_stats["diff_image"],
                webgl,
                webgl_stats["diff_image"],
            ],
            ["base", "positive", "negative", "renderer runtime", "oracle", "oracle diff x8", "webgl proof", "webgl diff x8"],
            strip_path,
        )
        renderer_paths.append(renderer_path)
        strip_paths.append(strip_path)
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "ready": frame.get("ready"),
            "renderer_path": os.path.abspath(renderer_path),
            "renderer_repo_path": posix_rel(renderer_path, root),
            "renderer_sha256": sha256_file(renderer_path),
            "renderer_size": os.path.getsize(renderer_path),
            "strip_repo_path": posix_rel(strip_path, root),
            "oracle_diff_repo_path": posix_rel(oracle_diff_path, root),
            "webgl_diff_repo_path": posix_rel(webgl_diff_path, root),
            "runtime_bindings": {
                "base_rgb": bindings.get("base_rgb", {}).get("repo_path"),
                "positive_delta_rgb": bindings.get("positive_delta_rgb", {}).get("repo_path"),
                "negative_delta_rgb": bindings.get("negative_delta_rgb", {}).get("repo_path"),
            },
            "oracle": {
                "repo_path": frame.get("oracle", {}).get("repo_path"),
                "mean_abs_diff": oracle_stats["mean_abs_diff"],
                "max_abs_diff": oracle_stats["max_abs_diff"],
                "mismatched_coverage": oracle_stats["mismatched_coverage"],
            },
            "webgl": {
                "repo_path": proof.get("webgl_frame", {}).get("repo_path"),
                "mean_abs_diff": webgl_stats["mean_abs_diff"],
                "max_abs_diff": webgl_stats["max_abs_diff"],
                "mismatched_coverage": webgl_stats["mismatched_coverage"],
            },
        })

    if not frames:
        raise SystemExit("no renderer runtime frames were produced")
    runtime_gif_path = os.path.join(assets_dir, "shot.gif")
    strip_gif_path = os.path.join(assets_dir, "runtime_consumer_strips.gif")
    write_gif(renderer_paths, runtime_gif_path, args.fps)
    write_gif(strip_paths, strip_gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(frames) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [
        copy_asset(runtime_gif_path, assets_dir, "shot.gif", "Renderer Runtime GIF", root),
        copy_asset(strip_gif_path, assets_dir, "runtime_consumer_strips.gif", "Runtime Strip GIF", root),
    ]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(frames[frame_index]["renderer_repo_path"], assets_dir, f"keyframe_{out_index:02d}.png", f"Runtime Keyframe {out_index + 1}", root))
        assets.append(copy_asset(frames[frame_index]["strip_repo_path"], assets_dir, f"runtime_strip_{out_index:02d}.png", f"Runtime Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    checks = {
        "source_status": preview.get("status"),
        "source_frames": len(preview.get("frames") or []),
        "frames": len(frames),
        "missing_references": len(missing),
        "dimension_mismatches": len(dimension_mismatches),
        "max_oracle_abs_diff": max((frame["oracle"]["max_abs_diff"] for frame in frames), default=0),
        "max_oracle_mean_abs_diff": max((frame["oracle"]["mean_abs_diff"] for frame in frames), default=0.0),
        "max_oracle_mismatched_coverage": max((frame["oracle"]["mismatched_coverage"] for frame in frames), default=0.0),
        "max_webgl_abs_diff": max((frame["webgl"]["max_abs_diff"] for frame in frames), default=0),
        "max_webgl_mean_abs_diff": max((frame["webgl"]["mean_abs_diff"] for frame in frames), default=0.0),
        "max_webgl_mismatched_coverage": max((frame["webgl"]["mismatched_coverage"] for frame in frames), default=0.0),
        "runtime_gif_bytes": os.path.getsize(runtime_gif_path),
        "strip_gif_bytes": os.path.getsize(strip_gif_path),
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
    status = "ready" if (
        checks["frames"] == checks["source_frames"]
        and checks["missing_references"] == 0
        and checks["dimension_mismatches"] == 0
        and checks["max_oracle_abs_diff"] <= args.max_abs_tolerance
        and checks["max_webgl_abs_diff"] <= args.max_abs_tolerance
        and checks["max_oracle_mean_abs_diff"] <= args.mean_abs_tolerance
        and checks["max_webgl_mean_abs_diff"] <= args.mean_abs_tolerance
    ) else "review"
    summary = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_runtime_preview",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source": {
            "runtime_import_preview": posix_rel(preview_path, root),
            "runtime_import_preview_sha256": sha256_file(preview_path),
            "runtime_import_preview_schema": preview.get("schema"),
            "runtime_import_preview_status": preview.get("status"),
        },
        "settings": {
            "texture_gain": gain,
            "stage": "renderer_post_tonemap_low_frequency_runtime_consumer",
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "missing_references": missing,
        "dimension_mismatches": dimension_mismatches,
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        summary_metadata_entry(summary_path, assets_dir, root),
        copy_asset(preview_path, assets_dir, "runtime_import_preview.json", "Runtime Import Preview", root),
    ]
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
    os.makedirs(os.path.dirname(resolve_path(metadata_files[0]["repo_path"], root)), exist_ok=True)
    shutil.copy2(summary_path, resolve_path(metadata_files[0]["repo_path"], root))
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_renderer_runtime_preview_gallery",
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
        f"status={status} frames={checks['frames']} oracle_max={checks['max_oracle_abs_diff']} "
        f"webgl_max={checks['max_webgl_abs_diff']} summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build low-frequency renderer runtime previews from an import manifest")
    parser.add_argument("import_preview")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--texture-gain", type=float, default=1.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--fail-on-review", action="store_true")
    parser.add_argument("--title", default="S497 Mitsuba Low Frequency Renderer Runtime Preview")
    parser.add_argument("--next", default="Wire this renderer-side runtime consumer into the production preview/export runner.")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    build_preview(args)


if __name__ == "__main__":
    main()
