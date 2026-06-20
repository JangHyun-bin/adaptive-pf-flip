#!/usr/bin/env python
"""Build a portable runtime handoff bundle for the low-frequency compositor."""

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
    resolved = require_file(source, label)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(resolved) != os.path.abspath(dest):
        shutil.copy2(resolved, dest)
    return {
        "label": label,
        "role": role,
        "source_path": resolved,
        "source_repo_path": posix_rel(resolved, root),
        "path": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }


def json_source(path, label, root):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    entry = {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "subschema": payload.get("subschema"),
        "status": payload.get("status"),
        "version": payload.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }
    return entry, payload


def proof_runtime_path(proof, root):
    for item in (((proof.get("gallery") or {}).get("metadata_files")) or []):
        if item.get("label") == "Runtime HTML":
            return resolve_path(item.get("asset") or item.get("repo_path"), root)
    return None


def proof_gallery_asset(proof, label, root):
    for item in (((proof.get("gallery") or {}).get("assets")) or []):
        if item.get("label") == label:
            return resolve_path(item.get("asset") or item.get("repo_path"), root)
    return None


def source_path(source, root):
    return resolve_path(source.get("path") or source.get("repo_path"), root)


def contract_source(contract, name, root):
    source = ((contract.get("sources") or {}).get(name) or {})
    path = source_path(source, root)
    if not path:
        raise SystemExit(f"contract missing source {name}")
    return path


def artifact_path(artifact, root):
    return resolve_path(artifact.get("path") or artifact.get("repo_path"), root)


def copy_metadata(webgl_summary_path, proof, contract_path, contract, root, out_dir):
    metadata_dir = os.path.join(out_dir, "metadata")
    entries = [
        copy_entry(webgl_summary_path, os.path.join(metadata_dir, "webgl_compositor_proof_summary.json"), "webgl_proof_summary", "metadata", root),
        copy_entry(contract_path, os.path.join(metadata_dir, "low_frequency_compositor_contract.json"), "compositor_contract", "metadata", root),
    ]
    for name in ("texture_package_summary", "post_tonemap_stage_summary", "target_gap_summary"):
        path = contract_source(contract, name, root)
        entries.append(copy_entry(path, os.path.join(metadata_dir, f"{name}.json"), name, "source_metadata", root))
    return entries


def copy_runtime_and_shaders(proof, contract, root, out_dir):
    entries = []
    runtime = proof_runtime_path(proof, root)
    if runtime:
        entries.append(copy_entry(runtime, os.path.join(out_dir, "runtime", "runtime_webgl.html"), "runtime_webgl", "runtime", root))
    gif = proof_gallery_asset(proof, "WebGL Proof GIF", root)
    if gif:
        entries.append(copy_entry(gif, os.path.join(out_dir, "gallery", "webgl_proof.gif"), "webgl_proof_gif", "proof_gallery", root))
    for artifact in contract.get("artifacts") or []:
        role = artifact.get("role") or "artifact"
        source = artifact_path(artifact, root)
        if not source:
            continue
        entries.append(copy_entry(source, os.path.join(out_dir, "shaders", os.path.basename(source)), artifact.get("label") or os.path.basename(source), role, root))
    return entries


def copy_frame_asset(path, dest_dir, index, label, role, root):
    ext = os.path.splitext(path)[1] or ".png"
    return copy_entry(path, os.path.join(dest_dir, f"frame_{index:04d}_{label}{ext}"), f"frame_{index:04d}_{label}", role, root)


