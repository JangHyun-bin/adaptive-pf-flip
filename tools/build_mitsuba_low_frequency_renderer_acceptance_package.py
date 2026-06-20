#!/usr/bin/env python
"""Build an acceptance package for the low-frequency renderer runtime path."""

import argparse
import os
import shutil
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
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


def copy_entry(source, dest, label, role, root):
    resolved = require_file(resolve_path(source, root), label)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(resolved) != os.path.abspath(dest):
        shutil.copy2(resolved, dest)
    return {
        "label": label,
        "role": role,
        "source_repo_path": posix_rel(resolved, root),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }


def json_source(path, label, root):
    resolved = require_file(resolve_path(path, root), label)
    payload = read_json(resolved)
    return {
        "label": label,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "version": payload.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, payload


def entry_path(item, root):
    return resolve_path((item or {}).get("repo_path") or (item or {}).get("path") or (item or {}).get("asset"), root)


def find_asset(summary, label):
    for item in ((summary.get("gallery") or {}).get("assets") or []):
        if item.get("label") == label:
            return item
    return None


def collect_shader_entries(import_preview, root, out_dir):
    copied = []
    shaders = {}
    for api, item in ((import_preview.get("runtime_assets") or {}).get("shaders") or {}).items():
        source = entry_path(item, root)
        if not source:
            continue
        entry = copy_entry(source, os.path.join(out_dir, "shaders", os.path.basename(source)), item.get("label") or os.path.basename(source), f"{api}_shader", root)
        copied.append(entry)
        shaders[api] = {
            "repo_path": entry["repo_path"],
            "sha256": entry["sha256"],
            "size": entry["size"],
        }
    return shaders, copied


def collect_gallery_artifacts(summary, root, out_dir):
    copied = []
    selected = [
        ("Renderer Runtime GIF", "runtime_gif", "shot.gif"),
        ("Runtime Strip GIF", "strip_gif", "runtime_consumer_strips.gif"),
    ]
    for label, role, name in selected:
        asset = find_asset(summary, label)
        source = entry_path(asset, root)
        if source:
            copied.append(copy_entry(source, os.path.join(out_dir, "gallery", name), label, role, root))
    return copied


def publish_checks(publish):
    checks = publish.get("checks") or []
    return {
        "public_url": publish.get("public_url"),
        "checks": checks,
        "all_http_200": bool(checks) and all(item.get("status") == 200 for item in checks),
        "public_checks": [item for item in checks if str(item.get("url", "")).startswith("https://")],
    }


def frame_digest(summary):
    frames = []
    for frame in summary.get("frames") or []:
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "renderer_repo_path": frame.get("renderer_repo_path"),
            "renderer_sha256": frame.get("renderer_sha256"),
            "oracle_max_abs_diff": (frame.get("oracle") or {}).get("max_abs_diff"),
            "oracle_mean_abs_diff": (frame.get("oracle") or {}).get("mean_abs_diff"),
            "webgl_max_abs_diff": (frame.get("webgl") or {}).get("max_abs_diff"),
            "webgl_mean_abs_diff": (frame.get("webgl") or {}).get("mean_abs_diff"),
            "bindings": frame.get("runtime_bindings") or {},
        })
    return frames


def markdown_report(package, manifest_path, root):
    checks = package.get("checks") or {}
    public = (package.get("public_review") or {}).get("url")
    lines = [
        f"# {package['title']}",
        "",
        f"Generated UTC: `{package['generated_utc']}`",
        f"Package JSON: `{posix_rel(manifest_path, root)}`",
        f"Status: `{package['status']}`",
        f"Public URL: `{public or 'n/a'}`",
        "",
        "## Checks",
        "",
        f"- Runtime summary status: `{checks.get('runtime_summary_status')}`",
        f"- Runtime validation status: `{checks.get('runtime_validation_status')}`",
        f"- Runtime import status: `{checks.get('runtime_import_status')}`",
        f"- Source frames: `{checks.get('source_frames')}`",
        f"- Accepted frames: `{checks.get('accepted_frames')}`",
        f"- Max oracle abs diff: `{checks.get('max_oracle_abs_diff')}`",
        f"- Max WebGL abs diff: `{checks.get('max_webgl_abs_diff')}`",
        f"- Public HTTP checks passed: `{checks.get('public_http_checks_passed')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        "",
        "## Copied Files",
        "",
        "| Label | Role | Size | Path |",
        "| --- | --- | ---: | --- |",
    ]
    for item in package.get("copied_files") or []:
        lines.append(f"| {item.get('label')} | `{item.get('role')}` | {format_bytes(item.get('size', 0))} | `{item.get('repo_path')}` |")
    lines.extend([
        "",
        "## Acceptance Contract",
        "",
        f"- Stage: `{(package.get('acceptance_contract') or {}).get('stage')}`",
        f"- Required bindings: `{', '.join((package.get('acceptance_contract') or {}).get('required_bindings') or [])}`",
        f"- Max abs threshold: `{((package.get('acceptance_contract') or {}).get('thresholds') or {}).get('max_abs_diff')}`",
        f"- Max mean threshold: `{((package.get('acceptance_contract') or {}).get('thresholds') or {}).get('max_mean_diff')}`",
        "",
        "## Next",
        "",
        package.get("next") or "Use this package as the renderer/export acceptance gate.",
        "",
    ])
    return "\n".join(lines)


