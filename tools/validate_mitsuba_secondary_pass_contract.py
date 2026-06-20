#!/usr/bin/env python
"""Validate a Mitsuba secondary-pass contract."""

import argparse
import math
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    sha256_file,
    write_json,
    write_text,
)


REQUIRED_FRAME_ASSETS = (
    "actual",
    "secondary_layer",
    "overlay",
    "overlay_graded",
    "target",
    "diff",
    "strip",
)


def resolve_path(value, root=None):
    if not value:
        return None
    text = str(value)
    if os.path.isabs(text):
        return os.path.abspath(text)
    base = root or os.getcwd()
    return os.path.abspath(os.path.join(base, text.replace("/", os.sep)))


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


def file_hash_check(checks, name, item, root):
    if not isinstance(item, dict):
        return add_check(checks, name, False, "missing file entry")
    path = resolve_path(item.get("path") or item.get("repo_path"), root)
    if not path:
        return add_check(checks, name, False, "missing path")
    if not os.path.isfile(path):
        return add_check(checks, name, False, f"missing file: {path}")
    expected_sha = item.get("sha256")
    if expected_sha:
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            return add_check(checks, name, False, "sha256 mismatch", expected_sha, actual_sha)
    expected_size = item.get("size")
    if expected_size is not None:
        actual_size = os.path.getsize(path)
        if actual_size != expected_size:
            return add_check(checks, name, False, "size mismatch", expected_size, actual_size)
    return add_check(checks, name, True, posix_rel(path, root))


def validate_sources(checks, contract, root):
    for label, source in (contract.get("sources") or {}).items():
        if not source:
            continue
        if not file_hash_check(checks, f"source:{label}", source, root):
            continue
        expected_schema = source.get("schema")
        if expected_schema:
            path = resolve_path(source.get("path") or source.get("repo_path"), root)
            payload = read_json(path)
            add_check(
                checks,
                f"source_schema:{label}",
                payload.get("schema") == expected_schema,
                "schema matches",
                expected_schema,
                payload.get("schema"),
            )


def validate_artifacts(checks, contract, root):
    for artifact in contract.get("artifacts") or []:
        label = artifact.get("label") or artifact.get("role") or "artifact"
        file_hash_check(checks, f"artifact:{label}", artifact, root)


def validate_checks_block(checks, contract, args):
    frames = contract.get("frames") or []
    block = contract.get("checks") or {}
    add_check(checks, "checks:frames", block.get("frames") == len(frames), "frame count", len(frames), block.get("frames"))
    add_check(
        checks,
        "checks:overlay_frames",
        block.get("overlay_frames") == len(frames),
        "overlay frame count",
        len(frames),
        block.get("overlay_frames"),
    )
    add_check(
        checks,
        "checks:missing_frame_assets",
        block.get("missing_frame_assets") == 0,
        "missing frame assets must stay zero",
        0,
        block.get("missing_frame_assets"),
    )
    add_check(
        checks,
        "checks:overlay_missing_references",
        block.get("overlay_missing_references") == 0,
        "overlay missing references must stay zero",
        0,
        block.get("overlay_missing_references"),
    )
    max_mad = block.get("max_overlay_mean_abs_diff")
    add_check(
        checks,
        "checks:max_overlay_mean_abs_diff",
        finite_number(max_mad) and float(max_mad) <= args.max_overlay_mean_abs_diff,
        "contract max overlay MAD",
        args.max_overlay_mean_abs_diff,
        max_mad,
    )
    mean_mad = block.get("mean_overlay_mean_abs_diff")
    add_check(
        checks,
        "checks:mean_overlay_mean_abs_diff",
        finite_number(mean_mad) and float(mean_mad) <= args.max_overlay_mean_abs_diff,
        "contract mean overlay MAD",
        args.max_overlay_mean_abs_diff,
        mean_mad,
    )
    max_diff = block.get("max_overlay_max_abs_diff")
    add_check(
        checks,
        "checks:max_overlay_max_abs_diff",
        isinstance(max_diff, int) and max_diff <= args.max_overlay_max_abs_diff,
        "contract max absolute channel diff",
        args.max_overlay_max_abs_diff,
        max_diff,
    )
    add_check(
        checks,
        "checks:public_url_present",
        bool(block.get("public_url_present")),
        "public review URL is recorded",
        True,
        block.get("public_url_present"),
    )


