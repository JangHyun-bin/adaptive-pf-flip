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
    preset = presets.get(preset_name)
    if not isinstance(preset, dict):
        fail(f"{resolved}: unknown render preset {preset_name!r}")
    return resolved, preset


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


def count_secondary_particles(path):
    counts = {"droplet": 0, "spray": 0, "foam": 0, "bubble": 0, "total": 0}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            kind = row.get("kind", "")
            channel = row.get("render_channel", "")
            if kind not in ("secondary_droplet", "secondary_bubble") and channel not in counts:
                continue
            if channel not in counts:
                channel = "bubble" if kind == "secondary_bubble" else "droplet"
            counts[channel] += 1
            counts["total"] += 1
    return counts


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
                     engine, samples, max_secondary_particles, render_preset_name=None,
                     render_preset=None):
    sequence = load_sequence(src, water_reconstruction_path)
    render_preset = render_preset or {}
    renderer_defaults = render_preset.get("renderer", {})
    engine = engine or renderer_defaults.get("engine", "eevee")
    samples = samples if samples is not None else as_int(renderer_defaults.get("samples"), 24)
    max_secondary_particles = (
        max_secondary_particles if max_secondary_particles is not None
        else as_int(renderer_defaults.get("max_secondary_particles"), 512)
    )
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
        frames.append({
            "index": out_index,
            "frame": frame["frame"],
            "time": frame["time"],
            "source_cache": frame.get("source_cache"),
            "camera": normalize_camera(frame["camera"]),
            "cinematic": frame.get("cinematic") or {},
            "header": {
                "dims": frame.get("header", {}).get("dims", sequence["sequence"].get("dims", [1, 1, 1])),
                "dx": as_float(frame.get("header", {}).get("dx"), as_float(sequence["sequence"].get("dx"), 1.0)),
            },
            "water_mesh": mesh_path,
            "water_mesh_vertex_count": as_int(water_mesh.get("vertex_count")),
            "water_mesh_face_count": as_int(water_mesh.get("face_count")),
            "water_mesh_occupied_cell_count": as_int(water_mesh.get("occupied_cell_count")),
            "particles_csv": frame["particles_csv"],
            "particle_count": frame.get("particle_count", 0),
            "secondary_counts": secondary_counts,
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
        "render_preset_name": render_preset_name,
        "render_preset": render_preset,
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


def material_values(preset, name, color, roughness, alpha, transmission):
    cfg = preset_section(preset_section(preset, "materials"), name)
    return {
        "color": vector_value(cfg.get("base_color"), color, 4),
        "roughness": scalar_value(cfg.get("roughness"), roughness),
        "alpha": scalar_value(cfg.get("alpha"), alpha),
        "transmission": scalar_value(cfg.get("transmission"), transmission),
    }


def make_principled_material(name, color, roughness=0.2, alpha=1.0, transmission=0.0):
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
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = True
    return mat


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
    preset_camera = preset_section(preset, "camera")
    cam.update(preset_camera)
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


def add_water_mesh(frame, material):
    objects = import_obj(frame["water_mesh"])
    for obj in objects:
        obj.name = "LSFS Water"
        obj["lsfs_frame_asset"] = True
        obj.rotation_euler[0] = math.radians(90.0)
        if hasattr(obj.data, "polygons"):
            for poly in obj.data.polygons:
                poly.use_smooth = True
        obj.data.materials.append(material)
    return len(objects)


def secondary_channel(row):
    channel = row.get("render_channel", "")
    if channel in ("droplet", "spray", "foam", "bubble"):
        return channel
    kind = row.get("kind", "")
    return "bubble" if kind == "secondary_bubble" else "droplet"


def add_secondary_particles(frame, materials, max_count):
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
            radius = min(0.14, max(0.035, 0.035 * math.sqrt(volume)))
            channel = secondary_channel(row)
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


def main():
    spec = read_spec()
    preset = spec.get("render_preset") or {}
    clear_scene()
    configure_scene(spec)
    camera = make_camera()
    add_lights(preset)
    water = material_values(preset, "water", (0.18, 0.66, 1.0, 0.52), 0.03, 0.52, 0.35)
    floor = material_values(preset, "floor", (0.015, 0.018, 0.024, 1.0), 0.7, 1.0, 0.0)
    droplet = material_values(preset, "droplet", (0.72, 0.95, 1.0, 0.85), 0.05, 0.85, 0.25)
    spray = material_values(preset, "spray", (0.9, 0.98, 1.0, 0.8), 0.12, 0.8, 0.15)
    foam = material_values(preset, "foam", (0.95, 0.94, 0.82, 1.0), 0.55, 1.0, 0.0)
    bubble = material_values(preset, "bubble", (1.0, 0.78, 0.34, 0.78), 0.15, 0.78, 0.15)
    water_mat = make_principled_material("LSFS Water Glass",
                                         water["color"],
                                         roughness=water["roughness"],
                                         alpha=water["alpha"],
                                         transmission=water["transmission"])
    floor_mat = make_principled_material("LSFS Dark Floor",
                                         floor["color"],
                                         roughness=floor["roughness"],
                                         alpha=floor["alpha"],
                                         transmission=floor["transmission"])
    particle_mats = {
        "droplet": make_principled_material("LSFS Droplet", droplet["color"], droplet["roughness"], droplet["alpha"], droplet["transmission"]),
        "spray": make_principled_material("LSFS Spray", spray["color"], spray["roughness"], spray["alpha"], spray["transmission"]),
        "foam": make_principled_material("LSFS Foam", foam["color"], foam["roughness"], foam["alpha"], foam["transmission"]),
        "bubble": make_principled_material("LSFS Bubble", bubble["color"], bubble["roughness"], bubble["alpha"], bubble["transmission"]),
    }
    if spec.get("frames"):
        add_floor(spec["frames"][0], floor_mat, preset)
    for frame in spec["frames"]:
        remove_frame_assets()
        configure_camera(camera, frame, preset)
        add_water_mesh(frame, water_mat)
        add_secondary_particles(frame, particle_mats, int(spec.get("max_secondary_particles", 512)))
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
        extrema = gray.getextrema()
        return {
            "path": path,
            "exists": True,
            "bytes": os.path.getsize(path),
            "width": gray.width,
            "height": gray.height,
            "nonblank_ratio": nonblack / total,
            "contrast": extrema[1] - extrema[0],
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
            "render_preset_name": args.render_preset,
            "preset_config": preset_config_path,
            "dependency": report,
            "frames": [{
                "index": frame["index"],
                "output_png": frame["output_png"],
                "water_mesh": frame["water_mesh"],
                "water_mesh_face_count": frame["water_mesh_face_count"],
                "secondary_counts": frame["secondary_counts"],
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
