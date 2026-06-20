#!/usr/bin/env python
"""Export an lsfs_render_data_summary from a renderer scene-cache handoff."""

import argparse
import math
import os
from datetime import datetime, timezone

from build_bridge_review_package import posix_rel, read_json, require_file, write_json, write_text


def finite_number(value):
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def stat_summary(values):
    clean = [float(v) for v in values if finite_number(v)]
    if not clean:
        return {"count": 0, "min": None, "mean": None, "max": None}
    return {
        "count": len(clean),
        "min": min(clean),
        "mean": sum(clean) / float(len(clean)),
        "max": max(clean),
    }


def vec_min(a, b):
    if a is None:
        return list(b) if b is not None else None
    if b is None:
        return list(a)
    return [min(float(a[i]), float(b[i])) for i in range(min(len(a), len(b)))]


def vec_max(a, b):
    if a is None:
        return list(b) if b is not None else None
    if b is None:
        return list(a)
    return [max(float(a[i]), float(b[i])) for i in range(min(len(a), len(b)))]


def span(lo, hi, axis):
    if not isinstance(lo, list) or not isinstance(hi, list):
        return None
    if len(lo) <= axis or len(hi) <= axis:
        return None
    if not finite_number(lo[axis]) or not finite_number(hi[axis]):
        return None
    return float(hi[axis]) - float(lo[axis])


