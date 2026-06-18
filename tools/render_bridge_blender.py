#!/usr/bin/env python
"""Render LSFS converted cache bundles through Blender.

This S42 bridge keeps the simulation cache and renderer integration separated:
it reads an S38 converted sequence bundle, consumes S41 OBJ water meshes, writes
a Blender scene spec, then optionally runs Blender in background mode to render
PNG frames.

Usage:
  python tools/render_bridge_blender.py --check
  python tools/render_bridge_blender.py build/render_cache_convert_mesh/sequence.json build/blender_bridge --frames 8
  python tools/render_bridge_blender.py build/render_cache_convert_mesh/sequence.json build/blender_bridge --frames 8 --dry-run
"""

import argparse
import csv
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

try:
    from PIL import Image
except ImportError:
    Image = None


class BridgeError(Exception):
    pass


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def default_preset_config_path():
    return os.path.join(repo_root(), "configs", "cinematic_presets.json")


def fail(message):
    raise BridgeError(message)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")


def resolve_config_path(path):
    if not path:
        return default_preset_config_path()
    if os.path.isabs(path):
        return path
    cwd_candidate = os.path.abspath(path)
    if os.path.isfile(cwd_candidate):
        return cwd_candidate
    return os.path.join(repo_root(), path)


def deep_merge(base, override):
    out = dict(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def resolve_preset(presets, preset_name, stack=None):
    stack = stack or []
    if preset_name in stack:
        chain = " -> ".join(stack + [preset_name])
        fail(f"preset extends cycle: {chain}")
    preset = presets.get(preset_name)
    if not isinstance(preset, dict):
        fail(f"unknown render preset {preset_name!r}")
    parent_name = preset.get("extends")
    if parent_name is None:
        return {key: value for key, value in preset.items() if key != "extends"}
    if not isinstance(parent_name, str) or not parent_name:
        fail(f"render preset {preset_name!r} has invalid extends value")
    parent = resolve_preset(presets, parent_name, stack + [preset_name])
    return deep_merge(parent, preset)


def load_render_preset(config_path, preset_name):
    if not preset_name:
        return None, None
    resolved = resolve_config_path(config_path)
    if not os.path.isfile(resolved):
        fail(f"{resolved}: preset config not found")
    data = read_json(resolved)
    if data.get("schema") != "lsfs_cinematic_presets":
        fail(f"{resolved}: expected lsfs_cinematic_presets schema")
    presets = data.get("presets")
    if not isinstance(presets, dict):
        fail(f"{resolved}: presets must be an object")
    return resolved, resolve_preset(presets, preset_name)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


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


def vec3(value, fallback=(0.0, 0.0, 0.0)):
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return [as_float(value[0]), as_float(value[1]), as_float(value[2])]
    return [fallback[0], fallback[1], fallback[2]]


def v_add(a, b):
    return [a[i] + b[i] for i in range(3)]


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
    if length <= 1e-12:
        return [fallback[0], fallback[1], fallback[2]]
    return [a[i] / length for i in range(3)]


def to_blender_coords(point):
    return [as_float(point[0]), -as_float(point[2]), as_float(point[1])]


def resolve_file(base_dir, path):
    if not isinstance(path, str) or not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(base_dir, path))


def relpath(path, base_dir):
    return os.path.relpath(path, base_dir).replace(os.sep, "/")


def unique_existing(paths):
    seen = set()
    out = []
    for path in paths:
        if not path:
            continue
        norm = os.path.abspath(path)
        key = os.path.normcase(norm)
        if key in seen or not os.path.isfile(norm):
            continue
        seen.add(key)
        out.append(norm)
    return out


def blender_version_key(path):
    parent = os.path.basename(os.path.dirname(path))
    nums = [int(part) for part in re.findall(r"\d+", parent)]
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


def discover_blender_candidates(explicit=None):
    if explicit:
        return unique_existing([explicit])
    candidates = []
    candidates.append(shutil.which("blender"))
    roots = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
    ]
    for root in roots:
        if not root:
            continue
        pattern = os.path.join(root, "Blender Foundation", "Blender *", "blender.exe")
        candidates.extend(glob.glob(pattern))
    found = unique_existing(candidates)
    return sorted(found, key=blender_version_key, reverse=True)


def find_blender(explicit=None):
    candidates = discover_blender_candidates(explicit)
    return candidates[0] if candidates else None


def blender_version(path):
    if not path:
        return None
    try:
        result = subprocess.run([path, "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                timeout=20,
                                check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"version probe failed: {exc}"
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[0] if lines else "unknown"


def dependency_report(blender_path=None):
    candidates = discover_blender_candidates(blender_path)
    selected = candidates[0] if candidates else None
    return {
        "bridge": "blender",
        "available": selected is not None,
        "selected": selected,
        "version": blender_version(selected) if selected else None,
        "candidates": candidates,
        "path_source": "explicit" if blender_path else "auto",
    }


def load_water_reconstruction(path):
    if not path:
        return None
    if not os.path.isfile(path):
        fail(f"{path}: water reconstruction index not found")
    data = read_json(path)
    if data.get("reconstructor") != "lsfs_water_reconstruction":
        fail(f"{path}: not an LSFS water reconstruction index")
    base_dir = os.path.dirname(os.path.abspath(path))
    frames = []
    for frame in data.get("frames", []):
        mesh_path = resolve_file(base_dir, frame.get("mesh"))
        if not mesh_path or not os.path.isfile(mesh_path):
            fail(f"{path}: missing water mesh {frame.get('mesh')!r}")
        frames.append({
            "mesh": mesh_path,
            "frame": as_int(frame.get("frame"), len(frames)),
            "source_frame": as_int(frame.get("source_frame"), 0),
            "source_time": as_float(frame.get("source_time"), 0.0),
            "vertex_count": as_int(frame.get("vertex_count")),
            "face_count": as_int(frame.get("face_count")),
            "occupied_cell_count": as_int(frame.get("occupied_cell_count")),
        })
    if not frames:
        fail(f"{path}: water reconstruction has no frames")
    return {
        "path": os.path.abspath(path),
        "representation": data.get("representation", "obj_mesh"),
        "frames": frames,
    }


def select_resampled(items, out_index, out_count):
    if not items:
        return None
    if out_count <= 1 or len(items) == 1:
        return items[0]
    src_index = round(out_index * (len(items) - 1) / max(1, out_count - 1))
    return items[src_index]


def require_file(path, label):
    if not path or not os.path.isfile(path):
        fail(f"{label}: file not found")
    return path


def load_sequence(path, water_reconstruction_path=None):
    if not os.path.isfile(path):
        fail(f"{path}: source sequence not found")
    data = read_json(path)
    if data.get("converter") != "lsfs_render_cache_converter":
        fail(f"{path}: expected an S38 converted sequence.json bundle")
    base_dir = os.path.dirname(os.path.abspath(path))
    water_index_path = water_reconstruction_path
    if not water_index_path:
        water_ref = data.get("water_reconstruction", {})
        water_index_path = resolve_file(base_dir, water_ref.get("path"))
    water_index = load_water_reconstruction(water_index_path) if water_index_path else None

    frames = []
    for entry in data.get("frames", []):
        camera_path = require_file(resolve_file(base_dir, entry.get("camera")), "camera")
        particles_path = require_file(resolve_file(base_dir, entry.get("particles")), "particles")
        camera_payload = read_json(camera_path)
        mesh_path = resolve_file(base_dir, entry.get("water_mesh"))
        if mesh_path and not os.path.isfile(mesh_path):
            fail(f"{path}: missing water mesh {entry.get('water_mesh')!r}")
        frames.append({
            "camera_path": camera_path,
            "particles_csv": particles_path,
            "source_cache": entry.get("source_cache"),
            "frame": as_int(entry.get("frame"), len(frames)),
            "time": as_float(entry.get("time"), 0.0),
            "camera": camera_payload.get("camera", {}),
            "header": camera_payload.get("header", {}),
            "cinematic": camera_payload.get("cinematic_metadata", {}),
            "water_mesh": mesh_path,
            "water_mesh_vertex_count": as_int(entry.get("water_mesh_vertex_count")),
            "water_mesh_face_count": as_int(entry.get("water_mesh_face_count")),
            "particle_count": as_int(entry.get("particle_count")),
            "secondary_channels": camera_payload.get("secondary_channels", {}),
        })
    if not frames:
        fail(f"{path}: sequence contains no frames")
    return {
        "source": os.path.abspath(path),
        "base_dir": base_dir,
        "sequence": data,
        "frames": frames,
        "water_reconstruction": water_index,
    }


def secondary_render_channel(row):
    kind = row.get("kind", "")
    channel = row.get("render_channel", "")
    if channel in ("droplet", "spray", "foam", "bubble"):
        return channel
    if kind == "secondary_bubble":
        return "bubble"
    if kind == "secondary_droplet":
        return "droplet"
    return ""


def count_secondary_particles(path):
    counts = {"droplet": 0, "spray": 0, "foam": 0, "bubble": 0, "total": 0}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            channel = secondary_render_channel(row)
            if channel not in counts:
                continue
            counts[channel] += 1
            counts["total"] += 1
    return counts


def estimate_secondary_streak_counts(path, max_count, streak_pass):
    counts = {"spray": 0, "foam": 0, "total": 0}
    if not streak_pass.get("enabled", False) or max_count <= 0:
        return counts
    channels = streak_pass.get("channels") if isinstance(streak_pass.get("channels"), dict) else {}
    min_speed = as_float(streak_pass.get("min_speed"), 0.35)
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if counts["total"] >= max_count:
                break
            channel = secondary_render_channel(row)
            channel_mult = as_float(channels.get(channel), 0.0)
            if channel not in ("spray", "foam") or channel_mult <= 0.0:
                continue
            vx = as_float(row.get("vx"), 0.0)
            vy = as_float(row.get("vy"), 0.0)
            vz = as_float(row.get("vz"), 0.0)
            speed = math.sqrt(vx * vx + vy * vy + vz * vz)
            if speed < min_speed:
                continue
            counts[channel] += 1
            counts["total"] += 1
    return counts


def summarize_secondary_streak_counts(frames):
    if not frames:
        return {}
    totals = [as_int(frame.get("secondary_streak_counts", {}).get("total"), 0) for frame in frames]
    return {
        "first": frames[0].get("secondary_streak_counts", {}),
        "last": frames[-1].get("secondary_streak_counts", {}),
        "min_total": min(totals),
        "max_total": max(totals),
        "mean_total": sum(totals) / float(len(totals)),
    }


def secondary_framing_qa_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "secondary_framing_qa")
    channels = preset_section(cfg, "channels")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "spray": bool(channels.get("spray", True)),
            "foam": bool(channels.get("foam", True)),
        },
        "min_mean_inside_ratio": cfg.get("min_mean_inside_ratio"),
        "min_frame_inside_ratio": cfg.get("min_frame_inside_ratio"),
        "min_mean_screen_y": cfg.get("min_mean_screen_y"),
        "max_mean_screen_y": cfg.get("max_mean_screen_y"),
    }


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


