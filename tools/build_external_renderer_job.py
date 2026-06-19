#!/usr/bin/env python
"""Build an external-renderer job manifest from an LSFS bridge bundle."""

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


REQUIRED_ASSETS = ("camera", "particles", "phase_cells", "water_mesh")


def optional_file(path, label):
    if not path:
        return None
    return require_file(path, label)


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def asset_path(asset):
    path = (asset or {}).get("path") or (asset or {}).get("repo_path")
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def asset_contract(asset, root, role, encoding, fields=None):
    path = asset_path(asset)
    present = bool(path and os.path.isfile(path))
    entry = {
        "role": role,
        "encoding": encoding,
        "status": "present" if present else "missing",
        "path": path,
        "repo_path": posix_rel(path, root) if path else None,
        "size": os.path.getsize(path) if present else 0,
    }
    if fields:
        entry["fields"] = fields
    return entry


def summarize_camera(camera_asset):
    path = asset_path(camera_asset)
    if not path or not os.path.isfile(path):
        return {"status": "missing", "path": path}
    payload = read_json(path)
    camera = payload.get("camera", {})
    header = payload.get("header", {})
    metadata = payload.get("cinematic_metadata", {})
    water = payload.get("water_volume", {})
    secondary = payload.get("secondary_channels", {})
    return {
        "status": "ok",
        "position": camera.get("position"),
        "target": camera.get("target"),
        "up": camera.get("up"),
        "fov_degrees": camera.get("fov_degrees"),
        "vertical_fov_degrees": camera.get("vertical_fov_degrees"),
        "focal_length_mm": camera.get("focal_length_mm"),
        "near_clip": camera.get("near_clip"),
        "far_clip": camera.get("far_clip"),
        "time": header.get("time"),
        "shutter_open": header.get("shutter_open", metadata.get("shutter_open")),
        "shutter_close": header.get("shutter_close", metadata.get("shutter_close")),
        "world_units": header.get("world_units", metadata.get("world_units")),
        "dims": header.get("dims"),
        "dx": header.get("dx"),
        "phase": header.get("phase", {}),
        "water_bounds_min": metadata.get("water_bounds_min"),
        "water_bounds_max": metadata.get("water_bounds_max"),
        "secondary_bounds_min": metadata.get("secondary_bounds_min"),
        "secondary_bounds_max": metadata.get("secondary_bounds_max"),
        "water_volume": {
            "phase_field_cells": water.get("phase_field_cells"),
            "phase_field_liquid_volume": water.get("phase_field_liquid_volume"),
            "primary_liquid_count": water.get("primary_liquid_count"),
            "primary_gas_count": water.get("primary_gas_count"),
            "secondary_particle_count": water.get("secondary_particle_count"),
        },
        "secondary_channels": {
            "total": secondary.get("total_count"),
            "droplet": secondary.get("droplet_count"),
            "spray": secondary.get("spray_count"),
            "foam": secondary.get("foam_count"),
            "bubble": secondary.get("bubble_count"),
        },
    }


def compact_bridge_look(summary):
    if not summary:
        return {}
    keys = (
        "engine",
        "camera_motion",
        "camera_framing",
        "camera_path_metrics",
        "water_material",
        "water_volume_scattering_pass",
        "water_volume_occlusion_pass",
        "water_surface_detail",
        "water_surface_glint_pass",
        "water_reflection_pass",
        "water_mesh_quality_material_pass",
        "secondary_direct_pass",
        "secondary_soft_pass",
        "secondary_streak_pass",
        "secondary_channel_radius_scales",
        "visual_qa",
    )
    return {key: summary[key] for key in keys if key in summary}


def related_json(path, label, root):
    if not path:
        return None
    payload = read_json(path)
    return {
        "label": label,
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "sha256": sha256_file(path),
    }


