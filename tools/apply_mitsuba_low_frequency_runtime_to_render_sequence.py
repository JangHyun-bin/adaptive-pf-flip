#!/usr/bin/env python
"""Apply low-frequency runtime deltas across a full Mitsuba render sequence."""

import argparse
import html
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from apply_mitsuba_low_frequency_runtime_to_render import (
    copy_asset,
    image_entry,
    render_frame_map,
    resolve_path,
    source_path,
)
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


def output_frame_value(frame):
    value = frame.get("output_frame")
    if value is None:
        value = frame.get("frame")
    return int(value)


def preview_path(render_frame, root):
    preview = (render_frame or {}).get("preview") or {}
    return source_path(preview, root)


def runtime_binding_paths(runtime_frame, root):
    bindings = runtime_frame.get("runtime_bindings") or {}
    return {
        "positive_delta_rgb": source_path(bindings.get("positive_delta_rgb"), root),
        "negative_delta_rgb": source_path(bindings.get("negative_delta_rgb"), root),
    }


def runtime_anchor(runtime_frame, root):
    paths = runtime_binding_paths(runtime_frame, root)
    missing = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
    if missing:
        raise SystemExit(
            f"runtime frame {runtime_frame.get('frame')} output {runtime_frame.get('output_frame')} "
            f"missing bindings: {', '.join(missing)}"
        )
    return {
        "frame": runtime_frame.get("frame"),
        "output_frame": output_frame_value(runtime_frame),
        "runtime_frame": runtime_frame,
        "positive_path": paths["positive_delta_rgb"],
        "negative_path": paths["negative_delta_rgb"],
    }


def find_bracket(anchors, output_frame):
    if output_frame <= anchors[0]["output_frame"]:
        return anchors[0], anchors[0], 0.0
    if output_frame >= anchors[-1]["output_frame"]:
        return anchors[-1], anchors[-1], 0.0
    previous = anchors[0]
    for current in anchors[1:]:
        if output_frame == current["output_frame"]:
            return current, current, 0.0
        if output_frame < current["output_frame"]:
            span = current["output_frame"] - previous["output_frame"]
            t = (output_frame - previous["output_frame"]) / float(span)
            return previous, current, t
        previous = current
    return anchors[-1], anchors[-1], 0.0


def lerp_image(path_a, path_b, t, size):
    image_a = Image.open(path_a).convert("RGB")
    image_b = Image.open(path_b).convert("RGB")
    if image_a.size != size or image_b.size != size:
        raise ValueError(f"delta dimensions do not match raw frame: {image_a.size}, {image_b.size}, raw={size}")
    if t <= 0.0 or os.path.abspath(path_a) == os.path.abspath(path_b):
        return image_a.copy()
    if t >= 1.0:
        return image_b.copy()
    return Image.blend(image_a, image_b, t)


