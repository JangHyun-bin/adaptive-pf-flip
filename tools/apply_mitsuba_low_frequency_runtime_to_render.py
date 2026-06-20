#!/usr/bin/env python
"""Apply low-frequency runtime deltas to an existing Mitsuba render manifest."""

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
from build_mitsuba_low_frequency_parity_texture_package import diff_stats, write_gif
from build_mitsuba_low_frequency_renderer_runtime_preview import blend_delta, labeled_strip


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to apply low-frequency runtime deltas")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def source_path(item, root):
    return resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)


def image_entry(path, root):
    entry = {
        "path": os.path.abspath(path),
        "repo_path": posix_rel(os.path.abspath(path), root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def copy_asset(src, dest, label, root, href):
    source = require_file(resolve_path(src, root), label)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(source) != os.path.abspath(dest):
        shutil.copy2(source, dest)
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": href,
        "source_repo_path": posix_rel(source, root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def render_frame_map(render):
    frames = {}
    for frame in render.get("frames") or []:
        output_frame = frame.get("output_frame")
        if output_frame is not None:
            frames[int(output_frame)] = frame
    return frames


def html_page(title, summary, assets, metadata_files):
    shot = next((item for item in assets if item.get("label") == "Corrected GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Correction Strip")]
    keyframes = [item for item in assets if item.get("label", "").startswith("Corrected Keyframe")]
    checks = summary.get("checks") or {}
    links = "\n".join(
        f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>'
        for item in metadata_files
    )
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Missing", checks.get("missing_references")),
        ("Dim mismatches", checks.get("dimension_mismatches")),
        ("Max change", checks.get("max_corrected_abs_diff")),
        ("Mean change", checks.get("max_corrected_mean_abs_diff")),
    ]
    metrics_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metrics
    )
    hero = f'<section class="hero"><img src="{html.escape(shot["href"])}" alt="Corrected GIF"></section>' if shot else ""
    strip_html = "\n".join(
        f'<figure><a href="{html.escape(item["href"])}"><img src="{html.escape(item["href"])}" alt="{html.escape(item["label"])}"></a><figcaption>{html.escape(item["label"])}</figcaption></figure>'
        for item in strips
    )
    key_html = "\n".join(
        f'<figure><a href="{html.escape(item["href"])}"><img src="{html.escape(item["href"])}" alt="{html.escape(item["label"])}"></a><figcaption>{html.escape(item["label"])}</figcaption></figure>'
        for item in keyframes
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
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); overflow: auto; }}
    figure img {{ width: 100%; min-width: 920px; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{html.escape(title)}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{metrics_html}</section>
    <section class="grid">{key_html}{strip_html}</section>
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
        f"- Render manifest: `{summary['sources']['render_manifest']['repo_path']}`",
        f"- Runtime import preview: `{summary['sources']['runtime_import_preview']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Render source frames: `{checks.get('render_source_frames')}`",
        f"- Runtime source frames: `{checks.get('runtime_source_frames')}`",
        f"- Frames corrected: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Dimension mismatches: `{checks.get('dimension_mismatches')}`",
        f"- Max corrected abs diff: `{checks.get('max_corrected_abs_diff')}`",
        f"- Max corrected mean abs diff: `{checks.get('max_corrected_mean_abs_diff')}`",
        f"- Corrected bytes: `{format_bytes(checks.get('corrected_bytes', 0))}`",
        f"- Corrected GIF bytes: `{format_bytes(checks.get('corrected_gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Mean Change | Max Change | Raw | Corrected | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('corrected_change', {}).get('mean_abs_diff')} | {frame.get('corrected_change', {}).get('max_abs_diff')} | "
            f"`{frame.get('raw_repo_path')}` | `{frame.get('corrected_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Publish this corrected render review gallery.", ""])
    return "\n".join(lines)


