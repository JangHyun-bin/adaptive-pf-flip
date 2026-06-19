#!/usr/bin/env python3
"""Export a compact render/depth metadata sidecar for a cinematic shot."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path


MESH_FRAME_RE = re.compile(r"frame_(\d+)_water\.obj$")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def finite_number(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


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


def parse_cache_metadata(path: Path):
    sections = {}
    wanted = {"header", "camera", "water_volume", "secondary_channels", "cinematic_metadata"}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            section = item.get("section")
            if section in wanted:
                sections[section] = item
            if section == "phase_field":
                break
    return sections


def mesh_frame_index(path_text: str | None):
    if not path_text:
        return None
    match = MESH_FRAME_RE.search(Path(path_text).name)
    if not match:
        return None
    return int(match.group(1))


def resolve_input_paths(shot_dir: Path):
    cache_manifest = shot_dir / "cache" / "manifest.json"
    sequence = shot_dir / "converted" / "sequence.json"
    water_reconstruction = shot_dir / "water_mesh" / "water_reconstruction.json"
    render_summary = shot_dir / "blender" / "bridge_summary.json"
    missing = [
        str(path)
        for path in (cache_manifest, sequence, water_reconstruction, render_summary)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("missing shot inputs: " + ", ".join(missing))
    return cache_manifest, sequence, water_reconstruction, render_summary


def build_summary(shot_dir: Path):
    cache_manifest_path, sequence_path, water_path, render_summary_path = resolve_input_paths(shot_dir)
    manifest = read_json(cache_manifest_path)
    sequence = read_json(sequence_path)
    water = read_json(water_path)
    render_summary = read_json(render_summary_path)

    water_frames = {int(frame["frame"]): frame for frame in water.get("frames", [])}
    render_frames = render_summary.get("frames", [])
    cache_dir = cache_manifest_path.parent

    frames = []
    water_bounds_min = None
    water_bounds_max = None
    secondary_bounds_min = None
    secondary_bounds_max = None
    water_depth_y_spans = []
    water_depth_z_spans = []
    liquid_volumes = []
    phase_cells = []
    mesh_faces = []
    mesh_occupied_cells = []
    secondary_totals = []
    source_frames = []

    for render_frame in render_frames:
        output_frame = int(render_frame.get("index", len(frames)))
        recon_index = mesh_frame_index(render_frame.get("water_mesh"))
        recon_frame = water_frames.get(recon_index) if recon_index is not None else None
        if recon_frame is None and output_frame in water_frames:
            recon_frame = water_frames[output_frame]
            recon_index = output_frame
        if recon_frame is None:
            raise ValueError(f"could not map render frame {output_frame} to water reconstruction frame")

        source_cache = recon_frame.get("source_cache")
        if not source_cache:
            raise ValueError(f"water reconstruction frame {recon_index} has no source_cache")
        cache_path = cache_dir / source_cache
        cache_meta = parse_cache_metadata(cache_path)
        cinematic = cache_meta.get("cinematic_metadata", {})
        water_volume = cache_meta.get("water_volume", {})
        secondary_channels = cache_meta.get("secondary_channels", {})
        header = cache_meta.get("header", {})

        wb_min = cinematic.get("water_bounds_min")
        wb_max = cinematic.get("water_bounds_max")
        sb_min = cinematic.get("secondary_bounds_min")
        sb_max = cinematic.get("secondary_bounds_max")
        water_bounds_min = vec_min(water_bounds_min, wb_min)
        water_bounds_max = vec_max(water_bounds_max, wb_max)
        secondary_bounds_min = vec_min(secondary_bounds_min, sb_min)
        secondary_bounds_max = vec_max(secondary_bounds_max, sb_max)

        y_span = None
        z_span = None
        if wb_min and wb_max and len(wb_min) >= 3 and len(wb_max) >= 3:
            y_span = float(wb_max[1]) - float(wb_min[1])
            z_span = float(wb_max[2]) - float(wb_min[2])
            water_depth_y_spans.append(y_span)
            water_depth_z_spans.append(z_span)

        liquid_volume = water_volume.get("phase_field_liquid_volume")
        liquid_volumes.append(liquid_volume)
        phase_cells.append(water_volume.get("phase_field_cells"))
        face_count = render_frame.get("water_mesh_face_count", recon_frame.get("face_count"))
        mesh_faces.append(face_count)
        occupied_cell_count = recon_frame.get("occupied_cell_count")
        mesh_occupied_cells.append(occupied_cell_count)
        secondary_total = (
            render_frame.get("secondary_counts", {}).get("total")
            or secondary_channels.get("total_count")
            or water_volume.get("secondary_particle_count")
        )
        secondary_totals.append(secondary_total)
        source_frame = recon_frame.get("source_frame", header.get("frame"))
        source_frames.append(source_frame)

        frames.append({
            "output_frame": output_frame,
            "water_reconstruction_frame": recon_index,
            "source_frame": source_frame,
            "source_time": recon_frame.get("source_time", header.get("time")),
            "source_cache": source_cache,
            "water_mesh": render_frame.get("water_mesh") or recon_frame.get("mesh"),
            "water_mesh_face_count": face_count,
            "water_mesh_vertex_count": recon_frame.get("vertex_count"),
            "occupied_cell_count": occupied_cell_count,
            "water_mesh_occupied_cell_count": occupied_cell_count,
            "water_bounds_min": wb_min,
            "water_bounds_max": wb_max,
            "water_depth_y_span": y_span,
            "water_depth_z_span": z_span,
            "secondary_bounds_min": sb_min,
            "secondary_bounds_max": sb_max,
            "primary_liquid_count": water_volume.get("primary_liquid_count"),
            "primary_gas_count": water_volume.get("primary_gas_count"),
            "phase_field_cells": water_volume.get("phase_field_cells"),
            "phase_field_liquid_volume": liquid_volume,
            "secondary_counts": render_frame.get("secondary_counts", {
                "droplet": secondary_channels.get("droplet_count"),
                "spray": secondary_channels.get("spray_count"),
                "foam": secondary_channels.get("foam_count"),
                "bubble": secondary_channels.get("bubble_count"),
                "total": secondary_channels.get("total_count"),
            }),
        })

    source_frame_numbers = [int(v) for v in source_frames if v is not None]
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
    ]

    return {
        "schema": "lsfs_render_data_summary",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "shot_dir": os.fspath(shot_dir),
        "inputs": {
            "manifest": os.fspath(cache_manifest_path),
            "sequence": os.fspath(sequence_path),
            "water_reconstruction": os.fspath(water_path),
            "render_summary": os.fspath(render_summary_path),
        },
        "simulation": {
            "sim_kind": manifest.get("sim_kind"),
            "dims": manifest.get("dims"),
            "dx": manifest.get("dx"),
            "world_units": manifest.get("world_units"),
            "cache_frame_count": manifest.get("frame_count"),
            "converted_frame_count": sequence.get("frame_count"),
            "render_frame_count": len(frames),
        },
        "camera": {
            "motion": render_summary.get("camera_motion", {}),
            "path_metrics": render_summary.get("camera_path_metrics", {}),
            "framing": render_summary.get("camera_framing", {}),
        },
        "render_passes": {
            "water_material": render_summary.get("water_material", {}),
            "water_volume_scattering_pass": render_summary.get("water_volume_scattering_pass", {}),
            "water_surface_glint_pass": render_summary.get("water_surface_glint_pass", {}),
            "water_reflection_pass": render_summary.get("water_reflection_pass", {}),
            "secondary_soft_pass": render_summary.get("secondary_soft_pass", {}),
            "secondary_streak_pass": render_summary.get("secondary_streak_pass", {}),
        },
        "summary": {
            "water_bounds_min": water_bounds_min,
            "water_bounds_max": water_bounds_max,
            "secondary_bounds_min": secondary_bounds_min,
            "secondary_bounds_max": secondary_bounds_max,
            "water_depth_y_span": stat_summary(water_depth_y_spans),
            "water_depth_z_span": stat_summary(water_depth_z_spans),
            "phase_field_liquid_volume": stat_summary(liquid_volumes),
            "phase_field_cells": stat_summary(phase_cells),
            "water_mesh_face_count": stat_summary(mesh_faces),
            "water_mesh_occupied_cell_count": stat_summary(mesh_occupied_cells),
            "secondary_total_count": stat_summary(secondary_totals),
        },
        "sanity_checks": sanity_checks,
        "status": "ok" if all(check["passed"] for check in sanity_checks) else "failed",
        "frames": frames,
    }


def write_report(path: Path, summary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    checks = summary.get("sanity_checks", [])
    s = summary.get("summary", {})
    lines = [
        "# S171 Render Data Depth Export",
        "",
        f"Generated UTC: `{summary.get('generated_utc')}`",
        f"Status: `{summary.get('status')}`",
        f"Shot directory: `{summary.get('shot_dir')}`",
        "",
        "## Outputs",
        "",
        f"- Render data summary: `{summary.get('output_path', '')}`",
        "",
        "## Frame Coverage",
        "",
        f"- Cache frames: `{summary.get('simulation', {}).get('cache_frame_count')}`",
        f"- Converted frames: `{summary.get('simulation', {}).get('converted_frame_count')}`",
        f"- Render frames: `{summary.get('simulation', {}).get('render_frame_count')}`",
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
    for check in checks:
        lines.append(f"| `{check.get('name')}` | `{check.get('passed')}` | `{check.get('value')}` |")
    lines.extend([
        "",
        "## Render Pass Context",
        "",
        f"- Water material: `{summary.get('render_passes', {}).get('water_material')}`",
        f"- Water volume scattering: `{summary.get('render_passes', {}).get('water_volume_scattering_pass')}`",
        f"- Water glint pass: `{summary.get('render_passes', {}).get('water_surface_glint_pass')}`",
        f"- Water reflection pass: `{summary.get('render_passes', {}).get('water_reflection_pass')}`",
        "",
        "## Next",
        "",
        "Use this sidecar as the renderer-facing data contract for the next pass:",
        "consume water bounds/depth spans, mesh complexity, secondary counts, and",
        "camera context without re-reading large raw cache JSONL files.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shot_dir", help="Cinematic shot directory")
    parser.add_argument("--out", required=True, help="Output render data summary JSON")
    parser.add_argument("--report", help="Optional Markdown report path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    shot_dir = Path(args.shot_dir)
    out = Path(args.out)
    summary = build_summary(shot_dir)
    summary["output_path"] = os.fspath(out)
    write_json(out, summary)
    if args.report:
        write_report(Path(args.report), summary)
    print(f"status={summary['status']}")
    print(f"frames={summary['simulation']['render_frame_count']}")
    print(f"out={out}")
    if args.report:
        print(f"report={args.report}")
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
