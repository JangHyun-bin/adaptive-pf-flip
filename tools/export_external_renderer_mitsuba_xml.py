#!/usr/bin/env python
"""Export LSFS external renderer scene descriptors to Mitsuba XML scenes."""

import argparse
import csv
import json
import math
import os
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)

SECONDARY_CHANNELS = ("spray", "foam", "bubble", "droplet")
SECONDARY_BSDFS = {
    "spray": {
        "id": "lsfs_secondary_spray",
        "reflectance": "0.70, 0.82, 0.92",
        "default_radius_scale": 0.56,
    },
    "foam": {
        "id": "lsfs_secondary_foam",
        "reflectance": "0.92, 0.96, 0.98",
        "default_radius_scale": 0.96,
    },
    "bubble": {
        "id": "lsfs_secondary_bubble",
        "reflectance": "0.62, 0.82, 0.96",
        "default_radius_scale": 0.4,
    },
    "droplet": {
        "id": "lsfs_secondary_droplet",
        "reflectance": "0.82, 0.90, 1.0",
        "default_radius_scale": 0.5,
    },
}
PHASE_VOLUME_BSDF = {
    "id": "lsfs_phase_volume_proxy",
    "reflectance": "0.12, 0.34, 0.62",
}


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def xml_path(path):
    return escape(resolve_path(path).replace(os.sep, "/")) if path else ""


def csv3(values, default):
    items = values if isinstance(values, list) and len(values) >= 3 else default
    return ", ".join(f"{float(items[i]):.8g}" for i in range(3))


def csv3_required(values, label):
    parts = [part.strip() for part in values.split(",")] if values else []
    if len(parts) != 3:
        raise ValueError(f"{label} must contain three comma-separated numbers")
    return [float(part) for part in parts]


def csv2_required(values, label):
    parts = [part.strip() for part in values.split(",")] if values else []
    if len(parts) != 2:
        raise ValueError(f"{label} must contain two comma-separated numbers")
    return [float(part) for part in parts]


def parse_channel_values(values, label):
    if not values:
        return None
    result = {}
    for part in values.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"{label} entries must be channel=value")
        channel, value = [item.strip() for item in part.split("=", 1)]
        if channel not in SECONDARY_CHANNELS:
            raise ValueError(f"{label}: unknown channel {channel!r}")
        parsed = float(value)
        if not (0.0 < parsed <= 1.0):
            raise ValueError(f"{label}: {channel} opacity must be in the range (0, 1]")
        result[channel] = parsed
    return result or None


def override3(value, fallback):
    return value if value is not None else fallback


def selected_frames(frames, requested=None):
    if not frames:
        return []
    if requested is None or requested <= 0 or requested >= len(frames):
        return frames
    if requested == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(requested - 1)) for i in range(requested)))
    return [frames[index] for index in indices]


def render_command(command, mode, xml_scene, output_image):
    mode_arg = f" -m {mode}" if mode else ""
    return f'{command}{mode_arg} "{xml_scene}" -o "{output_image}"'


def scene_ref_path(frame):
    ref = frame.get("scene_descriptor") or {}
    return resolve_path(ref.get("path") or ref.get("repo_path"))


def asset_path(scene, name):
    asset = (scene.get("assets") or {}).get(name) or {}
    return resolve_path(asset.get("path") or asset.get("repo_path"))