def build_job(args):
    root = os.getcwd()
    bundle_path = require_file(args.bundle, "external render bundle")
    bundle = read_json(bundle_path)
    if bundle.get("schema") != "lsfs_bridge_external_render_bundle":
        raise SystemExit(f"unsupported bundle schema: {bundle.get('schema')}")

    bridge_summary_path = optional_file(args.bridge_summary, "bridge summary")
    bridge_summary = read_json(bridge_summary_path) if bridge_summary_path else {}
    review_package_path = optional_file(args.review_package, "review package")
    accepted_publish_path = optional_file(args.accepted_publish, "accepted publish manifest")
    benchmark_summary_path = optional_file(args.benchmark_summary, "benchmark summary")

    width = args.width or as_int(bridge_summary.get("width"), 1920)
    height = args.height or as_int(bridge_summary.get("height"), 1080)
    samples = args.samples or as_int(bridge_summary.get("samples"), 64)
    totals = {
        "camera_bytes": 0,
        "particle_csv_bytes": 0,
        "phase_cell_csv_bytes": 0,
        "water_mesh_bytes": 0,
    }
    frames = []
    missing_assets = []
    camera_failures = []
    sequence_frames = []
    min_water_mesh_faces = None
    quality_labels = {}

    for frame in bundle.get("frames", []):
        assets = frame.get("assets") or {}
        contracts = {
            "camera": asset_contract(assets.get("camera"), root, "camera", "json_camera"),
            "particles": asset_contract(
                assets.get("particles"),
                root,
                "particle_stream",
                "csv",
                ["kind", "render_channel", "index", "phase", "x", "y", "z", "vx", "vy", "vz", "volume", "age"],
            ),
            "phase_cells": asset_contract(
                assets.get("phase_cells"),
                root,
                "phase_field_cells",
                "csv",
                ["i", "j", "k", "level", "marker", "phi", "liquid_volume"],
            ),
            "water_mesh": asset_contract(assets.get("water_mesh"), root, "water_surface_mesh", "obj"),
        }
        for key, contract in contracts.items():
            if contract["status"] != "present":
                missing_assets.append({
                    "output_frame": frame.get("output_frame"),
                    "asset": key,
                    "path": contract.get("path"),
                })
        totals["camera_bytes"] += contracts["camera"]["size"]
        totals["particle_csv_bytes"] += contracts["particles"]["size"]
        totals["phase_cell_csv_bytes"] += contracts["phase_cells"]["size"]
        totals["water_mesh_bytes"] += contracts["water_mesh"]["size"]

        camera = summarize_camera(assets.get("camera"))
        if camera.get("status") != "ok":
            camera_failures.append({
                "output_frame": frame.get("output_frame"),
                "path": camera.get("path"),
                "status": camera.get("status"),
            })

        sequence_frames.append(frame.get("sequence_frame"))
        faces = frame.get("water_mesh_face_count")
        if isinstance(faces, int):
            min_water_mesh_faces = faces if min_water_mesh_faces is None else min(min_water_mesh_faces, faces)
        quality = (frame.get("water_mesh_surface_quality") or {}).get("label", "unknown")
        quality_labels[quality] = quality_labels.get(quality, 0) + 1

        frames.append({
            "output_frame": frame.get("output_frame"),
            "sequence_frame": frame.get("sequence_frame"),
            "time": frame.get("time"),
            "particle_count": frame.get("particle_count"),
            "phase_cell_count": frame.get("phase_cell_count"),
            "water_mesh_face_count": frame.get("water_mesh_face_count"),
            "water_mesh_vertex_count": frame.get("water_mesh_vertex_count"),
            "water_mesh_surface_quality": frame.get("water_mesh_surface_quality", {}),
            "secondary_counts": (frame.get("render_data") or {}).get("secondary_counts", {}),
            "render_data": frame.get("render_data", {}),
            "camera": camera,
            "assets": contracts,
        })

    sequence_monotonic = all(
        sequence_frames[i] is None
        or sequence_frames[i + 1] is None
        or sequence_frames[i] <= sequence_frames[i + 1]
        for i in range(max(0, len(sequence_frames) - 1))
    )
    gates = {
        "missing_assets": len(missing_assets),
        "camera_failures": len(camera_failures),
        "sequence_monotonic": sequence_monotonic,
        "min_water_mesh_faces": min_water_mesh_faces,
        "min_water_mesh_faces_required": args.min_water_mesh_faces,
        "quality_labels": quality_labels,
    }
    failed = (
        gates["missing_assets"] > 0
        or gates["camera_failures"] > 0
        or not sequence_monotonic
        or (min_water_mesh_faces or 0) < args.min_water_mesh_faces
    )

    related = []
    for path, label in (
        (bridge_summary_path, "bridge_summary"),
        (review_package_path, "review_package"),
        (accepted_publish_path, "accepted_publish"),
        (benchmark_summary_path, "external_bundle_benchmark"),
    ):
        item = related_json(path, label, root)
        if item:
            related.append(item)

    accepted_publish = read_json(accepted_publish_path) if accepted_publish_path else {}
    benchmark = read_json(benchmark_summary_path) if benchmark_summary_path else {}
    return {
        "schema": "lsfs_external_renderer_job",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed" if failed else "ready",
        "title": args.title,
        "target_renderer": args.target_renderer,
        "bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "schema": bundle.get("schema"),
            "version": bundle.get("version"),
            "sha256": sha256_file(bundle_path),
            "accepted_preset": bundle.get("accepted_preset"),
            "frame_count": bundle.get("frame_count"),
            "source_window": bundle.get("source_window", {}),
            "asset_hash_mode": bundle.get("asset_hash_mode"),
        },
        "render_settings": {
            "width": width,
            "height": height,
            "fps": args.fps,
            "samples": samples,
            "output_format": args.output_format,
            "frame_naming": "frame_%04d",
            "world_units": "cell",
            "coordinate_note": "Input assets use LSFS cell-space coordinates; renderer adapters may convert axes.",
        },
        "channel_contract": {
            "camera": {
                "asset": "camera",
                "encoding": "json_camera",
                "required": True,
                "semantics": "Per-frame camera, shutter, bounds, and metadata summary.",
            },
            "water_surface": {
                "asset": "water_mesh",
                "encoding": "obj",
                "required": True,
                "semantics": "Primary liquid surface mesh for path tracing or Blender import.",
            },
            "phase_volume": {
                "asset": "phase_cells",
                "encoding": "csv",
                "required": True,
                "semantics": "Sparse phase-field cells for volumetric fill, masks, and diagnostics.",
            },
            "particle_stream": {
                "asset": "particles",
                "encoding": "csv",
                "required": True,
                "semantics": "Primary gas/liquid particles plus secondary spray, foam, droplet, and bubble channels.",
            },
        },
        "look_reference": compact_bridge_look(bridge_summary),
        "review": {
            "accepted_publish_status": accepted_publish.get("status"),
            "accepted_public_url": accepted_publish.get("public_url"),
            "benchmark_status": benchmark.get("status"),
            "benchmark_preview": (benchmark.get("preview") or {}) if benchmark else {},
        },
        "related_artifacts": related,
        "input_footprint": {
            **totals,
            "total_bytes": sum(totals.values()),
        },
        "quality_gates": gates,
        "missing_assets": missing_assets,
        "camera_failures": camera_failures,
        "frames": frames,
        "next": args.next,
    }


