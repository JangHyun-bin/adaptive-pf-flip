#!/usr/bin/env python
"""Validate an external-render bundle before larger-shot or benchmark work."""

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from build_bridge_review_package import format_bytes, posix_rel, read_json, require_file, write_json, write_text


def add_check(checks, name, passed, detail, expected=None, actual=None):
    checks.append({
        "name": name,
        "status": "passed" if passed else "failed",
        "detail": detail,
        "expected": expected,
        "actual": actual,
    })


def asset_path(asset):
    path = asset.get("path") or asset.get("repo_path")
    if not path:
        return None
    return os.path.abspath(path) if os.path.isabs(path) else os.path.abspath(path.replace("/", os.sep))


def collect_asset_metrics(bundle):
    missing = []
    present_count = 0
    totals = {
        "camera_bytes": 0,
        "particle_csv_bytes": 0,
        "phase_cell_csv_bytes": 0,
        "water_mesh_bytes": 0,
    }
    min_particle_count = None
    max_particle_count = None
    min_phase_cell_count = None
    min_water_mesh_face_count = None
    quality_labels = {}
    sequence_frames = []
    for frame in bundle.get("frames", []):
        particle_count = frame.get("particle_count")
        phase_cell_count = frame.get("phase_cell_count")
        water_faces = frame.get("water_mesh_face_count")
        if isinstance(particle_count, int):
            min_particle_count = particle_count if min_particle_count is None else min(min_particle_count, particle_count)
            max_particle_count = particle_count if max_particle_count is None else max(max_particle_count, particle_count)
        if isinstance(phase_cell_count, int):
            min_phase_cell_count = phase_cell_count if min_phase_cell_count is None else min(min_phase_cell_count, phase_cell_count)
        if isinstance(water_faces, int):
            min_water_mesh_face_count = water_faces if min_water_mesh_face_count is None else min(min_water_mesh_face_count, water_faces)
        label = (frame.get("water_mesh_surface_quality") or {}).get("label", "unknown")
        quality_labels[label] = quality_labels.get(label, 0) + 1
        sequence_frames.append(frame.get("sequence_frame"))
        for key, total_key in (
            ("camera", "camera_bytes"),
            ("particles", "particle_csv_bytes"),
            ("phase_cells", "phase_cell_csv_bytes"),
            ("water_mesh", "water_mesh_bytes"),
        ):
            asset = (frame.get("assets") or {}).get(key) or {}
            path = asset_path(asset)
            if not path or not os.path.isfile(path):
                missing.append({
                    "output_frame": frame.get("output_frame"),
                    "asset": key,
                    "path": path,
                })
                continue
            present_count += 1
            totals[total_key] += os.path.getsize(path)
    return {
        "missing_assets": missing,
        "present_asset_count": present_count,
        "totals": totals,
        "min_particle_count": min_particle_count,
        "max_particle_count": max_particle_count,
        "min_phase_cell_count": min_phase_cell_count,
        "min_water_mesh_face_count": min_water_mesh_face_count,
        "quality_labels": quality_labels,
        "sequence_frames": sequence_frames,
        "sequence_monotonic": all(
            sequence_frames[i] is None
            or sequence_frames[i + 1] is None
            or sequence_frames[i] <= sequence_frames[i + 1]
            for i in range(max(0, len(sequence_frames) - 1))
        ),
    }


def preview_metrics(path):
    if not path:
        return None
    summary_path = require_file(path, "preview render summary")
    summary = read_json(summary_path)
    frames = summary.get("frames", [])
    secondary_pixels = [
        frame.get("secondary_pixels", 0)
        for frame in frames
        if isinstance(frame.get("secondary_pixels"), int)
    ]
    return {
        "path": summary_path,
        "repo_path": posix_rel(summary_path, os.getcwd()),
        "renderer": summary.get("renderer"),
        "frame_count": summary.get("frame_count"),
        "width": summary.get("width"),
        "height": summary.get("height"),
        "min_occupancy": summary.get("min_occupancy"),
        "secondary_channel": summary.get("secondary_channel"),
        "min_secondary_pixels": min(secondary_pixels) if secondary_pixels else None,
        "max_secondary_pixels": max(secondary_pixels) if secondary_pixels else None,
    }


def publish_metrics(path):
    if not path:
        return None
    manifest_path = require_file(path, "publish manifest")
    manifest = read_json(manifest_path)
    return {
        "path": manifest_path,
        "repo_path": posix_rel(manifest_path, os.getcwd()),
        "status": manifest.get("status"),
        "local_url": manifest.get("local_url"),
        "public_url": manifest.get("public_url"),
        "processes": manifest.get("processes", {}),
        "checks": manifest.get("checks", []),
    }


