#!/usr/bin/env python
"""Export coarse water meshes from LSFS 3D render cache phase cells.

This S41 tool is intentionally dependency-free. It thresholds phase cells into
occupied voxels, exports exposed faces as OBJ quads, and writes a movable
water_reconstruction.json index.

Usage:
  python tools/reconstruct_water.py <manifest.json|sequence.json|frame.jsonl> <out_dir> --frames 8
"""

import argparse
import csv
import json
import math
import os
import sys


class ReconstructionError(Exception):
    pass


def fail(message):
    raise ReconstructionError(message)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")


def read_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"{path}:{line_no}: invalid JSON: {exc}")
            if not isinstance(rec, dict):
                fail(f"{path}:{line_no}: expected object record")
            records.append(rec)
    if not records:
        fail(f"{path}: empty JSONL frame")
    return records


def resolve_path(base_dir, path):
    if os.path.isabs(path):
        return path
    candidate = os.path.join(base_dir, path)
    if os.path.isfile(candidate):
        return candidate
    return path


def relpath(path, base_dir):
    return os.path.relpath(path, base_dir).replace(os.sep, "/")


def as_float(value, fallback=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def as_int(value, fallback=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def section(records, name):
    for rec in records:
        if rec.get("section") == name:
            return rec
    return None


def sections(records, name):
    return [rec for rec in records if rec.get("section") == name]


def read_phase_csv(path):
    cells = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            cells.append({
                "i": as_int(row.get("i")),
                "j": as_int(row.get("j")),
                "k": as_int(row.get("k")),
                "level": as_int(row.get("level")),
                "marker": as_int(row.get("marker")),
                "phi": as_float(row.get("phi")),
                "liquid_volume": as_float(row.get("liquid_volume")),
            })
    return cells


def normalize_frame(source, header, cells):
    dims = header.get("dims", [1, 1, 1])
    return {
        "source": source,
        "frame": as_int(header.get("frame"), 0),
        "time": as_float(header.get("time"), 0.0),
        "dims": [as_int(dims[0], 1), as_int(dims[1], 1), as_int(dims[2], 1)],
        "dx": max(1e-12, as_float(header.get("dx"), 1.0)),
        "phase_cells": cells,
    }


def load_jsonl_frame(path, display_path=None):
    records = read_jsonl(path)
    header = section(records, "header")
    if header is None:
        fail(f"{path}: missing header")
    return normalize_frame(display_path or path, header, sections(records, "phase_cell"))


def load_manifest(path):
    data = read_json(path)
    if data.get("lsfs_cache3d_manifest_version") != 1:
        fail(f"{path}: not an LSFS render cache manifest")
    base_dir = os.path.dirname(os.path.abspath(path))
    frames = []
    for entry in data.get("frames", []):
        frame_path = resolve_path(base_dir, entry.get("path", ""))
        if not os.path.isfile(frame_path):
            fail(f"{path}: missing frame {entry.get('path')!r}")
        frames.append(load_jsonl_frame(frame_path, entry.get("path", frame_path)))
    if not frames:
        fail(f"{path}: manifest contains no frames")
    return frames


def load_sequence(path):
    data = read_json(path)
    if data.get("converter") != "lsfs_render_cache_converter":
        fail(f"{path}: not an LSFS converted sequence")
    base_dir = os.path.dirname(os.path.abspath(path))
    frames = []
    for entry in data.get("frames", []):
        camera_path = resolve_path(base_dir, entry.get("camera", ""))
        phase_path = resolve_path(base_dir, entry.get("phase_cells", ""))
        if not os.path.isfile(camera_path):
            fail(f"{path}: missing camera file {entry.get('camera')!r}")
        if not os.path.isfile(phase_path):
            fail(f"{path}: missing phase cells file {entry.get('phase_cells')!r}")
        camera_payload = read_json(camera_path)
        header = camera_payload.get("header", {})
        frames.append(normalize_frame(entry.get("source_cache", phase_path),
                                      header,
                                      read_phase_csv(phase_path)))
    if not frames:
        fail(f"{path}: sequence contains no frames")
    return frames


def load_source(path):
    if not os.path.isfile(path):
        fail(f"{path}: input not found")
    if path.lower().endswith(".jsonl"):
        return [load_jsonl_frame(path)]
    data = read_json(path)
    if data.get("lsfs_cache3d_manifest_version") == 1:
        return load_manifest(path)
    if data.get("converter") == "lsfs_render_cache_converter":
        return load_sequence(path)
    fail(f"{path}: expected manifest, sequence.json, or JSONL frame")


def occupied_voxels(frame, threshold):
    occupied = set()
    dx = frame["dx"]
    cell_volume = dx * dx * dx
    for cell in frame["phase_cells"]:
        phi = max(0.0, as_float(cell.get("phi")))
        liquid_volume = max(0.0, as_float(cell.get("liquid_volume")))
        if phi < threshold and liquid_volume <= threshold * cell_volume:
            continue
        step = 1 << max(0, as_int(cell.get("level"), 0))
        i0 = as_int(cell.get("i"))
        j0 = as_int(cell.get("j"))
        k0 = as_int(cell.get("k"))
        for dz in range(step):
            for dy in range(step):
                for dx_i in range(step):
                    occupied.add((i0 + dx_i, j0 + dy, k0 + dz))
    return occupied


FACE_DEFS = [
    ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
    ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
    ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
]


def build_surface_mesh(frame, occupied):
    dx = frame["dx"]
    vertices = []
    faces = []
    vertex_index = {}

    def add_vertex(coord):
        if coord in vertex_index:
            return vertex_index[coord]
        x, y, z = coord
        vertices.append((x * dx, y * dx, z * dx))
        vertex_index[coord] = len(vertices)
        return len(vertices)

    for i, j, k in sorted(occupied):
        for normal, corners in FACE_DEFS:
            ni = i + normal[0]
            nj = j + normal[1]
            nk = k + normal[2]
            if (ni, nj, nk) in occupied:
                continue
            face = [add_vertex((i + cx, j + cy, k + cz)) for cx, cy, cz in corners]
            faces.append(face)

    return vertices, faces


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def normalize(v):
    length = math.sqrt(max(0.0, v[0] * v[0] + v[1] * v[1] + v[2] * v[2]))
    if length <= 1e-12:
        return (0.0, 1.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def build_adjacency(vertex_count, faces):
    neighbors = [set() for _ in range(vertex_count)]
    for face in faces:
        zero = [idx - 1 for idx in face]
        for a, b in zip(zero, zero[1:] + zero[:1]):
            if 0 <= a < vertex_count and 0 <= b < vertex_count:
                neighbors[a].add(b)
                neighbors[b].add(a)
    return neighbors


def smooth_vertices(vertices, faces, iterations, alpha):
    if iterations <= 0 or alpha <= 0.0 or not vertices:
        return vertices
    alpha = min(1.0, max(0.0, alpha))
    neighbors = build_adjacency(len(vertices), faces)
    current = list(vertices)
    for _ in range(iterations):
        updated = []
        for idx, vertex in enumerate(current):
            linked = neighbors[idx]
            if not linked:
                updated.append(vertex)
                continue
            avg = (
                sum(current[n][0] for n in linked) / len(linked),
                sum(current[n][1] for n in linked) / len(linked),
                sum(current[n][2] for n in linked) / len(linked),
            )
            updated.append((
                vertex[0] * (1.0 - alpha) + avg[0] * alpha,
                vertex[1] * (1.0 - alpha) + avg[1] * alpha,
                vertex[2] * (1.0 - alpha) + avg[2] * alpha,
            ))
        current = updated
    return current


def compute_vertex_normals(vertices, faces):
    normals = [(0.0, 0.0, 0.0) for _ in vertices]
    for face in faces:
        if len(face) < 3:
            continue
        i0, i1, i2 = face[0] - 1, face[1] - 1, face[2] - 1
        if not (0 <= i0 < len(vertices) and 0 <= i1 < len(vertices) and 0 <= i2 < len(vertices)):
            continue
        edge_a = vec_sub(vertices[i1], vertices[i0])
        edge_b = vec_sub(vertices[i2], vertices[i0])
        n = cross(edge_a, edge_b)
        for idx in face:
            vi = idx - 1
            if 0 <= vi < len(normals):
                prev = normals[vi]
                normals[vi] = (prev[0] + n[0], prev[1] + n[1], prev[2] + n[2])
    return [normalize(n) for n in normals]


def write_obj(path, frame, vertices, faces, write_normals):
    normals = compute_vertex_normals(vertices, faces) if write_normals else []
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# LSFS S41 water reconstruction OBJ\n")
        f.write(f"# source {frame['source']}\n")
        f.write(f"# frame {frame['frame']} time {frame['time']:.17g}\n")
        for x, y, z in vertices:
            f.write(f"v {x:.17g} {y:.17g} {z:.17g}\n")
        for x, y, z in normals:
            f.write(f"vn {x:.17g} {y:.17g} {z:.17g}\n")
        f.write("g water\n")
        for face in faces:
            if write_normals:
                f.write("f " + " ".join(f"{idx}//{idx}" for idx in face) + "\n")
            else:
                f.write("f " + " ".join(str(idx) for idx in face) + "\n")
    return len(vertices), len(faces), len(normals)


def select_source_frame(frames, out_index, out_count):
    if out_count <= 1 or len(frames) == 1:
        return frames[0]
    src_index = round(out_index * (len(frames) - 1) / max(1, out_count - 1))
    return frames[src_index]


def reconstruct(src, out_dir, frame_count, threshold,
                smooth_iterations=0, smooth_alpha=0.18, write_normals=False):
    frames = load_source(src)
    out_dir = os.path.abspath(out_dir)
    mesh_dir = os.path.join(out_dir, "meshes")
    os.makedirs(mesh_dir, exist_ok=True)

    output_frames = []
    for out_index in range(frame_count):
        frame = select_source_frame(frames, out_index, frame_count)
        occupied = occupied_voxels(frame, threshold)
        if not occupied:
            fail(f"{frame['source']}: no occupied water cells at threshold {threshold}")
        mesh_path = os.path.join(mesh_dir, f"frame_{out_index:04d}_water.obj")
        vertices, faces = build_surface_mesh(frame, occupied)
        vertices = smooth_vertices(vertices, faces, smooth_iterations, smooth_alpha)
        vertex_count, face_count, normal_count = write_obj(mesh_path, frame, vertices, faces, write_normals)
        output_frames.append({
            "frame": out_index,
            "source_frame": frame["frame"],
            "source_time": frame["time"],
            "source_cache": frame["source"],
            "mesh": relpath(mesh_path, out_dir),
            "occupied_cell_count": len(occupied),
            "vertex_count": vertex_count,
            "face_count": face_count,
            "normal_count": normal_count,
        })

    summary = {
        "reconstructor": "lsfs_water_reconstruction",
        "version": 1,
        "representation": "obj_mesh",
        "source": src,
        "threshold": threshold,
        "smooth_iterations": smooth_iterations,
        "smooth_alpha": smooth_alpha,
        "write_normals": write_normals,
        "frame_count": len(output_frames),
        "frames": output_frames,
    }
    summary_path = os.path.join(out_dir, "water_reconstruction.json")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    return summary_path, summary


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Export LSFS water reconstruction OBJ meshes")
    parser.add_argument("src", help="render cache manifest, converted sequence.json, or JSONL frame")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--frames", type=int, default=8, help="number of OBJ frames to write")
    parser.add_argument("--threshold", type=float, default=0.02,
                        help="minimum phase-cell phi or liquid-volume fraction")
    parser.add_argument("--smooth-iterations", type=int, default=0,
                        help="Laplacian smoothing iterations for exported vertices")
    parser.add_argument("--smooth-alpha", type=float, default=0.18,
                        help="smoothing blend factor per iteration")
    parser.add_argument("--write-normals", action="store_true",
                        help="write one OBJ vertex normal per vertex")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.threshold < 0.0 or not math.isfinite(args.threshold):
        parser.error("threshold must be finite and non-negative")
    if args.smooth_iterations < 0:
        parser.error("smooth-iterations must be non-negative")
    if args.smooth_alpha < 0.0 or args.smooth_alpha > 1.0 or not math.isfinite(args.smooth_alpha):
        parser.error("smooth-alpha must be finite in [0, 1]")
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary_path, summary = reconstruct(args.src,
                                            args.out_dir,
                                            args.frames,
                                            args.threshold,
                                            smooth_iterations=args.smooth_iterations,
                                            smooth_alpha=args.smooth_alpha,
                                            write_normals=args.write_normals)
    except ReconstructionError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1
    print(f"frames={summary['frame_count']}")
    print(f"representation={summary['representation']}")
    print(f"summary={summary_path}")
    print("status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
