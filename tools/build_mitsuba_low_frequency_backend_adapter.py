#!/usr/bin/env python
"""Build backend adapter descriptors from a low-frequency renderer job manifest."""

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


def read_job(path, root):
    resolved = require_file(resolve_path(path, root), "renderer job manifest")
    job = read_json(resolved)
    if job.get("schema") != "lsfs_mitsuba_low_frequency_renderer_job_manifest":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_low_frequency_renderer_job_manifest schema")
    if job.get("status") != "ready":
        raise SystemExit(f"{path}: job status is {job.get('status')!r}")
    return {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": job.get("schema"),
        "status": job.get("status"),
        "version": job.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, job


def file_ref(item, root, role, required=True):
    path = resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)
    present = bool(path and os.path.isfile(path))
    entry = {
        "role": role,
        "required": bool(required),
        "status": "present" if present else "missing",
        "repo_path": posix_rel(path, root) if path else (item or {}).get("repo_path"),
        "size": os.path.getsize(path) if present else 0,
    }
    expected_sha = (item or {}).get("expected_sha256") or (item or {}).get("sha256")
    if expected_sha:
        entry["expected_sha256"] = expected_sha
    if present:
        entry["sha256"] = sha256_file(path)
    return entry


def output_ref(item, root):
    repo_path = (item or {}).get("repo_path")
    path = resolve_path(repo_path, root)
    return {
        "repo_path": posix_rel(path, root) if path else repo_path,
        "format": (item or {}).get("format"),
        "semantics": (item or {}).get("semantics"),
    }


def shader_refs(job, root):
    refs = {}
    missing = []
    for api, shader in ((job.get("runtime_contract") or {}).get("shader_entrypoints") or {}).items():
        entry = file_ref(shader, root, f"{api}_shader", required=True)
        entry["api"] = api
        refs[api] = entry
        if entry["status"] != "present":
            missing.append({"role": f"{api}_shader", "repo_path": shader.get("repo_path")})
        elif shader.get("sha256") and entry.get("sha256") != shader.get("sha256"):
            missing.append({"role": f"{api}_shader", "repo_path": shader.get("repo_path"), "reason": "sha256_mismatch"})
    return refs, missing


def scene_descriptor(args, job, frame_job, index, root, out_dir, shaders):
    frame_name = f"frame_{index:04d}"
    scene_path = os.path.abspath(os.path.join(out_dir, "scenes", f"{frame_name}_backend_scene.json"))
    inputs = {
        key: file_ref(value, root, "texture_binding", required=True)
        for key, value in ((frame_job.get("inputs") or {}).items())
    }
    reference = file_ref(frame_job.get("accepted_reference"), root, "accepted_reference", required=True)
    outputs = {
        key: output_ref(value, root)
        for key, value in ((frame_job.get("outputs") or {}).items())
    }
    contract = job.get("runtime_contract") or {}
    descriptor = {
        "schema": "lsfs_mitsuba_low_frequency_backend_scene_descriptor",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "target_renderer": args.target_renderer,
        "backend": {
            "kind": args.backend_kind,
            "command": args.backend_command,
            "adapter_mode": "descriptor_only",
        },
        "job_index": frame_job.get("job_index"),
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "stage": frame_job.get("stage"),
        "runtime_contract": {
            "stage": contract.get("stage"),
            "expression": contract.get("expression"),
            "required_bindings": contract.get("required_bindings") or [],
            "optional_bindings": contract.get("optional_bindings") or [],
            "thresholds": contract.get("thresholds") or {},
        },
        "shaders": shaders,
        "inputs": inputs,
        "accepted_reference": reference,
        "outputs": outputs,
        "validation_expectations": frame_job.get("validation_expectations") or {},
        "backend_notes": [
            "Bind base_rgb, positive_delta_rgb, and negative_delta_rgb as post-tonemap normalized RGB textures.",
            "Apply clamp(base + (positive - negative) * texture_gain, 0, 1).",
            "Write the declared output image and validation metadata paths.",
        ],
    }
    return scene_path, descriptor


def command_line(args, scene_path, output_image):
    return (
        f'{args.backend_command} --scene "{scene_path}" '
        f'--output "{output_image}" --mode low_frequency_post_tonemap'
    )


def markdown_report(manifest, out_path, root):
    checks = manifest.get("checks") or {}
    lines = [
        f"# {manifest['title']}",
        "",
        f"Generated UTC: `{manifest['generated_utc']}`",
        f"Adapter manifest: `{posix_rel(out_path, root)}`",
        f"Status: `{manifest['status']}`",
        f"Target renderer: `{manifest['target_renderer']}`",
        f"Backend kind: `{manifest['backend']['kind']}`",
        "",
        "## Source",
        "",
        f"- Source job: `{manifest['source_job']['repo_path']}`",
        f"- Source job status: `{manifest['source_job']['status']}`",
        f"- Command list: `{manifest['command_list']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Scene descriptors: `{checks.get('scene_descriptors')}`",
        f"- Required inputs: `{checks.get('required_inputs_present')}` / `{checks.get('required_inputs_total')}`",
        f"- Missing inputs: `{checks.get('missing_inputs')}`",
        f"- Missing shaders: `{checks.get('missing_shaders')}`",
        f"- Reference hash mismatches: `{checks.get('reference_hash_mismatches')}`",
        f"- Output targets: `{checks.get('output_targets')}`",
        "",
        "## Frame Descriptors",
        "",
        "| Job | Frame | Output | Scene | Output Image |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    for frame in manifest.get("frames") or []:
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('output_frame')} | "
            f"`{frame.get('scene_descriptor', {}).get('repo_path')}` | "
            f"`{frame.get('outputs', {}).get('image', {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Commands", ""])
    for command in manifest.get("commands") or []:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Next", "", manifest.get("next") or "Use these descriptors for a backend-specific renderer dry run.", ""])
    return "\n".join(lines)


