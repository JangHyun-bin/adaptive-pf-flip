#!/usr/bin/env python
"""Convert LSFS 3D render cache manifests into renderer-neutral assets.

The converter keeps the JSONL cache as the canonical simulation output and
writes a simple movable bundle:

  sequence.json
  frames/frame_000_camera.json
  frames/frame_000_particles.csv
  frames/frame_000_phase_cells.csv

Usage:
  python tools/convert_render_cache.py <manifest.json> <out_dir> [--require-cinematic]
"""

import argparse
import csv
import json
import math
import os
import sys


PARTICLE_COLUMNS = [
    "kind",
    "render_channel",
    "index",
    "phase",
    "x",
    "y",
    "z",
    "vx",
    "vy",
    "vz",
    "volume",
    "age",
]

PHASE_CELL_COLUMNS = [
    "i",
    "j",
    "k",
    "level",
    "marker",
    "phi",
    "liquid_volume",
]


class ConvertError(Exception):
    pass


def fail(message):
    raise ConvertError(message)


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


def require_vec3(value, label):
    if not isinstance(value, list) or len(value) != 3:
        fail(f"{label}: expected 3-vector")
    return [require_finite(value[i], f"{label}[{i}]") for i in range(3)]


def require_object(value, label):
    if not isinstance(value, dict):
        fail(f"{label}: expected object")
    return value


def require_string(value, label):
    if not isinstance(value, str) or not value:
        fail(f"{label}: expected non-empty string")
    return value


def require_dims(value, label):
    if not isinstance(value, list) or len(value) != 3:
        fail(f"{label}: expected [nx, ny, nz]")
    dims = [require_int(value[i], f"{label}[{i}]") for i in range(3)]
    if any(v <= 0 for v in dims):
        fail(f"{label}: dimensions must be positive")
    return dims


def schema_version(data):
    version = data.get("cache_schema_version", 1)
    version = require_int(version, "cache_schema_version")
    if version not in (1, 2):
        fail("cache_schema_version: expected 1 or 2")
    return version


def resolve_frame_path(base_dir, path):
    if os.path.isabs(path):
        return path
    base_candidate = os.path.join(base_dir, path)
    if os.path.isfile(base_candidate):
        return base_candidate
    return path


def output_relpath(path, out_dir):
    return os.path.relpath(path, out_dir).replace(os.sep, "/")


def load_manifest(path, require_cinematic=False):
    if not os.path.isfile(path):
        fail(f"{path}: manifest not found")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid manifest JSON: {exc}")

    if data.get("lsfs_cache3d_manifest_version") != 1:
        fail(f"{path}: expected lsfs_cache3d_manifest_version=1")
    version = schema_version(data)
    if require_cinematic and version < 2:
        fail(f"{path}: require-cinematic needs cache_schema_version >= 2")
    sim_kind = require_string(data.get("sim_kind"), f"{path}: sim_kind")
    dims = require_dims(data.get("dims"), f"{path}: dims")
    dx = require_finite(data.get("dx"), f"{path}: dx")
    if dx <= 0.0:
        fail(f"{path}: dx must be positive")
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        fail(f"{path}: frames must be a non-empty list")
    frame_count = require_int(data.get("frame_count"), f"{path}: frame_count")
    if frame_count != len(frames):
        fail(f"{path}: frame_count {frame_count} != frames length {len(frames)}")

    base_dir = os.path.dirname(os.path.abspath(path))
    parsed = []
    for i, frame in enumerate(frames):
        require_object(frame, f"{path}: frames[{i}]")
        frame_index = require_int(frame.get("frame"), f"{path}: frames[{i}].frame")
        step = require_int(frame.get("step"), f"{path}: frames[{i}].step")
        time = require_finite(frame.get("time"), f"{path}: frames[{i}].time")
        frame_path = require_string(frame.get("path"), f"{path}: frames[{i}].path")
        bytes_value = require_int(frame.get("bytes"), f"{path}: frames[{i}].bytes")
        resolved = resolve_frame_path(base_dir, frame_path)
        if not os.path.isfile(resolved):
            fail(f"{path}: missing frame file {frame_path}")
        if bytes_value > 0 and os.path.getsize(resolved) != bytes_value:
            fail(f"{path}: byte size mismatch for {frame_path}")
        parsed.append({
            "frame": frame_index,
            "step": step,
            "time": time,
            "path": resolved,
            "manifest_path": frame_path,
            "bytes": bytes_value,
            "shutter_open": frame.get("shutter_open"),
            "shutter_close": frame.get("shutter_close"),
            "frame_bounds_min": frame.get("frame_bounds_min"),
            "frame_bounds_max": frame.get("frame_bounds_max"),
        })

    return {
        "path": os.path.abspath(path),
        "schema_version": version,
        "sim_kind": sim_kind,
        "dims": dims,
        "dx": dx,
        "frame_count": frame_count,
        "frames": parsed,
    }


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
        fail(f"{path}: empty frame")
    return records