def markdown_report(job, out_path, root):
    settings = job.get("render_settings", {})
    footprint = job.get("input_footprint", {})
    gates = job.get("quality_gates", {})
    lines = [
        f"# {job['title']}",
        "",
        f"Generated UTC: `{job['generated_utc']}`",
        f"Job JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{job['status']}`",
        f"Target renderer: `{job['target_renderer']}`",
        "",
        "## Bundle",
        "",
        f"- Bundle: `{job['bundle']['repo_path']}`",
        f"- Accepted preset: `{job['bundle'].get('accepted_preset')}`",
        f"- Frames: `{job['bundle'].get('frame_count')}`",
        f"- Source window: `{job['bundle'].get('source_window', {}).get('start_index')}..{job['bundle'].get('source_window', {}).get('end_index')}`",
        "",
        "## Render Settings",
        "",
        f"- Resolution: `{settings.get('width')} x {settings.get('height')}`",
        f"- FPS: `{settings.get('fps')}`",
        f"- Samples: `{settings.get('samples')}`",
        f"- Output format: `{settings.get('output_format')}`",
        "",
        "## Channel Contract",
        "",
    ]
    for name, channel in job.get("channel_contract", {}).items():
        lines.append(
            f"- `{name}`: `{channel.get('encoding')}` from `{channel.get('asset')}`; {channel.get('semantics')}"
        )
    lines.extend([
        "",
        "## Input Footprint",
        "",
        f"- Camera JSON: `{format_bytes(footprint.get('camera_bytes', 0))}`",
        f"- Particle CSV: `{format_bytes(footprint.get('particle_csv_bytes', 0))}`",
        f"- Phase-cell CSV: `{format_bytes(footprint.get('phase_cell_csv_bytes', 0))}`",
        f"- Water mesh OBJ: `{format_bytes(footprint.get('water_mesh_bytes', 0))}`",
        f"- Total: `{format_bytes(footprint.get('total_bytes', 0))}`",
        "",
        "## Gates",
        "",
        f"- Missing assets: `{gates.get('missing_assets')}`",
        f"- Camera failures: `{gates.get('camera_failures')}`",
        f"- Sequence monotonic: `{gates.get('sequence_monotonic')}`",
        f"- Minimum water mesh faces: `{gates.get('min_water_mesh_faces')}`",
        f"- Quality labels: `{gates.get('quality_labels')}`",
        "",
        "## Review Links",
        "",
        f"- Accepted public URL: `{job.get('review', {}).get('accepted_public_url') or 'n/a'}`",
        f"- Benchmark status: `{job.get('review', {}).get('benchmark_status') or 'n/a'}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Sequence | Time | Particles | Phase Cells | Water Faces | Camera FOV | Secondary Total |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    frames = job.get("frames", [])
    indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in indices:
        frame = frames[index]
        camera = frame.get("camera", {})
        secondary = frame.get("secondary_counts", {})
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('sequence_frame')} | {frame.get('time')} | "
            f"{frame.get('particle_count')} | {frame.get('phase_cell_count')} | "
            f"{frame.get('water_mesh_face_count')} | {camera.get('vertical_fov_degrees')} | "
            f"{secondary.get('total')} |"
        )
    lines.extend([
        "",
        "## Related Artifacts",
        "",
    ])
    for item in job.get("related_artifacts", []):
        lines.append(f"- `{item['label']}`: `{item['repo_path']}`")
    lines.extend([
        "",
        "## Next",
        "",
        job.get("next", "Use this job manifest as the renderer handoff contract."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build an external renderer job manifest")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="External Renderer Job")
    parser.add_argument("--target-renderer", default="external_path_tracer")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=float, default=8.0)
    parser.add_argument("--samples", type=int)
    parser.add_argument("--output-format", default="png")
    parser.add_argument("--bridge-summary")
    parser.add_argument("--review-package")
    parser.add_argument("--accepted-publish")
    parser.add_argument("--benchmark-summary")
    parser.add_argument("--min-water-mesh-faces", type=int, default=1000)
    parser.add_argument(
        "--next",
        default="Use this job manifest as the renderer handoff contract before writing a renderer-specific adapter.",
    )
    args = parser.parse_args(argv)
    if args.width is not None and args.width <= 0:
        parser.error("width must be positive")
    if args.height is not None and args.height <= 0:
        parser.error("height must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.samples is not None and args.samples <= 0:
        parser.error("samples must be positive")

    job = build_job(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, job)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(job, out_path, os.getcwd()))
    print(
        f"status={job['status']} frames={len(job['frames'])} "
        f"missing_assets={job['quality_gates']['missing_assets']} "
        f"camera_failures={job['quality_gates']['camera_failures']} job={out_path}"
    )
    print(f"report={report_path}")
    if job["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
