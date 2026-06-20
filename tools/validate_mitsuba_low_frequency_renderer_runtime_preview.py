#!/usr/bin/env python
"""Validate a low-frequency renderer runtime preview summary."""

import argparse
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def add_check(checks, name, ok, detail="", expected=None, actual=None):
    item = {
        "name": name,
        "status": "ok" if ok else "failed",
        "detail": detail,
    }
    if expected is not None:
        item["expected"] = expected
    if actual is not None:
        item["actual"] = actual
    checks.append(item)
    return ok


def file_check(checks, name, path_value, root, expected_sha=None):
    path = resolve_path(path_value, root)
    if not path:
        return add_check(checks, name, False, "missing path")
    if not os.path.isfile(path):
        return add_check(checks, name, False, f"missing file: {path}")
    if expected_sha:
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            return add_check(checks, name, False, "sha256 mismatch", expected_sha, actual_sha)
    return add_check(checks, name, True, posix_rel(path, root))


def validate_source(checks, summary, root):
    source = summary.get("source") or {}
    path = source.get("runtime_import_preview")
    if not file_check(checks, "source:runtime_import_preview", path, root, source.get("runtime_import_preview_sha256")):
        return {}
    preview_path = resolve_path(path, root)
    preview = read_json(preview_path)
    add_check(
        checks,
        "source:schema",
        preview.get("schema") == "lsfs_mitsuba_low_frequency_runtime_import_preview",
        "source schema",
        "lsfs_mitsuba_low_frequency_runtime_import_preview",
        preview.get("schema"),
    )
    add_check(checks, "source:status", preview.get("status") == "ready", "source status", "ready", preview.get("status"))
    return preview


def validate_checks_block(checks, summary, args):
    block = summary.get("checks") or {}
    add_check(checks, "summary:status", summary.get("status") == "ready", "status", "ready", summary.get("status"))
    add_check(checks, "checks:frame_count", block.get("frames") == block.get("source_frames"), "all source frames generated", block.get("source_frames"), block.get("frames"))
    add_check(checks, "checks:missing", block.get("missing_references") == 0, "missing references", 0, block.get("missing_references"))
    add_check(checks, "checks:dimensions", block.get("dimension_mismatches") == 0, "dimension mismatches", 0, block.get("dimension_mismatches"))
    add_check(checks, "checks:oracle_abs", int(block.get("max_oracle_abs_diff", 999)) <= args.max_abs_diff, "oracle max abs diff", args.max_abs_diff, block.get("max_oracle_abs_diff"))
    add_check(checks, "checks:webgl_abs", int(block.get("max_webgl_abs_diff", 999)) <= args.max_abs_diff, "WebGL max abs diff", args.max_abs_diff, block.get("max_webgl_abs_diff"))
    add_check(checks, "checks:oracle_mean", float(block.get("max_oracle_mean_abs_diff", 999.0)) <= args.max_mean_diff, "oracle mean abs diff", args.max_mean_diff, block.get("max_oracle_mean_abs_diff"))
    add_check(checks, "checks:webgl_mean", float(block.get("max_webgl_mean_abs_diff", 999.0)) <= args.max_mean_diff, "WebGL mean abs diff", args.max_mean_diff, block.get("max_webgl_mean_abs_diff"))
    add_check(checks, "checks:runtime_gif", int(block.get("runtime_gif_bytes", 0)) > 0, "runtime GIF nonempty")
    add_check(checks, "checks:strip_gif", int(block.get("strip_gif_bytes", 0)) > 0, "strip GIF nonempty")


def validate_frames(checks, summary, preview, root, args):
    frames = summary.get("frames") or []
    preview_frames = preview.get("frames") or []
    add_check(checks, "frames:count", len(frames) == len(preview_frames), "preview frame count", len(preview_frames), len(frames))
    for index, frame in enumerate(frames):
        frame_id = frame.get("frame")
        file_check(checks, f"frame:{frame_id}:renderer", frame.get("renderer_repo_path"), root, frame.get("renderer_sha256"))
        file_check(checks, f"frame:{frame_id}:strip", frame.get("strip_repo_path"), root)
        file_check(checks, f"frame:{frame_id}:oracle_diff", frame.get("oracle_diff_repo_path"), root)
        file_check(checks, f"frame:{frame_id}:webgl_diff", frame.get("webgl_diff_repo_path"), root)
        add_check(checks, f"frame:{frame_id}:oracle_abs", int((frame.get("oracle") or {}).get("max_abs_diff", 999)) <= args.max_abs_diff, "oracle max abs diff", args.max_abs_diff, (frame.get("oracle") or {}).get("max_abs_diff"))
        add_check(checks, f"frame:{frame_id}:webgl_abs", int((frame.get("webgl") or {}).get("max_abs_diff", 999)) <= args.max_abs_diff, "WebGL max abs diff", args.max_abs_diff, (frame.get("webgl") or {}).get("max_abs_diff"))
        add_check(checks, f"frame:{frame_id}:oracle_mean", float((frame.get("oracle") or {}).get("mean_abs_diff", 999.0)) <= args.max_mean_diff, "oracle mean abs diff", args.max_mean_diff, (frame.get("oracle") or {}).get("mean_abs_diff"))
        add_check(checks, f"frame:{frame_id}:webgl_mean", float((frame.get("webgl") or {}).get("mean_abs_diff", 999.0)) <= args.max_mean_diff, "WebGL mean abs diff", args.max_mean_diff, (frame.get("webgl") or {}).get("mean_abs_diff"))
        if index < len(preview_frames):
            add_check(
                checks,
                f"frame:{frame_id}:output_match",
                frame.get("output_frame") == preview_frames[index].get("output_frame"),
                "output frame matches import preview",
                preview_frames[index].get("output_frame"),
                frame.get("output_frame"),
            )


