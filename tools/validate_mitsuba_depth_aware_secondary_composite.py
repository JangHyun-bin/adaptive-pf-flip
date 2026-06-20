#!/usr/bin/env python
"""Validate a Mitsuba depth-aware secondary composite summary."""

import argparse
import math
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    sha256_file,
    write_json,
    write_text,
)


REQUIRED_FRAME_FILES = (
    "native_repo_path",
    "contract_repo_path",
    "secondary_layer_repo_path",
    "target_repo_path",
    "composite_repo_path",
    "native_weight_mask_repo_path",
    "diff_repo_path",
    "strip_repo_path",
)


def resolve_path(value, root=None):
    if not value:
        return None
    text = str(value)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root or os.getcwd(), text.replace("/", os.sep)))


def add_check(checks, name, ok, detail="", expected=None, actual=None, skipped=False):
    item = {
        "name": name,
        "status": "skipped" if skipped else ("ok" if ok else "failed"),
        "detail": detail,
    }
    if expected is not None:
        item["expected"] = expected
    if actual is not None:
        item["actual"] = actual
    checks.append(item)
    return ok


def finite_number(value):
    return isinstance(value, (float, int)) and math.isfinite(float(value))


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


def validate_sources(checks, summary, root):
    for label, source in (summary.get("sources") or {}).items():
        path = source.get("path") or source.get("repo_path")
        if not file_check(checks, f"source:{label}", path, root, source.get("sha256")):
            continue
        schema = source.get("schema")
        if schema:
            payload = read_json(resolve_path(path, root))
            add_check(
                checks,
                f"source_schema:{label}",
                payload.get("schema") == schema,
                "schema matches",
                schema,
                payload.get("schema"),
            )


def validate_gallery(checks, summary, root):
    gallery = summary.get("gallery") or {}
    file_check(checks, "gallery:index", gallery.get("index_path") or gallery.get("index_repo_path"), root)
    for item in gallery.get("assets") or []:
        label = item.get("label") or "asset"
        file_check(checks, f"gallery_asset:{label}", item.get("asset") or item.get("repo_path"), root, item.get("sha256"))
    for item in gallery.get("metadata_files") or []:
        label = item.get("label") or "metadata"
        expected_sha = None if item.get("hash_policy") == "self_referential_json" else item.get("sha256")
        file_check(checks, f"gallery_metadata:{label}", item.get("asset") or item.get("repo_path"), root, expected_sha)


def validate_checks_block(checks, summary, args):
    frames = summary.get("frames") or []
    block = summary.get("checks") or {}
    contract_max = block.get("contract_max_overlay_mean_abs_diff")
    max_target = block.get("max_target_mean_abs_diff")
    mean_target = block.get("mean_target_mean_abs_diff")
    max_contract = block.get("max_contract_mean_abs_diff")
    add_check(checks, "checks:frames", block.get("frames") == len(frames), "frame count", len(frames), block.get("frames"))
    add_check(
        checks,
        "checks:missing_references",
        block.get("missing_references") == 0,
        "missing references must stay zero",
        0,
        block.get("missing_references"),
    )
    add_check(
        checks,
        "checks:max_target_mad",
        finite_number(max_target) and float(max_target) <= args.max_target_mean_abs_diff,
        "max target MAD threshold",
        args.max_target_mean_abs_diff,
        max_target,
    )
    add_check(
        checks,
        "checks:mean_target_mad",
        finite_number(mean_target) and float(mean_target) <= args.max_target_mean_abs_diff,
        "mean target MAD threshold",
        args.max_target_mean_abs_diff,
        mean_target,
    )
    add_check(
        checks,
        "checks:beats_contract_max",
        finite_number(max_target) and finite_number(contract_max) and float(max_target) < float(contract_max),
        "composite max target MAD must beat S335 contract",
        contract_max,
        max_target,
    )
    add_check(
        checks,
        "checks:max_contract_mad",
        finite_number(max_contract) and float(max_contract) <= args.max_contract_mean_abs_diff,
        "max contract drift threshold",
        args.max_contract_mean_abs_diff,
        max_contract,
    )
    mean_weight = block.get("mean_native_weight")
    add_check(
        checks,
        "checks:mean_native_weight",
        finite_number(mean_weight) and args.min_mean_native_weight <= float(mean_weight) <= args.max_mean_native_weight,
        "mean native weight range",
        [args.min_mean_native_weight, args.max_mean_native_weight],
        mean_weight,
    )


