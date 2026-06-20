#!/usr/bin/env python
"""Validate a low-frequency renderer job dry-run summary."""

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


def file_check(checks, name, item_or_path, root, expected_sha=None):
    if isinstance(item_or_path, dict):
        path_value = item_or_path.get("repo_path") or item_or_path.get("path") or item_or_path.get("asset")
        expected_size = item_or_path.get("size")
        expected = expected_sha or item_or_path.get("sha256")
    else:
        path_value = item_or_path
        expected_size = None
        expected = expected_sha
    path = resolve_path(path_value, root)
    if not path:
        return add_check(checks, name, False, "missing path")
    if not os.path.isfile(path):
        return add_check(checks, name, False, f"missing file: {path}")
    if expected_size is not None:
        actual_size = os.path.getsize(path)
        if actual_size != expected_size:
            return add_check(checks, name, False, "size mismatch", expected_size, actual_size)
    if expected:
        actual_sha = sha256_file(path)
        if actual_sha != expected:
            return add_check(checks, name, False, "sha256 mismatch", expected, actual_sha)
    return add_check(checks, name, True, posix_rel(path, root))


def validate_source(checks, summary, root):
    source = summary.get("source_job") or {}
    if not file_check(checks, "source:job", source, root):
        return {}
    job = read_json(resolve_path(source.get("repo_path"), root))
    add_check(
        checks,
        "source:schema",
        job.get("schema") == "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        "job schema",
        "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        job.get("schema"),
    )
    add_check(checks, "source:status", job.get("status") == "ready", "job status", "ready", job.get("status"))
    return job


def validate_checks_block(checks, summary):
    block = summary.get("checks") or {}
    add_check(checks, "summary:status", summary.get("status") == "passed", "status", "passed", summary.get("status"))
    add_check(checks, "checks:frame_count", block.get("passed_frames") == block.get("frames"), "all frames passed", block.get("frames"), block.get("passed_frames"))
    add_check(checks, "checks:failed", block.get("failed_frames") == 0, "failed frames", 0, block.get("failed_frames"))
    add_check(checks, "checks:missing", block.get("missing_frames") == 0, "missing frames", 0, block.get("missing_frames"))
    add_check(checks, "checks:max_abs", block.get("max_abs_diff") == 0, "max abs diff", 0, block.get("max_abs_diff"))
    add_check(checks, "checks:max_mean", block.get("max_mean_abs_diff") == 0.0, "max mean diff", 0.0, block.get("max_mean_abs_diff"))
    add_check(checks, "checks:output_bytes", int(block.get("output_bytes") or 0) > 0, "output bytes nonzero")
    add_check(checks, "checks:gif_bytes", int(block.get("gif_bytes") or 0) > 0, "GIF bytes nonzero")


def validate_frames(checks, summary, job, root):
    frames = summary.get("frames") or []
    jobs = job.get("frame_jobs") or []
    add_check(checks, "frames:count", len(frames) == len(jobs), "job frame count", len(jobs), len(frames))
    job_by_index = {item.get("job_index"): item for item in jobs}
    for frame in frames:
        index = frame.get("job_index")
        frame_id = frame.get("frame")
        add_check(checks, f"frame:{frame_id}:status", frame.get("status") == "passed", "frame status")
        file_check(checks, f"frame:{frame_id}:output", frame.get("output_image_repo_path"), root, frame.get("output_sha256"))
        file_check(checks, f"frame:{frame_id}:metadata", frame.get("metadata_repo_path"), root)
        file_check(checks, f"frame:{frame_id}:validation", frame.get("validation_repo_path"), root)
        file_check(checks, f"frame:{frame_id}:strip", frame.get("strip_repo_path"), root)
        add_check(checks, f"frame:{frame_id}:max_abs", frame.get("max_abs_diff") == 0, "max abs diff", 0, frame.get("max_abs_diff"))
        add_check(checks, f"frame:{frame_id}:mean_abs", frame.get("mean_abs_diff") == 0.0, "mean abs diff", 0.0, frame.get("mean_abs_diff"))
        add_check(checks, f"frame:{frame_id}:reference_hash", frame.get("reference_sha256") == frame.get("expected_reference_sha256"), "reference hash")
        job_frame = job_by_index.get(index) or {}
        output_target = (((job_frame.get("outputs") or {}).get("image") or {}).get("repo_path"))
        add_check(checks, f"frame:{frame_id}:target_match", frame.get("output_image_repo_path") == output_target, "output path matches job")


def validate_gallery(checks, summary, root):
    gallery = summary.get("gallery") or {}
    file_check(checks, "gallery:index", gallery.get("index_repo_path") or gallery.get("index_path"), root)
    labels = set()
    for asset in gallery.get("assets") or []:
        labels.add(asset.get("label"))
        file_check(checks, f"gallery:asset:{asset.get('label')}", asset, root)
    add_check(checks, "gallery:dry_run_gif", "Dry Run GIF" in labels, "dry-run GIF present")
    add_check(checks, "gallery:strip_gif", "Dry Run Strip GIF" in labels, "strip GIF present")
    for item in gallery.get("metadata_files") or []:
        file_check(checks, f"gallery:metadata:{item.get('label')}", item, root)


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
    summary_path = require_file(resolve_path(args.summary_path, root), "dry-run summary")
    summary = read_json(summary_path)
    checks = []
    add_check(
        checks,
        "summary:schema",
        summary.get("schema") == "lsfs_mitsuba_low_frequency_renderer_job_dry_run",
        "schema",
        "lsfs_mitsuba_low_frequency_renderer_job_dry_run",
        summary.get("schema"),
    )
    add_check(checks, "summary:version", summary.get("version") == 1, "version", 1, summary.get("version"))
    job = validate_source(checks, summary, root)
    validate_checks_block(checks, summary)
    validate_frames(checks, summary, job, root)
    validate_gallery(checks, summary, root)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_dry_run_validation",
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
    parser = argparse.ArgumentParser(description="Validate a low-frequency renderer job dry run")
    parser.add_argument("summary_path")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S500 Mitsuba Low Frequency Renderer Job Dry Run Validation")
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
