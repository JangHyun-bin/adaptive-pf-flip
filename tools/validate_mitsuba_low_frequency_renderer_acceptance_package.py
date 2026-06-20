#!/usr/bin/env python
"""Validate a low-frequency renderer acceptance package."""

import argparse
import os
import urllib.error
import urllib.request
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


def validate_sources(checks, package, root):
    expected = {
        "runtime_summary": ("lsfs_mitsuba_low_frequency_renderer_runtime_preview", "ready"),
        "runtime_validation": ("lsfs_mitsuba_low_frequency_renderer_runtime_preview_validation", "passed"),
        "runtime_import_preview": ("lsfs_mitsuba_low_frequency_runtime_import_preview", "ready"),
        "runtime_handoff_bundle": ("lsfs_mitsuba_low_frequency_runtime_handoff_bundle", "ready"),
    }
    for name, (schema, status) in expected.items():
        source = (package.get("sources") or {}).get(name) or {}
        if not file_check(checks, f"source:{name}", source, root):
            continue
        payload = read_json(resolve_path(source.get("repo_path") or source.get("path"), root))
        add_check(checks, f"source:{name}:schema", payload.get("schema") == schema, "source schema", schema, payload.get("schema"))
        add_check(checks, f"source:{name}:status", payload.get("status") == status, "source status", status, payload.get("status"))
    publish = (package.get("sources") or {}).get("publish_manifest")
    if publish:
        file_check(checks, "source:publish_manifest", publish, root)


def validate_contract(checks, package):
    contract = package.get("acceptance_contract") or {}
    required = contract.get("required_bindings") or []
    thresholds = contract.get("thresholds") or {}
    add_check(checks, "contract:stage", contract.get("stage") == "renderer_post_tonemap_low_frequency_runtime_consumer", "stage")
    add_check(checks, "contract:expression", "positive_delta_rgb - negative_delta_rgb" in (contract.get("expression") or ""), "low-frequency expression")
    for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
        add_check(checks, f"contract:binding:{binding}", binding in required, "required binding present")
    shaders = contract.get("shader_entrypoints") or {}
    add_check(checks, "contract:shader:glsl", "glsl" in shaders, "GLSL shader present")
    add_check(checks, "contract:shader:hlsl", "hlsl" in shaders, "HLSL shader present")
    add_check(checks, "contract:threshold:max_abs", thresholds.get("max_abs_diff") == 0, "max abs threshold", 0, thresholds.get("max_abs_diff"))
    add_check(checks, "contract:threshold:max_mean", thresholds.get("max_mean_diff") == 0.0, "max mean threshold", 0.0, thresholds.get("max_mean_diff"))


def validate_checks_block(checks, package):
    block = package.get("checks") or {}
    add_check(checks, "package:status", package.get("status") == "ready", "status", "ready", package.get("status"))
    add_check(checks, "checks:runtime_summary_status", block.get("runtime_summary_status") == "ready", "runtime summary status")
    add_check(checks, "checks:runtime_validation_status", block.get("runtime_validation_status") == "passed", "runtime validation status")
    add_check(checks, "checks:runtime_validation_failed", block.get("runtime_validation_failed") == 0, "runtime validation failures")
    add_check(checks, "checks:runtime_import_status", block.get("runtime_import_status") == "ready", "runtime import status")
    add_check(checks, "checks:runtime_handoff_status", block.get("runtime_handoff_status") == "ready", "runtime handoff status")
    add_check(checks, "checks:frames", block.get("source_frames") == block.get("accepted_frames"), "accepted all frames", block.get("source_frames"), block.get("accepted_frames"))
    add_check(checks, "checks:missing", block.get("missing_references") == 0, "missing references")
    add_check(checks, "checks:dimensions", block.get("dimension_mismatches") == 0, "dimension mismatches")
    add_check(checks, "checks:oracle_abs", block.get("max_oracle_abs_diff") == 0, "oracle max diff")
    add_check(checks, "checks:webgl_abs", block.get("max_webgl_abs_diff") == 0, "WebGL max diff")
    add_check(checks, "checks:public_http", block.get("public_http_checks_passed") is True, "public HTTP checks")
    add_check(checks, "checks:copied_files", int(block.get("copied_files") or 0) == len(package.get("copied_files") or []), "copied file count")


