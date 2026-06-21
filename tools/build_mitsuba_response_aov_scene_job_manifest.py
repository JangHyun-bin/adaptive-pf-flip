#!/usr/bin/env python
"""Build renderer/cache job descriptors from a response-AOV scene handoff."""

import argparse
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


HANDOFF_SCHEMA = "lsfs_mitsuba_response_aov_scene_handoff"
JOB_SCHEMA = "lsfs_mitsuba_response_aov_scene_job_manifest"
DESCRIPTOR_SCHEMA = "lsfs_mitsuba_response_aov_scene_frame_job"
STAGE = "renderer_cache_scene_response_aov_consumer"
AOV_KEYS = (
    "base_rgb",
    "response_positive_rgb",
    "response_negative_rgb",
    "selected_composite_rgb",
    "full_render_rgb",
)
SCENE_ASSET_KEYS = ("camera", "particles", "phase_cells", "water_mesh")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_handoff(path, root):
    resolved = require_file(resolve_path(path, root), "response-AOV scene handoff")
    payload = read_json(resolved)
    if payload.get("schema") != HANDOFF_SCHEMA:
        raise SystemExit(f"{path}: expected {HANDOFF_SCHEMA} schema")
    if payload.get("status") != "ready":
        raise SystemExit(f"{path}: handoff status is {payload.get('status')!r}")
    return resolved, payload


def file_status(entry, root, role, required=True, verify_hash=True):
    source = entry or {}
    repo_path = source.get("repo_path") or source.get("path")
    path = resolve_path(repo_path, root)
    expected_sha = source.get("sha256") or source.get("expected_sha256")
    expected_size = source.get("size")
    result = {
        "role": role,
        "required": required,
        "repo_path": posix_rel(path, root) if path else repo_path,
        "status": "missing",
    }
    issues = []
    if not path or not os.path.isfile(path):
        if required:
            issues.append({"role": role, "repo_path": repo_path, "reason": "missing"})
        return result, issues
    result.update({
        "status": "present",
        "size": os.path.getsize(path),
    })
    dims = image_dimensions(path)
    if dims:
        result["dimensions"] = dims
    if expected_size is not None:
        result["expected_size"] = expected_size
        if int(expected_size) != result["size"]:
            issues.append({
                "role": role,
                "repo_path": result["repo_path"],
                "reason": "size_mismatch",
                "expected": expected_size,
                "actual": result["size"],
            })
    if expected_sha:
        result["expected_sha256"] = expected_sha
    if verify_hash or expected_sha:
        actual_sha = sha256_file(path)
        result["sha256"] = actual_sha
        if expected_sha and actual_sha != expected_sha:
            issues.append({
                "role": role,
                "repo_path": result["repo_path"],
                "reason": "sha256_mismatch",
                "expected": expected_sha,
                "actual": actual_sha,
            })
    return result, issues


def source_status(source, root, label):
    result, issues = file_status(source, root, label, required=True, verify_hash=True)
    result["schema"] = source.get("schema")
    result["source_status"] = source.get("status")
    result["subschema"] = source.get("subschema")
    return result, issues


def compact_render_data(frame):
    data = frame.get("render_data") or {}
    return {
        "source_frame": data.get("source_frame"),
        "source_time": data.get("source_time"),
        "water_bounds_min": data.get("water_bounds_min"),
        "water_bounds_max": data.get("water_bounds_max"),
        "water_depth_y_span": data.get("water_depth_y_span"),
        "water_depth_z_span": data.get("water_depth_z_span"),
        "water_mesh_vertex_count": data.get("water_mesh_vertex_count"),
        "water_mesh_face_count": data.get("water_mesh_face_count"),
        "phase_field_cells": data.get("phase_field_cells"),
        "phase_field_liquid_volume": data.get("phase_field_liquid_volume"),
        "primary_liquid_count": data.get("primary_liquid_count"),
        "primary_gas_count": data.get("primary_gas_count"),
        "secondary_counts": data.get("secondary_counts"),
    }


def output_targets(out_dir, frame_index, root, output_format):
    name = f"frame_{frame_index:04d}"
    return {
        "renderer_candidate": {
            "repo_path": posix_rel(os.path.join(out_dir, "renderer_frames", f"{name}.{output_format}"), root),
            "format": output_format,
            "semantics": "future renderer/cache output from scene plus signed response AOV layers",
        },
        "metadata": {
            "repo_path": posix_rel(os.path.join(out_dir, "renderer_metadata", f"{name}_metadata.json"), root),
            "format": "json",
        },
        "validation": {
            "repo_path": posix_rel(os.path.join(out_dir, "renderer_validation", f"{name}_validation.json"), root),
            "format": "json",
        },
    }