def validate_pass_contract(checks, contract):
    pass_contract = contract.get("secondary_pass_contract") or {}
    add_check(
        checks,
        "pass:base_renderer",
        pass_contract.get("base_renderer") == "mitsuba",
        "base renderer",
        "mitsuba",
        pass_contract.get("base_renderer"),
    )
    add_check(
        checks,
        "pass:implementation_stage",
        pass_contract.get("implementation_stage") == "screen_space_secondary_overlay_hybrid",
        "implementation stage",
        "screen_space_secondary_overlay_hybrid",
        pass_contract.get("implementation_stage"),
    )
    add_check(
        checks,
        "pass:composition",
        pass_contract.get("composition") == "alpha_composite_secondary_layer_then_apply_grade",
        "composition contract",
        "alpha_composite_secondary_layer_then_apply_grade",
        pass_contract.get("composition"),
    )
    expectations = pass_contract.get("future_renderer_expectation") or []
    add_check(
        checks,
        "pass:future_expectations",
        isinstance(expectations, list) and len(expectations) >= 3,
        "renderer-native follow-up expectations recorded",
    )


def validate_frames(checks, contract, args, root):
    frames = contract.get("frames") or []
    frame_ids = []
    output_frames = []
    for index, frame in enumerate(frames):
        frame_id = frame.get("frame")
        output_frame = frame.get("output_frame")
        frame_ids.append(frame_id)
        output_frames.append(output_frame)
        add_check(checks, f"frame:{index}:frame_id", isinstance(frame_id, int), "integer frame id")
        add_check(checks, f"frame:{index}:output_frame", isinstance(output_frame, int), "integer output frame")
        metrics = frame.get("metrics") or {}
        mad = metrics.get("overlay_mean_abs_diff")
        max_diff = metrics.get("overlay_max_abs_diff")
        add_check(
            checks,
            f"frame:{frame_id}:overlay_mean_abs_diff",
            finite_number(mad) and 0.0 <= float(mad) <= args.max_overlay_mean_abs_diff,
            "per-frame overlay MAD",
            args.max_overlay_mean_abs_diff,
            mad,
        )
        add_check(
            checks,
            f"frame:{frame_id}:overlay_max_abs_diff",
            isinstance(max_diff, int) and 0 <= max_diff <= args.max_overlay_max_abs_diff,
            "per-frame max absolute channel diff",
            args.max_overlay_max_abs_diff,
            max_diff,
        )
        assets = frame.get("assets") or {}
        for role in REQUIRED_FRAME_ASSETS:
            asset = assets.get(role)
            add_check(
                checks,
                f"frame:{frame_id}:{role}:status",
                isinstance(asset, dict) and asset.get("status") == "present",
                "asset status",
                "present",
                (asset or {}).get("status") if isinstance(asset, dict) else None,
            )
            if isinstance(asset, dict):
                file_hash_check(checks, f"frame:{frame_id}:{role}:file", asset, root)
        overlay_asset = assets.get("overlay_graded") or {}
        expected_overlay_sha = frame.get("expected_overlay_sha256")
        actual_overlay_sha = overlay_asset.get("sha256")
        add_check(
            checks,
            f"frame:{frame_id}:overlay_graded_sha",
            bool(expected_overlay_sha) and expected_overlay_sha == actual_overlay_sha,
            "overlay graded hash matches expected frame hash",
            expected_overlay_sha,
            actual_overlay_sha,
        )

    add_check(checks, "frames:unique_frame_ids", len(frame_ids) == len(set(frame_ids)), "unique frame ids")
    add_check(checks, "frames:unique_output_frames", len(output_frames) == len(set(output_frames)), "unique output frames")
    add_check(checks, "frames:ascending_output_frames", output_frames == sorted(output_frames), "ascending output frame mapping")


