#!/usr/bin/env python
"""Attach water mesh surface-quality metadata to a Mitsuba export manifest."""

import argparse
import csv
import os
from collections import Counter
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


QUALITY_FIELDS = (
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
)


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def path_keys(path, root):
    resolved = resolve_path(path)
    if not resolved:
        return []
    keys = {resolved.replace(os.sep, "/").lower()}
    try:
        keys.add(os.path.relpath(resolved, root).replace(os.sep, "/").lower())
    except ValueError:
        pass
    keys.add(os.path.basename(resolved).lower())
    return sorted(keys)


def quality_payload(row, root):
    payload = {
        "schema": "lsfs_water_mesh_surface_quality_frame",
        "frame": as_int(row.get("frame")),
        "source_frame": as_int(row.get("source_frame")),
        "source_time": as_float(row.get("source_time")),
        "label": row.get("label") or "unknown",
        "mesh_repo_path": posix_rel(resolve_path(row.get("mesh")), root) if row.get("mesh") else None,
    }
    for field in QUALITY_FIELDS:
        if field in ("frame", "source_frame", "source_time", "label", "mesh"):
            continue
        payload[field] = as_float(row.get(field))
    return payload


def load_quality_csv(path, root):
    by_key = {}
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            payload = quality_payload(row, root)
            rows.append(payload)
            for key in path_keys(row.get("mesh"), root):
                by_key[key] = payload
    return rows, by_key


def find_quality(frame, by_key, root):
    water_mesh = frame.get("water_mesh") or {}
    for value in (water_mesh.get("path"), water_mesh.get("repo_path")):
        for key in path_keys(value, root):
            found = by_key.get(key)
            if found:
                return found
    return None


def metric_max(frames, key):
    values = [
        ((frame.get("water_mesh") or {}).get("surface_quality") or {}).get(key)
        for frame in frames
    ]
    clean = [float(value) for value in values if isinstance(value, (int, float))]
    return max(clean) if clean else None


def markdown_report(summary, summary_path, root, next_text):
    checks = summary["checks"]
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Annotated export: `{summary['annotated_export']['repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Annotated frames: `{checks.get('annotated_frames')}`",
        f"- Missing quality frames: `{checks.get('missing_quality_frames')}`",
        f"- Label counts: `{checks.get('label_counts')}`",
        f"- Max normal discontinuity p95: `{checks.get('max_normal_discontinuity_p95')}`",
        f"- Max mesh quality risk score: `{checks.get('max_mesh_quality_risk_score')}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Sequence | Mesh | Label | Normal p95 | Risk |",
        "| ---: | ---: | --- | --- | ---: | ---: |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        quality = ((frame.get("water_mesh") or {}).get("surface_quality") or {})
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('sequence_frame')} | "
            f"`{(frame.get('water_mesh') or {}).get('repo_path')}` | `{quality.get('label')}` | "
            f"{quality.get('normal_discontinuity_p95')} | {quality.get('mesh_quality_risk_score')} |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def annotate(args):
    root = os.getcwd()
    export_path = require_file(args.mitsuba_export, "Mitsuba export")
    quality_csv_path = require_file(args.surface_quality_csv, "surface quality CSV")
    export = read_json(export_path)
    if export.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.mitsuba_export}: expected lsfs_mitsuba_xml_export schema")
    quality_rows, quality_by_key = load_quality_csv(quality_csv_path, root)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    annotated_path = os.path.join(out_dir, "mitsuba_export_surface_quality.json")
    summary_path = os.path.join(out_dir, "mitsuba_export_surface_quality_summary.json")

    annotated = dict(export)
    frames = []
    missing = []
    labels = Counter()
    for frame in export.get("frames") or []:
        out_frame = dict(frame)
        water_mesh = dict(out_frame.get("water_mesh") or {})
        quality = find_quality(frame, quality_by_key, root)
        if quality:
            water_mesh["surface_quality"] = quality
            labels[quality.get("label") or "unknown"] += 1
        else:
            missing.append(frame.get("output_frame"))
        out_frame["water_mesh"] = water_mesh
        frames.append(out_frame)
    annotated["frames"] = frames
    annotated["surface_quality_annotation"] = {
        "schema": "lsfs_mitsuba_export_surface_quality_annotation",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_export": posix_rel(export_path, root),
        "surface_quality_csv": posix_rel(quality_csv_path, root),
        "quality_rows": len(quality_rows),
        "annotated_frames": len(frames) - len(missing),
        "missing_quality_frames": missing,
        "label_counts": dict(sorted(labels.items())),
    }
    write_json(annotated_path, annotated)
    annotated_sha = sha256_file(annotated_path)
    checks = {
        "frames": len(frames),
        "annotated_frames": len(frames) - len(missing),
        "missing_quality_frames": len(missing),
        "label_counts": dict(sorted(labels.items())),
        "max_normal_discontinuity_p95": metric_max(frames, "normal_discontinuity_p95"),
        "max_mesh_quality_risk_score": metric_max(frames, "mesh_quality_risk_score"),
    }
    summary = {
        "schema": "lsfs_mitsuba_export_surface_quality_annotation_summary",
        "version": 1,
        "generated_utc": annotated["surface_quality_annotation"]["generated_utc"],
        "title": args.title,
        "status": "ready" if not missing else "missing_quality",
        "source": {
            "mitsuba_export": posix_rel(export_path, root),
            "surface_quality_csv": posix_rel(quality_csv_path, root),
        },
        "annotated_export": {
            "path": annotated_path,
            "repo_path": posix_rel(annotated_path, root),
            "sha256": annotated_sha,
            "size": os.path.getsize(annotated_path),
        },
        "checks": checks,
        "frames": frames,
        "next": args.next,
    }
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} frames={checks['frames']} annotated={checks['annotated_frames']} "
        f"missing={checks['missing_quality_frames']} labels={checks['label_counts']} summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Annotate a Mitsuba export with water mesh surface quality")
    parser.add_argument("mitsuba_export", help="lsfs_mitsuba_xml_export manifest")
    parser.add_argument("surface_quality_csv", help="water_mesh_surface_quality_profile.csv")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Export Surface Quality Annotation")
    parser.add_argument("--next", default="Use annotated water-mesh quality as frame-level material evidence, or add per-pixel normal/contact masks if frame-level evidence is too coarse.")
    return parser.parse_args()


if __name__ == "__main__":
    annotate(parse_args())
