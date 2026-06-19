#!/usr/bin/env python
"""Build a portable handoff bundle from a Mitsuba renderer-review contract."""

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


def resolve_path(value):
    if not value:
        return None
    return os.path.abspath(str(value).replace("/", os.sep))


def copy_entry(source, dest, label, role, root):
    resolved = require_file(source, label)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
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
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, payload


def source_entries(contract):
    for label, source in sorted((contract.get("sources") or {}).items()):
        if not source:
            continue
        path = source.get("path") or source.get("repo_path")
        if path:
            yield label, path


def copy_metadata(contract, args, root, out_dir):
    entries = []
    metadata_dir = os.path.join(out_dir, "metadata")
    entries.append(copy_entry(args.contract, os.path.join(metadata_dir, "renderer_review_contract.json"), "contract", "contract", root))
    if args.validation:
        entries.append(copy_entry(args.validation, os.path.join(metadata_dir, "contract_validation.json"), "validation", "validation", root))
    for label, path in source_entries(contract):
        entries.append(copy_entry(path, os.path.join(metadata_dir, f"{label}.json"), label, "source_metadata", root))
    return entries


def copy_artifacts(contract, root, out_dir):
    entries = []
    gallery_dir = os.path.join(out_dir, "gallery")
    for artifact in contract.get("artifacts") or []:
        source = artifact.get("path") or artifact.get("repo_path")
        if not source:
            continue
        name = os.path.basename(resolve_path(source))
        if artifact.get("label") == "gallery_index":
            name = "index.html"
        elif artifact.get("label") == "shot_gif":
            name = "shot.gif"
        entries.append(copy_entry(source, os.path.join(gallery_dir, name), artifact.get("label"), artifact.get("role", "artifact"), root))
    return entries


def copy_frame_reference(frame, frame_index, key, root, out_dir):
    source = frame.get(key)
    if not source:
        return None
    dest = os.path.join(out_dir, "reference_frames", key, f"frame_{frame_index:04d}.png")
    return copy_entry(source, dest, f"frame_{frame_index:04d}_{key}", key, root)


def build_frames(contract, args, root, out_dir):
    frames = []
    copied = []
    missing = []
    for index, frame in enumerate(contract.get("frames") or []):
        item = {
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "particles_projected": frame.get("particles_projected"),
            "secondary_counts": frame.get("secondary_counts", {}),
            "layer_coverage": frame.get("layer_coverage"),
            "references": {},
        }
        for key in ("base_preview", "secondary_layer", "composite", "graded"):
            source = frame.get(key)
            resolved = resolve_path(source)
            if not resolved or not os.path.isfile(resolved):
                missing.append({"frame": frame.get("frame"), "role": key, "path": source})
                item["references"][key] = {"status": "missing", "source_repo_path": source}
                continue
            if args.copy_reference_images:
                entry = copy_frame_reference(frame, index, key, root, out_dir)
                copied.append(entry)
                item["references"][key] = {
                    "status": "copied",
                    "source_repo_path": posix_rel(resolved, root),
                    "repo_path": entry["repo_path"],
                    "sha256": entry["sha256"],
                    "size": entry["size"],
                }
            else:
                item["references"][key] = {
                    "status": "referenced",
                    "source_repo_path": posix_rel(resolved, root),
                    "sha256": sha256_file(resolved),
                    "size": os.path.getsize(resolved),
                }
        frames.append(item)
    return frames, copied, missing


