#!/usr/bin/env python
"""QA validator for LSFS 3D render cache manifests and JSONL frames.

This tool is intentionally stricter than the preview renderer. It fails early on
schema drift, missing sections, non-finite numeric data, out-of-domain particles,
bad manifest ordering, and large water-volume drift.

Usage:
  python tools/validate_render_cache.py <manifest.json|cache.jsonl|cache-dir|glob> [options]
"""

import argparse
import glob
import json
import math
import os
import sys


SIM_KINDS = {"sparse3d_tp", "multires3d_tp"}
PARTICLE_KINDS = {"primary", "secondary_droplet", "secondary_bubble"}
PARTICLE_PHASES = {"liquid", "gas"}


class ValidationError(Exception):
    pass


def fail(message):
    raise ValidationError(message)


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def require_finite(value, label):
    if not is_number(value) or not math.isfinite(float(value)):
        fail(f"{label}: expected finite number")
    return float(value)


def require_int(value, label):
    if not isinstance(value, int) or isinstance(value, bool):
        fail(f"{label}: expected integer")
    return value


def require_nonnegative(value, label):
    value = require_finite(value, label)
    if value < 0.0:
        fail(f"{label}: expected non-negative value")
    return value


def require_positive(value, label):
    value = require_finite(value, label)
    if value <= 0.0:
        fail(f"{label}: expected positive value")
    return value


def require_vec3(value, label):
    if not isinstance(value, list) or len(value) != 3:
        fail(f"{label}: expected 3-vector")
    return [require_finite(value[i], f"{label}[{i}]") for i in range(3)]


def require_dims(value, label):
    if not isinstance(value, list) or len(value) != 3:
        fail(f"{label}: expected [nx, ny, nz]")
    dims = [require_int(value[i], f"{label}[{i}]") for i in range(3)]
    if any(v <= 0 for v in dims):
        fail(f"{label}: dimensions must be positive")
    return tuple(dims)


def resolve_frame_path(base_dir, path):
    if os.path.isabs(path):
        return path
    base_candidate = os.path.join(base_dir, path)
    if os.path.isfile(base_candidate):
        return base_candidate
    return path


