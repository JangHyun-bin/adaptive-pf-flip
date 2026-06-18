#!/usr/bin/env python
"""Run the LSFS cinematic shot pipeline end to end.

The runner orchestrates existing tools; it does not change simulation or render
formats. It writes a durable shot_summary.json with commands, timings, and
artifact paths so a shot can be inspected or rerun.

Usage:
  python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/bubble_cinematic --frames 24 --width 1280 --height 720
"""

import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone


BUILTIN_PRESETS = {
    "bubble_cinematic": {
        "kind": "sparse",
        "scene": "bubble",
        "nx": 12,
        "ny": 18,
        "nz": 12,
        "dt": 0.02,
        "cg_iters": None,
        "physics_preset": False,
        "description": "Small sparse 3D two-phase bubble tank cinematic smoke preset.",
    },
}


class ShotError(Exception):
    pass


def fail(message):
    raise ShotError(message)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def default_preset_config_path():
    return os.path.join(repo_root(), "configs", "cinematic_presets.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, payload):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path, text):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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


def read_jsonl_section(path, section):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("section") == section:
                return rec
    return {}


def rel_path(path, root):
    if not path:
        return None
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path


def tool_path(root, name):
    return os.path.join(root, "tools", name)


def executable_name(base):
    return base + (".exe" if os.name == "nt" else "")


def exporter_candidates(build_dir, config):
    name = executable_name("export_render_cache3d")
    return [
        os.path.join(build_dir, config, name),
        os.path.join(build_dir, name),
    ]


def find_exporter(build_dir, config):
    for path in exporter_candidates(build_dir, config):
        if os.path.isfile(path):
            return os.path.abspath(path)
    return None


def command_for_summary(command):
    return [str(item) for item in command]


def format_ms(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if value >= 1000.0:
        return f"{value / 1000.0:.2f}s"
    return f"{value:.1f}ms"


def report_path(path, root):
    if not path:
        return "n/a"
    return rel_path(path, root)


def format_secondary_channels(channels):
    if not isinstance(channels, dict) or not channels:
        return "n/a"
    keys = ("spray_count", "droplet_count", "foam_count", "bubble_count", "total_count")
    return " ".join(f"{key.replace('_count', '')}={channels.get(key, 0)}" for key in keys)


def format_secondary_volumes(volumes):
    if not isinstance(volumes, dict) or not volumes:
        return "n/a"
    droplet = float(volumes.get("secondary_droplet_volume", 0.0))
    bubble = float(volumes.get("secondary_bubble_volume", 0.0))
    total = droplet + bubble
    return f"droplet={droplet:.6g} bubble={bubble:.6g} total={total:.6g}"


def secondary_total_count(channels):
    if not isinstance(channels, dict):
        return 0
    return int(channels.get("total_count", 0) or 0)


def parse_key_value_stdout(text):
    metrics = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value in ("true", "false"):
            metrics[key] = value == "true"
            continue
        try:
            metrics[key] = int(value)
            continue
        except ValueError:
            pass
        try:
            metrics[key] = float(value)
            continue
        except ValueError:
            pass
        metrics[key] = value
    return metrics


def key_value_stdout(metrics, status):
    lines = []
    for key in sorted(metrics):
        if key in ("status", "wrote"):
            continue
        value = metrics[key]
        if isinstance(value, bool):
            value = "true" if value else "false"
        lines.append(f"{key}={value}")
    lines.append(f"status={status}")
    return "\n".join(lines) + "\n"


def manifest_cache_assets_exist(manifest_path):
    if not os.path.isfile(manifest_path):
        return False
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError):
        return False
    if manifest.get("lsfs_cache3d_manifest_version") != 1:
        return False
    frames = manifest.get("frames")
    if not isinstance(frames, list) or not frames:
        return False
    if manifest.get("frame_count") != len(frames):
        return False
    base_dir = os.path.dirname(os.path.abspath(manifest_path))
    for frame in frames:
        if not isinstance(frame, dict):
            return False
        frame_path = frame.get("path")
        if not isinstance(frame_path, str) or not frame_path:
            return False
        resolved = frame_path if os.path.isabs(frame_path) else os.path.join(base_dir, frame_path)
        if not os.path.isfile(resolved):
            return False
        expected_bytes = frame.get("bytes")
        if isinstance(expected_bytes, int) and expected_bytes > 0 and os.path.getsize(resolved) != expected_bytes:
            return False
    return True


def export_cache_fingerprint(exporter, export_cmd):
    return {
        "version": 1,
        "exporter": file_fingerprint("exporter", exporter),
        "command": command_for_summary(export_cmd),
    }


def load_reusable_export_cache(stamp_path, expected_fingerprint, manifest_path):
    if not os.path.isfile(stamp_path):
        return None
    try:
        stamp = read_json(stamp_path)
    except (OSError, json.JSONDecodeError):
        return None
    if stamp.get("status") != "ok":
        return None
    if stamp.get("export_fingerprint") != expected_fingerprint:
        return None
    if not manifest_cache_assets_exist(manifest_path):
        return None
    return stamp


def write_export_cache_stamp(path, fingerprint, manifest_path, export_metrics):
    write_json(path, {
        "runner": "lsfs_cinematic_export_cache_stamp",
        "version": 1,
        "status": "ok",
        "manifest": manifest_path,
        "export_fingerprint": fingerprint,
        "export_metrics": export_metrics,
    })


def format_secondary_interface_gate(metrics):
    if not isinstance(metrics, dict) or "secondary_spray_interface_gate" not in metrics:
        return "n/a"
    return (
        f"enabled={metrics.get('secondary_spray_interface_gate')} "
        f"passed={metrics.get('secondary_spray_interface_gate_passed_last')} "
        f"effective_requested={metrics.get('secondary_spray_effective_requested_last', 'n/a')} "
        f"interface_cells={metrics.get('secondary_spray_interface_cells_last', 'n/a')} "
        f"impact_candidates={metrics.get('secondary_spray_impact_candidates_last', 'n/a')} "
        f"foam_ready={metrics.get('secondary_spray_foam_ready_droplets_last', 'n/a')} "
        f"grad_max={metrics.get('secondary_spray_interface_grad_max_last', 'n/a')} "
        f"curvature_abs_max={metrics.get('secondary_spray_interface_curvature_abs_max_last', 'n/a')}"
    )


def secondary_channel_count(channels, name):
    if not isinstance(channels, dict):
        return 0
    return int(channels.get(f"{name}_count", 0) or 0)


def manifest_frame_path(manifest_path, frame_entry):
    path = frame_entry.get("path", "")
    if os.path.isabs(path):
        return path
    return os.path.join(os.path.dirname(os.path.abspath(manifest_path)), path)


def secondary_channel_metrics(manifest_path, manifest):
    frames = manifest.get("frames", [])
    if not frames:
        return {}
    first_path = manifest_frame_path(manifest_path, frames[0])
    last_path = manifest_frame_path(manifest_path, frames[-1])
    out = {
        "first": read_jsonl_section(first_path, "secondary_channels"),
        "last": read_jsonl_section(last_path, "secondary_channels"),
    }
    return out


def secondary_volume_metrics(manifest_path, manifest):
    frames = manifest.get("frames", [])
    if not frames:
        return {}
    first_path = manifest_frame_path(manifest_path, frames[0])
    last_path = manifest_frame_path(manifest_path, frames[-1])
    return {
        "first": read_jsonl_section(first_path, "water_volume"),
        "last": read_jsonl_section(last_path, "water_volume"),
    }


def frame_number_from_path(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    tail = stem.rsplit("_", 1)[-1]
    try:
        return int(tail)
    except ValueError:
        return None


def select_keyframes(frame_dir, count):
    paths = [
        os.path.join(frame_dir, name)
        for name in sorted(os.listdir(frame_dir))
        if name.startswith("frame_") and name.lower().endswith(".png")
    ]
    if not paths:
        fail(f"no PNG frames found in render frame directory: {frame_dir}")
    if count <= 0:
        return []
    if count >= len(paths):
        return paths
    if count == 1:
        return [paths[0]]
    selected = []
    used = set()
    for i in range(count):
        index = int(round(i * (len(paths) - 1) / float(count - 1)))
        while index in used and index + 1 < len(paths):
            index += 1
        while index in used and index > 0:
            index -= 1
        used.add(index)
        selected.append(paths[index])
    return selected


def summarize_values(values):
    if not values:
        return {"min": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "min": min(values),
        "mean": sum(values) / float(len(values)),
        "max": max(values),
    }


def clamp_unit(value, fallback):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = fallback
    return max(0.0, min(1.0, value))


def summarize_temporal_highlights(frame_dir, qa_config):
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        fail("Pillow is required to create the temporal highlight review")

    paths = [
        os.path.join(frame_dir, name)
        for name in sorted(os.listdir(frame_dir))
        if name.startswith("frame_") and name.lower().endswith(".png")
    ]
    target_width = int(qa_config.get("sample_width", 320) or 320)
    highlight_threshold = int(qa_config.get("highlight_threshold", 220) or 220)
    mean_delta = []
    peak_delta = []
    highlight_change_ratio = []
    highlight_ratio = []
    prev = None
    prev_highlight = None
    for path in paths:
        with Image.open(path) as source:
            img = source.convert("L")
            if target_width > 0 and img.width > target_width:
                target_height = max(1, int(round(img.height * (target_width / float(img.width)))))
                resampling = getattr(Image, "Resampling", Image)
                resample_filter = getattr(resampling, "BILINEAR", getattr(Image, "BICUBIC", 3))
                img = img.resize((target_width, target_height), resample_filter)
        highlight = img.point(lambda value: 255 if value >= highlight_threshold else 0)
        pixels = max(1, img.width * img.height)
        highlight_ratio.append(ImageStat.Stat(highlight).sum[0] / float(255 * pixels))
        if prev is not None:
            diff = ImageChops.difference(prev, img)
            mean_delta.append(ImageStat.Stat(diff).mean[0])
            peak_delta.append(diff.getextrema()[1])
            highlight_diff = ImageChops.difference(prev_highlight, highlight)
            highlight_change_ratio.append(ImageStat.Stat(highlight_diff).sum[0] / float(255 * pixels))
        prev = img
        prev_highlight = highlight
    return {
        "frame_count": len(paths),
        "pair_count": max(0, len(paths) - 1),
        "sample_width": target_width,
        "highlight_threshold": highlight_threshold,
        "mean_delta": summarize_values(mean_delta),
        "peak_delta": summarize_values(peak_delta),
        "highlight_change_ratio": summarize_values(highlight_change_ratio),
        "highlight_ratio": summarize_values(highlight_ratio),
    }


def select_temporal_pairs(frame_dir, count):
    paths = [
        os.path.join(frame_dir, name)
        for name in sorted(os.listdir(frame_dir))
        if name.startswith("frame_") and name.lower().endswith(".png")
    ]
    if len(paths) < 2 or count <= 0:
        return []
    pair_total = len(paths) - 1
    if count >= pair_total:
        indexes = list(range(pair_total))
    elif count == 1:
        indexes = [0]
    else:
        indexes = []
        used = set()
        for i in range(count):
            index = int(round(i * (pair_total - 1) / float(count - 1)))
            while index in used and index + 1 < pair_total:
                index += 1
            while index in used and index > 0:
                index -= 1
            used.add(index)
            indexes.append(index)
    return [(paths[index], paths[index + 1]) for index in indexes]


def create_temporal_diff_review(summary, root, frame_dir, diff_config):
    if not isinstance(diff_config, dict) or not diff_config.get("enabled", False):
        return None
    try:
        from PIL import Image, ImageChops, ImageDraw
    except ImportError:
        fail("Pillow is required to create the temporal difference review")

    pairs = select_temporal_pairs(frame_dir, int(diff_config.get("max_pairs", 8) or 8))
    if not pairs:
        return None
    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    diff_dir = os.path.join(review_dir, "temporal_diffs")
    os.makedirs(diff_dir, exist_ok=True)
    target_width = int(diff_config.get("sample_width", 320) or 320)
    amplify = max(1.0, float(diff_config.get("amplify", 3.0) or 3.0))
    label_h = 24
    pad = 12
    diff_images = []
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "BILINEAR", getattr(Image, "BICUBIC", 3))
    for pair_index, (a_path, b_path) in enumerate(pairs):
        with Image.open(a_path) as a_source, Image.open(b_path) as b_source:
            a = a_source.convert("L")
            b = b_source.convert("L")
            if target_width > 0 and a.width > target_width:
                target_height = max(1, int(round(a.height * (target_width / float(a.width)))))
                a = a.resize((target_width, target_height), resample_filter)
                b = b.resize((target_width, target_height), resample_filter)
            diff = ImageChops.difference(a, b)
            diff = diff.point(lambda value: min(255, int(value * amplify)))
            diff_rgb = Image.merge("RGB", (diff, diff, diff))
            a_frame = frame_number_from_path(a_path)
            b_frame = frame_number_from_path(b_path)
            diff_name = f"temporal_diff_{pair_index:02d}_{a_frame:04d}_{b_frame:04d}.png"
            diff_path = os.path.join(diff_dir, diff_name)
            diff_rgb.save(diff_path)
            diff_images.append({
                "source_a": a_path,
                "source_b": b_path,
                "frame_a": a_frame,
                "frame_b": b_frame,
                "diff": diff_path,
            })
    with Image.open(diff_images[0]["diff"]) as first_diff:
        thumb_w, thumb_h = first_diff.size
    columns = min(4, max(1, int(math.ceil(math.sqrt(len(diff_images))))))
    rows = int(math.ceil(len(diff_images) / float(columns)))
    sheet_w = pad + columns * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(diff_images):
        with Image.open(item["diff"]) as img:
            cell = img.convert("RGB")
        col = index % columns
        row = index // columns
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        sheet.paste(cell, (x, y))
        draw.text((x + 6, y + thumb_h + 5),
                  f"frames {item['frame_a']:04d}->{item['frame_b']:04d}",
                  fill=(224, 234, 240))
    sheet_path = os.path.join(review_dir, "temporal_diff_sheet.png")
    manifest_path = os.path.join(review_dir, "temporal_diff_manifest.json")
    sheet.save(sheet_path)
    manifest = {
        "schema": "lsfs_cinematic_temporal_diff_review",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "render_preset": summary.get("render_preset"),
        "sample_width": target_width,
        "amplify": amplify,
        "temporal_diff_sheet": rel_path(sheet_path, root),
        "pair_count": len(diff_images),
        "pairs": [
            {
                "frame_a": item["frame_a"],
                "frame_b": item["frame_b"],
                "source_a": rel_path(item["source_a"], root),
                "source_b": rel_path(item["source_b"], root),
                "diff": rel_path(item["diff"], root),
            }
            for item in diff_images
        ],
    }
    write_json(manifest_path, manifest)
    return {
        "temporal_diff_sheet": sheet_path,
        "temporal_diff_manifest": manifest_path,
        "temporal_diff_pair_count": len(diff_images),
    }


def create_review_pack(summary, root, frame_dir, review_frame_count):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the cinematic review pack")

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    keyframe_dir = os.path.join(review_dir, "keyframes")
    os.makedirs(keyframe_dir, exist_ok=True)
    selected = select_keyframes(frame_dir, review_frame_count)
    if not selected:
        fail("review pack requires at least one key frame")

    with Image.open(selected[0]) as first:
        src_w, src_h = first.size
    thumb_w = min(320, max(160, src_w // 3))
    thumb_h = max(1, int(round(src_h * (thumb_w / float(src_w)))))
    label_h = 24
    pad = 12
    columns = min(4, max(1, int(math.ceil(math.sqrt(len(selected))))))
    rows = int(math.ceil(len(selected) / float(columns)))
    sheet_w = pad + columns * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 22, 26))
    draw = ImageDraw.Draw(sheet)
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))

    keyframes = []
    for out_index, source in enumerate(selected):
        with Image.open(source) as img:
            thumb = img.convert("RGB")
            thumb.thumbnail((thumb_w, thumb_h), resample_filter)
            cell = Image.new("RGB", (thumb_w, thumb_h), (8, 10, 12))
            cell.paste(thumb, ((thumb_w - thumb.width) // 2, (thumb_h - thumb.height) // 2))
            thumb_name = f"keyframe_{out_index:02d}_{os.path.basename(source)}"
            thumb_path = os.path.join(keyframe_dir, thumb_name)
            cell.save(thumb_path)

        col = out_index % columns
        row = out_index // columns
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        sheet.paste(cell, (x, y))
        frame_no = frame_number_from_path(source)
        label = f"frame {frame_no:04d}" if frame_no is not None else os.path.basename(source)
        draw.text((x + 6, y + thumb_h + 5), label, fill=(224, 234, 240))
        keyframes.append({
            "source": source,
            "thumbnail": thumb_path,
            "frame": frame_no,
        })

    contact_sheet = os.path.join(review_dir, "contact_sheet.png")
    sheet.save(contact_sheet)
    manifest_path = os.path.join(review_dir, "review_manifest.json")
    metrics = dict(summary.get("metrics", {}))
    metrics["review_frame_count"] = len(keyframes)
    manifest = {
        "schema": "lsfs_cinematic_review_pack",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "render_preset": summary.get("render_preset"),
        "selected_renderer": summary.get("selected_renderer"),
        "frame_count": summary.get("config", {}).get("frames"),
        "contact_sheet": rel_path(contact_sheet, root),
        "gif": rel_path(summary.get("artifacts", {}).get("gif"), root),
        "report": rel_path(summary.get("artifacts", {}).get("report"), root),
        "shot_summary": rel_path(os.path.join(out_dir, "shot_summary.json"), root),
        "render_frame_dir": rel_path(frame_dir, root),
        "focus_sheet": rel_path(summary.get("artifacts", {}).get("focus_sheet"), root),
        "focus_review_manifest": rel_path(summary.get("artifacts", {}).get("focus_review_manifest"), root),
        "secondary_depth_sheet": rel_path(summary.get("artifacts", {}).get("secondary_depth_sheet"), root),
        "secondary_depth_manifest": rel_path(summary.get("artifacts", {}).get("secondary_depth_manifest"), root),
        "ripple_readability_sheet": rel_path(summary.get("artifacts", {}).get("ripple_readability_sheet"), root),
        "ripple_readability_manifest": rel_path(summary.get("artifacts", {}).get("ripple_readability_manifest"), root),
        "metrics": metrics,
        "keyframes": [
            {
                "frame": item["frame"],
                "source": rel_path(item["source"], root),
                "thumbnail": rel_path(item["thumbnail"], root),
            }
            for item in keyframes
        ],
    }
    write_json(manifest_path, manifest)
    return {
        "review_dir": review_dir,
        "contact_sheet": contact_sheet,
        "review_manifest": manifest_path,
        "review_keyframes": [item["thumbnail"] for item in keyframes],
        "review_frame_count": len(keyframes),
    }


def normalized_crop(crop):
    if not isinstance(crop, (list, tuple)) or len(crop) != 4:
        crop = (0.02, 0.34, 0.98, 0.9)
    left = clamp_unit(crop[0], 0.02)
    top = clamp_unit(crop[1], 0.34)
    right = clamp_unit(crop[2], 0.98)
    bottom = clamp_unit(crop[3], 0.9)
    if right <= left:
        left, right = 0.0, 1.0
    if bottom <= top:
        top, bottom = 0.0, 1.0
    return [left, top, right, bottom]


def crop_box_for_image(image, crop):
    left, top, right, bottom = normalized_crop(crop)
    x0 = max(0, min(image.width - 1, int(round(left * image.width))))
    y0 = max(0, min(image.height - 1, int(round(top * image.height))))
    x1 = max(x0 + 1, min(image.width, int(round(right * image.width))))
    y1 = max(y0 + 1, min(image.height, int(round(bottom * image.height))))
    return x0, y0, x1, y1


def scalar_value(value, fallback=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def vec3_value(value, fallback=(0.0, 0.0, 0.0)):
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return [scalar_value(value[0]), scalar_value(value[1]), scalar_value(value[2])]
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


def v_norm(a, fallback=(0.0, 0.0, 1.0)):
    length = math.sqrt(max(0.0, v_dot(a, a)))
    if length <= 1e-12:
        return [fallback[0], fallback[1], fallback[2]]
    return [a[i] / length for i in range(3)]


def to_blender_coords(point):
    return [scalar_value(point[0]), -scalar_value(point[2]), scalar_value(point[1])]


def project_scene_point(point, camera, width, height):
    position = to_blender_coords(vec3_value(camera.get("position"), (0.0, 0.0, 1.0)))
    target = to_blender_coords(vec3_value(camera.get("target"), (0.0, 0.0, 0.0)))
    up = to_blender_coords(vec3_value(camera.get("up"), (0.0, 1.0, 0.0)))
    forward = v_norm(v_sub(target, position), (0.0, 0.0, -1.0))
    right = v_norm(v_cross(forward, up), (1.0, 0.0, 0.0))
    true_up = v_norm(v_cross(right, forward), (0.0, 0.0, 1.0))
    rel = v_sub(to_blender_coords(point), position)
    depth = v_dot(rel, forward)
    if depth <= max(1e-6, scalar_value(camera.get("near_clip"), 0.05)):
        return None
    vfov = math.radians(max(1e-6, scalar_value(camera.get("vertical_fov_degrees"), 45.0)))
    aspect = max(1e-6, float(width) / float(max(1, height)))
    half_y = math.tan(vfov * 0.5)
    half_x = half_y * aspect
    x = v_dot(rel, right) / (depth * half_x)
    y = v_dot(rel, true_up) / (depth * half_y)
    return {
        "x": (x + 1.0) * 0.5,
        "y": 1.0 - ((y + 1.0) * 0.5),
        "depth": depth,
    }


def secondary_render_channel(row):
    channel = (row.get("render_channel") or row.get("channel") or "").strip().lower()
    if channel in ("droplet", "spray", "foam", "bubble"):
        return channel
    kind = (row.get("kind") or "").strip().lower()
    if kind == "secondary_bubble":
        return "bubble"
    if kind == "secondary_droplet":
        return "droplet"
    return channel


def load_render_scene_spec(summary):
    render_summary_path = summary.get("artifacts", {}).get("render_summary")
    if not render_summary_path or not os.path.isfile(render_summary_path):
        return None, None
    render_summary = read_json(render_summary_path)
    spec_path = render_summary.get("scene_spec")
    if not spec_path:
        return None, None
    if not os.path.isabs(spec_path):
        spec_path = os.path.abspath(os.path.join(os.path.dirname(render_summary_path), spec_path))
    if not os.path.isfile(spec_path):
        return None, None
    return spec_path, read_json(spec_path)


def scene_spec_frame_lookup(spec):
    by_output = {}
    by_index = {}
    for frame in spec.get("frames", []):
        output = frame.get("output_png")
        if output:
            by_output[os.path.normcase(os.path.abspath(output))] = frame
        try:
            by_index[int(frame.get("index"))] = frame
        except (TypeError, ValueError):
            pass
    return by_output, by_index


def summarize_secondary_depth_stats(frame_stats):
    return {
        "active_particles": summarize_values([item["active_particles"] for item in frame_stats]),
        "crop_particles": summarize_values([item["crop_particles"] for item in frame_stats]),
        "crop_ratio": summarize_values([item["crop_ratio"] for item in frame_stats]),
        "depth_mean": summarize_values([item["depth_mean"] for item in frame_stats if item["crop_particles"] > 0]),
        "depth_span": summarize_values([item["depth_span"] for item in frame_stats if item["crop_particles"] > 0]),
        "normalized_depth_span": summarize_values([
            item["normalized_depth_span"] for item in frame_stats if item["crop_particles"] > 0
        ]),
        "channel_depth_delta": summarize_values([
            item["channel_depth_delta"] for item in frame_stats if item["crop_particles"] > 0
        ]),
    }


def create_secondary_depth_review(summary, root, frame_dir, review_config, review_frame_count):
    if not isinstance(review_config, dict) or not review_config.get("enabled", False):
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the secondary depth review")

    spec_path, spec = load_render_scene_spec(summary)
    if not spec:
        fail("secondary depth review requires a Blender scene spec")
    by_output, by_index = scene_spec_frame_lookup(spec)
    selected = select_keyframes(frame_dir, review_frame_count)
    if not selected:
        fail("secondary depth review requires at least one key frame")

    channels_cfg = review_config.get("channels") if isinstance(review_config.get("channels"), dict) else {}
    enabled_channels = {name for name, enabled in channels_cfg.items() if enabled}
    if not enabled_channels:
        enabled_channels = {"spray", "foam"}
    crop = normalized_crop(review_config.get("crop", (0.02, 0.2, 0.98, 0.9)))
    thumb_w = max(160, int(review_config.get("thumbnail_width", 420) or 420))
    label_h = 42
    pad = 12
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    keyframe_dir = os.path.join(review_dir, "secondary_depth_keyframes")
    os.makedirs(keyframe_dir, exist_ok=True)

    frame_items = []
    frame_stats = []
    thumb_h = None
    channel_colors = {
        "spray": (120, 226, 255),
        "foam": (255, 238, 150),
        "droplet": (160, 220, 255),
        "bubble": (255, 170, 80),
    }
    for out_index, source in enumerate(selected):
        frame_no = frame_number_from_path(source)
        spec_frame = by_output.get(os.path.normcase(os.path.abspath(source)))
        if spec_frame is None and frame_no is not None:
            spec_frame = by_index.get(frame_no)
        if spec_frame is None:
            fail(f"secondary depth review cannot match frame: {source}")

        with Image.open(source) as img:
            rgb = img.convert("RGB")
            box = crop_box_for_image(rgb, crop)
            crop_img = rgb.crop(box)
            draw = ImageDraw.Draw(crop_img)
            active = 0
            crop_particles = 0
            depths = []
            channel_depths = {name: [] for name in enabled_channels}
            points = []
            particle_path = spec_frame.get("particles_csv")
            if particle_path and os.path.isfile(particle_path):
                with open(particle_path, encoding="utf-8", newline="") as f:
                    for row in csv.DictReader(f):
                        channel = secondary_render_channel(row)
                        if channel not in enabled_channels:
                            continue
                        active += 1
                        projected = project_scene_point(
                            [row.get("x", 0.0), row.get("y", 0.0), row.get("z", 0.0)],
                            spec_frame.get("camera", {}),
                            rgb.width,
                            rgb.height)
                        if not projected:
                            continue
                        x = projected["x"]
                        y = projected["y"]
                        if crop[0] <= x <= crop[2] and crop[1] <= y <= crop[3]:
                            crop_particles += 1
                            depth = projected["depth"]
                            depths.append(depth)
                            channel_depths.setdefault(channel, []).append(depth)
                            px = int(round((x - crop[0]) / max(1e-6, crop[2] - crop[0]) * crop_img.width))
                            py = int(round((y - crop[1]) / max(1e-6, crop[3] - crop[1]) * crop_img.height))
                            points.append((px, py, channel))
            for px, py, channel in points:
                color = channel_colors.get(channel, (240, 240, 240))
                radius = 2 if channel == "spray" else 3
                draw.ellipse((px - radius, py - radius, px + radius, py + radius), outline=color, fill=color)

            depth_mean = sum(depths) / float(len(depths)) if depths else 0.0
            depth_span = max(depths) - min(depths) if depths else 0.0
            normalized_span = depth_span / depth_mean if depth_mean > 1e-6 else 0.0
            means = [
                sum(values) / float(len(values))
                for values in channel_depths.values()
                if values
            ]
            channel_delta = max(means) - min(means) if len(means) >= 2 else 0.0
            stats = {
                "active_particles": active,
                "crop_particles": crop_particles,
                "crop_ratio": crop_particles / float(max(1, active)),
                "depth_mean": depth_mean,
                "depth_span": depth_span,
                "normalized_depth_span": normalized_span,
                "channel_depth_delta": channel_delta,
                "channel_counts": {name: len(channel_depths.get(name, [])) for name in sorted(enabled_channels)},
            }
            label = f"n={crop_particles}/{active} span={depth_span:.2f} norm={normalized_span:.2f}"
            draw.rectangle((5, 5, min(crop_img.width - 1, 5 + len(label) * 7), 24), fill=(8, 10, 12))
            draw.text((9, 8), label, fill=(232, 240, 245))

            thumb = crop_img
            target_h = max(1, int(round(thumb.height * (thumb_w / float(thumb.width)))))
            thumb = thumb.resize((thumb_w, target_h), resample_filter)
            if thumb_h is None:
                thumb_h = thumb.height
            depth_name = f"secondary_depth_{out_index:02d}_{os.path.basename(source)}"
            depth_path = os.path.join(keyframe_dir, depth_name)
            thumb.save(depth_path)

        frame_stats.append(stats)
        frame_items.append({
            "source": source,
            "thumbnail": depth_path,
            "frame": frame_no,
            "stats": stats,
        })

    thumb_h = thumb_h or max(1, int(round(thumb_w * 0.56)))
    columns = min(4, max(1, int(math.ceil(math.sqrt(len(frame_items))))))
    rows = int(math.ceil(len(frame_items) / float(columns)))
    sheet_w = pad + columns * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(frame_items):
        with Image.open(item["thumbnail"]) as img:
            cell = img.convert("RGB")
        if cell.size != (thumb_w, thumb_h):
            base = Image.new("RGB", (thumb_w, thumb_h), (8, 10, 12))
            base.paste(cell, ((thumb_w - cell.width) // 2, (thumb_h - cell.height) // 2))
            cell = base
        col = index % columns
        row = index // columns
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        sheet.paste(cell, (x, y))
        label = f"frame {item['frame']:04d}" if item["frame"] is not None else os.path.basename(item["source"])
        metric = item["stats"]
        draw.text((x + 6, y + thumb_h + 5), label, fill=(224, 234, 240))
        draw.text((x + 6, y + thumb_h + 23),
                  f"crop={metric['crop_particles']} span={metric['depth_span']:.2f}",
                  fill=(170, 198, 214))

    sheet_path = os.path.join(review_dir, "secondary_depth_sheet.png")
    manifest_path = os.path.join(review_dir, "secondary_depth_manifest.json")
    sheet.save(sheet_path)
    metrics = {
        "enabled": True,
        "frame_count": len(frame_items),
        "active_frame_count": sum(1 for item in frame_stats if item["crop_particles"] > 0),
        "crop": crop,
        "channels": sorted(enabled_channels),
        "summary": summarize_secondary_depth_stats(frame_stats),
    }
    manifest = {
        "schema": "lsfs_cinematic_secondary_depth_review",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "render_preset": summary.get("render_preset"),
        "selected_renderer": summary.get("selected_renderer"),
        "scene_spec": rel_path(spec_path, root),
        "secondary_depth_sheet": rel_path(sheet_path, root),
        "render_frame_dir": rel_path(frame_dir, root),
        "metrics": metrics,
        "keyframes": [
            {
                "frame": item["frame"],
                "source": rel_path(item["source"], root),
                "thumbnail": rel_path(item["thumbnail"], root),
                "stats": item["stats"],
            }
            for item in frame_items
        ],
    }
    write_json(manifest_path, manifest)
    return {
        "secondary_depth_sheet": sheet_path,
        "secondary_depth_manifest": manifest_path,
        "secondary_depth_review": metrics,
    }


def focus_image_stats(image, bright_threshold, nonblank_threshold):
    from PIL import ImageStat

    gray = image.convert("L")
    extrema = gray.getextrema()
    pixels = max(1, gray.width * gray.height)
    bright = gray.point(lambda value: 255 if value >= bright_threshold else 0)
    nonblank = gray.point(lambda value: 255 if value > nonblank_threshold else 0)
    return {
        "mean_luminance": ImageStat.Stat(gray).mean[0],
        "contrast": float(extrema[1] - extrema[0]),
        "bright_ratio": ImageStat.Stat(bright).sum[0] / float(255 * pixels),
        "nonblank_ratio": ImageStat.Stat(nonblank).sum[0] / float(255 * pixels),
    }


def summarize_focus_stats(frame_stats):
    return {
        "mean_luminance": summarize_values([item["mean_luminance"] for item in frame_stats]),
        "contrast": summarize_values([item["contrast"] for item in frame_stats]),
        "bright_ratio": summarize_values([item["bright_ratio"] for item in frame_stats]),
        "nonblank_ratio": summarize_values([item["nonblank_ratio"] for item in frame_stats]),
    }


def create_focus_review(summary, root, frame_dir, focus_config, review_frame_count):
    if not isinstance(focus_config, dict) or not focus_config.get("enabled", False):
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the cinematic focus review")

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    focus_dir = os.path.join(review_dir, "focus_keyframes")
    os.makedirs(focus_dir, exist_ok=True)
    selected = select_keyframes(frame_dir, review_frame_count)
    if not selected:
        fail("focus review requires at least one key frame")

    crop = normalized_crop(focus_config.get("crop"))
    bright_threshold = int(focus_config.get("bright_threshold", 220) or 220)
    nonblank_threshold = int(focus_config.get("nonblank_threshold", 8) or 8)
    thumb_w = max(160, int(focus_config.get("thumbnail_width", 420) or 420))
    label_h = 24
    pad = 12
    columns = min(4, max(1, int(math.ceil(math.sqrt(len(selected))))))
    rows = int(math.ceil(len(selected) / float(columns)))
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))

    focus_frames = []
    frame_stats = []
    thumb_h = None
    for out_index, source in enumerate(selected):
        with Image.open(source) as img:
            rgb = img.convert("RGB")
            box = crop_box_for_image(rgb, crop)
            crop_img = rgb.crop(box)
            stats = focus_image_stats(crop_img, bright_threshold, nonblank_threshold)
            thumb = crop_img
            if thumb.width > thumb_w:
                target_h = max(1, int(round(thumb.height * (thumb_w / float(thumb.width)))))
                thumb = thumb.resize((thumb_w, target_h), resample_filter)
            elif thumb.width < thumb_w:
                target_h = max(1, int(round(thumb.height * (thumb_w / float(thumb.width)))))
                thumb = thumb.resize((thumb_w, target_h), resample_filter)
            if thumb_h is None:
                thumb_h = thumb.height
            focus_name = f"focus_{out_index:02d}_{os.path.basename(source)}"
            focus_path = os.path.join(focus_dir, focus_name)
            thumb.save(focus_path)

        frame_no = frame_number_from_path(source)
        frame_stats.append(stats)
        focus_frames.append({
            "source": source,
            "thumbnail": focus_path,
            "frame": frame_no,
            "stats": stats,
        })

    thumb_h = thumb_h or max(1, int(round(thumb_w * 0.56)))
    sheet_w = pad + columns * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(focus_frames):
        with Image.open(item["thumbnail"]) as img:
            cell = img.convert("RGB")
        if cell.size != (thumb_w, thumb_h):
            base = Image.new("RGB", (thumb_w, thumb_h), (8, 10, 12))
            base.paste(cell, ((thumb_w - cell.width) // 2, (thumb_h - cell.height) // 2))
            cell = base
        col = index % columns
        row = index // columns
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        sheet.paste(cell, (x, y))
        label = f"frame {item['frame']:04d}" if item["frame"] is not None else os.path.basename(item["source"])
        draw.text((x + 6, y + thumb_h + 5), label, fill=(224, 234, 240))

    focus_sheet = os.path.join(review_dir, "focus_sheet.png")
    manifest_path = os.path.join(review_dir, "focus_review_manifest.json")
    sheet.save(focus_sheet)
    metrics = {
        "enabled": True,
        "frame_count": len(focus_frames),
        "crop": crop,
        "bright_threshold": bright_threshold,
        "nonblank_threshold": nonblank_threshold,
        "summary": summarize_focus_stats(frame_stats),
    }
    manifest = {
        "schema": "lsfs_cinematic_focus_review",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "render_preset": summary.get("render_preset"),
        "selected_renderer": summary.get("selected_renderer"),
        "focus_sheet": rel_path(focus_sheet, root),
        "render_frame_dir": rel_path(frame_dir, root),
        "metrics": metrics,
        "keyframes": [
            {
                "frame": item["frame"],
                "source": rel_path(item["source"], root),
                "thumbnail": rel_path(item["thumbnail"], root),
                "stats": item["stats"],
            }
            for item in focus_frames
        ],
    }
    write_json(manifest_path, manifest)
    return {
        "focus_sheet": focus_sheet,
        "focus_review_manifest": manifest_path,
        "focus_review": metrics,
    }


def summarize_readability_stats(frame_stats):
    return {
        "edge_mean": summarize_values([item["edge_mean"] for item in frame_stats]),
        "edge_nonzero_ratio": summarize_values([item["edge_nonzero_ratio"] for item in frame_stats]),
        "highlight_ratio": summarize_values([item["highlight_ratio"] for item in frame_stats]),
        "mean_luminance": summarize_values([item["mean_luminance"] for item in frame_stats]),
    }


def create_ripple_readability_review(summary, root, frame_dir, review_config, review_frame_count):
    if not isinstance(review_config, dict) or not review_config.get("enabled", False):
        return None
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageStat
    except ImportError:
        fail("Pillow is required to create the ripple readability review")

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    keyframe_dir = os.path.join(review_dir, "ripple_readability_keyframes")
    os.makedirs(keyframe_dir, exist_ok=True)
    selected = select_keyframes(frame_dir, review_frame_count)
    if not selected:
        fail("ripple readability review requires at least one key frame")

    crop = normalized_crop(review_config.get("crop"))
    thumb_w = max(160, int(review_config.get("thumbnail_width", 420) or 420))
    edge_amplify = max(1.0, float(review_config.get("edge_amplify", 3.0) or 3.0))
    edge_threshold = int(review_config.get("edge_threshold", 18) or 18)
    highlight_threshold = int(review_config.get("highlight_threshold", 220) or 220)
    label_h = 24
    pad = 12
    columns = min(4, max(1, int(math.ceil(math.sqrt(len(selected))))))
    rows = int(math.ceil(len(selected) / float(columns)))
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))

    frames = []
    frame_stats = []
    thumb_h = None
    for out_index, source in enumerate(selected):
        with Image.open(source) as img:
            crop_img = img.convert("RGB").crop(crop_box_for_image(img, crop))
            gray = crop_img.convert("L")
            edge = gray.filter(ImageFilter.FIND_EDGES)
            edge = edge.point(lambda value: min(255, int(value * edge_amplify)))
            edge = ImageOps.autocontrast(edge)
            highlight = gray.point(lambda value: 255 if value >= highlight_threshold else 0)
            pixels = max(1, edge.width * edge.height)
            edge_nonzero = edge.point(lambda value: 255 if value >= edge_threshold else 0)
            stats = {
                "edge_mean": ImageStat.Stat(edge).mean[0],
                "edge_nonzero_ratio": ImageStat.Stat(edge_nonzero).sum[0] / float(255 * pixels),
                "highlight_ratio": ImageStat.Stat(highlight).sum[0] / float(255 * pixels),
                "mean_luminance": ImageStat.Stat(gray).mean[0],
            }
            diag = Image.merge("RGB", (edge, edge, highlight))
            if diag.width != thumb_w:
                target_h = max(1, int(round(diag.height * (thumb_w / float(diag.width)))))
                diag = diag.resize((thumb_w, target_h), resample_filter)
            if thumb_h is None:
                thumb_h = diag.height
            diag_name = f"ripple_diag_{out_index:02d}_{os.path.basename(source)}"
            diag_path = os.path.join(keyframe_dir, diag_name)
            diag.save(diag_path)

        frame_no = frame_number_from_path(source)
        frame_stats.append(stats)
        frames.append({
            "source": source,
            "thumbnail": diag_path,
            "frame": frame_no,
            "stats": stats,
        })

    thumb_h = thumb_h or max(1, int(round(thumb_w * 0.56)))
    sheet_w = pad + columns * (thumb_w + pad)
    sheet_h = pad + rows * (thumb_h + label_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(frames):
        with Image.open(item["thumbnail"]) as img:
            cell = img.convert("RGB")
        if cell.size != (thumb_w, thumb_h):
            base = Image.new("RGB", (thumb_w, thumb_h), (8, 10, 12))
            base.paste(cell, ((thumb_w - cell.width) // 2, (thumb_h - cell.height) // 2))
            cell = base
        col = index % columns
        row = index // columns
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        sheet.paste(cell, (x, y))
        label = f"frame {item['frame']:04d}" if item["frame"] is not None else os.path.basename(item["source"])
        draw.text((x + 6, y + thumb_h + 5), label, fill=(224, 234, 240))

    sheet_path = os.path.join(review_dir, "ripple_readability_sheet.png")
    manifest_path = os.path.join(review_dir, "ripple_readability_manifest.json")
    sheet.save(sheet_path)
    metrics = {
        "enabled": True,
        "frame_count": len(frames),
        "crop": crop,
        "edge_amplify": edge_amplify,
        "edge_threshold": edge_threshold,
        "highlight_threshold": highlight_threshold,
        "summary": summarize_readability_stats(frame_stats),
    }
    manifest = {
        "schema": "lsfs_cinematic_ripple_readability_review",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "render_preset": summary.get("render_preset"),
        "selected_renderer": summary.get("selected_renderer"),
        "ripple_readability_sheet": rel_path(sheet_path, root),
        "render_frame_dir": rel_path(frame_dir, root),
        "metrics": metrics,
        "keyframes": [
            {
                "frame": item["frame"],
                "source": rel_path(item["source"], root),
                "thumbnail": rel_path(item["thumbnail"], root),
                "stats": item["stats"],
            }
            for item in frames
        ],
    }
    write_json(manifest_path, manifest)
    return {
        "ripple_readability_sheet": sheet_path,
        "ripple_readability_manifest": manifest_path,
        "ripple_readability": metrics,
    }


def resolve_review_artifact(manifest_path, root, path):
    if not path:
        return None
    candidates = []
    if os.path.isabs(path):
        candidates.append(path)
    else:
        candidates.append(os.path.abspath(os.path.join(root, path)))
        candidates.append(os.path.abspath(os.path.join(os.path.dirname(manifest_path), path)))
        candidates.append(os.path.abspath(path))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return candidates[0] if candidates else None


def load_review_source(path, root):
    manifest_path = os.path.abspath(path)
    if not os.path.isfile(manifest_path):
        fail(f"comparison review manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_cinematic_review_pack":
        fail(f"{manifest_path}: expected lsfs_cinematic_review_pack schema")
    contact_sheet = resolve_review_artifact(manifest_path, root, manifest.get("contact_sheet"))
    if not contact_sheet or not os.path.isfile(contact_sheet):
        fail(f"{manifest_path}: comparison contact sheet not found")
    return {
        "manifest": manifest_path,
        "contact_sheet": contact_sheet,
        "shot_preset": manifest.get("shot_preset", "unknown"),
        "render_preset": manifest.get("render_preset", "unknown"),
        "selected_renderer": manifest.get("selected_renderer", "unknown"),
        "frame_count": manifest.get("frame_count", "n/a"),
    }


def create_review_comparison(summary, root, current_review_manifest, compare_manifests):
    if not compare_manifests:
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the cinematic review comparison")

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    os.makedirs(review_dir, exist_ok=True)
    sources = [load_review_source(path, root) for path in compare_manifests]
    sources.append(load_review_source(current_review_manifest, root))

    max_panel_w = 640
    label_h = 40
    pad = 14
    panels = []
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    for source in sources:
        with Image.open(source["contact_sheet"]) as img:
            panel = img.convert("RGB")
            if panel.width > max_panel_w:
                scale = max_panel_w / float(panel.width)
                panel = panel.resize((max_panel_w, max(1, int(round(panel.height * scale)))), resample_filter)
        panels.append((source, panel))

    columns = min(2, len(panels))
    rows = int(math.ceil(len(panels) / float(columns)))
    panel_w = max(panel.width for _source, panel in panels)
    panel_h = max(panel.height for _source, panel in panels)
    sheet_w = pad + columns * (panel_w + pad)
    sheet_h = pad + rows * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, (source, panel) in enumerate(panels):
        col = index % columns
        row = index // columns
        x = pad + col * (panel_w + pad)
        y = pad + row * (label_h + panel_h + pad)
        label = f"{source['shot_preset']} / {source['selected_renderer']} / frames={source['frame_count']}"
        draw.text((x + 6, y + 8), label, fill=(224, 234, 240))
        panel_x = x + (panel_w - panel.width) // 2
        sheet.paste(panel, (panel_x, y + label_h))

    comparison_sheet = os.path.join(review_dir, "comparison_sheet.png")
    comparison_manifest = os.path.join(review_dir, "comparison_manifest.json")
    sheet.save(comparison_sheet)
    manifest = {
        "schema": "lsfs_cinematic_review_comparison",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "comparison_sheet": rel_path(comparison_sheet, root),
        "sources": [
            {
                "manifest": rel_path(item["manifest"], root),
                "contact_sheet": rel_path(item["contact_sheet"], root),
                "shot_preset": item["shot_preset"],
                "render_preset": item["render_preset"],
                "selected_renderer": item["selected_renderer"],
                "frame_count": item["frame_count"],
            }
            for item in sources
        ],
    }
    write_json(comparison_manifest, manifest)
    return {
        "comparison_sheet": comparison_sheet,
        "comparison_manifest": comparison_manifest,
        "comparison_source_count": len(sources),
    }


def load_focus_review_source(path, root):
    manifest_path = os.path.abspath(path)
    if not os.path.isfile(manifest_path):
        fail(f"focus comparison review manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_cinematic_review_pack":
        fail(f"{manifest_path}: expected lsfs_cinematic_review_pack schema")
    focus_sheet = resolve_review_artifact(manifest_path, root, manifest.get("focus_sheet"))
    if not focus_sheet or not os.path.isfile(focus_sheet):
        return None
    focus_manifest = resolve_review_artifact(manifest_path, root, manifest.get("focus_review_manifest"))
    return {
        "manifest": manifest_path,
        "focus_sheet": focus_sheet,
        "focus_review_manifest": focus_manifest if focus_manifest and os.path.isfile(focus_manifest) else None,
        "shot_preset": manifest.get("shot_preset", "unknown"),
        "render_preset": manifest.get("render_preset", "unknown"),
        "selected_renderer": manifest.get("selected_renderer", "unknown"),
        "frame_count": manifest.get("frame_count", "n/a"),
    }


def create_focus_review_comparison(summary, root, current_review_manifest, compare_manifests):
    if not compare_manifests:
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the cinematic focus review comparison")

    sources = []
    for path in compare_manifests:
        source = load_focus_review_source(path, root)
        if source:
            sources.append(source)
    current = load_focus_review_source(current_review_manifest, root)
    if current:
        sources.append(current)
    if len(sources) < 2:
        return None

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    os.makedirs(review_dir, exist_ok=True)
    max_panel_w = 640
    label_h = 40
    pad = 14
    panels = []
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    for source in sources:
        with Image.open(source["focus_sheet"]) as img:
            panel = img.convert("RGB")
            if panel.width > max_panel_w:
                scale = max_panel_w / float(panel.width)
                panel = panel.resize((max_panel_w, max(1, int(round(panel.height * scale)))), resample_filter)
        panels.append((source, panel))

    columns = min(2, len(panels))
    rows = int(math.ceil(len(panels) / float(columns)))
    panel_w = max(panel.width for _source, panel in panels)
    panel_h = max(panel.height for _source, panel in panels)
    sheet_w = pad + columns * (panel_w + pad)
    sheet_h = pad + rows * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, (source, panel) in enumerate(panels):
        col = index % columns
        row = index // columns
        x = pad + col * (panel_w + pad)
        y = pad + row * (label_h + panel_h + pad)
        label = f"{source['shot_preset']} / focus / frames={source['frame_count']}"
        draw.text((x + 6, y + 8), label, fill=(224, 234, 240))
        panel_x = x + (panel_w - panel.width) // 2
        sheet.paste(panel, (panel_x, y + label_h))

    focus_comparison_sheet = os.path.join(review_dir, "focus_comparison_sheet.png")
    focus_comparison_manifest = os.path.join(review_dir, "focus_comparison_manifest.json")
    sheet.save(focus_comparison_sheet)
    manifest = {
        "schema": "lsfs_cinematic_focus_review_comparison",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "focus_comparison_sheet": rel_path(focus_comparison_sheet, root),
        "sources": [
            {
                "manifest": rel_path(item["manifest"], root),
                "focus_sheet": rel_path(item["focus_sheet"], root),
                "focus_review_manifest": rel_path(item["focus_review_manifest"], root),
                "shot_preset": item["shot_preset"],
                "render_preset": item["render_preset"],
                "selected_renderer": item["selected_renderer"],
                "frame_count": item["frame_count"],
            }
            for item in sources
        ],
    }
    write_json(focus_comparison_manifest, manifest)
    return {
        "focus_comparison_sheet": focus_comparison_sheet,
        "focus_comparison_manifest": focus_comparison_manifest,
        "focus_comparison_source_count": len(sources),
    }


def load_ripple_readability_source(path, root):
    manifest_path = os.path.abspath(path)
    if not os.path.isfile(manifest_path):
        fail(f"ripple diagnostic comparison review manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_cinematic_review_pack":
        fail(f"{manifest_path}: expected lsfs_cinematic_review_pack schema")
    sheet = resolve_review_artifact(manifest_path, root, manifest.get("ripple_readability_sheet"))
    if not sheet or not os.path.isfile(sheet):
        return None
    diag_manifest = resolve_review_artifact(manifest_path, root, manifest.get("ripple_readability_manifest"))
    return {
        "manifest": manifest_path,
        "ripple_readability_sheet": sheet,
        "ripple_readability_manifest": diag_manifest if diag_manifest and os.path.isfile(diag_manifest) else None,
        "shot_preset": manifest.get("shot_preset", "unknown"),
        "render_preset": manifest.get("render_preset", "unknown"),
        "selected_renderer": manifest.get("selected_renderer", "unknown"),
        "frame_count": manifest.get("frame_count", "n/a"),
    }


def create_ripple_readability_comparison(summary, root, current_review_manifest, compare_manifests):
    if not compare_manifests:
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the ripple diagnostic comparison")

    sources = []
    for path in compare_manifests:
        source = load_ripple_readability_source(path, root)
        if source:
            sources.append(source)
    current = load_ripple_readability_source(current_review_manifest, root)
    if current:
        sources.append(current)
    if len(sources) < 2:
        return None

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    os.makedirs(review_dir, exist_ok=True)
    max_panel_w = 640
    label_h = 40
    pad = 14
    panels = []
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    for source in sources:
        with Image.open(source["ripple_readability_sheet"]) as img:
            panel = img.convert("RGB")
            if panel.width > max_panel_w:
                scale = max_panel_w / float(panel.width)
                panel = panel.resize((max_panel_w, max(1, int(round(panel.height * scale)))), resample_filter)
        panels.append((source, panel))

    columns = min(2, len(panels))
    rows = int(math.ceil(len(panels) / float(columns)))
    panel_w = max(panel.width for _source, panel in panels)
    panel_h = max(panel.height for _source, panel in panels)
    sheet_w = pad + columns * (panel_w + pad)
    sheet_h = pad + rows * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, (source, panel) in enumerate(panels):
        col = index % columns
        row = index // columns
        x = pad + col * (panel_w + pad)
        y = pad + row * (label_h + panel_h + pad)
        label = f"{source['shot_preset']} / ripple diagnostic / frames={source['frame_count']}"
        draw.text((x + 6, y + 8), label, fill=(224, 234, 240))
        panel_x = x + (panel_w - panel.width) // 2
        sheet.paste(panel, (panel_x, y + label_h))

    comparison_sheet = os.path.join(review_dir, "ripple_readability_comparison_sheet.png")
    comparison_manifest = os.path.join(review_dir, "ripple_readability_comparison_manifest.json")
    sheet.save(comparison_sheet)
    manifest = {
        "schema": "lsfs_cinematic_ripple_readability_comparison",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "ripple_readability_comparison_sheet": rel_path(comparison_sheet, root),
        "sources": [
            {
                "manifest": rel_path(item["manifest"], root),
                "ripple_readability_sheet": rel_path(item["ripple_readability_sheet"], root),
                "ripple_readability_manifest": rel_path(item["ripple_readability_manifest"], root),
                "shot_preset": item["shot_preset"],
                "render_preset": item["render_preset"],
                "selected_renderer": item["selected_renderer"],
                "frame_count": item["frame_count"],
            }
            for item in sources
        ],
    }
    write_json(comparison_manifest, manifest)
    return {
        "ripple_readability_comparison_sheet": comparison_sheet,
        "ripple_readability_comparison_manifest": comparison_manifest,
        "ripple_readability_comparison_source_count": len(sources),
    }


def load_secondary_depth_source(path, root):
    manifest_path = os.path.abspath(path)
    if not os.path.isfile(manifest_path):
        fail(f"secondary depth comparison review manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_cinematic_review_pack":
        fail(f"{manifest_path}: expected lsfs_cinematic_review_pack schema")
    sheet = resolve_review_artifact(manifest_path, root, manifest.get("secondary_depth_sheet"))
    if not sheet or not os.path.isfile(sheet):
        return None
    depth_manifest = resolve_review_artifact(manifest_path, root, manifest.get("secondary_depth_manifest"))
    return {
        "manifest": manifest_path,
        "secondary_depth_sheet": sheet,
        "secondary_depth_manifest": depth_manifest if depth_manifest and os.path.isfile(depth_manifest) else None,
        "shot_name": os.path.basename(os.path.dirname(os.path.dirname(manifest_path))),
        "shot_preset": manifest.get("shot_preset", "unknown"),
        "render_preset": manifest.get("render_preset", "unknown"),
        "selected_renderer": manifest.get("selected_renderer", "unknown"),
        "frame_count": manifest.get("frame_count", "n/a"),
    }


def create_secondary_depth_comparison(summary, root, current_review_manifest, compare_manifests):
    if not compare_manifests:
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        fail("Pillow is required to create the secondary depth comparison")

    sources = []
    for path in compare_manifests:
        source = load_secondary_depth_source(path, root)
        if source:
            sources.append(source)
    current = load_secondary_depth_source(current_review_manifest, root)
    if current:
        sources.append(current)
    if len(sources) < 2:
        return None

    out_dir = summary["out_dir"]
    review_dir = os.path.join(out_dir, "review")
    os.makedirs(review_dir, exist_ok=True)
    max_panel_w = 760
    label_h = 40
    pad = 14
    panels = []
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    for source in sources:
        with Image.open(source["secondary_depth_sheet"]) as img:
            panel = img.convert("RGB")
            if panel.width > max_panel_w:
                scale = max_panel_w / float(panel.width)
                panel = panel.resize((max_panel_w, max(1, int(round(panel.height * scale)))), resample_filter)
        panels.append((source, panel))

    columns = min(2, len(panels))
    rows = int(math.ceil(len(panels) / float(columns)))
    panel_w = max(panel.width for _source, panel in panels)
    panel_h = max(panel.height for _source, panel in panels)
    sheet_w = pad + columns * (panel_w + pad)
    sheet_h = pad + rows * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for index, (source, panel) in enumerate(panels):
        col = index % columns
        row = index // columns
        x = pad + col * (panel_w + pad)
        y = pad + row * (label_h + panel_h + pad)
        label = f"{source['shot_name']} / secondary depth / frames={source['frame_count']}"
        draw.text((x + 6, y + 8), label, fill=(224, 234, 240))
        panel_x = x + (panel_w - panel.width) // 2
        sheet.paste(panel, (panel_x, y + label_h))

    comparison_sheet = os.path.join(review_dir, "secondary_depth_comparison_sheet.png")
    comparison_manifest = os.path.join(review_dir, "secondary_depth_comparison_manifest.json")
    sheet.save(comparison_sheet)
    manifest = {
        "schema": "lsfs_cinematic_secondary_depth_comparison",
        "version": 1,
        "generated_utc": utc_now(),
        "shot_preset": summary.get("shot_preset"),
        "secondary_depth_comparison_sheet": rel_path(comparison_sheet, root),
        "sources": [
            {
                "manifest": rel_path(item["manifest"], root),
                "secondary_depth_sheet": rel_path(item["secondary_depth_sheet"], root),
                "secondary_depth_manifest": rel_path(item["secondary_depth_manifest"], root),
                "shot_name": item["shot_name"],
                "shot_preset": item["shot_preset"],
                "render_preset": item["render_preset"],
                "selected_renderer": item["selected_renderer"],
                "frame_count": item["frame_count"],
            }
            for item in sources
        ],
    }
    write_json(comparison_manifest, manifest)
    return {
        "secondary_depth_comparison_sheet": comparison_sheet,
        "secondary_depth_comparison_manifest": comparison_manifest,
        "secondary_depth_comparison_source_count": len(sources),
    }


def evaluate_camera_stability(config, camera_path):
    gate = config.get("camera_stability")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_position_y": (camera_path.get("min_position_y"), gate.get("min_position_y"), ">="),
        "min_target_distance": (camera_path.get("min_target_distance"), gate.get("min_target_distance"), ">="),
        "max_vertical_fov_degrees": (camera_path.get("max_vertical_fov_degrees"), gate.get("max_vertical_fov_degrees"), "<="),
    }
    passed = True
    for name, (value, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def nested_metric(metrics, path):
    value = metrics
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def evaluate_visual_qa(config, visual_qa):
    gate = config.get("visual_qa")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_nonblank_ratio": (("nonblank_ratio", "min"), gate.get("min_nonblank_ratio"), ">="),
        "min_contrast": (("contrast", "min"), gate.get("min_contrast"), ">="),
        "min_mean_luminance": (("mean_luminance", "mean"), gate.get("min_mean_luminance"), ">="),
        "max_mean_luminance": (("mean_luminance", "mean"), gate.get("max_mean_luminance"), "<="),
        "min_mean_bright_ratio": (("bright_ratio", "mean"), gate.get("min_mean_bright_ratio"), ">="),
    }
    passed = True
    for name, (path, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = nested_metric(visual_qa, path)
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def evaluate_temporal_highlight_qa(config, temporal):
    gate = config.get("temporal_highlight_qa")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_pair_count": (("pair_count",), gate.get("min_pair_count"), ">="),
        "min_mean_delta": (("mean_delta", "mean"), gate.get("min_mean_delta"), ">="),
        "max_mean_delta": (("mean_delta", "max"), gate.get("max_mean_delta"), "<="),
        "max_peak_delta": (("peak_delta", "max"), gate.get("max_peak_delta"), "<="),
        "max_highlight_change_ratio": (("highlight_change_ratio", "max"), gate.get("max_highlight_change_ratio"), "<="),
    }
    passed = True
    for name, (path, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = nested_metric(temporal, path)
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def evaluate_secondary_framing_qa(config, framing):
    gate = config.get("secondary_framing_qa")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_mean_inside_ratio": (("mean_inside_ratio",), gate.get("min_mean_inside_ratio"), ">="),
        "min_frame_inside_ratio": (("min_inside_ratio",), gate.get("min_frame_inside_ratio"), ">="),
        "min_mean_screen_y": (("mean_screen_y",), gate.get("min_mean_screen_y"), ">="),
        "max_mean_screen_y": (("mean_screen_y",), gate.get("max_mean_screen_y"), "<="),
    }
    passed = True
    for name, (path, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = nested_metric(framing, path)
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def evaluate_focus_review_qa(config, focus_review):
    gate = config.get("focus_review")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_frame_count": (("frame_count",), gate.get("min_frame_count"), ">="),
        "min_nonblank_ratio": (("summary", "nonblank_ratio", "min"), gate.get("min_nonblank_ratio"), ">="),
        "min_contrast": (("summary", "contrast", "min"), gate.get("min_contrast"), ">="),
        "min_mean_luminance": (("summary", "mean_luminance", "mean"), gate.get("min_mean_luminance"), ">="),
        "max_mean_luminance": (("summary", "mean_luminance", "mean"), gate.get("max_mean_luminance"), "<="),
        "min_mean_bright_ratio": (("summary", "bright_ratio", "mean"), gate.get("min_mean_bright_ratio"), ">="),
    }
    passed = True
    for name, (path, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = nested_metric(focus_review, path)
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def evaluate_secondary_depth_review_qa(config, depth_review):
    gate = config.get("secondary_depth_review")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_frame_count": (("frame_count",), gate.get("min_frame_count"), ">="),
        "min_active_frame_count": (("active_frame_count",), gate.get("min_active_frame_count"), ">="),
        "min_mean_crop_particles": (("summary", "crop_particles", "mean"), gate.get("min_mean_crop_particles"), ">="),
        "min_mean_crop_ratio": (("summary", "crop_ratio", "mean"), gate.get("min_mean_crop_ratio"), ">="),
        "min_mean_depth_span": (("summary", "depth_span", "mean"), gate.get("min_mean_depth_span"), ">="),
        "min_mean_normalized_depth_span": (
            ("summary", "normalized_depth_span", "mean"),
            gate.get("min_mean_normalized_depth_span"),
            ">=",
        ),
    }
    passed = True
    for name, (path, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = nested_metric(depth_review, path)
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def evaluate_ripple_readability_qa(config, readability):
    gate = config.get("ripple_readability_review")
    if not isinstance(gate, dict) or not gate.get("enabled", False):
        return {"enabled": False}
    checks = []
    thresholds = {
        "min_frame_count": (("frame_count",), gate.get("min_frame_count"), ">="),
        "min_edge_mean": (("summary", "edge_mean", "mean"), gate.get("min_edge_mean"), ">="),
        "min_edge_nonzero_ratio": (
            ("summary", "edge_nonzero_ratio", "mean"),
            gate.get("min_edge_nonzero_ratio"),
            ">=",
        ),
        "max_highlight_ratio": (("summary", "highlight_ratio", "max"), gate.get("max_highlight_ratio"), "<="),
    }
    passed = True
    for name, (path, threshold, op) in thresholds.items():
        if threshold is None:
            continue
        value = nested_metric(readability, path)
        value = float(value or 0.0)
        threshold = float(threshold)
        ok = value >= threshold if op == ">=" else value <= threshold
        passed = passed and ok
        checks.append({
            "metric": name,
            "value": value,
            "threshold": threshold,
            "operator": op,
            "passed": ok,
        })
    return {
        "enabled": True,
        "passed": passed,
        "checks": checks,
    }


def render_report(summary, root):
    config = summary.get("config", {})
    metrics = summary.get("metrics", {})
    artifacts = summary.get("artifacts", {})
    lines = [
        "# Cinematic Shot Report",
        "",
        "## Summary",
        "",
        f"- Status: `{summary.get('status', 'unknown')}`",
        f"- Shot preset: `{summary.get('shot_preset', config.get('preset', 'unknown'))}`",
        f"- Render preset: `{summary.get('render_preset', config.get('render_preset', 'unknown'))}`",
        f"- Selected renderer: `{summary.get('selected_renderer', 'unknown')}`",
        f"- Simulation scene: `{config.get('scene', 'bubble')}`",
        f"- Secondary demo particles: `{config.get('secondary_demo_particles', 0)}`",
        f"- Secondary physical particles: `{config.get('secondary_physical_particles', 0)}`",
        f"- Secondary radius scale: `{config.get('secondary_radius_scale', 1.0)}`",
        f"- Frames: `{config.get('frames', 'n/a')}`",
        f"- Resolution: `{config.get('width', 'n/a')} x {config.get('height', 'n/a')}`",
        f"- Simulation grid: `{config.get('nx', 'n/a')} x {config.get('ny', 'n/a')} x {config.get('nz', 'n/a')}`",
        f"- Simulation steps: `{config.get('sim_steps', 'n/a')}`",
        "",
        "## Artifacts",
        "",
    ]
    for key in ("manifest", "export_stamp", "validation_stamp", "sequence", "water_reconstruction", "render_summary",
                "render_frame_dir", "gif", "contact_sheet", "review_manifest",
                "comparison_sheet", "comparison_manifest", "temporal_diff_sheet",
                "temporal_diff_manifest", "focus_sheet", "focus_review_manifest",
                "focus_comparison_sheet", "focus_comparison_manifest",
                "secondary_depth_sheet", "secondary_depth_manifest",
                "secondary_depth_comparison_sheet", "secondary_depth_comparison_manifest",
                "ripple_readability_sheet", "ripple_readability_manifest",
                "ripple_readability_comparison_sheet", "ripple_readability_comparison_manifest",
                "review_dir"):
            if key in artifacts:
                lines.append(f"- {key}: `{report_path(artifacts.get(key), root)}`")
    lines.extend([
        "",
        "## Metrics",
        "",
        f"- Cache frames: `{metrics.get('cache_frame_count', 'n/a')}`",
        f"- Export cache reused: `{metrics.get('export_cache_reused', 'n/a')}`",
        f"- Render cache validation reused: `{metrics.get('validation_reused', 'n/a')}`",
        f"- Converted frames: `{metrics.get('converted_frame_count', 'n/a')}`",
        f"- Converted sequence reused: `{metrics.get('converted_sequence_reused', 'n/a')}`",
        f"- Water mesh frames: `{metrics.get('water_mesh_frame_count', 'n/a')}`",
        f"- Water reconstruction reused: `{metrics.get('water_reconstruction_reused', 'n/a')}`",
        f"- Surface mode: `{metrics.get('surface_mode', 'n/a')}`",
        f"- Implicit blur iterations: `{metrics.get('implicit_blur_iterations', 'n/a')}`",
        f"- GIF bytes: `{metrics.get('shot_gif_bytes', 'n/a')}`",
        f"- Camera motion: `{metrics.get('camera_motion', {}).get('enabled', False)}`",
        f"- Camera auto framing: `{metrics.get('camera_framing', {}).get('enabled', False)}`",
        f"- Camera frame scale: `{metrics.get('camera_framing', {}).get('max_scale', 1.0)}`",
        f"- Camera path metrics: `{metrics.get('camera_path', {})}`",
        f"- Camera stability: `{metrics.get('camera_stability', {})}`",
        f"- Visual QA summary: `{metrics.get('visual_qa', {})}`",
        f"- Visual QA gate: `{metrics.get('visual_qa_gate', {})}`",
        f"- Temporal highlight summary: `{metrics.get('temporal_highlight', {})}`",
        f"- Temporal highlight gate: `{metrics.get('temporal_highlight_gate', {})}`",
        f"- Water depth strength: `{metrics.get('water_material', {}).get('depth_strength', 0.0)}`",
        f"- Water rim strength: `{metrics.get('water_material', {}).get('rim_strength', 0.0)}`",
        f"- Water surface detail: `{metrics.get('water_surface_detail', {})}`",
        f"- Water surface glint pass: `{metrics.get('water_surface_glint_pass', {})}`",
        f"- Water reflection pass: `{metrics.get('water_reflection_pass', {})}`",
        f"- Water volume scattering pass: `{metrics.get('water_volume_scattering_pass', {})}`",
        f"- Water impact ripple pass: `{metrics.get('water_impact_ripple_pass', {})}`",
        f"- Water impact ripple counts: `{metrics.get('water_impact_ripple_counts', {})}`",
        f"- Secondary channel radius scales: `{metrics.get('secondary_channel_radius_scales', {})}`",
        f"- Secondary soft pass: `{metrics.get('secondary_soft_pass', {})}`",
        f"- Secondary streak pass: `{metrics.get('secondary_streak_pass', {})}`",
        f"- Secondary streak counts: `{metrics.get('secondary_streak_counts', {})}`",
        f"- Surface contact foam pass: `{metrics.get('surface_contact_foam_pass', {})}`",
        f"- Surface contact foam counts: `{metrics.get('surface_contact_foam_counts', {})}`",
        f"- Secondary framing summary: `{metrics.get('secondary_framing', {})}`",
        f"- Secondary framing gate: `{metrics.get('secondary_framing_gate', {})}`",
        f"- Focus review summary: `{metrics.get('focus_review', {})}`",
        f"- Focus review gate: `{metrics.get('focus_review_gate', {})}`",
        f"- Secondary depth review summary: `{metrics.get('secondary_depth_review', {})}`",
        f"- Secondary depth review gate: `{metrics.get('secondary_depth_review_gate', {})}`",
        f"- Ripple readability summary: `{metrics.get('ripple_readability', {})}`",
        f"- Ripple readability gate: `{metrics.get('ripple_readability_gate', {})}`",
        f"- Secondary channels first: `{format_secondary_channels(metrics.get('secondary_channels', {}).get('first'))}`",
        f"- Secondary channels last: `{format_secondary_channels(metrics.get('secondary_channels', {}).get('last'))}`",
        f"- Secondary volume first: `{format_secondary_volumes(metrics.get('secondary_volumes', {}).get('first'))}`",
        f"- Secondary volume last: `{format_secondary_volumes(metrics.get('secondary_volumes', {}).get('last'))}`",
        f"- Secondary acceptance QA: `{config.get('secondary_acceptance_qa', {})}`",
        f"- Secondary acceptance min: `{metrics.get('secondary_acceptance_min', 'n/a')}`",
        f"- Secondary foam acceptance min: `{metrics.get('secondary_foam_acceptance_min', 'n/a')}`",
        f"- Secondary interface gate: `{format_secondary_interface_gate(summary.get('export_metrics', {}))}`",
        f"- Review keyframes: `{metrics.get('review_frame_count', 'n/a')}`",
        f"- Review comparison sources: `{metrics.get('comparison_source_count', 'n/a')}`",
        f"- Focus comparison sources: `{metrics.get('focus_comparison_source_count', 'n/a')}`",
        f"- Secondary depth comparison sources: `{metrics.get('secondary_depth_comparison_source_count', 'n/a')}`",
        f"- Ripple readability comparison sources: `{metrics.get('ripple_readability_comparison_source_count', 'n/a')}`",
        f"- Temporal diff review pairs: `{metrics.get('temporal_diff_pair_count', 'n/a')}`",
        "",
        "## Stage Timings",
        "",
        "| Stage | Exit | Elapsed |",
        "| --- | ---: | ---: |",
    ])
    for item in summary.get("commands", []):
        lines.append(
            f"| `{item.get('label', 'unknown')}` | `{item.get('returncode', 'n/a')}` | {format_ms(item.get('elapsed_ms'))} |")
    scene = config.get("scene", "bubble")
    scene_note = "- The current exporter scene is bubble-tank style; use `--scene falling-water` or `dam_break_cinematic` for a more dynamic falling/collapsing water body."
    if scene in ("dam-break", "dambreak", "falling-water", "falling"):
        scene_note = "- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface."
    elif scene in ("large-water-event", "water-event", "wide-falling-water"):
        scene_note = "- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells."
    surface_mode = metrics.get("surface_mode", "voxel")
    surface_note = "- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky."
    if surface_mode == "tetra":
        surface_note = "- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution."
    secondary_note = "- This gate has no visible secondary particle model enabled."
    if config.get("secondary_physical_particles", 0) > 0:
        secondary_note = "- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver."
    elif config.get("secondary_demo_particles", 0) > 0:
        secondary_note = "- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model."
    lines.extend([
        "",
        "## Known Limitations",
        "",
        surface_note,
        scene_note,
        secondary_note,
        "- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.",
        "",
        "## Next Recommended Milestone",
        "",
        "S114 should add a conservative render-frame freshness check that can skip preview/Blender rendering when the sequence, renderer options, and existing frame outputs are unchanged.",
        "",
    ])
    return "\n".join(lines)


class Pipeline:
    def __init__(self, out_dir, cwd):
        self.out_dir = os.path.abspath(out_dir)
        self.cwd = cwd
        self.logs_dir = os.path.join(self.out_dir, "logs")
        self.commands = []
        os.makedirs(self.logs_dir, exist_ok=True)

    def record(self, label, command, stdout="", stderr="", returncode=0, elapsed_ms=0.0):
        index = len(self.commands) + 1
        safe_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label)
        stdout_path = os.path.join(self.logs_dir, f"{index:02d}_{safe_label}.stdout.log")
        stderr_path = os.path.join(self.logs_dir, f"{index:02d}_{safe_label}.stderr.log")
        with open(stdout_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(stdout)
        with open(stderr_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(stderr)
        item = {
            "label": label,
            "command": command_for_summary(command),
            "returncode": returncode,
            "elapsed_ms": elapsed_ms,
            "stdout_log": stdout_path,
            "stderr_log": stderr_path,
            "reused": True,
        }
        self.commands.append(item)
        return subprocess.CompletedProcess(command, returncode, stdout, stderr), item

    def run(self, label, command, allow_failure=False):
        index = len(self.commands) + 1
        safe_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label)
        stdout_path = os.path.join(self.logs_dir, f"{index:02d}_{safe_label}.stdout.log")
        stderr_path = os.path.join(self.logs_dir, f"{index:02d}_{safe_label}.stderr.log")
        started = time.perf_counter()
        result = subprocess.run(command,
                                cwd=self.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=False)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        with open(stdout_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(result.stdout)
        with open(stderr_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(result.stderr)
        item = {
            "label": label,
            "command": command_for_summary(command),
            "returncode": result.returncode,
            "elapsed_ms": elapsed_ms,
            "stdout_log": stdout_path,
            "stderr_log": stderr_path,
        }
        self.commands.append(item)
        if result.returncode != 0 and not allow_failure:
            tail = result.stderr.strip() or result.stdout.strip()
            if len(tail) > 500:
                tail = tail[-500:]
            fail(f"{label} failed with exit code {result.returncode}: {tail}")
        return result, item


def parse_positive_int(value, label):
    try:
        out = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"{label} must be an integer")
    if out <= 0:
        raise argparse.ArgumentTypeError(f"{label} must be positive")
    return out


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run an LSFS cinematic shot pipeline")
    parser.add_argument("--preset", default="bubble_cinematic",
                        help="shot preset name from --preset-config")
    parser.add_argument("--preset-config", default=default_preset_config_path(),
                        help="cinematic preset config JSON")
    parser.add_argument("--render-preset",
                        help="render look preset name; defaults to --preset")
    parser.add_argument("--out", required=True, help="output shot directory")
    parser.add_argument("--frames", type=lambda v: parse_positive_int(v, "frames"))
    parser.add_argument("--width", type=lambda v: parse_positive_int(v, "width"))
    parser.add_argument("--height", type=lambda v: parse_positive_int(v, "height"))
    parser.add_argument("--renderer", choices=("auto", "preview", "blender"))
    parser.add_argument("--kind", choices=("sparse", "mr"), help="override preset simulation kind")
    parser.add_argument("--scene",
                        choices=("bubble", "dam-break", "dambreak",
                                 "falling-water", "falling",
                                 "large-water-event", "water-event", "wide-falling-water"),
                        help="override preset simulation scene")
    parser.add_argument("--nx", type=lambda v: parse_positive_int(v, "nx"))
    parser.add_argument("--ny", type=lambda v: parse_positive_int(v, "ny"))
    parser.add_argument("--nz", type=lambda v: parse_positive_int(v, "nz"))
    parser.add_argument("--sim-steps", type=lambda v: parse_positive_int(v, "sim-steps"),
                        help="simulation steps to export; defaults to --frames")
    parser.add_argument("--cache-every", type=lambda v: parse_positive_int(v, "cache-every"))
    parser.add_argument("--dt", type=float, help="simulation dt override")
    parser.add_argument("--cg-iters", type=int, help="pressure CG iteration override")
    parser.add_argument("--physics-preset", action="store_true", help="enable full physics preset in exporter")
    parser.add_argument("--secondary-demo-particles", type=int,
                        help="opt-in render-demo secondary particles per exported frame")
    parser.add_argument("--secondary-physical-particles", type=int,
                        help="opt-in physically conditioned secondary spray particles per exported frame")
    parser.add_argument("--build-dir", default="build", help="CMake build directory")
    parser.add_argument("--config", default="Release", help="CMake build config")
    parser.add_argument("--no-build", action="store_true", help="do not build exporter if missing")
    parser.add_argument("--rebuild", action="store_true", help="build exporter target before running")
    parser.add_argument("--threshold", type=float, default=0.02, help="water reconstruction threshold")
    parser.add_argument("--smooth-iterations", type=int,
                        help="water mesh smoothing iterations")
    parser.add_argument("--smooth-alpha", type=float,
                        help="water mesh smoothing blend factor")
    parser.add_argument("--write-normals", action="store_true",
                        help="force OBJ normal output for reconstructed water meshes")
    parser.add_argument("--surface-mode", choices=("voxel", "tetra"),
                        help="water surface extraction mode")
    parser.add_argument("--implicit-iso", type=float,
                        help="implicit tetra isosurface threshold")
    parser.add_argument("--implicit-blur-iterations", type=int,
                        help="scalar-grid blur iterations for implicit tetra reconstruction")
    parser.add_argument("--fps", type=float, help="output GIF frame rate")
    parser.add_argument("--samples", type=int, help="Blender render samples")
    parser.add_argument("--blender", help="explicit Blender executable path")
    parser.add_argument("--max-secondary-particles", type=int)
    parser.add_argument("--secondary-radius-scale", type=float,
                        help="scale factor for Blender secondary particle radii")
    parser.add_argument("--min-occupancy", type=float,
                        help="preview renderer minimum occupancy")
    parser.add_argument("--min-nonblank-ratio", type=float,
                        help="Blender frame nonblank gate")
    parser.add_argument("--timeout-seconds", type=int, default=300,
                        help="Blender subprocess timeout")
    parser.add_argument("--report", help="optional markdown report path")
    parser.add_argument("--review-frames", type=int, default=6,
                        help="number of evenly sampled keyframes in the review contact sheet")
    parser.add_argument("--no-review-pack", action="store_true",
                        help="skip contact sheet and review manifest generation")
    parser.add_argument("--compare-review-manifest", action="append", default=[],
                        help="previous review_manifest.json to include in a wide/close comparison sheet")
    parser.add_argument("--reuse-export-cache", action="store_true",
                        help="reuse an existing exported cache when the export command and cache files are unchanged")
    parser.add_argument("--reuse-converted", action="store_true",
                        help="let convert_render_cache.py reuse sequence.json when inputs are unchanged")
    parser.add_argument("--reuse-validation", action="store_true",
                        help="reuse a validation stamp when manifest and cache frame contents are unchanged")
    parser.add_argument("--reuse-water-mesh", action="store_true",
                        help="let reconstruct_water.py reuse water meshes when inputs and options are unchanged")
    args = parser.parse_args(argv)
    if args.dt is not None and (args.dt <= 0.0 or not math.isfinite(args.dt)):
        parser.error("dt must be finite and positive")
    if args.cg_iters is not None and args.cg_iters < 0:
        parser.error("cg-iters must be non-negative")
    if args.threshold < 0.0 or not math.isfinite(args.threshold):
        parser.error("threshold must be finite and non-negative")
    if args.smooth_iterations is not None and args.smooth_iterations < 0:
        parser.error("smooth-iterations must be non-negative")
    if args.smooth_alpha is not None and (
            args.smooth_alpha < 0.0 or args.smooth_alpha > 1.0 or not math.isfinite(args.smooth_alpha)):
        parser.error("smooth-alpha must be finite in [0, 1]")
    if args.implicit_iso is not None and (
            args.implicit_iso <= 0.0 or args.implicit_iso >= 1.0 or not math.isfinite(args.implicit_iso)):
        parser.error("implicit-iso must be finite in (0, 1)")
    if args.implicit_blur_iterations is not None and args.implicit_blur_iterations < 0:
        parser.error("implicit-blur-iterations must be non-negative")
    if args.fps is not None and (args.fps <= 0.0 or not math.isfinite(args.fps)):
        parser.error("fps must be finite and positive")
    if args.samples is not None and args.samples <= 0:
        parser.error("samples must be positive")
    if args.secondary_demo_particles is not None and args.secondary_demo_particles < 0:
        parser.error("secondary-demo-particles must be non-negative")
    if args.secondary_physical_particles is not None and args.secondary_physical_particles < 0:
        parser.error("secondary-physical-particles must be non-negative")
    if args.max_secondary_particles is not None and args.max_secondary_particles < 0:
        parser.error("max-secondary-particles must be non-negative")
    if args.secondary_radius_scale is not None and (
            args.secondary_radius_scale <= 0.0 or not math.isfinite(args.secondary_radius_scale)):
        parser.error("secondary-radius-scale must be finite and positive")
    if args.min_occupancy is not None and (args.min_occupancy < 0.0 or not math.isfinite(args.min_occupancy)):
        parser.error("min-occupancy must be finite and non-negative")
    if args.min_nonblank_ratio is not None and (
            args.min_nonblank_ratio < 0.0 or not math.isfinite(args.min_nonblank_ratio)):
        parser.error("min-nonblank-ratio must be finite and non-negative")
    if args.timeout_seconds <= 0:
        parser.error("timeout-seconds must be positive")
    if args.review_frames <= 0:
        parser.error("review-frames must be positive")
    return args


def resolve_config_path(path):
    if os.path.isabs(path):
        return path
    cwd_candidate = os.path.abspath(path)
    if os.path.isfile(cwd_candidate):
        return cwd_candidate
    return os.path.join(repo_root(), path)


def load_preset_config(path):
    resolved = resolve_config_path(path)
    if os.path.isfile(resolved):
        data = read_json(resolved)
        if data.get("schema") != "lsfs_cinematic_presets":
            fail(f"{resolved}: expected lsfs_cinematic_presets schema")
        presets = data.get("presets")
        if not isinstance(presets, dict) or not presets:
            fail(f"{resolved}: presets must be a non-empty object")
        return resolved, presets
    if os.path.normcase(os.path.abspath(resolved)) == os.path.normcase(os.path.abspath(default_preset_config_path())):
        return None, BUILTIN_PRESETS
    fail(f"{resolved}: preset config not found")


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


def preset_object(presets, name, label, stack=None):
    stack = stack or []
    if name in stack:
        chain = " -> ".join(stack + [name])
        fail(f"{label} preset extends cycle: {chain}")
    value = presets.get(name)
    if not isinstance(value, dict):
        known = ", ".join(sorted(presets))
        fail(f"unknown {label} preset {name!r}; known presets: {known}")
    parent_name = value.get("extends")
    if parent_name is None:
        return {key: item for key, item in value.items() if key != "extends"}
    if not isinstance(parent_name, str) or not parent_name:
        fail(f"{label} preset {name!r} has invalid extends value")
    return deep_merge(preset_object(presets, parent_name, label, stack + [name]), value)


def section(preset, name):
    value = preset.get(name, {})
    return value if isinstance(value, dict) else {}


def first_value(*values):
    for value in values:
        if value is not None:
            return value
    return None


def effective_config(args, shot_preset, render_preset_name, render_preset, preset_config_path):
    sim = section(shot_preset, "simulation")
    shot = section(shot_preset, "shot")
    renderer = section(render_preset, "renderer")
    reconstruction = section(render_preset, "reconstruction")
    frames = first_value(args.frames, shot.get("frames"), 24)
    width = first_value(args.width, shot.get("width"), 1280)
    height = first_value(args.height, shot.get("height"), 720)
    return {
        "preset": args.preset,
        "render_preset": render_preset_name,
        "preset_config": preset_config_path,
        "description": shot_preset.get("description", ""),
        "kind": args.kind or sim.get("kind", "sparse"),
        "scene": args.scene or sim.get("scene", "bubble"),
        "nx": first_value(args.nx, sim.get("nx"), 12),
        "ny": first_value(args.ny, sim.get("ny"), 18),
        "nz": first_value(args.nz, sim.get("nz"), 12),
        "dt": first_value(args.dt, sim.get("dt"), 0.02),
        "cg_iters": first_value(args.cg_iters, sim.get("cg_iters")),
        "physics_preset": bool(args.physics_preset or sim.get("physics_preset", False)),
        "secondary_demo_particles": first_value(args.secondary_demo_particles,
                                                sim.get("secondary_demo_particles"),
                                                0),
        "secondary_physical_particles": first_value(args.secondary_physical_particles,
                                                    sim.get("secondary_physical_particles"),
                                                    0),
        "sim_steps": first_value(args.sim_steps, shot.get("sim_steps"), frames),
        "cache_every": first_value(args.cache_every, shot.get("cache_every"), 1),
        "frames": frames,
        "width": width,
        "height": height,
        "renderer": args.renderer or renderer.get("preferred", "auto"),
        "samples": first_value(args.samples, renderer.get("samples"), 24),
        "max_secondary_particles": first_value(args.max_secondary_particles,
                                               renderer.get("max_secondary_particles"),
                                               512),
        "secondary_radius_scale": first_value(args.secondary_radius_scale,
                                             renderer.get("secondary_radius_scale"),
                                             1.0),
        "min_occupancy": first_value(args.min_occupancy, renderer.get("min_occupancy"), 0.01),
        "min_nonblank_ratio": first_value(args.min_nonblank_ratio,
                                          renderer.get("min_nonblank_ratio"),
                                          0.05),
        "visual_qa": section(renderer, "visual_qa"),
        "temporal_highlight_qa": section(renderer, "temporal_highlight_qa"),
        "temporal_diff_review": section(renderer, "temporal_diff_review"),
        "secondary_framing_qa": section(renderer, "secondary_framing_qa"),
        "secondary_acceptance_qa": section(renderer, "secondary_acceptance_qa"),
        "focus_review": section(renderer, "focus_review"),
        "secondary_depth_review": section(renderer, "secondary_depth_review"),
        "ripple_readability_review": section(renderer, "ripple_readability_review"),
        "fps": first_value(args.fps, shot.get("fps"), 12.0),
        "smooth_iterations": first_value(args.smooth_iterations,
                                         reconstruction.get("smooth_iterations"),
                                         0),
        "smooth_alpha": first_value(args.smooth_alpha,
                                    reconstruction.get("smooth_alpha"),
                                    0.18),
        "write_normals": bool(args.write_normals or reconstruction.get("write_normals", False)),
        "surface_mode": first_value(args.surface_mode,
                                    reconstruction.get("surface_mode"),
                                    "voxel"),
        "implicit_iso": first_value(args.implicit_iso,
                                    reconstruction.get("implicit_iso"),
                                    0.45),
        "implicit_blur_iterations": first_value(args.implicit_blur_iterations,
                                                reconstruction.get("implicit_blur_iterations"),
                                                0),
        "review_pack": not args.no_review_pack,
        "review_frames": args.review_frames,
        "compare_review_manifests": list(args.compare_review_manifest or []),
        "camera_stability": section(section(render_preset, "camera"), "stability"),
    }


def ensure_exporter(pipeline, root, build_dir, config, no_build, rebuild):
    build_dir_abs = os.path.abspath(build_dir)
    exporter = find_exporter(build_dir_abs, config)
    if rebuild or (exporter is None and not no_build):
        pipeline.run("build_exporter", [
            "cmake", "--build", build_dir_abs, "--config", config, "--target", "export_render_cache3d"
        ])
        exporter = find_exporter(build_dir_abs, config)
    if exporter is None:
        candidates = ", ".join(exporter_candidates(build_dir_abs, config))
        fail(f"export_render_cache3d executable not found; checked {candidates}")
    return exporter


def parse_blender_check(stdout):
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {"available": False, "error": "invalid check JSON"}
    return payload if isinstance(payload, dict) else {"available": False, "error": "invalid check payload"}


def choose_renderer(renderer_choice, args, pipeline, root):
    if renderer_choice != "auto":
        return renderer_choice, None
    command = [sys.executable, tool_path(root, "render_bridge_blender.py"), "--check"]
    if args.blender:
        command.extend(["--blender", args.blender])
    result, _ = pipeline.run("check_blender", command, allow_failure=True)
    report = parse_blender_check(result.stdout)
    return ("blender" if report.get("available") else "preview"), report


def require_file(path, label):
    if not os.path.isfile(path):
        fail(f"{label} was not created: {path}")
    return path


def require_dir(path, label):
    if not os.path.isdir(path):
        fail(f"{label} was not created: {path}")
    return path


def run_pipeline(args):
    root = repo_root()
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    pipeline = Pipeline(out_dir, root)
    started = utc_now()
    preset_config_path, presets = load_preset_config(args.preset_config)
    shot_preset = preset_object(presets, args.preset, "shot")
    render_preset_name = args.render_preset or args.preset
    render_preset = preset_object(presets, render_preset_name, "render")
    config = effective_config(args, shot_preset, render_preset_name, render_preset, preset_config_path)
    cache_dir = os.path.join(out_dir, "cache")
    converted_dir = os.path.join(out_dir, "converted")
    water_dir = os.path.join(out_dir, "water_mesh")
    preview_dir = os.path.join(out_dir, "preview")
    blender_dir = os.path.join(out_dir, "blender")
    os.makedirs(cache_dir, exist_ok=True)

    manifest_path = os.path.join(cache_dir, "manifest.json")
    cache_prefix = os.path.join(cache_dir, "render_cache")
    export_stamp = os.path.join(cache_dir, "export_stamp.json")
    validation_stamp = os.path.join(cache_dir, "validation_stamp.json")
    water_index = os.path.join(water_dir, "water_reconstruction.json")
    sequence_path = os.path.join(converted_dir, "sequence.json")
    gif_path = os.path.join(out_dir, "shot.gif")
    summary_path = os.path.join(out_dir, "shot_summary.json")
    summary = {
        "runner": "lsfs_cinematic_shot_pipeline",
        "version": 1,
        "status": "running",
        "started_utc": started,
        "finished_utc": None,
        "out_dir": out_dir,
        "config": config,
        "requested_renderer": args.renderer,
        "selected_renderer": None,
        "preset_config": preset_config_path,
        "shot_preset": args.preset,
        "render_preset": render_preset_name,
        "artifacts": {
            "manifest": manifest_path,
            "export_stamp": export_stamp,
            "validation_stamp": validation_stamp,
            "sequence": sequence_path,
            "water_reconstruction": water_index,
            "gif": gif_path,
        },
        "commands": pipeline.commands,
    }

    def finish(status, error=None):
        summary["status"] = status
        summary["finished_utc"] = utc_now()
        summary["commands"] = pipeline.commands
        if error:
            summary["error"] = str(error)
        write_json(summary_path, summary)

    try:
        exporter = ensure_exporter(pipeline,
                                   root,
                                   args.build_dir,
                                   args.config,
                                   args.no_build,
                                   args.rebuild)
        summary["exporter"] = exporter
        export_cmd = [
            exporter,
            "--kind", config["kind"],
            "--scene", config["scene"],
            "--nx", str(config["nx"]),
            "--ny", str(config["ny"]),
            "--nz", str(config["nz"]),
            "--steps", str(config["sim_steps"]),
            "--every", str(config["cache_every"]),
            "--dt", str(config["dt"]),
            "--out-prefix", cache_prefix,
            "--manifest", manifest_path,
        ]
        if config["cg_iters"] is not None:
            export_cmd.extend(["--cg-iters", str(config["cg_iters"])])
        if config["physics_preset"]:
            export_cmd.append("--physics-preset")
        if config["secondary_demo_particles"] > 0:
            export_cmd.extend(["--secondary-demo-particles", str(config["secondary_demo_particles"])])
        if config["secondary_physical_particles"] > 0:
            export_cmd.extend(["--secondary-physical-particles", str(config["secondary_physical_particles"])])
        export_fingerprint = export_cache_fingerprint(exporter, export_cmd)
        export_stamp_payload = (
            load_reusable_export_cache(export_stamp, export_fingerprint, manifest_path)
            if args.reuse_export_cache else None
        )
        if export_stamp_payload:
            export_metrics = dict(export_stamp_payload.get("export_metrics", {}))
            export_metrics["reused"] = True
            export_result, _export_item = pipeline.record(
                "export_render_cache",
                export_cmd,
                stdout=key_value_stdout(export_metrics, "reused"))
            _ = export_result
            summary["export_metrics"] = export_metrics
        else:
            export_result, _export_item = pipeline.run("export_render_cache", export_cmd)
            export_metrics = parse_key_value_stdout(export_result.stdout)
            export_metrics.pop("status", None)
            export_metrics["reused"] = False
            summary["export_metrics"] = export_metrics
            write_export_cache_stamp(export_stamp, export_fingerprint, manifest_path, export_metrics)
        require_file(manifest_path, "render cache manifest")

        validate_cmd = [
            sys.executable,
            tool_path(root, "validate_render_cache.py"),
            manifest_path,
            "--require-cinematic",
            "--stamp", validation_stamp,
        ]
        if args.reuse_validation:
            validate_cmd.append("--reuse-if-fresh")
        validate_result, _validate_item = pipeline.run("validate_render_cache", validate_cmd)
        summary["validation_metrics"] = parse_key_value_stdout(validate_result.stdout)

        reconstruct_cmd = [
            sys.executable,
            tool_path(root, "reconstruct_water.py"),
            manifest_path,
            water_dir,
            "--frames", str(config["frames"]),
            "--threshold", str(args.threshold),
            "--smooth-iterations", str(config["smooth_iterations"]),
            "--smooth-alpha", str(config["smooth_alpha"]),
            "--surface-mode", str(config["surface_mode"]),
            "--implicit-iso", str(config["implicit_iso"]),
            "--implicit-blur-iterations", str(config["implicit_blur_iterations"]),
        ]
        if config["write_normals"]:
            reconstruct_cmd.append("--write-normals")
        if args.reuse_water_mesh:
            reconstruct_cmd.append("--reuse-if-fresh")
        reconstruct_result, _reconstruct_item = pipeline.run("reconstruct_water", reconstruct_cmd)
        summary["reconstruction_metrics"] = parse_key_value_stdout(reconstruct_result.stdout)
        require_file(water_index, "water reconstruction index")

        convert_cmd = [
            sys.executable,
            tool_path(root, "convert_render_cache.py"),
            manifest_path,
            converted_dir,
            "--require-cinematic",
            "--water-reconstruction", water_index,
        ]
        if args.reuse_converted:
            convert_cmd.append("--reuse-if-fresh")
        convert_result, _convert_item = pipeline.run("convert_render_cache", convert_cmd)
        summary["convert_metrics"] = parse_key_value_stdout(convert_result.stdout)
        require_file(sequence_path, "converted sequence")

        selected_renderer, blender_report = choose_renderer(config["renderer"], args, pipeline, root)
        summary["selected_renderer"] = selected_renderer
        if blender_report is not None:
            summary["blender_check"] = blender_report

        if selected_renderer == "blender":
            render_dir = blender_dir
            command = [
                sys.executable,
                tool_path(root, "render_bridge_blender.py"),
                sequence_path,
                render_dir,
                "--frames", str(config["frames"]),
                "--width", str(config["width"]),
                "--height", str(config["height"]),
                "--samples", str(config["samples"]),
                "--max-secondary-particles", str(config["max_secondary_particles"]),
                "--secondary-radius-scale", str(config["secondary_radius_scale"]),
                "--min-nonblank-ratio", str(config["min_nonblank_ratio"]),
                "--timeout-seconds", str(args.timeout_seconds),
                "--preset-config", preset_config_path or default_preset_config_path(),
                "--render-preset", render_preset_name,
            ]
            if args.blender:
                command.extend(["--blender", args.blender])
            pipeline.run("render_blender", command)
            frame_dir = os.path.join(render_dir, "frames")
            summary["artifacts"]["render_summary"] = os.path.join(render_dir, "bridge_summary.json")
        else:
            render_dir = preview_dir
            pipeline.run("render_preview", [
                sys.executable,
                tool_path(root, "cinematic_render_stub.py"),
                manifest_path,
                render_dir,
                "--frames", str(config["frames"]),
                "--width", str(config["width"]),
                "--height", str(config["height"]),
                "--min-occupancy", str(config["min_occupancy"]),
                "--water-reconstruction", water_index,
            ])
            frame_dir = render_dir
            summary["artifacts"]["render_summary"] = os.path.join(render_dir, "render_summary.json")
        require_dir(frame_dir, "render frame directory")
        summary["artifacts"]["render_frame_dir"] = frame_dir

        pipeline.run("assemble_gif", [
            sys.executable,
            tool_path(root, "assemble_frames.py"),
            frame_dir,
            gif_path,
            "--fps", str(config["fps"]),
        ])
        require_file(gif_path, "shot GIF")

        manifest = read_json(manifest_path)
        sequence = read_json(sequence_path)
        water = read_json(water_index)
        secondary_channels = secondary_channel_metrics(manifest_path, manifest)
        secondary_volumes = secondary_volume_metrics(manifest_path, manifest)
        summary["metrics"] = {
            "cache_frame_count": len(manifest.get("frames", [])),
            "export_cache_reused": bool(summary.get("export_metrics", {}).get("reused", False)),
            "validation_reused": bool(summary.get("validation_metrics", {}).get("reused", False)),
            "converted_frame_count": sequence.get("frame_count"),
            "water_mesh_frame_count": water.get("frame_count"),
            "water_reconstruction_reused": bool(summary.get("reconstruction_metrics", {}).get("reused", False)),
            "surface_mode": water.get("surface_mode", "voxel"),
            "implicit_iso": water.get("implicit_iso"),
            "implicit_blur_iterations": water.get("implicit_blur_iterations", 0),
            "converted_sequence_reused": bool(summary.get("convert_metrics", {}).get("reused", False)),
            "secondary_channels": secondary_channels,
            "secondary_volumes": secondary_volumes,
            "shot_gif_bytes": os.path.getsize(gif_path),
        }
        if config["secondary_physical_particles"] > 0:
            secondary_acceptance = config.get("secondary_acceptance_qa")
            if not isinstance(secondary_acceptance, dict):
                secondary_acceptance = {}
            total_fraction = float(secondary_acceptance.get("min_total_fraction", 0.5) or 0.5)
            foam_fraction = float(secondary_acceptance.get("min_foam_fraction", 0.08) or 0.08)
            acceptance_min = max(1, int(config["secondary_physical_particles"] * total_fraction))
            if secondary_acceptance.get("min_total_count") is not None:
                acceptance_min = max(1, int(secondary_acceptance.get("min_total_count")))
            summary["metrics"]["secondary_acceptance_min"] = acceptance_min
            first_total = secondary_total_count(secondary_channels.get("first", {}))
            last_total = secondary_total_count(secondary_channels.get("last", {}))
            if first_total < acceptance_min or last_total < acceptance_min:
                fail(f"physical secondary channel count below acceptance min {acceptance_min}: first={first_total} last={last_total}")
            foam_acceptance_min = max(1, int(config["secondary_physical_particles"] * foam_fraction))
            if secondary_acceptance.get("min_foam_count") is not None:
                foam_acceptance_min = max(1, int(secondary_acceptance.get("min_foam_count")))
            summary["metrics"]["secondary_foam_acceptance_min"] = foam_acceptance_min
            first_foam = secondary_channel_count(secondary_channels.get("first", {}), "foam")
            last_foam = secondary_channel_count(secondary_channels.get("last", {}), "foam")
            if first_foam < foam_acceptance_min or last_foam < foam_acceptance_min:
                fail(f"physical secondary foam count below acceptance min {foam_acceptance_min}: first={first_foam} last={last_foam}")
            export_metrics = summary.get("export_metrics", {})
            if export_metrics.get("secondary_spray_interface_gate") is True:
                if export_metrics.get("secondary_spray_interface_gate_passed_last") is not True:
                    fail("physical secondary interface gate did not pass")
                effective_requested = int(export_metrics.get("secondary_spray_effective_requested_last", 0) or 0)
                if effective_requested < acceptance_min:
                    fail(
                        f"physical secondary interface gate effective request below acceptance min "
                        f"{acceptance_min}: effective={effective_requested}"
                    )
                if "secondary_spray_impact_candidates_last" in export_metrics:
                    impact_candidates = int(export_metrics.get("secondary_spray_impact_candidates_last", 0) or 0)
                    if impact_candidates <= 0:
                        fail("physical secondary impact candidate count is zero")
                if "secondary_spray_foam_ready_droplets_last" in export_metrics:
                    foam_ready = int(export_metrics.get("secondary_spray_foam_ready_droplets_last", 0) or 0)
                    if foam_ready < foam_acceptance_min:
                        fail(f"physical secondary foam-ready droplet count below acceptance min {foam_acceptance_min}: foam_ready={foam_ready}")
        render_summary_path = summary["artifacts"].get("render_summary")
        if render_summary_path and os.path.isfile(render_summary_path):
            render_summary = read_json(render_summary_path)
            summary["metrics"]["camera_motion"] = render_summary.get("camera_motion", {})
            summary["metrics"]["camera_framing"] = render_summary.get("camera_framing", {})
            summary["metrics"]["camera_path"] = render_summary.get("camera_path_metrics", {})
            summary["metrics"]["camera_stability"] = evaluate_camera_stability(
                config, summary["metrics"]["camera_path"])
            if summary["metrics"]["camera_stability"].get("enabled") and not summary["metrics"]["camera_stability"].get("passed"):
                fail(f"camera stability gate failed: {summary['metrics']['camera_stability']}")
            summary["metrics"]["water_material"] = render_summary.get("water_material", {})
            summary["metrics"]["water_surface_detail"] = render_summary.get("water_surface_detail", {})
            summary["metrics"]["water_surface_glint_pass"] = render_summary.get("water_surface_glint_pass", {})
            summary["metrics"]["water_reflection_pass"] = render_summary.get("water_reflection_pass", {})
            summary["metrics"]["water_volume_scattering_pass"] = render_summary.get("water_volume_scattering_pass", {})
            summary["metrics"]["water_impact_ripple_pass"] = render_summary.get("water_impact_ripple_pass", {})
            summary["metrics"]["water_impact_ripple_counts"] = render_summary.get("water_impact_ripple_counts", {})
            summary["metrics"]["secondary_channel_radius_scales"] = render_summary.get("secondary_channel_radius_scales", {})
            summary["metrics"]["secondary_soft_pass"] = render_summary.get("secondary_soft_pass", {})
            summary["metrics"]["secondary_streak_pass"] = render_summary.get("secondary_streak_pass", {})
            summary["metrics"]["secondary_streak_counts"] = render_summary.get("secondary_streak_counts", {})
            summary["metrics"]["surface_contact_foam_pass"] = render_summary.get("surface_contact_foam_pass", {})
            summary["metrics"]["surface_contact_foam_counts"] = render_summary.get("surface_contact_foam_counts", {})
            summary["metrics"]["secondary_framing"] = render_summary.get("secondary_framing", {})
            summary["metrics"]["secondary_framing_gate"] = evaluate_secondary_framing_qa(
                config, summary["metrics"]["secondary_framing"])
            if summary["metrics"]["secondary_framing_gate"].get("enabled") and not summary["metrics"]["secondary_framing_gate"].get("passed"):
                fail(f"secondary framing QA gate failed: {summary['metrics']['secondary_framing_gate']}")
            summary["metrics"]["visual_qa"] = render_summary.get("visual_qa", {})
            summary["metrics"]["visual_qa_gate"] = evaluate_visual_qa(
                config, summary["metrics"]["visual_qa"])
            if summary["metrics"]["visual_qa_gate"].get("enabled") and not summary["metrics"]["visual_qa_gate"].get("passed"):
                fail(f"visual QA gate failed: {summary['metrics']['visual_qa_gate']}")
            temporal_cfg = config.get("temporal_highlight_qa", {})
            if isinstance(temporal_cfg, dict) and temporal_cfg.get("enabled", False):
                summary["metrics"]["temporal_highlight"] = summarize_temporal_highlights(
                    frame_dir, temporal_cfg)
                summary["metrics"]["temporal_highlight_gate"] = evaluate_temporal_highlight_qa(
                    config, summary["metrics"]["temporal_highlight"])
                if summary["metrics"]["temporal_highlight_gate"].get("enabled") and not summary["metrics"]["temporal_highlight_gate"].get("passed"):
                    fail(f"temporal highlight QA gate failed: {summary['metrics']['temporal_highlight_gate']}")
            else:
                summary["metrics"]["temporal_highlight_gate"] = {"enabled": False}
        if args.report:
            report_out = os.path.abspath(args.report)
            summary["artifacts"]["report"] = report_out
        focus_review = create_focus_review(
            summary, root, frame_dir, config.get("focus_review", {}), config["review_frames"])
        if focus_review:
            summary["artifacts"]["focus_sheet"] = focus_review["focus_sheet"]
            summary["artifacts"]["focus_review_manifest"] = focus_review["focus_review_manifest"]
            summary["metrics"]["focus_review"] = focus_review["focus_review"]
            summary["metrics"]["focus_review_gate"] = evaluate_focus_review_qa(
                config, summary["metrics"]["focus_review"])
            if (summary["metrics"]["focus_review_gate"].get("enabled")
                    and not summary["metrics"]["focus_review_gate"].get("passed")):
                fail(f"focus review QA gate failed: {summary['metrics']['focus_review_gate']}")
        secondary_depth = create_secondary_depth_review(
            summary, root, frame_dir, config.get("secondary_depth_review", {}), config["review_frames"])
        if secondary_depth:
            summary["artifacts"]["secondary_depth_sheet"] = secondary_depth["secondary_depth_sheet"]
            summary["artifacts"]["secondary_depth_manifest"] = secondary_depth["secondary_depth_manifest"]
            summary["metrics"]["secondary_depth_review"] = secondary_depth["secondary_depth_review"]
            summary["metrics"]["secondary_depth_review_gate"] = evaluate_secondary_depth_review_qa(
                config, summary["metrics"]["secondary_depth_review"])
            if (summary["metrics"]["secondary_depth_review_gate"].get("enabled")
                    and not summary["metrics"]["secondary_depth_review_gate"].get("passed")):
                fail(f"secondary depth review QA gate failed: {summary['metrics']['secondary_depth_review_gate']}")
        ripple_readability = create_ripple_readability_review(
            summary, root, frame_dir, config.get("ripple_readability_review", {}), config["review_frames"])
        if ripple_readability:
            summary["artifacts"]["ripple_readability_sheet"] = ripple_readability["ripple_readability_sheet"]
            summary["artifacts"]["ripple_readability_manifest"] = ripple_readability["ripple_readability_manifest"]
            summary["metrics"]["ripple_readability"] = ripple_readability["ripple_readability"]
            summary["metrics"]["ripple_readability_gate"] = evaluate_ripple_readability_qa(
                config, summary["metrics"]["ripple_readability"])
            if (summary["metrics"]["ripple_readability_gate"].get("enabled")
                    and not summary["metrics"]["ripple_readability_gate"].get("passed")):
                fail(f"ripple readability QA gate failed: {summary['metrics']['ripple_readability_gate']}")
        if config["review_pack"]:
            review = create_review_pack(summary, root, frame_dir, config["review_frames"])
            summary["artifacts"]["review_dir"] = review["review_dir"]
            summary["artifacts"]["contact_sheet"] = review["contact_sheet"]
            summary["artifacts"]["review_manifest"] = review["review_manifest"]
            summary["artifacts"]["review_keyframes"] = review["review_keyframes"]
            summary["metrics"]["review_frame_count"] = review["review_frame_count"]
            comparison = create_review_comparison(
                summary, root, review["review_manifest"], config["compare_review_manifests"])
            if comparison:
                summary["artifacts"]["comparison_sheet"] = comparison["comparison_sheet"]
                summary["artifacts"]["comparison_manifest"] = comparison["comparison_manifest"]
                summary["metrics"]["comparison_source_count"] = comparison["comparison_source_count"]
            focus_comparison = create_focus_review_comparison(
                summary, root, review["review_manifest"], config["compare_review_manifests"])
            if focus_comparison:
                summary["artifacts"]["focus_comparison_sheet"] = focus_comparison["focus_comparison_sheet"]
                summary["artifacts"]["focus_comparison_manifest"] = focus_comparison["focus_comparison_manifest"]
                summary["metrics"]["focus_comparison_source_count"] = focus_comparison["focus_comparison_source_count"]
            depth_comparison = create_secondary_depth_comparison(
                summary, root, review["review_manifest"], config["compare_review_manifests"])
            if depth_comparison:
                summary["artifacts"]["secondary_depth_comparison_sheet"] = (
                    depth_comparison["secondary_depth_comparison_sheet"]
                )
                summary["artifacts"]["secondary_depth_comparison_manifest"] = (
                    depth_comparison["secondary_depth_comparison_manifest"]
                )
                summary["metrics"]["secondary_depth_comparison_source_count"] = (
                    depth_comparison["secondary_depth_comparison_source_count"]
                )
            readability_comparison = create_ripple_readability_comparison(
                summary, root, review["review_manifest"], config["compare_review_manifests"])
            if readability_comparison:
                summary["artifacts"]["ripple_readability_comparison_sheet"] = (
                    readability_comparison["ripple_readability_comparison_sheet"]
                )
                summary["artifacts"]["ripple_readability_comparison_manifest"] = (
                    readability_comparison["ripple_readability_comparison_manifest"]
                )
                summary["metrics"]["ripple_readability_comparison_source_count"] = (
                    readability_comparison["ripple_readability_comparison_source_count"]
                )
            temporal_diff = create_temporal_diff_review(
                summary, root, frame_dir, config.get("temporal_diff_review", {}))
            if temporal_diff:
                summary["artifacts"]["temporal_diff_sheet"] = temporal_diff["temporal_diff_sheet"]
                summary["artifacts"]["temporal_diff_manifest"] = temporal_diff["temporal_diff_manifest"]
                summary["metrics"]["temporal_diff_pair_count"] = temporal_diff["temporal_diff_pair_count"]
        finish("ok")
        if args.report:
            write_text(report_out, render_report(summary, root))
            write_json(summary_path, summary)
        print(f"status=ok renderer={selected_renderer} frames={config['frames']}")
        print(f"summary={summary_path}")
        print(f"gif={gif_path}")
        if args.report:
            print(f"report={report_out}")
        return 0
    except ShotError as exc:
        finish("failed", exc)
        print(f"status=fail error={exc} summary={summary_path}", file=sys.stderr)
        return 1
    except OSError as exc:
        finish("failed", exc)
        print(f"status=fail error={exc} summary={summary_path}", file=sys.stderr)
        return 1


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())
