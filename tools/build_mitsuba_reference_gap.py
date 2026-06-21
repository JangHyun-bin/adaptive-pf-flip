#!/usr/bin/env python
"""Build a renderer-target-gap summary from a render and a reference sequence."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from compare_mitsuba_renderer_target_gap import (
    diff_image,
    labeled_strip,
    max_abs_diff,
    mean_abs_diff,
    write_gif,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a reference gap")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def frame_map_from_sequence(payload, role):
    schema = payload.get("schema")
    frames = {}
    for frame in payload.get("frames") or []:
        output = frame.get("output_frame")
        if output is None:
            continue
        path = None
        if schema == "lsfs_mitsuba_xml_render":
            preview = frame.get("preview") or {}
            path = preview.get("path") or preview.get("repo_path")
        elif schema == "lsfs_mitsuba_secondary_composite":
            path = frame.get("composite_path") or frame.get("composite_repo_path")
        elif schema == "lsfs_mitsuba_renderer_scene_depth_material_target":
            target = (frame.get("references") or {}).get("target_preview") or {}
            path = target.get("path") or target.get("repo_path")
        elif schema == "lsfs_mitsuba_renderer_target_preview":
            path = frame.get("renderer_target_path") or frame.get("renderer_target_repo_path")
        else:
            raise SystemExit(f"{role}: unsupported schema {schema!r}")
        frames[output] = {
            "frame": frame.get("frame"),
            "output_frame": output,
            "path": resolve_path(path),
        }
    return frames


def source_entry(path, root, payload):
    return {
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "sha256": sha256_file(path),
    }


def copy_asset(path, out_dir, name, label, root):
    dst = os.path.join(out_dir, name)
    if os.path.abspath(path) != os.path.abspath(dst):
        shutil.copy2(path, dst)
    return {
        "label": label,
        "path": dst,
        "repo_path": posix_rel(dst, root),
        "sha256": sha256_file(dst),
        "size": os.path.getsize(dst),
    }


def markdown_report(summary):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Actual: `{summary['source']['actual']['repo_path']}`",
        f"- Reference: `{summary['source']['reference']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Mean gap MAD: `{checks.get('mean_gap_mean_abs_diff')}`",
        f"- Max gap MAD: `{checks.get('max_gap_mean_abs_diff')}`",
        f"- Max gap abs: `{checks.get('max_gap_max_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | MAD | Max Abs | Strip |",
        "| ---: | ---: | ---: | --- |",
    ]
    rows = summary.get("frames") or []
    sample_indices = sorted(set([0, len(rows) // 2, len(rows) - 1])) if rows else []
    for index in sample_indices:
        frame = rows[index]
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('gap_mean_abs_diff')} | "
            f"{frame.get('gap_max_abs_diff')} | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Use this gap summary for signed-error analysis.", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    actual_path = require_file(args.actual_summary, "actual summary")
    reference_path = require_file(args.reference_summary, "reference summary")
    actual = read_json(actual_path)
    reference = read_json(reference_path)
    actual_frames = frame_map_from_sequence(actual, "actual summary")
    reference_frames = frame_map_from_sequence(reference, "reference summary")

    out_dir = os.path.abspath(args.out_dir)
    diff_dir = os.path.join(out_dir, "diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    frames = []
    missing = []
    strip_paths = []
    for index, output in enumerate(sorted(set(actual_frames) & set(reference_frames))):
        actual_frame = actual_frames[output]
        reference_frame = reference_frames[output]
        actual_img_path = actual_frame.get("path")
        reference_img_path = reference_frame.get("path")
        if not actual_img_path or not os.path.isfile(actual_img_path) or not reference_img_path or not os.path.isfile(reference_img_path):
            missing.append({"output_frame": output, "actual": actual_img_path, "reference": reference_img_path})
            continue
        actual_img = Image.open(actual_img_path).convert("RGB")
        reference_img = Image.open(reference_img_path).convert("RGB")
        if actual_img.size != reference_img.size:
            actual_img = actual_img.resize(reference_img.size, Image.Resampling.BICUBIC)
        diff = diff_image(actual_img, reference_img)
        base_name = f"frame_{index:04d}.png"
        diff_path = os.path.join(diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        diff.save(diff_path)
        labeled_strip([actual_img, reference_img, diff], ["actual", "reference", "gap diff"], strip_path)
        strip_paths.append(strip_path)
        frames.append({
            "frame": actual_frame.get("frame"),
            "output_frame": output,
            "actual_repo_path": posix_rel(actual_img_path, root),
            "target_repo_path": posix_rel(reference_img_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "actual_sha256": sha256_file(actual_img_path),
            "target_sha256": sha256_file(reference_img_path),
            "gap_mean_abs_diff": mean_abs_diff(actual_img, reference_img),
            "gap_max_abs_diff": max_abs_diff(actual_img, reference_img),
        })

    if not frames:
        raise SystemExit("no comparable frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Gap GIF", root)]
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"gap_strip_{out_index:02d}.png", f"Gap Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "renderer_target_gap_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_renderer_target_gap",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready" if not missing else "review",
        "source": {
            "actual": source_entry(actual_path, root, actual),
            "reference": source_entry(reference_path, root, reference),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frames),
            "missing_references": len(missing),
            "mean_gap_mean_abs_diff": sum(item["gap_mean_abs_diff"] for item in frames) / len(frames),
            "max_gap_mean_abs_diff": max(item["gap_mean_abs_diff"] for item in frames),
            "max_gap_max_abs_diff": max(item["gap_max_abs_diff"] for item in frames),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "missing_references": missing,
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "assets": assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    copy_asset(summary_path, assets_dir, "renderer_target_gap_summary.json", "Gap summary", root)
    if args.report:
        write_text(args.report, markdown_report(summary))
    print(
        f"status={summary['status']} frames={len(frames)} "
        f"mean_gap_mad={summary['checks']['mean_gap_mean_abs_diff']:.6f} "
        f"max_gap_mad={summary['checks']['max_gap_mean_abs_diff']:.6f} "
        f"out={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a target-gap summary from an actual render and reference sequence")
    parser.add_argument("actual_summary")
    parser.add_argument("reference_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Reference Target Gap")
    parser.add_argument("--next", default="Use this gap summary for signed-error analysis and renderer-native correction.")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
