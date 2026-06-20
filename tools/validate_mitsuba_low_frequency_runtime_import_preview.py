#!/usr/bin/env python
"""Validate a low-frequency runtime import preview."""

import argparse
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
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


def is_inside(path, parent):
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(parent)]) == os.path.abspath(parent)
    except ValueError:
        return False


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


def count_source_keys(value):
    if isinstance(value, dict):
        total = sum(1 for key in value if "source" in str(key).lower())
        return total + sum(count_source_keys(item) for item in value.values())
    if isinstance(value, list):
        return sum(count_source_keys(item) for item in value)
    return 0


def file_check(checks, name, item, root, bundle_root=None):
    path = resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)
    if not path:
        return add_check(checks, name, False, "missing path")
    if not os.path.isfile(path):
        return add_check(checks, name, False, f"missing file: {path}")
    expected_size = item.get("size")
    if expected_size is not None:
        actual_size = os.path.getsize(path)
        if actual_size != expected_size:
            return add_check(checks, name, False, "size mismatch", expected_size, actual_size)
    expected_sha = item.get("sha256")
    if expected_sha:
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            return add_check(checks, name, False, "sha256 mismatch", expected_sha, actual_sha)
    if bundle_root:
        add_check(checks, f"{name}:inside_bundle", is_inside(path, bundle_root), "bundle-local asset")
    return add_check(checks, name, True, posix_rel(path, root))


def validate_asset_set(checks, prefix, mapping, root, bundle_root):
    for key, item in (mapping or {}).items():
        file_check(checks, f"{prefix}:{key}", item, root, bundle_root)


def validate_runtime_assets(checks, preview, root, bundle_root):
    assets = preview.get("runtime_assets") or {}
    file_check(checks, "runtime:runtime_webgl", assets.get("runtime_webgl"), root, bundle_root)
    file_check(checks, "runtime:webgl_proof_gif", assets.get("webgl_proof_gif"), root, bundle_root)
    shaders = assets.get("shaders") or {}
    entrypoints = (preview.get("runtime_contract") or {}).get("shader_entrypoints") or {}
    add_check(checks, "runtime:shader_count", len(shaders) == len(entrypoints), "shader entrypoints resolved", len(entrypoints), len(shaders))
    for api, item in shaders.items():
        file_check(checks, f"runtime:shader:{api}", item, root, bundle_root)


def validate_frames(checks, preview, source_bundle, root, bundle_root):
    contract = preview.get("runtime_contract") or {}
    required = contract.get("required_bindings") or []
    source_frames = source_bundle.get("frames") or []
    frames = preview.get("frames") or []
    add_check(checks, "frames:count", len(frames) == len(source_frames), "frame count", len(source_frames), len(frames))
    for index, frame in enumerate(frames):
        frame_id = frame.get("frame")
        bindings = frame.get("runtime_bindings") or {}
        for binding in required:
            add_check(checks, f"frame:{frame_id}:binding_present:{binding}", binding in bindings, "required binding present")
            if binding in bindings:
                file_check(checks, f"frame:{frame_id}:binding:{binding}", bindings.get(binding), root, bundle_root)
        validate_asset_set(checks, f"frame:{frame_id}:optional", frame.get("optional_bindings") or {}, root, bundle_root)
        file_check(checks, f"frame:{frame_id}:oracle", frame.get("oracle"), root, bundle_root)
        proof = frame.get("proof") or {}
        file_check(checks, f"frame:{frame_id}:proof:webgl", proof.get("webgl_frame"), root, bundle_root)
        file_check(checks, f"frame:{frame_id}:proof:strip", proof.get("proof_strip"), root, bundle_root)
        add_check(checks, f"frame:{frame_id}:proof_abs_diff", proof.get("max_abs_diff") == 0, "proof max diff", 0, proof.get("max_abs_diff"))
        add_check(checks, f"frame:{frame_id}:proof_mean_diff", proof.get("mean_abs_diff") == 0.0, "proof mean diff", 0.0, proof.get("mean_abs_diff"))
        add_check(checks, f"frame:{frame_id}:ready", bool(frame.get("ready")), "frame ready")
        ui_inputs = frame.get("ui_runtime_inputs") or []
        ui_semantics = {item.get("semantic") for item in ui_inputs}
        for binding in required:
            add_check(checks, f"frame:{frame_id}:ui_input:{binding}", binding in ui_semantics, "UI input semantic present")
        add_check(checks, f"frame:{frame_id}:ui_no_source_keys", count_source_keys(ui_inputs) == 0, "no source-path keys in UI inputs")
        if index < len(source_frames):
            add_check(
                checks,
                f"frame:{frame_id}:source_frame_match",
                frame.get("output_frame") == source_frames[index].get("output_frame"),
                "output frame matches bundle",
                source_frames[index].get("output_frame"),
                frame.get("output_frame"),
            )