def build_summary(handoff_path):
    root = os.getcwd()
    resolved = require_file(handoff_path, "renderer scene-cache handoff")
    handoff = read_json(resolved)
    if handoff.get("schema") != "lsfs_mitsuba_renderer_scene_cache_handoff":
        raise SystemExit(f"{handoff_path}: expected lsfs_mitsuba_renderer_scene_cache_handoff schema")

    frames = []
    water_bounds_min = None
    water_bounds_max = None
    secondary_bounds_min = None
    secondary_bounds_max = None
    water_y_spans = []
    water_z_spans = []
    liquid_volumes = []
    phase_cells = []
    mesh_faces = []
    mesh_occupied = []
    secondary_totals = []
    source_frames = []
    output_frames = []

    for mapped in handoff.get("frames") or []:
        scene = mapped.get("scene") or {}
        counts = scene.get("counts") or {}
        cinematic = scene.get("cinematic") or {}
        assets = scene.get("assets") or {}
        wb_min = cinematic.get("water_bounds_min")
        wb_max = cinematic.get("water_bounds_max")
        sb_min = cinematic.get("secondary_bounds_min")
        sb_max = cinematic.get("secondary_bounds_max")
        y_span = span(wb_min, wb_max, 1)
        z_span = span(wb_min, wb_max, 2)
        water_bounds_min = vec_min(water_bounds_min, wb_min)
        water_bounds_max = vec_max(water_bounds_max, wb_max)
        secondary_bounds_min = vec_min(secondary_bounds_min, sb_min)
        secondary_bounds_max = vec_max(secondary_bounds_max, sb_max)
        water_y_spans.append(y_span)
        water_z_spans.append(z_span)
        liquid_volumes.append(counts.get("phase_field_liquid_volume"))
        phase_cells.append(counts.get("phase_field_cells", counts.get("phase_cell_count")))
        mesh_faces.append(counts.get("water_mesh_face_count"))
        mesh_occupied.append(counts.get("water_mesh_occupied_cell_count"))
        secondary_total = counts.get("secondary_particle_count")
        secondary_totals.append(secondary_total)
        source_frame = mapped.get("scene_frame")
        output_frame = mapped.get("output_frame")
        source_frames.append(source_frame)
        output_frames.append(output_frame)
        frames.append({
            "output_frame": output_frame,
            "source_frame": source_frame,
            "source_time": mapped.get("scene_time"),
            "source_cache": scene.get("source_cache"),
            "water_mesh": ((assets.get("water_mesh") or {}).get("path") or (assets.get("water_mesh") or {}).get("repo_path")),
            "water_mesh_face_count": counts.get("water_mesh_face_count"),
            "water_mesh_vertex_count": counts.get("water_mesh_vertex_count"),
            "occupied_cell_count": counts.get("water_mesh_occupied_cell_count"),
            "water_mesh_occupied_cell_count": counts.get("water_mesh_occupied_cell_count"),
            "water_bounds_min": wb_min,
            "water_bounds_max": wb_max,
            "water_depth_y_span": y_span,
            "water_depth_z_span": z_span,
            "secondary_bounds_min": sb_min,
            "secondary_bounds_max": sb_max,
            "primary_liquid_count": counts.get("primary_liquid_count"),
            "primary_gas_count": counts.get("primary_gas_count"),
            "phase_field_cells": counts.get("phase_field_cells", counts.get("phase_cell_count")),
            "phase_field_liquid_volume": counts.get("phase_field_liquid_volume"),
            "secondary_counts": {
                "droplet": counts.get("secondary_droplet_count"),
                "spray": counts.get("secondary_spray_count"),
                "foam": counts.get("secondary_foam_count"),
                "bubble": counts.get("secondary_bubble_count"),
                "total": secondary_total,
            },
            "visual_contract": {
                "frame": mapped.get("frame"),
                "mapping_mode": (handoff.get("checks") or {}).get("mapping_mode"),
                "consumer_composite": (((mapped.get("consumer") or {}).get("composite") or {}).get("repo_path")),
                "consumer_expected": (mapped.get("consumer") or {}).get("expected", {}),
                "texture_response": (mapped.get("consumer") or {}).get("response", {}),
            },
        })

    source_frame_numbers = [int(v) for v in source_frames if v is not None]
    output_frame_numbers = [int(v) for v in output_frames if v is not None]
    sanity_checks = [
        {
            "name": "render_frame_count_positive",
            "passed": len(frames) > 0,
            "value": len(frames),
        },
        {
            "name": "all_frames_have_water_bounds",
            "passed": all(frame.get("water_bounds_min") and frame.get("water_bounds_max") for frame in frames),
            "value": sum(1 for frame in frames if frame.get("water_bounds_min") and frame.get("water_bounds_max")),
        },
        {
            "name": "all_frames_have_mesh_faces",
            "passed": all((frame.get("water_mesh_face_count") or 0) > 0 for frame in frames),
            "value": sum(1 for frame in frames if (frame.get("water_mesh_face_count") or 0) > 0),
        },
        {
            "name": "all_frames_have_secondary_counts",
            "passed": all((frame.get("secondary_counts", {}).get("total") or 0) > 0 for frame in frames),
            "value": sum(1 for frame in frames if (frame.get("secondary_counts", {}).get("total") or 0) > 0),
        },
        {
            "name": "source_frames_are_monotonic",
            "passed": source_frame_numbers == sorted(source_frame_numbers),
            "value": source_frame_numbers[:3] + source_frame_numbers[-3:] if len(source_frame_numbers) >= 6 else source_frame_numbers,
        },
        {
            "name": "output_frames_are_monotonic",
            "passed": output_frame_numbers == sorted(output_frame_numbers),
            "value": output_frame_numbers[:3] + output_frame_numbers[-3:] if len(output_frame_numbers) >= 6 else output_frame_numbers,
        },
    ]
    scene_sequence = handoff.get("scene_sequence") or {}
    summary = {
        "schema": "lsfs_render_data_summary",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "shot_dir": (handoff.get("bundle_root") or {}).get("repo_path"),
        "inputs": {
            "renderer_scene_cache_handoff": posix_rel(resolved, root),
        },
        "simulation": {
            "sim_kind": scene_sequence.get("sim_kind"),
            "dims": scene_sequence.get("dims"),
            "dx": scene_sequence.get("dx"),
            "world_units": "cell",
            "cache_frame_count": (handoff.get("checks") or {}).get("scene_frames"),
            "converted_frame_count": (handoff.get("checks") or {}).get("scene_frames"),
            "render_frame_count": len(frames),
            "visual_frame_count": (handoff.get("checks") or {}).get("visual_frames"),
            "mapping_mode": (handoff.get("checks") or {}).get("mapping_mode"),
        },
        "camera": {
            "source": "renderer_scene_cache_handoff",
        },
        "render_passes": {
            "visual_contract": handoff.get("visual_contract", {}),
        },
        "summary": {
            "water_bounds_min": water_bounds_min,
            "water_bounds_max": water_bounds_max,
            "secondary_bounds_min": secondary_bounds_min,
            "secondary_bounds_max": secondary_bounds_max,
            "water_depth_y_span": stat_summary(water_y_spans),
            "water_depth_z_span": stat_summary(water_z_spans),
            "phase_field_liquid_volume": stat_summary(liquid_volumes),
            "phase_field_cells": stat_summary(phase_cells),
            "water_mesh_face_count": stat_summary(mesh_faces),
            "water_mesh_occupied_cell_count": stat_summary(mesh_occupied),
            "secondary_total_count": stat_summary(secondary_totals),
        },
        "sanity_checks": sanity_checks,
        "status": "ok" if all(check["passed"] for check in sanity_checks) else "failed",
        "frames": frames,
    }
    return summary


