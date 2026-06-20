#!/usr/bin/env python
"""Validate a low-frequency backend adapter manifest."""

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


def file_check(checks, name, item, root):
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
    expected = item.get("expected_sha256") or item.get("sha256")
    if expected:
        actual_sha = sha256_file(path)
        if actual_sha != expected:
            return add_check(checks, name, False, "sha256 mismatch", expected, actual_sha)
    return add_check(checks, name, True, posix_rel(path, root))


def validate_source(checks, manifest, root):
    source = manifest.get("source_job") or {}
    if not file_check(checks, "source:job", source, root):
        return {}
    job = read_json(resolve_path(source.get("repo_path"), root))
    add_check(
        checks,
        "source:schema",
        job.get("schema") == "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        "source schema",
        "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        job.get("schema"),
    )
    add_check(checks, "source:status", job.get("status") == "ready", "source status", "ready", job.get("status"))
    return job


def validate_policy(checks, manifest):
    policy = manifest.get("dependency_policy") or {}
    add_check(checks, "policy:root_manifest_only", policy.get("root_manifest_only") is True, "root manifest only")
    add_check(
        checks,
        "policy:root_manifest_schema",
        policy.get("root_manifest_schema") == "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        "root schema",
    )


def validate_contract(checks, manifest, root):
    contract = manifest.get("runtime_contract") or {}
    required = contract.get("required_bindings") or []
    add_check(checks, "contract:stage", contract.get("stage") == "renderer_post_tonemap_low_frequency_runtime_consumer", "stage")
    add_check(checks, "contract:expression", "positive_delta_rgb - negative_delta_rgb" in (contract.get("expression") or ""), "expression")
    for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
        add_check(checks, f"contract:binding:{binding}", binding in required, "required binding present")
    for api, shader in (manifest.get("shaders") or {}).items():
        file_check(checks, f"shader:{api}", shader, root)


def validate_checks_block(checks, manifest):
    block = manifest.get("checks") or {}
    add_check(checks, "manifest:status", manifest.get("status") == "ready", "status", "ready", manifest.get("status"))
    add_check(checks, "checks:source_status", block.get("source_job_status") == "ready", "source job status")
    add_check(checks, "checks:frames", block.get("frames") == block.get("scene_descriptors"), "scene count", block.get("frames"), block.get("scene_descriptors"))
    add_check(checks, "checks:inputs", block.get("required_inputs_present") == block.get("required_inputs_total"), "required inputs")
    add_check(checks, "checks:missing_inputs", block.get("missing_inputs") == 0, "missing inputs")
    add_check(checks, "checks:missing_shaders", block.get("missing_shaders") == 0, "missing shaders")
    add_check(checks, "checks:reference_hash", block.get("reference_hash_mismatches") == 0, "reference hashes")
    add_check(checks, "checks:output_targets", block.get("output_targets") == block.get("frames") * 3, "output targets")
    add_check(checks, "checks:scene_bytes", int(block.get("scene_descriptor_bytes") or 0) > 0, "scene descriptor bytes")


def validate_scene_descriptor(checks, manifest, frame, root):
    frame_id = frame.get("frame")
    scene = frame.get("scene_descriptor") or {}
    if not file_check(checks, f"frame:{frame_id}:scene", scene, root):
        return
    descriptor = read_json(resolve_path(scene.get("repo_path"), root))
    add_check(
        checks,
        f"frame:{frame_id}:scene_schema",
        descriptor.get("schema") == "lsfs_mitsuba_low_frequency_backend_scene_descriptor",
        "scene schema",
    )
    add_check(checks, f"frame:{frame_id}:scene_stage", descriptor.get("stage") == "renderer_post_tonemap_low_frequency_runtime_consumer", "scene stage")
    for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
        item = (descriptor.get("inputs") or {}).get(binding)
        add_check(checks, f"frame:{frame_id}:scene_input_present:{binding}", bool(item), "scene input present")
        if item:
            file_check(checks, f"frame:{frame_id}:scene_input:{binding}", item, root)
    file_check(checks, f"frame:{frame_id}:scene_reference", descriptor.get("accepted_reference") or {}, root)
    outputs = descriptor.get("outputs") or {}
    for name in ("image", "metadata", "validation"):
        add_check(checks, f"frame:{frame_id}:scene_output:{name}", bool((outputs.get(name) or {}).get("repo_path")), "scene output path")


def validate_frames(checks, manifest, root):
    frames = manifest.get("frames") or []
    add_check(checks, "frames:nonempty", bool(frames), "frames nonempty")
    for frame in frames:
        frame_id = frame.get("frame")
        for binding, item in (frame.get("inputs") or {}).items():
            file_check(checks, f"frame:{frame_id}:input:{binding}", item, root)
        file_check(checks, f"frame:{frame_id}:reference", frame.get("accepted_reference") or {}, root)
        outputs = frame.get("outputs") or {}
        for name in ("image", "metadata", "validation"):
            add_check(checks, f"frame:{frame_id}:output:{name}", bool((outputs.get(name) or {}).get("repo_path")), "output path")
        validate_scene_descriptor(checks, manifest, frame, root)


def markdown_report(validation, out_path, root):
    failed = [item for item in validation.get("checks") or [] if item.get("status") == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Manifest: `{validation['adapter_manifest']['repo_path']}`",
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
    manifest_path = require_file(resolve_path(args.manifest_path, root), "backend adapter manifest")
    manifest = read_json(manifest_path)
    checks = []
    add_check(
        checks,
        "manifest:schema",
        manifest.get("schema") == "lsfs_mitsuba_low_frequency_backend_adapter_manifest",
        "schema",
        "lsfs_mitsuba_low_frequency_backend_adapter_manifest",
        manifest.get("schema"),
    )
    add_check(checks, "manifest:version", manifest.get("version") == 1, "version", 1, manifest.get("version"))
    validate_source(checks, manifest, root)
    validate_policy(checks, manifest)
    validate_contract(checks, manifest, root)
    validate_checks_block(checks, manifest)
    file_check(checks, "command_list", manifest.get("command_list") or {}, root)
    validate_frames(checks, manifest, root)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_backend_adapter_manifest_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "adapter_manifest": {
            "path": manifest_path,
            "repo_path": posix_rel(manifest_path, root),
            "schema": manifest.get("schema"),
            "status": manifest.get("status"),
            "sha256": sha256_file(manifest_path),
            "size": os.path.getsize(manifest_path),
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
    parser = argparse.ArgumentParser(description="Validate low-frequency backend adapter descriptors")
    parser.add_argument("manifest_path")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S502 Mitsuba Low Frequency Backend Adapter Validation")
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
