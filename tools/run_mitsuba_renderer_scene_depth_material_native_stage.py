#!/usr/bin/env python
"""Run the selected scene-depth material target through a renderer-stage adapter."""

import argparse
import os
import time
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
from build_mitsuba_low_frequency_parity_texture_package import diff_stats
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    ImageOps,
    copy_asset,
    labeled_strip,
    preview_image,
    require_pillow,
    resolve_path,
    write_gif,
)


def ref_path(ref, root):
    if not isinstance(ref, dict):
        return None
    return resolve_path(ref.get("path") or ref.get("repo_path"), root)


def file_entry(path, root):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def target_frames(target):
    return sorted(target.get("frames") or [], key=lambda item: int(item.get("frame") or 0))


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "Native Stage GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Native Stage Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Passed", checks.get("passed_frames")),
            ("Max diff", checks.get("max_abs_diff")),
            ("Mean diff", f"{checks.get('max_mean_abs_diff', 0.0):.6f}"),
            ("Elapsed", f"{checks.get('elapsed_ms', 0.0):.1f} ms"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="native stage gif"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 16px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; overflow-x: auto; margin: 0 0 12px; }}
    img {{ display: block; max-width: none; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Renderer-stage adapter proof that consumes the S585 selected target controls and reproduces the target previews.</p>
  <section class="tiles">{tiles}</section>
  {hero}
  <section>{figures}</section>
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
        f"- Passed frames: `{checks.get('passed_frames')}`",
        f"- Failed frames: `{checks.get('failed_frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max absolute diff vs S585 target: `{checks.get('max_abs_diff')}`",
        f"- Max mean diff vs S585 target: `{checks.get('max_mean_abs_diff')}`",
        f"- Max native delta from source: `{checks.get('max_native_delta_from_source')}`",
        f"- Output bytes: `{format_bytes(checks.get('output_bytes', 0))}`",
        f"- Elapsed milliseconds: `{checks.get('elapsed_ms')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Strength | Max Diff | Mean Diff | Native | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{(frame.get('control') or {}).get('effective_strength')} | "
            f"{frame.get('diff', {}).get('max_abs_diff')} | "
            f"{frame.get('diff', {}).get('mean_abs_diff')} | "
            f"`{frame.get('native_output', {}).get('repo_path')}` | "
            f"`{frame.get('strip', {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def run_frame(frame, root, frames_dir, strips_dir):
    frame_id = int(frame.get("frame") or 0)
    refs = frame.get("references") or {}
    source_path = ref_path(refs.get("source_composite"), root)
    magnitude_path = ref_path(refs.get("magnitude_mask"), root)
    target_path = ref_path(refs.get("target_preview"), root)
    missing = [
        name for name, path in (
            ("source_composite", source_path),
            ("magnitude_mask", magnitude_path),
            ("target_preview", target_path),
        )
        if not path or not os.path.isfile(path)
    ]
    if missing:
        return {"status": "failed", "frame": frame_id, "missing": missing}

    source = Image.open(source_path).convert("RGB")
    magnitude = Image.open(magnitude_path).convert("L")
    target = Image.open(target_path).convert("RGB")
    if source.size != magnitude.size or source.size != target.size:
        return {"status": "failed", "frame": frame_id, "missing": ["dimension_mismatch"]}

    started = time.perf_counter()
    control = frame.get("control") or {}
    strength = float(control.get("effective_strength") or 0.0)
    native, native_delta = preview_image(source, magnitude, strength)
    diff = diff_stats(native, target)
    native_path = os.path.abspath(os.path.join(frames_dir, f"frame_{frame_id:04d}.png"))
    strip_path = os.path.abspath(os.path.join(strips_dir, f"frame_{frame_id:04d}_native_stage.png"))
    os.makedirs(os.path.dirname(native_path), exist_ok=True)
    os.makedirs(os.path.dirname(strip_path), exist_ok=True)
    native.save(native_path)
    mask_visual = ImageOps.colorize(magnitude, black=(6, 12, 18), white=(255, 218, 120))
    labeled_strip(
        [source, mask_visual, native, target, diff["diff_image"]],
        ["source composite", "magnitude mask", "native stage", "S585 target", "target diff x8"],
        strip_path,
    )
    status = "passed" if diff["max_abs_diff"] == 0 and diff["mean_abs_diff"] == 0.0 else "failed"
    return {
        "status": status,
        "frame": frame_id,
        "output_frame": frame.get("output_frame"),
        "control": control,
        "native_delta_from_source": native_delta,
        "diff": {
            "max_abs_diff": diff["max_abs_diff"],
            "mean_abs_diff": diff["mean_abs_diff"],
            "mismatched_coverage": diff["mismatched_coverage"],
        },
        "references": {
            "source_composite": posix_rel(source_path, root),
            "magnitude_mask": posix_rel(magnitude_path, root),
            "target_preview": posix_rel(target_path, root),
        },
        "native_output": file_entry(native_path, root),
        "strip": file_entry(strip_path, root),
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def run(args):
    require_pillow()
    root = os.getcwd()
    target_path = require_file(resolve_path(args.target_summary, root), "depth/material target summary")
    target = read_json(target_path)
    if target.get("schema") != "lsfs_mitsuba_renderer_scene_depth_material_target":
        raise SystemExit(f"{args.target_summary}: expected lsfs_mitsuba_renderer_scene_depth_material_target schema")
    if target.get("status") != "ready":
        raise SystemExit(f"{args.target_summary}: target status is {target.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    strips_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (frames_dir, strips_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    started = time.perf_counter()
    frames = [run_frame(frame, root, frames_dir, strips_dir) for frame in target_frames(target)]
    passed = [frame for frame in frames if frame.get("status") == "passed"]
    failed = [frame for frame in frames if frame.get("status") != "passed"]
    output_paths = [resolve_path(frame["native_output"]["repo_path"], root) for frame in passed if frame.get("native_output")]
    strip_paths = [resolve_path(frame["strip"]["repo_path"], root) for frame in passed if frame.get("strip")]
    gif_path = os.path.join(out_dir, "native_stage.gif")
    strip_gif_path = os.path.join(out_dir, "native_stage_strips.gif")
    if output_paths:
        write_gif(output_paths, gif_path, args.fps)
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(gif_path):
        assets.append(copy_asset(gif_path, assets_dir, "native_stage.gif", "Native Stage GIF", root))
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "native_stage_strips.gif", "Native Stage Strip GIF", root))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["strip"]["repo_path"], assets_dir, f"native_stage_strip_{out_index:02d}.png", f"Native Stage Strip {out_index + 1}", root))

    checks = {
        "frames": len(frames),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "missing_references": sum(len(frame.get("missing") or []) for frame in failed),
        "max_abs_diff": max((frame.get("diff", {}).get("max_abs_diff", 999) for frame in frames), default=999),
        "max_mean_abs_diff": max((frame.get("diff", {}).get("mean_abs_diff", 999.0) for frame in frames), default=999.0),
        "max_mismatched_coverage": max((frame.get("diff", {}).get("mismatched_coverage", 1.0) for frame in frames), default=1.0),
        "max_native_delta_from_source": max((frame.get("native_delta_from_source", {}).get("max_abs_delta", 0) for frame in frames), default=0),
        "output_bytes": sum(os.path.getsize(path) for path in output_paths if path and os.path.isfile(path)),
        "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    status = "passed" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["max_abs_diff"] <= args.max_abs_tolerance
        and checks["max_mean_abs_diff"] <= args.mean_abs_tolerance
    ) else "failed"

    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [copy_asset(target_path, assets_dir, "depth_material_target_summary.json", "Depth Material Target Summary", root)]
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_native_stage",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "backend": {
            "kind": "scene_depth_material_native_stage_adapter",
            "mode": "renderer_stage_process_proof",
            "source_contract": "S585 selected target",
        },
        "inputs": {
            "target_summary": posix_rel(target_path, root),
            "target_schema": target.get("schema"),
            "target_status": target.get("status"),
            "selected_label": (target.get("selected") or {}).get("label"),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
            "max_abs_tolerance": args.max_abs_tolerance,
            "mean_abs_tolerance": args.mean_abs_tolerance,
        },
        "checks": checks,
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": index_path,
            "index_repo_path": posix_rel(index_path, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "native_stage_summary.json", "Native Stage Summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    summary_asset = resolve_path(metadata_files[0]["repo_path"], root)
    write_json(summary_asset, summary)
    write_text(index_path, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_native_stage_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} passed={checks['passed_frames']} "
        f"max_diff={checks['max_abs_diff']} max_mean={checks['max_mean_abs_diff']:.6f} summary={summary_path}"
    )
    if status != "passed":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a scene-depth material target through a renderer-stage adapter")
    parser.add_argument("target_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="S586 Mitsuba Renderer Scene Depth Material Native Stage")
    parser.add_argument(
        "--next",
        default="Use this native-stage proof to replace the image-space target with a real renderer material or tonemap backend sample.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    run(args)


if __name__ == "__main__":
    main()
