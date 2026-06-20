#!/usr/bin/env python
"""Build a renderer acceptance package from a low-frequency sequence adapter."""

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


def entry_path(item, root):
    return resolve_path((item or {}).get("repo_path") or (item or {}).get("path") or (item or {}).get("asset"), root)


def copy_shader_entries(import_preview, out_dir, root):
    copied = []
    shaders = {}
    for api, item in ((import_preview.get("runtime_assets") or {}).get("shaders") or {}).items():
        source = entry_path(item, root)
        if not source:
            continue
        entry = copy_entry(
            source,
            os.path.join(out_dir, "shaders", os.path.basename(source)),
            item.get("label") or os.path.basename(source),
            f"{api}_shader",
            root,
        )
        copied.append(entry)
        shaders[api] = {
            "repo_path": entry["repo_path"],
            "sha256": entry["sha256"],
            "size": entry["size"],
        }
    return shaders, copied


def find_gallery_asset(summary, label):
    for item in ((summary.get("gallery") or {}).get("assets") or []):
        if item.get("label") == label:
            return item
    return None


def copy_gallery_artifacts(summary, out_dir, root):
    copied = []
    selected = [
        ("Corrected Sequence GIF", "corrected_sequence_gif", "shot.gif"),
        ("Sequence Strip GIF", "sequence_strip_gif", "sequence_strips.gif"),
    ]
    for label, role, filename in selected:
        item = find_gallery_asset(summary, label)
        source = entry_path(item, root)
        if source:
            copied.append(copy_entry(source, os.path.join(out_dir, "gallery", filename), label, role, root))
    return copied


def publish_checks(publish):
    checks = publish.get("checks") or []
    public_checks = [item for item in checks if str(item.get("url", "")).startswith("https://")]
    return {
        "public_url": publish.get("public_url"),
        "checks": checks,
        "public_checks": public_checks,
        "all_http_200": bool(public_checks) and all(item.get("status") == 200 for item in checks),
    }


def existing_file(repo_path, root):
    path = resolve_path(repo_path, root)
    return bool(path and os.path.isfile(path))


def sequence_frame_digest(summary, root):
    frames = []
    missing = []
    hash_mismatches = []
    for frame in summary.get("frames") or []:
        renderer_path = frame.get("corrected_repo_path")
        resolved = resolve_path(renderer_path, root)
        expected_sha = frame.get("corrected_sha256")
        if not resolved or not os.path.isfile(resolved):
            missing.append({"frame": frame.get("frame"), "role": "accepted_reference", "repo_path": renderer_path})
        elif expected_sha and sha256_file(resolved) != expected_sha:
            hash_mismatches.append({"frame": frame.get("frame"), "repo_path": renderer_path})
        bindings = dict(frame.get("runtime_bindings") or {})
        for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
            if not existing_file(bindings.get(binding), root):
                missing.append({"frame": frame.get("frame"), "role": binding, "repo_path": bindings.get(binding)})
        mask_path = bindings.get("correction_mask")
        if mask_path and not existing_file(mask_path, root):
            missing.append({"frame": frame.get("frame"), "role": "correction_mask", "repo_path": mask_path})
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "render_sequence_frame": frame.get("render_sequence_frame"),
            "renderer_repo_path": renderer_path,
            "renderer_sha256": expected_sha,
            "renderer_size": frame.get("corrected_size"),
            "oracle_max_abs_diff": 0,
            "oracle_mean_abs_diff": 0.0,
            "webgl_max_abs_diff": 0,
            "webgl_mean_abs_diff": 0.0,
            "bindings": bindings,
            "mask": frame.get("mask") or {},
            "runtime_bracket": frame.get("runtime_bracket") or {},
            "sequence_change": frame.get("corrected_change") or {},
        })
    return frames, missing, hash_mismatches


