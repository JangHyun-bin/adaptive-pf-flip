#!/usr/bin/env python
"""Build a depth-aware 3D secondary-particle sidecar for Mitsuba experiments."""

import argparse
import csv
import math
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    sha256_file,
    write_json,
    write_text,
)

SECONDARY_CHANNELS = ("spray", "foam", "bubble", "droplet")
DEFAULT_RADIUS_SCALE = {
    "spray": 0.56,
    "foam": 0.96,
    "bubble": 0.4,
    "droplet": 0.5,
}


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def as_float(value, default=0.0):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def csv3_required(value, label):
    parts = [part.strip() for part in value.split(",")] if value else []
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{label} must contain three comma-separated numbers")
    try:
        return [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} contains a non-numeric value") from exc


def selected_frames(frames, requested=None):
    if not frames:
        return []
    if requested is None or requested <= 0 or requested >= len(frames):
        return frames
    if requested == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(requested - 1)) for i in range(requested)))
    return [frames[index] for index in indices]


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


def v_norm(a, fallback):
    length = math.sqrt(max(0.0, v_dot(a, a)))
    if length <= 1e-12:
        return list(fallback)
    return [a[i] / length for i in range(3)]


def project_point(point, camera, width, height):
    position = camera["position"]
    target = camera["target"]
    up = camera["up"]
    forward = v_norm(v_sub(target, position), (0.0, 0.0, -1.0))
    right = v_norm(v_cross(forward, up), (1.0, 0.0, 0.0))
    true_up = v_norm(v_cross(right, forward), (0.0, 1.0, 0.0))
    rel = v_sub(point, position)
    depth = v_dot(rel, forward)
    if depth <= max(1e-6, camera["near_clip"]):
        return {"in_front": False, "depth": depth}
    vfov = math.radians(max(1e-6, camera["vertical_fov_degrees"]))
    aspect = max(1e-6, float(width) / float(max(1, height)))
    half_y = math.tan(vfov * 0.5)
    half_x = half_y * aspect
    sx = v_dot(rel, right) / (depth * half_x)
    sy = v_dot(rel, true_up) / (depth * half_y)
    ndc_x = (sx + 1.0) * 0.5
    ndc_y = 1.0 - ((sy + 1.0) * 0.5)
    return {
        "in_front": True,
        "in_frame": 0.0 <= ndc_x <= 1.0 and 0.0 <= ndc_y <= 1.0,
        "ndc_x": ndc_x,
        "ndc_y": ndc_y,
        "depth": depth,
    }


def scene_ref_path(frame):
    ref = frame.get("scene_descriptor") or {}
    return resolve_path(ref.get("path") or ref.get("repo_path"))


def asset_path(scene, name):
    asset = (scene.get("assets") or {}).get(name) or {}
    return resolve_path(asset.get("path") or asset.get("repo_path"))


def frame_camera(scene, args):
    camera = dict(scene.get("camera") or {})
    return {
        "position": args.camera_position_vec or list(camera.get("position") or [18.0, 30.8, 102.0]),
        "target": args.camera_target_vec or list(camera.get("target") or [18.0, 22.0, 14.0]),
        "up": args.camera_up_vec or list(camera.get("up") or [0.0, 1.0, 0.0]),
        "near_clip": as_float(camera.get("near_clip"), 0.05),
        "far_clip": as_float(camera.get("far_clip"), 220.0),
        "vertical_fov_degrees": args.camera_fov if args.camera_fov is not None else as_float(
            camera.get("vertical_fov_degrees") or camera.get("fov_degrees"),
            45.0,
        ),
    }


def channel_radius_scale(scene, channel):
    channels = (((scene.get("materials") or {}).get("secondary_particles") or {}).get("channels") or {})
    spec = channels.get(channel) or {}
    return as_float(spec.get("radius_scale"), DEFAULT_RADIUS_SCALE[channel])


def volume_radius(base_radius, radius_scale, volume):
    volume_scale = volume ** (1.0 / 3.0) if volume > 0.0 else 1.0
    return base_radius * radius_scale * max(0.55, min(1.45, volume_scale))