def validate_frames(checks, package):
    frames = package.get("frames") or []
    add_check(checks, "frames:nonempty", bool(frames), "frame list nonempty")
    for frame in frames:
        frame_id = frame.get("frame")
        add_check(checks, f"frame:{frame_id}:oracle_abs", frame.get("oracle_max_abs_diff") == 0, "oracle max diff")
        add_check(checks, f"frame:{frame_id}:oracle_mean", frame.get("oracle_mean_abs_diff") == 0.0, "oracle mean diff")
        add_check(checks, f"frame:{frame_id}:webgl_abs", frame.get("webgl_max_abs_diff") == 0, "WebGL max diff")
        add_check(checks, f"frame:{frame_id}:webgl_mean", frame.get("webgl_mean_abs_diff") == 0.0, "WebGL mean diff")
        bindings = frame.get("bindings") or {}
        for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
            add_check(checks, f"frame:{frame_id}:binding:{binding}", bool(bindings.get(binding)), "binding path present")


def http_check(url, method, timeout):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": "lsfs-acceptance-package-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if method == "GET":
            size = len(response.read())
        else:
            length = response.headers.get("Content-Length")
            size = int(length) if length and length.isdigit() else None
        return {"status": response.status, "content_length": size}


def validate_public(checks, package, args):
    public = package.get("public_review") or {}
    url = (public.get("url") or "").rstrip("/")
    add_check(checks, "public:url", bool(url and url.startswith("https://")), "public URL present")
    manifest_checks = public.get("checks") or []
    add_check(checks, "public:manifest_checks", bool(manifest_checks) and all(item.get("status") == 200 for item in manifest_checks), "manifest HTTP checks")
    if not args.check_public:
        add_check(checks, "public:live_index", True, "not requested", skipped=True)
        return
    try:
        result = http_check(f"{url}/index.html", "GET", args.timeout)
        add_check(checks, "public:live_index", result["status"] == 200, str(result), 200, result["status"])
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        add_check(checks, "public:live_index", False, str(exc))


def validate_copied_files(checks, package, root):
    for entry in package.get("copied_files") or []:
        file_check(checks, f"copied:{entry.get('role')}:{entry.get('label')}", entry, root)


def markdown_report(validation, out_path, root):
    failed = [item for item in validation.get("checks") or [] if item.get("status") == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Package: `{validation['package']['repo_path']}`",
        "",
        "## Summary",
        "",
        f"- Total checks: `{validation['summary']['total']}`",
        f"- Failed checks: `{validation['summary']['failed']}`",
        f"- Skipped checks: `{validation['summary']['skipped']}`",
        f"- Public URL: `{validation.get('public_url') or 'n/a'}`",
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
    package_path = require_file(resolve_path(args.package, root), "acceptance package")
    package = read_json(package_path)
    checks = []
    add_check(
        checks,
        "package:schema",
        package.get("schema") == "lsfs_mitsuba_low_frequency_renderer_acceptance_package",
        "schema",
        "lsfs_mitsuba_low_frequency_renderer_acceptance_package",
        package.get("schema"),
    )
    add_check(checks, "package:version", package.get("version") == 1, "version", 1, package.get("version"))
    validate_sources(checks, package, root)
    validate_contract(checks, package)
    validate_checks_block(checks, package)
    validate_frames(checks, package)
    validate_public(checks, package, args)
    validate_copied_files(checks, package, root)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    skipped = sum(1 for item in checks if item.get("status") == "skipped")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_acceptance_package_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "package": {
            "path": package_path,
            "repo_path": posix_rel(package_path, root),
            "schema": package.get("schema"),
            "status": package.get("status"),
            "sha256": sha256_file(package_path),
            "size": os.path.getsize(package_path),
        },
        "public_url": (package.get("public_review") or {}).get("url"),
        "summary": {
            "total": len(checks),
            "failed": failed,
            "skipped": skipped,
        },
        "checks": checks,
    }
    out_path = resolve_path(args.out, root)
    write_json(out_path, validation)
    if args.report:
        write_text(args.report, markdown_report(validation, out_path, root))
    print(f"status={validation['status']} total={len(checks)} failed={failed} skipped={skipped} out={out_path}")
    if failed:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a low-frequency renderer acceptance package")
    parser.add_argument("package")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S498 Mitsuba Low Frequency Renderer Acceptance Package Validation")
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
