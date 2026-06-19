#!/usr/bin/env python3
"""Analyze exported LSFS water reconstruction OBJ mesh quality."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


AREA_EPSILON = 1.0e-12
SHARP_EDGE_DOT = 0.85


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


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def length(v):
    return math.sqrt(max(0.0, dot(v, v)))


def normalize(v):
    l = length(v)
    if l <= 0.0:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


def distance(a, b):
    return length(vec_sub(a, b))


def stat_summary(values):
    clean = [float(v) for v in values if finite(v)]
    if not clean:
        return {"count": 0, "min": None, "mean": None, "max": None, "stddev": None}
    mean = sum(clean) / float(len(clean))
    variance = sum((value - mean) ** 2 for value in clean) / float(len(clean))
    return {
        "count": len(clean),
        "min": min(clean),
        "mean": mean,
        "max": max(clean),
        "stddev": math.sqrt(max(0.0, variance)),
    }


def coefficient_of_variation(values):
    stats = stat_summary(values)
    mean = stats["mean"]
    if mean is None or abs(mean) <= 1.0e-12 or stats["stddev"] is None:
        return None
    return stats["stddev"] / abs(mean)


def percentile(values, q):
    clean = sorted(float(v) for v in values if finite(v))
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    pos = max(0.0, min(1.0, q)) * (len(clean) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return clean[lo]
    t = pos - lo
    return clean[lo] * (1.0 - t) + clean[hi] * t


def parse_face_token(token, vertex_count):
    head = token.split("/", 1)[0]
    if not head:
        return None
    try:
        raw = int(head)
    except ValueError:
        return None
    if raw < 0:
        index = vertex_count + raw
    else:
        index = raw - 1
    return index if 0 <= index < vertex_count else None


def parse_obj(path: Path):
    vertices = []
    normals = []
    faces = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("vn "):
                parts = line.split()
                if len(parts) >= 4:
                    normals.append(normalize((float(parts[1]), float(parts[2]), float(parts[3]))))
            elif line.startswith("f "):
                face = []
                for token in line.split()[1:]:
                    index = parse_face_token(token, len(vertices))
                    if index is not None:
                        face.append(index)
                if len(face) >= 3:
                    faces.append(face)
    return vertices, normals, faces


class DisjointSet:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item):
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def face_geometry(vertices, face):
    p0 = vertices[face[0]]
    area = 0.0
    normal_sum = (0.0, 0.0, 0.0)
    for i in range(1, len(face) - 1):
        a = vec_sub(vertices[face[i]], p0)
        b = vec_sub(vertices[face[i + 1]], p0)
        n = cross(a, b)
        tri_area = 0.5 * length(n)
        area += tri_area
        normal_sum = (
            normal_sum[0] + n[0],
            normal_sum[1] + n[1],
            normal_sum[2] + n[2],
        )
    return area, normalize(normal_sum)


def analyze_mesh(path: Path):
    vertices, normals, faces = parse_obj(path)
    edge_lengths = []
    face_areas = []
    face_normals = []
    edge_faces = defaultdict(list)
    dsu = DisjointSet(len(vertices))
    used_vertices = set()

    for face_index, face in enumerate(faces):
        area, normal = face_geometry(vertices, face)
        face_areas.append(area)
        face_normals.append(normal)
        for vi in face:
            used_vertices.add(vi)
        for i, a in enumerate(face):
            b = face[(i + 1) % len(face)]
            if not (0 <= a < len(vertices) and 0 <= b < len(vertices)):
                continue
            edge_lengths.append(distance(vertices[a], vertices[b]))
            dsu.union(a, b)
            edge_faces[tuple(sorted((a, b)))].append(face_index)

    component_faces = defaultdict(int)
    for face in faces:
        roots = [dsu.find(vi) for vi in face if 0 <= vi < len(vertices)]
        if roots:
            component_faces[roots[0]] += 1
    largest_component_faces = max(component_faces.values()) if component_faces else 0

    shared_edge_discontinuities = []
    sharp_edges = 0
    boundary_edges = 0
    nonmanifold_edges = 0
    for edge, adjacent in edge_faces.items():
        if len(adjacent) == 1:
            boundary_edges += 1
        elif len(adjacent) == 2:
            n0 = face_normals[adjacent[0]]
            n1 = face_normals[adjacent[1]]
            alignment = abs(max(-1.0, min(1.0, dot(n0, n1))))
            shared_edge_discontinuities.append(1.0 - alignment)
            if alignment < SHARP_EDGE_DOT:
                sharp_edges += 1
        else:
            nonmanifold_edges += 1

    face_count = len(faces)
    edge_count = len(edge_faces)
    degenerate_faces = sum(1 for area in face_areas if area <= AREA_EPSILON)
    return {
        "path": str(path),
        "vertex_count": len(vertices),
        "normal_count": len(normals),
        "face_count": face_count,
        "used_vertex_count": len(used_vertices),
        "component_count": len(component_faces),
        "largest_component_face_ratio": (
            largest_component_faces / float(face_count) if face_count else None
        ),
        "edge_count": edge_count,
        "boundary_edge_ratio": boundary_edges / float(edge_count) if edge_count else None,
        "nonmanifold_edge_ratio": nonmanifold_edges / float(edge_count) if edge_count else None,
        "sharp_edge_ratio": sharp_edges / float(max(1, len(shared_edge_discontinuities))),
        "normal_discontinuity_mean": stat_summary(shared_edge_discontinuities)["mean"],
        "normal_discontinuity_p95": percentile(shared_edge_discontinuities, 0.95),
        "edge_length_mean": stat_summary(edge_lengths)["mean"],
        "edge_length_p95": percentile(edge_lengths, 0.95),
        "edge_length_cv": coefficient_of_variation(edge_lengths),
        "face_area_mean": stat_summary(face_areas)["mean"],
        "face_area_p95": percentile(face_areas, 0.95),
        "face_area_cv": coefficient_of_variation(face_areas),
        "degenerate_face_ratio": degenerate_faces / float(face_count) if face_count else None,
    }


def resolve_mesh_path(reconstruction_path: Path, mesh_path: str) -> Path:
    mesh = Path(mesh_path)
    if mesh.is_absolute():
        return mesh
    return (reconstruction_path.parent / mesh).resolve()


def risk_score(row):
    boundary = row.get("boundary_edge_ratio") or 0.0
    nonmanifold = row.get("nonmanifold_edge_ratio") or 0.0
    degenerate = row.get("degenerate_face_ratio") or 0.0
    sharp = row.get("sharp_edge_ratio") or 0.0
    normal = row.get("normal_discontinuity_p95") or 0.0
    edge_cv = row.get("edge_length_cv") or 0.0
    area_cv = row.get("face_area_cv") or 0.0
    fragmentation = 1.0 - (row.get("largest_component_face_ratio") or 0.0)
    return (
        0.2 * min(1.0, boundary * 3.0)
        + 0.15 * min(1.0, nonmanifold * 20.0)
        + 0.15 * min(1.0, degenerate * 100.0)
        + 0.18 * min(1.0, sharp * 2.0)
        + 0.12 * min(1.0, normal * 5.0)
        + 0.1 * min(1.0, edge_cv)
        + 0.06 * min(1.0, area_cv)
        + 0.04 * min(1.0, fragmentation * 20.0)
    )


def build_rows(reconstruction_path: Path, reconstruction):
    rows = []
    for frame in reconstruction.get("frames", []):
        mesh_path = resolve_mesh_path(reconstruction_path, frame.get("mesh", ""))
        metrics = analyze_mesh(mesh_path)
        row = {
            "frame": frame.get("frame"),
            "source_frame": frame.get("source_frame"),
            "source_time": frame.get("source_time"),
            "mesh": str(mesh_path),
            "summary_vertex_count": frame.get("vertex_count"),
            "summary_face_count": frame.get("face_count"),
            "occupied_cell_count": frame.get("occupied_cell_count"),
            **metrics,
        }
        row["mesh_quality_risk_score"] = risk_score(row)
        rows.append(row)
    return rows


def write_csv(path: Path, rows) -> None:
    columns = [
        "frame",
        "source_frame",
        "source_time",
        "summary_vertex_count",
        "summary_face_count",
        "vertex_count",
        "normal_count",
        "face_count",
        "occupied_cell_count",
        "used_vertex_count",
        "component_count",
        "largest_component_face_ratio",
        "edge_count",
        "boundary_edge_ratio",
        "nonmanifold_edge_ratio",
        "sharp_edge_ratio",
        "normal_discontinuity_mean",
        "normal_discontinuity_p95",
        "edge_length_mean",
        "edge_length_p95",
        "edge_length_cv",
        "face_area_mean",
        "face_area_p95",
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
            writer.writerow({key: row.get(key) for key in columns})


def trend(rows, key):
    values = [row.get(key) for row in rows]
    stats = stat_summary(values)
    clean = [float(value) for value in values if finite(value)]
    stats["delta"] = None if len(clean) < 2 else clean[-1] - clean[0]
    return stats


def build_summary(reconstruction_path: Path, rows, out_dir: Path, next_text):
    checks = [
        {
            "name": "frames_present",
            "passed": len(rows) > 0,
            "value": len(rows),
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
        {
            "name": "no_degenerate_faces",
            "passed": all((row.get("degenerate_face_ratio") or 0.0) <= 0.0 for row in rows),
            "value": trend(rows, "degenerate_face_ratio"),
        },
        {
            "name": "normals_present",
            "passed": all((row.get("normal_count") or 0) == (row.get("vertex_count") or 0) for row in rows),
            "value": trend(rows, "normal_count"),
        },
        {
            "name": "single_dominant_component",
            "passed": all((row.get("largest_component_face_ratio") or 0.0) >= 0.98 for row in rows),
            "value": trend(rows, "largest_component_face_ratio"),
        },
        {
            "name": "quality_scores_finite",
            "passed": all(finite(row.get("mesh_quality_risk_score")) for row in rows),
            "value": trend(rows, "mesh_quality_risk_score"),
        },
    ]
    worst = sorted(rows, key=lambda row: row.get("mesh_quality_risk_score") or 0.0, reverse=True)[:8]
    return {
        "schema": "lsfs_water_mesh_quality_diagnostics",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ok" if all(check["passed"] for check in checks) else "warning",
        "inputs": {
            "water_reconstruction": str(reconstruction_path),
        },
        "outputs": {
            "csv": str(out_dir / "water_mesh_quality_profile.csv"),
            "summary": str(out_dir / "water_mesh_quality_summary.json"),
        },
        "frame_count": len(rows),
        "trends": {
            "face_count": trend(rows, "face_count"),
            "occupied_cell_count": trend(rows, "occupied_cell_count"),
            "component_count": trend(rows, "component_count"),
            "largest_component_face_ratio": trend(rows, "largest_component_face_ratio"),
            "boundary_edge_ratio": trend(rows, "boundary_edge_ratio"),
            "nonmanifold_edge_ratio": trend(rows, "nonmanifold_edge_ratio"),
            "sharp_edge_ratio": trend(rows, "sharp_edge_ratio"),
            "normal_discontinuity_p95": trend(rows, "normal_discontinuity_p95"),
            "edge_length_cv": trend(rows, "edge_length_cv"),
            "face_area_cv": trend(rows, "face_area_cv"),
            "degenerate_face_ratio": trend(rows, "degenerate_face_ratio"),
            "mesh_quality_risk_score": trend(rows, "mesh_quality_risk_score"),
        },
        "worst_frames": worst,
        "sanity_checks": checks,
        "findings": [
            "This diagnostic reads exported OBJ meshes directly, so it can catch surface-data issues that bridge-summary frame metrics cannot see.",
            "High boundary or component fragmentation points toward export/reconstruction topology work, while high normal discontinuity points toward normal or smoothing metadata.",
            "Use the worst frames to choose whether S198 should continue into cache-side normal/gradient export or a reconstruction smoothing variant.",
        ],
        "next_recommendation": next_text or "Use this OBJ-level quality profile to choose the next reconstruction/export smoothing pass.",
    }


def markdown_value(value):
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def write_report(path: Path, summary, title) -> None:
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
        f"- CSV profile: `{summary['outputs']['csv']}`",
        f"- JSON summary: `{summary['outputs']['summary']}`",
        "",
        "## Trend Summary",
        "",
        "| Trend | Count | Min | Mean | Max | Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, stat in summary["trends"].items():
        lines.append(
            f"| `{key}` | {stat['count']} | {markdown_value(stat['min'])} | "
            f"{markdown_value(stat['mean'])} | {markdown_value(stat['max'])} | "
            f"{markdown_value(stat.get('delta'))} |"
        )
    lines.extend([
        "",
        "## Worst Mesh Frames",
        "",
        "| Rank | Frame | Source frame | Score | Faces | Components | Largest comp | Boundary edge | Sharp edge | Normal p95 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for rank, row in enumerate(summary["worst_frames"], 1):
        lines.append(
            f"| {rank} | {row.get('frame')} | {row.get('source_frame')} | "
            f"{markdown_value(row.get('mesh_quality_risk_score'))} | "
            f"{markdown_value(row.get('face_count'))} | "
            f"{markdown_value(row.get('component_count'))} | "
            f"{markdown_value(row.get('largest_component_face_ratio'))} | "
            f"{markdown_value(row.get('boundary_edge_ratio'))} | "
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


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("water_reconstruction", help="water_reconstruction.json")
    parser.add_argument("--out-dir", required=True, help="Output diagnostic directory")
    parser.add_argument("--report", help="Optional Markdown report path")
    parser.add_argument("--title", default="Water Mesh Quality Diagnostics")
    parser.add_argument("--next", dest="next_text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reconstruction_path = Path(args.water_reconstruction)
    out_dir = Path(args.out_dir)
    reconstruction = read_json(reconstruction_path)
    if reconstruction.get("reconstructor") != "lsfs_water_reconstruction":
        raise RuntimeError(f"{reconstruction_path}: not an LSFS water reconstruction index")
    rows = build_rows(reconstruction_path, reconstruction)
    csv_path = out_dir / "water_mesh_quality_profile.csv"
    json_path = out_dir / "water_mesh_quality_summary.json"
    write_csv(csv_path, rows)
    summary = build_summary(reconstruction_path, rows, out_dir, args.next_text)
    write_json(json_path, summary)
    if args.report:
        write_report(Path(args.report), summary, args.title)
    print(f"status={summary['status']}")
    print(f"frames={summary['frame_count']}")
    print(f"csv={csv_path}")
    print(f"summary={json_path}")
    if args.report:
        print(f"report={args.report}")
    return 0 if summary["status"] in ("ok", "warning") else 1


if __name__ == "__main__":
    raise SystemExit(main())
