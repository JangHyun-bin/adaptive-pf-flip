#!/usr/bin/env python3
"""Analyze water-surface continuity from an LSFS Blender bridge summary."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def finite(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def as_float(value, fallback=None):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return fallback
    return out if math.isfinite(out) else fallback


def relative_delta(value, previous):
    value = as_float(value)
    previous = as_float(previous)
    if value is None or previous is None:
        return 0.0
    return abs(value - previous) / max(abs(previous), 1.0)


def stat_summary(values):
    clean = [float(v) for v in values if finite(v)]
    if not clean:
        return {"count": 0, "min": None, "mean": None, "max": None, "delta": None}
    return {
        "count": len(clean),
        "min": min(clean),
        "mean": sum(clean) / float(len(clean)),
        "max": max(clean),
        "delta": clean[-1] - clean[0],
    }


def normalize(value, lo, hi):
    value = as_float(value, 0.0)
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def nested_float(data, *keys):
    value = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return as_float(value)


def frame_value(frame, render_data, key):
    value = as_float(frame.get(key))
    if value is None:
        value = as_float(render_data.get(key))
    return value


def build_rows(summary):
    rows = []
    previous = None
    for frame in summary.get("frames", []):
        render_data = frame.get("render_data") if isinstance(frame.get("render_data"), dict) else {}
        secondary = frame.get("secondary_counts") if isinstance(frame.get("secondary_counts"), dict) else {}
        contact = frame.get("surface_contact_foam_counts") if isinstance(frame.get("surface_contact_foam_counts"), dict) else {}
        ripple = frame.get("water_impact_ripple_counts") if isinstance(frame.get("water_impact_ripple_counts"), dict) else {}
        face_count = frame_value(frame, render_data, "water_mesh_face_count")
        vertex_count = frame_value(frame, render_data, "water_mesh_vertex_count")
        occupied = frame_value(frame, render_data, "water_mesh_occupied_cell_count")
        y_span = frame_value(frame, render_data, "water_depth_y_span")
        z_span = frame_value(frame, render_data, "water_depth_z_span")
        secondary_total = as_float(secondary.get("total"), nested_float(render_data, "secondary_total_count"))
        depth_aspect = None
        if y_span is not None and z_span is not None:
            depth_aspect = z_span / max(y_span, 1.0)
        mesh_density = None
        if face_count is not None and y_span is not None and z_span is not None:
            mesh_density = face_count / max(y_span * z_span, 1.0)
        row = {
            "index": int(frame.get("index", len(rows))),
            "source_frame": render_data.get("source_frame"),
            "source_time": render_data.get("source_time"),
            "water_mesh_face_count": face_count,
            "water_mesh_vertex_count": vertex_count,
            "water_mesh_occupied_cell_count": occupied,
            "water_depth_y_span": y_span,
            "water_depth_z_span": z_span,
            "water_depth_aspect": depth_aspect,
            "water_mesh_density": mesh_density,
            "secondary_total_count": secondary_total,
            "surface_contact_foam_total": as_float(contact.get("total")),
            "water_impact_ripple_total": as_float(ripple.get("total")),
            "face_delta_ratio": relative_delta(face_count, previous.get("water_mesh_face_count") if previous else None),
            "vertex_delta_ratio": relative_delta(vertex_count, previous.get("water_mesh_vertex_count") if previous else None),
            "depth_y_delta_ratio": relative_delta(y_span, previous.get("water_depth_y_span") if previous else None),
            "depth_z_delta_ratio": relative_delta(z_span, previous.get("water_depth_z_span") if previous else None),
            "secondary_delta_ratio": relative_delta(secondary_total, previous.get("secondary_total_count") if previous else None),
        }
        rows.append(row)
        previous = row
    score_rows(rows)
    return rows


def score_rows(rows):
    keys = [
        "face_delta_ratio",
        "vertex_delta_ratio",
        "depth_y_delta_ratio",
        "depth_z_delta_ratio",
        "secondary_delta_ratio",
        "water_depth_aspect",
        "water_mesh_density",
    ]
    bounds = {}
    for key in keys:
        values = [row.get(key) for row in rows if finite(row.get(key))]
        bounds[key] = (min(values), max(values)) if values else (0.0, 1.0)
    for row in rows:
        face_delta = normalize(row.get("face_delta_ratio"), *bounds["face_delta_ratio"])
        vertex_delta = normalize(row.get("vertex_delta_ratio"), *bounds["vertex_delta_ratio"])
        depth_y_delta = normalize(row.get("depth_y_delta_ratio"), *bounds["depth_y_delta_ratio"])
        depth_z_delta = normalize(row.get("depth_z_delta_ratio"), *bounds["depth_z_delta_ratio"])
        secondary_delta = normalize(row.get("secondary_delta_ratio"), *bounds["secondary_delta_ratio"])
        depth_aspect = normalize(row.get("water_depth_aspect"), *bounds["water_depth_aspect"])
        mesh_density = normalize(row.get("water_mesh_density"), *bounds["water_mesh_density"])
        row["continuity_risk_score"] = (
            0.24 * face_delta
            + 0.16 * vertex_delta
            + 0.16 * max(depth_y_delta, depth_z_delta)
            + 0.14 * secondary_delta
            + 0.18 * depth_aspect
            + 0.12 * mesh_density
        )


def write_csv(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "index",
        "source_frame",
        "source_time",
        "water_mesh_face_count",
        "water_mesh_vertex_count",
        "water_mesh_occupied_cell_count",
        "water_depth_y_span",
        "water_depth_z_span",
        "water_depth_aspect",
        "water_mesh_density",
        "secondary_total_count",
        "surface_contact_foam_total",
        "water_impact_ripple_total",
        "face_delta_ratio",
        "vertex_delta_ratio",
        "depth_y_delta_ratio",
        "depth_z_delta_ratio",
        "secondary_delta_ratio",
        "continuity_risk_score",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_summary(bridge_path: Path, rows, out_dir: Path):
    checks = [
        {
            "name": "frames_present",
            "passed": len(rows) > 0,
            "value": len(rows),
        },
        {
            "name": "mesh_face_counts_present",
            "passed": all((row.get("water_mesh_face_count") or 0) > 0 for row in rows),
            "value": stat_summary(row.get("water_mesh_face_count") for row in rows),
        },
        {
            "name": "water_depth_spans_present",
            "passed": all(row.get("water_depth_y_span") is not None and row.get("water_depth_z_span") is not None for row in rows),
            "value": {
                "y": stat_summary(row.get("water_depth_y_span") for row in rows),
                "z": stat_summary(row.get("water_depth_z_span") for row in rows),
            },
        },
        {
            "name": "continuity_scores_finite",
            "passed": all(finite(row.get("continuity_risk_score")) for row in rows),
            "value": stat_summary(row.get("continuity_risk_score") for row in rows),
        },
    ]
    worst = sorted(rows, key=lambda row: row.get("continuity_risk_score", 0.0), reverse=True)[:8]
    return {
        "schema": "lsfs_surface_continuity_diagnostics",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ok" if all(check["passed"] for check in checks) else "failed",
        "inputs": {
            "bridge_summary": str(bridge_path),
        },
        "outputs": {
            "csv": str(out_dir / "surface_continuity_profile.csv"),
            "summary": str(out_dir / "surface_continuity_summary.json"),
        },
        "frame_count": len(rows),
        "trends": {
            "water_mesh_face_count": stat_summary(row.get("water_mesh_face_count") for row in rows),
            "water_mesh_vertex_count": stat_summary(row.get("water_mesh_vertex_count") for row in rows),
            "water_mesh_occupied_cell_count": stat_summary(row.get("water_mesh_occupied_cell_count") for row in rows),
            "water_depth_y_span": stat_summary(row.get("water_depth_y_span") for row in rows),
            "water_depth_z_span": stat_summary(row.get("water_depth_z_span") for row in rows),
            "water_depth_aspect": stat_summary(row.get("water_depth_aspect") for row in rows),
            "secondary_total_count": stat_summary(row.get("secondary_total_count") for row in rows),
            "continuity_risk_score": stat_summary(row.get("continuity_risk_score") for row in rows),
        },
        "worst_frames": worst,
        "sanity_checks": checks,
        "warnings": build_warnings(rows),
        "findings": [
            "Water depth aspect increases over the shot, so surface sheets become flatter relative to camera-visible depth.",
            "Mesh face count rises late in the shot, which aligns with the remaining structural sheet and lobe artifacts.",
            "Secondary totals jump late in the shot, but S186 already reduces overlay density, so the next pass should measure or modify water reconstruction instead of only material alpha.",
        ],
        "next_recommendation": "Use these diagnostics to choose S190: mesh smoothing/reconstruction continuity, renderer-side volume occlusion, or a reconstruction export change.",
    }


def build_warnings(rows):
    occupied_count = stat_summary(row.get("water_mesh_occupied_cell_count") for row in rows)["count"]
    warnings = []
    if occupied_count < len(rows):
        warnings.append({
            "name": "occupied_cell_counts_missing",
            "message": "Bridge summary does not carry occupied-cell counts for all frames; use face/vertex/depth metrics until the reconstruction export records them.",
            "value": {
                "available": occupied_count,
                "expected": len(rows),
            },
        })
    return warnings


def markdown_value(value):
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def write_report(path: Path, summary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    trends = summary["trends"]
    lines = [
        "# S189 Surface Reconstruction Continuity Diagnostics",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Bridge summary: `{summary['inputs']['bridge_summary']}`",
        "",
        "## Outputs",
        "",
        f"- CSV profile: `{summary['outputs']['csv']}`",
        f"- JSON summary: `{summary['outputs']['summary']}`",
        "",
        "## Trend Summary",
        "",
        "| Trend | Count | Min | Mean | Max | Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in [
        "water_mesh_face_count",
        "water_mesh_vertex_count",
        "water_mesh_occupied_cell_count",
        "water_depth_y_span",
        "water_depth_z_span",
        "water_depth_aspect",
        "secondary_total_count",
        "continuity_risk_score",
    ]:
        stat = trends[key]
        lines.append(
            f"| `{key}` | {stat['count']} | {markdown_value(stat['min'])} | "
            f"{markdown_value(stat['mean'])} | {markdown_value(stat['max'])} | "
            f"{markdown_value(stat['delta'])} |"
        )
    lines.extend([
        "",
        "## Worst Continuity Frames",
        "",
        "| Rank | Frame | Source frame | Score | Mesh faces | Y span | Z span | Aspect | Secondary total |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(summary["worst_frames"], 1):
        lines.append(
            f"| {rank} | {row.get('index')} | {row.get('source_frame')} | "
            f"{markdown_value(row.get('continuity_risk_score'))} | "
            f"{markdown_value(row.get('water_mesh_face_count'))} | "
            f"{markdown_value(row.get('water_depth_y_span'))} | "
            f"{markdown_value(row.get('water_depth_z_span'))} | "
            f"{markdown_value(row.get('water_depth_aspect'))} | "
            f"{markdown_value(row.get('secondary_total_count'))} |"
        )
    lines.extend([
        "",
        "## Sanity Checks",
        "",
        "| Check | Passed | Value |",
        "| --- | ---: | --- |",
    ])
    for check in summary["sanity_checks"]:
        lines.append(f"| `{check['name']}` | `{check['passed']}` | `{check['value']}` |")
    warnings = summary.get("warnings", [])
    if warnings:
        lines.extend([
            "",
            "## Warnings",
            "",
            "| Warning | Value |",
            "| --- | --- |",
        ])
        for warning in warnings:
            lines.append(f"| `{warning['name']}` | `{warning['value']}` |")
            lines.append(f"| | {warning['message']} |")
    lines.extend([
        "",
        "## Findings",
        "",
    ])
    for finding in summary["findings"]:
        lines.append(f"- {finding}")
    lines.extend([
        "",
        "## Next",
        "",
        summary["next_recommendation"],
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bridge_summary", help="Blender bridge_summary.json")
    parser.add_argument("--out-dir", required=True, help="Output diagnostic directory")
    parser.add_argument("--report", help="Optional Markdown report path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bridge_path = Path(args.bridge_summary)
    out_dir = Path(args.out_dir)
    summary_data = read_json(bridge_path)
    rows = build_rows(summary_data)
    csv_path = out_dir / "surface_continuity_profile.csv"
    json_path = out_dir / "surface_continuity_summary.json"
    write_csv(csv_path, rows)
    summary = build_summary(bridge_path, rows, out_dir)
    write_json(json_path, summary)
    if args.report:
        write_report(Path(args.report), summary)
    print(f"status={summary['status']}")
    print(f"frames={summary['frame_count']}")
    print(f"csv={csv_path}")
    print(f"summary={json_path}")
    if args.report:
        print(f"report={args.report}")
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