def run_adapter(args):
    require_pillow()
    root = os.getcwd()
    render_manifest_path = require_file(resolve_path(args.render_manifest, root), "Mitsuba render manifest")
    runtime_preview_path = require_file(resolve_path(args.runtime_import_preview, root), "runtime import preview")
    render = read_json(render_manifest_path)
    preview = read_json(runtime_preview_path)
    if preview.get("schema") != "lsfs_mitsuba_low_frequency_runtime_import_preview":
        raise SystemExit(f"{args.runtime_import_preview}: expected lsfs_mitsuba_low_frequency_runtime_import_preview schema")
    if preview.get("status") != "ready":
        raise SystemExit(f"{args.runtime_import_preview}: runtime preview status is {preview.get('status')!r}")
    if render.get("failures"):
        raise SystemExit(f"{args.render_manifest}: render manifest has failures")

    out_dir = os.path.abspath(args.out_dir)
    corrected_dir = os.path.join(out_dir, "corrected")
    strip_dir = os.path.join(out_dir, "strips")
    diff_dir = os.path.join(out_dir, "diffs")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (corrected_dir, strip_dir, diff_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    render_frames = render_frame_map(render)
    contract_gain = ((preview.get("runtime_contract") or {}).get("parameters") or {}).get("texture_gain")
    gain = float(args.texture_gain if args.override_texture_gain else (contract_gain if contract_gain is not None else args.texture_gain))
    frames = []
    corrected_paths = []
    strip_paths = []
    missing = []
    dimension_mismatches = []
    corrected_bytes = 0
    for index, runtime_frame in enumerate(preview.get("frames") or []):
        output_frame = runtime_frame.get("output_frame")
        render_frame = render_frames.get(int(output_frame)) if output_frame is not None else None
        bindings = runtime_frame.get("runtime_bindings") or {}
        paths = {
            "raw": source_path((render_frame or {}).get("preview"), root),
            "positive_delta_rgb": source_path(bindings.get("positive_delta_rgb"), root),
            "negative_delta_rgb": source_path(bindings.get("negative_delta_rgb"), root),
            "oracle": source_path(runtime_frame.get("oracle"), root),
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": runtime_frame.get("frame"), "output_frame": output_frame, "missing": absent})
            continue

        raw = Image.open(paths["raw"]).convert("RGB")
        positive = Image.open(paths["positive_delta_rgb"]).convert("RGB")
        negative = Image.open(paths["negative_delta_rgb"]).convert("RGB")
        oracle = Image.open(paths["oracle"]).convert("RGB")
        if any(image.size != raw.size for image in (positive, negative, oracle)):
            dimension_mismatches.append({
                "frame": runtime_frame.get("frame"),
                "output_frame": output_frame,
                "raw_size": raw.size,
                "positive_size": positive.size,
                "negative_size": negative.size,
                "oracle_size": oracle.size,
            })
            continue

        corrected = blend_delta(raw, positive, negative, gain)
        change = diff_stats(corrected, raw)
        oracle_gap = diff_stats(corrected, oracle)
        corrected_path = os.path.join(corrected_dir, f"frame_{index:04d}.png")
        diff_path = os.path.join(diff_dir, f"frame_{index:04d}_corrected_minus_raw.png")
        oracle_diff_path = os.path.join(diff_dir, f"frame_{index:04d}_corrected_minus_oracle.png")
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_low_frequency_render_adapter.png")
        corrected.save(corrected_path)
        change["diff_image"].save(diff_path)
        oracle_gap["diff_image"].save(oracle_diff_path)
        labeled_strip(
            [raw, positive, negative, corrected, change["diff_image"], oracle, oracle_gap["diff_image"]],
            ["raw render", "positive", "negative", "corrected render", "change x8", "runtime oracle", "oracle gap x8"],
            strip_path,
        )
        corrected_bytes += os.path.getsize(corrected_path)
        corrected_paths.append(corrected_path)
        strip_paths.append(strip_path)
        frames.append({
            "frame": runtime_frame.get("frame"),
            "output_frame": output_frame,
            "render_sequence_frame": (render_frame or {}).get("sequence_frame"),
            "raw_repo_path": posix_rel(paths["raw"], root),
            "corrected_repo_path": posix_rel(corrected_path, root),
            "corrected_sha256": sha256_file(corrected_path),
            "corrected_size": os.path.getsize(corrected_path),
            "strip_repo_path": posix_rel(strip_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "oracle_diff_repo_path": posix_rel(oracle_diff_path, root),
            "runtime_bindings": {
                "positive_delta_rgb": bindings.get("positive_delta_rgb", {}).get("repo_path"),
                "negative_delta_rgb": bindings.get("negative_delta_rgb", {}).get("repo_path"),
            },
            "corrected_change": {
                "mean_abs_diff": change["mean_abs_diff"],
                "max_abs_diff": change["max_abs_diff"],
                "mismatched_coverage": change["mismatched_coverage"],
            },
            "oracle_gap": {
                "repo_path": runtime_frame.get("oracle", {}).get("repo_path"),
                "mean_abs_diff": oracle_gap["mean_abs_diff"],
                "max_abs_diff": oracle_gap["max_abs_diff"],
                "mismatched_coverage": oracle_gap["mismatched_coverage"],
            },
        })

    if not frames:
        raise SystemExit("no corrected frames were produced")

    corrected_gif = os.path.join(assets_dir, "shot.gif")
    strip_gif = os.path.join(assets_dir, "correction_strips.gif")
    write_gif(corrected_paths, corrected_gif, args.fps)
    write_gif(strip_paths, strip_gif, args.fps)
    key_indices = sorted(set(round(i * (len(frames) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [
        copy_asset(corrected_gif, os.path.join(assets_dir, "shot.gif"), "Corrected GIF", root, "assets/shot.gif"),
        copy_asset(strip_gif, os.path.join(assets_dir, "correction_strips.gif"), "Correction Strip GIF", root, "assets/correction_strips.gif"),
    ]
    for out_index, frame_index in enumerate(key_indices):
        frame = frames[frame_index]
        assets.append(copy_asset(frame["corrected_repo_path"], os.path.join(assets_dir, f"keyframe_{out_index:02d}.png"), f"Corrected Keyframe {out_index + 1}", root, f"assets/keyframe_{out_index:02d}.png"))
        assets.append(copy_asset(frame["strip_repo_path"], os.path.join(assets_dir, f"correction_strip_{out_index:02d}.png"), f"Correction Strip {out_index + 1}", root, f"assets/correction_strip_{out_index:02d}.png"))

    summary_path = os.path.abspath(args.summary)
    checks = {
        "render_source_frames": len(render.get("frames") or []),
        "runtime_source_frames": len(preview.get("frames") or []),
        "frames": len(frames),
        "missing_references": len(missing),
        "dimension_mismatches": len(dimension_mismatches),
        "max_corrected_abs_diff": max((frame["corrected_change"]["max_abs_diff"] for frame in frames), default=0),
        "max_corrected_mean_abs_diff": max((frame["corrected_change"]["mean_abs_diff"] for frame in frames), default=0.0),
        "max_corrected_mismatched_coverage": max((frame["corrected_change"]["mismatched_coverage"] for frame in frames), default=0.0),
        "max_oracle_gap_abs_diff": max((frame["oracle_gap"]["max_abs_diff"] for frame in frames), default=0),
        "max_oracle_gap_mean_abs_diff": max((frame["oracle_gap"]["mean_abs_diff"] for frame in frames), default=0.0),
        "corrected_bytes": corrected_bytes,
        "corrected_gif_bytes": os.path.getsize(corrected_gif),
        "strip_gif_bytes": os.path.getsize(strip_gif),
    }
    status = "ready" if (
        checks["frames"] > 0
        and checks["missing_references"] == 0
        and checks["dimension_mismatches"] == 0
    ) else "review"
    summary = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_render_adapter",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "sources": {
            "render_manifest": image_entry(render_manifest_path, root),
            "runtime_import_preview": image_entry(runtime_preview_path, root),
        },
        "settings": {
            "texture_gain": gain,
            "contract_texture_gain": contract_gain,
            "override_texture_gain": args.override_texture_gain,
            "stage": "post_tonemap_low_frequency_runtime_render_adapter",
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
        copy_asset(summary_path, os.path.join(assets_dir, "runtime_render_adapter_summary.json"), "Runtime Render Adapter Summary", root, "assets/runtime_render_adapter_summary.json"),
        copy_asset(render_manifest_path, os.path.join(assets_dir, "mitsuba_render_manifest.json"), "Mitsuba Render Manifest", root, "assets/mitsuba_render_manifest.json"),
        copy_asset(runtime_preview_path, os.path.join(assets_dir, "runtime_import_preview.json"), "Runtime Import Preview", root, "assets/runtime_import_preview.json"),
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
    shutil.copy2(summary_path, resolve_path(metadata_files[0]["repo_path"], root))
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_runtime_render_adapter_gallery",
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
        f"status={status} frames={checks['frames']} max_change={checks['max_corrected_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply low-frequency runtime deltas to an existing Mitsuba render manifest")
    parser.add_argument("render_manifest")
    parser.add_argument("runtime_import_preview")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--texture-gain", type=float, default=1.0)
    parser.add_argument("--override-texture-gain", action="store_true")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--fail-on-review", action="store_true")
    parser.add_argument("--title", default="Mitsuba Low Frequency Runtime Render Adapter")
    parser.add_argument("--next", default="Publish this corrected render review gallery.")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run_adapter(args)


if __name__ == "__main__":
    main()