def secondary_framing_for_frame(frame, width, height, framing_qa):
    channels = framing_qa.get("channels") if isinstance(framing_qa.get("channels"), dict) else {}
    enabled_channels = {name for name, enabled in channels.items() if enabled}
    if not enabled_channels:
        return {"active": 0, "inside": 0, "inside_ratio": 0.0}
    active = 0
    inside = 0
    ys = []
    with open(frame["particles_csv"], encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            channel = secondary_render_channel(row)
            if channel not in enabled_channels:
                continue
            active += 1
            projected = project_camera_point(
                [row.get("x", 0.0), row.get("y", 0.0), row.get("z", 0.0)],
                frame["camera"],
                width,
                height)
            if not projected:
                continue
            x = projected["x"]
            y = projected["y"]
            if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                inside += 1
                ys.append(y)
    if active <= 0:
        return {"active": 0, "inside": 0, "inside_ratio": 0.0}
    metrics = {
        "active": active,
        "inside": inside,
        "inside_ratio": inside / float(active),
    }
    if ys:
        metrics.update({
            "mean_screen_y": sum(ys) / float(len(ys)),
            "min_screen_y": min(ys),
            "max_screen_y": max(ys),
        })
    return metrics


def summarize_secondary_framing(frames, width, height, framing_qa):
    if not framing_qa.get("enabled", False) or not frames:
        return {"enabled": False}
    frame_metrics = [secondary_framing_for_frame(frame, width, height, framing_qa) for frame in frames]
    ratios = [as_float(item.get("inside_ratio"), 0.0) for item in frame_metrics]
    ys = [as_float(item.get("mean_screen_y"), 0.0) for item in frame_metrics if item.get("inside", 0) > 0]
    return {
        "enabled": True,
        "channels": framing_qa.get("channels", {}),
        "frame_count": len(frame_metrics),
        "first": frame_metrics[0],
        "last": frame_metrics[-1],
        "min_inside_ratio": min(ratios),
        "mean_inside_ratio": sum(ratios) / float(len(ratios)),
        "max_inside_ratio": max(ratios),
        "mean_screen_y": sum(ys) / float(len(ys)) if ys else None,
        "min_mean_screen_y": min(ys) if ys else None,
        "max_mean_screen_y": max(ys) if ys else None,
    }


def preset_section(data, name):
    if not isinstance(data, dict):
        return {}
    value = data.get(name, {})
    return value if isinstance(value, dict) else {}


def normalize_camera(camera):
    return {
        "position": vec3(camera.get("position"), (0.0, 0.0, 1.0)),
        "target": vec3(camera.get("target"), (0.0, 0.0, 0.0)),
        "up": vec3(camera.get("up"), (0.0, 1.0, 0.0)),
        "focal_length_mm": as_float(camera.get("focal_length_mm"), 50.0),
        "vertical_fov_degrees": as_float(
            camera.get("vertical_fov_degrees", camera.get("fov_degrees")),
            45.0),
        "near_clip": as_float(camera.get("near_clip"), 0.05),
        "far_clip": as_float(camera.get("far_clip"), 500.0),
    }


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_vec(a, b, t):
    return [lerp(as_float(a[i]), as_float(b[i]), t) for i in range(3)]


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def sorted_camera_keys(path):
    keys = [item for item in path if isinstance(item, dict)]
    if not keys:
        return []
    return sorted(keys, key=lambda item: as_float(item.get("t"), 0.0))


def interpolate_camera_keys(keys, t, fallback):
    if not keys:
        return fallback
    if len(keys) == 1 or t <= as_float(keys[0].get("t"), 0.0):
        return {**fallback, **keys[0]}
    if t >= as_float(keys[-1].get("t"), 1.0):
        return {**fallback, **keys[-1]}
    lo = keys[0]
    hi = keys[-1]
    for i in range(1, len(keys)):
        candidate = keys[i]
        if t <= as_float(candidate.get("t"), 1.0):
            lo = keys[i - 1]
            hi = candidate
            break
    t0 = as_float(lo.get("t"), 0.0)
    t1 = as_float(hi.get("t"), 1.0)
    local = 0.0 if t1 <= t0 else (t - t0) / (t1 - t0)
    out = dict(fallback)
    for key in ("position", "target", "up"):
        out[key] = lerp_vec(vec3(lo.get(key), out[key]), vec3(hi.get(key), out[key]), local)
    for key in ("focal_length_mm", "vertical_fov_degrees", "near_clip", "far_clip"):
        out[key] = lerp(as_float(lo.get(key), out[key]), as_float(hi.get(key), out[key]), local)
    return out


def dims3(value, fallback):
    if not isinstance(value, list) or len(value) < 3:
        return [float(fallback[0]), float(fallback[1]), float(fallback[2])]
    return [max(1e-12, as_float(value[i], fallback[i])) for i in range(3)]


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def apply_camera_auto_frame(cam, preset_camera, header):
    auto = preset_section(preset_camera, "auto_frame")
    if not auto.get("enabled", False):
        return cam
    dims = dims3(header.get("dims"), [1.0, 1.0, 1.0])
    reference_dims = dims3(auto.get("reference_dims"), dims)
    raw_scale = max(
        dims[0] / max(1e-12, reference_dims[0]),
        dims[1] / max(1e-12, reference_dims[1]),
        dims[2] / max(1e-12, reference_dims[2]),
    )
    strength = clamp(as_float(auto.get("strength"), 1.0), 0.0, 1.0)
    scale = lerp(1.0, raw_scale, strength)
    scale = clamp(scale,
                  max(0.01, as_float(auto.get("min_scale"), 1.0)),
                  max(0.01, as_float(auto.get("max_scale"), 2.0)))
    reference_center = vec3(auto.get("reference_center"),
                            [reference_dims[0] * 0.5, reference_dims[1] * 0.5, reference_dims[2] * 0.5])
    scene_center = vec3(auto.get("scene_center"),
                        [dims[0] * 0.5, dims[1] * 0.5, dims[2] * 0.5])
    target_offset_scale = as_float(auto.get("target_offset_scale"), scale)
    old_target = vec3(cam.get("target"), reference_center)
    old_position = vec3(cam.get("position"), old_target)
    target = [
        scene_center[i] + (old_target[i] - reference_center[i]) * target_offset_scale
        for i in range(3)
    ]
    position = [
        target[i] + (old_position[i] - old_target[i]) * scale
        for i in range(3)
    ]
    fov_pad = max(0.0, as_float(auto.get("fov_pad_degrees"), 0.0))
    cam["position"] = position
    cam["target"] = target
    cam["vertical_fov_degrees"] = min(175.0, as_float(cam.get("vertical_fov_degrees"), 45.0) + fov_pad)
    cam["auto_frame"] = {
        "enabled": True,
        "dims": dims,
        "reference_dims": reference_dims,
        "raw_scale": raw_scale,
        "scale": scale,
        "target_offset_scale": target_offset_scale,
    }
    return cam


def apply_camera_preset(base_camera, render_preset, out_index, out_count, header=None):
    cam = normalize_camera(base_camera)
    preset_camera = preset_section(render_preset, "camera")
    motion = preset_section(preset_camera, "motion")
    for key, value in preset_camera.items():
        if key != "motion":
            cam[key] = value
    cam = normalize_camera(cam)
    cam["preset_applied"] = True
    cam["motion_enabled"] = False
    if motion.get("enabled", False):
        path = sorted_camera_keys(motion.get("path", []))
        if path:
            raw_t = 0.0 if out_count <= 1 else out_index / max(1, out_count - 1)
            eased_t = smoothstep(raw_t) if motion.get("easing", "linear") == "smoothstep" else raw_t
            cam = normalize_camera(interpolate_camera_keys(path, eased_t, cam))
            cam["preset_applied"] = True
            cam["motion_enabled"] = True
            cam["motion_t"] = raw_t
            cam["motion_eased_t"] = eased_t
    cam = apply_camera_auto_frame(cam, preset_camera, header or {})
    return cam


def camera_motion_summary(render_preset):
    motion = preset_section(preset_section(render_preset, "camera"), "motion")
    path = sorted_camera_keys(motion.get("path", []))
    return {
        "enabled": bool(motion.get("enabled", False) and path),
        "key_count": len(path),
        "easing": motion.get("easing", "linear"),
    }


def camera_framing_summary(render_preset, frames):
    configured = preset_section(preset_section(render_preset, "camera"), "auto_frame")
    applied = [frame["camera"].get("auto_frame") for frame in frames if frame["camera"].get("auto_frame")]
    scales = [as_float(item.get("scale"), 1.0) for item in applied]
    return {
        "configured": bool(configured.get("enabled", False)),
        "enabled": bool(applied),
        "frame_count": len(applied),
        "reference_dims": dims3(configured.get("reference_dims"), [1.0, 1.0, 1.0]) if configured else [],
        "min_scale": min(scales) if scales else 1.0,
        "max_scale": max(scales) if scales else 1.0,
    }


def distance3(a, b):
    if not isinstance(a, list) or not isinstance(b, list) or len(a) < 3 or len(b) < 3:
        return 0.0
    return math.sqrt(sum((as_float(a[i]) - as_float(b[i])) ** 2 for i in range(3)))


def camera_path_metrics(frames):
    cameras = [frame.get("camera", {}) for frame in frames]
    positions = [vec3(camera.get("position"), [0.0, 0.0, 0.0]) for camera in cameras]
    targets = [vec3(camera.get("target"), [0.0, 0.0, 0.0]) for camera in cameras]
    fovs = [as_float(camera.get("vertical_fov_degrees"), 0.0) for camera in cameras]
    target_distances = [distance3(pos, target) for pos, target in zip(positions, targets)]
    return {
        "frame_count": len(cameras),
        "min_position_y": min((item[1] for item in positions), default=0.0),
        "max_position_y": max((item[1] for item in positions), default=0.0),
        "min_target_y": min((item[1] for item in targets), default=0.0),
        "max_target_y": max((item[1] for item in targets), default=0.0),
        "min_target_distance": min(target_distances, default=0.0),
        "max_target_distance": max(target_distances, default=0.0),
        "min_vertical_fov_degrees": min(fovs, default=0.0),
        "max_vertical_fov_degrees": max(fovs, default=0.0),
    }


def water_material_summary(render_preset):
    water = preset_section(preset_section(render_preset, "materials"), "water")
    return {
        "depth_strength": as_float(water.get("depth_strength"), 0.0),
        "rim_strength": as_float(water.get("rim_strength"), 0.0),
        "rim_width": as_float(water.get("rim_width"), 0.0),
    }


def water_surface_detail_summary(render_preset):
    detail = preset_section(preset_section(render_preset, "renderer"), "water_surface_detail")
    return {
        "enabled": bool(detail.get("enabled", False)),
        "strength": as_float(detail.get("strength"), 0.0),
        "scale": as_float(detail.get("scale"), 3.0),
        "depth": as_int(detail.get("depth"), 3),
    }


def secondary_channel_radius_summary(render_preset):
    scales = preset_section(preset_section(render_preset, "renderer"), "secondary_channel_radius_scales")
    return {
        "droplet": as_float(scales.get("droplet"), 1.0),
        "spray": as_float(scales.get("spray"), 1.0),
        "foam": as_float(scales.get("foam"), 1.0),
        "bubble": as_float(scales.get("bubble"), 1.0),
    }


def secondary_soft_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "secondary_soft_pass")
    channels = preset_section(cfg, "channels")
    falloff = cfg.get("falloff", [1.0, 0.45, 0.16, 0.04])
    if not isinstance(falloff, list) or not falloff:
        falloff = [1.0, 0.45, 0.16, 0.04]
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "spray": as_float(channels.get("spray"), 0.0),
            "foam": as_float(channels.get("foam"), 0.0),
        },
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.35),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.5),
        "max_radius": as_float(cfg.get("max_radius"), 1.0),
        "geometry": str(cfg.get("geometry", "batched_spheres")),
        "falloff": [as_float(item, 0.0) for item in falloff],
        "material_falloff": str(cfg.get("material_falloff", "ring_materials")),
    }


def secondary_streak_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "secondary_streak_pass")
    channels = preset_section(cfg, "channels")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "spray": as_float(channels.get("spray"), 0.0),
            "foam": as_float(channels.get("foam"), 0.0),
        },
        "length_scale": as_float(cfg.get("length_scale"), 0.04),
        "max_length": as_float(cfg.get("max_length"), 1.0),
        "width_scale": as_float(cfg.get("width_scale"), 0.45),
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.22),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.9),
        "min_speed": as_float(cfg.get("min_speed"), 0.35),
    }


def surface_contact_foam_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "surface_contact_foam_pass")
    channels = preset_section(cfg, "channels")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "foam": as_float(channels.get("foam"), 0.0),
        },
        "max_count": as_int(cfg.get("max_count"), 256),
        "radius_x": as_float(cfg.get("radius_x"), 0.7),
        "radius_z": as_float(cfg.get("radius_z"), 0.22),
        "vertical_offset": as_float(cfg.get("vertical_offset"), -1.2),
        "flow_aligned": bool(cfg.get("flow_aligned", False)),
        "flow_center": vec3(cfg.get("flow_center"), (14.0, 0.0, 11.0)),
        "material_falloff": str(cfg.get("material_falloff", "solid")),
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.32),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.35),
    }


def water_surface_glint_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "water_surface_glint_pass")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "count": as_int(cfg.get("count"), 0),
        "region_min": vec3(cfg.get("region_min"), (1.0, 4.8, 3.0)),
        "region_max": vec3(cfg.get("region_max"), (27.0, 8.2, 19.0)),
        "length": as_float(cfg.get("length"), 1.35),
        "width": as_float(cfg.get("width"), 0.035),
        "flow_dir": vec3(cfg.get("flow_dir"), (1.0, 0.0, 0.18)),
        "drift_per_frame": as_float(cfg.get("drift_per_frame"), 0.08),
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.22),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.45),
    }


def water_reflection_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "water_reflection_pass")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "count": as_int(cfg.get("count"), 0),
        "region_min": vec3(cfg.get("region_min"), (1.0, 4.7, 3.0)),
        "region_max": vec3(cfg.get("region_max"), (27.0, 8.0, 19.0)),
        "length": as_float(cfg.get("length"), 3.8),
        "width": as_float(cfg.get("width"), 0.075),
        "flow_dir": vec3(cfg.get("flow_dir"), (1.0, 0.0, 0.14)),
        "drift_per_frame": as_float(cfg.get("drift_per_frame"), 0.035),
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.18),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.32),
    }