def as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def sample_items(items, requested):
    if requested <= 0 or not items:
        return []
    if requested >= len(items):
        return list(items)
    if requested == 1:
        return [items[len(items) // 2]]
    indices = sorted(set(round(i * (len(items) - 1) / float(requested - 1)) for i in range(requested)))
    return [items[index] for index in indices]


def allocate_channel_samples(channel_rows, limit):
    total = sum(len(rows) for rows in channel_rows.values())
    target = min(max(0, limit), total)
    allocations = {channel: 0 for channel in SECONDARY_CHANNELS}
    if target <= 0:
        return allocations
    present = [channel for channel in SECONDARY_CHANNELS if channel_rows.get(channel)]
    for channel in present:
        if sum(allocations.values()) < target:
            allocations[channel] = 1
    remaining = target - sum(allocations.values())
    if remaining <= 0:
        return allocations
    present_total = sum(len(channel_rows[channel]) for channel in present)
    weighted = []
    for channel in present:
        rows = len(channel_rows[channel])
        exact = remaining * rows / float(max(1, present_total))
        extra = min(rows - allocations[channel], int(exact))
        allocations[channel] += extra
        weighted.append((exact - int(exact), rows, channel))
    remaining = target - sum(allocations.values())
    for _fraction, _rows, channel in sorted(weighted, reverse=True):
        if remaining <= 0:
            break
        capacity = len(channel_rows[channel]) - allocations[channel]
        if capacity <= 0:
            continue
        allocations[channel] += 1
        remaining -= 1
    while remaining > 0:
        progressed = False
        for channel in present:
            capacity = len(channel_rows[channel]) - allocations[channel]
            if capacity <= 0:
                continue
            allocations[channel] += 1
            remaining -= 1
            progressed = True
            if remaining <= 0:
                break
        if not progressed:
            break
    return allocations


def channel_radius_scale(scene, channel):
    channels = (((scene.get("materials") or {}).get("secondary_particles") or {}).get("channels") or {})
    channel_spec = channels.get(channel) or {}
    return as_float(
        channel_spec.get("radius_scale"),
        SECONDARY_BSDFS.get(channel, {}).get("default_radius_scale", 1.0),
    )


def build_secondary_proxy_payload(scene, limit, base_radius):
    payload = {
        "enabled": limit > 0,
        "limit": limit,
        "base_radius": base_radius,
        "available_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
        "proxy_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
        "proxy_count": 0,
        "proxies": [],
    }
    if limit <= 0:
        return payload, []
    particles = asset_path(scene, "particle_stream")
    if not particles or not os.path.isfile(particles):
        return payload, [{
            "kind": "missing_particle_stream",
            "output_frame": scene.get("output_frame"),
            "path": particles,
        }]

    channel_rows = {channel: [] for channel in SECONDARY_CHANNELS}
    with open(particles, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            channel = (row.get("render_channel") or "").strip()
            if channel not in channel_rows:
                continue
            kind = (row.get("kind") or "").strip()
            if not kind.startswith("secondary"):
                continue
            channel_rows[channel].append({
                "channel": channel,
                "x": as_float(row.get("x")),
                "y": as_float(row.get("y")),
                "z": as_float(row.get("z")),
                "volume": as_float(row.get("volume"), 1.0),
                "age": as_float(row.get("age"), 0.0),
            })

    payload["available_counts"] = {channel: len(channel_rows[channel]) for channel in SECONDARY_CHANNELS}
    allocations = allocate_channel_samples(channel_rows, limit)
    proxies = []
    for channel in SECONDARY_CHANNELS:
        radius_scale = channel_radius_scale(scene, channel)
        for row in sample_items(channel_rows[channel], allocations.get(channel, 0)):
            volume_scale = max(0.55, min(1.45, row["volume"] ** (1.0 / 3.0) if row["volume"] > 0.0 else 1.0))
            proxies.append({
                "channel": channel,
                "x": row["x"],
                "y": row["y"],
                "z": row["z"],
                "radius": base_radius * radius_scale * volume_scale,
                "age": row["age"],
            })
    payload["proxies"] = proxies
    payload["proxy_count"] = len(proxies)
    payload["proxy_counts"] = {
        channel: sum(1 for item in proxies if item["channel"] == channel)
        for channel in SECONDARY_CHANNELS
    }
    return payload, []


def load_secondary_3d_sidecar(path, root):
    if not path:
        return None
    sidecar_path = resolve_path(path)
    payload = read_json(sidecar_path)
    if payload.get("schema") != "lsfs_mitsuba_secondary_3d_sidecar":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_secondary_3d_sidecar schema")
    frame_lookup = {}
    for frame in payload.get("frames", []):
        key = frame.get("output_frame")
        if key is None:
            continue
        frame_lookup[int(key)] = frame
    return {
        "path": sidecar_path,
        "repo_path": posix_rel(sidecar_path, root),
        "sha256": sha256_file(sidecar_path),
        "frame_lookup": frame_lookup,
        "checks": payload.get("checks", {}),
    }


def build_secondary_proxy_payload_from_sidecar(frame, sidecar, limit, radius_scale, depth_radius_falloff):
    payload = {
        "enabled": limit > 0,
        "limit": limit,
        "base_radius": None,
        "radius_scale": radius_scale,
        "depth_radius_falloff": depth_radius_falloff,
        "source": "secondary_3d_sidecar",
        "sidecar": {
            "path": sidecar["path"],
            "repo_path": sidecar["repo_path"],
            "sha256": sidecar["sha256"],
        },
        "available_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
        "proxy_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
        "proxy_count": 0,
        "proxies": [],
    }
    output_frame = frame.get("output_frame")
    sidecar_frame = sidecar["frame_lookup"].get(int(output_frame)) if output_frame is not None else None
    if not sidecar_frame:
        return payload, [{
            "kind": "missing_secondary_3d_sidecar_frame",
            "output_frame": output_frame,
            "path": sidecar["path"],
        }]
    payload["sidecar_frame"] = {
        "output_frame": sidecar_frame.get("output_frame"),
        "repo_path": (sidecar_frame.get("sidecar") or {}).get("repo_path"),
        "sha256": (sidecar_frame.get("sidecar") or {}).get("sha256"),
    }
    if limit <= 0:
        return payload, []
    jsonl_path = resolve_path((sidecar_frame.get("sidecar") or {}).get("path") or (sidecar_frame.get("sidecar") or {}).get("repo_path"))
    if not jsonl_path or not os.path.isfile(jsonl_path):
        return payload, [{
            "kind": "missing_secondary_3d_sidecar_jsonl",
            "output_frame": output_frame,
            "path": jsonl_path,
        }]

    raw_rows = []
    with open(jsonl_path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            channel = (row.get("channel") or "").strip()
            if channel not in SECONDARY_CHANNELS:
                continue
            position = row.get("position") or [0.0, 0.0, 0.0]
            depth = (row.get("camera") or {}).get("depth")
            raw_rows.append({
                "channel": channel,
                "x": as_float(position[0] if len(position) > 0 else 0.0),
                "y": as_float(position[1] if len(position) > 1 else 0.0),
                "z": as_float(position[2] if len(position) > 2 else 0.0),
                "radius": as_float(row.get("radius"), 0.075) * radius_scale,
                "age": as_float(row.get("age"), 0.0),
                "depth": depth,
                "in_frame": bool((row.get("camera") or {}).get("in_frame")),
            })

    depths = [
        as_float(row.get("depth"))
        for row in raw_rows
        if isinstance(row.get("depth"), (int, float)) and math.isfinite(float(row.get("depth")))
    ]
    depth_min = min(depths) if depths else None
    depth_max = max(depths) if depths else None
    depth_span = (depth_max - depth_min) if depth_min is not None and depth_max is not None else 0.0
    channel_rows = {channel: [] for channel in SECONDARY_CHANNELS}
    for row in raw_rows:
        if depth_radius_falloff > 0.0 and depth_span > 1e-9:
            normalized_depth = max(0.0, min(1.0, (as_float(row.get("depth"), depth_min) - depth_min) / depth_span))
            radius_factor = max(0.05, 1.0 - depth_radius_falloff * normalized_depth)
            row["radius"] *= radius_factor
            row["depth_radius_factor"] = radius_factor
        channel_rows[row["channel"]].append(row)

    payload["available_counts"] = {channel: len(channel_rows[channel]) for channel in SECONDARY_CHANNELS}
    payload["depth_min"] = depth_min
    payload["depth_max"] = depth_max
    allocations = allocate_channel_samples(channel_rows, limit)
    proxies = []
    for channel in SECONDARY_CHANNELS:
        proxies.extend(sample_items(channel_rows[channel], allocations.get(channel, 0)))
    payload["proxies"] = proxies
    payload["proxy_count"] = len(proxies)
    payload["proxy_counts"] = {
        channel: sum(1 for item in proxies if item["channel"] == channel)
        for channel in SECONDARY_CHANNELS
    }
    return payload, []


def build_phase_volume_proxy_payload(scene, limit, base_radius):
    payload = {
        "enabled": limit > 0,
        "limit": limit,
        "base_radius": base_radius,
        "available_count": 0,
        "proxy_count": 0,
        "proxies": [],
    }
    if limit <= 0:
        return payload, []
    phase_cells = asset_path(scene, "phase_volume")
    if not phase_cells or not os.path.isfile(phase_cells):
        return payload, [{
            "kind": "missing_phase_volume",
            "output_frame": scene.get("output_frame"),
            "path": phase_cells,
        }]

    liquid_cells = []
    with open(phase_cells, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            liquid_volume = as_float(row.get("liquid_volume"), 0.0)
            if liquid_volume <= 0.0:
                continue
            liquid_cells.append({
                "x": as_float(row.get("i")) + 0.5,
                "y": as_float(row.get("j")) + 0.5,
                "z": as_float(row.get("k")) + 0.5,
                "liquid_volume": liquid_volume,
                "phi": as_float(row.get("phi"), 0.0),
            })
    proxies = []
    for row in sample_items(liquid_cells, min(max(0, limit), len(liquid_cells))):
        volume_scale = max(0.45, min(1.25, row["liquid_volume"] ** (1.0 / 3.0)))
        proxies.append({
            "x": row["x"],
            "y": row["y"],
            "z": row["z"],
            "radius": base_radius * volume_scale,
            "liquid_volume": row["liquid_volume"],
            "phi": row["phi"],
        })
    payload["available_count"] = len(liquid_cells)
    payload["proxies"] = proxies
    payload["proxy_count"] = len(proxies)
    return payload, []


def secondary_bsdf_lines(opacity=None):
    lines = []
    for channel in SECONDARY_CHANNELS:
        spec = SECONDARY_BSDFS[channel]
        channel_opacity = opacity.get(channel) if isinstance(opacity, dict) else opacity
        if channel_opacity is None:
            lines.extend([
                f'  <bsdf type="diffuse" id="{spec["id"]}">',
                f'    <rgb name="reflectance" value="{spec["reflectance"]}"/>',
                '  </bsdf>',
            ])
        else:
            lines.extend([
                f'  <bsdf type="mask" id="{spec["id"]}">',
                f'    <float name="opacity" value="{channel_opacity:.8g}"/>',
                '    <bsdf type="diffuse">',
                f'      <rgb name="reflectance" value="{spec["reflectance"]}"/>',
                '    </bsdf>',
                '  </bsdf>',
            ])
    return lines


def secondary_halo_bsdf_lines(opacity=None):
    if opacity is None:
        return []
    lines = []
    for channel in SECONDARY_CHANNELS:
        spec = SECONDARY_BSDFS[channel]
        lines.extend([
            f'  <bsdf type="mask" id="{spec["id"]}_halo">',
            f'    <float name="opacity" value="{opacity:.8g}"/>',
            '    <bsdf type="diffuse">',
            f'      <rgb name="reflectance" value="{spec["reflectance"]}"/>',
            '    </bsdf>',
            '  </bsdf>',
        ])
    return lines


def secondary_mist_bsdf_lines(opacity=None):
    if opacity is None:
        return []
    lines = []
    for channel in SECONDARY_CHANNELS:
        spec = SECONDARY_BSDFS[channel]
        lines.extend([
            f'  <bsdf type="mask" id="{spec["id"]}_mist">',
            f'    <float name="opacity" value="{opacity:.8g}"/>',
            '    <bsdf type="diffuse">',
            f'      <rgb name="reflectance" value="{spec["reflectance"]}"/>',
            '    </bsdf>',
            '  </bsdf>',
        ])
    return lines


def secondary_billboard_bsdf_lines(opacity=None):
    if opacity is None:
        return []
    lines = []
    for channel in SECONDARY_CHANNELS:
        spec = SECONDARY_BSDFS[channel]
        lines.extend([
            f'  <bsdf type="mask" id="{spec["id"]}_billboard">',
            f'    <float name="opacity" value="{opacity:.8g}"/>',
            '    <bsdf type="diffuse">',
            f'      <rgb name="reflectance" value="{spec["reflectance"]}"/>',
            '    </bsdf>',
            '  </bsdf>',
        ])
    return lines


def phase_volume_bsdf_lines():
    return [
        f'  <bsdf type="diffuse" id="{PHASE_VOLUME_BSDF["id"]}">',
        f'    <rgb name="reflectance" value="{PHASE_VOLUME_BSDF["reflectance"]}"/>',
        '  </bsdf>',
    ]


def secondary_proxy_shape_lines(proxy):
    spec = SECONDARY_BSDFS.get(proxy["channel"], SECONDARY_BSDFS["spray"])
    return [
        '  <shape type="sphere">',
        f'    <point name="center" x="{proxy["x"]:.8g}" y="{proxy["y"]:.8g}" z="{proxy["z"]:.8g}"/>',
        f'    <float name="radius" value="{proxy["radius"]:.8g}"/>',
        f'    <ref name="bsdf" id="{spec["id"]}"/>',
        '  </shape>',
    ]


def secondary_halo_proxy_shape_lines(proxy, radius_scale):
    spec = SECONDARY_BSDFS.get(proxy["channel"], SECONDARY_BSDFS["spray"])
    return [
        '  <shape type="sphere">',
        f'    <point name="center" x="{proxy["x"]:.8g}" y="{proxy["y"]:.8g}" z="{proxy["z"]:.8g}"/>',
        f'    <float name="radius" value="{proxy["radius"] * radius_scale:.8g}"/>',
        f'    <ref name="bsdf" id="{spec["id"]}_halo"/>',
        '  </shape>',
    ]


def secondary_mist_proxy_shape_lines(proxy, radius_scale, shells, shell_spacing):
    spec = SECONDARY_BSDFS.get(proxy["channel"], SECONDARY_BSDFS["spray"])
    lines = []
    for shell in range(shells):
        shell_scale = radius_scale * (1.0 + shell * shell_spacing)
        lines.extend([
            '  <shape type="sphere">',
            f'    <point name="center" x="{proxy["x"]:.8g}" y="{proxy["y"]:.8g}" z="{proxy["z"]:.8g}"/>',
            f'    <float name="radius" value="{proxy["radius"] * shell_scale:.8g}"/>',
            f'    <ref name="bsdf" id="{spec["id"]}_mist"/>',
            '  </shape>',
        ])
    return lines


def secondary_billboard_proxy_shape_lines(proxy, radius_scale, aspect, camera_position, camera_up):
    spec = SECONDARY_BSDFS.get(proxy["channel"], SECONDARY_BSDFS["spray"])
    radius = proxy["radius"] * radius_scale
    center = [proxy["x"], proxy["y"], proxy["z"]]
    return [
        '  <shape type="disk">',
        '    <transform name="to_world">',
        f'      <lookat origin="{csv3(center, [0.0, 0.0, 0.0])}" target="{csv3(camera_position, [18.0, 20.0, 58.0])}" up="{csv3(camera_up, [0.0, 1.0, 0.0])}"/>',
        f'      <scale x="{radius:.8g}" y="{radius * aspect:.8g}" z="1"/>',
        '    </transform>',
        f'    <ref name="bsdf" id="{spec["id"]}_billboard"/>',
        '  </shape>',
    ]


def phase_volume_proxy_shape_lines(proxy):
    return [
        '  <shape type="sphere">',
        f'    <point name="center" x="{proxy["x"]:.8g}" y="{proxy["y"]:.8g}" z="{proxy["z"]:.8g}"/>',
        f'    <float name="radius" value="{proxy["radius"]:.8g}"/>',
        f'    <ref name="bsdf" id="{PHASE_VOLUME_BSDF["id"]}"/>',
        '  </shape>',
    ]


def key_light_lines(args, camera_target):
    if args.key_light_radiance_vec is None:
        return []
    position = args.key_light_position_vec or [18.0, 30.0, 36.0]
    target = args.key_light_target_vec or camera_target or [18.0, 8.0, 14.0]
    scale = args.key_light_scale_vec or [18.0, 9.0]
    return [
        '  <shape type="rectangle">',
        '    <transform name="to_world">',
        f'      <lookat origin="{csv3(position, [18.0, 30.0, 36.0])}" target="{csv3(target, [18.0, 8.0, 14.0])}" up="0, 1, 0"/>',
        f'      <scale x="{float(scale[0]):.8g}" y="{float(scale[1]):.8g}"/>',
        '    </transform>',
        '    <emitter type="area">',
        f'      <rgb name="radiance" value="{csv3(args.key_light_radiance_vec, [0.0, 0.0, 0.0])}"/>',
        '    </emitter>',
        '  </shape>',
    ]


def write_mitsuba_scene(scene, out_path, output_image, args, secondary_proxy, phase_volume_proxy):
    camera = scene.get("camera") or {}
    settings = scene.get("render_settings") or {}
    diagnostics = scene.get("diagnostics") or {}
    water_mesh = asset_path(scene, "water_surface")
    phase_cells = asset_path(scene, "phase_volume")
    particles = asset_path(scene, "particle_stream")
    width = int(settings.get("width") or 960)
    height = int(settings.get("height") or 540)
    samples = int(args.samples if args.samples is not None else settings.get("samples") or 12)
    fov = float(args.camera_fov if args.camera_fov is not None else camera.get("vertical_fov_degrees") or camera.get("fov_degrees") or 45.0)
    camera_position = override3(args.camera_position_vec, camera.get("position"))
    camera_target = override3(args.camera_target_vec, camera.get("target"))
    camera_up = override3(args.camera_up_vec, camera.get("up"))
    background_radiance = override3(args.background_radiance_vec, [0.55, 0.62, 0.72])
    water_alpha = args.water_alpha if args.water_alpha is not None else 0.035
    water_int_ior = args.water_int_ior if args.water_int_ior is not None else 1.333
    water_ext_ior = args.water_ext_ior if args.water_ext_ior is not None else 1.0
    secondary = diagnostics.get("secondary_counts") or {}
    water_faces = diagnostics.get("water_mesh_face_count")
    time = scene.get("time")
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<scene version="3.0.0">',
        f'  <!-- LSFS output_frame={scene.get("output_frame")} sequence_frame={scene.get("sequence_frame")} time={time} -->',
        f'  <!-- water_faces={water_faces} secondary_total={secondary.get("total")} -->',
        f'  <!-- secondary_proxy_count={secondary_proxy.get("proxy_count", 0)} -->',
        f'  <!-- secondary_mist_proxy_count={secondary_proxy.get("proxy_count", 0) * args.secondary_mist_shells if args.secondary_mist_opacity is not None else 0} -->',
        f'  <!-- secondary_billboard_proxy_count={secondary_proxy.get("proxy_count", 0) if args.secondary_billboard_opacity is not None else 0} -->',
        f'  <!-- phase_volume_proxy_count={phase_volume_proxy.get("proxy_count", 0)} -->',
        f'  <!-- phase_cells_csv={xml_path(phase_cells)} -->',
        f'  <!-- particles_csv={xml_path(particles)} -->',
        '  <integrator type="path">',
        '    <integer name="max_depth" value="12"/>',
        '  </integrator>',
        '  <sensor type="perspective">',
        f'    <float name="fov" value="{fov:.8g}"/>',
        '    <string name="fov_axis" value="y"/>',
        '    <transform name="to_world">',
        f'      <lookat origin="{csv3(camera_position, [18.0, 30.8, 102.0])}" target="{csv3(camera_target, [18.0, 22.0, 14.0])}" up="{csv3(camera_up, [0.0, 1.0, 0.0])}"/>',
        '    </transform>',
        '    <sampler type="independent">',
        f'      <integer name="sample_count" value="{samples}"/>',
        '    </sampler>',
        f'    <film type="{escape(args.film)}">',
        f'      <integer name="width" value="{width}"/>',
        f'      <integer name="height" value="{height}"/>',
        '      <rfilter type="gaussian"/>',
        '    </film>',
        '  </sensor>',
        '  <emitter type="constant">',
        f'    <rgb name="radiance" value="{csv3(background_radiance, [0.55, 0.62, 0.72])}"/>',
        '  </emitter>',
        *key_light_lines(args, camera_target),
        '  <bsdf type="roughdielectric" id="lsfs_water_surface">',
        f'    <float name="alpha" value="{water_alpha:.8g}"/>',
        f'    <float name="int_ior" value="{water_int_ior:.8g}"/>',
        f'    <float name="ext_ior" value="{water_ext_ior:.8g}"/>',
        *(
            [f'    <rgb name="specular_transmittance" value="{csv3(args.water_specular_transmittance_vec, [1.0, 1.0, 1.0])}"/>']
            if args.water_specular_transmittance_vec is not None else []
        ),
        '  </bsdf>',
        *secondary_bsdf_lines(
            args.secondary_3d_channel_opacity_map
            if secondary_proxy.get("source") == "secondary_3d_sidecar" and args.secondary_3d_channel_opacity_map
            else args.secondary_opacity
        ),
        *secondary_halo_bsdf_lines(args.secondary_halo_opacity),
        *secondary_mist_bsdf_lines(args.secondary_mist_opacity),
        *secondary_billboard_bsdf_lines(args.secondary_billboard_opacity),
        *phase_volume_bsdf_lines(),
        '  <shape type="obj">',
        f'    <string name="filename" value="{xml_path(water_mesh)}"/>',
        '    <boolean name="face_normals" value="true"/>',
        '    <ref name="bsdf" id="lsfs_water_surface"/>',
        '  </shape>',
    ]
    for proxy in phase_volume_proxy.get("proxies", []):
        lines.extend(phase_volume_proxy_shape_lines(proxy))
    if args.secondary_mist_opacity is not None:
        for proxy in secondary_proxy.get("proxies", []):
            lines.extend(secondary_mist_proxy_shape_lines(
                proxy,
                args.secondary_mist_radius_scale,
                args.secondary_mist_shells,
                args.secondary_mist_shell_spacing,
            ))
    if args.secondary_billboard_opacity is not None:
        for proxy in secondary_proxy.get("proxies", []):
            lines.extend(secondary_billboard_proxy_shape_lines(
                proxy,
                args.secondary_billboard_radius_scale,
                args.secondary_billboard_aspect,
                camera_position,
                camera_up,
            ))
    if args.secondary_halo_opacity is not None:
        for proxy in secondary_proxy.get("proxies", []):
            lines.extend(secondary_halo_proxy_shape_lines(proxy, args.secondary_halo_radius_scale))
    for proxy in secondary_proxy.get("proxies", []):
        lines.extend(secondary_proxy_shape_lines(proxy))
    lines.extend([
        '</scene>',
        '',
    ])
    write_text(out_path, "\n".join(lines))
    return {
        "output_frame": scene.get("output_frame"),
        "source_output_frame": scene.get("source_output_frame"),
        "sequence_frame": scene.get("sequence_frame"),
        "time": time,
        "xml_scene": {
            "path": out_path,
            "repo_path": posix_rel(out_path, os.getcwd()),
            "sha256": sha256_file(out_path),
            "size": os.path.getsize(out_path),
        },
        "expected_output": {
            "path": output_image,
            "repo_path": posix_rel(output_image, os.getcwd()),
        },
        "water_mesh": {
            "path": water_mesh,
            "repo_path": posix_rel(water_mesh, os.getcwd()) if water_mesh else None,
            "size": os.path.getsize(water_mesh) if water_mesh and os.path.isfile(water_mesh) else 0,
            "faces": water_faces,
        },
        "sidecar_assets": {
            "phase_cells": posix_rel(phase_cells, os.getcwd()) if phase_cells else None,
            "particles": posix_rel(particles, os.getcwd()) if particles else None,
        },
        "secondary_counts": secondary,
        "secondary_proxy": {
            "enabled": secondary_proxy.get("enabled", False),
            "limit": secondary_proxy.get("limit", 0),
            "available_counts": secondary_proxy.get("available_counts", {}),
            "proxy_counts": secondary_proxy.get("proxy_counts", {}),
            "proxy_count": secondary_proxy.get("proxy_count", 0),
            "halo_enabled": args.secondary_halo_opacity is not None,
            "halo_opacity": args.secondary_halo_opacity,
            "halo_radius_scale": args.secondary_halo_radius_scale if args.secondary_halo_opacity is not None else None,
            "halo_proxy_count": secondary_proxy.get("proxy_count", 0) if args.secondary_halo_opacity is not None else 0,
            "mist_enabled": args.secondary_mist_opacity is not None,
            "mist_opacity": args.secondary_mist_opacity,
            "mist_radius_scale": args.secondary_mist_radius_scale if args.secondary_mist_opacity is not None else None,
            "mist_shells": args.secondary_mist_shells if args.secondary_mist_opacity is not None else 0,
            "mist_shell_spacing": args.secondary_mist_shell_spacing if args.secondary_mist_opacity is not None else None,
            "mist_proxy_count": (
                secondary_proxy.get("proxy_count", 0) * args.secondary_mist_shells
                if args.secondary_mist_opacity is not None else 0
            ),
            "billboard_enabled": args.secondary_billboard_opacity is not None,
            "billboard_opacity": args.secondary_billboard_opacity,
            "billboard_radius_scale": args.secondary_billboard_radius_scale if args.secondary_billboard_opacity is not None else None,
            "billboard_aspect": args.secondary_billboard_aspect if args.secondary_billboard_opacity is not None else None,
            "billboard_proxy_count": secondary_proxy.get("proxy_count", 0) if args.secondary_billboard_opacity is not None else 0,
        },
        "phase_volume_proxy": {
            "enabled": phase_volume_proxy.get("enabled", False),
            "limit": phase_volume_proxy.get("limit", 0),
            "available_count": phase_volume_proxy.get("available_count", 0),
            "proxy_count": phase_volume_proxy.get("proxy_count", 0),
        },
    }


def export_mitsuba(args):
    root = os.getcwd()
    manifest_path = require_file(args.manifest, "adapter manifest")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_external_renderer_adapter_manifest":
        raise SystemExit(f"{args.manifest}: expected lsfs_external_renderer_adapter_manifest schema")
    if manifest.get("status") != "ready":
        raise SystemExit(f"{args.manifest}: adapter manifest status is {manifest.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    exported = []
    failures = []
    commands = []
    secondary_3d_sidecar = load_secondary_3d_sidecar(args.secondary_3d_sidecar, root)
    for index, frame in enumerate(selected_frames(manifest.get("frames") or [], args.frames)):
        scene_path = scene_ref_path(frame)
        if not scene_path or not os.path.isfile(scene_path):
            failures.append({
                "kind": "missing_scene_descriptor",
                "output_frame": frame.get("output_frame"),
                "path": scene_path,
            })
            continue
        scene = read_json(scene_path)
        water_mesh = asset_path(scene, "water_surface")
        if not water_mesh or not os.path.isfile(water_mesh):
            failures.append({
                "kind": "missing_water_mesh",
                "output_frame": frame.get("output_frame"),
                "path": water_mesh,
            })
            continue
        if secondary_3d_sidecar:
            secondary_proxy, proxy_failures = build_secondary_proxy_payload_from_sidecar(
                frame,
                secondary_3d_sidecar,
                args.secondary_proxy_limit,
                args.secondary_3d_radius_scale,
                args.secondary_3d_depth_radius_falloff,
            )
        else:
            secondary_proxy, proxy_failures = build_secondary_proxy_payload(
                scene,
                args.secondary_proxy_limit,
                args.secondary_proxy_radius,
            )
        if proxy_failures:
            failures.extend(proxy_failures)
            continue
        phase_volume_proxy, phase_proxy_failures = build_phase_volume_proxy_payload(
            scene,
            args.phase_volume_proxy_limit,
            args.phase_volume_proxy_radius,
        )
        if phase_proxy_failures:
            failures.extend(phase_proxy_failures)
            continue
        xml_scene = os.path.abspath(os.path.join(scene_dir, f"frame_{index:04d}.xml"))
        output_image = os.path.abspath(os.path.join(render_dir, f"frame_{index:04d}.{args.output_format}"))
        item = write_mitsuba_scene(
            scene,
            xml_scene,
            output_image,
            args,
            secondary_proxy,
            phase_volume_proxy,
        )
        exported.append(item)
        commands.append(render_command(args.mitsuba_command, args.mitsuba_mode, xml_scene, output_image))

    command_list_path = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_text(command_list_path, "\n".join(commands) + ("\n" if commands else ""))
    status = "failed" if failures or not exported else "ready"
    return {
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "title": args.title,
        "adapter_manifest": {
            "path": manifest_path,
            "repo_path": posix_rel(manifest_path, root),
            "sha256": sha256_file(manifest_path),
        },
        "target_renderer": "mitsuba",
        "execution_mode": "xml_export_only",
        "render_settings": {
            "film": args.film,
            "output_format": args.output_format,
            "mitsuba_command": args.mitsuba_command,
            "mitsuba_mode": args.mitsuba_mode,
            "samples_override": args.samples,
            "camera_position_override": args.camera_position_vec,
            "camera_target_override": args.camera_target_vec,
            "camera_up_override": args.camera_up_vec,
            "camera_fov_override": args.camera_fov,
            "background_radiance_override": args.background_radiance_vec,
            "water_alpha_override": args.water_alpha,
            "water_int_ior_override": args.water_int_ior,
            "water_ext_ior_override": args.water_ext_ior,
            "water_specular_transmittance": args.water_specular_transmittance_vec,
            "key_light_radiance": args.key_light_radiance_vec,
            "key_light_position": args.key_light_position_vec,
            "key_light_target": args.key_light_target_vec,
            "key_light_scale": args.key_light_scale_vec,
            "frames_requested": args.frames,
            "frames_exported": len(exported),
            "secondary_proxy_limit": args.secondary_proxy_limit,
            "secondary_proxy_radius": args.secondary_proxy_radius,
            "secondary_3d_sidecar": secondary_3d_sidecar and {
                "repo_path": secondary_3d_sidecar["repo_path"],
                "sha256": secondary_3d_sidecar["sha256"],
                "secondary_particles": secondary_3d_sidecar.get("checks", {}).get("secondary_particles"),
            },
            "secondary_3d_radius_scale": args.secondary_3d_radius_scale,
            "secondary_3d_depth_radius_falloff": args.secondary_3d_depth_radius_falloff,
            "secondary_3d_channel_opacity": args.secondary_3d_channel_opacity_map,
            "secondary_opacity": args.secondary_opacity,
            "secondary_halo_opacity": args.secondary_halo_opacity,
            "secondary_halo_radius_scale": args.secondary_halo_radius_scale,
            "secondary_mist_opacity": args.secondary_mist_opacity,
            "secondary_mist_radius_scale": args.secondary_mist_radius_scale,
            "secondary_mist_shells": args.secondary_mist_shells,
            "secondary_mist_shell_spacing": args.secondary_mist_shell_spacing,
            "secondary_billboard_opacity": args.secondary_billboard_opacity,
            "secondary_billboard_radius_scale": args.secondary_billboard_radius_scale,
            "secondary_billboard_aspect": args.secondary_billboard_aspect,
            "phase_volume_proxy_limit": args.phase_volume_proxy_limit,
            "phase_volume_proxy_radius": args.phase_volume_proxy_radius,
        },
        "command_list": {
            "path": command_list_path,
            "repo_path": posix_rel(command_list_path, root),
            "sha256": sha256_file(command_list_path),
        },
        "checks": {
            "frames_exported": len(exported),
            "failures": len(failures),
            "water_mesh_bytes": sum(item["water_mesh"]["size"] for item in exported),
            "xml_scene_bytes": sum(item["xml_scene"]["size"] for item in exported),
            "secondary_proxy_count": sum(item["secondary_proxy"]["proxy_count"] for item in exported),
            "secondary_halo_proxy_count": sum(item["secondary_proxy"].get("halo_proxy_count", 0) for item in exported),
            "secondary_mist_proxy_count": sum(item["secondary_proxy"].get("mist_proxy_count", 0) for item in exported),
            "secondary_billboard_proxy_count": sum(item["secondary_proxy"].get("billboard_proxy_count", 0) for item in exported),
            "secondary_proxy_available": sum(
                sum(item["secondary_proxy"].get("available_counts", {}).values())
                for item in exported
            ),
            "phase_volume_proxy_count": sum(item["phase_volume_proxy"]["proxy_count"] for item in exported),
            "phase_volume_proxy_available": sum(
                item["phase_volume_proxy"].get("available_count", 0)
                for item in exported
            ),
        },
        "failures": failures,
        "frames": exported,
        "next": args.next,
    }


def markdown_report(export, out_path, root):
    checks = export.get("checks", {})
    lines = [
        f"# {export['title']}",
        "",
        f"Generated UTC: `{export['generated_utc']}`",
        f"Export JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{export['status']}`",
        f"Target renderer: `{export['target_renderer']}`",
        f"Execution mode: `{export['execution_mode']}`",
        "",
        "## Inputs",
        "",
        f"- Adapter manifest: `{export.get('adapter_manifest', {}).get('repo_path')}`",
        f"- Command list: `{export.get('command_list', {}).get('repo_path')}`",
        f"- Mitsuba command: `{export.get('render_settings', {}).get('mitsuba_command')}`",
        f"- Mitsuba mode: `{export.get('render_settings', {}).get('mitsuba_mode')}`",
        f"- Samples override: `{export.get('render_settings', {}).get('samples_override')}`",
        f"- Camera position override: `{export.get('render_settings', {}).get('camera_position_override')}`",
        f"- Camera target override: `{export.get('render_settings', {}).get('camera_target_override')}`",
        f"- Camera FOV override: `{export.get('render_settings', {}).get('camera_fov_override')}`",
        f"- Water alpha override: `{export.get('render_settings', {}).get('water_alpha_override')}`",
        f"- Water int IOR override: `{export.get('render_settings', {}).get('water_int_ior_override')}`",
        f"- Water ext IOR override: `{export.get('render_settings', {}).get('water_ext_ior_override')}`",
        f"- Water specular transmittance: `{export.get('render_settings', {}).get('water_specular_transmittance')}`",
        f"- Key light radiance: `{export.get('render_settings', {}).get('key_light_radiance')}`",
        f"- Key light position: `{export.get('render_settings', {}).get('key_light_position')}`",
        f"- Key light target: `{export.get('render_settings', {}).get('key_light_target')}`",
        f"- Key light scale: `{export.get('render_settings', {}).get('key_light_scale')}`",
        f"- Secondary opacity: `{export.get('render_settings', {}).get('secondary_opacity')}`",
        f"- Secondary 3D sidecar: `{export.get('render_settings', {}).get('secondary_3d_sidecar')}`",
        f"- Secondary 3D radius scale: `{export.get('render_settings', {}).get('secondary_3d_radius_scale')}`",
        f"- Secondary 3D depth radius falloff: `{export.get('render_settings', {}).get('secondary_3d_depth_radius_falloff')}`",
        f"- Secondary 3D channel opacity: `{export.get('render_settings', {}).get('secondary_3d_channel_opacity')}`",
        f"- Secondary halo opacity: `{export.get('render_settings', {}).get('secondary_halo_opacity')}`",
        f"- Secondary halo radius scale: `{export.get('render_settings', {}).get('secondary_halo_radius_scale')}`",
        f"- Secondary mist opacity: `{export.get('render_settings', {}).get('secondary_mist_opacity')}`",
        f"- Secondary mist radius scale: `{export.get('render_settings', {}).get('secondary_mist_radius_scale')}`",
        f"- Secondary mist shells: `{export.get('render_settings', {}).get('secondary_mist_shells')}`",
        f"- Secondary mist shell spacing: `{export.get('render_settings', {}).get('secondary_mist_shell_spacing')}`",
        f"- Secondary billboard opacity: `{export.get('render_settings', {}).get('secondary_billboard_opacity')}`",
        f"- Secondary billboard radius scale: `{export.get('render_settings', {}).get('secondary_billboard_radius_scale')}`",
        f"- Secondary billboard aspect: `{export.get('render_settings', {}).get('secondary_billboard_aspect')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Failures: `{checks.get('failures')}`",
        f"- Water mesh bytes: `{format_bytes(checks.get('water_mesh_bytes', 0))}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        f"- Secondary proxies emitted: `{checks.get('secondary_proxy_count', 0)}`",
        f"- Secondary halo proxies emitted: `{checks.get('secondary_halo_proxy_count', 0)}`",
        f"- Secondary mist proxies emitted: `{checks.get('secondary_mist_proxy_count', 0)}`",
        f"- Secondary billboard proxies emitted: `{checks.get('secondary_billboard_proxy_count', 0)}`",
        f"- Secondary particles available: `{checks.get('secondary_proxy_available', 0)}`",
        f"- Phase volume proxies emitted: `{checks.get('phase_volume_proxy_count', 0)}`",
        f"- Phase volume cells available: `{checks.get('phase_volume_proxy_available', 0)}`",
        "",
        "## Frame Samples",
        "",
        "| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('output_frame')} | `{frame.get('xml_scene', {}).get('repo_path')}` | "
            f"{frame.get('sequence_frame')} | {frame.get('water_mesh', {}).get('faces')} | "
            f"{(frame.get('secondary_counts') or {}).get('total')} | "
            f"{(frame.get('secondary_proxy') or {}).get('proxy_count', 0)} | "
            f"{(frame.get('secondary_proxy') or {}).get('mist_proxy_count', 0)} | "
            f"{(frame.get('secondary_proxy') or {}).get('billboard_proxy_count', 0)} | "
            f"{(frame.get('phase_volume_proxy') or {}).get('proxy_count', 0)} |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"][:12]:
            lines.append(f"- `{failure.get('kind')}`")
    lines.extend([
        "",
        "## Next",
        "",
        export.get("next", "Install Mitsuba or adapt this XML export into the selected renderer backend."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export adapter manifest scenes to Mitsuba XML")
    parser.add_argument("manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--film", default="hdrfilm")
    parser.add_argument("--output-format", default="exr")
    parser.add_argument("--mitsuba-command", default="mitsuba",
                        help="command name or path used in the generated render command list")
    parser.add_argument("--mitsuba-mode", default="scalar_rgb",
                        help="Mitsuba -m variant used in the generated render command list")
    parser.add_argument("--samples", type=int,
                        help="override scene sampler sample_count")
    parser.add_argument("--camera-position",
                        help="override camera origin as x,y,z")
    parser.add_argument("--camera-target",
                        help="override camera target as x,y,z")
    parser.add_argument("--camera-up",
                        help="override camera up vector as x,y,z")
    parser.add_argument("--camera-fov", type=float,
                        help="override perspective vertical FOV in degrees")
    parser.add_argument("--background-radiance",
                        help="override constant emitter radiance as r,g,b")
    parser.add_argument("--water-alpha", type=float,
                        help="override roughdielectric alpha for the water surface")
    parser.add_argument("--water-int-ior", type=float,
                        help="override roughdielectric internal IOR for the water surface")
    parser.add_argument("--water-ext-ior", type=float,
                        help="override roughdielectric external IOR for the water surface")
    parser.add_argument("--water-specular-transmittance",
                        help="override roughdielectric specular transmittance as r,g,b in [0,1]")
    parser.add_argument("--key-light-radiance",
                        help="enable a rectangular area key light with RGB radiance r,g,b")
    parser.add_argument("--key-light-position",
                        help="key light origin as x,y,z")
    parser.add_argument("--key-light-target",
                        help="key light target as x,y,z")
    parser.add_argument("--key-light-scale",
                        help="key light rectangle x,y scale")
    parser.add_argument("--secondary-proxy-limit", type=int, default=0,
                        help="maximum sampled secondary particle sphere proxies per frame")
    parser.add_argument("--secondary-proxy-radius", type=float, default=0.075,
                        help="base radius for secondary particle sphere proxies in cell units")
    parser.add_argument("--secondary-3d-sidecar",
                        help="use an lsfs_mitsuba_secondary_3d_sidecar JSON manifest instead of CSV resampling")
    parser.add_argument("--secondary-3d-radius-scale", type=float, default=1.0,
                        help="radius multiplier applied only to secondary 3D sidecar proxy records")
    parser.add_argument("--secondary-3d-depth-radius-falloff", type=float, default=0.0,
                        help="shrink far secondary 3D sidecar proxies by this normalized depth amount in [0, 1]")
    parser.add_argument("--secondary-3d-channel-opacity",
                        help="per-channel sidecar opacity as spray=v,foam=v,bubble=v,droplet=v")
    parser.add_argument("--secondary-opacity", type=float,
                        help="wrap secondary BSDFs in a Mitsuba mask BSDF with this opacity")
    parser.add_argument("--secondary-halo-opacity", type=float,
                        help="emit larger low-opacity secondary halo proxies with this mask opacity")
    parser.add_argument("--secondary-halo-radius-scale", type=float, default=2.2,
                        help="radius multiplier for secondary halo proxies")
    parser.add_argument("--secondary-mist-opacity", type=float,
                        help="emit broad low-opacity secondary mist shell proxies with this mask opacity")
    parser.add_argument("--secondary-mist-radius-scale", type=float, default=5.0,
                        help="base radius multiplier for secondary mist shell proxies")
    parser.add_argument("--secondary-mist-shells", type=int, default=1,
                        help="number of mist shell proxies emitted for each secondary proxy")
    parser.add_argument("--secondary-mist-shell-spacing", type=float, default=0.55,
                        help="incremental radius multiplier between secondary mist shells")
    parser.add_argument("--secondary-billboard-opacity", type=float,
                        help="emit camera-facing secondary disk billboards with this mask opacity")
    parser.add_argument("--secondary-billboard-radius-scale", type=float, default=2.2,
                        help="radius multiplier for camera-facing secondary disk billboards")
    parser.add_argument("--secondary-billboard-aspect", type=float, default=1.0,
                        help="vertical aspect multiplier for camera-facing secondary disk billboards")
    parser.add_argument("--phase-volume-proxy-limit", type=int, default=0,
                        help="maximum sampled phase-volume sphere proxies per frame")
    parser.add_argument("--phase-volume-proxy-radius", type=float, default=0.11,
                        help="base radius for phase-volume sphere proxies in cell units")
    parser.add_argument("--manifest-name", default="mitsuba_export.json")
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba XML Export")
    parser.add_argument(
        "--next",
        default="Install Mitsuba or add a renderer invocation gate that consumes the exported XML scenes.",
    )
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames <= 0:
        parser.error("frames must be positive")
    if args.secondary_proxy_limit < 0:
        parser.error("secondary-proxy-limit must be non-negative")
    if args.secondary_proxy_radius <= 0.0:
        parser.error("secondary-proxy-radius must be positive")
    if args.secondary_3d_radius_scale <= 0.0:
        parser.error("secondary-3d-radius-scale must be positive")
    if not (0.0 <= args.secondary_3d_depth_radius_falloff <= 1.0):
        parser.error("secondary-3d-depth-radius-falloff must be in the range [0, 1]")
    if args.secondary_opacity is not None and not (0.0 < args.secondary_opacity <= 1.0):
        parser.error("secondary-opacity must be in the range (0, 1]")
    if args.secondary_halo_opacity is not None and not (0.0 < args.secondary_halo_opacity <= 1.0):
        parser.error("secondary-halo-opacity must be in the range (0, 1]")
    if args.secondary_halo_radius_scale <= 0.0:
        parser.error("secondary-halo-radius-scale must be positive")
    if args.secondary_mist_opacity is not None and not (0.0 < args.secondary_mist_opacity <= 1.0):
        parser.error("secondary-mist-opacity must be in the range (0, 1]")
    if args.secondary_mist_radius_scale <= 0.0:
        parser.error("secondary-mist-radius-scale must be positive")
    if args.secondary_mist_shells <= 0:
        parser.error("secondary-mist-shells must be positive")
    if args.secondary_mist_shell_spacing < 0.0:
        parser.error("secondary-mist-shell-spacing must be non-negative")
    if args.secondary_billboard_opacity is not None and not (0.0 < args.secondary_billboard_opacity <= 1.0):
        parser.error("secondary-billboard-opacity must be in the range (0, 1]")
    if args.secondary_billboard_radius_scale <= 0.0:
        parser.error("secondary-billboard-radius-scale must be positive")
    if args.secondary_billboard_aspect <= 0.0:
        parser.error("secondary-billboard-aspect must be positive")
    if args.phase_volume_proxy_limit < 0:
        parser.error("phase-volume-proxy-limit must be non-negative")
    if args.phase_volume_proxy_radius <= 0.0:
        parser.error("phase-volume-proxy-radius must be positive")
    if args.samples is not None and args.samples <= 0:
        parser.error("samples must be positive")
    if args.camera_fov is not None and args.camera_fov <= 0.0:
        parser.error("camera-fov must be positive")
    if args.water_alpha is not None and args.water_alpha <= 0.0:
        parser.error("water-alpha must be positive")
    if args.water_int_ior is not None and args.water_int_ior <= 0.0:
        parser.error("water-int-ior must be positive")
    if args.water_ext_ior is not None and args.water_ext_ior <= 0.0:
        parser.error("water-ext-ior must be positive")
    try:
        args.camera_position_vec = csv3_required(args.camera_position, "camera-position") if args.camera_position else None
        args.camera_target_vec = csv3_required(args.camera_target, "camera-target") if args.camera_target else None
        args.camera_up_vec = csv3_required(args.camera_up, "camera-up") if args.camera_up else None
        args.background_radiance_vec = csv3_required(args.background_radiance, "background-radiance") if args.background_radiance else None
        args.water_specular_transmittance_vec = (
            csv3_required(args.water_specular_transmittance, "water-specular-transmittance")
            if args.water_specular_transmittance else None
        )
        args.key_light_radiance_vec = csv3_required(args.key_light_radiance, "key-light-radiance") if args.key_light_radiance else None
        args.key_light_position_vec = csv3_required(args.key_light_position, "key-light-position") if args.key_light_position else None
        args.key_light_target_vec = csv3_required(args.key_light_target, "key-light-target") if args.key_light_target else None
        args.key_light_scale_vec = csv2_required(args.key_light_scale, "key-light-scale") if args.key_light_scale else None
        args.secondary_3d_channel_opacity_map = parse_channel_values(
            args.secondary_3d_channel_opacity,
            "secondary-3d-channel-opacity",
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.water_specular_transmittance_vec is not None:
        for value in args.water_specular_transmittance_vec:
            if value < 0.0 or value > 1.0:
                parser.error("water-specular-transmittance values must be in [0, 1]")
    if args.key_light_scale_vec is not None and any(value <= 0.0 for value in args.key_light_scale_vec):
        parser.error("key-light-scale values must be positive")

    export = export_mitsuba(args)
    out_path = os.path.abspath(os.path.join(args.out_dir, args.manifest_name))
    write_json(out_path, export)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(export, out_path, os.getcwd()))
    print(
        f"status={export['status']} frames={export['checks']['frames_exported']} "
        f"failures={export['checks']['failures']} export={out_path}"
    )
    print(f"report={report_path}")
    if export["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
