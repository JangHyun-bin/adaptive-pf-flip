#!/usr/bin/env python
"""Validate a Mitsuba renderer target preview summary."""

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


def resolve_path(value):
    if not value:
        return None
    if os.path.isabs(value):
        return os.path.abspath(value)
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


def file_check(checks, name, path_value, expected_sha=None):
    path = resolve_path(path_value)
    if not path:
        return add_check(checks, name, False, "missing path")
    if not os.path.isfile(path):
        return add_check(checks, name, False, f"missing file: {path}")
    if expected_sha:
        actual_sha = sha256_file(path)
        if actual_sha != expected_sha:
            return add_check(checks, name, False, "sha256 mismatch", expected_sha, actual_sha)
    return add_check(checks, name, True, posix_rel(path, os.getcwd()))


def validate_summary(summary, checks, args):
    add_check(
        checks,
        "summary:schema",
        summary.get("schema") == "lsfs_mitsuba_renderer_target_preview",
        "schema",
        "lsfs_mitsuba_renderer_target_preview",
        summary.get("schema"),
    )
    add_check(checks, "summary:version", summary.get("version") == 1, "version", 1, summary.get("version"))
    add_check(checks, "summary:status", summary.get("status") == "ready", "status", "ready", summary.get("status"))
    frames = summary.get("frames") or []
    checks_block = summary.get("checks") or {}
    add_check(checks, "frames:count", len(frames) == checks_block.get("frames"), "frame count", checks_block.get("frames"), len(frames))
    add_check(
        checks,
        "frames:missing_references",
        checks_block.get("missing_references") == 0,
        "missing references",
        0,
        checks_block.get("missing_references"),
    )
    add_check(
        checks,
        "diff:composite_mean",
        float(checks_block.get("max_composite_mean_abs_diff", 999.0)) <= args.max_composite_mean_abs_diff,
        "max composite mean abs diff",
        args.max_composite_mean_abs_diff,
        checks_block.get("max_composite_mean_abs_diff"),
    )
    add_check(
        checks,
        "diff:target_mean",
        float(checks_block.get("max_target_mean_abs_diff", 999.0)) <= args.max_target_mean_abs_diff,
        "max target mean abs diff",
        args.max_target_mean_abs_diff,
        checks_block.get("max_target_mean_abs_diff"),
    )
    add_check(
        checks,
        "diff:target_max",
        int(checks_block.get("max_target_max_abs_diff", 999)) <= args.max_target_max_abs_diff,
        "max target max abs diff",
        args.max_target_max_abs_diff,
        checks_block.get("max_target_max_abs_diff"),
    )

    source = summary.get("source") or {}
    file_check(checks, "source:handoff_manifest", source.get("handoff_manifest"))
    gallery = summary.get("gallery") or {}
    file_check(checks, "gallery:index", gallery.get("index_repo_path") or gallery.get("index_path"))
    gif_path = None
    for asset in gallery.get("assets") or []:
        if asset.get("label") == "Target GIF":
            gif_path = asset.get("repo_path") or asset.get("asset")
            break
    file_check(checks, "gallery:shot_gif", gif_path)

    for frame in frames:
        frame_id = frame.get("frame")
        file_check(checks, f"frame:{frame_id}:renderer_secondary", frame.get("renderer_secondary_repo_path"))
        file_check(checks, f"frame:{frame_id}:renderer_target", frame.get("renderer_target_repo_path"), frame.get("renderer_target_sha256"))
        file_check(checks, f"frame:{frame_id}:diff", frame.get("diff_repo_path"))
        file_check(checks, f"frame:{frame_id}:strip", frame.get("strip_repo_path"))
        add_check(
            checks,
            f"frame:{frame_id}:target_mean_diff",
            float(frame.get("target_mean_abs_diff", 999.0)) <= args.max_target_mean_abs_diff,
            "target mean diff",
            args.max_target_mean_abs_diff,
            frame.get("target_mean_abs_diff"),
        )
        add_check(
            checks,
            f"frame:{frame_id}:target_max_diff",
            int(frame.get("target_max_abs_diff", 999)) <= args.max_target_max_abs_diff,
            "target max diff",
            args.max_target_max_abs_diff,
            frame.get("target_max_abs_diff"),
        )


