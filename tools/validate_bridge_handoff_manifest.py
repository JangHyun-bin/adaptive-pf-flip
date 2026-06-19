#!/usr/bin/env python
"""Validate an accepted bridge cinematic handoff manifest."""

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    sha256_file,
    write_json,
    write_text,
)


def add_check(checks, name, status, detail="", path=None, expected=None, actual=None):
    check = {
        "name": name,
        "status": status,
        "detail": detail,
    }
    if path:
        check["path"] = path
    if expected is not None:
        check["expected"] = expected
    if actual is not None:
        check["actual"] = actual
    checks.append(check)
    return check


def resolve_manifest_path(value, root):
    path = value.get("path") or value.get("repo_path")
    if not path:
        return None
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(root, path.replace("/", os.sep)))


def check_hash(checks, root, name, item):
    path = resolve_manifest_path(item, root)
    if not path:
        add_check(checks, name, "failed", "missing path")
        return
    repo_path = posix_rel(path, root)
    if not os.path.isfile(path):
        add_check(checks, name, "failed", "file missing", path=repo_path)
        return
    expected = item.get("sha256")
    if not expected:
        add_check(checks, name, "warning", "no sha256 recorded", path=repo_path)
        return
    actual = sha256_file(path)
    status = "passed" if actual == expected else "failed"
    detail = "sha256 matched" if status == "passed" else "sha256 mismatch"
    add_check(checks, name, status, detail, path=repo_path, expected=expected, actual=actual)


def check_http(checks, name, url, method="GET", timeout=20):
    request = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.getcode()
            length = response.headers.get("Content-Length")
    except urllib.error.HTTPError as exc:
        add_check(checks, name, "failed", f"HTTP {exc.code}", path=url, actual=exc.code)
        return
    except Exception as exc:
        add_check(checks, name, "failed", str(exc), path=url)
        return
    status = "passed" if 200 <= int(status_code) < 300 else "failed"
    detail = f"HTTP {status_code}"
    if length:
        detail += f", {length} bytes"
    add_check(checks, name, status, detail, path=url, actual=status_code)


def validate_manifest(manifest, root, args):
    checks = []
    add_check(
        checks,
        "schema",
        "passed" if manifest.get("schema") == "lsfs_bridge_cinematic_handoff_manifest" else "failed",
        "schema check",
        expected="lsfs_bridge_cinematic_handoff_manifest",
        actual=manifest.get("schema"),
    )
    add_check(
        checks,
        "version",
        "passed" if manifest.get("version") == 1 else "failed",
        "version check",
        expected=1,
        actual=manifest.get("version"),
    )
    add_check(
        checks,
        "accepted_preset",
        "passed" if manifest.get("accepted_preset") else "failed",
        "accepted preset recorded",
        actual=manifest.get("accepted_preset"),
    )

    for label, item in sorted((manifest.get("sources") or {}).items()):
        if isinstance(item, dict):
            check_hash(checks, root, f"source:{label}", item)

    for index, item in enumerate(manifest.get("review_package", {}).get("artifacts", [])):
        if isinstance(item, dict):
            label = item.get("label") or f"artifact_{index}"
            check_hash(checks, root, f"artifact:{label}", item)

    public_review = manifest.get("public_review", {})
    if public_review.get("enabled"):
        status = public_review.get("status")
        add_check(
            checks,
            "publish_status",
            "passed" if status == "running" else "warning",
            "publish manifest status",
            actual=status,
        )
        if args.check_public:
            public_url = public_review.get("public_url")
            if public_url:
                check_http(checks, "public:index", public_url.rstrip("/") + "/index.html", "GET", args.timeout_seconds)
                check_http(checks, "public:shot_gif", public_url.rstrip("/") + "/assets/shot.gif", "HEAD", args.timeout_seconds)
            else:
                add_check(checks, "public:url", "failed", "public URL missing")
    elif args.check_public:
        add_check(checks, "public_review", "failed", "public review disabled")

    failed = sum(1 for item in checks if item["status"] == "failed")
    warnings = sum(1 for item in checks if item["status"] == "warning")
    return {
        "schema": "lsfs_bridge_cinematic_handoff_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_title": manifest.get("title"),
        "accepted_preset": manifest.get("accepted_preset"),
        "status": "failed" if failed else "passed",
        "failed_count": failed,
        "warning_count": warnings,
        "check_count": len(checks),
        "checks": checks,
    }


def markdown_report(validation, out_path, root):
    lines = [
        f"# {validation.get('manifest_title') or 'Bridge Handoff'} Validation",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Accepted preset: `{validation.get('accepted_preset') or 'n/a'}`",
        f"Checks: `{validation['check_count']}`",
        f"Failures: `{validation['failed_count']}`",
        f"Warnings: `{validation['warning_count']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail | Path |",
        "| --- | --- | --- | --- |",
    ]
    for item in validation.get("checks", []):
        detail = item.get("detail", "")
        path = item.get("path", "")
        lines.append(f"| {item.get('name')} | `{item.get('status')}` | {detail} | `{path}` |")
    lines.extend([
        "",
        "## Next",
        "",
        "Use this validation before treating the handoff manifest as an external-render or large-benchmark baseline.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an accepted bridge cinematic handoff manifest")
    parser.add_argument("manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args(argv)

    root = os.getcwd()
    manifest_path = os.path.abspath(args.manifest)
    manifest = read_json(manifest_path)
    validation = validate_manifest(manifest, root, args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, validation)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(validation, out_path, root))
    print(f"status={validation['status']} checks={validation['check_count']} failures={validation['failed_count']} warnings={validation['warning_count']}")
    print(f"validation={out_path}")
    print(f"report={report_path}")
    if validation["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
