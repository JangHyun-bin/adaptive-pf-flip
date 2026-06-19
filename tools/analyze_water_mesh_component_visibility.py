#!/usr/bin/env python3
"""Diagnose whether water mesh components selected for a render are visible."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
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


def as_float(value, fallback=0.0):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return fallback
    return out if math.isfinite(out) else fallback


def as_int(value, fallback=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def vec3(value, fallback=(0.0, 0.0, 0.0)):
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return [as_float(value[0]), as_float(value[1]), as_float(value[2])]
    return [fallback[0], fallback[1], fallback[2]]


def v_sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def v_dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def v_cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def v_len(a):
    return math.sqrt(max(0.0, v_dot(a, a)))


def v_norm(a, fallback=(0.0, 0.0, 1.0)):
    length = v_len(a)
    if length <= 1.0e-12:
        return [fallback[0], fallback[1], fallback[2]]
    return [a[i] / length for i in range(3)]


def to_blender_coords(point):
    return [as_float(point[0]), -as_float(point[2]), as_float(point[1])]


def project_camera_point(point, camera, width, height):
    position = to_blender_coords(vec3(camera.get("position"), (0.0, 0.0, 1.0)))
    target = to_blender_coords(vec3(camera.get("target"), (0.0, 0.0, 0.0)))
    up = to_blender_coords(vec3(camera.get("up"), (0.0, 1.0, 0.0)))
    forward = v_norm(v_sub(target, position), (0.0, 0.0, -1.0))
    right = v_norm(v_cross(forward, up), (1.0, 0.0, 0.0))
    true_up = v_norm(v_cross(right, forward), (0.0, 0.0, 1.0))
    rel = v_sub(to_blender_coords(point), position)
    depth = v_dot(rel, forward)
    if depth <= max(1e-6, as_float(camera.get("near_clip"), 0.05)):
        return None
    vfov = math.radians(max(1e-6, as_float(camera.get("vertical_fov_degrees"), 45.0)))
    aspect = max(1e-6, float(width) / float(max(1, height)))
    half_y = math.tan(vfov * 0.5)
    half_x = half_y * aspect
    x = v_dot(rel, right) / (depth * half_x)
    y = v_dot(rel, true_up) / (depth * half_y)
    return {
        "x": (x + 1.0) * 0.5,
        "y": (y + 1.0) * 0.5,
        "depth": depth,
    }


def parse_face_token(token, vertex_count):
    head = token.split("/", 1)[0]
    if not head:
        return None
    try:
        raw = int(head)
    except ValueError:
        return None
    index = vertex_count + raw if raw < 0 else raw - 1
    return index if 0 <= index < vertex_count else None


def parse_obj(path: Path):
    vertices = []
    faces = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                face = []
                for token in line.split()[1:]:
                    index = parse_face_token(token, len(vertices))
                    if index is not None:
                        face.append(index)
                if len(face) >= 3:
                    faces.append(face)
    return vertices, faces


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


def mesh_components(vertices, faces):
    dsu = DisjointSet(len(vertices))
    for face in faces:
        if not face:
            continue
        root = face[0]
        for vi in face[1:]:
            dsu.union(root, vi)
    components = {}
    for face_index, face in enumerate(faces):
        if not face:
            continue
        root = dsu.find(face[0])
        item = components.setdefault(root, {"face_indices": [], "vertices": set()})
        item["face_indices"].append(face_index)
        item["vertices"].update(face)
    out = []
    for root, item in components.items():
        out.append({
            "root": root,
            "face_count": len(item["face_indices"]),
            "vertex_indices": sorted(item["vertices"]),
        })
    out.sort(key=lambda item: (item["face_count"], len(item["vertex_indices"])), reverse=True)
    face_count = max(1, len(faces))
    vertex_count = max(1, len(vertices))
    for index, item in enumerate(out):
        item["rank"] = index + 1
        item["face_ratio"] = item["face_count"] / float(face_count)
        item["vertex_ratio"] = len(item["vertex_indices"]) / float(vertex_count)
    return out


def mesh_frame_index(path):
    match = re.search(r"frame_(\d+)_water\.obj$", str(path).replace("\\", "/"))
    return int(match.group(1)) if match else None


def resolve_mesh(reconstruction_path: Path, frame):
    mesh = Path(frame.get("mesh", ""))
    if mesh.is_absolute():
        return mesh
    return (reconstruction_path.parent / mesh).resolve()


def reconstruction_meshes(reconstruction_path: Path):
    data = read_json(reconstruction_path)
    if data.get("reconstructor") != "lsfs_water_reconstruction":
        raise RuntimeError(f"{reconstruction_path}: not an LSFS water reconstruction index")
    meshes = {}
    for frame in data.get("frames", []):
        index = as_int(frame.get("frame"), len(meshes))
        meshes[index] = {
            "path": resolve_mesh(reconstruction_path, frame),
            "source_frame": frame.get("source_frame"),
            "source_time": frame.get("source_time"),
        }
    return meshes


def component_visibility(component, vertices, camera, width, height):
    projected = []
    inside = 0
    depths = []
    for vi in component["vertex_indices"]:
        item = project_camera_point(vertices[vi], camera, width, height)
        if item is None:
            continue
        projected.append(item)
        depths.append(item["depth"])
        if 0.0 <= item["x"] <= 1.0 and 0.0 <= item["y"] <= 1.0:
            inside += 1
    if not projected:
        return {
            "projected_vertex_count": 0,
            "inside_vertex_count": 0,
            "inside_vertex_ratio": 0.0,
            "screen_min_x": None,
            "screen_max_x": None,
            "screen_min_y": None,
            "screen_max_y": None,
            "clipped_screen_area": 0.0,
            "mean_depth": None,
        }
    xs = [item["x"] for item in projected]
    ys = [item["y"] for item in projected]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    clipped_w = max(0.0, min(1.0, max_x) - max(0.0, min_x))
    clipped_h = max(0.0, min(1.0, max_y) - max(0.0, min_y))
    return {
        "projected_vertex_count": len(projected),
        "inside_vertex_count": inside,
        "inside_vertex_ratio": inside / float(max(1, len(component["vertex_indices"]))),
        "screen_min_x": min_x,
        "screen_max_x": max_x,
        "screen_min_y": min_y,
        "screen_max_y": max_y,
        "clipped_screen_area": clipped_w * clipped_h,
        "mean_depth": sum(depths) / float(len(depths)) if depths else None,
    }


def build_rows(scene_spec_path: Path, reconstruction_path: Path, filter_threshold):
    spec = read_json(scene_spec_path)
    width = as_int(spec.get("width"), 1280)
    height = as_int(spec.get("height"), 720)
    meshes = reconstruction_meshes(reconstruction_path)
    mesh_cache = {}
    rows = []
    for frame in spec.get("frames", []):
        selected_index = mesh_frame_index(frame.get("water_mesh", ""))
        if selected_index is None or selected_index not in meshes:
            continue
        mesh_path = meshes[selected_index]["path"]
        if mesh_path not in mesh_cache:
            vertices, faces = parse_obj(mesh_path)
            mesh_cache[mesh_path] = (vertices, faces, mesh_components(vertices, faces))
        vertices, faces, components = mesh_cache[mesh_path]
        for component in components:
            visibility = component_visibility(component, vertices, frame.get("camera", {}), width, height)
            would_filter = component["face_ratio"] < filter_threshold
            rows.append({
                "render_frame": frame.get("index"),
                "render_source_frame": (frame.get("render_data") or {}).get("source_frame"),
                "selected_mesh_frame": selected_index,
                "water_source_frame": meshes[selected_index].get("source_frame"),
                "component_rank": component["rank"],
                "component_count": len(components),
                "face_count": component["face_count"],
                "face_ratio": component["face_ratio"],
                "vertex_count": len(component["vertex_indices"]),
                "vertex_ratio": component["vertex_ratio"],
                "would_filter": would_filter,
                **visibility,
            })
    return rows


def stat(values):
    clean = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    if not clean:
        return {"count": 0, "min": None, "mean": None, "max": None}
    return {
        "count": len(clean),
        "min": min(clean),
        "mean": sum(clean) / float(len(clean)),
        "max": max(clean),
    }


def write_csv(path: Path, rows) -> None:
    columns = [
        "render_frame",
        "render_source_frame",
        "selected_mesh_frame",
        "water_source_frame",
        "component_rank",
        "component_count",
        "face_count",
        "face_ratio",
        "vertex_count",
        "vertex_ratio",
        "would_filter",
        "projected_vertex_count",
        "inside_vertex_count",
        "inside_vertex_ratio",
        "screen_min_x",
        "screen_max_x",
        "screen_min_y",
        "screen_max_y",
        "clipped_screen_area",
        "mean_depth",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in columns})


def build_summary(scene_spec_path: Path, reconstruction_path: Path, rows, out_dir: Path, filter_threshold, next_text):
    selected_mesh_frames = sorted({row["selected_mesh_frame"] for row in rows})
    would_filter_rows = [row for row in rows if row.get("would_filter")]
    visible_filtered = [
        row for row in would_filter_rows
        if (row.get("inside_vertex_count") or 0) > 0 or (row.get("clipped_screen_area") or 0.0) > 0.0
    ]
    selected_filtered_frames = sorted({row["selected_mesh_frame"] for row in would_filter_rows})
    return {
        "schema": "lsfs_water_mesh_component_visibility",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ok",
        "inputs": {
            "scene_spec": str(scene_spec_path),
            "water_reconstruction": str(reconstruction_path),
        },
        "outputs": {
            "csv": str(out_dir / "water_mesh_component_visibility.csv"),
            "summary": str(out_dir / "water_mesh_component_visibility_summary.json"),
        },
        "filter_threshold": filter_threshold,
        "render_frame_count": len({row["render_frame"] for row in rows}),
        "selected_mesh_frames": selected_mesh_frames,
        "component_rows": len(rows),
        "selected_component_count": stat(row.get("component_count") for row in rows if row.get("component_rank") == 1),
        "would_filter_component_rows": len(would_filter_rows),
        "visible_would_filter_component_rows": len(visible_filtered),
        "selected_mesh_frames_with_filtered_components": selected_filtered_frames,
        "inside_vertex_ratio": stat(row.get("inside_vertex_ratio") for row in rows),
        "clipped_screen_area": stat(row.get("clipped_screen_area") for row in rows),
        "worst_filtered_components": sorted(
            would_filter_rows,
            key=lambda row: (row.get("clipped_screen_area") or 0.0, row.get("inside_vertex_ratio") or 0.0),
            reverse=True)[:8],
        "findings": [
            "This diagnostic uses the final Blender scene spec, so source-window and camera-motion choices are included.",
            "If no selected mesh frames contain would-filter components, an island filter can be pixel-identical even when it changes the full reconstruction.",
            "Visible would-filter components should be reviewed before enabling pruning in production renders.",
        ],
        "next_recommendation": next_text or "Use these rows to decide whether component filtering needs a different review window or visible labels.",
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
        f"- Scene spec: `{summary['inputs']['scene_spec']}`",
        f"- Water reconstruction: `{summary['inputs']['water_reconstruction']}`",
        f"- Filter threshold: `{summary['filter_threshold']}`",
        "",
        "## Outputs",
        "",
        f"- CSV: `{summary['outputs']['csv']}`",
        f"- JSON: `{summary['outputs']['summary']}`",
        "",
        "## Summary",
        "",
        f"- Render frames: `{summary['render_frame_count']}`",
        f"- Selected mesh frames: `{summary['selected_mesh_frames']}`",
        f"- Component rows: `{summary['component_rows']}`",
        f"- Would-filter component rows: `{summary['would_filter_component_rows']}`",
        f"- Visible would-filter component rows: `{summary['visible_would_filter_component_rows']}`",
        f"- Selected mesh frames with filtered components: `{summary['selected_mesh_frames_with_filtered_components']}`",
        f"- Inside vertex ratio: `{summary['inside_vertex_ratio']}`",
        f"- Clipped screen area: `{summary['clipped_screen_area']}`",
        "",
        "## Filtered Components",
        "",
        "| Rank | Render frame | Mesh frame | Component | Face ratio | Inside ratio | Clipped area | Screen x | Screen y |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for rank, row in enumerate(summary["worst_filtered_components"], 1):
        lines.append(
            f"| {rank} | {row.get('render_frame')} | {row.get('selected_mesh_frame')} | "
            f"{row.get('component_rank')} | {markdown_value(row.get('face_ratio'))} | "
            f"{markdown_value(row.get('inside_vertex_ratio'))} | "
            f"{markdown_value(row.get('clipped_screen_area'))} | "
            f"{markdown_value(row.get('screen_min_x'))}..{markdown_value(row.get('screen_max_x'))} | "
            f"{markdown_value(row.get('screen_min_y'))}..{markdown_value(row.get('screen_max_y'))} |"
        )
    if not summary["worst_filtered_components"]:
        lines.append("| | | | | | | | | |")
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
    parser.add_argument("scene_spec", help="Blender bridge scene spec JSON")
    parser.add_argument("water_reconstruction", help="reference water_reconstruction.json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--filter-threshold", type=float, default=0.24)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Water Mesh Component Visibility Diagnostics")
    parser.add_argument("--next", dest="next_text")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.filter_threshold < 0.0 or args.filter_threshold >= 1.0:
        raise RuntimeError("--filter-threshold must be in [0, 1)")
    scene_spec_path = Path(args.scene_spec)
    reconstruction_path = Path(args.water_reconstruction)
    out_dir = Path(args.out_dir)
    rows = build_rows(scene_spec_path, reconstruction_path, args.filter_threshold)
    csv_path = out_dir / "water_mesh_component_visibility.csv"
    json_path = out_dir / "water_mesh_component_visibility_summary.json"
    write_csv(csv_path, rows)
    summary = build_summary(scene_spec_path, reconstruction_path, rows, out_dir,
                            args.filter_threshold, args.next_text)
    write_json(json_path, summary)
    if args.report:
        write_report(Path(args.report), summary, args.title)
    print(f"status={summary['status']}")
    print(f"render_frames={summary['render_frame_count']}")
    print(f"would_filter_components={summary['would_filter_component_rows']}")
    print(f"visible_would_filter_components={summary['visible_would_filter_component_rows']}")
    print(f"csv={csv_path}")
    print(f"summary={json_path}")
    if args.report:
        print(f"report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