def water_volume_scattering_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "water_volume_scattering_pass")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "layers": as_int(cfg.get("layers"), 0),
        "region_min": vec3(cfg.get("region_min"), (1.0, 4.5, 3.2)),
        "region_max": vec3(cfg.get("region_max"), (27.0, 7.8, 19.0)),
        "inset": as_float(cfg.get("inset"), 0.15),
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.22),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.18),
    }


def water_impact_ripple_pass_summary(render_preset):
    cfg = preset_section(preset_section(render_preset, "renderer"), "water_impact_ripple_pass")
    channels = preset_section(cfg, "channels")
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "foam": as_float(channels.get("foam"), 0.0),
            "spray": as_float(channels.get("spray"), 0.0),
        },
        "max_count": as_int(cfg.get("max_count"), 128),
        "ring_count": as_int(cfg.get("ring_count"), 2),
        "segments": as_int(cfg.get("segments"), 18),
        "arc_fraction": as_float(cfg.get("arc_fraction"), 0.62),
        "radius": as_float(cfg.get("radius"), 0.48),
        "radius_step": as_float(cfg.get("radius_step"), 0.28),
        "width": as_float(cfg.get("width"), 0.035),
        "vertical_offset": as_float(cfg.get("vertical_offset"), -1.78),
        "flow_center": vec3(cfg.get("flow_center"), (14.0, 0.0, 11.0)),
        "material_falloff": str(cfg.get("material_falloff", "solid")),
        "alpha_scale": as_float(cfg.get("alpha_scale"), 0.26),
        "emission_scale": as_float(cfg.get("emission_scale"), 0.42),
    }


def estimate_surface_contact_foam_counts(path, contact_pass):
    count = 0
    if not contact_pass.get("enabled", False):
        return {"foam": 0, "total": 0}
    foam_scale = as_float(contact_pass.get("channels", {}).get("foam"), 0.0)
    max_count = max(0, as_int(contact_pass.get("max_count"), 256))
    if foam_scale <= 0.0 or max_count <= 0:
        return {"foam": 0, "total": 0}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if count >= max_count:
                break
            if secondary_render_channel(row) == "foam":
                count += 1
    return {"foam": count, "total": count}


def estimate_water_impact_ripple_counts(path, ripple_pass):
    counts = {"foam": 0, "spray": 0, "total": 0}
    if not ripple_pass.get("enabled", False):
        return counts
    channels = ripple_pass.get("channels") if isinstance(ripple_pass.get("channels"), dict) else {}
    max_count = max(0, as_int(ripple_pass.get("max_count"), 128))
    if max_count <= 0:
        return counts
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if counts["total"] >= max_count:
                break
            channel = secondary_render_channel(row)
            if channel not in ("foam", "spray"):
                continue
            if as_float(channels.get(channel), 0.0) <= 0.0:
                continue
            counts[channel] += 1
            counts["total"] += 1
    return counts


def summarize_surface_contact_foam_counts(frames):
    if not frames:
        return {}
    totals = [as_int(frame.get("surface_contact_foam_counts", {}).get("total"), 0) for frame in frames]
    return {
        "first": frames[0].get("surface_contact_foam_counts", {}),
        "last": frames[-1].get("surface_contact_foam_counts", {}),
        "min_total": min(totals),
        "max_total": max(totals),
        "mean_total": sum(totals) / float(len(totals)),
    }


def summarize_water_impact_ripple_counts(frames):
    if not frames:
        return {}
    totals = [as_int(frame.get("water_impact_ripple_counts", {}).get("total"), 0) for frame in frames]
    return {
        "first": frames[0].get("water_impact_ripple_counts", {}),
        "last": frames[-1].get("water_impact_ripple_counts", {}),
        "min_total": min(totals),
        "max_total": max(totals),
        "mean_total": sum(totals) / float(len(totals)),
    }


def pick_water_mesh(frame, water_index, out_index, out_count):
    if water_index:
        water_frame = select_resampled(water_index["frames"], out_index, out_count)
        if water_frame:
            return dict(water_frame)
    mesh = frame.get("water_mesh")
    if not mesh:
        return None
    return {
        "mesh": mesh,
        "frame": frame.get("frame", out_index),
        "source_frame": frame.get("frame", out_index),
        "source_time": frame.get("time", 0.0),
        "vertex_count": frame.get("water_mesh_vertex_count", 0),
        "face_count": frame.get("water_mesh_face_count", 0),
        "occupied_cell_count": 0,
    }


def build_scene_spec(src, out_dir, frame_count, width, height, water_reconstruction_path,
                     engine, samples, max_secondary_particles, secondary_radius_scale,
                     render_preset_name=None, render_preset=None):
    sequence = load_sequence(src, water_reconstruction_path)
    render_preset = render_preset or {}
    renderer_defaults = render_preset.get("renderer", {})
    engine = engine or renderer_defaults.get("engine", "eevee")
    samples = samples if samples is not None else as_int(renderer_defaults.get("samples"), 24)
    max_secondary_particles = (
        max_secondary_particles if max_secondary_particles is not None
        else as_int(renderer_defaults.get("max_secondary_particles"), 512)
    )
    secondary_radius_scale = (
        secondary_radius_scale if secondary_radius_scale is not None
        else as_float(renderer_defaults.get("secondary_radius_scale"), 1.0)
    )
    channel_radius_scales = secondary_channel_radius_summary(render_preset)
    secondary_soft_pass = secondary_soft_pass_summary(render_preset)
    secondary_streak_pass = secondary_streak_pass_summary(render_preset)
    surface_contact_foam_pass = surface_contact_foam_pass_summary(render_preset)
    water_surface_glint_pass = water_surface_glint_pass_summary(render_preset)
    water_reflection_pass = water_reflection_pass_summary(render_preset)
    water_volume_scattering_pass = water_volume_scattering_pass_summary(render_preset)
    water_impact_ripple_pass = water_impact_ripple_pass_summary(render_preset)
    secondary_framing_qa = secondary_framing_qa_summary(render_preset)
    render_dir = os.path.join(out_dir, "frames")
    os.makedirs(render_dir, exist_ok=True)
    frames = []
    for out_index in range(frame_count):
        frame = select_resampled(sequence["frames"], out_index, frame_count)
        water_mesh = pick_water_mesh(frame,
                                     sequence.get("water_reconstruction"),
                                     out_index,
                                     frame_count)
        if not water_mesh:
            fail("sequence does not include water_mesh entries; run reconstruct_water.py and convert_render_cache.py first")
        mesh_path = require_file(water_mesh.get("mesh"), "water_mesh")
        secondary_counts = count_secondary_particles(frame["particles_csv"])
        secondary_streak_counts = estimate_secondary_streak_counts(
            frame["particles_csv"],
            max_secondary_particles,
            secondary_streak_pass)
        surface_contact_foam_counts = estimate_surface_contact_foam_counts(
            frame["particles_csv"],
            surface_contact_foam_pass)
        water_impact_ripple_counts = estimate_water_impact_ripple_counts(
            frame["particles_csv"],
            water_impact_ripple_pass)
        header = {
            "dims": frame.get("header", {}).get("dims", sequence["sequence"].get("dims", [1, 1, 1])),
            "dx": as_float(frame.get("header", {}).get("dx"), as_float(sequence["sequence"].get("dx"), 1.0)),
        }
        frames.append({
            "index": out_index,
            "frame": frame["frame"],
            "time": frame["time"],
            "source_cache": frame.get("source_cache"),
            "camera": apply_camera_preset(frame["camera"], render_preset, out_index, frame_count, header),
            "cinematic": frame.get("cinematic") or {},
            "header": header,
            "water_mesh": mesh_path,
            "water_mesh_vertex_count": as_int(water_mesh.get("vertex_count")),
            "water_mesh_face_count": as_int(water_mesh.get("face_count")),
            "water_mesh_occupied_cell_count": as_int(water_mesh.get("occupied_cell_count")),
            "particles_csv": frame["particles_csv"],
            "particle_count": frame.get("particle_count", 0),
            "secondary_counts": secondary_counts,
            "secondary_streak_counts": secondary_streak_counts,
            "surface_contact_foam_counts": surface_contact_foam_counts,
            "water_impact_ripple_counts": water_impact_ripple_counts,
            "output_png": os.path.abspath(os.path.join(render_dir, f"frame_{out_index:04d}.png")),
        })

    if any(as_int(frame["water_mesh_face_count"]) <= 0 for frame in frames):
        fail("water mesh face counts must be positive for Blender bridge rendering")

    return {
        "bridge": "lsfs_blender_bridge",
        "version": 1,
        "source": os.path.abspath(src),
        "width": width,
        "height": height,
        "engine": engine,
        "samples": samples,
        "max_secondary_particles": max_secondary_particles,
        "secondary_radius_scale": secondary_radius_scale,
        "secondary_channel_radius_scales": channel_radius_scales,
        "secondary_soft_pass": secondary_soft_pass,
        "secondary_streak_pass": secondary_streak_pass,
        "secondary_streak_counts": summarize_secondary_streak_counts(frames),
        "surface_contact_foam_pass": surface_contact_foam_pass,
        "surface_contact_foam_counts": summarize_surface_contact_foam_counts(frames),
        "water_surface_glint_pass": water_surface_glint_pass,
        "water_reflection_pass": water_reflection_pass,
        "water_volume_scattering_pass": water_volume_scattering_pass,
        "water_impact_ripple_pass": water_impact_ripple_pass,
        "water_impact_ripple_counts": summarize_water_impact_ripple_counts(frames),
        "secondary_framing_qa": secondary_framing_qa,
        "secondary_framing": summarize_secondary_framing(frames, width, height, secondary_framing_qa),
        "render_preset_name": render_preset_name,
        "render_preset": render_preset,
        "camera_motion": camera_motion_summary(render_preset),
        "camera_framing": camera_framing_summary(render_preset, frames),
        "camera_path_metrics": camera_path_metrics(frames),
        "water_material": water_material_summary(render_preset),
        "water_surface_detail": water_surface_detail_summary(render_preset),
        "world_units": "cell",
        "sequence_frame_count": len(sequence["frames"]),
        "water_reconstruction": sequence.get("water_reconstruction", {}),
        "frames": frames,
    }


