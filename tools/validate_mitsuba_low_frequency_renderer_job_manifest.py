#!/usr/bin/env python
"""Validate a low-frequency renderer job manifest."""

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


def file_check(checks, name, item, root, expected_sha=None):
    path = resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)
    if not path:
        return add_check(checks, name, False, "missing path")
    if not os.path.isfile(path):
        return add_check(checks, name, False, f"missing file: {path}")
    expected_size = (item or {}).get("size")
    if expected_size is not None:
        actual_size = os.path.getsize(path)
        if actual_size != expected_size:
            return add_check(checks, name, False, "size mismatch", expected_size, actual_size)
    expected = expected_sha or (item or {}).get("expected_sha256") or (item or {}).get("sha256")
    if expected:
        actual_sha = sha256_file(path)
        if actual_sha != expected:
            return add_check(checks, name, False, "sha256 mismatch", expected, actual_sha)
    return add_check(checks, name, True, posix_rel(path, root))


def validate_source(checks, job, root):
    source = job.get("source") or {}
    if not file_check(checks, "source:acceptance_package", source, root):
        return {}
    package = read_json(resolve_path(source.get("repo_path") or source.get("path"), root))
    add_check(
        checks,
        "source:schema",
        package.get("schema") == "lsfs_mitsuba_low_frequency_renderer_acceptance_package",
        "package schema",
        "lsfs_mitsuba_low_frequency_renderer_acceptance_package",
        package.get("schema"),
    )
    add_check(checks, "source:status", package.get("status") == "ready", "package status", "ready", package.get("status"))
    return package


def validate_dependency_policy(checks, job):
    policy = job.get("dependency_policy") or {}
    add_check(checks, "policy:root_manifest_only", policy.get("root_manifest_only") is True, "single root manifest policy")
    add_check(
        checks,
        "policy:root_manifest_schema",
        policy.get("root_manifest_schema") == "lsfs_mitsuba_low_frequency_renderer_acceptance_package",
        "root manifest schema",
    )


def validate_runtime_contract(checks, job, root):
    contract = job.get("runtime_contract") or {}
    required = contract.get("required_bindings") or []
    thresholds = contract.get("thresholds") or {}
    add_check(checks, "contract:stage", contract.get("stage") == "renderer_post_tonemap_low_frequency_runtime_consumer", "stage")
    add_check(checks, "contract:expression", "positive_delta_rgb - negative_delta_rgb" in (contract.get("expression") or ""), "expression")
    for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
        add_check(checks, f"contract:binding:{binding}", binding in required, "required binding present")
    add_check(checks, "contract:max_abs", thresholds.get("max_abs_diff") == 0, "max abs threshold", 0, thresholds.get("max_abs_diff"))
    add_check(checks, "contract:max_mean", thresholds.get("max_mean_diff") == 0.0, "max mean threshold", 0.0, thresholds.get("max_mean_diff"))
    shaders = contract.get("shader_entrypoints") or {}
    add_check(checks, "contract:shader_count", len(shaders) >= 2, "shader refs present")
    for api, shader in shaders.items():
        file_check(checks, f"contract:shader:{api}", shader, root)


def validate_checks_block(checks, job):
    block = job.get("checks") or {}
    add_check(checks, "job:status", job.get("status") == "ready", "status", "ready", job.get("status"))
    add_check(checks, "checks:package_status", block.get("package_status") == "ready", "package status")
    add_check(checks, "checks:package_validation", block.get("package_validation_status") == "passed", "package validation status")
    add_check(checks, "checks:frames", int(block.get("frames") or 0) == len(job.get("frame_jobs") or []), "frame count")
    add_check(checks, "checks:bindings", block.get("required_bindings_present") == block.get("required_bindings_total"), "all required bindings present")
    add_check(checks, "checks:missing_inputs", block.get("missing_inputs") == 0, "missing inputs")
    add_check(checks, "checks:missing_shaders", block.get("missing_shaders") == 0, "missing shaders")
    add_check(checks, "checks:reference_hash", block.get("reference_hash_mismatches") == 0, "reference hash mismatches")
    add_check(checks, "checks:public_http", block.get("public_http_checks_passed") is True, "public HTTP passed")


def output_under_root(repo_path, output_root):
    if not repo_path or not output_root:
        return False
    path = repo_path.replace("\\", "/")
    root = output_root.replace("\\", "/").rstrip("/") + "/"
    return path.startswith(root)


def validate_frame_jobs(checks, job, root):
    required = (job.get("runtime_contract") or {}).get("required_bindings") or []
    output_root = (job.get("render_settings") or {}).get("output_root")
    frames = job.get("frame_jobs") or []
    add_check(checks, "frames:nonempty", bool(frames), "frame jobs nonempty")
    for frame in frames:
        frame_id = frame.get("frame")
        inputs = frame.get("inputs") or {}
        for binding in required:
            add_check(checks, f"frame:{frame_id}:input_present:{binding}", binding in inputs, "required input in job")
            if binding in inputs:
                file_check(checks, f"frame:{frame_id}:input:{binding}", inputs.get(binding), root)
        file_check(checks, f"frame:{frame_id}:accepted_reference", frame.get("accepted_reference"), root)
        outputs = frame.get("outputs") or {}
        for name, item in outputs.items():
            add_check(
                checks,
                f"frame:{frame_id}:output_target:{name}",
                output_under_root(item.get("repo_path"), output_root),
                "output target under output_root",
            )
        expectations = frame.get("validation_expectations") or {}
        add_check(checks, f"frame:{frame_id}:oracle_abs", expectations.get("oracle_max_abs_diff") == 0, "oracle threshold")
        add_check(checks, f"frame:{frame_id}:webgl_abs", expectations.get("webgl_max_abs_diff") == 0, "WebGL threshold")


def http_check(url, method, timeout):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": "lsfs-renderer-job-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if method == "GET":
            size = len(response.read())
        else:
            length = response.headers.get("Content-Length")
            size = int(length) if length and length.isdigit() else None
        return {"status": response.status, "content_length": size}


def validate_public(checks, job, args):
    public = job.get("public_review") or {}
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


def markdown_report(validation, out_path, root):
    failed = [item for item in validation.get("checks") or [] if item.get("status") == "failed"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Job: `{validation['job']['repo_path']}`",
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
    job_path = require_file(resolve_path(args.job, root), "renderer job manifest")
    job = read_json(job_path)
    checks = []
    add_check(
        checks,
        "job:schema",
        job.get("schema") == "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        "schema",
        "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        job.get("schema"),
    )
    add_check(checks, "job:version", job.get("version") == 1, "version", 1, job.get("version"))
    validate_source(checks, job, root)
    validate_dependency_policy(checks, job)
    validate_runtime_contract(checks, job, root)
    validate_checks_block(checks, job)
    validate_frame_jobs(checks, job, root)
    validate_public(checks, job, args)
    failed = sum(1 for item in checks if item.get("status") == "failed")
    skipped = sum(1 for item in checks if item.get("status") == "skipped")
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_manifest_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "job": {
            "path": job_path,
            "repo_path": posix_rel(job_path, root),
            "schema": job.get("schema"),
            "status": job.get("status"),
            "sha256": sha256_file(job_path),
            "size": os.path.getsize(job_path),
        },
        "public_url": (job.get("public_review") or {}).get("url"),
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
    parser = argparse.ArgumentParser(description="Validate a low-frequency renderer job manifest")
    parser.add_argument("job")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S499 Mitsuba Low Frequency Renderer Job Manifest Validation")
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