def check_url(checks, name, url, method, timeout):
    request = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.getcode())
            length = response.headers.get("Content-Length")
    except urllib.error.HTTPError as exc:
        add_check(checks, name, False, f"HTTP {exc.code}", expected="2xx", actual=exc.code)
        return
    except Exception as exc:
        add_check(checks, name, False, str(exc), expected="2xx", actual=str(exc))
        return
    detail = f"HTTP {status}"
    if length:
        detail += f", {length} bytes"
    add_check(checks, name, 200 <= status < 300, detail, expected="2xx", actual=status)


def projected_bytes(total_bytes, current_frames, target_frames):
    if current_frames <= 0:
        return None
    return int(round(total_bytes * target_frames / current_frames))


def build_gate(args):
    root = os.getcwd()
    bundle_path = require_file(args.bundle, "external render bundle")
    bundle = read_json(bundle_path)
    checks = []
    add_check(
        checks,
        "bundle_schema",
        bundle.get("schema") == "lsfs_bridge_external_render_bundle",
        "bundle schema",
        expected="lsfs_bridge_external_render_bundle",
        actual=bundle.get("schema"),
    )
    frame_count = int(bundle.get("frame_count") or 0)
    add_check(checks, "bundle_frame_count", frame_count >= args.min_frames, "minimum bundle frame count", args.min_frames, frame_count)
    asset_metrics = collect_asset_metrics(bundle)
    missing_count = len(asset_metrics["missing_assets"])
    add_check(checks, "bundle_missing_assets", missing_count <= args.max_missing_assets, "missing asset count", args.max_missing_assets, missing_count)
    add_check(checks, "bundle_sequence_monotonic", bool(asset_metrics["sequence_monotonic"]), "sequence frame order is monotonic", True, asset_metrics["sequence_monotonic"])
    add_check(
        checks,
        "bundle_water_mesh_faces",
        (asset_metrics["min_water_mesh_face_count"] or 0) >= args.min_water_mesh_faces,
        "minimum water mesh face count",
        args.min_water_mesh_faces,
        asset_metrics["min_water_mesh_face_count"],
    )

    preview = preview_metrics(args.preview_summary)
    if preview:
        add_check(checks, "preview_frame_count", int(preview.get("frame_count") or 0) >= args.min_preview_frames, "minimum preview frame count", args.min_preview_frames, preview.get("frame_count"))
        add_check(checks, "preview_occupancy", float(preview.get("min_occupancy") or 0.0) >= args.min_preview_occupancy, "minimum preview occupancy", args.min_preview_occupancy, preview.get("min_occupancy"))
        add_check(checks, "preview_resolution_width", int(preview.get("width") or 0) >= args.min_preview_width, "minimum preview width", args.min_preview_width, preview.get("width"))
        add_check(checks, "preview_resolution_height", int(preview.get("height") or 0) >= args.min_preview_height, "minimum preview height", args.min_preview_height, preview.get("height"))

    publish = publish_metrics(args.publish_manifest)
    if publish:
        add_check(checks, "publish_status", publish.get("status") == "running", "publish status", "running", publish.get("status"))
        failed_recorded = [check for check in publish.get("checks", []) if int(check.get("status", 0) or 0) < 200 or int(check.get("status", 0) or 0) >= 300]
        add_check(checks, "publish_recorded_checks", not failed_recorded, "recorded publish checks are 2xx", 0, len(failed_recorded))
        if args.check_public and publish.get("public_url"):
            base = publish["public_url"].rstrip("/")
            check_url(checks, "public_index_live", f"{base}/index.html", "GET", args.timeout_seconds)
            check_url(checks, "public_gif_live", f"{base}/assets/shot.gif", "HEAD", args.timeout_seconds)
    elif args.check_public:
        add_check(checks, "publish_manifest", False, "publish manifest required for public check")

    total_input_bytes = sum(asset_metrics["totals"].values())
    projections = {
        "current_frames": frame_count,
        "current_input_bytes": total_input_bytes,
        "target_frames": args.project_frames,
        "projected_input_bytes": projected_bytes(total_input_bytes, frame_count, args.project_frames),
        "target_preview_frames": args.project_preview_frames,
        "projected_preview_sample_bytes": projected_bytes(total_input_bytes, frame_count, args.project_preview_frames),
    }
    failed_count = sum(1 for check in checks if check["status"] == "failed")
    return {
        "schema": "lsfs_external_bundle_benchmark_gate",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed" if failed_count else "passed",
        "failed_count": failed_count,
        "check_count": len(checks),
        "checks": checks,
        "bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "frame_count": frame_count,
            "accepted_preset": bundle.get("accepted_preset"),
            "source_window": bundle.get("source_window", {}),
            "asset_hash_mode": bundle.get("asset_hash_mode"),
            "public_url": (bundle.get("public_review") or {}).get("public_url"),
        },
        "asset_metrics": asset_metrics,
        "preview": preview,
        "publish": publish,
        "projections": projections,
    }


