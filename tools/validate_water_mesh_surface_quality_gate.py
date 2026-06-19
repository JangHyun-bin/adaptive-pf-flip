#!/usr/bin/env python3
"""Validate render-window water mesh surface-quality labels."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_BLOCK_LABELS = [
    "component_fragmented",
    "topology_boundary",
    "topology_nonmanifold",
    "topology_degenerate",
]

DEFAULT_WARN_LABELS = [
    "normal_rough",
    "sharp_edges",
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


def mesh_key(path) -> str:
    if not isinstance(path, str) or not path:
        return ""
    return os.path.basename(path.replace("\\", "/"))


def mesh_frame_index(path):
    match = re.search(r"frame_(\d+)_water\.obj", mesh_key(path))
    return int(match.group(1)) if match else None


def quality_map_from_sequence(sequence_path: Path):
    data = read_json(sequence_path)
    if data.get("converter") != "lsfs_render_cache_converter":
        raise RuntimeError(f"{sequence_path}: expected lsfs_render_cache_converter")
    out = {}
    duplicate_labels = {}
    for index, frame in enumerate(data.get("frames", [])):
        key = mesh_key(frame.get("water_mesh"))
        quality = frame.get("water_mesh_surface_quality")
        if not key or not isinstance(quality, dict):
            continue
        label = quality.get("label")
        existing = out.get(key)
        if existing and existing.get("label") != label:
            duplicate_labels.setdefault(key, set()).update([existing.get("label"), label])
        out[key] = {
            "sequence_index": index,
            "sequence_frame": frame.get("frame"),
            "mesh": frame.get("water_mesh"),
            "quality": quality,
            "label": label,
        }
    return out, {key: sorted(value) for key, value in duplicate_labels.items()}


def row_for_render_frame(render_frame, frame_index, quality_by_mesh):
    quality = render_frame.get("water_mesh_surface_quality")
    quality_source = "render_summary"
    if not isinstance(quality, dict) or not quality:
        key = mesh_key(render_frame.get("water_mesh"))
        mapped = quality_by_mesh.get(key)
        quality = mapped.get("quality") if mapped else None
        quality_source = "annotated_sequence" if mapped else "missing"
    else:
        key = mesh_key(render_frame.get("water_mesh"))
        mapped = quality_by_mesh.get(key)
    label = quality.get("label") if isinstance(quality, dict) else "missing"
    render_data = render_frame.get("render_data") if isinstance(render_frame.get("render_data"), dict) else {}
    mapped = mapped if "mapped" in locals() else None
    return {
        "render_index": render_frame.get("index", frame_index),
        "source_frame": render_data.get("source_frame"),
        "source_time": render_data.get("source_time"),
        "mesh": render_frame.get("water_mesh"),
        "mesh_key": key,
        "mesh_frame_index": mesh_frame_index(render_frame.get("water_mesh")),
        "quality_source": quality_source,
        "label": label,
        "sequence_index": mapped.get("sequence_index") if mapped else None,
        "sequence_frame": mapped.get("sequence_frame") if mapped else None,
        "component_count": quality.get("component_count") if isinstance(quality, dict) else None,
        "largest_component_face_ratio": quality.get("largest_component_face_ratio") if isinstance(quality, dict) else None,
        "normal_discontinuity_p95": quality.get("normal_discontinuity_p95") if isinstance(quality, dict) else None,
        "sharp_edge_ratio": quality.get("sharp_edge_ratio") if isinstance(quality, dict) else None,
        "mesh_quality_risk_score": quality.get("mesh_quality_risk_score") if isinstance(quality, dict) else None,
    }


def build_rows(render_summary_path: Path, annotated_sequence_path: Path):
    render_summary = read_json(render_summary_path)
    frames = render_summary.get("frames")
    if not isinstance(frames, list) or not frames:
        raise RuntimeError(f"{render_summary_path}: missing frames")
    quality_by_mesh, duplicate_labels = quality_map_from_sequence(annotated_sequence_path)
    rows = [row_for_render_frame(frame, index, quality_by_mesh) for index, frame in enumerate(frames)]
    return render_summary, rows, duplicate_labels


def stat_summary(values):
    clean = [float(value) for value in values if finite(value)]
    if not clean:
        return {"count": 0, "min": None, "mean": None, "max": None}
    return {
        "count": len(clean),
        "min": min(clean),
        "mean": sum(clean) / float(len(clean)),
        "max": max(clean),
    }


def build_summary(render_summary_path: Path,
                  annotated_sequence_path: Path,
                  render_summary,
                  rows,
                  duplicate_labels,
                  out_dir: Path,
                  block_labels,
                  warn_labels,
                  min_stable_ratio,
                  next_text):
    labels = Counter(row.get("label", "missing") for row in rows)
    missing_rows = [row for row in rows if row.get("label") == "missing"]
    blocked_rows = [row for row in rows if row.get("label") in block_labels]
    warned_rows = [row for row in rows if row.get("label") in warn_labels]
    stable_ratio = labels.get("stable", 0) / float(max(1, len(rows)))
    mesh_indices = [row.get("mesh_frame_index") for row in rows if row.get("mesh_frame_index") is not None]
    passed = (
        not missing_rows
        and not duplicate_labels
        and not blocked_rows
        and stable_ratio >= min_stable_ratio
    )
    checks = [
        {
            "name": "frames_present",
            "passed": len(rows) > 0,
            "value": len(rows),
        },
        {
            "name": "surface_quality_present",
            "passed": not missing_rows,
            "value": len(missing_rows),
        },
        {
            "name": "no_duplicate_mesh_label_conflicts",
            "passed": not duplicate_labels,
            "value": duplicate_labels,
        },
        {
            "name": "blocked_labels_absent",
            "passed": not blocked_rows,
            "value": {
                "blocked_labels": block_labels,
                "blocked_count": len(blocked_rows),
            },
        },
        {
            "name": "stable_ratio_floor",
            "passed": stable_ratio >= min_stable_ratio,
            "value": {
                "stable_ratio": stable_ratio,
                "min_stable_ratio": min_stable_ratio,
            },
        },
    ]
    return {
        "schema": "lsfs_water_mesh_surface_quality_gate",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "passed" if passed else "failed",
        "inputs": {
            "render_summary": str(render_summary_path),
            "annotated_sequence": str(annotated_sequence_path),
        },
        "outputs": {
            "csv": str(out_dir / "water_mesh_surface_quality_gate.csv"),
            "summary": str(out_dir / "water_mesh_surface_quality_gate_summary.json"),
        },
        "render_frame_count": len(rows),
        "source_window": render_summary.get("source_window", {}),
        "mesh_frame_index_range": {
            "min": min(mesh_indices) if mesh_indices else None,
            "max": max(mesh_indices) if mesh_indices else None,
            "unique_count": len(set(mesh_indices)),
        },
        "label_counts": dict(sorted(labels.items())),
        "blocked_label_count": len(blocked_rows),
        "warn_label_count": len(warned_rows),
        "stable_ratio": stable_ratio,
        "component_treatment_noop": labels.get("component_fragmented", 0) == 0,
        "risk_score": stat_summary(row.get("mesh_quality_risk_score") for row in rows),
        "normal_discontinuity_p95": stat_summary(row.get("normal_discontinuity_p95") for row in rows),
        "sharp_edge_ratio": stat_summary(row.get("sharp_edge_ratio") for row in rows),
        "sanity_checks": checks,
        "worst_rows": sorted(
            rows,
            key=lambda row: row.get("mesh_quality_risk_score") if finite(row.get("mesh_quality_risk_score")) else -1.0,
            reverse=True)[:8],
        "findings": [
            "The gate validates the actual render window rather than the full reconstruction.",
            "A passing component_treatment_noop result means component-specific material treatment should not affect this accepted window.",
            "Warning labels are reported but do not fail the gate unless they are also listed as blocked labels.",
        ],
        "next_recommendation": next_text or "Use a passing gate before enabling label-driven water surface treatment in a render preset.",
    }


def write_csv(path: Path, rows) -> None:
    columns = [
        "render_index",
        "source_frame",
        "source_time",
        "mesh_key",
        "mesh_frame_index",
        "quality_source",
        "label",
        "sequence_index",
        "sequence_frame",
        "component_count",
        "largest_component_face_ratio",
        "normal_discontinuity_p95",
        "sharp_edge_ratio",
        "mesh_quality_risk_score",
        "mesh",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in columns})


def write_report(path: Path, summary, title) -> None:
    lines = [
        f"# {title}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Render summary: `{summary['inputs']['render_summary']}`",
        f"- Annotated sequence: `{summary['inputs']['annotated_sequence']}`",
        "",
        "## Outputs",
        "",
        f"- CSV profile: `{summary['outputs']['csv']}`",
        f"- JSON summary: `{summary['outputs']['summary']}`",
        "",
        "## Gate Summary",
        "",
        f"- Render frames: `{summary['render_frame_count']}`",
        f"- Source window: `{summary['source_window']}`",
        f"- Mesh frame index range: `{summary['mesh_frame_index_range']}`",
        f"- Label counts: `{summary['label_counts']}`",
        f"- Stable ratio: `{summary['stable_ratio']}`",
        f"- Component treatment no-op: `{summary['component_treatment_noop']}`",
        f"- Blocked label count: `{summary['blocked_label_count']}`",
        f"- Warn label count: `{summary['warn_label_count']}`",
        "",
        "## Metric Summary",
        "",
        "| Metric | Count | Min | Mean | Max |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for key in ("risk_score", "normal_discontinuity_p95", "sharp_edge_ratio"):
        stat = summary[key]
        lines.append(
            f"| `{key}` | {stat['count']} | {markdown_value(stat['min'])} | "
            f"{markdown_value(stat['mean'])} | {markdown_value(stat['max'])} |"
        )
    lines.extend([
        "",
        "## Worst Rows",
        "",
        "| Rank | Render | Source frame | Mesh frame | Label | Score | Normal p95 | Sharp edge |",
        "| ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(summary["worst_rows"], 1):
        lines.append(
            f"| {rank} | {row.get('render_index')} | {row.get('source_frame')} | "
            f"{row.get('mesh_frame_index')} | `{row.get('label')}` | "
            f"{markdown_value(row.get('mesh_quality_risk_score'))} | "
            f"{markdown_value(row.get('normal_discontinuity_p95'))} | "
            f"{markdown_value(row.get('sharp_edge_ratio'))} |"
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


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render_summary", help="bridge_summary.json or blender_scene_spec.json")
    parser.add_argument("annotated_sequence", help="converted sequence.json with water_mesh_surface_quality")
    parser.add_argument("--out-dir", required=True, help="gate output directory")
    parser.add_argument("--report", help="optional Markdown report")
    parser.add_argument("--title", default="Water Mesh Surface Quality Gate")
    parser.add_argument("--block-label", action="append", dest="block_labels",
                        help="label that fails the gate; can be repeated")
    parser.add_argument("--warn-label", action="append", dest="warn_labels",
                        help="label to report without failing; can be repeated")
    parser.add_argument("--min-stable-ratio", type=float, default=0.9)
    parser.add_argument("--next", dest="next_text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_stable_ratio < 0.0 or args.min_stable_ratio > 1.0 or not math.isfinite(args.min_stable_ratio):
        raise SystemExit("min-stable-ratio must be finite in [0, 1]")
    block_labels = args.block_labels if args.block_labels is not None else DEFAULT_BLOCK_LABELS
    warn_labels = args.warn_labels if args.warn_labels is not None else DEFAULT_WARN_LABELS
    out_dir = Path(args.out_dir)
    render_summary, rows, duplicate_labels = build_rows(Path(args.render_summary), Path(args.annotated_sequence))
    summary = build_summary(Path(args.render_summary),
                            Path(args.annotated_sequence),
                            render_summary,
                            rows,
                            duplicate_labels,
                            out_dir,
                            block_labels,
                            warn_labels,
                            args.min_stable_ratio,
                            args.next_text)
    write_csv(out_dir / "water_mesh_surface_quality_gate.csv", rows)
    write_json(out_dir / "water_mesh_surface_quality_gate_summary.json", summary)
    if args.report:
        write_report(Path(args.report), summary, args.title)
    print(f"status={summary['status']}")
    print(f"frames={summary['render_frame_count']}")
    print(f"labels={summary['label_counts']}")
    print(f"component_treatment_noop={summary['component_treatment_noop']}")
    print(f"summary={summary['outputs']['summary']}")
    if args.report:
        print(f"report={args.report}")
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