def build_bundle(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    contract_source, contract = json_source(args.contract, "renderer review contract", root)
    if contract.get("schema") != "lsfs_mitsuba_renderer_review_contract":
        raise SystemExit(f"{args.contract}: expected lsfs_mitsuba_renderer_review_contract schema")
    validation_source = None
    validation = {}
    if args.validation:
        validation_source, validation = json_source(args.validation, "renderer review contract validation", root)
        if validation.get("schema") != "lsfs_mitsuba_renderer_review_contract_validation":
            raise SystemExit(f"{args.validation}: expected lsfs_mitsuba_renderer_review_contract_validation schema")

    metadata = copy_metadata(contract, args, root, out_dir)
    artifacts = copy_artifacts(contract, root, out_dir)
    frames, frame_copies, missing = build_frames(contract, args, root, out_dir)
    copied_files = metadata + artifacts + frame_copies
    total_bytes = sum(item.get("size", 0) for item in copied_files)
    validation_ok = not validation or validation.get("status") == "passed"
    status = "ready" if contract.get("status") == "ready" and validation_ok and not missing else "failed"
    return {
        "schema": "lsfs_mitsuba_renderer_handoff_bundle",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "bundle_root": {
            "path": out_dir,
            "repo_path": posix_rel(out_dir, root),
        },
        "sources": {
            "contract": contract_source,
            "validation": validation_source,
        },
        "public_reference": contract.get("public_review", {}),
        "look_intent": contract.get("renderer_contract", {}),
        "copy_reference_images": bool(args.copy_reference_images),
        "metadata_files": metadata,
        "gallery_artifacts": artifacts,
        "frames": frames,
        "totals": {
            "frames": len(frames),
            "copied_files": len(copied_files),
            "copied_bytes": total_bytes,
            "missing_references": len(missing),
        },
        "missing_references": missing,
        "next": args.next,
    }


def markdown_report(bundle, out_path, root):
    totals = bundle.get("totals", {})
    public = bundle.get("public_reference", {})
    lines = [
        f"# {bundle['title']}",
        "",
        f"Generated UTC: `{bundle['generated_utc']}`",
        f"Bundle JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{bundle['status']}`",
        f"Bundle root: `{bundle['bundle_root']['repo_path']}`",
        f"Public URL: `{public.get('url') or 'n/a'}`",
        "",
        "## Totals",
        "",
        f"- Frames: `{totals.get('frames')}`",
        f"- Copied files: `{totals.get('copied_files')}`",
        f"- Copied bytes: `{format_bytes(totals.get('copied_bytes', 0))}`",
        f"- Missing references: `{totals.get('missing_references')}`",
        f"- Reference images copied: `{bundle.get('copy_reference_images')}`",
        "",
        "## Look Intent",
        "",
        f"- Base renderer: `{(bundle.get('look_intent') or {}).get('base_renderer')}`",
        f"- Secondary representation: `{((bundle.get('look_intent') or {}).get('secondary_layer') or {}).get('representation')}`",
        f"- Grade representation: `{((bundle.get('look_intent') or {}).get('grade') or {}).get('representation')}`",
        "",
        "## Bundle Files",
        "",
        "| Label | Role | Size | Path |",
        "| --- | --- | ---: | --- |",
    ]
    for item in (bundle.get("metadata_files") or []) + (bundle.get("gallery_artifacts") or []):
        lines.append(f"| {item['label']} | `{item['role']}` | {format_bytes(item['size'])} | `{item['repo_path']}` |")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Projected | Coverage | Graded Ref |",
        "| ---: | ---: | ---: | ---: | --- |",
    ])
    frames = bundle.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        graded = (frame.get("references") or {}).get("graded") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('particles_projected')} | "
            f"{frame.get('layer_coverage')} | `{graded.get('repo_path') or graded.get('source_repo_path')}` |"
        )
    if bundle.get("missing_references"):
        lines.extend(["", "## Missing References", ""])
        for item in bundle["missing_references"]:
            lines.append(f"- frame `{item.get('frame')}` {item.get('role')}: `{item.get('path')}`")
    lines.extend(["", "## Next", "", bundle.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Mitsuba renderer handoff bundle")
    parser.add_argument("contract")
    parser.add_argument("--validation")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--copy-reference-images", action="store_true")
    parser.add_argument("--title", default="Mitsuba Renderer Handoff Bundle")
    parser.add_argument(
        "--next",
        default="Use this bundle as the portable review reference for renderer-side secondary and look development.",
    )
    args = parser.parse_args(argv)
    bundle = build_bundle(args)
    manifest_path = os.path.abspath(args.manifest)
    write_json(manifest_path, bundle)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(manifest_path)[0] + ".md"
    write_text(report_path, markdown_report(bundle, manifest_path, os.getcwd()))
    print(
        f"status={bundle['status']} frames={bundle['totals']['frames']} "
        f"copied={bundle['totals']['copied_files']} missing={bundle['totals']['missing_references']} "
        f"manifest={manifest_path}"
    )
    print(f"report={report_path}")
    if bundle["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