def html_page(title, summary, assets, metadata_files):
    shot = next((item for item in assets if item.get("label") == "Corrected Sequence GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Sequence Strip")]
    keyframes = [item for item in assets if item.get("label", "").startswith("Corrected Sequence Keyframe")]
    checks = summary.get("checks") or {}
    links = "\n".join(
        f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>'
        for item in metadata_files
    )
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Anchors", checks.get("runtime_anchor_frames")),
        ("Interpolated", checks.get("interpolated_frames")),
        ("Max change", checks.get("max_corrected_abs_diff")),
        ("Mean change", checks.get("max_corrected_mean_abs_diff")),
    ]
    metrics_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metrics
    )
    hero = f'<section class="hero"><img src="{html.escape(shot["href"])}" alt="Corrected sequence GIF"></section>' if shot else ""
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
    :root {{ color-scheme: dark; --bg: #071015; --panel: #111b22; --line: #2b3d47; --ink: #edf8fb; --muted: #9cb0bb; --accent: #91dcff; }}
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
        f"- Runtime anchor frames: `{checks.get('runtime_anchor_frames')}`",
        f"- Frames corrected: `{checks.get('frames')}`",
        f"- Interpolated frames: `{checks.get('interpolated_frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Dimension mismatches: `{checks.get('dimension_mismatches')}`",
        f"- Max corrected abs diff: `{checks.get('max_corrected_abs_diff')}`",
        f"- Max corrected mean abs diff: `{checks.get('max_corrected_mean_abs_diff')}`",
        f"- Corrected bytes: `{format_bytes(checks.get('corrected_bytes', 0))}`",
        f"- Corrected GIF bytes: `{format_bytes(checks.get('corrected_gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Bracket | t | Mean Change | Max Change | Raw | Corrected | Strip |",
        "| ---: | ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        bracket = frame.get("runtime_bracket") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{bracket.get('previous_output_frame')}->{bracket.get('next_output_frame')} | {bracket.get('t')} | "
            f"{frame.get('corrected_change', {}).get('mean_abs_diff')} | {frame.get('corrected_change', {}).get('max_abs_diff')} | "
            f"`{frame.get('raw_repo_path')}` | `{frame.get('corrected_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Publish this corrected full-sequence render review gallery.", ""])
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
    anchors = [runtime_anchor(frame, root) for frame in preview.get("frames") or []]
    anchors.sort(key=lambda item: item["output_frame"])
    if len(anchors) < 2:
        raise SystemExit("at least two runtime frames are required for sequence interpolation")
    contract_gain = ((preview.get("runtime_contract") or {}).get("parameters") or {}).get("texture_gain")
    gain = float(args.texture_gain if args.override_texture_gain else (contract_gain if contract_gain is not None else args.texture_gain))

    frames = []
    corrected_paths = []
    strip_paths = []
    missing = []
    dimension_mismatches = []
    interpolation_failures = []
    corrected_bytes = 0
    render_items = sorted(render.get("frames") or [], key=output_frame_value)
    if args.frames:
        wanted = {int(value.strip()) for value in args.frames.split(",") if value.strip()}
        render_items = [frame for frame in render_items if output_frame_value(frame) in wanted]
    for index, render_frame in enumerate(render_items):
        output_frame = output_frame_value(render_frame)
        raw_path = preview_path(render_frame, root)
        if not raw_path or not os.path.isfile(raw_path):
            missing.append({"frame": index, "output_frame": output_frame, "missing": ["raw"]})
            continue
        raw = Image.open(raw_path).convert("RGB")
        previous, next_anchor, t = find_bracket(anchors, output_frame)
        try:
            positive = lerp_image(previous["positive_path"], next_anchor["positive_path"], t, raw.size)
            negative = lerp_image(previous["negative_path"], next_anchor["negative_path"], t, raw.size)
        except ValueError as exc:
            dimension_mismatches.append({"frame": index, "output_frame": output_frame, "error": str(exc)})
            continue
        except OSError as exc:
            interpolation_failures.append({"frame": index, "output_frame": output_frame, "error": str(exc)})
            continue

        corrected = blend_delta(raw, positive, negative, gain)
        change = diff_stats(corrected, raw)
        corrected_path = os.path.join(corrected_dir, f"frame_{output_frame:04d}.png")
        diff_path = os.path.join(diff_dir, f"frame_{output_frame:04d}_corrected_minus_raw.png")
        strip_path = os.path.join(strip_dir, f"frame_{output_frame:04d}_low_frequency_sequence_adapter.png")
        corrected.save(corrected_path)
        change["diff_image"].save(diff_path)
        labeled_strip(
            [raw, positive, negative, corrected, change["diff_image"]],
            ["raw render", "positive interp", "negative interp", "corrected render", "change x8"],
            strip_path,
        )
        corrected_bytes += os.path.getsize(corrected_path)
        corrected_paths.append(corrected_path)
        strip_paths.append(strip_path)
        frames.append({
            "frame": index,
            "output_frame": output_frame,
            "render_sequence_frame": render_frame.get("sequence_frame"),
            "raw_repo_path": posix_rel(raw_path, root),
            "corrected_repo_path": posix_rel(corrected_path, root),
            "corrected_sha256": sha256_file(corrected_path),
            "corrected_size": os.path.getsize(corrected_path),
            "strip_repo_path": posix_rel(strip_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "runtime_bracket": {
                "previous_output_frame": previous["output_frame"],
                "next_output_frame": next_anchor["output_frame"],
                "t": round(t, 6),
            },
            "corrected_change": {
                "mean_abs_diff": change["mean_abs_diff"],
                "max_abs_diff": change["max_abs_diff"],
                "mismatched_coverage": change["mismatched_coverage"],
            },
        })

    if not frames:
        raise SystemExit("no corrected frames were produced")

    corrected_gif = os.path.join(assets_dir, "shot.gif")
    strip_gif = os.path.join(assets_dir, "sequence_strips.gif")
    write_gif(corrected_paths, corrected_gif, args.fps)
    write_gif(strip_paths, strip_gif, args.fps)
    key_indices = sorted(set(round(i * (len(frames) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [
        copy_asset(corrected_gif, os.path.join(assets_dir, "shot.gif"), "Corrected Sequence GIF", root, "assets/shot.gif"),
        copy_asset(strip_gif, os.path.join(assets_dir, "sequence_strips.gif"), "Sequence Strip GIF", root, "assets/sequence_strips.gif"),
    ]
    for out_index, frame_index in enumerate(key_indices):
        frame = frames[frame_index]
        assets.append(copy_asset(frame["corrected_repo_path"], os.path.join(assets_dir, f"keyframe_{out_index:02d}.png"), f"Corrected Sequence Keyframe {out_index + 1}", root, f"assets/keyframe_{out_index:02d}.png"))
        assets.append(copy_asset(frame["strip_repo_path"], os.path.join(assets_dir, f"sequence_strip_{out_index:02d}.png"), f"Sequence Strip {out_index + 1}", root, f"assets/sequence_strip_{out_index:02d}.png"))

    exact_anchor_outputs = {anchor["output_frame"] for anchor in anchors}
    checks = {
        "render_source_frames": len(render.get("frames") or []),
        "runtime_anchor_frames": len(anchors),
        "frames": len(frames),
        "exact_anchor_frames": sum(1 for frame in frames if frame["output_frame"] in exact_anchor_outputs),
        "interpolated_frames": sum(1 for frame in frames if frame["output_frame"] not in exact_anchor_outputs),
        "missing_references": len(missing),
        "dimension_mismatches": len(dimension_mismatches),
        "interpolation_failures": len(interpolation_failures),
        "max_corrected_abs_diff": max((frame["corrected_change"]["max_abs_diff"] for frame in frames), default=0),
        "max_corrected_mean_abs_diff": max((frame["corrected_change"]["mean_abs_diff"] for frame in frames), default=0.0),
        "max_corrected_mismatched_coverage": max((frame["corrected_change"]["mismatched_coverage"] for frame in frames), default=0.0),
        "corrected_bytes": corrected_bytes,
        "corrected_gif_bytes": os.path.getsize(corrected_gif),
        "strip_gif_bytes": os.path.getsize(strip_gif),
    }
    status = "ready" if (
        checks["frames"] > 0
        and checks["missing_references"] == 0
        and checks["dimension_mismatches"] == 0
        and checks["interpolation_failures"] == 0
    ) else "review"
    summary_path = os.path.abspath(args.summary)
    summary = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter",
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
            "stage": "post_tonemap_low_frequency_runtime_render_sequence_adapter",
            "fps": args.fps,
            "keyframes": args.keyframes,
            "frames_filter": args.frames,
        },
        "checks": checks,
        "missing_references": missing,
        "dimension_mismatches": dimension_mismatches,
        "interpolation_failures": interpolation_failures,
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        copy_asset(summary_path, os.path.join(assets_dir, "runtime_render_sequence_adapter_summary.json"), "Runtime Render Sequence Adapter Summary", root, "assets/runtime_render_sequence_adapter_summary.json"),
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
        "schema": "lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter_gallery",
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
        f"status={status} frames={checks['frames']} interpolated={checks['interpolated_frames']} "
        f"max_change={checks['max_corrected_abs_diff']} summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply low-frequency runtime deltas across a full Mitsuba render sequence")
    parser.add_argument("render_manifest")
    parser.add_argument("runtime_import_preview")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--texture-gain", type=float, default=1.0)
    parser.add_argument("--override-texture-gain", action="store_true")
    parser.add_argument("--fps", type=float, default=8.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--frames", help="optional comma-separated output frame filter")
    parser.add_argument("--fail-on-review", action="store_true")
    parser.add_argument("--title", default="Mitsuba Low Frequency Runtime Render Sequence Adapter")
    parser.add_argument("--next", default="Publish this corrected full-sequence render review gallery.")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run_adapter(args)


if __name__ == "__main__":
    main()