def sections(records, name):
    return [rec for rec in records if rec.get("section") == name]


def single_section(records, name, path):
    found = sections(records, name)
    if len(found) != 1:
        fail(f"{path}: expected exactly one {name!r} section, found {len(found)}")
    return found[0]


def optional_single_section(records, name, path):
    found = sections(records, name)
    if len(found) > 1:
        fail(f"{path}: expected at most one {name!r} section, found {len(found)}")
    return found[0] if found else None


def validate_header(header, path, manifest, manifest_frame, require_cinematic):
    if header.get("lsfs_cache3d_version") != 1:
        fail(f"{path}: header missing lsfs_cache3d_version=1")
    version = schema_version(header)
    if require_cinematic and version < 2:
        fail(f"{path}: require-cinematic needs header cache_schema_version >= 2")
    dims = require_dims(header.get("dims"), f"{path}: header.dims")
    if dims != manifest["dims"]:
        fail(f"{path}: header dims mismatch with manifest")
    dx = require_finite(header.get("dx"), f"{path}: header.dx")
    if abs(dx - manifest["dx"]) > max(1e-9, 1e-9 * manifest["dx"]):
        fail(f"{path}: header dx mismatch with manifest")
    frame = require_int(header.get("frame"), f"{path}: header.frame")
    if frame != manifest_frame["frame"]:
        fail(f"{path}: header frame mismatch with manifest")
    time = require_finite(header.get("time"), f"{path}: header.time")
    if abs(time - manifest_frame["time"]) > 1e-8:
        fail(f"{path}: header time mismatch with manifest")
    require_finite(header.get("dt"), f"{path}: header.dt")


def validate_camera(camera, path, require_cinematic):
    for key in ("position", "target", "up"):
        require_vec3(camera.get(key), f"{path}: camera.{key}")
    require_finite(camera.get("fov_degrees"), f"{path}: camera.fov_degrees")
    require_finite(camera.get("near_clip"), f"{path}: camera.near_clip")
    require_finite(camera.get("far_clip"), f"{path}: camera.far_clip")
    if require_cinematic:
        require_finite(camera.get("vertical_fov_degrees"), f"{path}: camera.vertical_fov_degrees")
        require_finite(camera.get("focal_length_mm"), f"{path}: camera.focal_length_mm")


def validate_cinematic(cinematic, path, require_cinematic):
    if cinematic is None:
        if require_cinematic:
            fail(f"{path}: missing cinematic_metadata section")
        return
    version = schema_version(cinematic)
    if version < 2:
        fail(f"{path}: cinematic_metadata requires cache_schema_version >= 2")
    require_string(cinematic.get("world_units"), f"{path}: cinematic_metadata.world_units")
    require_finite(cinematic.get("shutter_open"), f"{path}: cinematic_metadata.shutter_open")
    require_finite(cinematic.get("shutter_close"), f"{path}: cinematic_metadata.shutter_close")
    for prefix in ("frame_bounds", "water_bounds", "secondary_bounds"):
        require_vec3(cinematic.get(f"{prefix}_min"), f"{path}: cinematic_metadata.{prefix}_min")
        require_vec3(cinematic.get(f"{prefix}_max"), f"{path}: cinematic_metadata.{prefix}_max")


def particle_row(rec, path):
    pos = require_vec3(rec.get("position"), f"{path}: particle.position")
    vel = require_vec3(rec.get("velocity"), f"{path}: particle.velocity")
    return {
        "kind": require_string(rec.get("kind"), f"{path}: particle.kind"),
        "render_channel": rec.get("render_channel", ""),
        "index": require_int(rec.get("index"), f"{path}: particle.index"),
        "phase": require_string(rec.get("phase"), f"{path}: particle.phase"),
        "x": pos[0],
        "y": pos[1],
        "z": pos[2],
        "vx": vel[0],
        "vy": vel[1],
        "vz": vel[2],
        "volume": require_finite(rec.get("volume"), f"{path}: particle.volume"),
        "age": rec.get("age", ""),
    }