def markdown_report(gate, out_path, root, next_text):
    totals = gate["asset_metrics"]["totals"]
    projections = gate["projections"]
    lines = [
        "# S279 External Bundle Benchmark Gate",
        "",
        f"Generated UTC: `{gate['generated_utc']}`",
        f"Gate JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{gate['status']}`",
        f"Checks: `{gate['check_count']}`",
        f"Failures: `{gate['failed_count']}`",
        "",
        "## Bundle",
        "",
        f"- Bundle: `{gate['bundle']['repo_path']}`",
        f"- Accepted preset: `{gate['bundle'].get('accepted_preset')}`",
        f"- Frames: `{gate['bundle'].get('frame_count')}`",
        f"- Source window: `{gate['bundle'].get('source_window', {}).get('start_index')}..{gate['bundle'].get('source_window', {}).get('end_index')}`",
        f"- Missing assets: `{len(gate['asset_metrics']['missing_assets'])}`",
        f"- Quality labels: `{gate['asset_metrics']['quality_labels']}`",
        "",
        "## Input Footprint",
        "",
        f"- Camera JSON: `{format_bytes(totals['camera_bytes'])}`",
        f"- Particle CSV: `{format_bytes(totals['particle_csv_bytes'])}`",
        f"- Phase-cell CSV: `{format_bytes(totals['phase_cell_csv_bytes'])}`",
        f"- Water mesh OBJ: `{format_bytes(totals['water_mesh_bytes'])}`",
        f"- Total current input: `{format_bytes(projections['current_input_bytes'])}`",
        f"- Projected {projections['target_frames']}-frame input: `{format_bytes(projections['projected_input_bytes'])}`",
        f"- Projected {projections['target_preview_frames']}-frame preview sample input: `{format_bytes(projections['projected_preview_sample_bytes'])}`",
        "",
        "## Preview",
        "",
    ]
    preview = gate.get("preview") or {}
    if preview:
        lines.extend([
            f"- Preview: `{preview.get('repo_path')}`",
            f"- Frames: `{preview.get('frame_count')}`",
            f"- Resolution: `{preview.get('width')} x {preview.get('height')}`",
            f"- Min occupancy: `{preview.get('min_occupancy')}`",
            f"- Secondary pixels: `{preview.get('min_secondary_pixels')}..{preview.get('max_secondary_pixels')}`",
        ])
    else:
        lines.append("- Preview: `not provided`")
    lines.extend([
        "",
        "## Publish",
        "",
    ])
    publish = gate.get("publish") or {}
    if publish:
        lines.extend([
            f"- Status: `{publish.get('status')}`",
            f"- Public URL: `{publish.get('public_url')}`",
        ])
    else:
        lines.append("- Publish: `not provided`")
    lines.extend([
        "",
        "## Checks",
        "",
        "| Check | Status | Expected | Actual | Detail |",
        "| --- | --- | --- | --- | --- |",
    ])
    for check in gate.get("checks", []):
        lines.append(
            f"| {check['name']} | `{check['status']}` | `{check.get('expected')}` | `{check.get('actual')}` | {check.get('detail', '')} |"
        )
    lines.extend([
        "",
        "## Next",
        "",
        next_text,
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate external bundle benchmark readiness")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--preview-summary")
    parser.add_argument("--publish-manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--min-frames", type=int, default=32)
    parser.add_argument("--max-missing-assets", type=int, default=0)
    parser.add_argument("--min-water-mesh-faces", type=int, default=1000)
    parser.add_argument("--min-preview-frames", type=int, default=16)
    parser.add_argument("--min-preview-occupancy", type=float, default=0.01)
    parser.add_argument("--min-preview-width", type=int, default=960)
    parser.add_argument("--min-preview-height", type=int, default=540)
    parser.add_argument("--project-frames", type=int, default=64)
    parser.add_argument("--project-preview-frames", type=int, default=24)
    parser.add_argument("--check-public", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--next", default="Use this gate before starting larger-shot or benchmark runs from the external bundle path.")
    args = parser.parse_args(argv)

    gate = build_gate(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, gate)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(gate, out_path, os.getcwd(), args.next))
    print(f"status={gate['status']} checks={gate['check_count']} failures={gate['failed_count']}")
    print(f"gate={out_path}")
    print(f"report={report_path}")
    if gate["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
