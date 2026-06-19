#!/usr/bin/env python
"""Validate a Mitsuba renderer-review contract."""

import argparse
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


def resolve_path(value):
    if not value:
        return None
    return os.path.abspath(str(value).replace("/", os.sep))


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


def file_hash_check(checks, name, item, path_key="path"):
    path = resolve_path(item.get(path_key) or item.get("repo_path"))
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
    return add_check(checks, name, True, posix_rel(path, os.getcwd()))


def validate_sources(checks, contract):
    for label, source in (contract.get("sources") or {}).items():
        if not source:
            continue
        if not file_hash_check(checks, f"source:{label}", source):
            continue
        schema = source.get("schema")
        path = resolve_path(source.get("path") or source.get("repo_path"))
        if schema:
            payload = read_json(path)
            add_check(
                checks,
                f"source_schema:{label}",
                payload.get("schema") == schema,
                "schema matches",
                schema,
                payload.get("schema"),
            )


def validate_artifacts(checks, contract):
    for artifact in contract.get("artifacts") or []:
        file_hash_check(checks, f"artifact:{artifact.get('label')}", artifact)


def validate_frames(checks, contract):
    frames = contract.get("frames") or []
    expected = (contract.get("checks") or {}).get("frames")
    add_check(checks, "frames:count", len(frames) == expected, "contract frame count", expected, len(frames))
    for key in ("grade_frames", "composite_frames", "render_frames"):
        value = (contract.get("checks") or {}).get(key)
        add_check(checks, f"frames:{key}", value == len(frames), "source frame count matches", len(frames), value)
    add_check(
        checks,
        "frames:missing_assets",
        (contract.get("checks") or {}).get("missing_frame_assets") == 0,
        "missing frame assets must stay zero",
        0,
        (contract.get("checks") or {}).get("missing_frame_assets"),
    )

    for frame in frames:
        frame_id = frame.get("frame")
        for label in ("base_preview", "secondary_layer", "composite", "graded"):
            path = resolve_path(frame.get(label))
            add_check(
                checks,
                f"frame:{frame_id}:{label}",
                bool(path and os.path.isfile(path)),
                posix_rel(path, os.getcwd()) if path else "missing path",
            )
        graded = resolve_path(frame.get("graded"))
        expected_sha = frame.get("graded_sha256")
        if graded and os.path.isfile(graded) and expected_sha:
            actual_sha = sha256_file(graded)
            add_check(
                checks,
                f"frame:{frame_id}:graded_sha256",
                actual_sha == expected_sha,
                "graded frame hash",
                expected_sha,
                actual_sha,
            )
        projected = frame.get("particles_projected")
        add_check(
            checks,
            f"frame:{frame_id}:particles_projected",
            isinstance(projected, int) and projected >= 0,
            "non-negative projected particle count",
        )
        coverage = frame.get("layer_coverage")
        add_check(
            checks,
            f"frame:{frame_id}:layer_coverage",
            isinstance(coverage, (float, int)) and 0.0 <= float(coverage) <= 1.0,
            "coverage in [0, 1]",
        )


def http_probe(url, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": "lsfs-contract-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read(1024)
        return {
            "status": response.status,
            "content_type": response.headers.get("content-type"),
            "sample_bytes": len(data),
        }


def validate_public(checks, contract, check_public, timeout):
    url = ((contract.get("public_review") or {}).get("url") or "").rstrip("/")
    if not check_public:
        add_check(checks, "public:index", True, "not requested", skipped=True)
        add_check(checks, "public:shot_gif", True, "not requested", skipped=True)
        return
    if not url:
        add_check(checks, "public:index", False, "missing public URL")
        add_check(checks, "public:shot_gif", False, "missing public URL")
        return
    for name, suffix in (("public:index", "/index.html"), ("public:shot_gif", "/assets/shot.gif")):
        try:
            result = http_probe(url + suffix, timeout)
            add_check(checks, name, result["status"] == 200, str(result), 200, result["status"])
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            add_check(checks, name, False, str(exc))


def validate_contract(contract, args):
    checks = []
    add_check(
        checks,
        "contract:schema",
        contract.get("schema") == "lsfs_mitsuba_renderer_review_contract",
        "schema",
        "lsfs_mitsuba_renderer_review_contract",
        contract.get("schema"),
    )
    add_check(checks, "contract:version", contract.get("version") == 1, "version", 1, contract.get("version"))
    add_check(checks, "contract:status", contract.get("status") == "ready", "status", "ready", contract.get("status"))
    validate_sources(checks, contract)
    validate_artifacts(checks, contract)
    validate_frames(checks, contract)
    validate_public(checks, contract, args.check_public, args.timeout)
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
        f"Public check: `{validation['check_public']}`",
        "",
        "## Summary",
        "",
        f"- Total checks: `{validation['summary']['total']}`",
        f"- Failed checks: `{validation['summary']['failed']}`",
        f"- Skipped checks: `{validation['summary']['skipped']}`",
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
    parser = argparse.ArgumentParser(description="Validate a Mitsuba renderer-review contract")
    parser.add_argument("contract")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Renderer Review Contract Validation")
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args(argv)

    root = os.getcwd()
    contract_path = resolve_path(args.contract)
    if not contract_path or not os.path.isfile(contract_path):
        raise SystemExit(f"Missing contract: {args.contract}")
    contract = read_json(contract_path)
    checks = validate_contract(contract, args)
    failed = sum(1 for check in checks if check["status"] == "failed")
    skipped = sum(1 for check in checks if check["status"] == "skipped")
    validation = {
        "schema": "lsfs_mitsuba_renderer_review_contract_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "check_public": bool(args.check_public),
        "contract": {
            "path": contract_path,
            "repo_path": posix_rel(contract_path, root),
            "sha256": sha256_file(contract_path),
            "size": os.path.getsize(contract_path),
            "schema": contract.get("schema"),
            "version": contract.get("version"),
        },
        "summary": {
            "total": len(checks),
            "failed": failed,
            "skipped": skipped,
        },
        "checks": checks,
    }
    out_path = resolve_path(args.out)
    write_json(out_path, validation)
    report_path = resolve_path(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(validation, out_path, root))
    print(
        f"status={validation['status']} total={validation['summary']['total']} "
        f"failed={failed} skipped={skipped} out={out_path}"
    )
    print(f"report={report_path}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
