#!/usr/bin/env python
"""Build a production renderer job manifest from a low-frequency acceptance package."""

import argparse
import os
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


def source_package(path, root):
    resolved = require_file(resolve_path(path, root), "renderer acceptance package")
    package = read_json(resolved)
    if package.get("schema") != "lsfs_mitsuba_low_frequency_renderer_acceptance_package":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_low_frequency_renderer_acceptance_package schema")
    if package.get("status") != "ready":
        raise SystemExit(f"{path}: package status is {package.get('status')!r}")
    return {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": package.get("schema"),
        "status": package.get("status"),
        "version": package.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, package


def file_entry(repo_path, root, label, role):
    path = resolve_path(repo_path, root)
    present = bool(path and os.path.isfile(path))
    entry = {
        "label": label,
        "role": role,
        "status": "present" if present else "missing",
        "repo_path": posix_rel(path, root) if path else repo_path,
        "size": os.path.getsize(path) if present else 0,
    }
    if present:
        entry["sha256"] = sha256_file(path)
    return entry


def frame_input(binding, frame, root):
    repo_path = (frame.get("bindings") or {}).get(binding)
    entry = file_entry(repo_path, root, binding, "texture_binding")
    entry["semantic"] = binding
    entry["color_space"] = "tonemapped_rgb_normalized"
    entry["required"] = True
    return entry


def frame_reference(frame, root):
    entry = file_entry(frame.get("renderer_repo_path"), root, "accepted_renderer_reference", "accepted_reference")
    entry["expected_sha256"] = frame.get("renderer_sha256")
    entry["oracle_max_abs_diff"] = frame.get("oracle_max_abs_diff")
    entry["webgl_max_abs_diff"] = frame.get("webgl_max_abs_diff")
    return entry


def frame_job(frame, index, package, root, output_dir, output_format):
    output_name = f"frame_{index:04d}.{output_format}"
    output_path = os.path.join(output_dir, output_name)
    metadata_path = os.path.join(output_dir, "metadata", f"frame_{index:04d}.json")
    validation_path = os.path.join(output_dir, "validation", f"frame_{index:04d}.json")
    inputs = {
        binding: frame_input(binding, frame, root)
        for binding in ((package.get("acceptance_contract") or {}).get("required_bindings") or [])
    }
    reference = frame_reference(frame, root)
    return {
        "frame": frame.get("frame"),
        "output_frame": frame.get("output_frame"),
        "job_index": index,
        "stage": "renderer_post_tonemap_low_frequency_runtime_consumer",
        "inputs": inputs,
        "accepted_reference": reference,
        "outputs": {
            "image": {
                "repo_path": posix_rel(output_path, root),
                "format": output_format,
                "semantics": "post-tonemap low-frequency corrected renderer frame",
            },
            "metadata": {
                "repo_path": posix_rel(metadata_path, root),
                "format": "json",
            },
            "validation": {
                "repo_path": posix_rel(validation_path, root),
                "format": "json",
            },
        },
        "validation_expectations": {
            "reference_sha256": frame.get("renderer_sha256"),
            "oracle_max_abs_diff": frame.get("oracle_max_abs_diff"),
            "oracle_mean_abs_diff": frame.get("oracle_mean_abs_diff"),
            "webgl_max_abs_diff": frame.get("webgl_max_abs_diff"),
            "webgl_mean_abs_diff": frame.get("webgl_mean_abs_diff"),
        },
    }


def collect_shader_refs(package, root):
    shaders = {}
    missing = []
    for api, shader in ((package.get("acceptance_contract") or {}).get("shader_entrypoints") or {}).items():
        entry = file_entry(shader.get("repo_path"), root, f"{api}_shader", "shader")
        entry["api"] = api
        entry["expected_sha256"] = shader.get("sha256")
        shaders[api] = entry
        if entry["status"] != "present":
            missing.append({"role": f"{api}_shader", "repo_path": shader.get("repo_path")})
        elif shader.get("sha256") and entry.get("sha256") != shader.get("sha256"):
            missing.append({"role": f"{api}_shader", "repo_path": shader.get("repo_path"), "reason": "sha256_mismatch"})
    return shaders, missing


def markdown_report(job, manifest_path, root):
    checks = job.get("checks") or {}
    settings = job.get("render_settings") or {}
    lines = [
        f"# {job['title']}",
        "",
        f"Generated UTC: `{job['generated_utc']}`",
        f"Job JSON: `{posix_rel(manifest_path, root)}`",
        f"Status: `{job['status']}`",
        f"Target renderer: `{job['target_renderer']}`",
        "",
        "## Source",
        "",
        f"- Acceptance package: `{job['source']['repo_path']}`",
        f"- Package status: `{job['source']['status']}`",
        f"- Public URL: `{(job.get('public_review') or {}).get('url') or 'n/a'}`",
        "",
        "## Render Settings",
        "",
        f"- Output root: `{settings.get('output_root')}`",
        f"- Output format: `{settings.get('output_format')}`",
        f"- Frame naming: `{settings.get('frame_naming')}`",
        f"- Texture gain: `{settings.get('texture_gain')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Required bindings per frame: `{checks.get('required_bindings_per_frame')}`",
        f"- Required bindings present: `{checks.get('required_bindings_present')}`",
        f"- Missing inputs: `{checks.get('missing_inputs')}`",
        f"- Missing shaders: `{checks.get('missing_shaders')}`",
        f"- Reference hash mismatches: `{checks.get('reference_hash_mismatches')}`",
        f"- Public HTTP passed: `{checks.get('public_http_checks_passed')}`",
        "",
        "## Runtime Contract",
        "",
        f"- Stage: `{(job.get('runtime_contract') or {}).get('stage')}`",
        f"- Expression: `{(job.get('runtime_contract') or {}).get('expression')}`",
        f"- Required bindings: `{', '.join((job.get('runtime_contract') or {}).get('required_bindings') or [])}`",
        "",
        "## Frame Jobs",
        "",
        "| Job | Frame | Output | Inputs | Target | Reference |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in job.get("frame_jobs") or []:
        lines.append(
            f"| {item.get('job_index')} | {item.get('frame')} | {item.get('output_frame')} | "
            f"{len(item.get('inputs') or {})} | `{(item.get('outputs') or {}).get('image', {}).get('repo_path')}` | "
            f"`{(item.get('accepted_reference') or {}).get('repo_path')}` |"
        )
    lines.extend([
        "",
        "## Runner Commands",
        "",
    ])
    for command in job.get("runner_commands") or []:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Next", "", job.get("next") or "Use this job manifest as the production renderer/export adapter input.", ""])
    return "\n".join(lines)


def build_job(args):
    root = os.getcwd()
    package_source, package = source_package(args.acceptance_package, root)
    out_dir = os.path.abspath(args.out_dir)
    output_dir = os.path.join(out_dir, "outputs")
    for directory in (output_dir, os.path.join(output_dir, "metadata"), os.path.join(output_dir, "validation")):
        os.makedirs(directory, exist_ok=True)
    contract = package.get("acceptance_contract") or {}
    shaders, shader_missing = collect_shader_refs(package, root)
    frames = package.get("frames") or []
    frame_jobs = [frame_job(frame, index, package, root, output_dir, args.output_format) for index, frame in enumerate(frames)]
    missing_inputs = []
    reference_hash_mismatches = []
    for job in frame_jobs:
        for binding, entry in (job.get("inputs") or {}).items():
            if entry.get("status") != "present":
                missing_inputs.append({"frame": job.get("frame"), "binding": binding, "repo_path": entry.get("repo_path")})
        ref = job.get("accepted_reference") or {}
        if ref.get("status") != "present":
            missing_inputs.append({"frame": job.get("frame"), "binding": "accepted_reference", "repo_path": ref.get("repo_path")})
        elif ref.get("expected_sha256") and ref.get("sha256") != ref.get("expected_sha256"):
            reference_hash_mismatches.append({"frame": job.get("frame"), "repo_path": ref.get("repo_path")})
    required_per_frame = len(contract.get("required_bindings") or [])
    required_present = sum(
        1
        for job in frame_jobs
        for entry in (job.get("inputs") or {}).values()
        if entry.get("status") == "present"
    )
    checks = {
        "package_status": package.get("status"),
        "package_validation_status": (package.get("checks") or {}).get("runtime_validation_status"),
        "frames": len(frame_jobs),
        "required_bindings_per_frame": required_per_frame,
        "required_bindings_total": len(frame_jobs) * required_per_frame,
        "required_bindings_present": required_present,
        "missing_inputs": len(missing_inputs),
        "missing_shaders": len(shader_missing),
        "reference_hash_mismatches": len(reference_hash_mismatches),
        "public_http_checks_passed": (package.get("checks") or {}).get("public_http_checks_passed"),
        "oracle_threshold": ((contract.get("thresholds") or {}).get("max_abs_diff")),
        "mean_threshold": ((contract.get("thresholds") or {}).get("max_mean_diff")),
    }
    status = "ready" if (
        checks["package_status"] == "ready"
        and checks["package_validation_status"] == "passed"
        and checks["frames"] > 0
        and checks["required_bindings_present"] == checks["required_bindings_total"]
        and checks["missing_inputs"] == 0
        and checks["missing_shaders"] == 0
        and checks["reference_hash_mismatches"] == 0
        and checks["public_http_checks_passed"] is True
        and checks["oracle_threshold"] == 0
        and checks["mean_threshold"] == 0.0
    ) else "review"
    manifest_path = os.path.abspath(args.manifest)
    job = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "target_renderer": args.target_renderer,
        "source": package_source,
        "dependency_policy": {
            "root_manifest_only": True,
            "root_manifest_schema": package_source.get("schema"),
            "note": "This adapter reads only the S498 acceptance package as its root input; frame assets are referenced through that package contract.",
        },
        "render_settings": {
            "output_root": posix_rel(output_dir, root),
            "output_format": args.output_format,
            "frame_naming": "frame_%04d",
            "color_space": "tonemapped_rgb_normalized",
            "texture_gain": (contract.get("parameters") or {}).get("texture_gain", 1.0),
        },
        "runtime_contract": {
            "stage": contract.get("stage"),
            "expression": contract.get("expression"),
            "required_bindings": contract.get("required_bindings") or [],
            "optional_bindings": contract.get("optional_bindings") or [],
            "shader_entrypoints": shaders,
            "thresholds": contract.get("thresholds") or {},
        },
        "public_review": package.get("public_review") or {},
        "checks": checks,
        "missing_inputs": missing_inputs,
        "missing_shaders": shader_missing,
        "reference_hash_mismatches": reference_hash_mismatches,
        "frame_jobs": frame_jobs,
        "runner_commands": [
            f"load {posix_rel(manifest_path, root)}",
            "for each frame_job: bind base_rgb, positive_delta_rgb, negative_delta_rgb",
            "execute renderer_post_tonemap_low_frequency_runtime_consumer",
            "write outputs.image and outputs.metadata",
            "validate outputs.image sha256 or zero-diff against accepted_reference",
        ],
        "next": args.next,
    }
    write_json(manifest_path, job)
    if args.report:
        write_text(args.report, markdown_report(job, manifest_path, root))
    print(
        f"status={status} frames={checks['frames']} inputs={checks['required_bindings_present']}/"
        f"{checks['required_bindings_total']} manifest={manifest_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a production renderer job manifest from an acceptance package")
    parser.add_argument("acceptance_package")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S499 Mitsuba Low Frequency Renderer Job Manifest")
    parser.add_argument("--target-renderer", default="mitsuba_or_external_path_tracer")
    parser.add_argument("--output-format", default="png")
    parser.add_argument("--next", default="Use this job manifest as the sole input for the first production renderer/export dry run.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if not args.output_format or any(ch in args.output_format for ch in "\\/ ."):
        parser.error("output-format must be a simple extension without punctuation")
    build_job(args)


if __name__ == "__main__":
    main()