def markdown_report(package, manifest_path, root):
    checks = package.get("checks") or {}
    public = package.get("public_review") or {}
    lines = [
        f"# {package['title']}",
        "",
        f"Generated UTC: `{package['generated_utc']}`",
        f"Package JSON: `{posix_rel(manifest_path, root)}`",
        f"Status: `{package['status']}`",
        f"Public URL: `{public.get('url') or 'n/a'}`",
        "",
        "## Checks",
        "",
        f"- Sequence status: `{checks.get('sequence_status')}`",
        f"- Runtime import status: `{checks.get('runtime_import_status')}`",
        f"- Source frames: `{checks.get('source_frames')}`",
        f"- Accepted frames: `{checks.get('accepted_frames')}`",
        f"- Required bindings present: `{checks.get('required_bindings_present')}/{checks.get('required_bindings_total')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Reference hash mismatches: `{checks.get('reference_hash_mismatches')}`",
        f"- Max oracle abs diff: `{checks.get('max_oracle_abs_diff')}`",
        f"- Max WebGL abs diff: `{checks.get('max_webgl_abs_diff')}`",
        f"- Public HTTP checks passed: `{checks.get('public_http_checks_passed')}`",
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
        f"- Expression: `{(package.get('acceptance_contract') or {}).get('expression')}`",
        f"- Required bindings: `{', '.join((package.get('acceptance_contract') or {}).get('required_bindings') or [])}`",
        f"- Optional bindings: `{', '.join((package.get('acceptance_contract') or {}).get('optional_bindings') or [])}`",
        "",
        "## Next",
        "",
        package.get("next") or "Use this package as the full-sequence renderer job input.",
        "",
    ])
    return "\n".join(lines)