def copy_frames(contract, proof, root, out_dir):
    proof_frames = {frame.get("output_frame"): frame for frame in proof.get("frames") or []}
    frames = []
    copied = []
    missing = []
    for index, contract_frame in enumerate(contract.get("frames") or []):
        output_frame = contract_frame.get("output_frame")
        proof_frame = proof_frames.get(output_frame)
        frame_dir = os.path.join(out_dir, "frames", f"frame_{index:04d}")
        item = {
            "frame": contract_frame.get("frame"),
            "output_frame": output_frame,
            "bindings": {},
            "proof": {},
            "oracle": {},
        }
        bindings = contract_frame.get("bindings") or {}
        for key in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb", "dark_damping_weight_luma"):
            source = resolve_path(bindings.get(key), root)
            if not source or not os.path.isfile(source):
                missing.append({"frame": contract_frame.get("frame"), "role": key, "path": bindings.get(key)})
                continue
            entry = copy_frame_asset(source, os.path.join(frame_dir, "bindings"), index, key, key, root)
            copied.append(entry)
            item["bindings"][key] = {
                "repo_path": entry["repo_path"],
                "source_repo_path": entry["source_repo_path"],
                "sha256": entry["sha256"],
                "size": entry["size"],
            }
        oracle_source = resolve_path(contract_frame.get("oracle_repo_path"), root)
        if oracle_source and os.path.isfile(oracle_source):
            entry = copy_frame_asset(oracle_source, os.path.join(frame_dir, "oracle"), index, "oracle", "oracle", root)
            copied.append(entry)
            item["oracle"] = {
                "repo_path": entry["repo_path"],
                "source_repo_path": entry["source_repo_path"],
                "sha256": entry["sha256"],
                "size": entry["size"],
            }
        else:
            missing.append({"frame": contract_frame.get("frame"), "role": "oracle", "path": contract_frame.get("oracle_repo_path")})
        if proof_frame:
            for key, role in (("webgl_repo_path", "webgl_frame"), ("strip_repo_path", "proof_strip")):
                source = resolve_path(proof_frame.get(key), root)
                if not source or not os.path.isfile(source):
                    missing.append({"frame": contract_frame.get("frame"), "role": role, "path": proof_frame.get(key)})
                    continue
                entry = copy_frame_asset(source, os.path.join(frame_dir, "proof"), index, role, role, root)
                copied.append(entry)
                item["proof"][role] = {
                    "repo_path": entry["repo_path"],
                    "source_repo_path": entry["source_repo_path"],
                    "sha256": entry["sha256"],
                    "size": entry["size"],
                }
            item["proof"]["max_abs_diff"] = proof_frame.get("max_abs_diff")
            item["proof"]["mean_abs_diff"] = proof_frame.get("mean_abs_diff")
            item["proof"]["mismatched_coverage"] = proof_frame.get("mismatched_coverage")
        else:
            missing.append({"frame": contract_frame.get("frame"), "role": "proof_frame", "path": None})
        frames.append(item)
    return frames, copied, missing