def build_descriptor(frame, index, root, out_dir, output_format):
    frame_id = int(frame.get("frame") or index)
    descriptor_path = os.path.join(out_dir, "descriptors", f"frame_{index:04d}_scene_aov_job.json")
    scene_assets = {}
    issues = []
    assets = (frame.get("scene") or {}).get("assets") or {}
    for key in SCENE_ASSET_KEYS:
        ref, ref_issues = file_status(assets.get(key), root, f"scene:{key}", required=True, verify_hash=False)
        scene_assets[key] = ref
        issues.extend(ref_issues)

    aov_layers = {}
    for key in AOV_KEYS:
        ref, ref_issues = file_status(
            ((frame.get("response_aov_contract") or {}).get("references") or {}).get(key),
            root,
            f"aov:{key}",
            required=True,
            verify_hash=True,
        )
        aov_layers[key] = ref
        issues.extend(ref_issues)

    imported = frame.get("response_aov_import") or {}
    imported_refs = {}
    for key, role, required in (
        ("composite_repo_path", "imported:selected_composite", True),
        ("strip_repo_path", "imported:strip", False),
    ):
        ref, ref_issues = file_status({"repo_path": imported.get(key)}, root, role, required=required, verify_hash=False)
        imported_refs[role.split(":", 1)[1]] = ref
        issues.extend(ref_issues)

    descriptor = {
        "schema": DESCRIPTOR_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "job_index": index,
        "frame": frame_id,
        "output_frame": frame.get("output_frame"),
        "source_frame": frame.get("source_frame"),
        "scene_frame": frame.get("scene_frame"),
        "scene_time": frame.get("scene_time"),
        "stage": STAGE,
        "inputs": {
            "scene_assets": scene_assets,
            "aov_layers": aov_layers,
            "imported_composite": imported_refs.get("selected_composite"),
            "imported_strip": imported_refs.get("strip"),
        },
        "render_data": compact_render_data(frame),
        "response": {
            "scale": frame.get("response_scale"),
            "contract_stats": (frame.get("response_aov_contract") or {}).get("stats") or {},
            "import_validation": {
                "max_import_abs_diff": imported.get("max_import_abs_diff"),
                "mean_import_abs_diff": imported.get("mean_import_abs_diff"),
                "mismatched_coverage": imported.get("mismatched_coverage"),
            },
        },
        "visual_gate": frame.get("visual_gate") or {},
        "outputs": output_targets(out_dir, index, root, output_format),
        "validation_expectations": {
            "aov_import_max_abs_diff": 0,
            "aov_import_max_mean_abs_diff": 0.0,
            "selected_composite_source": "response_aov_contract:selected_composite_rgb",
            "renderer_gate_sources": ["s577_gap_summary", "s585_gap_summary"],
        },
    }
    write_json(descriptor_path, descriptor)
    descriptor_ref, descriptor_issues = file_status(
        {"repo_path": posix_rel(descriptor_path, root)},
        root,
        "descriptor",
        required=True,
        verify_hash=True,
    )
    issues.extend(descriptor_issues)
    descriptor_ref["schema"] = DESCRIPTOR_SCHEMA
    return {
        "job_index": index,
        "frame": frame_id,
        "output_frame": frame.get("output_frame"),
        "source_frame": frame.get("source_frame"),
        "scene_frame": frame.get("scene_frame"),
        "scene_time": frame.get("scene_time"),
        "descriptor": descriptor_ref,
        "response_scale": frame.get("response_scale"),
        "max_import_abs_diff": imported.get("max_import_abs_diff"),
        "mean_import_abs_diff": imported.get("mean_import_abs_diff"),
        "scene_assets_present": sum(1 for item in scene_assets.values() if item.get("status") == "present"),
        "aov_layers_present": sum(1 for item in aov_layers.values() if item.get("status") == "present"),
        "visual_gate": frame.get("visual_gate") or {},
        "issues": issues,
    }