def write_report(path, summary, out_path):
    s = summary.get("summary") or {}
    lines = [
        "# S580 Renderer Scene Render Data Summary",
        "",
        f"Generated UTC: `{summary.get('generated_utc')}`",
        f"Status: `{summary.get('status')}`",
        f"Output: `{out_path}`",
        "",
        "## Coverage",
        "",
        f"- Scene/cache frames: `{summary.get('simulation', {}).get('cache_frame_count')}`",
        f"- Visual frames: `{summary.get('simulation', {}).get('visual_frame_count')}`",
        f"- Render-data frames: `{summary.get('simulation', {}).get('render_frame_count')}`",
        f"- Mapping mode: `{summary.get('simulation', {}).get('mapping_mode')}`",
        "",
        "## Bounds And Depth",
        "",
        f"- Water bounds min: `{s.get('water_bounds_min')}`",
        f"- Water bounds max: `{s.get('water_bounds_max')}`",
        f"- Secondary bounds min: `{s.get('secondary_bounds_min')}`",
        f"- Secondary bounds max: `{s.get('secondary_bounds_max')}`",
        f"- Water Y-depth span: `{s.get('water_depth_y_span')}`",
        f"- Water Z-depth span: `{s.get('water_depth_z_span')}`",
        f"- Phase-field liquid volume: `{s.get('phase_field_liquid_volume')}`",
        f"- Water mesh face count: `{s.get('water_mesh_face_count')}`",
        f"- Water mesh occupied cell count: `{s.get('water_mesh_occupied_cell_count')}`",
        f"- Secondary total count: `{s.get('secondary_total_count')}`",
        "",
        "## Sanity Checks",
        "",
        "| Check | Passed | Value |",
        "| --- | ---: | --- |",
    ]
    for check in summary.get("sanity_checks") or []:
        lines.append(f"| `{check.get('name')}` | `{check.get('passed')}` | `{check.get('value')}` |")
    lines.extend([
        "",
        "## Next",
        "",
        "Run profile diagnostics, then consume this sidecar in a bounded renderer-side depth/material preview over the S578 visual contract.",
        "",
    ])
    write_text(path, "\n".join(lines))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export render-data sidecar from a Mitsuba renderer scene-cache handoff")
    parser.add_argument("handoff_manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    summary = build_summary(args.handoff_manifest)
    write_json(args.out, summary)
    if args.report:
        write_report(args.report, summary, args.out)
    print(f"status={summary['status']}")
    print(f"frames={summary['simulation']['render_frame_count']}")
    print(f"out={args.out}")
    if args.report:
        print(f"report={args.report}")
    if summary["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