BLENDER_DRIVER = r'''#!/usr/bin/env python
import csv
import json
import math
import os
import sys
import traceback

import bpy
from mathutils import Vector


def read_spec():
    argv = sys.argv
    if "--" not in argv:
        raise RuntimeError("missing -- <scene_spec.json>")
    args = argv[argv.index("--") + 1:]
    if len(args) != 1:
        raise RuntimeError("expected one scene spec path after --")
    with open(args[0], encoding="utf-8") as f:
        return json.load(f)


def to_blender(point):
    return (float(point[0]), -float(point[2]), float(point[1]))


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def remove_frame_assets():
    doomed = [obj for obj in bpy.context.scene.objects if obj.get("lsfs_frame_asset")]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)


def set_input(node, names, value):
    for name in names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return True
    return False


def preset_section(preset, name):
    value = preset.get(name, {})
    return value if isinstance(value, dict) else {}


def vector_value(value, fallback, length=None):
    if isinstance(value, (list, tuple)):
        target_len = length or len(fallback)
        if len(value) >= target_len:
            out = []
            for i in range(target_len):
                try:
                    out.append(float(value[i]))
                except (TypeError, ValueError):
                    return tuple(fallback)
            return tuple(out)
    return tuple(fallback)


def scalar_value(value, fallback):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def blend_color(a, b, t):
    t = clamp01(t)
    return tuple(float(a[i]) * (1.0 - t) + float(b[i]) * t for i in range(4))


def material_values(preset, name, color, roughness, alpha, transmission):
    cfg = preset_section(preset_section(preset, "materials"), name)
    return {
        "color": vector_value(cfg.get("base_color"), color, 4),
        "depth_color": vector_value(cfg.get("depth_color"), color, 4),
        "depth_strength": clamp01(scalar_value(cfg.get("depth_strength"), 0.0)),
        "rim_color": vector_value(cfg.get("rim_color"), (0.82, 0.96, 1.0, 0.8), 4),
        "rim_strength": max(0.0, scalar_value(cfg.get("rim_strength"), 0.0)),
        "rim_width": clamp01(scalar_value(cfg.get("rim_width"), 0.0)),
        "specular": max(0.0, scalar_value(cfg.get("specular"), 0.5)),
        "coat_weight": max(0.0, scalar_value(cfg.get("coat_weight"), 0.0)),
        "roughness": scalar_value(cfg.get("roughness"), roughness),
        "alpha": scalar_value(cfg.get("alpha"), alpha),
        "transmission": scalar_value(cfg.get("transmission"), transmission),
        "emission_color": vector_value(cfg.get("emission_color"), color, 4),
        "emission_strength": max(0.0, scalar_value(cfg.get("emission_strength"), 0.0)),
    }


def make_principled_material(name, color, roughness=0.2, alpha=1.0, transmission=0.0,
                             emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        set_input(bsdf, ("Base Color",), color)
        set_input(bsdf, ("Alpha",), alpha)
        set_input(bsdf, ("Roughness",), roughness)
        set_input(bsdf, ("Transmission Weight", "Transmission"), transmission)
        set_input(bsdf, ("Metallic",), 0.0)
        if emission_strength > 0.0:
            set_input(bsdf, ("Emission Color",), emission_color or color)
            set_input(bsdf, ("Emission Strength",), emission_strength)
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = True
    return mat


def make_water_material(name, values):
    body_color = blend_color(values["color"], values["depth_color"], values["depth_strength"])
    mat = make_principled_material(name,
                                   body_color,
                                   roughness=values["roughness"],
                                   alpha=values["alpha"],
                                   transmission=values["transmission"])
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return mat
    set_input(bsdf, ("Specular IOR Level", "Specular"), values["specular"])
    set_input(bsdf, ("Coat Weight", "Coat"), values["coat_weight"])
    if values["rim_strength"] > 0.0:
        try:
            layer = mat.node_tree.nodes.new(type="ShaderNodeLayerWeight")
            ramp = mat.node_tree.nodes.new(type="ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = 0.0
            ramp.color_ramp.elements[0].color = values["rim_color"]
            ramp.color_ramp.elements[1].position = max(0.02, values["rim_width"])
            ramp.color_ramp.elements[1].color = body_color
            mat.node_tree.links.new(layer.outputs["Facing"], ramp.inputs["Fac"])
            mat.node_tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
            set_input(bsdf, ("Emission Color",), values["rim_color"])
            set_input(bsdf, ("Emission Strength",), values["rim_strength"] * 0.08)
        except Exception:
            set_input(bsdf, ("Base Color",), body_color)
    return mat


def scaled_particle_values(values, alpha_scale=1.0, emission_scale=1.0):
    out = dict(values)
    color = list(out["color"])
    color[3] = clamp01(color[3] * max(0.0, alpha_scale))
    out["color"] = tuple(color)
    emission = list(out["emission_color"])
    emission[3] = clamp01(emission[3] * max(0.0, alpha_scale))
    out["emission_color"] = tuple(emission)
    out["alpha"] = clamp01(out["alpha"] * max(0.0, alpha_scale))
    out["emission_strength"] = max(0.0, out["emission_strength"] * max(0.0, emission_scale))
    out["roughness"] = min(1.0, max(out["roughness"], 0.65))
    out["transmission"] = 0.0
    return out


def scaled_overlay_values(values, alpha_scale=1.0, emission_scale=1.0):
    out = dict(values)
    color = list(out["color"])
    color[3] = clamp01(color[3] * max(0.0, alpha_scale))
    out["color"] = tuple(color)
    emission = list(out["emission_color"])
    emission[3] = clamp01(emission[3] * max(0.0, alpha_scale))
    out["emission_color"] = tuple(emission)
    out["alpha"] = clamp01(out["alpha"] * max(0.0, alpha_scale))
    out["emission_strength"] = max(0.0, out["emission_strength"] * max(0.0, emission_scale))
    return out


def surface_detail_values(preset):
    detail = preset_section(preset_section(preset, "renderer"), "water_surface_detail")
    return {
        "enabled": bool(detail.get("enabled", False)),
        "strength": max(0.0, scalar_value(detail.get("strength"), 0.0)),
        "scale": max(0.01, scalar_value(detail.get("scale"), 3.0)),
        "depth": max(1, int(scalar_value(detail.get("depth"), 3))),
    }


def configure_engine(scene, engine, samples):
    choices = ["CYCLES"] if engine == "cycles" else ["BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"]
    for choice in choices:
        try:
            scene.render.engine = choice
            break
        except TypeError:
            continue
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = max(1, int(samples))
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = max(1, int(samples))


def configure_scene(spec):
    scene = bpy.context.scene
    preset = spec.get("render_preset") or {}
    tone = preset_section(preset, "tone_mapping")
    lighting = preset_section(preset, "lighting")
    scene.render.resolution_x = int(spec["width"])
    scene.render.resolution_y = int(spec["height"])
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    configure_engine(scene, spec.get("engine", "eevee"), spec.get("samples", 24))
    try:
        scene.view_settings.view_transform = tone.get("view_transform", "Filmic")
        scene.view_settings.look = tone.get("look", "Medium High Contrast")
        scene.view_settings.exposure = scalar_value(tone.get("exposure"), 0.0)
        scene.view_settings.gamma = scalar_value(tone.get("gamma"), 1.0)
    except TypeError:
        pass
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = vector_value(lighting.get("world_color"), (0.02, 0.025, 0.032), 3)


def make_camera():
    camera_data = bpy.data.cameras.new("LSFS Camera")
    camera = bpy.data.objects.new("LSFS Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def look_at(obj, target):
    direction = Vector(target) - Vector(obj.location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_camera(camera, frame, preset):
    cam = dict(frame["camera"])
    if not cam.get("preset_applied"):
        preset_camera = preset_section(preset, "camera")
        for key, value in preset_camera.items():
            if key != "motion":
                cam[key] = value
    camera.location = to_blender(cam["position"])
    target = to_blender(cam["target"])
    look_at(camera, target)
    camera.data.lens = float(cam.get("focal_length_mm", 50.0))
    vfov = float(cam.get("vertical_fov_degrees", 0.0))
    if vfov > 0.0:
        camera.data.angle = math.radians(vfov)
    camera.data.clip_start = max(0.001, float(cam.get("near_clip", 0.05)))
    camera.data.clip_end = max(1.0, float(cam.get("far_clip", 500.0)))


def add_lights(preset):
    lighting = preset_section(preset, "lighting")
    key_cfg = preset_section(lighting, "key_area")
    sun_cfg = preset_section(lighting, "sun")
    key_location = vector_value(key_cfg.get("location"), (3.0, -12.0, 20.0), 3)
    bpy.ops.object.light_add(type="AREA", location=key_location)
    key = bpy.context.object
    key.name = "LSFS Key Area"
    key.data.energy = scalar_value(key_cfg.get("energy"), 450.0)
    key.data.size = scalar_value(key_cfg.get("size"), 7.0)
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 12.0))
    sun = bpy.context.object
    sun.name = "LSFS Sun"
    sun.data.energy = scalar_value(sun_cfg.get("energy"), 1.3)
    sun_rotation = vector_value(sun_cfg.get("rotation_degrees"), (40.0, 0.0, 30.0), 3)
    sun.rotation_euler = tuple(math.radians(v) for v in sun_rotation)


def add_floor(frame, material, preset):
    floor_cfg = preset_section(preset_section(preset, "lighting"), "floor")
    if floor_cfg.get("enabled", True) is False:
        return
    dims = frame.get("header", {}).get("dims", [10, 10, 10])
    dx = float(frame.get("header", {}).get("dx", 1.0))
    size = max(float(dims[0]), float(dims[2]), 1.0) * dx * scalar_value(floor_cfg.get("scale"), 1.3)
    bpy.ops.mesh.primitive_plane_add(size=size, location=(float(dims[0]) * dx * 0.5,
                                                         -float(dims[2]) * dx * 0.5,
                                                         -0.015))
    floor = bpy.context.object
    floor.name = "LSFS Matte Floor"
    floor.data.materials.append(material)


def import_obj(path):
    before = set(bpy.data.objects)
    try:
        bpy.ops.wm.obj_import(filepath=path)
    except Exception:
        bpy.ops.import_scene.obj(filepath=path)
    after = set(bpy.data.objects)
    objects = list(after - before)
    if not objects and bpy.context.selected_objects:
        objects = list(bpy.context.selected_objects)
    return objects


def apply_surface_detail(obj, detail, frame_index):
    if not detail.get("enabled") or detail.get("strength", 0.0) <= 0.0:
        return
    try:
        tex = bpy.data.textures.new(f"LSFS Water Detail {frame_index}", type="VORONOI")
        tex.noise_scale = float(detail.get("scale", 3.0))
        tex.intensity = 0.35
        mod = obj.modifiers.new("LSFS surface detail", type="DISPLACE")
        mod.strength = float(detail.get("strength", 0.0))
        mod.texture = tex
    except Exception:
        return


def add_water_mesh(frame, material, detail):
    objects = import_obj(frame["water_mesh"])
    for obj in objects:
        obj.name = "LSFS Water"
        obj["lsfs_frame_asset"] = True
        obj.rotation_euler[0] = math.radians(90.0)
        if hasattr(obj.data, "polygons"):
            for poly in obj.data.polygons:
                poly.use_smooth = True
        apply_surface_detail(obj, detail, int(frame.get("index", 0)))
        obj.data.materials.append(material)
    return len(objects)


def secondary_channel(row):
    channel = row.get("render_channel", "")
    if channel in ("droplet", "spray", "foam", "bubble"):
        return channel
    kind = row.get("kind", "")
    return "bubble" if kind == "secondary_bubble" else "droplet"


def channel_radius_scale(channel, scales):
    try:
        return max(0.01, float(scales.get(channel, 1.0)))
    except Exception:
        return 1.0


def add_secondary_particles(frame, materials, max_count, radius_scale, channel_scales):
    path = frame.get("particles_csv")
    if not path or not os.path.isfile(path) or max_count <= 0:
        return 0
    count = 0
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            kind = row.get("kind", "")
            channel = row.get("render_channel", "")
            if kind not in ("secondary_droplet", "secondary_bubble") and channel not in materials:
                continue
            if count >= max_count:
                break
            pos = (float(row.get("x", 0.0)), float(row.get("y", 0.0)), float(row.get("z", 0.0)))
            volume = max(0.05, float(row.get("volume", 1.0)))
            base_radius = min(0.14, max(0.035, 0.035 * math.sqrt(volume)))
            channel = secondary_channel(row)
            channel_scale = channel_radius_scale(channel, channel_scales)
            radius = min(0.55, max(0.02, base_radius * max(0.01, radius_scale) * channel_scale))
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8,
                                                 ring_count=4,
                                                 radius=radius,
                                                 location=to_blender(pos))
            sphere = bpy.context.object
            sphere.name = "LSFS Secondary"
            sphere["lsfs_frame_asset"] = True
            sphere.data.materials.append(materials.get(channel, materials["droplet"]))
            count += 1
    return count


def secondary_soft_pass_values(spec):
    cfg = spec.get("secondary_soft_pass") or {}
    channels = cfg.get("channels") if isinstance(cfg.get("channels"), dict) else {}
    falloff = cfg.get("falloff", [1.0, 0.45, 0.16, 0.04])
    if not isinstance(falloff, list) or not falloff:
        falloff = [1.0, 0.45, 0.16, 0.04]
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "spray": max(0.0, scalar_value(channels.get("spray"), 0.0)),
            "foam": max(0.0, scalar_value(channels.get("foam"), 0.0)),
        },
        "max_radius": max(0.01, scalar_value(cfg.get("max_radius"), 1.0)),
        "geometry": str(cfg.get("geometry", "batched_spheres")),
        "falloff": [max(0.0, scalar_value(item, 0.0)) for item in falloff],
        "material_falloff": str(cfg.get("material_falloff", "ring_materials")),
    }


def secondary_streak_pass_values(spec):
    cfg = spec.get("secondary_streak_pass") or {}
    channels = cfg.get("channels") if isinstance(cfg.get("channels"), dict) else {}
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "spray": max(0.0, scalar_value(channels.get("spray"), 0.0)),
            "foam": max(0.0, scalar_value(channels.get("foam"), 0.0)),
        },
        "length_scale": max(0.0, scalar_value(cfg.get("length_scale"), 0.04)),
        "max_length": max(0.01, scalar_value(cfg.get("max_length"), 1.0)),
        "width_scale": max(0.01, scalar_value(cfg.get("width_scale"), 0.45)),
        "min_speed": max(0.0, scalar_value(cfg.get("min_speed"), 0.35)),
    }


def surface_contact_foam_pass_values(spec):
    cfg = spec.get("surface_contact_foam_pass") or {}
    channels = cfg.get("channels") if isinstance(cfg.get("channels"), dict) else {}
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "foam": max(0.0, scalar_value(channels.get("foam"), 0.0)),
        },
        "max_count": max(0, int(scalar_value(cfg.get("max_count"), 256))),
        "radius_x": max(0.01, scalar_value(cfg.get("radius_x"), 0.7)),
        "radius_z": max(0.01, scalar_value(cfg.get("radius_z"), 0.22)),
        "vertical_offset": scalar_value(cfg.get("vertical_offset"), -1.2),
        "flow_aligned": bool(cfg.get("flow_aligned", False)),
        "flow_center": vector_value(cfg.get("flow_center"), (14.0, 0.0, 11.0), 3),
        "material_falloff": str(cfg.get("material_falloff", "solid")),
    }


def water_surface_glint_pass_values(spec):
    cfg = spec.get("water_surface_glint_pass") or {}
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "count": max(0, int(scalar_value(cfg.get("count"), 0))),
        "region_min": vector_value(cfg.get("region_min"), (1.0, 4.8, 3.0), 3),
        "region_max": vector_value(cfg.get("region_max"), (27.0, 8.2, 19.0), 3),
        "length": max(0.01, scalar_value(cfg.get("length"), 1.35)),
        "width": max(0.001, scalar_value(cfg.get("width"), 0.035)),
        "flow_dir": vector_value(cfg.get("flow_dir"), (1.0, 0.0, 0.18), 3),
        "drift_per_frame": scalar_value(cfg.get("drift_per_frame"), 0.08),
        "alpha_scale": max(0.0, scalar_value(cfg.get("alpha_scale"), 0.22)),
        "emission_scale": max(0.0, scalar_value(cfg.get("emission_scale"), 0.45)),
    }


def water_reflection_pass_values(spec):
    cfg = spec.get("water_reflection_pass") or {}
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "count": max(0, int(scalar_value(cfg.get("count"), 0))),
        "region_min": vector_value(cfg.get("region_min"), (1.0, 4.7, 3.0), 3),
        "region_max": vector_value(cfg.get("region_max"), (27.0, 8.0, 19.0), 3),
        "length": max(0.01, scalar_value(cfg.get("length"), 3.8)),
        "width": max(0.001, scalar_value(cfg.get("width"), 0.075)),
        "flow_dir": vector_value(cfg.get("flow_dir"), (1.0, 0.0, 0.14), 3),
        "drift_per_frame": scalar_value(cfg.get("drift_per_frame"), 0.035),
        "alpha_scale": max(0.0, scalar_value(cfg.get("alpha_scale"), 0.18)),
        "emission_scale": max(0.0, scalar_value(cfg.get("emission_scale"), 0.32)),
    }


def water_volume_scattering_pass_values(spec):
    cfg = spec.get("water_volume_scattering_pass") or {}
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "layers": max(0, int(scalar_value(cfg.get("layers"), 0))),
        "region_min": vector_value(cfg.get("region_min"), (1.0, 4.5, 3.2), 3),
        "region_max": vector_value(cfg.get("region_max"), (27.0, 7.8, 19.0), 3),
        "inset": max(0.0, scalar_value(cfg.get("inset"), 0.15)),
        "alpha_scale": max(0.0, scalar_value(cfg.get("alpha_scale"), 0.22)),
        "emission_scale": max(0.0, scalar_value(cfg.get("emission_scale"), 0.18)),
    }


def water_impact_ripple_pass_values(spec):
    cfg = spec.get("water_impact_ripple_pass") or {}
    channels = cfg.get("channels") if isinstance(cfg.get("channels"), dict) else {}
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "channels": {
            "foam": max(0.0, scalar_value(channels.get("foam"), 0.0)),
            "spray": max(0.0, scalar_value(channels.get("spray"), 0.0)),
        },
        "max_count": max(0, int(scalar_value(cfg.get("max_count"), 128))),
        "ring_count": max(1, int(scalar_value(cfg.get("ring_count"), 2))),
        "segments": max(4, int(scalar_value(cfg.get("segments"), 18))),
        "arc_fraction": min(1.0, max(0.08, scalar_value(cfg.get("arc_fraction"), 0.62))),
        "radius": max(0.01, scalar_value(cfg.get("radius"), 0.48)),
        "radius_step": max(0.0, scalar_value(cfg.get("radius_step"), 0.28)),
        "width": max(0.001, scalar_value(cfg.get("width"), 0.035)),
        "vertical_offset": scalar_value(cfg.get("vertical_offset"), -1.78),
        "flow_center": vector_value(cfg.get("flow_center"), (14.0, 0.0, 11.0), 3),
        "material_falloff": str(cfg.get("material_falloff", "solid")),
        "alpha_scale": max(0.0, scalar_value(cfg.get("alpha_scale"), 0.26)),
        "emission_scale": max(0.0, scalar_value(cfg.get("emission_scale"), 0.42)),
    }


def hash01(index, salt):
    value = math.sin(index * 12.9898 + salt * 78.233) * 43758.5453
    return value - math.floor(value)


def flow_strip_axes(flow):
    flow_xz = Vector((float(flow[0]), -float(flow[2]), 0.0))
    if flow_xz.length <= 1e-8:
        flow_xz = Vector((1.0, 0.0, 0.0))
    direction = flow_xz.normalized()
    side = Vector((-direction.y, direction.x, 0.0))
    return direction, side


def add_flow_strip_mesh(name, strips, material):
    verts = []
    faces = []
    for center, direction, side, length, width in strips:
        center_vec = Vector(center)
        half_len = max(0.001, float(length)) * 0.5
        half_width = max(0.001, float(width)) * 0.5
        base = len(verts)
        start = center_vec - direction * half_len
        end = center_vec + direction * half_len
        verts.extend([
            tuple(start - side * half_width),
            tuple(start + side * half_width),
            tuple(end + side * half_width),
            tuple(end - side * half_width),
        ])
        faces.append((base, base + 1, base + 2, base + 3))
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    obj.data.materials.append(material)
    return obj


def add_water_volume_scattering_pass(frame, material, scattering_pass):
    if not scattering_pass.get("enabled", False):
        return 0
    layers = int(scattering_pass.get("layers", 0))
    if layers <= 0:
        return 0
    region_min = scattering_pass.get("region_min", (1.0, 4.5, 3.2))
    region_max = scattering_pass.get("region_max", (27.0, 7.8, 19.0))
    xmin, ymin, zmin = (float(region_min[0]), float(region_min[1]), float(region_min[2]))
    xmax, ymax, zmax = (float(region_max[0]), float(region_max[1]), float(region_max[2]))
    if xmax <= xmin or ymax <= ymin or zmax <= zmin:
        return 0
    inset = max(0.0, float(scattering_pass.get("inset", 0.15)))
    max_inset = min((xmax - xmin) * 0.45, (zmax - zmin) * 0.45)
    inset = min(inset, max_inset)
    verts = []
    faces = []
    for layer in range(layers):
        t = (layer + 0.5) / float(layers)
        y = ymin + (ymax - ymin) * t
        layer_inset = inset * (0.65 + 0.7 * hash01(layer, 31.0))
        x0 = xmin + layer_inset
        x1 = xmax - layer_inset
        z0 = zmin + layer_inset
        z1 = zmax - layer_inset
        if x1 <= x0 or z1 <= z0:
            continue
        base = len(verts)
        verts.extend([
            to_blender((x0, y, z0)),
            to_blender((x1, y, z0)),
            to_blender((x1, y, z1)),
            to_blender((x0, y, z1)),
        ])
        faces.append((base, base + 1, base + 2, base + 3))
    if not faces:
        return 0
    mesh = bpy.data.meshes.new("LSFS Water Volume Scattering Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("LSFS Water Volume Scattering", mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    obj.data.materials.append(material)
    return len(faces)


def add_water_surface_glint_pass(frame, material, glint_pass):
    if not glint_pass.get("enabled", False):
        return 0
    count = int(glint_pass.get("count", 0))
    if count <= 0:
        return 0
    region_min = glint_pass.get("region_min", (1.0, 4.8, 3.0))
    region_max = glint_pass.get("region_max", (27.0, 8.2, 19.0))
    flow = glint_pass.get("flow_dir", (1.0, 0.0, 0.18))
    direction, side = flow_strip_axes(flow)
    length = float(glint_pass.get("length", 1.35))
    width = float(glint_pass.get("width", 0.035))
    drift = float(glint_pass.get("drift_per_frame", 0.08)) * int(frame.get("index", 0))
    strokes = []
    for index in range(count):
        tx = (hash01(index, 1.0) + drift * 0.07) % 1.0
        ty = hash01(index, 2.0)
        tz = (hash01(index, 3.0) + drift * 0.11) % 1.0
        x = float(region_min[0]) + (float(region_max[0]) - float(region_min[0])) * tx
        y = float(region_min[1]) + (float(region_max[1]) - float(region_min[1])) * ty
        z = float(region_min[2]) + (float(region_max[2]) - float(region_min[2])) * tz
        scale = 0.55 + hash01(index, 4.0) * 0.75
        strokes.append((to_blender((x, y, z)), direction, side, length * scale, width))
    add_flow_strip_mesh("LSFS Water Surface Glints", strokes, material)
    return len(strokes)


def add_water_reflection_pass(frame, material, reflection_pass):
    if not reflection_pass.get("enabled", False):
        return 0
    count = int(reflection_pass.get("count", 0))
    if count <= 0:
        return 0
    region_min = reflection_pass.get("region_min", (1.0, 4.7, 3.0))
    region_max = reflection_pass.get("region_max", (27.0, 8.0, 19.0))
    direction, side = flow_strip_axes(reflection_pass.get("flow_dir", (1.0, 0.0, 0.14)))
    length = float(reflection_pass.get("length", 3.8))
    width = float(reflection_pass.get("width", 0.075))
    drift = float(reflection_pass.get("drift_per_frame", 0.035)) * int(frame.get("index", 0))
    strips = []
    for index in range(count):
        tx = (hash01(index, 11.0) + drift * 0.025) % 1.0
        ty = 0.35 + hash01(index, 12.0) * 0.65
        tz = (hash01(index, 13.0) + drift * 0.055) % 1.0
        x = float(region_min[0]) + (float(region_max[0]) - float(region_min[0])) * tx
        y = float(region_min[1]) + (float(region_max[1]) - float(region_min[1])) * ty
        z = float(region_min[2]) + (float(region_max[2]) - float(region_min[2])) * tz
        strip_length = length * (0.65 + hash01(index, 14.0) * 0.8)
        strip_width = width * (0.7 + hash01(index, 15.0) * 0.7)
        strips.append((to_blender((x, y, z)), direction, side, strip_length, strip_width))
    add_flow_strip_mesh("LSFS Water Reflection Ribbons", strips, material)
    return len(strips)


def add_water_impact_ripple_pass(frame, material, ripple_pass):
    if not ripple_pass.get("enabled", False):
        return 0
    max_count = int(ripple_pass.get("max_count", 0))
    if max_count <= 0:
        return 0
    path = frame.get("particles_csv")
    if not path or not os.path.isfile(path):
        return 0
    channels = ripple_pass.get("channels", {})
    vertical_offset = float(ripple_pass.get("vertical_offset", -1.78))
    flow_center = ripple_pass.get("flow_center", (14.0, 0.0, 11.0))
    base_radius = float(ripple_pass.get("radius", 0.48))
    radius_step = float(ripple_pass.get("radius_step", 0.28))
    width = float(ripple_pass.get("width", 0.035))
    ring_count = int(ripple_pass.get("ring_count", 2))
    arc_fraction = float(ripple_pass.get("arc_fraction", 0.62))
    segments = int(ripple_pass.get("segments", 18))
    arcs = []
    count = 0
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if count >= max_count:
                break
            channel = secondary_channel(row)
            channel_scale = float(channels.get(channel, 0.0) or 0.0)
            if channel not in ("foam", "spray") or channel_scale <= 0.0:
                continue
            x = float(row.get("x", 0.0))
            y = float(row.get("y", 0.0)) + vertical_offset
            z = float(row.get("z", 0.0))
            vx = float(row.get("vx", 0.0))
            vz = float(row.get("vz", 0.0))
            horizontal_speed = math.sqrt(vx * vx + vz * vz)
            if horizontal_speed > 1e-5:
                direction = (vx / horizontal_speed, vz / horizontal_speed)
            else:
                dx = x - float(flow_center[0])
                dz = z - float(flow_center[2])
                radial = math.sqrt(dx * dx + dz * dz)
                direction = (dx / radial, dz / radial) if radial > 1e-5 else (1.0, 0.0)
            axis_x = Vector((float(direction[0]), -float(direction[1]), 0.0))
            if axis_x.length <= 1e-8:
                axis_x = Vector((1.0, 0.0, 0.0))
            axis_x = axis_x.normalized()
            axis_z = Vector((-axis_x.y, axis_x.x, 0.0))
            volume = max(0.05, float(row.get("volume", 1.0)))
            volume_scale = 0.72 + min(0.9, math.sqrt(volume) * 0.12)
            center = to_blender((x, y, z))
            for ring in range(ring_count):
                ring_radius = (base_radius + radius_step * ring) * volume_scale * channel_scale
                ring_width = width * (1.0 + ring * 0.18)
                sweep = max(0.2, min(2.0 * math.pi, 2.0 * math.pi * arc_fraction * (1.0 - ring * 0.08)))
                arcs.append((center, axis_x, axis_z, ring_radius, ring_width, sweep))
            count += 1
    if arcs:
        add_water_impact_ripple_mesh("LSFS Impact Ripple Cues", arcs, material, segments)
    return count


def add_water_impact_ripple_mesh(name, arcs, material, segments):
    verts = []
    vert_uvs = []
    faces = []
    segments = max(4, int(segments))
    for center, axis_x, axis_z, radius, width, sweep in arcs:
        center_vec = Vector(center)
        inner = max(0.001, float(radius) - float(width) * 0.5)
        outer = max(inner + 0.001, float(radius) + float(width) * 0.5)
        base = len(verts)
        for seg in range(segments + 1):
            t = -float(sweep) * 0.5 + float(sweep) * seg / float(segments)
            c = math.cos(t)
            s = math.sin(t)
            u = seg / float(segments)
            verts.append(tuple(center_vec + axis_x * (c * inner) + axis_z * (s * inner)))
            vert_uvs.append((u, 0.0))
            verts.append(tuple(center_vec + axis_x * (c * outer) + axis_z * (s * outer)))
            vert_uvs.append((u, 1.0))
        for seg in range(segments):
            i0 = base + seg * 2
            i1 = i0 + 1
            i2 = i0 + 3
            i3 = i0 + 2
            faces.append((i0, i1, i2, i3))
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if vert_uvs:
        uv_layer = mesh.uv_layers.new(name="ImpactRippleFalloffUV")
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                uv_layer.data[loop_index].uv = vert_uvs[vertex_index]
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    obj.data.materials.append(material)
    return obj


def add_surface_contact_foam_pass(frame, material, contact_pass):
    if not contact_pass.get("enabled", False):
        return 0
    foam_scale = float(contact_pass.get("channels", {}).get("foam", 0.0) or 0.0)
    max_count = int(contact_pass.get("max_count", 0))
    path = frame.get("particles_csv")
    if foam_scale <= 0.0 or max_count <= 0 or not path or not os.path.isfile(path):
        return 0
    patches = []
    vertical_offset = float(contact_pass.get("vertical_offset", -1.2))
    radius_x = float(contact_pass.get("radius_x", 0.7))
    radius_z = float(contact_pass.get("radius_z", 0.22))
    flow_aligned = bool(contact_pass.get("flow_aligned", False))
    flow_center = contact_pass.get("flow_center", (14.0, 0.0, 11.0))
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if len(patches) >= max_count:
                break
            if secondary_channel(row) != "foam":
                continue
            volume = max(0.05, float(row.get("volume", 1.0)))
            scale = max(0.45, min(1.35, math.sqrt(volume) * 0.55)) * foam_scale
            pos = (
                float(row.get("x", 0.0)),
                float(row.get("y", 0.0)) + vertical_offset,
                float(row.get("z", 0.0)),
            )
            direction = (1.0, 0.0)
            if flow_aligned:
                vx = float(row.get("vx", 0.0))
                vz = float(row.get("vz", 0.0))
                horizontal_speed = math.sqrt(vx * vx + vz * vz)
                if horizontal_speed > 1e-5:
                    direction = (vx / horizontal_speed, vz / horizontal_speed)
                else:
                    dx = pos[0] - float(flow_center[0])
                    dz = pos[2] - float(flow_center[2])
                    radial = math.sqrt(dx * dx + dz * dz)
                    if radial > 1e-5:
                        direction = (dx / radial, dz / radial)
            patches.append((to_blender(pos), direction, radius_x * scale, radius_z * scale))
    if patches:
        add_surface_contact_foam_mesh("LSFS Surface Contact Foam", patches, material)
    return len(patches)


def add_surface_contact_foam_mesh(name, patches, material, segments=14):
    verts = []
    vert_uvs = []
    faces = []
    segments = max(6, int(segments))
    for center, direction, radius_x, radius_z in patches:
        center_vec = Vector(center)
        axis_x = Vector((float(direction[0]), -float(direction[1]), 0.0))
        if axis_x.length <= 1e-8:
            axis_x = Vector((1.0, 0.0, 0.0))
        axis_x = axis_x.normalized()
        axis_z = Vector((-axis_x.y, axis_x.x, 0.0))
        base = len(verts)
        verts.append(tuple(center_vec))
        vert_uvs.append((0.5, 0.5))
        for seg in range(segments):
            theta = 2.0 * math.pi * seg / float(segments)
            p = center_vec + axis_x * (math.cos(theta) * radius_x) + axis_z * (math.sin(theta) * radius_z)
            verts.append(tuple(p))
            vert_uvs.append((0.5 + math.cos(theta) * 0.5, 0.5 + math.sin(theta) * 0.5))
        for seg in range(segments):
            faces.append((base, base + 1 + seg, base + 1 + ((seg + 1) % segments)))
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if vert_uvs:
        uv_layer = mesh.uv_layers.new(name="ContactFoamFalloffUV")
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                uv_layer.data[loop_index].uv = vert_uvs[vertex_index]
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    obj.data.materials.append(material)
    return obj


def add_secondary_soft_pass(frame, materials, max_count, radius_scale, channel_scales, soft_pass):
    if not soft_pass.get("enabled", False):
        return 0
    path = frame.get("particles_csv")
    if not path or not os.path.isfile(path) or max_count <= 0:
        return 0
    count = 0
    by_channel = {"spray": [], "foam": []}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if count >= max_count:
                break
            channel = secondary_channel(row)
            soft_scale = float(soft_pass.get("channels", {}).get(channel, 0.0) or 0.0)
            if soft_scale <= 0.0 or f"{channel}_soft" not in materials:
                continue
            pos = (float(row.get("x", 0.0)), float(row.get("y", 0.0)), float(row.get("z", 0.0)))
            volume = max(0.05, float(row.get("volume", 1.0)))
            base_radius = min(0.14, max(0.035, 0.035 * math.sqrt(volume)))
            channel_scale = channel_radius_scale(channel, channel_scales)
            core_radius = min(0.55, max(0.02, base_radius * max(0.01, radius_scale) * channel_scale))
            radius = min(float(soft_pass.get("max_radius", 1.0)), max(core_radius, core_radius * soft_scale))
            by_channel[channel].append((to_blender(pos), radius))
            count += 1
    for channel, particles in by_channel.items():
        if particles:
            if soft_pass.get("geometry") == "billboard_disks":
                add_billboard_cloud_mesh(f"LSFS {channel.title()} Mist Disks",
                                         particles,
                                         materials.get(f"{channel}_soft_falloff", [materials[f"{channel}_soft"]]),
                                         frame,
                                         segments=12,
                                         falloff=soft_pass.get("falloff", [1.0, 0.45, 0.16, 0.04]))
            else:
                add_sphere_cloud_mesh(f"LSFS {channel.title()} Soft Cloud",
                                      particles,
                                      materials[f"{channel}_soft"],
                                      segments=8,
                                      rings=4)
    return count


def to_blender_vec(vec):
    return Vector((float(vec[0]), -float(vec[2]), float(vec[1])))


def add_secondary_streak_pass(frame, materials, max_count, radius_scale, channel_scales, streak_pass):
    if not streak_pass.get("enabled", False):
        return 0
    path = frame.get("particles_csv")
    if not path or not os.path.isfile(path) or max_count <= 0:
        return 0
    count = 0
    by_channel = {"spray": [], "foam": []}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if count >= max_count:
                break
            channel = secondary_channel(row)
            channel_mult = float(streak_pass.get("channels", {}).get(channel, 0.0) or 0.0)
            if channel_mult <= 0.0 or f"{channel}_streak" not in materials:
                continue
            velocity = (
                float(row.get("vx", 0.0)),
                float(row.get("vy", 0.0)),
                float(row.get("vz", 0.0)),
            )
            speed = math.sqrt(sum(v * v for v in velocity))
            if speed < float(streak_pass.get("min_speed", 0.0)):
                continue
            pos = (float(row.get("x", 0.0)), float(row.get("y", 0.0)), float(row.get("z", 0.0)))
            volume = max(0.05, float(row.get("volume", 1.0)))
            base_radius = min(0.14, max(0.035, 0.035 * math.sqrt(volume)))
            channel_scale = channel_radius_scale(channel, channel_scales)
            core_radius = min(0.55, max(0.02, base_radius * max(0.01, radius_scale) * channel_scale))
            length = min(float(streak_pass.get("max_length", 1.0)),
                         max(core_radius, speed * float(streak_pass.get("length_scale", 0.04)) * channel_mult))
            width = max(0.01, core_radius * float(streak_pass.get("width_scale", 0.45)))
            by_channel[channel].append((to_blender(pos), to_blender_vec(velocity), length, width))
            count += 1
    for channel, particles in by_channel.items():
        if particles:
            add_streak_cloud_mesh(f"LSFS {channel.title()} Velocity Streaks",
                                  particles,
                                  materials[f"{channel}_streak"],
                                  frame)
    return count


def safe_normalized(vec, fallback):
    try:
        if vec.length > 1e-8:
            return vec.normalized()
    except Exception:
        pass
    return Vector(fallback)


def billboard_axes(frame, center):
    cam = frame.get("camera", {})
    camera_pos = Vector(to_blender(cam.get("position", [0.0, 0.0, 1.0])))
    forward = safe_normalized(camera_pos - Vector(center), (0.0, 0.0, 1.0))
    world_up = Vector((0.0, 0.0, 1.0))
    right = forward.cross(world_up)
    if right.length <= 1e-8:
        right = forward.cross(Vector((0.0, 1.0, 0.0)))
    right = safe_normalized(right, (1.0, 0.0, 0.0))
    up = safe_normalized(right.cross(forward), (0.0, 0.0, 1.0))
    return right, up


def add_streak_cloud_mesh(name, particles, material, frame):
    verts = []
    faces = []
    for center, velocity, length, width in particles:
        center_vec = Vector(center)
        camera_pos = Vector(to_blender(frame.get("camera", {}).get("position", [0.0, 0.0, 1.0])))
        forward = safe_normalized(camera_pos - center_vec, (0.0, 0.0, 1.0))
        direction = velocity - forward * velocity.dot(forward)
        direction = safe_normalized(direction, (1.0, 0.0, 0.0))
        side = safe_normalized(direction.cross(forward), (0.0, 0.0, 1.0))
        half_len = max(0.001, float(length)) * 0.5
        half_width = max(0.001, float(width)) * 0.5
        base = len(verts)
        start = center_vec - direction * half_len
        end = center_vec + direction * half_len
        verts.extend([
            tuple(start - side * half_width),
            tuple(start + side * half_width),
            tuple(end + side * half_width),
            tuple(end - side * half_width),
        ])
        faces.append((base, base + 1, base + 2, base + 3))
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    obj.data.materials.append(material)
    return obj


def add_billboard_cloud_mesh(name, particles, materials, frame, segments=10, falloff=None):
    verts = []
    vert_uvs = []
    faces = []
    material_indices = []
    segments = max(5, int(segments))
    falloff = falloff if isinstance(falloff, list) and falloff else [1.0, 0.45, 0.16, 0.04]
    ring_count = max(2, len(falloff))
    for center, radius in particles:
        base = len(verts)
        center_vec = Vector(center)
        radius = max(0.001, float(radius))
        right, up = billboard_axes(frame, center)
        verts.append(tuple(center_vec))
        vert_uvs.append((0.5, 0.5))
        for ring in range(1, ring_count + 1):
            r = radius * ring / float(ring_count)
            uv_r = 0.5 * ring / float(ring_count)
            for seg in range(segments):
                theta = 2.0 * math.pi * seg / float(segments)
                p = center_vec + right * (math.cos(theta) * r) + up * (math.sin(theta) * r)
                verts.append(tuple(p))
                vert_uvs.append((0.5 + math.cos(theta) * uv_r, 0.5 + math.sin(theta) * uv_r))
        first_ring = base + 1
        for seg in range(segments):
            faces.append((base, first_ring + seg, first_ring + ((seg + 1) % segments)))
            material_indices.append(0)
        for ring in range(1, ring_count):
            row0 = base + 1 + (ring - 1) * segments
            row1 = row0 + segments
            mat_index = min(ring, len(falloff) - 1)
            for seg in range(segments):
                faces.append((
                    row0 + seg,
                    row0 + ((seg + 1) % segments),
                    row1 + ((seg + 1) % segments),
                    row1 + seg,
                ))
                material_indices.append(mat_index)
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if vert_uvs:
        uv_layer = mesh.uv_layers.new(name="MistFalloffUV")
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                uv_layer.data[loop_index].uv = vert_uvs[vertex_index]
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    for material in materials:
        obj.data.materials.append(material)
    for index, poly in enumerate(obj.data.polygons):
        poly.material_index = min(material_indices[index], max(0, len(materials) - 1))
    return obj


def add_sphere_cloud_mesh(name, particles, material, segments=8, rings=4):
    verts = []
    faces = []
    segments = max(4, int(segments))
    rings = max(3, int(rings))
    for center, radius in particles:
        base = len(verts)
        cx, cy, cz = center
        radius = max(0.001, float(radius))
        verts.append((cx, cy, cz + radius))
        for ring in range(1, rings):
            phi = math.pi * ring / float(rings)
            z = math.cos(phi) * radius
            rr = math.sin(phi) * radius
            for seg in range(segments):
                theta = 2.0 * math.pi * seg / float(segments)
                verts.append((cx + math.cos(theta) * rr, cy + math.sin(theta) * rr, cz + z))
        bottom = len(verts)
        verts.append((cx, cy, cz - radius))
        first_ring = base + 1
        for seg in range(segments):
            faces.append((base, first_ring + seg, first_ring + ((seg + 1) % segments)))
        for ring in range(rings - 2):
            row0 = base + 1 + ring * segments
            row1 = row0 + segments
            for seg in range(segments):
                faces.append((
                    row0 + seg,
                    row0 + ((seg + 1) % segments),
                    row1 + ((seg + 1) % segments),
                    row1 + seg,
                ))
        last_ring = base + 1 + (rings - 2) * segments
        for seg in range(segments):
            faces.append((last_ring + ((seg + 1) % segments), last_ring + seg, bottom))
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj["lsfs_frame_asset"] = True
    obj.data.materials.append(material)
    return obj


def make_particle_falloff_materials(prefix, values, falloff):
    mats = []
    for index, factor in enumerate(falloff if isinstance(falloff, list) and falloff else [1.0]):
        scaled = scaled_particle_values(values, factor, factor)
        mats.append(make_principled_material(
            f"{prefix} {index}",
            scaled["color"],
            scaled["roughness"],
            scaled["alpha"],
            scaled["transmission"],
            scaled["emission_color"],
            scaled["emission_strength"]))
    return mats


def make_radial_soft_material(name, values):
    mat = make_principled_material(name,
                                   values["color"],
                                   values["roughness"],
                                   values["alpha"],
                                   values["transmission"],
                                   values["emission_color"],
                                   values["emission_strength"])
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return mat
    try:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        texcoord = nodes.new(type="ShaderNodeTexCoord")
        subtract = nodes.new(type="ShaderNodeVectorMath")
        subtract.operation = "SUBTRACT"
        subtract.inputs[1].default_value = (0.5, 0.5, 0.0)
        length = nodes.new(type="ShaderNodeVectorMath")
        length.operation = "LENGTH"
        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, clamp01(values["alpha"]))
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 0.0)
        mid = ramp.color_ramp.elements.new(0.24)
        mid.color = (1.0, 1.0, 1.0, clamp01(values["alpha"] * 0.38))
        links.new(texcoord.outputs["UV"], subtract.inputs[0])
        links.new(subtract.outputs["Vector"], length.inputs[0])
        links.new(length.outputs["Value"], ramp.inputs["Fac"])
        if "Alpha" in ramp.outputs and "Alpha" in bsdf.inputs:
            links.new(ramp.outputs["Alpha"], bsdf.inputs["Alpha"])
    except Exception:
        pass
    return mat


def make_edge_falloff_material(name, values):
    mat = make_principled_material(name,
                                   values["color"],
                                   values["roughness"],
                                   values["alpha"],
                                   values["transmission"],
                                   values["emission_color"],
                                   values["emission_strength"])
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return mat
    try:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        texcoord = nodes.new(type="ShaderNodeTexCoord")
        separate = nodes.new(type="ShaderNodeSeparateXYZ")
        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 0.0)
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 0.0)
        mid = ramp.color_ramp.elements.new(0.5)
        mid.color = (1.0, 1.0, 1.0, clamp01(values["alpha"]))
        inner = ramp.color_ramp.elements.new(0.22)
        inner.color = (1.0, 1.0, 1.0, clamp01(values["alpha"] * 0.42))
        outer = ramp.color_ramp.elements.new(0.78)
        outer.color = (1.0, 1.0, 1.0, clamp01(values["alpha"] * 0.42))
        links.new(texcoord.outputs["UV"], separate.inputs["Vector"])
        links.new(separate.outputs["Y"], ramp.inputs["Fac"])
        if "Alpha" in ramp.outputs and "Alpha" in bsdf.inputs:
            links.new(ramp.outputs["Alpha"], bsdf.inputs["Alpha"])
    except Exception:
        pass
    return mat


def main():
    spec = read_spec()
    preset = spec.get("render_preset") or {}
    clear_scene()
    configure_scene(spec)
    camera = make_camera()
    add_lights(preset)
    water = material_values(preset, "water", (0.18, 0.66, 1.0, 0.52), 0.03, 0.52, 0.35)
    water_glint = material_values(preset, "water_glint", (0.82, 0.96, 1.0, 0.32), 0.08, 0.32, 0.0)
    water_reflection = material_values(preset, "water_reflection", (0.62, 0.86, 1.0, 0.24), 0.06, 0.24, 0.0)
    water_volume_scatter = material_values(preset, "water_volume_scatter", (0.24, 0.58, 0.9, 0.16), 0.82, 0.16, 0.0)
    water_ripple = material_values(preset, "water_ripple", (0.8, 0.96, 1.0, 0.3), 0.08, 0.3, 0.0)
    floor = material_values(preset, "floor", (0.015, 0.018, 0.024, 1.0), 0.7, 1.0, 0.0)
    droplet = material_values(preset, "droplet", (0.72, 0.95, 1.0, 0.85), 0.05, 0.85, 0.25)
    spray = material_values(preset, "spray", (0.9, 0.98, 1.0, 0.8), 0.12, 0.8, 0.15)
    foam = material_values(preset, "foam", (0.95, 0.94, 0.82, 1.0), 0.55, 1.0, 0.0)
    bubble = material_values(preset, "bubble", (1.0, 0.78, 0.34, 0.78), 0.15, 0.78, 0.15)
    surface_detail = surface_detail_values(preset)
    water_mat = make_water_material("LSFS Water Glass", water)
    floor_mat = make_principled_material("LSFS Dark Floor",
                                         floor["color"],
                                         roughness=floor["roughness"],
                                         alpha=floor["alpha"],
                                         transmission=floor["transmission"])
    soft_pass = secondary_soft_pass_values(spec)
    streak_pass = secondary_streak_pass_values(spec)
    contact_foam_pass = surface_contact_foam_pass_values(spec)
    glint_pass = water_surface_glint_pass_values(spec)
    reflection_pass = water_reflection_pass_values(spec)
    scattering_pass = water_volume_scattering_pass_values(spec)
    ripple_pass = water_impact_ripple_pass_values(spec)
    water_glint = scaled_overlay_values(water_glint,
                                        glint_pass.get("alpha_scale", 0.22),
                                        glint_pass.get("emission_scale", 0.45))
    water_reflection = scaled_overlay_values(water_reflection,
                                             reflection_pass.get("alpha_scale", 0.18),
                                             reflection_pass.get("emission_scale", 0.32))
    water_volume_scatter = scaled_overlay_values(water_volume_scatter,
                                                 scattering_pass.get("alpha_scale", 0.22),
                                                 scattering_pass.get("emission_scale", 0.18))
    water_ripple = scaled_overlay_values(water_ripple,
                                         ripple_pass.get("alpha_scale", 0.26),
                                         ripple_pass.get("emission_scale", 0.42))
    spray_soft = scaled_particle_values(spray,
                                        spec.get("secondary_soft_pass", {}).get("alpha_scale", 0.35),
                                        spec.get("secondary_soft_pass", {}).get("emission_scale", 0.5))
    foam_soft = scaled_particle_values(foam,
                                       spec.get("secondary_soft_pass", {}).get("alpha_scale", 0.35),
                                       spec.get("secondary_soft_pass", {}).get("emission_scale", 0.5))
    spray_streak = scaled_particle_values(spray,
                                          spec.get("secondary_streak_pass", {}).get("alpha_scale", 0.22),
                                          spec.get("secondary_streak_pass", {}).get("emission_scale", 0.9))
    foam_streak = scaled_particle_values(foam,
                                         spec.get("secondary_streak_pass", {}).get("alpha_scale", 0.22),
                                         spec.get("secondary_streak_pass", {}).get("emission_scale", 0.9))
    foam_contact = scaled_particle_values(foam,
                                          spec.get("surface_contact_foam_pass", {}).get("alpha_scale", 0.32),
                                          spec.get("surface_contact_foam_pass", {}).get("emission_scale", 0.35))
    particle_mats = {
        "droplet": make_principled_material("LSFS Droplet", droplet["color"], droplet["roughness"], droplet["alpha"], droplet["transmission"], droplet["emission_color"], droplet["emission_strength"]),
        "spray": make_principled_material("LSFS Spray", spray["color"], spray["roughness"], spray["alpha"], spray["transmission"], spray["emission_color"], spray["emission_strength"]),
        "foam": make_principled_material("LSFS Foam", foam["color"], foam["roughness"], foam["alpha"], foam["transmission"], foam["emission_color"], foam["emission_strength"]),
        "bubble": make_principled_material("LSFS Bubble", bubble["color"], bubble["roughness"], bubble["alpha"], bubble["transmission"], bubble["emission_color"], bubble["emission_strength"]),
        "spray_soft": make_principled_material("LSFS Spray Mist", spray_soft["color"], spray_soft["roughness"], spray_soft["alpha"], spray_soft["transmission"], spray_soft["emission_color"], spray_soft["emission_strength"]),
        "foam_soft": make_principled_material("LSFS Foam Soft", foam_soft["color"], foam_soft["roughness"], foam_soft["alpha"], foam_soft["transmission"], foam_soft["emission_color"], foam_soft["emission_strength"]),
        "spray_soft_falloff": make_particle_falloff_materials("LSFS Spray Mist Falloff", spray_soft, soft_pass.get("falloff", [1.0])),
        "foam_soft_falloff": make_particle_falloff_materials("LSFS Foam Soft Falloff", foam_soft, soft_pass.get("falloff", [1.0])),
        "spray_streak": make_principled_material("LSFS Spray Streak", spray_streak["color"], spray_streak["roughness"], spray_streak["alpha"], spray_streak["transmission"], spray_streak["emission_color"], spray_streak["emission_strength"]),
        "foam_streak": make_principled_material("LSFS Foam Streak", foam_streak["color"], foam_streak["roughness"], foam_streak["alpha"], foam_streak["transmission"], foam_streak["emission_color"], foam_streak["emission_strength"]),
        "foam_contact": make_principled_material("LSFS Surface Contact Foam", foam_contact["color"], foam_contact["roughness"], foam_contact["alpha"], foam_contact["transmission"], foam_contact["emission_color"], foam_contact["emission_strength"]),
        "water_glint": make_principled_material("LSFS Water Surface Glint", water_glint["color"], water_glint["roughness"], water_glint["alpha"], water_glint["transmission"], water_glint["emission_color"], water_glint["emission_strength"]),
        "water_reflection": make_principled_material("LSFS Water Reflection Ribbons", water_reflection["color"], water_reflection["roughness"], water_reflection["alpha"], water_reflection["transmission"], water_reflection["emission_color"], water_reflection["emission_strength"]),
        "water_volume_scatter": make_principled_material("LSFS Water Volume Scattering", water_volume_scatter["color"], water_volume_scatter["roughness"], water_volume_scatter["alpha"], water_volume_scatter["transmission"], water_volume_scatter["emission_color"], water_volume_scatter["emission_strength"]),
        "water_ripple": make_principled_material("LSFS Impact Ripple Cues", water_ripple["color"], water_ripple["roughness"], water_ripple["alpha"], water_ripple["transmission"], water_ripple["emission_color"], water_ripple["emission_strength"]),
    }
    if soft_pass.get("material_falloff") == "radial_shader":
        particle_mats["spray_soft_falloff"] = [make_radial_soft_material("LSFS Spray Mist Radial", spray_soft)]
        particle_mats["foam_soft_falloff"] = [make_radial_soft_material("LSFS Foam Soft Radial", foam_soft)]
    if contact_foam_pass.get("material_falloff") == "radial_shader":
        particle_mats["foam_contact"] = make_radial_soft_material("LSFS Surface Contact Foam Radial", foam_contact)
    if ripple_pass.get("material_falloff") == "edge_shader":
        particle_mats["water_ripple"] = make_edge_falloff_material("LSFS Impact Ripple Edge Falloff", water_ripple)
    channel_scales = spec.get("secondary_channel_radius_scales") or {}
    if spec.get("frames"):
        add_floor(spec["frames"][0], floor_mat, preset)
    for frame in spec["frames"]:
        remove_frame_assets()
        configure_camera(camera, frame, preset)
        add_water_mesh(frame, water_mat, surface_detail)
        add_water_volume_scattering_pass(frame,
                                         particle_mats["water_volume_scatter"],
                                         scattering_pass)
        add_water_impact_ripple_pass(frame,
                                     particle_mats["water_ripple"],
                                     ripple_pass)
        add_water_reflection_pass(frame,
                                  particle_mats["water_reflection"],
                                  reflection_pass)
        add_water_surface_glint_pass(frame,
                                     particle_mats["water_glint"],
                                     glint_pass)
        add_surface_contact_foam_pass(frame,
                                      particle_mats["foam_contact"],
                                      contact_foam_pass)
        add_secondary_particles(frame,
                                particle_mats,
                                int(spec.get("max_secondary_particles", 512)),
                                float(spec.get("secondary_radius_scale", 1.0)),
                                channel_scales)
        add_secondary_streak_pass(frame,
                                  particle_mats,
                                  int(spec.get("max_secondary_particles", 512)),
                                  float(spec.get("secondary_radius_scale", 1.0)),
                                  channel_scales,
                                  streak_pass)
        add_secondary_soft_pass(frame,
                                particle_mats,
                                int(spec.get("max_secondary_particles", 512)),
                                float(spec.get("secondary_radius_scale", 1.0)),
                                channel_scales,
                                soft_pass)
        bpy.context.scene.frame_set(int(frame["index"]))
        bpy.context.scene.render.filepath = frame["output_png"]
        bpy.ops.render.render(write_still=True)


try:
    main()
except Exception:
    traceback.print_exc()
    sys.exit(1)
'''


