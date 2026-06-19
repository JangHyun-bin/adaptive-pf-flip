#!/usr/bin/env python3
"""Annotate LSFS water_reconstruction.json with OBJ surface-quality metadata."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import analyze_water_mesh_quality as mesh_quality


SURFACE_QUALITY_KEYS = [
    "vertex_count",
    "normal_count",
    "face_count",
    "used_vertex_count",
    "component_count",
    "largest_component_face_ratio",
    "boundary_edge_ratio",
    "nonmanifold_edge_ratio",
    "sharp_edge_ratio",
    "normal_discontinuity_mean",
    "normal_discontinuity_p95",
    "edge_length_cv",
    "face_area_cv",
    "degenerate_face_ratio",
    "mesh_quality_risk_score",
]


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


def markdown_value(value):
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def surface_quality_label(row) -> str:
    if (row.get("boundary_edge_ratio") or 0.0) > 0.0:
        return "topology_boundary"
    if (row.get("nonmanifold_edge_ratio") or 0.0) > 0.0:
        return "topology_nonmanifold"
    if (row.get("degenerate_face_ratio") or 0.0) > 0.0:
        return "topology_degenerate"
    if (row.get("largest_component_face_ratio") or 0.0) < 0.98:
        return "component_fragmented"
    if (row.get("normal_discontinuity_p95") or 0.0) >= 0.085:
        return "normal_rough"
    if (row.get("sharp_edge_ratio") or 0.0) >= 0.012:
        return "sharp_edges"
    return "stable"


def frame_surface_quality(row):
    out = {
        "schema": "lsfs_water_mesh_surface_quality_frame",
        "version": 1,
        "label": surface_quality_label(row),
    }
    for key in SURFACE_QUALITY_KEYS:
        value = row.get(key)
        if finite(value) or isinstance(value, int):
            out[key] = value
        elif value is None:
            out[key] = None
    return out


def mesh_abs_path(reconstruction_path: Path, frame) -> Path:
    mesh = Path(frame.get("mesh", ""))
    if mesh.is_absolute():
        return mesh
    return (reconstruction_path.parent / mesh).resolve()


def rebase_mesh_paths(annotated, reconstruction_path: Path, out_path: Path) -> None:
    out_base = out_path.parent.resolve()
    for frame in annotated.get("frames", []):
        if not isinstance(frame, dict) or not frame.get("mesh"):
            continue
        mesh_path = mesh_abs_path(reconstruction_path, frame)
        frame["mesh"] = os.path.relpath(mesh_path, out_base).replace(os.sep, "/")


def trend(rows, key):
    return mesh_quality.trend(rows, key)


def build_summary(reconstruction_path: Path, annotated_path: Path, rows, out_dir: Path, next_text):
    labels = Counter(surface_quality_label(row) for row in rows)
    worst = sorted(rows, key=lambda row: row.get("mesh_quality_risk_score") or 0.0, reverse=True)[:8]
    checks = [
        {
            "name": "frames_present",
            "passed": len(rows) > 0,
            "value": len(rows),
        },
        {
            "name": "surface_quality_labels_present",
            "passed": sum(labels.values()) == len(rows),
            "value": dict(sorted(labels.items())),
        },
        {
            "name": "quality_scores_finite",
            "passed": all(finite(row.get("mesh_quality_risk_score")) for row in rows),
            "value": trend(rows, "mesh_quality_risk_score"),
        },
        {
            "name": "obj_counts_match_index",
            "passed": all(
                row.get("vertex_count") == row.get("summary_vertex_count")
                and row.get("face_count") == row.get("summary_face_count")
                for row in rows
            ),
            "value": len(rows),
        },
    ]
    return {
        "schema": "lsfs_water_mesh_surface_quality_annotation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ok" if all(check["passed"] for check in checks) else "warning",
        "inputs": {
            "water_reconstruction": str(reconstruction_path),
        },
        "outputs": {
            "annotated_reconstruction": str(annotated_path),
            "csv": str(out_dir / "water_mesh_surface_quality_profile.csv"),
            "summary": str(out_dir / "water_mesh_surface_quality_summary.json"),
        },
        "frame_count": len(rows),
        "label_counts": dict(sorted(labels.items())),
        "trends": {
            "component_count": trend(rows, "component_count"),
            "largest_component_face_ratio": trend(rows, "largest_component_face_ratio"),
            "sharp_edge_ratio": trend(rows, "sharp_edge_ratio"),
            "normal_discontinuity_p95": trend(rows, "normal_discontinuity_p95"),
            "edge_length_cv": trend(rows, "edge_length_cv"),
            "face_area_cv": trend(rows, "face_area_cv"),
            "mesh_quality_risk_score": trend(rows, "mesh_quality_risk_score"),
        },
        "worst_frames": worst,
        "sanity_checks": checks,
        "findings": [
            "This annotation keeps water mesh geometry unchanged and records OBJ-level quality as frame metadata.",
            "component_fragmented labels identify frames where a smaller closed water component exists and should be treated, not deleted, without visual review.",
            "normal_rough and sharp_edges labels are renderer/export hints for later surface shading or continuity passes.",
        ],
        "next_recommendation": next_text or "Feed the annotated reconstruction through convert_render_cache so render frames carry water_mesh_surface_quality metadata.",
    }


def write_csv(path: Path, rows) -> None:
    columns = [
        "frame",
        "source_frame",
        "source_time",
        "label",
        "component_count",
        "largest_component_face_ratio",
        "sharp_edge_ratio",
        "normal_discontinuity_p95",
        "edge_length_cv",
        "face_area_cv",
        "degenerate_face_ratio",
        "mesh_quality_risk_score",
        "mesh",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            item = {key: row.get(key) for key in columns}
            item["label"] = surface_quality_label(row)
            writer.writerow(item)


def write_report(path: Path, summary, title) -> None:
    trends = summary["trends"]
    lines = [
        f"# {title}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Water reconstruction: `{summary['inputs']['water_reconstruction']}`",
        "",
        "## Outputs",
        "",
        f"- Annotated reconstruction: `{summary['outputs']['annotated_reconstruction']}`",
        f"- CSV profile: `{summary['outputs']['csv']}`",
        f"- JSON summary: `{summary['outputs']['summary']}`",
        "",
        "## Label Counts",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label, count in summary["label_counts"].items():
        lines.append(f"| `{label}` | {count} |")
    lines.extend([
        "",
        "## Trend Summary",
        "",
        "| Trend | Count | Min | Mean | Max | Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for key, stat in trends.items():
        lines.append(
            f"| `{key}` | {stat['count']} | {markdown_value(stat['min'])} | "
            f"{markdown_value(stat['mean'])} | {markdown_value(stat['max'])} | "
            f"{markdown_value(stat.get('delta'))} |"
        )
    lines.extend([
        "",
        "## Worst Surface Frames",
        "",
        "| Rank | Frame | Source frame | Label | Score | Components | Largest comp | Sharp edge | Normal p95 |",
        "| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(summary["worst_frames"], 1):
        lines.append(
            f"| {rank} | {row.get('frame')} | {row.get('source_frame')} | "
            f"`{surface_quality_label(row)}` | "
            f"{markdown_value(row.get('mesh_quality_risk_score'))} | "
            f"{markdown_value(row.get('component_count'))} | "
            f"{markdown_value(row.get('largest_component_face_ratio'))} | "
            f"{markdown_value(row.get('sharp_edge_ratio'))} | "
            f"{markdown_value(row.get('normal_discontinuity_p95'))} |"
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def annotate(reconstruction_path: Path, out_path: Path, out_dir: Path, next_text=None):
    reconstruction = read_json(reconstruction_path)
    if reconstruction.get("reconstructor") != "lsfs_water_reconstruction":
        raise RuntimeError(f"{reconstruction_path}: not an LSFS water reconstruction index")
    rows = mesh_quality.build_rows(reconstruction_path, reconstruction)
    annotated = copy.deepcopy(reconstruction)
    rebase_mesh_paths(annotated, reconstruction_path, out_path)
    for frame, row in zip(annotated.get("frames", []), rows):
        frame["surface_quality"] = frame_surface_quality(row)
    summary = build_summary(reconstruction_path, out_path, rows, out_dir, next_text)
    annotated["surface_quality_annotation"] = {
        "schema": summary["schema"],
        "version": summary["version"],
        "generated_utc": summary["generated_utc"],
        "status": summary["status"],
        "label_counts": summary["label_counts"],
        "trends": summary["trends"],
    }
    write_json(out_path, annotated)
    write_csv(out_dir / "water_mesh_surface_quality_profile.csv", rows)
    write_json(out_dir / "water_mesh_surface_quality_summary.json", summary)
    return summary


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("water_reconstruction", help="input water_reconstruction.json")
    parser.add_argument("--out", required=True, help="annotated water_reconstruction.json output")
    parser.add_argument("--out-dir", required=True, help="diagnostic output directory")
    parser.add_argument("--report", help="optional Markdown report")
    parser.add_argument("--title", default="Water Mesh Surface Quality Annotation")
    parser.add_argument("--next", dest="next_text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reconstruction_path = Path(args.water_reconstruction)
    out_path = Path(args.out)
    out_dir = Path(args.out_dir)
    summary = annotate(reconstruction_path, out_path, out_dir, args.next_text)
    if args.report:
        write_report(Path(args.report), summary, args.title)
    print(f"status={summary['status']}")
    print(f"frames={summary['frame_count']}")
    print(f"labels={summary['label_counts']}")
    print(f"annotated={summary['outputs']['annotated_reconstruction']}")
    print(f"summary={summary['outputs']['summary']}")
    if args.report:
        print(f"report={args.report}")
    return 0 if summary["status"] in ("ok", "warning") else 1


if __name__ == "__main__":
    raise SystemExit(main())