def build_manifest(args):
    root = os.getcwd()
    source, job = read_job(args.job, root)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(os.path.join(out_dir, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "render_metadata"), exist_ok=True)
    shaders, shader_missing = shader_refs(job, root)
    frames = []
    commands = []
    missing_inputs = []
    reference_mismatches = []
    required_inputs_present = 0
    required_inputs_total = 0
    output_targets = 0
    scene_bytes = 0
    for index, frame_job in enumerate(job.get("frame_jobs") or []):
        scene_path, descriptor = scene_descriptor(args, job, frame_job, index, root, out_dir, shaders)
        write_json(scene_path, descriptor)
        scene_bytes += os.path.getsize(scene_path)
        for binding, item in (descriptor.get("inputs") or {}).items():
            required_inputs_total += 1
            if item.get("status") == "present":
                required_inputs_present += 1
            else:
                missing_inputs.append({"frame": frame_job.get("frame"), "binding": binding, "repo_path": item.get("repo_path")})
        ref = descriptor.get("accepted_reference") or {}
        if ref.get("expected_sha256") and ref.get("sha256") != ref.get("expected_sha256"):
            reference_mismatches.append({"frame": frame_job.get("frame"), "repo_path": ref.get("repo_path")})
        outputs = descriptor.get("outputs") or {}
        output_targets += len(outputs)
        output_image = resolve_path((outputs.get("image") or {}).get("repo_path"), root)
        command = command_line(args, scene_path, output_image)
        commands.append(command)
        frames.append({
            "job_index": frame_job.get("job_index"),
            "frame": frame_job.get("frame"),
            "output_frame": frame_job.get("output_frame"),
            "scene_descriptor": {
                "repo_path": posix_rel(scene_path, root),
                "sha256": sha256_file(scene_path),
                "size": os.path.getsize(scene_path),
            },
            "inputs": descriptor.get("inputs") or {},
            "accepted_reference": ref,
            "outputs": outputs,
            "command": command,
        })
    command_list_path = os.path.abspath(os.path.join(out_dir, "backend_commands.txt"))
    write_text(command_list_path, "\n".join(commands) + ("\n" if commands else ""))
    checks = {
        "source_job_status": job.get("status"),
        "frames": len(job.get("frame_jobs") or []),
        "scene_descriptors": len(frames),
        "required_inputs_present": required_inputs_present,
        "required_inputs_total": required_inputs_total,
        "missing_inputs": len(missing_inputs),
        "missing_shaders": len(shader_missing),
        "reference_hash_mismatches": len(reference_mismatches),
        "output_targets": output_targets,
        "scene_descriptor_bytes": scene_bytes,
    }
    status = "ready" if (
        checks["source_job_status"] == "ready"
        and checks["frames"] > 0
        and checks["frames"] == checks["scene_descriptors"]
        and checks["required_inputs_present"] == checks["required_inputs_total"]
        and checks["missing_inputs"] == 0
        and checks["missing_shaders"] == 0
        and checks["reference_hash_mismatches"] == 0
        and checks["output_targets"] == checks["frames"] * 3
    ) else "review"
    manifest = {
        "schema": "lsfs_mitsuba_low_frequency_backend_adapter_manifest",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "target_renderer": args.target_renderer,
        "backend": {
            "kind": args.backend_kind,
            "command": args.backend_command,
            "adapter_mode": "descriptor_only",
        },
        "source_job": source,
        "dependency_policy": {
            "root_manifest_only": True,
            "root_manifest_schema": "lsfs_mitsuba_low_frequency_renderer_job_manifest",
        },
        "command_list": {
            "repo_path": posix_rel(command_list_path, root),
            "sha256": sha256_file(command_list_path),
            "size": os.path.getsize(command_list_path),
        },
        "runtime_contract": job.get("runtime_contract") or {},
        "shaders": shaders,
        "checks": checks,
        "missing_inputs": missing_inputs,
        "missing_shaders": shader_missing,
        "reference_hash_mismatches": reference_mismatches,
        "frames": frames,
        "commands": commands,
        "next": args.next,
    }
    manifest_path = os.path.abspath(args.manifest)
    write_json(manifest_path, manifest)
    if args.report:
        write_text(args.report, markdown_report(manifest, manifest_path, root))
    print(
        f"status={status} frames={checks['frames']} descriptors={checks['scene_descriptors']} "
        f"missing_inputs={checks['missing_inputs']} manifest={manifest_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build low-frequency backend adapter descriptors")
    parser.add_argument("job")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--target-renderer", default="mitsuba_or_external_path_tracer")
    parser.add_argument("--backend-kind", default="mitsuba_descriptor_skeleton")
    parser.add_argument("--backend-command", default="mitsuba_low_frequency_backend")
    parser.add_argument("--title", default="S502 Mitsuba Low Frequency Backend Adapter")
    parser.add_argument("--next", default="Use these backend descriptors as the first renderer-specific implementation skeleton.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    build_manifest(args)


if __name__ == "__main__":
    main()