def write_driver(path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(BLENDER_DRIVER)
        f.write("\n")


def image_stats(path):
    if Image is None:
        return {
            "path": path,
            "exists": os.path.isfile(path),
            "bytes": os.path.getsize(path) if os.path.isfile(path) else 0,
            "nonblank_ratio": None,
            "contrast": None,
        }
    with Image.open(path) as img:
        gray = img.convert("L")
        hist = gray.histogram()
        total = max(1, gray.width * gray.height)
        nonblack = sum(hist[3:])
        mean_luminance = sum(index * count for index, count in enumerate(hist)) / float(total)
        extrema = gray.getextrema()
        return {
            "path": path,
            "exists": True,
            "bytes": os.path.getsize(path),
            "width": gray.width,
            "height": gray.height,
            "nonblank_ratio": nonblack / total,
            "mean_luminance": mean_luminance,
            "bright_ratio": sum(hist[140:]) / total,
            "highlight_ratio": sum(hist[180:]) / total,
            "dark_ratio": sum(hist[:8]) / total,
            "contrast": extrema[1] - extrema[0],
        }


def stat_summary(values):
    values = [float(item) for item in values if item is not None]
    if not values:
        return {"min": None, "mean": None, "max": None}
    return {
        "min": min(values),
        "mean": sum(values) / float(len(values)),
        "max": max(values),
    }


def visual_qa_summary(stats):
    return {
        "frame_count": len(stats),
        "nonblank_ratio": stat_summary(item.get("nonblank_ratio") for item in stats),
        "contrast": stat_summary(item.get("contrast") for item in stats),
        "mean_luminance": stat_summary(item.get("mean_luminance") for item in stats),
        "bright_ratio": stat_summary(item.get("bright_ratio") for item in stats),
        "highlight_ratio": stat_summary(item.get("highlight_ratio") for item in stats),
        "dark_ratio": stat_summary(item.get("dark_ratio") for item in stats),
        "png_bytes": stat_summary(item.get("bytes") for item in stats),
    }


def validate_rendered_frames(spec, min_nonblank_ratio):
    stats = []
    for frame in spec["frames"]:
        path = frame["output_png"]
        if not os.path.isfile(path):
            fail(f"Blender did not create {path}")
        item = image_stats(path)
        if item["bytes"] <= 128:
            fail(f"{path}: rendered PNG is too small")
        if item.get("nonblank_ratio") is not None:
            if item["nonblank_ratio"] < min_nonblank_ratio:
                fail(f"{path}: nonblank ratio {item['nonblank_ratio']:.6g} below {min_nonblank_ratio:.6g}")
            if item["contrast"] <= 0:
                fail(f"{path}: rendered PNG has no luminance contrast")
        stats.append(item)
    return stats


def run_blender(blender_path, driver_path, spec_path, out_dir, timeout_seconds):
    cmd = [blender_path, "--background", "--python", driver_path, "--", spec_path]
    started = time.perf_counter()
    result = subprocess.run(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=timeout_seconds,
                            check=False)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    stdout_path = os.path.join(out_dir, "blender_stdout.log")
    stderr_path = os.path.join(out_dir, "blender_stderr.log")
    with open(stdout_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(result.stdout)
    with open(stderr_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(result.stderr)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "elapsed_ms": elapsed_ms,
        "stdout": stdout_path,
        "stderr": stderr_path,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Render LSFS converted cache assets through Blender")
    parser.add_argument("src", nargs="?", help="S38 converted sequence.json")
    parser.add_argument("out_dir", nargs="?", help="output directory")
    parser.add_argument("--check", action="store_true", help="print Blender dependency report and exit")
    parser.add_argument("--blender", help="explicit blender executable path")
    parser.add_argument("--dry-run", action="store_true", help="write scene spec and driver without launching Blender")
    parser.add_argument("--water-reconstruction", help="optional S41 water_reconstruction.json override")
    parser.add_argument("--preset-config", default=default_preset_config_path(),
                        help="cinematic preset config JSON")
    parser.add_argument("--render-preset", help="named render preset to apply")
    parser.add_argument("--frames", type=int, default=8, help="number of PNG frames to render")
    parser.add_argument("--width", type=int, default=1280, help="output image width")
    parser.add_argument("--height", type=int, default=720, help="output image height")
    parser.add_argument("--engine", choices=("eevee", "cycles"), help="Blender render engine")
    parser.add_argument("--samples", type=int, help="render samples")
    parser.add_argument("--max-secondary-particles", type=int,
                        help="maximum secondary particles instantiated per frame")
    parser.add_argument("--secondary-radius-scale", type=float,
                        help="scale factor for rendered secondary particle sphere radii")
    parser.add_argument("--min-nonblank-ratio", type=float, default=0.05,
                        help="minimum nonblack pixel ratio required after rendering")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Blender process timeout")
    args = parser.parse_args(argv)
    if args.check:
        return args
    if not args.src or not args.out_dir:
        parser.error("src and out_dir are required unless --check is used")
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.width <= 0 or args.height <= 0:
        parser.error("width and height must be positive")
    if args.samples is not None and args.samples <= 0:
        parser.error("samples must be positive")
    if args.max_secondary_particles is not None and args.max_secondary_particles < 0:
        parser.error("max-secondary-particles must be non-negative")
    if args.secondary_radius_scale is not None and (
            args.secondary_radius_scale <= 0.0 or not math.isfinite(args.secondary_radius_scale)):
        parser.error("secondary-radius-scale must be finite and positive")
    if args.min_nonblank_ratio < 0.0 or not math.isfinite(args.min_nonblank_ratio):
        parser.error("min-nonblank-ratio must be finite and non-negative")
    if args.timeout_seconds <= 0:
        parser.error("timeout-seconds must be positive")
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check:
        print(json.dumps(dependency_report(args.blender), indent=2, sort_keys=True))
        return 0

    try:
        os.makedirs(args.out_dir, exist_ok=True)
        preset_config_path, render_preset = load_render_preset(args.preset_config, args.render_preset)
        spec = build_scene_spec(args.src,
                                args.out_dir,
                                args.frames,
                                args.width,
                                args.height,
                                args.water_reconstruction,
                                args.engine,
                                args.samples,
                                args.max_secondary_particles,
                                args.secondary_radius_scale,
                                args.render_preset,
                                render_preset)
        spec_path = os.path.abspath(os.path.join(args.out_dir, "blender_scene_spec.json"))
        driver_path = os.path.abspath(os.path.join(args.out_dir, "blender_driver.py"))
        write_json(spec_path, spec)
        write_driver(driver_path)
        report = dependency_report(args.blender)
        summary = {
            "bridge": "lsfs_blender_bridge",
            "version": 1,
            "status": "dry_run" if args.dry_run else "pending",
            "source": os.path.abspath(args.src),
            "out_dir": os.path.abspath(args.out_dir),
            "scene_spec": spec_path,
            "driver_script": driver_path,
            "width": args.width,
            "height": args.height,
            "frame_count": len(spec["frames"]),
            "engine": spec["engine"],
            "samples": spec["samples"],
            "secondary_radius_scale": spec["secondary_radius_scale"],
            "secondary_channel_radius_scales": spec["secondary_channel_radius_scales"],
            "secondary_soft_pass": spec["secondary_soft_pass"],
            "secondary_streak_pass": spec["secondary_streak_pass"],
            "secondary_streak_counts": spec["secondary_streak_counts"],
            "surface_contact_foam_pass": spec["surface_contact_foam_pass"],
            "surface_contact_foam_counts": spec["surface_contact_foam_counts"],
            "water_surface_glint_pass": spec["water_surface_glint_pass"],
            "water_reflection_pass": spec["water_reflection_pass"],
            "water_volume_scattering_pass": spec["water_volume_scattering_pass"],
            "water_impact_ripple_pass": spec["water_impact_ripple_pass"],
            "water_impact_ripple_counts": spec["water_impact_ripple_counts"],
            "secondary_framing_qa": spec["secondary_framing_qa"],
            "secondary_framing": spec["secondary_framing"],
            "camera_motion": spec["camera_motion"],
            "camera_framing": spec["camera_framing"],
            "camera_path_metrics": spec["camera_path_metrics"],
            "water_material": spec["water_material"],
            "water_surface_detail": spec["water_surface_detail"],
            "render_preset_name": args.render_preset,
            "preset_config": preset_config_path,
            "dependency": report,
            "frames": [{
                "index": frame["index"],
                "output_png": frame["output_png"],
                "water_mesh": frame["water_mesh"],
                "water_mesh_face_count": frame["water_mesh_face_count"],
                "secondary_counts": frame["secondary_counts"],
                "secondary_streak_counts": frame["secondary_streak_counts"],
                "surface_contact_foam_counts": frame["surface_contact_foam_counts"],
                "water_impact_ripple_counts": frame["water_impact_ripple_counts"],
            } for frame in spec["frames"]],
        }
        summary_path = os.path.abspath(os.path.join(args.out_dir, "bridge_summary.json"))
        if args.dry_run:
            write_json(summary_path, summary)
            print(f"status=ok mode=dry-run frames={len(spec['frames'])} summary={summary_path}")
            return 0
        blender_path = report.get("selected")
        if not blender_path:
            summary["status"] = "missing_dependency"
            summary["error"] = "Blender executable not found; run with --blender PATH or install Blender"
            write_json(summary_path, summary)
            print(f"status=fail error={summary['error']} summary={summary_path}", file=sys.stderr)
            return 2
        run = run_blender(blender_path, driver_path, spec_path, args.out_dir, args.timeout_seconds)
        summary["blender_run"] = run
        if run["returncode"] != 0:
            summary["status"] = "renderer_failed"
            summary["error"] = f"Blender exited with code {run['returncode']}"
            write_json(summary_path, summary)
            print(f"status=fail error={summary['error']} summary={summary_path}", file=sys.stderr)
            return 3
        rendered_stats = validate_rendered_frames(spec, args.min_nonblank_ratio)
        summary["status"] = "rendered"
        summary["rendered_frames"] = rendered_stats
        summary["min_nonblank_ratio"] = min(item.get("nonblank_ratio", 1.0) or 1.0 for item in rendered_stats)
        summary["min_contrast"] = min(item.get("contrast", 1) or 1 for item in rendered_stats)
        summary["visual_qa"] = visual_qa_summary(rendered_stats)
        write_json(summary_path, summary)
        print(f"status=ok renderer=blender frames={len(rendered_stats)} summary={summary_path}")
        return 0
    except subprocess.TimeoutExpired as exc:
        print(f"status=fail error=Blender timed out after {exc.timeout}s", file=sys.stderr)
        return 4
    except BridgeError as exc:
        print(f"status=fail error={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