def html_page(summary):
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Descriptors", checks.get("descriptors")),
            ("Missing", checks.get("missing_inputs")),
            ("SHA Mismatch", checks.get("sha_mismatches")),
            ("Import Max", checks.get("max_import_abs_diff")),
            ("Scene Frames", checks.get("unique_scene_frames")),
            ("Scale", checks.get("response_scale")),
        )
    )
    rows = []
    for frame in summary.get("frames") or []:
        rows.append(
            "<tr>"
            f"<td>{frame.get('job_index')}</td>"
            f"<td>{frame.get('frame')}</td>"
            f"<td>{frame.get('scene_frame')}</td>"
            f"<td>{frame.get('source_frame')}</td>"
            f"<td>{frame.get('aov_layers_present')}</td>"
            f"<td>{frame.get('scene_assets_present')}</td>"
            f"<td>{frame.get('max_import_abs_diff')}</td>"
            f"<td><code>{(frame.get('descriptor') or {}).get('repo_path')}</code></td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --line: #31424c; --ink: #eef8fb; --muted: #9fb1bc; --accent: #8fe1ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1500px; margin: 0 auto; padding: 24px 18px 42px; }}
    h1 {{ margin: 0 0 16px; font-size: 26px; font-weight: 670; letter-spacing: 0; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 8px; margin-bottom: 18px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; min-height: 58px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    strong {{ display: block; font-size: 15px; word-break: break-word; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 7px 8px; border-bottom: 1px solid var(--line); text-align: left; font-size: 12px; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 620; }}
    code {{ color: var(--accent); overflow-wrap: anywhere; }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <section class="tiles">{tiles}</section>
  <table>
    <thead><tr><th>Job</th><th>Frame</th><th>Scene</th><th>Source</th><th>AOV</th><th>Scene Assets</th><th>Import Max</th><th>Descriptor</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Manifest JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Input",
        "",
        f"- Response AOV scene handoff: `{summary['source']['repo_path']}`",
        f"- Source status: `{summary['source']['source_status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Descriptors: `{checks.get('descriptors')}`",
        f"- Missing inputs: `{checks.get('missing_inputs')}`",
        f"- SHA mismatches: `{checks.get('sha_mismatches')}`",
        f"- Size mismatches: `{checks.get('size_mismatches')}`",
        f"- Max import abs diff: `{checks.get('max_import_abs_diff')}`",
        f"- Max import mean abs diff: `{checks.get('max_import_mean_abs_diff')}`",
        f"- Unique scene frames: `{checks.get('unique_scene_frames')}`",
        f"- Scene frame count mismatch: `{checks.get('scene_frame_count_mismatch')}`",
        f"- Response scale: `{checks.get('response_scale')}`",
        f"- Scene asset refs: `{checks.get('scene_asset_refs_present')}` / `{checks.get('scene_asset_refs_total')}`",
        f"- AOV refs: `{checks.get('aov_refs_present')}` / `{checks.get('aov_refs_total')}`",
        "",
        "## Frame Samples",
        "",
        "| Job | Frame | Scene | Source | AOV | Scene Assets | Import Max | Descriptor |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('scene_frame')} | "
            f"{frame.get('source_frame')} | {frame.get('aov_layers_present')} | "
            f"{frame.get('scene_assets_present')} | {frame.get('max_import_abs_diff')} | "
            f"`{(frame.get('descriptor') or {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    handoff_path, handoff = load_handoff(args.handoff_summary, root)
    out_dir = os.path.abspath(args.out_dir)
    ensure_dir(out_dir)
    for subdir in ("descriptors", "renderer_frames", "renderer_metadata", "renderer_validation", "gallery"):
        ensure_dir(os.path.join(out_dir, subdir))

    source_ref, source_issues = file_status(
        {"repo_path": posix_rel(handoff_path, root), "sha256": sha256_file(handoff_path), "size": os.path.getsize(handoff_path)},
        root,
        "response_aov_scene_handoff",
        required=True,
        verify_hash=True,
    )
    source_ref.update({
        "schema": handoff.get("schema"),
        "source_status": handoff.get("status"),
    })

    source_refs = {}
    source_issues_all = list(source_issues)
    for label, source in (handoff.get("sources") or {}).items():
        ref, ref_issues = source_status(source, root, label)
        source_refs[label] = ref
        source_issues_all.extend(ref_issues)

    frame_jobs = [
        build_descriptor(frame, index, root, out_dir, args.output_format)
        for index, frame in enumerate(handoff.get("frames") or [])
    ]
    frame_issues = [issue for frame in frame_jobs for issue in frame.get("issues") or []]
    all_issues = source_issues_all + frame_issues
    missing = [issue for issue in all_issues if issue.get("reason") == "missing"]
    sha_mismatches = [issue for issue in all_issues if issue.get("reason") == "sha256_mismatch"]
    size_mismatches = [issue for issue in all_issues if issue.get("reason") == "size_mismatch"]
    source_checks = handoff.get("checks") or {}
    max_import_abs = max((int(frame.get("max_import_abs_diff") or 0) for frame in frame_jobs), default=999)
    max_import_mean = max((safe_float(frame.get("mean_import_abs_diff")) for frame in frame_jobs), default=999.0)
    scene_asset_total = len(frame_jobs) * len(SCENE_ASSET_KEYS)
    aov_total = len(frame_jobs) * len(AOV_KEYS)
    checks = {
        "frames": len(frame_jobs),
        "descriptors": len(frame_jobs),
        "missing_inputs": len(missing),
        "sha_mismatches": len(sha_mismatches),
        "size_mismatches": len(size_mismatches),
        "max_import_abs_diff": max_import_abs,
        "max_import_mean_abs_diff": max_import_mean,
        "source_handoff_missing_references": source_checks.get("missing_references"),
        "source_handoff_status": handoff.get("status"),
        "response_scale": source_checks.get("response_scale"),
        "unique_scene_frames": source_checks.get("unique_scene_frames"),
        "scene_frame_count_mismatch": source_checks.get("scene_frame_count_mismatch"),
        "s577_mean_gap_mad": source_checks.get("s577_mean_gap_mad"),
        "s577_max_gap_mad": source_checks.get("s577_max_gap_mad"),
        "s577_max_gap_abs": source_checks.get("s577_max_gap_abs"),
        "s585_mean_gap_mad": source_checks.get("s585_mean_gap_mad"),
        "s585_max_gap_mad": source_checks.get("s585_max_gap_mad"),
        "s585_max_gap_abs": source_checks.get("s585_max_gap_abs"),
        "scene_asset_refs_present": sum(frame.get("scene_assets_present") or 0 for frame in frame_jobs),
        "scene_asset_refs_total": scene_asset_total,
        "aov_refs_present": sum(frame.get("aov_layers_present") or 0 for frame in frame_jobs),
        "aov_refs_total": aov_total,
    }
    status = "ready" if (
        checks["frames"] > 0
        and checks["missing_inputs"] == 0
        and checks["sha_mismatches"] == 0
        and checks["size_mismatches"] == 0
        and checks["max_import_abs_diff"] == 0
        and checks["max_import_mean_abs_diff"] == 0.0
        and checks["source_handoff_missing_references"] == 0
        and checks["source_handoff_status"] == "ready"
        and checks["scene_asset_refs_present"] == checks["scene_asset_refs_total"]
        and checks["aov_refs_present"] == checks["aov_refs_total"]
    ) else "review"

    manifest_path = os.path.abspath(args.manifest) if args.manifest else os.path.join(out_dir, "response_aov_scene_job_manifest.json")
    gallery_dir = os.path.join(out_dir, "gallery")
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": JOB_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "stage": STAGE,
        "source": source_ref,
        "sources": source_refs,
        "checks": checks,
        "issues": all_issues,
        "frames": frame_jobs,
        "output_contract": {
            "output_format": args.output_format,
            "renderer_frame_root": posix_rel(os.path.join(out_dir, "renderer_frames"), root),
            "metadata_root": posix_rel(os.path.join(out_dir, "renderer_metadata"), root),
            "validation_root": posix_rel(os.path.join(out_dir, "renderer_validation"), root),
            "descriptor_root": posix_rel(os.path.join(out_dir, "descriptors"), root),
        },
        "runner_contract": {
            "input_schema": HANDOFF_SCHEMA,
            "frame_descriptor_schema": DESCRIPTOR_SCHEMA,
            "stage": STAGE,
            "expression": "renderer consumes scene assets plus base_rgb + response_positive_rgb - response_negative_rgb",
            "required_scene_assets": list(SCENE_ASSET_KEYS),
            "required_aov_layers": list(AOV_KEYS),
        },
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
        },
        "next": args.next,
    }
    write_json(manifest_path, summary)
    write_text(gallery_index, html_page(summary))
    summary["gallery"]["index_sha256"] = sha256_file(gallery_index)
    summary["gallery"]["index_size"] = os.path.getsize(gallery_index)
    write_json(manifest_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, manifest_path, root))
    print(
        "status={status} frames={frames} descriptors={descriptors} missing={missing} "
        "sha_mismatches={sha} out={out}".format(
            status=status,
            frames=checks["frames"],
            descriptors=checks["descriptors"],
            missing=checks["missing_inputs"],
            sha=checks["sha_mismatches"],
            out=manifest_path,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff_summary", help="S620 response-AOV scene handoff summary JSON")
    parser.add_argument("out_dir", help="Output directory for the renderer/cache job manifest")
    parser.add_argument("--manifest", help="Output manifest JSON path")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Job Manifest")
    parser.add_argument("--output-format", default="png")
    parser.add_argument(
        "--next",
        default="Use these frame descriptors as the next renderer/cache execution input.",
    )
    args = parser.parse_args()
    build(args)


if __name__ == "__main__":
    main()