def validate_checks_block(checks, preview):
    block = preview.get("checks") or {}
    add_check(checks, "preview:status", preview.get("status") == "ready", "status", "ready", preview.get("status"))
    for key in (
        "missing_required_bindings",
        "hash_mismatches",
        "size_mismatches",
        "dimension_mismatches",
        "inside_bundle_violations",
        "source_dependency_leaks",
        "proof_failures",
    ):
        add_check(checks, f"checks:{key}", block.get(key) == 0, key, 0, block.get(key))
    add_check(checks, "checks:ready_frames", block.get("ready_frames") == block.get("frames"), "all frames ready", block.get("frames"), block.get("ready_frames"))
    add_check(checks, "checks:runtime_html_resolved", block.get("runtime_html_resolved") is True, "runtime HTML resolved")
    add_check(checks, "checks:shader_refs_resolved", block.get("shader_refs_resolved") is True, "shader refs resolved")


def markdown_report(validation, out_path, root):
    failed = [item for item in validation.get("checks") or [] if item.get("status") == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Preview: `{validation['preview']['repo_path']}`",
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
    preview_path = resolve_path(args.preview, root)
    if not preview_path or not os.path.isfile(preview_path):
        raise SystemExit(f"Missing preview: {args.preview}")
    preview = read_json(preview_path)
    checks = []
    add_check(
        checks,
        "preview:schema",
        preview.get("schema") == "lsfs_mitsuba_low_frequency_runtime_import_preview",
        "schema",
        "lsfs_mitsuba_low_frequency_runtime_import_preview",
        preview.get("schema"),
    )
    add_check(checks, "preview:version", preview.get("version") == 1, "version", 1, preview.get("version"))
    source = preview.get("source_bundle") or {}
    file_check(checks, "source_bundle:file", source, root)
    source_path = resolve_path(source.get("repo_path") or source.get("path"), root)
    source_bundle = read_json(source_path) if source_path and os.path.isfile(source_path) else {}
    add_check(
        checks,
        "source_bundle:schema",
        source_bundle.get("schema") == "lsfs_mitsuba_low_frequency_runtime_handoff_bundle",
        "source bundle schema",
        "lsfs_mitsuba_low_frequency_runtime_handoff_bundle",
        source_bundle.get("schema"),
    )
    add_check(checks, "source_bundle:status", source_bundle.get("status") == "ready", "source bundle status", "ready", source_bundle.get("status"))
    bundle_root = resolve_path((source_bundle.get("bundle_root") or {}).get("repo_path") or os.path.dirname(source_path or ""), root)
    validate_checks_block(checks, preview)
    validate_runtime_assets(checks, preview, root, bundle_root)
    validate_frames(checks, preview, source_bundle, root, bundle_root)
    output = preview.get("output") or {}
    index_html = (output.get("index_html") or {})
    if file_check(checks, "output:index_html", index_html, root):
        index_path = resolve_path(index_html.get("repo_path") or index_html.get("path"), root)
        with open(index_path, encoding="utf-8") as f:
            html_text = f.read()
        add_check(checks, "output:index_mentions_bundle", "runtime_handoff_bundle.json" in html_text, "bundle link in HTML")
        add_check(checks, "output:index_mentions_frames", "Frame " in html_text, "frame sections in HTML")
    add_check(checks, "preview:no_source_keys_in_frames", count_source_keys(preview.get("frames") or []) == 0, "no source-path keys in frame import data")
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_import_preview_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "preview": {
            "path": preview_path,
            "repo_path": posix_rel(preview_path, root),
            "schema": preview.get("schema"),
            "status": preview.get("status"),
            "sha256": sha256_file(preview_path),
            "size": os.path.getsize(preview_path),
        },
        "source_bundle": {
            "path": source_path,
            "repo_path": posix_rel(source_path, root) if source_path else None,
            "schema": source_bundle.get("schema"),
            "status": source_bundle.get("status"),
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
    parser = argparse.ArgumentParser(description="Validate a runtime-bundle import preview")
    parser.add_argument("preview")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S495 Mitsuba Low Frequency Runtime Import Preview Validation")
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