def validate_gallery(checks, summary, root):
    gallery = summary.get("gallery") or {}
    file_check(checks, "gallery:index", gallery.get("index_repo_path") or gallery.get("index_path"), root)
    labels = set()
    for asset in gallery.get("assets") or []:
        labels.add(asset.get("label"))
        file_check(checks, f"gallery:asset:{asset.get('label')}", asset.get("repo_path") or asset.get("asset"), root, asset.get("sha256"))
    add_check(checks, "gallery:runtime_gif", "Renderer Runtime GIF" in labels, "runtime GIF present")
    add_check(checks, "gallery:strip_gif", "Runtime Strip GIF" in labels, "strip GIF present")
    for item in gallery.get("metadata_files") or []:
        file_check(checks, f"gallery:metadata:{item.get('label')}", item.get("repo_path") or item.get("asset"), root, item.get("sha256"))


def markdown_report(validation, out_path, root):
    failed = [item for item in validation.get("checks") or [] if item.get("status") == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Summary: `{validation['summary_source']['repo_path']}`",
        "",
        "## Summary",
        "",
        f"- Total checks: `{validation['summary']['total']}`",
        f"- Failed checks: `{validation['summary']['failed']}`",
        "",
        "## Failed Checks",
        "",
    ]
    if failed:
        for item in failed:
            lines.append(f"- `{item.get('name')}`: {item.get('detail')}")
    else:
        lines.append("- None")
    lines.extend(["", "## Checks", "", "| Check | Status | Detail |", "| --- | --- | --- |"])
    for item in validation.get("checks") or []:
        detail = str(item.get("detail", "")).replace("|", "\\|")
        lines.append(f"| `{item.get('name')}` | `{item.get('status')}` | {detail} |")
    lines.append("")
    return "\n".join(lines)


def validate(args):
    root = os.getcwd()
    summary_path = require_file(resolve_path(args.summary_path, root), "renderer runtime preview summary")
    summary = read_json(summary_path)
    checks = []
    add_check(
        checks,
        "summary:schema",
        summary.get("schema") == "lsfs_mitsuba_low_frequency_renderer_runtime_preview",
        "schema",
        "lsfs_mitsuba_low_frequency_renderer_runtime_preview",
        summary.get("schema"),
    )
    add_check(checks, "summary:version", summary.get("version") == 1, "version", 1, summary.get("version"))
    preview = validate_source(checks, summary, root)
    validate_checks_block(checks, summary, args)
    validate_frames(checks, summary, preview, root, args)
    validate_gallery(checks, summary, root)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_runtime_preview_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "summary_source": {
            "path": summary_path,
            "repo_path": posix_rel(summary_path, root),
            "schema": summary.get("schema"),
            "status": summary.get("status"),
            "sha256": sha256_file(summary_path),
            "size": os.path.getsize(summary_path),
        },
        "thresholds": {
            "max_abs_diff": args.max_abs_diff,
            "max_mean_diff": args.max_mean_diff,
        },
        "summary": {
            "total": len(checks),
            "failed": failed,
        },
        "checks": checks,
    }
    out_path = resolve_path(args.out, root)
    write_json(out_path, validation)
    if args.report:
        write_text(args.report, markdown_report(validation, out_path, root))
    print(f"status={validation['status']} total={len(checks)} failed={failed} out={out_path}")
    if failed:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a low-frequency renderer runtime preview")
    parser.add_argument("summary_path")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S497 Mitsuba Low Frequency Renderer Runtime Preview Validation")
    parser.add_argument("--max-abs-diff", type=int, default=0)
    parser.add_argument("--max-mean-diff", type=float, default=0.0)
    args = parser.parse_args(argv)
    if args.max_abs_diff < 0:
        parser.error("max-abs-diff must be non-negative")
    if args.max_mean_diff < 0.0:
        parser.error("max-mean-diff must be non-negative")
    validate(args)


if __name__ == "__main__":
    main()