def http_probe(url, method, timeout):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": "lsfs-secondary-contract-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        size = response.headers.get("Content-Length")
        if method == "GET":
            body = response.read()
            size = len(body)
        elif size is not None and str(size).isdigit():
            size = int(size)
        return {
            "status": response.status,
            "content_length": size,
            "content_type": response.headers.get("content-type"),
        }


def validate_public(checks, contract, args):
    url = ((contract.get("public_review") or {}).get("url") or "").rstrip("/")
    if not args.check_public:
        add_check(checks, "public:index", True, "not requested", skipped=True)
        add_check(checks, "public:shot_gif", True, "not requested", skipped=True)
        return
    if not url:
        add_check(checks, "public:index", False, "missing public URL")
        add_check(checks, "public:shot_gif", False, "missing public URL")
        return
    for name, suffix, method in (
        ("public:index", "/index.html", "GET"),
        ("public:shot_gif", "/assets/shot.gif", "HEAD"),
    ):
        try:
            result = http_probe(url + suffix, method, args.timeout)
            add_check(checks, name, result["status"] == 200, str(result), 200, result["status"])
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            add_check(checks, name, False, str(exc))


def validate_contract(contract, args, root):
    checks = []
    add_check(
        checks,
        "contract:schema",
        contract.get("schema") == "lsfs_mitsuba_secondary_pass_contract",
        "schema",
        "lsfs_mitsuba_secondary_pass_contract",
        contract.get("schema"),
    )
    add_check(checks, "contract:version", contract.get("version") == 1, "version", 1, contract.get("version"))
    add_check(checks, "contract:status", contract.get("status") == "ready", "status", "ready", contract.get("status"))
    validate_sources(checks, contract, root)
    validate_artifacts(checks, contract, root)
    validate_checks_block(checks, contract, args)
    validate_pass_contract(checks, contract)
    validate_frames(checks, contract, args, root)
    validate_public(checks, contract, args)
    return checks


def markdown_report(validation, out_path, root):
    failed = [check for check in validation["checks"] if check["status"] == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Contract: `{validation['contract']['repo_path']}`",
        f"Public URL: `{validation.get('public_url') or 'n/a'}`",
        f"Public check: `{validation['check_public']}`",
        "",
        "## Summary",
        "",
        f"- Total checks: `{validation['summary']['total']}`",
        f"- Failed checks: `{validation['summary']['failed']}`",
        f"- Skipped checks: `{validation['summary']['skipped']}`",
        f"- Max overlay MAD threshold: `{validation['thresholds']['max_overlay_mean_abs_diff']}`",
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
    parser = argparse.ArgumentParser(description="Validate a Mitsuba secondary-pass contract")
    parser.add_argument("contract")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Pass Contract Validation")
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--max-overlay-mean-abs-diff", type=float, default=20.0)
    parser.add_argument("--max-overlay-max-abs-diff", type=int, default=255)
    args = parser.parse_args(argv)

    root = os.getcwd()
    contract_path = resolve_path(args.contract, root)
    if not contract_path or not os.path.isfile(contract_path):
        raise SystemExit(f"Missing contract: {args.contract}")
    contract = read_json(contract_path)
    checks = validate_contract(contract, args, root)
    failed = sum(1 for check in checks if check["status"] == "failed")
    skipped = sum(1 for check in checks if check["status"] == "skipped")
    validation = {
        "schema": "lsfs_mitsuba_secondary_pass_contract_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "check_public": bool(args.check_public),
        "public_url": ((contract.get("public_review") or {}).get("url") or None),
        "contract": {
            "path": contract_path,
            "repo_path": posix_rel(contract_path, root),
            "sha256": sha256_file(contract_path),
            "size": os.path.getsize(contract_path),
            "schema": contract.get("schema"),
            "version": contract.get("version"),
        },
        "thresholds": {
            "max_overlay_mean_abs_diff": args.max_overlay_mean_abs_diff,
            "max_overlay_max_abs_diff": args.max_overlay_max_abs_diff,
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