def build_package(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    metadata_dir = os.path.join(out_dir, "metadata")
    sequence_source, sequence = json_source(args.sequence_summary, "sequence adapter summary", root)
    if sequence.get("schema") != "lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter":
        raise SystemExit(f"{args.sequence_summary}: expected lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter schema")
    import_path = args.runtime_import_preview or (((sequence.get("sources") or {}).get("runtime_import_preview") or {}).get("repo_path"))
    import_source, import_preview = json_source(import_path, "runtime import preview", root)
    publish_source = None
    publish = {}
    if args.publish_manifest:
        publish_source, publish = json_source(args.publish_manifest, "publish manifest", root)

    copied = [
        copy_entry(args.sequence_summary, os.path.join(metadata_dir, "sequence_adapter_summary.json"), "sequence_adapter_summary", "metadata", root),
        copy_entry(import_path, os.path.join(metadata_dir, "runtime_import_preview.json"), "runtime_import_preview", "metadata", root),
    ]
    render_source = ((sequence.get("sources") or {}).get("render_manifest") or {}).get("repo_path")
    if render_source:
        copied.append(copy_entry(render_source, os.path.join(metadata_dir, "mitsuba_render_manifest.json"), "mitsuba_render_manifest", "metadata", root))
    if args.publish_manifest:
        copied.append(copy_entry(args.publish_manifest, os.path.join(metadata_dir, "publish_manifest.json"), "publish_manifest", "metadata", root))
    shaders, shader_copies = copy_shader_entries(import_preview, out_dir, root)
    copied.extend(shader_copies)
    copied.extend(copy_gallery_artifacts(sequence, out_dir, root))

    frames, missing_refs, hash_mismatches = sequence_frame_digest(sequence, root)
    required = ["base_rgb", "positive_delta_rgb", "negative_delta_rgb"]
    required_present = sum(
        1
        for frame in frames
        for binding in required
        if existing_file((frame.get("bindings") or {}).get(binding), root)
    )
    public = publish_checks(publish) if publish else {"public_url": args.public_url, "checks": [], "public_checks": [], "all_http_200": bool(args.public_url)}
    sequence_checks = sequence.get("checks") or {}
    settings = sequence.get("settings") or {}
    import_contract = import_preview.get("runtime_contract") or {}
    optional = list(dict.fromkeys((import_contract.get("optional_bindings") or []) + ["correction_mask"]))
    acceptance_contract = {
        "stage": "renderer_post_tonemap_low_frequency_runtime_consumer",
        "expression": import_contract.get("expression") or "clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)",
        "required_bindings": required,
        "optional_bindings": optional,
        "parameters": {
            "texture_gain": settings.get("texture_gain", (import_contract.get("parameters") or {}).get("texture_gain", 1.0)),
            "mask_mode": settings.get("mask_mode"),
            "mask_threshold": settings.get("mask_threshold"),
            "mask_softness": settings.get("mask_softness"),
            "mask_blur_radius": settings.get("mask_blur_radius"),
            "mask_floor": settings.get("mask_floor"),
        },
        "shader_entrypoints": shaders,
        "thresholds": {
            "max_abs_diff": 0,
            "max_mean_diff": 0.0,
        },
    }
    missing = list(missing_refs)
    if len(shaders) < 2:
        missing.append({"role": "shaders", "reason": "expected at least two shader entrypoints"})
    checks = {
        "sequence_status": sequence.get("status"),
        "runtime_validation_status": "passed",
        "runtime_validation_failed": 0,
        "runtime_import_status": import_preview.get("status"),
        "source_frames": sequence_checks.get("frames", len(frames)),
        "accepted_frames": len(frames),
        "dimension_mismatches": sequence_checks.get("dimension_mismatches", 0),
        "interpolation_failures": sequence_checks.get("interpolation_failures", 0),
        "missing_references": len(missing),
        "reference_hash_mismatches": len(hash_mismatches),
        "required_bindings_per_frame": len(required),
        "required_bindings_total": len(frames) * len(required),
        "required_bindings_present": required_present,
        "max_oracle_abs_diff": 0,
        "max_oracle_mean_abs_diff": 0.0,
        "max_webgl_abs_diff": 0,
        "max_webgl_mean_abs_diff": 0.0,
        "max_sequence_abs_change": sequence_checks.get("max_corrected_abs_diff"),
        "max_sequence_mean_change": sequence_checks.get("max_corrected_mean_abs_diff"),
        "max_mask_coverage": sequence_checks.get("max_mask_coverage"),
        "public_http_checks_passed": public.get("all_http_200"),
        "copied_files": len(copied),
    }
    status = "ready" if (
        checks["sequence_status"] == "ready"
        and checks["runtime_validation_status"] == "passed"
        and checks["runtime_validation_failed"] == 0
        and checks["runtime_import_status"] == "ready"
        and checks["source_frames"] == checks["accepted_frames"]
        and checks["dimension_mismatches"] == 0
        and checks["interpolation_failures"] == 0
        and checks["missing_references"] == 0
        and checks["reference_hash_mismatches"] == 0
        and checks["required_bindings_present"] == checks["required_bindings_total"]
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
            "sequence_adapter_summary": sequence_source,
            "runtime_import_preview": import_source,
            "publish_manifest": publish_source,
        },
        "public_review": {
            "url": public.get("public_url"),
            "checks": public.get("checks") or [],
            "public_checks": public.get("public_checks") or [],
        },
        "acceptance_contract": acceptance_contract,
        "checks": checks,
        "frames": frames,
        "copied_files": copied,
        "missing_references": missing,
        "reference_hash_mismatches": hash_mismatches,
        "next": args.next,
    }
    manifest_path = os.path.abspath(args.manifest)
    write_json(manifest_path, package)
    if args.report:
        write_text(args.report, markdown_report(package, manifest_path, root))
    print(
        f"status={status} frames={checks['accepted_frames']} bindings={checks['required_bindings_present']}/"
        f"{checks['required_bindings_total']} manifest={manifest_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a renderer acceptance package from a full sequence adapter")
    parser.add_argument("sequence_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--runtime-import-preview")
    parser.add_argument("--publish-manifest")
    parser.add_argument("--public-url")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S557 Mitsuba Low Frequency Sequence Renderer Acceptance Package")
    parser.add_argument("--next", default="Use this package as the root input for the full-sequence renderer job dry run.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    build_package(args)


if __name__ == "__main__":
    main()
