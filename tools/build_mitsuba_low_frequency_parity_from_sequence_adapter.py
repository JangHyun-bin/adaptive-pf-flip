#!/usr/bin/env python
"""Bridge a low-frequency runtime sequence adapter into parity-summary schema."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageStat = None

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


SOURCE_SCHEMA = "lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter"
OUTPUT_SCHEMA = "lsfs_mitsuba_secondary_composite"
OUTPUT_SUBSCHEMA = "lsfs_mitsuba_low_frequency_parity"


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to bridge sequence adapters")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def frame_path(frame, *keys):
    for key in keys:
        value = frame.get(key)
        if value:
            return value
    bindings = frame.get("runtime_bindings") or {}
    for key in keys:
        value = bindings.get(key)
        if value:
            return value
    return None


def diff_stats(a, b):
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    stat = ImageStat.Stat(diff)
    hist = diff.convert("L").histogram()
    pixels = max(1, diff.size[0] * diff.size[1])
    return {
        "mean_abs_diff": sum(stat.mean) / 3.0,
        "max_abs_diff": max(channel[1] for channel in stat.extrema),
        "mismatched_coverage": (pixels - hist[0]) / float(pixels),
    }


def source_entry(path, root, label, payload=None):
    entry = {
        "label": label,
        "path": os.path.abspath(path),
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
        entry["status"] = payload.get("status")
    return entry


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Sequence adapter: `{summary['sources']['sequence_adapter']['repo_path']}`",
        f"- Source schema: `{summary['sources']['sequence_adapter'].get('schema')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Dimension mismatches: `{checks.get('dimension_mismatches')}`",
        f"- Max target abs diff: `{checks.get('max_target_abs_diff')}`",
        f"- Max target mean diff: `{checks.get('max_target_mean_abs_diff')}`",
        f"- Max target mismatched coverage: `{checks.get('max_target_mismatched_coverage')}`",
        f"- Source bytes: `{format_bytes(checks.get('source_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Mean Diff | Max Diff | Raw | Corrected |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('target_mean_abs_diff')} | {frame.get('target_max_abs_diff')} | "
            f"`{frame.get('native_repo_path')}` | `{frame.get('composite_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    sequence_path = require_file(args.sequence_summary, "sequence adapter summary")
    sequence = read_json(sequence_path)
    if sequence.get("schema") != SOURCE_SCHEMA:
        raise SystemExit(f"{args.sequence_summary}: expected {SOURCE_SCHEMA} schema")
    if sequence.get("status") != "ready":
        raise SystemExit(f"{args.sequence_summary}: sequence status is {sequence.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    frames = []
    missing = []
    dimension_mismatches = []
    source_bytes = 0
    for index, frame in enumerate(sequence.get("frames") or []):
        raw_ref = frame_path(frame, "raw_repo_path", "base_rgb")
        corrected_ref = frame_path(frame, "corrected_repo_path")
        raw_path = resolve_path(raw_ref)
        corrected_path = resolve_path(corrected_ref)
        absent = []
        if not raw_path or not os.path.isfile(raw_path):
            absent.append({"role": "raw", "path": raw_path})
        if not corrected_path or not os.path.isfile(corrected_path):
            absent.append({"role": "corrected", "path": corrected_path})
        if absent:
            missing.append({"frame": index, "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        raw = Image.open(raw_path).convert("RGB")
        corrected = Image.open(corrected_path).convert("RGB")
        if raw.size != corrected.size:
            dimension_mismatches.append({
                "frame": index,
                "output_frame": frame.get("output_frame"),
                "raw_dimensions": list(raw.size),
                "corrected_dimensions": list(corrected.size),
            })
            continue
        stats = diff_stats(raw, corrected)
        source_bytes += os.path.getsize(raw_path) + os.path.getsize(corrected_path)
        frames.append({
            "frame": index,
            "output_frame": frame.get("output_frame", index),
            "sequence_frame": frame.get("render_sequence_frame"),
            "native_repo_path": posix_rel(raw_path, root),
            "target_repo_path": posix_rel(corrected_path, root),
            "proxy_repo_path": posix_rel(corrected_path, root),
            "composite_repo_path": posix_rel(corrected_path, root),
            "native_sha256": sha256_file(raw_path),
            "target_sha256": sha256_file(corrected_path),
            "composite_sha256": sha256_file(corrected_path),
            "dimensions": image_dimensions(corrected_path),
            "target_mean_abs_diff": stats["mean_abs_diff"],
            "target_max_abs_diff": stats["max_abs_diff"],
            "target_mismatched_coverage": stats["mismatched_coverage"],
            "mask": frame.get("mask"),
            "source_corrected_change": frame.get("corrected_change"),
        })

    if not frames:
        raise SystemExit("no parity frames generated")
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "dimension_mismatches": len(dimension_mismatches),
        "max_target_abs_diff": max((frame.get("target_max_abs_diff") or 0 for frame in frames), default=0),
        "max_target_mean_abs_diff": max((frame.get("target_mean_abs_diff") or 0.0 for frame in frames), default=0.0),
        "max_target_mismatched_coverage": max((frame.get("target_mismatched_coverage") or 0.0 for frame in frames), default=0.0),
        "source_bytes": source_bytes,
    }
    status = "ready" if not missing and not dimension_mismatches else "review"
    summary_path = os.path.abspath(args.summary)
    summary = {
        "schema": OUTPUT_SCHEMA,
        "subschema": OUTPUT_SUBSCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "sources": {
            "sequence_adapter": source_entry(sequence_path, root, "low-frequency sequence adapter", sequence),
        },
        "settings": {
            "max_delta": args.max_delta,
            "blur_radius": args.blur_radius,
            "target_dark_luma": args.target_dark_luma,
            "dark_damping": args.dark_damping,
            "source_schema": SOURCE_SCHEMA,
        },
        "checks": checks,
        "frames": frames,
        "missing_references": missing,
        "dimension_mismatches": dimension_mismatches,
        "next": args.next,
    }
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={len(frames)} max_diff={checks['max_target_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bridge a low-frequency sequence adapter into parity summary schema")
    parser.add_argument("sequence_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--max-delta", type=float, default=48.0)
    parser.add_argument("--blur-radius", type=float, default=6.0)
    parser.add_argument("--target-dark-luma", type=float, default=55.0)
    parser.add_argument("--dark-damping", type=float, default=0.35)
    parser.add_argument("--title", default="Mitsuba Low Frequency Parity From Sequence Adapter")
    parser.add_argument("--next", default="Build a renderer texture/cache package from this full sequence parity summary.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.max_delta <= 0.0 or args.max_delta > 127.0:
        parser.error("max-delta must be in (0, 127]")
    if args.blur_radius < 0.0:
        parser.error("blur-radius must be non-negative")
    if not (0.0 <= args.target_dark_luma <= 255.0):
        parser.error("target-dark-luma must be in [0, 255]")
    if not (0.0 <= args.dark_damping <= 1.0):
        parser.error("dark-damping must be in [0, 1]")
    build(args)


if __name__ == "__main__":
    main()