def markdown_report(bundle, manifest_path, root):
    totals = bundle.get("totals") or {}
    checks = bundle.get("checks") or {}
    lines = [
        f"# {bundle['title']}",
        "",
        f"Generated UTC: `{bundle['generated_utc']}`",
        f"Bundle JSON: `{posix_rel(manifest_path, root)}`",
        f"Status: `{bundle['status']}`",
        f"Bundle root: `{bundle['bundle_root']['repo_path']}`",
        "",
        "## Totals",
        "",
        f"- Frames: `{totals.get('frames')}`",
        f"- Copied files: `{totals.get('copied_files')}`",
        f"- Copied bytes: `{format_bytes(totals.get('copied_bytes', 0))}`",
        f"- Missing references: `{totals.get('missing_references')}`",
        "",
        "## Checks",
        "",
        f"- Proof max oracle abs diff: `{checks.get('proof_max_oracle_abs_diff')}`",
        f"- Proof max oracle mean diff: `{checks.get('proof_max_oracle_mean_abs_diff')}`",
        f"- Target-gap mean MAD: `{checks.get('target_gap_mean_mad')}`",
        f"- Target-gap max MAD: `{checks.get('target_gap_max_mad')}`",
        f"- Target-gap max abs diff: `{checks.get('target_gap_max_abs_diff')}`",
        "",
        "## Bundle Contents",
        "",
        "| Label | Role | Size | Path |",
        "| --- | --- | ---: | --- |",
    ]
    for entry in bundle.get("copied_files") or []:
        lines.append(f"| {entry.get('label')} | `{entry.get('role')}` | {format_bytes(entry.get('size', 0))} | `{entry.get('repo_path')}` |")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Proof Max Diff | Base | WebGL |",
        "| ---: | ---: | ---: | --- | --- |",
    ])
    frames = bundle.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        bindings = frame.get("bindings") or {}
        proof = frame.get("proof") or {}
        webgl = proof.get("webgl_frame") or {}
        base = bindings.get("base_rgb") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {proof.get('max_abs_diff')} | "
            f"`{base.get('repo_path')}` | `{webgl.get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", bundle.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    proof_source, proof = json_source(args.webgl_proof_summary, "webgl proof summary", root)
    if proof.get("schema") != "lsfs_mitsuba_low_frequency_webgl_compositor_proof":
        raise SystemExit(f"{args.webgl_proof_summary}: expected lsfs_mitsuba_low_frequency_webgl_compositor_proof")
    contract_path = source_path(proof.get("contract") or {}, root)
    contract_source_entry, contract = json_source(contract_path, "compositor contract", root)
    if contract.get("schema") != "lsfs_mitsuba_low_frequency_compositor_contract":
        raise SystemExit(f"{contract_path}: expected lsfs_mitsuba_low_frequency_compositor_contract")

    metadata = copy_metadata(args.webgl_proof_summary, proof, contract_path, contract, root, out_dir)
    runtime_and_shaders = copy_runtime_and_shaders(proof, contract, root, out_dir)
    frames, frame_files, missing = copy_frames(contract, proof, root, out_dir)
    copied = metadata + runtime_and_shaders + frame_files
    target_gap = read_json(contract_source(contract, "target_gap_summary", root))
    proof_checks = proof.get("checks") or {}
    target_checks = target_gap.get("checks") or {}
    totals = {
        "frames": len(frames),
        "copied_files": len(copied),
        "copied_bytes": sum(entry.get("size", 0) for entry in copied),
        "missing_references": len(missing),
    }
    checks = {
        "proof_max_oracle_abs_diff": proof_checks.get("max_oracle_abs_diff"),
        "proof_max_oracle_mean_abs_diff": proof_checks.get("max_oracle_mean_abs_diff"),
        "proof_missing_references": proof_checks.get("missing_references"),
        "target_gap_mean_mad": target_checks.get("mean_gap_mean_abs_diff"),
        "target_gap_max_mad": target_checks.get("max_gap_mean_abs_diff"),
        "target_gap_max_abs_diff": target_checks.get("max_gap_max_abs_diff"),
        "contract_status": contract.get("status"),
        "proof_status": proof.get("status"),
    }
    status = "ready"
    if missing or proof.get("status") != "ready" or contract.get("status") != "ready":
        status = "failed"
    if proof_checks.get("max_oracle_abs_diff") != 0 or proof_checks.get("max_oracle_mean_abs_diff") != 0.0:
        status = "failed"
    bundle = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_handoff_bundle",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "bundle_root": {
            "path": out_dir,
            "repo_path": posix_rel(out_dir, root),
        },
        "sources": {
            "webgl_proof_summary": proof_source,
            "compositor_contract": contract_source_entry,
        },
        "runtime_contract": contract.get("compositor_contract"),
        "checks": checks,
        "totals": totals,
        "copied_files": copied,
        "frames": frames,
        "missing_references": missing,
        "next": args.next,
    }
    manifest_path = os.path.abspath(args.manifest)
    write_json(manifest_path, bundle)
    if args.report:
        write_text(args.report, markdown_report(bundle, manifest_path, root))
    print(
        f"status={status} frames={totals['frames']} copied={totals['copied_files']} "
        f"missing={totals['missing_references']} manifest={manifest_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a low-frequency runtime handoff bundle")
    parser.add_argument("webgl_proof_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S494 Mitsuba Low Frequency Runtime Handoff Bundle")
    parser.add_argument(
        "--next",
        default="Use this portable runtime bundle as the integration artifact for production renderer UI/export work.",
    )
    args = parser.parse_args(argv)
    build(args)


if __name__ == "__main__":
    main()