def phase_cell_row(rec, path):
    return {
        "i": require_int(rec.get("i"), f"{path}: phase_cell.i"),
        "j": require_int(rec.get("j"), f"{path}: phase_cell.j"),
        "k": require_int(rec.get("k"), f"{path}: phase_cell.k"),
        "level": require_int(rec.get("level"), f"{path}: phase_cell.level"),
        "marker": require_int(rec.get("marker"), f"{path}: phase_cell.marker"),
        "phi": require_finite(rec.get("phi"), f"{path}: phase_cell.phi"),
        "liquid_volume": require_finite(rec.get("liquid_volume"), f"{path}: phase_cell.liquid_volume"),
    }


def write_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_csv(path, columns, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def convert_frame(manifest, manifest_frame, out_dir, frames_dir, require_cinematic):
    source_path = manifest_frame["path"]
    records = read_jsonl(source_path)
    header = single_section(records, "header", source_path)
    camera = single_section(records, "camera", source_path)
    water = single_section(records, "water_volume", source_path)
    cinematic = optional_single_section(records, "cinematic_metadata", source_path)
    secondary_channels = optional_single_section(records, "secondary_channels", source_path)
    validate_header(header, source_path, manifest, manifest_frame, require_cinematic)
    validate_camera(camera, source_path, require_cinematic)
    validate_cinematic(cinematic, source_path, require_cinematic)

    particles = [particle_row(rec, source_path) for rec in sections(records, "particle")]
    phase_cells = [phase_cell_row(rec, source_path) for rec in sections(records, "phase_cell")]
    if not sections(records, "phase_field"):
        fail(f"{source_path}: missing phase_field section")

    frame_name = f"frame_{manifest_frame['frame']:03d}"
    camera_path = os.path.join(frames_dir, f"{frame_name}_camera.json")
    particles_path = os.path.join(frames_dir, f"{frame_name}_particles.csv")
    phase_cells_path = os.path.join(frames_dir, f"{frame_name}_phase_cells.csv")

    camera_payload = {
        "source_cache": manifest_frame["manifest_path"],
        "manifest_frame": {
            "frame": manifest_frame["frame"],
            "step": manifest_frame["step"],
            "time": manifest_frame["time"],
            "bytes": manifest_frame["bytes"],
            "shutter_open": manifest_frame["shutter_open"],
            "shutter_close": manifest_frame["shutter_close"],
            "frame_bounds_min": manifest_frame["frame_bounds_min"],
            "frame_bounds_max": manifest_frame["frame_bounds_max"],
        },
        "header": header,
        "camera": camera,
        "water_volume": water,
        "cinematic_metadata": cinematic,
        "secondary_channels": secondary_channels,
        "particle_count": len(particles),
        "phase_cell_count": len(phase_cells),
    }
    write_json(camera_path, camera_payload)
    write_csv(particles_path, PARTICLE_COLUMNS, particles)
    write_csv(phase_cells_path, PHASE_CELL_COLUMNS, phase_cells)

    return {
        "frame": manifest_frame["frame"],
        "step": manifest_frame["step"],
        "time": manifest_frame["time"],
        "source_cache": manifest_frame["manifest_path"],
        "camera": output_relpath(camera_path, out_dir),
        "particles": output_relpath(particles_path, out_dir),
        "phase_cells": output_relpath(phase_cells_path, out_dir),
        "particle_count": len(particles),
        "phase_cell_count": len(phase_cells),
    }


def convert(manifest_path, out_dir, require_cinematic=False):
    manifest = load_manifest(manifest_path, require_cinematic=require_cinematic)
    out_dir = os.path.abspath(out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    converted_frames = []
    for frame in manifest["frames"]:
        converted_frames.append(convert_frame(manifest, frame, out_dir, frames_dir, require_cinematic))

    sequence = {
        "converter": "lsfs_render_cache_converter",
        "version": 1,
        "source_manifest": os.path.basename(manifest["path"]),
        "manifest_schema_version": manifest["schema_version"],
        "sim_kind": manifest["sim_kind"],
        "dims": manifest["dims"],
        "dx": manifest["dx"],
        "frame_count": len(converted_frames),
        "frames": converted_frames,
    }
    write_json(os.path.join(out_dir, "sequence.json"), sequence)
    return sequence


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Convert LSFS 3D render cache manifests")
    parser.add_argument("manifest", help="render cache manifest JSON")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--require-cinematic", action="store_true",
                        help="require S37 cache_schema_version 2 cinematic metadata")
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    try:
        sequence = convert(args.manifest, args.out_dir, require_cinematic=args.require_cinematic)
    except ConvertError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1

    print(f"frames={sequence['frame_count']}")
    print(f"sequence={os.path.join(args.out_dir, 'sequence.json')}")
    print("status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
