#!/usr/bin/env python
"""Validate a low-frequency backend process-stub summary."""

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


def file_check(checks, name, item_or_path, root, expected_sha=None, require_hash=True):
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
    elif require_hash and isinstance(item_or_path, dict) and "sha256" in item_or_path:
        return add_check(checks, name, False, "missing sha256")
    return add_check(checks, name, True, posix_rel(path, root))


def validate_source(checks, summary, root):
    source = summary.get("source_adapter") or {}
    if not file_check(checks, "source:adapter", source, root):
        return {}
    adapter = read_json(resolve_path(source.get("repo_path"), root))
    add_check(
        checks,
        "source:schema",
        adapter.get("schema") == "lsfs_mitsuba_low_frequency_backend_adapter_manifest",
        "adapter schema",
        "lsfs_mitsuba_low_frequency_backend_adapter_manifest",
        adapter.get("schema"),
    )
    add_check(checks, "source:status", adapter.get("status") == "ready", "adapter status", "ready", adapter.get("status"))
    return adapter


def validate_settings(checks, summary, root):
    settings = summary.get("settings") or {}
    add_check(checks, "settings:stage", settings.get("stage") == "renderer_post_tonemap_low_frequency_runtime_consumer", "stage")
    file_check(checks, "settings:backend_script", settings.get("backend_script"), root)
    add_check(checks, "settings:frame_timeout", float(settings.get("frame_timeout") or 0.0) > 0.0, "frame timeout")


def validate_checks_block(checks, summary):
    block = summary.get("checks") or {}
    add_check(checks, "summary:status", summary.get("status") == "passed", "status", "passed", summary.get("status"))
    add_check(checks, "checks:frame_count", block.get("passed_frames") == block.get("frames"), "all frames passed", block.get("frames"), block.get("passed_frames"))
    add_check(checks, "checks:failed", block.get("failed_frames") == 0, "failed frames", 0, block.get("failed_frames"))
    add_check(checks, "checks:process_failures", block.get("process_failures") == 0, "process failures", 0, block.get("process_failures"))
    add_check(checks, "checks:max_abs", block.get("max_abs_diff") == 0, "max abs diff", 0, block.get("max_abs_diff"))
    add_check(checks, "checks:max_mean", block.get("max_mean_abs_diff") == 0.0, "max mean diff", 0.0, block.get("max_mean_abs_diff"))
    add_check(checks, "checks:output_bytes", int(block.get("output_bytes") or 0) > 0, "output bytes nonzero")
    add_check(checks, "checks:gif_bytes", int(block.get("gif_bytes") or 0) > 0, "GIF bytes nonzero")
    add_check(checks, "checks:strip_gif_bytes", int(block.get("strip_gif_bytes") or 0) > 0, "strip GIF bytes nonzero")
    add_check(checks, "checks:stdout_bytes", int(block.get("stdout_bytes") or 0) > 0, "stdout bytes nonzero")
    add_check(checks, "checks:stderr_bytes", int(block.get("stderr_bytes") or 0) == 0, "stderr bytes empty")
    add_check(checks, "checks:result_json_bytes", int(block.get("result_json_bytes") or 0) > 0, "result JSON bytes nonzero")


def validate_scene(checks, frame, adapter_frame, root):
    frame_id = frame.get("frame")
    scene_path = frame.get("scene_repo_path")
    scene = {}
    if file_check(checks, f"frame:{frame_id}:scene", scene_path, root):
        scene = read_json(resolve_path(scene_path, root))
    add_check(
        checks,
        f"frame:{frame_id}:scene_schema",
        scene.get("schema") == "lsfs_mitsuba_low_frequency_backend_scene_descriptor",
        "scene schema",
    )
    expected_scene = ((adapter_frame or {}).get("scene_descriptor") or {}).get("repo_path")
    add_check(checks, f"frame:{frame_id}:scene_match", scene_path == expected_scene, "scene path matches adapter", expected_scene, scene_path)
    outputs = scene.get("outputs") or {}
    for name in ("image", "metadata", "validation"):
        add_check(checks, f"frame:{frame_id}:scene_output:{name}", bool((outputs.get(name) or {}).get("repo_path")), "scene output path")


def validate_result_json(checks, frame, root):
    frame_id = frame.get("frame")
    result_item = frame.get("result_json") or {}
    if not file_check(checks, f"frame:{frame_id}:result_json", result_item, root):
        return {}
    result = read_json(resolve_path(result_item.get("repo_path"), root))
    add_check(
        checks,
        f"frame:{frame_id}:result_schema",
        result.get("schema") == "lsfs_mitsuba_low_frequency_backend_stub_result",
        "result schema",
    )
    add_check(checks, f"frame:{frame_id}:result_status", result.get("status") == "passed", "result status")
    add_check(checks, f"frame:{frame_id}:result_max_abs", result.get("max_abs_diff") == 0, "result max abs")
    add_check(checks, f"frame:{frame_id}:result_mean_abs", result.get("mean_abs_diff") == 0.0, "result mean abs")
    return result