def http_check(url, method, timeout):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": "lsfs-target-preview-validator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        size = response.headers.get("Content-Length")
        if method == "GET":
            body = response.read()
            size = len(body)
        elif size is not None and str(size).isdigit():
            size = int(size)
        return {"status": response.status, "content_length": size}


def validate_publish(summary, checks, args):
    if not args.publish_manifest:
        add_check(checks, "public:index", True, "no publish manifest supplied", skipped=True)
        add_check(checks, "public:shot_gif", True, "no publish manifest supplied", skipped=True)
        return None
    publish_path = require_file(args.publish_manifest, "publish manifest")
    publish = read_json(publish_path)
    add_check(checks, "publish:manifest", True, posix_rel(publish_path, os.getcwd()))
    public_url = (publish.get("public_url") or "").rstrip("/")
    if not public_url:
        add_check(checks, "public:index", False, "missing public URL")
        add_check(checks, "public:shot_gif", False, "missing public URL")
        return publish
    if not args.check_public:
        add_check(checks, "public:index", True, "not requested", skipped=True)
        add_check(checks, "public:shot_gif", True, "not requested", skipped=True)
        return publish
    for name, suffix, method in (
        ("public:index", "/index.html", "GET"),
        ("public:shot_gif", "/assets/shot.gif", "HEAD"),
    ):
        try:
            result = http_check(public_url + suffix, method, args.timeout)
            add_check(checks, name, result["status"] == 200, str(result), 200, result["status"])
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            add_check(checks, name, False, str(exc))
    return publish


def markdown_report(validation, out_path, root):
    failed = [check for check in validation["checks"] if check["status"] == "failed"]
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
        f"- Skipped checks: `{validation['summary']['skipped']}`",
        f"- Public URL: `{validation.get('public_url') or 'n/a'}`",
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
    parser = argparse.ArgumentParser(description="Validate a Mitsuba renderer target preview")
    parser.add_argument("summary")
    parser.add_argument("--publish-manifest")
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Renderer Target Preview Validation")
    parser.add_argument("--max-composite-mean-abs-diff", type=float, default=0.75)
    parser.add_argument("--max-target-mean-abs-diff", type=float, default=0.75)
    parser.add_argument("--max-target-max-abs-diff", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args(argv)
    root = os.getcwd()
    summary_path = require_file(args.summary, "target preview summary")
    summary = read_json(summary_path)
    checks = []
    validate_summary(summary, checks, args)
    publish = validate_publish(summary, checks, args)
    failed = sum(1 for check in checks if check["status"] == "failed")
    skipped = sum(1 for check in checks if check["status"] == "skipped")
    validation = {
        "schema": "lsfs_mitsuba_renderer_target_preview_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "passed" if failed == 0 else "failed",
        "summary_source": {
            "path": summary_path,
            "repo_path": posix_rel(summary_path, root),
            "sha256": sha256_file(summary_path),
            "size": os.path.getsize(summary_path),
            "schema": summary.get("schema"),
            "version": summary.get("version"),
        },
        "publish_source": {
            "path": os.path.abspath(args.publish_manifest) if args.publish_manifest else None,
            "repo_path": posix_rel(os.path.abspath(args.publish_manifest), root) if args.publish_manifest else None,
            "public_url": (publish or {}).get("public_url") if publish else None,
        },
        "public_url": (publish or {}).get("public_url") if publish else None,
        "thresholds": {
            "max_composite_mean_abs_diff": args.max_composite_mean_abs_diff,
            "max_target_mean_abs_diff": args.max_target_mean_abs_diff,
            "max_target_max_abs_diff": args.max_target_max_abs_diff,
        },
        "summary": {
            "total": len(checks),
            "failed": failed,
            "skipped": skipped,
        },
        "checks": checks,
    }
    out_path = os.path.abspath(args.out)
    write_json(out_path, validation)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
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
