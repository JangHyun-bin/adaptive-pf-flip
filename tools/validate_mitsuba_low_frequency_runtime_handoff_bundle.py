#!/usr/bin/env python
"""Validate a low-frequency runtime handoff bundle."""

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
    expected_sha = item.get("sha256")
    if expected_sha:
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            return add_check(checks, name, False, "sha256 mismatch", expected_sha, actual_sha)
    return add_check(checks, name, True, posix_rel(path, root))


def validate_sources(checks, bundle, root):
    for label, source in (bundle.get("sources") or {}).items():
        if not file_check(checks, f"source:{label}", source, root):
            continue
        schema = source.get("schema")
        path = resolve_path(source.get("repo_path") or source.get("path"), root)
        if schema:
            payload = read_json(path)
            add_check(checks, f"source_schema:{label}", payload.get("schema") == schema, "schema matches", schema, payload.get("schema"))


def validate_copied_files(checks, bundle, root):
    for entry in bundle.get("copied_files") or []:
        file_check(checks, f"copied:{entry.get('role')}:{entry.get('label')}", entry, root)


def validate_runtime_contract(checks, bundle):
    contract = bundle.get("runtime_contract") or {}
    required = contract.get("required_bindings") or []
    add_check(checks, "runtime_contract:stage", contract.get("stage") == "post_tonemap", "stage", "post_tonemap", contract.get("stage"))
    add_check(checks, "runtime_contract:expression", "positive_delta_rgb - negative_delta_rgb" in (contract.get("expression") or ""), "delta expression")
    for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
        add_check(checks, f"runtime_contract:binding:{binding}", binding in required, "required binding present")


def validate_checks_block(checks, bundle):
    block = bundle.get("checks") or {}
    totals = bundle.get("totals") or {}
    add_check(checks, "bundle:status", bundle.get("status") == "ready", "status", "ready", bundle.get("status"))
    add_check(checks, "checks:contract_status", block.get("contract_status") == "ready", "contract status", "ready", block.get("contract_status"))
    add_check(checks, "checks:proof_status", block.get("proof_status") == "ready", "proof status", "ready", block.get("proof_status"))
    add_check(checks, "checks:proof_abs_diff", block.get("proof_max_oracle_abs_diff") == 0, "WebGL proof max abs diff", 0, block.get("proof_max_oracle_abs_diff"))
    add_check(checks, "checks:proof_mean_diff", block.get("proof_max_oracle_mean_abs_diff") == 0.0, "WebGL proof max mean diff", 0.0, block.get("proof_max_oracle_mean_abs_diff"))
    add_check(checks, "checks:proof_missing", block.get("proof_missing_references") == 0, "WebGL proof missing refs", 0, block.get("proof_missing_references"))
    add_check(checks, "totals:frames", totals.get("frames") == len(bundle.get("frames") or []), "frame count", len(bundle.get("frames") or []), totals.get("frames"))
    add_check(checks, "totals:missing", totals.get("missing_references") == 0, "missing references", 0, totals.get("missing_references"))
    add_check(checks, "totals:copied_files", totals.get("copied_files") == len(bundle.get("copied_files") or []), "copied file count", len(bundle.get("copied_files") or []), totals.get("copied_files"))
    for key in ("target_gap_mean_mad", "target_gap_max_mad", "target_gap_max_abs_diff"):
        value = block.get(key)
        add_check(checks, f"checks:{key}", isinstance(value, (int, float)) and value >= 0, "non-negative target gap metric", actual=value)


def validate_frames(checks, bundle, root):
    for frame in bundle.get("frames") or []:
        frame_id = frame.get("frame")
        bindings = frame.get("bindings") or {}
        for key in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb", "dark_damping_weight_luma"):
            file_check(checks, f"frame:{frame_id}:binding:{key}", bindings.get(key), root)
        oracle = frame.get("oracle") or {}
        file_check(checks, f"frame:{frame_id}:oracle", oracle, root)
        proof = frame.get("proof") or {}
        file_check(checks, f"frame:{frame_id}:proof:webgl", proof.get("webgl_frame"), root)
        file_check(checks, f"frame:{frame_id}:proof:strip", proof.get("proof_strip"), root)
        add_check(checks, f"frame:{frame_id}:proof_abs_diff", proof.get("max_abs_diff") == 0, "frame WebGL proof diff", 0, proof.get("max_abs_diff"))
        add_check(checks, f"frame:{frame_id}:proof_mean_diff", proof.get("mean_abs_diff") == 0.0, "frame WebGL proof mean diff", 0.0, proof.get("mean_abs_diff"))


def markdown_report(validation, out_path, root):
    failed = [item for item in validation.get("checks") or [] if item.get("status") == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Bundle: `{validation['bundle']['repo_path']}`",
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
    bundle_path = resolve_path(args.bundle, root)
    if not bundle_path or not os.path.isfile(bundle_path):
        raise SystemExit(f"Missing bundle: {args.bundle}")
    bundle = read_json(bundle_path)
    checks = []
    add_check(
        checks,
        "bundle:schema",
        bundle.get("schema") == "lsfs_mitsuba_low_frequency_runtime_handoff_bundle",
        "schema",
        "lsfs_mitsuba_low_frequency_runtime_handoff_bundle",
        bundle.get("schema"),
    )
    add_check(checks, "bundle:version", bundle.get("version") == 1, "version", 1, bundle.get("version"))
    validate_sources(checks, bundle, root)
    validate_runtime_contract(checks, bundle)
    validate_checks_block(checks, bundle)
    validate_copied_files(checks, bundle, root)
    validate_frames(checks, bundle, root)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_handoff_bundle_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "sha256": sha256_file(bundle_path),
            "schema": bundle.get("schema"),
            "status": bundle.get("status"),
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
    parser = argparse.ArgumentParser(description="Validate a low-frequency runtime handoff bundle")
    parser.add_argument("bundle")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S494 Mitsuba Low Frequency Runtime Handoff Bundle Validation")
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