def validate_frame_sidecars(checks, frame, root):
    frame_id = frame.get("frame")
    metadata_path = resolve_path(frame.get("metadata_repo_path"), root)
    validation_path = resolve_path(frame.get("validation_repo_path"), root)
    metadata = read_json(metadata_path) if metadata_path and os.path.isfile(metadata_path) else {}
    validation = read_json(validation_path) if validation_path and os.path.isfile(validation_path) else {}
    add_check(
        checks,
        f"frame:{frame_id}:metadata_schema",
        metadata.get("schema") == "lsfs_mitsuba_low_frequency_backend_scene_metadata",
        "metadata schema",
    )
    add_check(
        checks,
        f"frame:{frame_id}:validation_schema",
        validation.get("schema") == "lsfs_mitsuba_low_frequency_backend_scene_validation",
        "validation schema",
    )
    add_check(checks, f"frame:{frame_id}:validation_status", validation.get("status") == "passed", "validation status")
    add_check(checks, f"frame:{frame_id}:validation_max_abs", ((validation.get("diff") or {}).get("max_abs_diff") == 0), "validation max abs")
    add_check(checks, f"frame:{frame_id}:validation_mean_abs", ((validation.get("diff") or {}).get("mean_abs_diff") == 0.0), "validation mean abs")


def validate_frames(checks, summary, adapter, root):
    frames = summary.get("frames") or []
    adapter_frames = adapter.get("frames") or []
    add_check(checks, "frames:count", len(frames) == len(adapter_frames), "adapter frame count", len(adapter_frames), len(frames))
    adapter_by_index = {item.get("job_index"): item for item in adapter_frames}
    for frame in frames:
        index = frame.get("job_index")
        frame_id = frame.get("frame")
        adapter_frame = adapter_by_index.get(index) or {}
        process = frame.get("process") or {}
        add_check(checks, f"frame:{frame_id}:status", frame.get("status") == "passed", "frame status")
        add_check(checks, f"frame:{frame_id}:returncode", process.get("returncode") == 0, "process return code", 0, process.get("returncode"))
        add_check(checks, f"frame:{frame_id}:elapsed", float(process.get("elapsed_ms") or 0.0) > 0.0, "process elapsed")
        file_check(checks, f"frame:{frame_id}:stdout", process.get("stdout") or {}, root)
        file_check(checks, f"frame:{frame_id}:stderr", process.get("stderr") or {}, root, require_hash=False)
        result = validate_result_json(checks, frame, root)
        file_check(checks, f"frame:{frame_id}:output", frame.get("output_image_repo_path"), root, frame.get("output_sha256"))
        file_check(checks, f"frame:{frame_id}:metadata", frame.get("metadata_repo_path"), root)
        file_check(checks, f"frame:{frame_id}:validation", frame.get("validation_repo_path"), root)
        file_check(checks, f"frame:{frame_id}:strip", frame.get("strip_repo_path"), root)
        add_check(checks, f"frame:{frame_id}:max_abs", frame.get("max_abs_diff") == 0, "max abs diff", 0, frame.get("max_abs_diff"))
        add_check(checks, f"frame:{frame_id}:mean_abs", frame.get("mean_abs_diff") == 0.0, "mean abs diff", 0.0, frame.get("mean_abs_diff"))
        add_check(checks, f"frame:{frame_id}:reference_hash", frame.get("reference_sha256") == frame.get("expected_reference_sha256"), "reference hash")
        add_check(checks, f"frame:{frame_id}:result_output_match", result.get("output_image_repo_path") == frame.get("output_image_repo_path"), "result output matches frame")
        output_target = (((adapter_frame.get("outputs") or {}).get("image") or {}).get("repo_path"))
        add_check(checks, f"frame:{frame_id}:target_match", frame.get("output_image_repo_path") == output_target, "output path matches adapter", output_target, frame.get("output_image_repo_path"))
        validate_scene(checks, frame, adapter_frame, root)
        validate_frame_sidecars(checks, frame, root)


def validate_gallery(checks, summary, root):
    gallery = summary.get("gallery") or {}
    file_check(checks, "gallery:index", gallery.get("index_repo_path") or gallery.get("index_path"), root)
    labels = set()
    for asset in gallery.get("assets") or []:
        labels.add(asset.get("label"))
        file_check(checks, f"gallery:asset:{asset.get('label')}", asset, root)
    add_check(checks, "gallery:process_stub_gif", "Backend Process Stub GIF" in labels, "process stub GIF present")
    add_check(checks, "gallery:process_stub_strip_gif", "Backend Process Stub Strip GIF" in labels, "process stub strip GIF present")
    for item in gallery.get("metadata_files") or []:
        file_check(checks, f"gallery:metadata:{item.get('label')}", item, root, require_hash=False)


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
    summary_path = require_file(resolve_path(args.summary_path, root), "backend process stub summary")
    summary = read_json(summary_path)
    checks = []
    add_check(
        checks,
        "summary:schema",
        summary.get("schema") == "lsfs_mitsuba_low_frequency_backend_process_stub",
        "schema",
        "lsfs_mitsuba_low_frequency_backend_process_stub",
        summary.get("schema"),
    )
    add_check(checks, "summary:version", summary.get("version") == 1, "version", 1, summary.get("version"))
    adapter = validate_source(checks, summary, root)
    validate_settings(checks, summary, root)
    validate_checks_block(checks, summary)
    validate_frames(checks, summary, adapter, root)
    validate_gallery(checks, summary, root)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_backend_process_stub_validation",
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
    parser = argparse.ArgumentParser(description="Validate a low-frequency backend process stub")
    parser.add_argument("summary_path")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S505 Mitsuba Low Frequency Backend Process Stub Validation")
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
