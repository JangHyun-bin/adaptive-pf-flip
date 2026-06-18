#!/usr/bin/env python
"""Export coarse water meshes from LSFS 3D render cache phase cells.

This S41 tool is intentionally dependency-free. It thresholds phase cells into
occupied voxels, exports exposed faces as OBJ quads, and writes a movable
water_reconstruction.json index.

Usage:
  python tools/reconstruct_water.py <manifest.json|sequence.json|frame.jsonl> <out_dir> --frames 8
  python tools/reconstruct_water.py <manifest.json> <out_dir> --frames 8 --reuse-if-fresh
"""

import argparse
import csv
import hashlib
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


def write_json(path, payload):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_fingerprint(role, path, **extra):
    abs_path = os.path.abspath(path)
    payload = {
        "role": role,
        "path": abs_path,
        "bytes": os.path.getsize(abs_path),
        "sha256": sha256_file(abs_path),
    }
    payload.update(extra)
    return payload


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


def normalize_frame(source, header, cells, fingerprint_paths=None):
    dims = header.get("dims", [1, 1, 1])
    return {
        "source": source,
        "frame": as_int(header.get("frame"), 0),
        "time": as_float(header.get("time"), 0.0),
        "dims": [as_int(dims[0], 1), as_int(dims[1], 1), as_int(dims[2], 1)],
        "dx": max(1e-12, as_float(header.get("dx"), 1.0)),
        "phase_cells": cells,
        "fingerprint_paths": [os.path.abspath(path) for path in (fingerprint_paths or [])],
    }


def load_jsonl_frame(path, display_path=None):
    records = read_jsonl(path)
    header = section(records, "header")
    if header is None:
        fail(f"{path}: missing header")
    return normalize_frame(display_path or path, header, sections(records, "phase_cell"), [path])


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
                                      read_phase_csv(phase_path),
                                      [camera_path, phase_path]))
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


def reconstruction_options(frame_count, threshold, smooth_iterations, smooth_alpha,
                           write_normals, surface_mode, implicit_iso, implicit_blur_iterations):
    return {
        "frame_count": int(frame_count),
        "threshold": float(threshold),
        "smooth_iterations": int(smooth_iterations),
        "smooth_alpha": float(smooth_alpha),
        "write_normals": bool(write_normals),
        "surface_mode": surface_mode,
        "implicit_iso": float(implicit_iso),
        "implicit_blur_iterations": int(implicit_blur_iterations),
    }


def reconstruction_fingerprint(src, frames, options):
    entries = [file_fingerprint("reconstructor", __file__)]
    seen = {os.path.abspath(__file__)}

    def add(role, path, **extra):
        abs_path = os.path.abspath(path)
        if abs_path in seen:
            return
        seen.add(abs_path)
        entries.append(file_fingerprint(role, abs_path, **extra))

    if os.path.isfile(src):
        add("source", src)
    for index, frame in enumerate(frames):
        for path in frame.get("fingerprint_paths", []):
            add("frame_input", path, frame=index)
    return {
        "version": 1,
        "src": os.path.abspath(src) if os.path.exists(src) else src,
        "options": options,
        "files": entries,
    }


def fast_reconstruction_fingerprint(src, options):
    src_abs = os.path.abspath(src)
    if not os.path.isfile(src_abs):
        fail(f"{src}: input not found")
    entries = [file_fingerprint("reconstructor", __file__)]
    seen = {os.path.abspath(__file__)}

    def add(role, path, **extra):
        abs_path = os.path.abspath(path)
        if abs_path in seen:
            return
        if not os.path.isfile(abs_path):
            fail(f"{src}: missing fingerprint input {path!r}")
        seen.add(abs_path)
        entries.append(file_fingerprint(role, abs_path, **extra))

    add("source", src_abs)

    if src_abs.lower().endswith(".jsonl"):
        add("frame_input", src_abs, frame=0)
    else:
        data = read_json(src_abs)
        base_dir = os.path.dirname(src_abs)
        if data.get("lsfs_cache3d_manifest_version") == 1:
            for index, entry in enumerate(data.get("frames", [])):
                frame_path = resolve_path(base_dir, entry.get("path", ""))
                add("frame_input", frame_path, frame=index)
        elif data.get("converter") == "lsfs_render_cache_converter":
            for index, entry in enumerate(data.get("frames", [])):
                camera_path = resolve_path(base_dir, entry.get("camera", ""))
                phase_path = resolve_path(base_dir, entry.get("phase_cells", ""))
                add("frame_input", camera_path, frame=index)
                add("frame_input", phase_path, frame=index)
        else:
            fail(f"{src}: expected manifest, sequence.json, or JSONL frame")

    return {
        "version": 1,
        "src": src_abs,
        "options": options,
        "files": entries,
    }


def output_asset_exists(out_dir, value):
    if not isinstance(value, str) or not value:
        return False
    path = value if os.path.isabs(value) else os.path.join(out_dir, value)
    return os.path.isfile(path)


