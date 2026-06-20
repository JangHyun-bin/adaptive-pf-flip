#!/usr/bin/env python
"""Validate a real Mitsuba XML backend command adapter summary."""

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
    source = summary.get("source_export") or {}
    if not file_check(checks, "source:export", source, root):
        return {}
    export = read_json(resolve_path(source.get("repo_path"), root))
    add_check(checks, "source:schema", export.get("schema") == "lsfs_mitsuba_xml_export", "export schema")
    add_check(checks, "source:status", export.get("status") == "ready", "export status", "ready", export.get("status"))
    return export


def validate_runtime(checks, summary, root):
    runtime = summary.get("runtime") or {}
    file_check(checks, "runtime:render_script", runtime.get("render_script"), root)
    file_check(checks, "runtime:gallery_script", runtime.get("gallery_script"), root)
    python_path = runtime.get("python")
    add_check(checks, "runtime:python", bool(python_path and os.path.isfile(python_path)), "renderer python exists", actual=python_path)
    if runtime.get("llvm_dll"):
        file_check(checks, "runtime:llvm_dll", runtime.get("llvm_dll"), root)
    add_check(checks, "runtime:spp", int(runtime.get("spp") or 0) > 0, "spp")
    add_check(checks, "runtime:write_png", runtime.get("write_png") is True, "png previews enabled")


def validate_process(checks, summary, root, name):
    proc = ((summary.get("processes") or {}).get(name) or {})
    add_check(checks, f"process:{name}:command", bool(proc.get("command")), "command present")
    add_check(checks, f"process:{name}:returncode", proc.get("returncode") == 0, "return code", 0, proc.get("returncode"))
    add_check(checks, f"process:{name}:timeout", proc.get("timed_out") is False, "not timed out")
    add_check(checks, f"process:{name}:elapsed", float(proc.get("elapsed_ms") or 0.0) > 0.0, "elapsed")
    file_check(checks, f"process:{name}:stdout", proc.get("stdout") or {}, root)
    file_check(checks, f"process:{name}:stderr", proc.get("stderr") or {}, root, require_hash=False)


def validate_render_manifest(checks, summary, root):
    item = summary.get("render_manifest") or {}
    if not file_check(checks, "render:manifest", item, root):
        return {}
    render = read_json(resolve_path(item.get("repo_path"), root))
    add_check(checks, "render:schema", render.get("schema") == "lsfs_mitsuba_xml_render", "render schema")
    add_check(checks, "render:status", render.get("status") == "ready", "render status", "ready", render.get("status"))
    render_checks = render.get("checks") or {}
    add_check(checks, "render:frame_count", render_checks.get("frames_rendered") == render_checks.get("frames_requested"), "all frames rendered")
    add_check(checks, "render:failures", render_checks.get("failures") == 0, "failures", 0, render_checks.get("failures"))
    add_check(checks, "render:image_bytes", int(render_checks.get("image_bytes") or 0) > 0, "image bytes")
    add_check(checks, "render:preview_bytes", int(render_checks.get("preview_bytes") or 0) > 0, "preview bytes")
    for index, frame in enumerate(render.get("frames") or []):
        file_check(checks, f"render:frame:{index}:image", frame.get("image") or {}, root)
        file_check(checks, f"render:frame:{index}:preview", frame.get("preview") or {}, root)
    return render


def validate_gallery_manifest(checks, summary, root):
    item = summary.get("gallery_manifest") or {}
    if not file_check(checks, "gallery:manifest", item, root):
        return {}
    gallery = read_json(resolve_path(item.get("repo_path"), root))
    add_check(checks, "gallery:schema", gallery.get("schema") == "lsfs_mitsuba_render_gallery", "gallery schema")
    file_check(checks, "gallery:index", gallery.get("index_repo_path") or gallery.get("index"), root)
    labels = set()
    for asset in gallery.get("assets") or []:
        labels.add(asset.get("label"))
        file_check(checks, f"gallery:asset:{asset.get('label')}", asset, root)
    add_check(checks, "gallery:shot_gif", "Shot GIF" in labels, "shot gif present")
    for item in gallery.get("metadata_files") or []:
        file_check(checks, f"gallery:metadata:{item.get('label')}", item, root)
    return gallery


def validate_checks_block(checks, summary):
    block = summary.get("checks") or {}
    add_check(checks, "summary:status", summary.get("status") == "ready", "status", "ready", summary.get("status"))
    add_check(checks, "checks:frames", block.get("frames_rendered") == block.get("frames_requested"), "frame count")
    add_check(checks, "checks:render_failures", block.get("render_failures") == 0, "render failures", 0, block.get("render_failures"))
    add_check(checks, "checks:process_failures", block.get("process_failures") == 0, "process failures", 0, block.get("process_failures"))
    add_check(checks, "checks:image_bytes", int(block.get("image_bytes") or 0) > 0, "image bytes")
    add_check(checks, "checks:preview_bytes", int(block.get("preview_bytes") or 0) > 0, "preview bytes")
    add_check(checks, "checks:gif_bytes", int(block.get("gif_bytes") or 0) > 0, "gif bytes")
    add_check(checks, "checks:gallery_assets", int(block.get("gallery_assets") or 0) >= 2, "gallery assets")
    add_check(checks, "checks:stdout_bytes", int(block.get("stdout_bytes") or 0) > 0, "stdout bytes")


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
    summary_path = require_file(resolve_path(args.summary_path, root), "Mitsuba XML backend command adapter summary")
    summary = read_json(summary_path)
    checks = []
    add_check(
        checks,
        "summary:schema",
        summary.get("schema") == "lsfs_mitsuba_xml_backend_command_adapter",
        "schema",
        "lsfs_mitsuba_xml_backend_command_adapter",
        summary.get("schema"),
    )
    add_check(checks, "summary:version", summary.get("version") == 1, "version", 1, summary.get("version"))
    validate_source(checks, summary, root)
    validate_runtime(checks, summary, root)
    validate_process(checks, summary, root, "render")
    validate_process(checks, summary, root, "gallery")
    validate_render_manifest(checks, summary, root)
    validate_gallery_manifest(checks, summary, root)
    validate_checks_block(checks, summary)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_xml_backend_command_adapter_validation",
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
    parser = argparse.ArgumentParser(description="Validate a real Mitsuba XML backend command adapter")
    parser.add_argument("summary_path")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S506 Mitsuba XML Backend Command Adapter Validation")
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