def particle_rows(scene, camera, args):
    particles = asset_path(scene, "particle_stream")
    if not particles or not os.path.isfile(particles):
        empty_stats = {
            "available_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
            "projected_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
            "in_frame_counts": {channel: 0 for channel in SECONDARY_CHANNELS},
            "bounds_min": None,
            "bounds_max": None,
            "bounds_valid": False,
        }
        return [], [{"kind": "missing_particle_stream", "path": particles}], empty_stats

    width = int((scene.get("render_settings") or {}).get("width") or args.width)
    height = int((scene.get("render_settings") or {}).get("height") or args.height)
    rows = []
    counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    projected_counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    in_frame_counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    bounds_min = [float("inf"), float("inf"), float("inf")]
    bounds_max = [float("-inf"), float("-inf"), float("-inf")]

    with open(particles, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            channel = (row.get("render_channel") or "").strip().lower()
            if channel not in counts:
                continue
            kind = (row.get("kind") or "").strip().lower()
            if not kind.startswith("secondary"):
                continue

            point = [as_float(row.get("x")), as_float(row.get("y")), as_float(row.get("z"))]
            velocity = [as_float(row.get("vx")), as_float(row.get("vy")), as_float(row.get("vz"))]
            volume = as_float(row.get("volume"), 1.0)
            radius = volume_radius(args.base_radius, channel_radius_scale(scene, channel), volume)
            projection = project_point(point, camera, width, height)
            speed = math.sqrt(max(0.0, v_dot(velocity, velocity)))

            for axis in range(3):
                bounds_min[axis] = min(bounds_min[axis], point[axis])
                bounds_max[axis] = max(bounds_max[axis], point[axis])
            counts[channel] += 1
            if projection.get("in_front"):
                projected_counts[channel] += 1
            if projection.get("in_frame"):
                in_frame_counts[channel] += 1

            rows.append({
                "kind": kind,
                "channel": channel,
                "index": as_int(row.get("index")),
                "phase": (row.get("phase") or "").strip().lower(),
                "position": point,
                "velocity": velocity,
                "speed": speed,
                "volume": volume,
                "age": as_float(row.get("age"), 0.0),
                "radius": radius,
                "camera": {
                    "depth": projection.get("depth"),
                    "in_front": bool(projection.get("in_front")),
                    "in_frame": bool(projection.get("in_frame")),
                    "ndc": [
                        projection.get("ndc_x"),
                        projection.get("ndc_y"),
                    ],
                },
            })

    if args.max_particles_per_frame > 0 and len(rows) > args.max_particles_per_frame:
        step = (len(rows) - 1) / float(max(1, args.max_particles_per_frame - 1))
        keep = sorted(set(round(i * step) for i in range(args.max_particles_per_frame)))
        rows = [rows[index] for index in keep]

    bounds_valid = all(math.isfinite(value) for value in bounds_min + bounds_max)
    return rows, [], {
        "available_counts": counts,
        "projected_counts": projected_counts,
        "in_frame_counts": in_frame_counts,
        "bounds_min": bounds_min if bounds_valid else None,
        "bounds_max": bounds_max if bounds_valid else None,
        "bounds_valid": bounds_valid,
    }


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            import json
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def frame_summary(scene, frame, sidecar_path, rows, stats, root):
    output_frame = frame.get("output_frame")
    counts = {channel: sum(1 for row in rows if row["channel"] == channel) for channel in SECONDARY_CHANNELS}
    return {
        "output_frame": output_frame,
        "sequence_frame": frame.get("sequence_frame"),
        "source_output_frame": frame.get("source_output_frame"),
        "time": scene.get("time"),
        "sidecar": {
            "path": sidecar_path,
            "repo_path": posix_rel(sidecar_path, root),
            "sha256": sha256_file(sidecar_path),
            "size": os.path.getsize(sidecar_path),
        },
        "camera": frame_camera(scene, argparse.Namespace(
            camera_position_vec=None,
            camera_target_vec=None,
            camera_up_vec=None,
            camera_fov=None,
        )),
        "counts": {
            "total": len(rows),
            **counts,
        },
        "available_counts": stats["available_counts"],
        "projected_counts": stats["projected_counts"],
        "in_frame_counts": stats["in_frame_counts"],
        "bounds_min": stats["bounds_min"],
        "bounds_max": stats["bounds_max"],
        "bounds_valid": stats["bounds_valid"],
        "expected_counts": frame.get("secondary_counts") or {},
    }


def markdown_report(summary, summary_path, root, next_text):
    checks = summary["checks"]
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks['frames']}`",
        f"- Sidecar JSONL files: `{checks['sidecar_files']}`",
        f"- Secondary particles: `{checks['secondary_particles']}`",
        f"- In-front particles: `{checks['in_front_particles']}`",
        f"- In-frame particles: `{checks['in_frame_particles']}`",
        f"- Missing references: `{checks['missing_references']}`",
        f"- Sidecar bytes: `{format_bytes(checks['sidecar_bytes'])}`",
        "",
        "## Channel Counts",
        "",
        "| Channel | Count | In front | In frame |",
        "| --- | ---: | ---: | ---: |",
    ]
    for channel in SECONDARY_CHANNELS:
        lines.append(
            f"| {channel} | `{checks['channel_counts'].get(channel, 0)}` | "
            f"`{checks['channel_projected_counts'].get(channel, 0)}` | "
            f"`{checks['channel_in_frame_counts'].get(channel, 0)}` |"
        )
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Sequence | Particles | In frame | Sidecar |",
        "| ---: | ---: | ---: | ---: | --- |",
    ])
    for frame in summary["frames"][:3] + summary["frames"][-1:]:
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('sequence_frame')} | "
            f"{frame['counts'].get('total', 0)} | {sum(frame.get('in_frame_counts', {}).values())} | "
            f"`{frame['sidecar']['repo_path']}` |"
        )
    lines.extend(["", "## Next", "", next_text])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--base-radius", type=float, default=0.095)
    parser.add_argument("--max-particles-per-frame", type=int, default=0)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--camera-position", type=lambda value: csv3_required(value, "camera-position"))
    parser.add_argument("--camera-target", type=lambda value: csv3_required(value, "camera-target"))
    parser.add_argument("--camera-up", type=lambda value: csv3_required(value, "camera-up"))
    parser.add_argument("--camera-fov", type=float)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary 3D Sidecar")
    parser.add_argument("--next", default="Validate the sidecar and wire it into a native Mitsuba secondary import pass.")
    args = parser.parse_args()

    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.base_radius <= 0.0 or not math.isfinite(args.base_radius):
        parser.error("base-radius must be finite and positive")
    if args.max_particles_per_frame < 0:
        parser.error("max-particles-per-frame must be non-negative")
    if args.width <= 0 or args.height <= 0:
        parser.error("width and height must be positive")
    if args.camera_fov is not None and args.camera_fov <= 0.0:
        parser.error("camera-fov must be positive")
    args.camera_position_vec = args.camera_position
    args.camera_target_vec = args.camera_target
    args.camera_up_vec = args.camera_up

    root = os.getcwd()
    manifest_path = resolve_path(args.adapter_manifest)
    manifest = read_json(manifest_path)
    out_dir = resolve_path(args.out_dir)
    sidecar_dir = os.path.join(out_dir, "secondary_3d")
    os.makedirs(sidecar_dir, exist_ok=True)

    frames = selected_frames(manifest.get("frames", []), args.frames)
    output_frames = []
    failures = []
    channel_counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    channel_projected = {channel: 0 for channel in SECONDARY_CHANNELS}
    channel_in_frame = {channel: 0 for channel in SECONDARY_CHANNELS}
    sidecar_bytes = 0

    for index, frame in enumerate(frames):
        scene_path = scene_ref_path(frame)
        if not scene_path or not os.path.isfile(scene_path):
            failures.append({"kind": "missing_scene_descriptor", "output_frame": frame.get("output_frame"), "path": scene_path})
            continue
        scene = read_json(scene_path)
        camera = frame_camera(scene, args)
        rows, row_failures, stats = particle_rows(scene, camera, args)
        failures.extend({"output_frame": frame.get("output_frame"), **failure} for failure in row_failures)
        sidecar_path = os.path.join(sidecar_dir, f"frame_{index:04d}_secondary_3d.jsonl")
        write_jsonl(sidecar_path, rows)
        sidecar_bytes += os.path.getsize(sidecar_path)
        for channel in SECONDARY_CHANNELS:
            channel_counts[channel] += sum(1 for row in rows if row["channel"] == channel)
            channel_projected[channel] += stats["projected_counts"].get(channel, 0)
            channel_in_frame[channel] += stats["in_frame_counts"].get(channel, 0)
        frame_item = {
            "output_frame": frame.get("output_frame"),
            "sequence_frame": frame.get("sequence_frame"),
            "source_output_frame": frame.get("source_output_frame"),
            "time": scene.get("time"),
            "sidecar": {
                "path": sidecar_path,
                "repo_path": posix_rel(sidecar_path, root),
                "sha256": sha256_file(sidecar_path),
                "size": os.path.getsize(sidecar_path),
            },
            "camera": camera,
            "counts": {
                "total": len(rows),
                **{channel: sum(1 for row in rows if row["channel"] == channel) for channel in SECONDARY_CHANNELS},
            },
            "available_counts": stats["available_counts"],
            "projected_counts": stats["projected_counts"],
            "in_frame_counts": stats["in_frame_counts"],
            "bounds_min": stats["bounds_min"],
            "bounds_max": stats["bounds_max"],
            "bounds_valid": stats["bounds_valid"],
            "expected_counts": frame.get("secondary_counts") or {},
        }
        output_frames.append(frame_item)

    secondary_particles = sum(frame["counts"]["total"] for frame in output_frames)
    in_front_particles = sum(sum(frame.get("projected_counts", {}).values()) for frame in output_frames)
    in_frame_particles = sum(sum(frame.get("in_frame_counts", {}).values()) for frame in output_frames)
    summary_path = os.path.join(out_dir, "secondary_3d_sidecar.json")
    summary = {
        "schema": "lsfs_mitsuba_secondary_3d_sidecar",
        "version": 1,
        "title": args.title,
        "status": "ready" if not failures else "review",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest": {
            "path": manifest_path,
            "repo_path": posix_rel(manifest_path, root),
            "schema": manifest.get("schema"),
            "sha256": sha256_file(manifest_path),
        },
        "settings": {
            "frames_requested": args.frames,
            "base_radius": args.base_radius,
            "max_particles_per_frame": args.max_particles_per_frame,
            "projection_space": "mitsuba_direct_lsfs_cell_space",
            "width": args.width,
            "height": args.height,
            "camera_position_override": args.camera_position,
            "camera_target_override": args.camera_target,
            "camera_up_override": args.camera_up,
            "camera_fov_override": args.camera_fov,
        },
        "checks": {
            "frames": len(output_frames),
            "sidecar_files": len(output_frames),
            "secondary_particles": secondary_particles,
            "in_front_particles": in_front_particles,
            "in_frame_particles": in_frame_particles,
            "missing_references": len(failures),
            "sidecar_bytes": sidecar_bytes,
            "channel_counts": channel_counts,
            "channel_projected_counts": channel_projected,
            "channel_in_frame_counts": channel_in_frame,
        },
        "frames": output_frames,
        "failures": failures,
        "next": args.next,
    }
    write_json(summary_path, summary)

    if args.report:
        write_text(resolve_path(args.report), markdown_report(summary, summary_path, root, args.next))

    print(
        "status={status} frames={frames} particles={particles} in_frame={in_frame} summary={summary}".format(
            status=summary["status"],
            frames=len(output_frames),
            particles=secondary_particles,
            in_frame=in_frame_particles,
            summary=summary_path,
        )
    )
    if args.report:
        print(f"report={resolve_path(args.report)}")


if __name__ == "__main__":
    main()