def load_reusable_reconstruction(out_dir, expected_fingerprint):
    summary_path = os.path.join(out_dir, "water_reconstruction.json")
    if not os.path.isfile(summary_path):
        return None
    try:
        summary = read_json(summary_path)
    except ReconstructionError:
        return None
    if summary.get("reconstruction_fingerprint") != expected_fingerprint:
        return None
    frames = summary.get("frames")
    if not isinstance(frames, list) or summary.get("frame_count") != len(frames):
        return None
    for frame in frames:
        if not isinstance(frame, dict) or not output_asset_exists(out_dir, frame.get("mesh")):
            return None
    summary["_runtime_reused"] = True
    return summary


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


CUBE_VERTEX_OFFSETS = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]


TETRA_DEFS = [
    (0, 5, 1, 6),
    (0, 1, 2, 6),
    (0, 2, 3, 6),
    (0, 3, 7, 6),
    (0, 7, 4, 6),
    (0, 4, 5, 6),
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


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def occupied_center(frame, occupied):
    dx = frame["dx"]
    inv_count = 1.0 / max(1, len(occupied))
    return (
        sum((i + 0.5) * dx for i, _, _ in occupied) * inv_count,
        sum((j + 0.5) * dx for _, j, _ in occupied) * inv_count,
        sum((k + 0.5) * dx for _, _, k in occupied) * inv_count,
    )


def occupancy_scalar(point, occupied):
    i, j, k = point
    total = 0
    for dz in (-1, 0):
        for dy in (-1, 0):
            for dx_i in (-1, 0):
                if (i + dx_i, j + dy, k + dz) in occupied:
                    total += 1
    return total / 8.0


def build_scalar_grid(occupied, blur_iterations):
    min_i = min(i for i, _, _ in occupied) - 1
    min_j = min(j for _, j, _ in occupied) - 1
    min_k = min(k for _, _, k in occupied) - 1
    max_i = max(i for i, _, _ in occupied) + 2
    max_j = max(j for _, j, _ in occupied) + 2
    max_k = max(k for _, _, k in occupied) + 2
    points = [
        (i, j, k)
        for k in range(min_k, max_k + 1)
        for j in range(min_j, max_j + 1)
        for i in range(min_i, max_i + 1)
    ]
    values = {point: occupancy_scalar(point, occupied) for point in points}
    neighbor_offsets = [
        (-1, 0, 0), (1, 0, 0),
        (0, -1, 0), (0, 1, 0),
        (0, 0, -1), (0, 0, 1),
    ]
    for _ in range(max(0, blur_iterations)):
        updated = {}
        for point in points:
            i, j, k = point
            neighbor_avg = sum(
                values.get((i + di, j + dj, k + dk), 0.0)
                for di, dj, dk in neighbor_offsets
            ) / len(neighbor_offsets)
            updated[point] = values[point] * 0.55 + neighbor_avg * 0.45
        values = updated
    bounds = (min_i, min_j, min_k, max_i, max_j, max_k)
    return values, bounds


def build_implicit_tetra_mesh(frame, occupied, iso, blur_iterations):
    dx = frame["dx"]
    iso = min(0.95, max(0.05, iso))
    scalar_grid, bounds = build_scalar_grid(occupied, blur_iterations)
    min_i, min_j, min_k, max_i, max_j, max_k = bounds
    center = occupied_center(frame, occupied)
    vertices = []
    faces = []
    edge_index = {}

    def add_edge_vertex(a, b, va, vb):
        key = (a, b) if a <= b else (b, a)
        if key in edge_index:
            return edge_index[key]
        denom = vb - va
        t = 0.5 if abs(denom) <= 1e-12 else (iso - va) / denom
        t = min(1.0, max(0.0, t))
        x = (a[0] + (b[0] - a[0]) * t) * dx
        y = (a[1] + (b[1] - a[1]) * t) * dx
        z = (a[2] + (b[2] - a[2]) * t) * dx
        vertices.append((x, y, z))
        edge_index[key] = len(vertices)
        return len(vertices)

    def add_oriented_face(face):
        if len(set(face)) < 3:
            return
        p0 = vertices[face[0] - 1]
        p1 = vertices[face[1] - 1]
        p2 = vertices[face[2] - 1]
        normal = cross(vec_sub(p1, p0), vec_sub(p2, p0))
        centroid = (
            (p0[0] + p1[0] + p2[0]) / 3.0,
            (p0[1] + p1[1] + p2[1]) / 3.0,
            (p0[2] + p1[2] + p2[2]) / 3.0,
        )
        if dot(normal, vec_sub(centroid, center)) < 0.0:
            face = list(reversed(face))
        faces.append(face)

    def edge_for(cube_points, cube_values, a, b):
        return add_edge_vertex(cube_points[a], cube_points[b], cube_values[a], cube_values[b])

    for k in range(min_k, max_k):
        for j in range(min_j, max_j):
            for i in range(min_i, max_i):
                cube_points = [(i + di, j + dj, k + dk) for di, dj, dk in CUBE_VERTEX_OFFSETS]
                cube_values = [scalar_grid.get(point, 0.0) for point in cube_points]
                if min(cube_values) >= iso or max(cube_values) < iso:
                    continue
                for tet in TETRA_DEFS:
                    tet_values = [cube_values[index] for index in tet]
                    inside = [local for local, value in enumerate(tet_values) if value >= iso]
                    outside = [local for local, value in enumerate(tet_values) if value < iso]
                    if not inside or not outside:
                        continue
                    if len(inside) == 1:
                        a = inside[0]
                        add_oriented_face([edge_for(cube_points, cube_values, tet[a], tet[b])
                                           for b in outside])
                    elif len(inside) == 3:
                        a = outside[0]
                        add_oriented_face([edge_for(cube_points, cube_values, tet[a], tet[b])
                                           for b in inside])
                    elif len(inside) == 2:
                        a, b = inside
                        c, d = outside
                        p_ac = edge_for(cube_points, cube_values, tet[a], tet[c])
                        p_ad = edge_for(cube_points, cube_values, tet[a], tet[d])
                        p_bc = edge_for(cube_points, cube_values, tet[b], tet[c])
                        p_bd = edge_for(cube_points, cube_values, tet[b], tet[d])
                        add_oriented_face([p_ac, p_ad, p_bd])
                        add_oriented_face([p_ac, p_bd, p_bc])

    if not vertices or not faces:
        fail("implicit tetra reconstruction produced an empty mesh")
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
                smooth_iterations=0, smooth_alpha=0.18, write_normals=False,
                surface_mode="voxel", implicit_iso=0.45, implicit_blur_iterations=0,
                reuse_if_fresh=False):
    out_dir = os.path.abspath(out_dir)
    options = reconstruction_options(frame_count,
                                     threshold,
                                     smooth_iterations,
                                     smooth_alpha,
                                     write_normals,
                                     surface_mode,
                                     implicit_iso,
                                     implicit_blur_iterations)
    fingerprint = fast_reconstruction_fingerprint(src, options)
    if reuse_if_fresh:
        summary = load_reusable_reconstruction(out_dir, fingerprint)
        if summary:
            return os.path.join(out_dir, "water_reconstruction.json"), summary

    frames = load_source(src)
    mesh_dir = os.path.join(out_dir, "meshes")
    os.makedirs(mesh_dir, exist_ok=True)

    output_frames = []
    for out_index in range(frame_count):
        frame = select_source_frame(frames, out_index, frame_count)
        occupied = occupied_voxels(frame, threshold)
        if not occupied:
            fail(f"{frame['source']}: no occupied water cells at threshold {threshold}")
        mesh_path = os.path.join(mesh_dir, f"frame_{out_index:04d}_water.obj")
        if surface_mode == "tetra":
            vertices, faces = build_implicit_tetra_mesh(frame, occupied, implicit_iso, implicit_blur_iterations)
        else:
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
            "surface_mode": surface_mode,
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
        "surface_mode": surface_mode,
        "implicit_iso": implicit_iso,
        "implicit_blur_iterations": implicit_blur_iterations,
        "smooth_iterations": smooth_iterations,
        "smooth_alpha": smooth_alpha,
        "write_normals": write_normals,
        "frame_count": len(output_frames),
        "reconstruction_fingerprint": fingerprint,
        "reconstruction_reused": False,
        "frames": output_frames,
    }
    summary_path = os.path.join(out_dir, "water_reconstruction.json")
    write_json(summary_path, summary)
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
    parser.add_argument("--surface-mode", choices=("voxel", "tetra"), default="voxel",
                        help="surface extraction mode")
    parser.add_argument("--implicit-iso", type=float, default=0.45,
                        help="implicit tetra isosurface threshold")
    parser.add_argument("--implicit-blur-iterations", type=int, default=0,
                        help="scalar-grid blur iterations for implicit tetra mode")
    parser.add_argument("--reuse-if-fresh", action="store_true",
                        help="reuse water_reconstruction.json if its input fingerprint still matches")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.threshold < 0.0 or not math.isfinite(args.threshold):
        parser.error("threshold must be finite and non-negative")
    if args.smooth_iterations < 0:
        parser.error("smooth-iterations must be non-negative")
    if args.smooth_alpha < 0.0 or args.smooth_alpha > 1.0 or not math.isfinite(args.smooth_alpha):
        parser.error("smooth-alpha must be finite in [0, 1]")
    if args.implicit_iso <= 0.0 or args.implicit_iso >= 1.0 or not math.isfinite(args.implicit_iso):
        parser.error("implicit-iso must be finite in (0, 1)")
    if args.implicit_blur_iterations < 0:
        parser.error("implicit-blur-iterations must be non-negative")
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
                                            write_normals=args.write_normals,
                                            surface_mode=args.surface_mode,
                                            implicit_iso=args.implicit_iso,
                                            implicit_blur_iterations=args.implicit_blur_iterations,
                                            reuse_if_fresh=args.reuse_if_fresh)
    except ReconstructionError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1
    print(f"frames={summary['frame_count']}")
    print(f"representation={summary['representation']}")
    print(f"surface_mode={summary['surface_mode']}")
    print(f"summary={summary_path}")
    reused = bool(summary.pop("_runtime_reused", False))
    print(f"reused={'true' if reused else 'false'}")
    print("status=reused" if reused else "status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