def load_manifest(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid manifest JSON: {exc}")

    if data.get("lsfs_cache3d_manifest_version") != 1:
        fail(f"{path}: expected lsfs_cache3d_manifest_version=1")
    sim_kind = data.get("sim_kind")
    if sim_kind not in SIM_KINDS:
        fail(f"{path}: invalid sim_kind {sim_kind!r}")
    dims = require_dims(data.get("dims"), f"{path}: dims")
    dx = require_positive(data.get("dx"), f"{path}: dx")
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        fail(f"{path}: frames must be a non-empty list")
    frame_count = require_int(data.get("frame_count"), f"{path}: frame_count")
    if frame_count != len(frames):
        fail(f"{path}: frame_count {frame_count} != frames length {len(frames)}")

    base_dir = os.path.dirname(os.path.abspath(path))
    parsed_frames = []
    prev_frame = -1
    prev_step = 0
    prev_time = -math.inf
    for i, frame in enumerate(frames):
        if not isinstance(frame, dict):
            fail(f"{path}: frames[{i}] must be an object")
        frame_index = require_int(frame.get("frame"), f"{path}: frames[{i}].frame")
        step = require_int(frame.get("step"), f"{path}: frames[{i}].step")
        time = require_finite(frame.get("time"), f"{path}: frames[{i}].time")
        frame_path = frame.get("path")
        if not isinstance(frame_path, str) or not frame_path:
            fail(f"{path}: frames[{i}].path must be a non-empty string")
        bytes_value = require_int(frame.get("bytes"), f"{path}: frames[{i}].bytes")
        if bytes_value < 0:
            fail(f"{path}: frames[{i}].bytes must be non-negative")
        if frame_index <= prev_frame:
            fail(f"{path}: frame indices must be strictly increasing")
        if step <= 0 or step < prev_step:
            fail(f"{path}: frame steps must be positive and nondecreasing")
        if time < prev_time:
            fail(f"{path}: frame times must be nondecreasing")
        resolved = resolve_frame_path(base_dir, frame_path)
        if not os.path.isfile(resolved):
            fail(f"{path}: missing frame file {frame_path}")
        if bytes_value > 0 and os.path.getsize(resolved) != bytes_value:
            fail(f"{path}: byte size mismatch for {frame_path}")
        parsed_frames.append({
            "frame": frame_index,
            "step": step,
            "time": time,
            "path": resolved,
            "manifest_path": frame_path,
        })
        prev_frame = frame_index
        prev_step = step
        prev_time = time

    return {
        "path": path,
        "sim_kind": sim_kind,
        "dims": dims,
        "dx": dx,
        "frames": parsed_frames,
    }


def discover_inputs(src):
    manifest = None
    if os.path.isfile(src) and src.lower().endswith(".json"):
        manifest = load_manifest(src)
        files = [f["path"] for f in manifest["frames"]]
        return manifest, files

    if any(ch in src for ch in "*?[]"):
        files = sorted(glob.glob(src))
    elif os.path.isdir(src):
        files = sorted(glob.glob(os.path.join(src, "*.jsonl")))
    else:
        files = [src]
    files = [p for p in files if os.path.isfile(p)]
    if not files:
        fail(f"{src}: no JSONL cache frames found")
    return manifest, files


def parse_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append((line_no, json.loads(line)))
            except json.JSONDecodeError as exc:
                fail(f"{path}:{line_no}: invalid JSON: {exc}")
    if not records:
        fail(f"{path}: empty frame file")
    return records


def section_records(records, section):
    return [(line_no, rec) for line_no, rec in records if rec.get("section") == section]


def require_single_section(path, records, section):
    found = section_records(records, section)
    if len(found) != 1:
        fail(f"{path}: expected exactly one {section!r} section, found {len(found)}")
    return found[0]


def validate_header(path, rec, expected):
    if rec.get("lsfs_cache3d_version") != 1:
        fail(f"{path}: header missing lsfs_cache3d_version=1")
    sim_kind = rec.get("sim_kind")
    if sim_kind not in SIM_KINDS:
        fail(f"{path}: header invalid sim_kind {sim_kind!r}")
    frame = require_int(rec.get("frame"), f"{path}: header.frame")
    time = require_finite(rec.get("time"), f"{path}: header.time")
    dt = require_positive(rec.get("dt"), f"{path}: header.dt")
    dims = require_dims(rec.get("dims"), f"{path}: header.dims")
    dx = require_positive(rec.get("dx"), f"{path}: header.dx")
    phase = rec.get("phase")
    if not isinstance(phase, dict):
        fail(f"{path}: header.phase must be an object")
    for key in ("rho_l", "rho_g", "alpha_phi", "rho_tilde_0"):
        require_finite(phase.get(key), f"{path}: header.phase.{key}")

    if expected:
        if sim_kind != expected["sim_kind"]:
            fail(f"{path}: sim_kind mismatch with manifest")
        if dims != expected["dims"]:
            fail(f"{path}: dims mismatch with manifest")
        if abs(dx - expected["dx"]) > max(1e-9, 1e-9 * expected["dx"]):
            fail(f"{path}: dx mismatch with manifest")
        manifest_frame = expected.get("frame")
        if manifest_frame is not None and frame != manifest_frame:
            fail(f"{path}: header frame {frame} != manifest frame {manifest_frame}")
        manifest_time = expected.get("time")
        if manifest_time is not None and abs(time - manifest_time) > 1e-8:
            fail(f"{path}: header time {time} != manifest time {manifest_time}")

    return {"sim_kind": sim_kind, "frame": frame, "time": time, "dt": dt, "dims": dims, "dx": dx}


def validate_camera(path, rec):
    for key in ("position", "target", "up"):
        require_vec3(rec.get(key), f"{path}: camera.{key}")
    require_positive(rec.get("fov_degrees"), f"{path}: camera.fov_degrees")
    near_clip = require_positive(rec.get("near_clip"), f"{path}: camera.near_clip")
    far_clip = require_positive(rec.get("far_clip"), f"{path}: camera.far_clip")
    if far_clip <= near_clip:
        fail(f"{path}: camera far_clip must be greater than near_clip")


def validate_water(path, rec):
    volumes = {}
    for key in (
        "primary_liquid_volume",
        "primary_gas_volume",
        "secondary_droplet_volume",
        "secondary_bubble_volume",
        "phase_field_liquid_volume",
    ):
        volumes[key] = require_nonnegative(rec.get(key), f"{path}: water_volume.{key}")
    phase_field_cells = require_int(rec.get("phase_field_cells"), f"{path}: water_volume.phase_field_cells")
    if phase_field_cells < 0:
        fail(f"{path}: water_volume.phase_field_cells must be non-negative")
    return volumes, phase_field_cells


def validate_phase(path, phase_field_rec, phase_cells, dims, dx):
    declared = require_int(phase_field_rec.get("count"), f"{path}: phase_field.count")
    if declared < 0:
        fail(f"{path}: phase_field.count must be non-negative")
    if phase_field_rec.get("encoding") != "jsonl_cells":
        fail(f"{path}: phase_field.encoding must be jsonl_cells")
    if declared != len(phase_cells):
        fail(f"{path}: phase_field count {declared} != phase_cell records {len(phase_cells)}")

    nx, ny, nz = dims
    cell_volume = dx * dx * dx
    liquid_volume_sum = 0.0
    for line_no, rec in phase_cells:
        i = require_int(rec.get("i"), f"{path}:{line_no}: phase_cell.i")
        j = require_int(rec.get("j"), f"{path}:{line_no}: phase_cell.j")
        k = require_int(rec.get("k"), f"{path}:{line_no}: phase_cell.k")
        level = require_int(rec.get("level"), f"{path}:{line_no}: phase_cell.level")
        marker = require_int(rec.get("marker"), f"{path}:{line_no}: phase_cell.marker")
        phi = require_finite(rec.get("phi"), f"{path}:{line_no}: phase_cell.phi")
        volume = require_nonnegative(rec.get("liquid_volume"), f"{path}:{line_no}: phase_cell.liquid_volume")
        step = 1 << max(0, level)
        if level < 0:
            fail(f"{path}:{line_no}: phase_cell.level must be non-negative")
        if i < 0 or j < 0 or k < 0 or i >= nx or j >= ny or k >= nz:
            fail(f"{path}:{line_no}: phase_cell index out of bounds")
        if marker < 0:
            fail(f"{path}:{line_no}: phase_cell.marker must be non-negative")
        if phi < -1e-8 or phi > 1.0 + 1e-6:
            fail(f"{path}:{line_no}: phase_cell.phi out of [0,1] range")
        max_volume = cell_volume * step * step * step * (1.0 + 1e-6)
        if volume > max_volume:
            fail(f"{path}:{line_no}: phase_cell.liquid_volume exceeds cell volume")
        liquid_volume_sum += volume
    return declared, liquid_volume_sum


def validate_particles(path, particle_sections, particle_records, dims, dx):
    declared = {}
    for line_no, rec in particle_sections:
        kind = rec.get("kind")
        if kind not in PARTICLE_KINDS:
            fail(f"{path}:{line_no}: invalid particles kind {kind!r}")
        if kind in declared:
            fail(f"{path}: duplicate particles declaration for {kind}")
        count = require_int(rec.get("count"), f"{path}:{line_no}: particles.count")
        if count < 0:
            fail(f"{path}:{line_no}: particles.count must be non-negative")
        declared[kind] = count
    for required in PARTICLE_KINDS:
        if required not in declared:
            fail(f"{path}: missing {required} particles declaration")

    observed = {kind: 0 for kind in PARTICLE_KINDS}
    volumes = {
        kind: {phase: 0.0 for phase in PARTICLE_PHASES}
        for kind in PARTICLE_KINDS
    }
    nx, ny, nz = dims
    tol = max(1e-7, dx * 1e-7)
    upper = (nx * dx + tol, ny * dx + tol, nz * dx + tol)
    for line_no, rec in particle_records:
        kind = rec.get("kind")
        if kind not in PARTICLE_KINDS:
            fail(f"{path}:{line_no}: invalid particle kind {kind!r}")
        phase = rec.get("phase")
        if phase not in PARTICLE_PHASES:
            fail(f"{path}:{line_no}: invalid particle phase {phase!r}")
        index = require_int(rec.get("index"), f"{path}:{line_no}: particle.index")
        if index < 0:
            fail(f"{path}:{line_no}: particle.index must be non-negative")
        pos = require_vec3(rec.get("position"), f"{path}:{line_no}: particle.position")
        vel = require_vec3(rec.get("velocity"), f"{path}:{line_no}: particle.velocity")
        volume = require_nonnegative(rec.get("volume"), f"{path}:{line_no}: particle.volume")
        if any(v < -tol for v in pos) or any(pos[axis] > upper[axis] for axis in range(3)):
            fail(f"{path}:{line_no}: particle.position out of domain")
        if "age" in rec:
            age = require_int(rec.get("age"), f"{path}:{line_no}: particle.age")
            if age < 0:
                fail(f"{path}:{line_no}: particle.age must be non-negative")
        observed[kind] += 1
        volumes[kind][phase] += volume
        _ = vel

    for kind, count in declared.items():
        if observed[kind] != count:
            fail(f"{path}: particles kind {kind} count {count} != records {observed[kind]}")
    return sum(observed.values()), volumes


def validate_frame(path, expected=None):
    records = parse_jsonl(path)
    _, header_rec = require_single_section(path, records, "header")
    _, camera_rec = require_single_section(path, records, "camera")
    _, water_rec = require_single_section(path, records, "water_volume")
    _, phase_field_rec = require_single_section(path, records, "phase_field")

    header = validate_header(path, header_rec, expected)
    validate_camera(path, camera_rec)
    water, phase_field_cells_declared = validate_water(path, water_rec)
    phase_cells = section_records(records, "phase_cell")
    particle_sections = section_records(records, "particles")
    particle_records = section_records(records, "particle")
    phase_cell_count, phase_liquid_volume = validate_phase(
        path, phase_field_rec, phase_cells, header["dims"], header["dx"])
    particle_count, particle_volumes = validate_particles(
        path, particle_sections, particle_records, header["dims"], header["dx"])

    if phase_field_cells_declared != phase_cell_count:
        fail(f"{path}: water_volume.phase_field_cells does not match phase_field count")
    if abs(water["phase_field_liquid_volume"] - phase_liquid_volume) > max(1e-6, 1e-6 * phase_liquid_volume):
        fail(f"{path}: phase field liquid volume summary mismatch")
    if abs(water["primary_liquid_volume"] - particle_volumes["primary"]["liquid"]) > max(1e-6, 1e-6 * particle_volumes["primary"]["liquid"]):
        fail(f"{path}: primary liquid volume summary mismatch")
    if abs(water["primary_gas_volume"] - particle_volumes["primary"]["gas"]) > max(1e-6, 1e-6 * particle_volumes["primary"]["gas"]):
        fail(f"{path}: primary gas volume summary mismatch")
    droplet_volume = sum(particle_volumes["secondary_droplet"].values())
    bubble_volume = sum(particle_volumes["secondary_bubble"].values())
    if abs(water["secondary_droplet_volume"] - droplet_volume) > max(1e-6, 1e-6 * droplet_volume):
        fail(f"{path}: secondary droplet volume summary mismatch")
    if abs(water["secondary_bubble_volume"] - bubble_volume) > max(1e-6, 1e-6 * bubble_volume):
        fail(f"{path}: secondary bubble volume summary mismatch")

    water_like = (
        water["phase_field_liquid_volume"] +
        water["primary_liquid_volume"] +
        water["secondary_droplet_volume"] +
        water["secondary_bubble_volume"]
    )
    return {
        "path": path,
        "frame": header["frame"],
        "time": header["time"],
        "dims": header["dims"],
        "dx": header["dx"],
        "particles": particle_count,
        "phase_cells": phase_cell_count,
        "water_like_volume": water_like,
    }


def validate_sequence(files, manifest, max_volume_drift):
    results = []
    prev_frame = -1
    prev_time = -math.inf
    manifest_by_path = {}
    if manifest:
        for frame in manifest["frames"]:
            manifest_by_path[os.path.abspath(frame["path"])] = {
                "sim_kind": manifest["sim_kind"],
                "dims": manifest["dims"],
                "dx": manifest["dx"],
                "frame": frame["frame"],
                "time": frame["time"],
            }

    for path in files:
        expected = manifest_by_path.get(os.path.abspath(path))
        result = validate_frame(path, expected)
        if result["frame"] <= prev_frame:
            fail(f"{path}: frame index must be strictly increasing across input")
        if result["time"] < prev_time:
            fail(f"{path}: time must be nondecreasing across input")
        results.append(result)
        prev_frame = result["frame"]
        prev_time = result["time"]

    baseline = results[0]["water_like_volume"]
    max_drift = 0.0
    for result in results[1:]:
        drift_abs = abs(result["water_like_volume"] - baseline)
        denom = max(abs(baseline), 1e-12)
        drift = drift_abs / denom
        max_drift = max(max_drift, drift)
    if max_drift > max_volume_drift:
        fail(f"volume drift {max_drift:.9g} exceeds limit {max_volume_drift:.9g}")
    return results, max_drift


def main(argv):
    parser = argparse.ArgumentParser(description="Validate LSFS 3D render cache data")
    parser.add_argument("src", help="manifest JSON, JSONL frame, directory, or glob")
    parser.add_argument("--max-volume-drift", type=float, default=0.25,
                        help="maximum relative water-like volume drift across frames")
    parser.add_argument("--allow-empty-secondary", action="store_true",
                        help="accepted for scripts; secondary particle sections may already be empty")
    parser.add_argument("--verbose", action="store_true", help="print one summary line per frame")
    args = parser.parse_args(argv)

    if args.max_volume_drift < 0.0 or not math.isfinite(args.max_volume_drift):
        print("max-volume-drift must be finite and non-negative", file=sys.stderr)
        return 2

    try:
        manifest, files = discover_inputs(args.src)
        results, max_drift = validate_sequence(files, manifest, args.max_volume_drift)
    except ValidationError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1

    if args.verbose:
        for result in results:
            print(
                f"frame={result['frame']} path={result['path']} particles={result['particles']} "
                f"phase_cells={result['phase_cells']} water_like_volume={result['water_like_volume']:.17g}"
            )
    print(f"frames={len(results)}")
    print(f"particles={sum(r['particles'] for r in results)}")
    print(f"phase_cells={sum(r['phase_cells'] for r in results)}")
    print(f"max_volume_drift={max_drift:.17g}")
    print("status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