def build_package(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    metadata_dir = os.path.join(out_dir, "metadata")
    summary_source, summary = json_source(args.runtime_summary, "renderer runtime preview summary", root)
    validation_source, validation = json_source(args.runtime_validation, "renderer runtime preview validation", root)
    import_path = (summary.get("source") or {}).get("runtime_import_preview")
    import_source, import_preview = json_source(import_path, "runtime import preview", root)
    handoff_path = (import_preview.get("source_bundle") or {}).get("repo_path")
    handoff_source, handoff = json_source(handoff_path, "runtime handoff bundle", root)
    publish_source = None
    publish = {}
    if args.publish_manifest:
        publish_source, publish = json_source(args.publish_manifest, "publish manifest", root)

    copied = [
        copy_entry(args.runtime_summary, os.path.join(metadata_dir, "renderer_runtime_preview_summary.json"), "renderer_runtime_preview_summary", "metadata", root),
        copy_entry(args.runtime_validation, os.path.join(metadata_dir, "renderer_runtime_preview_validation.json"), "renderer_runtime_preview_validation", "metadata", root),
        copy_entry(import_path, os.path.join(metadata_dir, "runtime_import_preview.json"), "runtime_import_preview", "metadata", root),
        copy_entry(handoff_path, os.path.join(metadata_dir, "runtime_handoff_bundle.json"), "runtime_handoff_bundle", "metadata", root),
    ]
    if args.publish_manifest:
        copied.append(copy_entry(args.publish_manifest, os.path.join(metadata_dir, "publish_manifest.json"), "publish_manifest", "metadata", root))
    shaders, shader_copies = collect_shader_entries(import_preview, root, out_dir)
    copied.extend(shader_copies)
    copied.extend(collect_gallery_artifacts(summary, root, out_dir))
    public = publish_checks(publish) if publish else {"public_url": args.public_url, "checks": [], "all_http_200": bool(args.public_url), "public_checks": []}
    checks_block = summary.get("checks") or {}
    validation_summary = validation.get("summary") or {}
    missing = []
    if not shaders:
        missing.append({"role": "shaders"})
    if not copied:
        missing.append({"role": "copied_files"})
    acceptance_contract = {
        "stage": "renderer_post_tonemap_low_frequency_runtime_consumer",
        "expression": ((import_preview.get("runtime_contract") or {}).get("expression")),
        "required_bindings": ((import_preview.get("runtime_contract") or {}).get("required_bindings") or []),
        "optional_bindings": ((import_preview.get("runtime_contract") or {}).get("optional_bindings") or []),
        "parameters": ((import_preview.get("runtime_contract") or {}).get("parameters") or {}),
        "shader_entrypoints": shaders,
        "thresholds": {
            "max_abs_diff": checks_block.get("max_abs_tolerance", 0),
            "max_mean_diff": checks_block.get("mean_abs_tolerance", 0.0),
        },
    }
    checks = {
        "runtime_summary_status": summary.get("status"),
        "runtime_validation_status": validation.get("status"),
        "runtime_validation_failed": validation_summary.get("failed"),
        "runtime_import_status": import_preview.get("status"),
        "runtime_handoff_status": handoff.get("status"),
        "source_frames": checks_block.get("source_frames"),
        "accepted_frames": checks_block.get("frames"),
        "missing_references": checks_block.get("missing_references", 0) + len(missing),
        "dimension_mismatches": checks_block.get("dimension_mismatches"),
        "max_oracle_abs_diff": checks_block.get("max_oracle_abs_diff"),
        "max_oracle_mean_abs_diff": checks_block.get("max_oracle_mean_abs_diff"),
        "max_webgl_abs_diff": checks_block.get("max_webgl_abs_diff"),
        "max_webgl_mean_abs_diff": checks_block.get("max_webgl_mean_abs_diff"),
        "public_http_checks_passed": public.get("all_http_200"),
        "copied_files": len(copied),
    }
    status = "ready" if (
        checks["runtime_summary_status"] == "ready"
        and checks["runtime_validation_status"] == "passed"
        and checks["runtime_validation_failed"] == 0
        and checks["runtime_import_status"] == "ready"
        and checks["runtime_handoff_status"] == "ready"
        and checks["source_frames"] == checks["accepted_frames"]
        and checks["missing_references"] == 0
        and checks["dimension_mismatches"] == 0
        and checks["max_oracle_abs_diff"] == 0
        and checks["max_webgl_abs_diff"] == 0
        and public.get("all_http_200")
    ) else "review"
    package = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_acceptance_package",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "package_root": {
            "path": out_dir,
            "repo_path": posix_rel(out_dir, root),
        },
        "sources": {
            "runtime_summary": summary_source,
            "runtime_validation": validation_source,
            "runtime_import_preview": import_source,
            "runtime_handoff_bundle": handoff_source,
            "publish_manifest": publish_source,
        },
        "public_review": {
            "url": public.get("public_url"),
            "checks": public.get("checks") or [],
            "public_checks": public.get("public_checks") or [],
        },
        "acceptance_contract": acceptance_contract,
        "checks": checks,
        "frames": frame_digest(summary),
        "copied_files": copied,
        "missing_references": missing,
        "next": args.next,
    }
    manifest_path = os.path.abspath(args.manifest)
    write_json(manifest_path, package)
    if args.report:
        write_text(args.report, markdown_report(package, manifest_path, root))
    print(
        f"status={status} frames={checks['accepted_frames']} copied={len(copied)} "
        f"public={public.get('public_url')} manifest={manifest_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a low-frequency renderer acceptance package")
    parser.add_argument("runtime_summary")
    parser.add_argument("runtime_validation")
    parser.add_argument("out_dir")
    parser.add_argument("--publish-manifest")
    parser.add_argument("--public-url")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S498 Mitsuba Low Frequency Renderer Acceptance Package")
    parser.add_argument("--next", default="Use this package as the production renderer/export acceptance gate.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    build_package(args)


if __name__ == "__main__":
    main()