def validate_frames(checks, summary, args, root):
    frames = summary.get("frames") or []
    output_frames = []
    for index, frame in enumerate(frames):
        frame_id = frame.get("frame")
        output_frame = frame.get("output_frame")
        output_frames.append(output_frame)
        add_check(checks, f"frame:{index}:frame_id", isinstance(frame_id, int), "integer frame id")
        add_check(checks, f"frame:{index}:output_frame", isinstance(output_frame, int), "integer output frame")
        for key in REQUIRED_FRAME_FILES:
            file_check(
                checks,
                f"frame:{frame_id}:{key}",
                frame.get(key),
                root,
                frame.get("composite_sha256") if key == "composite_repo_path" else None,
            )
        target_mad = frame.get("target_mean_abs_diff")
        contract_mad = frame.get("contract_mean_abs_diff")
        weight = frame.get("native_weight_mean")
        add_check(
            checks,
            f"frame:{frame_id}:target_mad",
            finite_number(target_mad) and 0.0 <= float(target_mad) <= args.max_target_mean_abs_diff,
            "frame target MAD",
            args.max_target_mean_abs_diff,
            target_mad,
        )
        add_check(
            checks,
            f"frame:{frame_id}:contract_mad",
            finite_number(contract_mad) and 0.0 <= float(contract_mad) <= args.max_contract_mean_abs_diff,
            "frame contract MAD",
            args.max_contract_mean_abs_diff,
            contract_mad,
        )
        add_check(
            checks,
            f"frame:{frame_id}:native_weight",
            finite_number(weight) and args.min_mean_native_weight <= float(weight) <= args.max_mean_native_weight,
            "frame native weight",
            [args.min_mean_native_weight, args.max_mean_native_weight],
            weight,
        )
    add_check(checks, "frames:unique_output_frames", len(output_frames) == len(set(output_frames)), "unique output frames")
    add_check(checks, "frames:ascending_output_frames", output_frames == sorted(output_frames), "ascending output frames")


def validate_summary(summary, args, root):
    checks = []
    add_check(
        checks,
        "summary:schema",
        summary.get("schema") == "lsfs_mitsuba_depth_aware_secondary_composite",
        "schema",
        "lsfs_mitsuba_depth_aware_secondary_composite",
        summary.get("schema"),
    )
    add_check(checks, "summary:version", summary.get("version") == 1, "version", 1, summary.get("version"))
    add_check(checks, "summary:status", summary.get("status") == "ready", "status", "ready", summary.get("status"))
    validate_sources(checks, summary, root)
    validate_gallery(checks, summary, root)
    validate_checks_block(checks, summary, args)
    validate_frames(checks, summary, args, root)
    return checks


def markdown_report(validation, out_path, root):
    failed = [check for check in validation["checks"] if check["status"] == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Composite: `{validation['composite']['repo_path']}`",
        "",
        "## Summary",
        "",
        f"- Total checks: `{validation['summary']['total']}`",
        f"- Failed checks: `{validation['summary']['failed']}`",
        f"- Skipped checks: `{validation['summary']['skipped']}`",
        f"- Max target MAD threshold: `{validation['thresholds']['max_target_mean_abs_diff']}`",
        f"- Max contract MAD threshold: `{validation['thresholds']['max_contract_mean_abs_diff']}`",
        "",
        "## Failed Checks",
        "",
    ]
    if failed:
        for check in failed:
            lines.append(f"- {check['name']}: {check.get('detail', '')}")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ])
    for check in validation["checks"]:
        detail = str(check.get("detail", "")).replace("|", "\\|")
        lines.append(f"| `{check['name']}` | `{check['status']}` | {detail} |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a Mitsuba depth-aware secondary composite")
    parser.add_argument("summary")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Depth-Aware Secondary Composite Validation")
    parser.add_argument("--max-target-mean-abs-diff", type=float, default=18.0)
    parser.add_argument("--max-contract-mean-abs-diff", type=float, default=9.0)
    parser.add_argument("--min-mean-native-weight", type=float, default=0.10)
    parser.add_argument("--max-mean-native-weight", type=float, default=0.18)
    args = parser.parse_args(argv)

    root = os.getcwd()
    summary_path = resolve_path(args.summary, root)
    if not summary_path or not os.path.isfile(summary_path):
        raise SystemExit(f"Missing composite summary: {args.summary}")
    composite = read_json(summary_path)
    checks = validate_summary(composite, args, root)
    failed = sum(1 for check in checks if check["status"] == "failed")
    skipped = sum(1 for check in checks if check["status"] == "skipped")
    validation = {
        "schema": "lsfs_mitsuba_depth_aware_secondary_composite_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "composite": {
            "path": summary_path,
            "repo_path": posix_rel(summary_path, root),
            "sha256": sha256_file(summary_path),
            "size": os.path.getsize(summary_path),
            "schema": composite.get("schema"),
            "version": composite.get("version"),
        },
        "thresholds": {
            "max_target_mean_abs_diff": args.max_target_mean_abs_diff,
            "max_contract_mean_abs_diff": args.max_contract_mean_abs_diff,
            "min_mean_native_weight": args.min_mean_native_weight,
            "max_mean_native_weight": args.max_mean_native_weight,
        },
        "summary": {
            "total": len(checks),
            "failed": failed,
            "skipped": skipped,
        },
        "checks": checks,
    }
    out_path = resolve_path(args.out, root)
    write_json(out_path, validation)
    report_path = resolve_path(args.report, root) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(validation, out_path, root))
    print(
        f"status={validation['status']} total={len(checks)} failed={failed} "
        f"skipped={skipped} out={out_path}"
    )
    print(f"report={report_path}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
