#!/usr/bin/env python
"""Run the LSFS cinematic shot pipeline end to end.

The runner orchestrates existing tools; it does not change simulation or render
formats. It writes a durable shot_summary.json with commands, timings, and
artifact paths so a shot can be inspected or rerun.

Usage:
  python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/bubble_cinematic --frames 24 --width 1280 --height 720
"""

import argparse
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
    for key in ("manifest", "sequence", "water_reconstruction", "render_summary",
                "render_frame_dir", "gif", "contact_sheet", "review_manifest",
                "comparison_sheet", "comparison_manifest", "temporal_diff_sheet",
                "temporal_diff_manifest", "focus_sheet", "focus_review_manifest",
                "review_dir"):
            if key in artifacts:
                lines.append(f"- {key}: `{report_path(artifacts.get(key), root)}`")
    lines.extend([
        "",
        "## Metrics",
        "",
        f"- Cache frames: `{metrics.get('cache_frame_count', 'n/a')}`",
        f"- Converted frames: `{metrics.get('converted_frame_count', 'n/a')}`",
        f"- Water mesh frames: `{metrics.get('water_mesh_frame_count', 'n/a')}`",
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
        f"- Secondary channels first: `{format_secondary_channels(metrics.get('secondary_channels', {}).get('first'))}`",
        f"- Secondary channels last: `{format_secondary_channels(metrics.get('secondary_channels', {}).get('last'))}`",
        f"- Secondary volume first: `{format_secondary_volumes(metrics.get('secondary_volumes', {}).get('first'))}`",
        f"- Secondary volume last: `{format_secondary_volumes(metrics.get('secondary_volumes', {}).get('last'))}`",
        f"- Secondary acceptance min: `{metrics.get('secondary_acceptance_min', 'n/a')}`",
        f"- Secondary foam acceptance min: `{metrics.get('secondary_foam_acceptance_min', 'n/a')}`",
        f"- Secondary interface gate: `{format_secondary_interface_gate(summary.get('export_metrics', {}))}`",
        f"- Review keyframes: `{metrics.get('review_frame_count', 'n/a')}`",
        f"- Review comparison sources: `{metrics.get('comparison_source_count', 'n/a')}`",
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
        "S88 should use the focus-review evidence to tune the contact camera, ripple placement, or focus-comparison artifacts.",
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
        "focus_review": section(renderer, "focus_review"),
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
        export_result, _export_item = pipeline.run("export_render_cache", export_cmd)
        summary["export_metrics"] = parse_key_value_stdout(export_result.stdout)
        require_file(manifest_path, "render cache manifest")

        pipeline.run("validate_render_cache", [
            sys.executable,
            tool_path(root, "validate_render_cache.py"),
            manifest_path,
            "--require-cinematic",
        ])

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
        pipeline.run("reconstruct_water", reconstruct_cmd)
        require_file(water_index, "water reconstruction index")

        pipeline.run("convert_render_cache", [
            sys.executable,
            tool_path(root, "convert_render_cache.py"),
            manifest_path,
            converted_dir,
            "--require-cinematic",
            "--water-reconstruction", water_index,
        ])
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
            "converted_frame_count": sequence.get("frame_count"),
            "water_mesh_frame_count": water.get("frame_count"),
            "surface_mode": water.get("surface_mode", "voxel"),
            "implicit_iso": water.get("implicit_iso"),
            "implicit_blur_iterations": water.get("implicit_blur_iterations", 0),
            "secondary_channels": secondary_channels,
            "secondary_volumes": secondary_volumes,
            "shot_gif_bytes": os.path.getsize(gif_path),
        }
        if config["secondary_physical_particles"] > 0:
            acceptance_min = max(1, int(config["secondary_physical_particles"] * 0.5))
            summary["metrics"]["secondary_acceptance_min"] = acceptance_min
            first_total = secondary_total_count(secondary_channels.get("first", {}))
            last_total = secondary_total_count(secondary_channels.get("last", {}))
            if first_total < acceptance_min or last_total < acceptance_min:
                fail(f"physical secondary channel count below acceptance min {acceptance_min}: first={first_total} last={last_total}")
            foam_acceptance_min = max(1, int(config["secondary_physical_particles"] * 0.08))
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
