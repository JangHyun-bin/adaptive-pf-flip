#!/usr/bin/env python
"""Split masked water faces into a localized Mitsuba material response."""

import argparse
import copy
import os
import re
from datetime import datetime, timezone

from add_mitsuba_water_mask_highlights import (
    MASK_SCHEMAS,
    add_response_comment,
    csv3,
    fmt,
    mask_layer_ref,
    output_frame_map,
    parse_vec3,
    resolve_path,
    selected_frames,
    source_entry,
    write_command_list,
)
from add_mitsuba_water_mask_mesh_response import (
    read_obj_mesh,
    require_pillow,
    select_faces,
    write_selected_obj,
    xml_path,
)
from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from composite_mitsuba_secondary_layer import parse_camera


RESPONSE_BSDF_ID = "lsfs_water_surface_masked_response"


def normalized_path(path):
    return os.path.normcase(os.path.abspath(str(path).replace("/", os.sep)))


def load_mask_luma(path):
    from PIL import Image

    image = Image.open(path)
    if "A" in image.getbands():
        alpha = image.getchannel("A")
        if alpha.getextrema() != (255, 255):
            return alpha
    return image.convert("L")


def current_water_shape_mesh(xml_text):
    pattern = re.compile(r'(?P<block>\s*<shape\s+type="obj"(?:\s+id="[^"]+")?>.*?</shape>)', re.DOTALL)
    candidates = []
    for match in pattern.finditer(xml_text):
        block = match.group("block")
        if '<ref name="bsdf" id="lsfs_water_surface"' not in block:
            continue
        filename = re.search(r'<string\s+name="filename"\s+value="([^"]+)"\s*/>', block)
        if not filename:
            continue
        score = 0
        if "water_remainder" in block:
            score += 2
        if 'id="lsfs_water_surface"' in block:
            score += 1
        candidates.append((score, filename.group(1)))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return resolve_path(candidates[0][1])


def response_bsdf_block(
    args,
    bsdf_id=RESPONSE_BSDF_ID,
    alpha=None,
    specular_reflectance=None,
    specular_transmittance=None,
):
    if alpha is None:
        alpha = args.response_alpha
    if specular_reflectance is None:
        specular_reflectance = args.response_specular_reflectance_vec
    if specular_transmittance is None:
        specular_transmittance = args.response_specular_transmittance_vec
    lines = [
        f'  <bsdf type="roughdielectric" id="{bsdf_id}">',
    ]
    if args.distribution != "none":
        lines.append(f'    <string name="distribution" value="{args.distribution}"/>')
    lines.extend([
        f'    <float name="alpha" value="{fmt(alpha)}"/>',
        f'    <float name="int_ior" value="{fmt(args.int_ior)}"/>',
        f'    <float name="ext_ior" value="{fmt(args.ext_ior)}"/>',
    ])
    if specular_reflectance is not None:
        lines.append(
            f'    <rgb name="specular_reflectance" value="{csv3(specular_reflectance)}"/>'
        )
    if specular_transmittance is not None:
        lines.append(
            f'    <rgb name="specular_transmittance" value="{csv3(specular_transmittance)}"/>'
        )
    lines.append("  </bsdf>")
    return "\n".join(lines)


def lerp(a, b, t):
    return float(a) + (float(b) - float(a)) * float(t)


def clamp(value, low, high):
    return max(float(low), min(float(high), float(value)))


def arg_float(args, name, default):
    value = getattr(args, name, default)
    return float(default if value is None else value)


def arg_int(args, name, default):
    value = getattr(args, name, default)
    return int(default if value is None else value)


def lerp_vec3(a, b, t):
    if a is None and b is None:
        return None
    if a is None:
        a = b
    if b is None:
        b = a
    return [lerp(a[index], b[index], t) for index in range(3)]


def scale_vec3(values, scale):
    if values is None:
        return None
    return [clamp(float(item) * float(scale), 0.0, 1.0) for item in values]


def coverage_float(frame, key):
    try:
        return float((frame or {}).get(key) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def coverage_control(mask_frame, args):
    coverage = coverage_float(mask_frame, "layer_coverage")
    strong_coverage = coverage_float(mask_frame, "layer_strong_coverage")
    strength = float(getattr(args, "coverage_attenuation_strength", 0.0) or 0.0)
    pivot = float(getattr(args, "coverage_attenuation_pivot", 0.0) or 0.0)
    width = max(1.0e-9, float(getattr(args, "coverage_attenuation_width", 1.0) or 1.0))
    max_attenuation = float(getattr(args, "coverage_attenuation_max", 1.0) or 0.0)
    ramp = clamp((coverage - pivot) / width, 0.0, 1.0) if strength > 0.0 else 0.0
    attenuation = clamp(ramp * strength, 0.0, max_attenuation) if strength > 0.0 else 0.0
    rescue_strength = float(getattr(args, "low_coverage_rescue_strength", 0.0) or 0.0)
    rescue_pivot = float(getattr(args, "low_coverage_rescue_pivot", 0.0) or 0.0)
    rescue_width = max(1.0e-9, float(getattr(args, "low_coverage_rescue_width", 1.0) or 1.0))
    rescue_ramp = clamp((rescue_pivot - coverage) / rescue_width, 0.0, 1.0) if rescue_strength > 0.0 else 0.0
    rescue = clamp(rescue_ramp * rescue_strength, 0.0, 1.0) if rescue_strength > 0.0 else 0.0
    band_strength = float(getattr(args, "coverage_band_rescue_strength", 0.0) or 0.0)
    band_center = float(getattr(args, "coverage_band_rescue_center", 0.0) or 0.0)
    band_width = max(1.0e-9, float(getattr(args, "coverage_band_rescue_width", 1.0) or 1.0))
    band_ramp = (
        clamp(1.0 - abs(coverage - band_center) / band_width, 0.0, 1.0)
        if band_strength > 0.0
        else 0.0
    )
    band_rescue = clamp(band_ramp * band_strength, 0.0, 1.0) if band_strength > 0.0 else 0.0
    total_rescue = clamp(rescue + band_rescue, 0.0, 1.0)

    face_limit = int(getattr(args, "face_limit", 0) or 0)
    if face_limit > 0:
        face_scale = max(
            0.0,
            1.0
            - attenuation
            + total_rescue * float(getattr(args, "low_coverage_rescue_face_limit_boost", 0.0) or 0.0),
        )
        effective_face_limit = max(1, int(round(face_limit * face_scale)))
    else:
        effective_face_limit = face_limit
    alpha_scale = 1.0 + attenuation * float(getattr(args, "coverage_alpha_boost", 0.0) or 0.0)
    alpha_scale *= max(
        0.0,
        1.0 - total_rescue * float(getattr(args, "low_coverage_rescue_alpha_tighten", 0.0) or 0.0),
    )
    reflectance_scale = max(
        0.0,
        1.0 - attenuation * float(getattr(args, "coverage_reflectance_attenuation", 0.0) or 0.0),
    )
    reflectance_scale *= 1.0 + total_rescue * float(getattr(args, "low_coverage_rescue_reflectance_boost", 0.0) or 0.0)
    transmittance_scale = max(
        0.0,
        1.0 - attenuation * float(getattr(args, "coverage_transmittance_attenuation", 0.0) or 0.0),
    )
    transmittance_scale *= 1.0 + total_rescue * float(getattr(args, "low_coverage_rescue_transmittance_boost", 0.0) or 0.0)
    return {
        "layer_coverage": coverage,
        "layer_strong_coverage": strong_coverage,
        "ramp": ramp,
        "attenuation": attenuation,
        "low_coverage_rescue_ramp": rescue_ramp,
        "low_coverage_rescue": rescue,
        "coverage_band_rescue_ramp": band_ramp,
        "coverage_band_rescue": band_rescue,
        "total_rescue": total_rescue,
        "effective_face_limit": effective_face_limit,
        "alpha_scale": alpha_scale,
        "reflectance_scale": reflectance_scale,
        "transmittance_scale": transmittance_scale,
    }


def screen_region_bounds(args):
    return {
        "x_min": arg_float(args, "screen_region_x_min", 0.0),
        "x_max": arg_float(args, "screen_region_x_max", 1.0),
        "y_min": arg_float(args, "screen_region_y_min", 0.0),
        "y_max": arg_float(args, "screen_region_y_max", 1.0),
    }


def screen_region_output_enabled(output_frame, args):
    output_min = arg_int(args, "screen_region_output_min", -1)
    output_max = arg_int(args, "screen_region_output_max", -1)
    try:
        frame_index = int(output_frame)
    except (TypeError, ValueError):
        return False
    if output_min >= 0 and frame_index < output_min:
        return False
    if output_max >= 0 and frame_index > output_max:
        return False
    return True


def screen_region_face_bucket(face_index):
    value = (int(face_index) * 2654435761 + 1013904223) & 0xFFFFFFFF
    return float(value) / 4294967296.0


def apply_screen_region_attenuation(selected, image_width, image_height, output_frame, mask_frame, args):
    strength = arg_float(args, "screen_region_attenuation_strength", 0.0)
    coverage = coverage_float(mask_frame, "layer_coverage")
    coverage_min = arg_float(args, "screen_region_coverage_min", 0.0)
    coverage_max = arg_float(args, "screen_region_coverage_max", 1.0)
    bounds = screen_region_bounds(args)
    stats = {
        "enabled": strength > 0.0,
        "active": False,
        "strength": strength,
        "layer_coverage": coverage,
        "coverage_min": coverage_min,
        "coverage_max": coverage_max,
        "output_min": arg_int(args, "screen_region_output_min", -1),
        "output_max": arg_int(args, "screen_region_output_max", -1),
        "x_min": bounds["x_min"],
        "x_max": bounds["x_max"],
        "y_min": bounds["y_min"],
        "y_max": bounds["y_max"],
        "candidate_faces": 0,
        "dropped_faces": 0,
        "kept_faces": len(selected),
        "drop_fraction": 0.0,
        "fallback_kept_one": False,
    }
    if not selected or strength <= 0.0:
        return selected, stats
    if coverage < coverage_min or coverage > coverage_max:
        return selected, stats
    if not screen_region_output_enabled(output_frame, args):
        return selected, stats

    width = max(1.0, float(image_width))
    height = max(1.0, float(image_height))
    kept = []
    dropped = []
    candidates = 0
    for item in selected:
        sx, sy = item["screen"]
        nx = clamp(float(sx) / width, 0.0, 1.0)
        ny = clamp(float(sy) / height, 0.0, 1.0)
        in_region = (
            bounds["x_min"] <= nx <= bounds["x_max"]
            and bounds["y_min"] <= ny <= bounds["y_max"]
        )
        if in_region:
            candidates += 1
            if screen_region_face_bucket(item["face_index"]) < strength:
                dropped.append(item)
                continue
        kept.append(item)
    if not dropped:
        stats["active"] = candidates > 0
        stats["candidate_faces"] = candidates
        return selected, stats
    if not kept:
        kept.append(dropped.pop(0))
        stats["fallback_kept_one"] = True
    stats["active"] = True
    stats["candidate_faces"] = candidates
    stats["dropped_faces"] = len(dropped)
    stats["kept_faces"] = len(kept)
    stats["drop_fraction"] = len(dropped) / float(max(1, len(selected)))
    return kept, stats


def screen_error_output_enabled(output_frame, args):
    output_min = arg_int(args, "screen_error_output_min", -1)
    output_max = arg_int(args, "screen_error_output_max", -1)
    try:
        frame_index = int(output_frame)
    except (TypeError, ValueError):
        return False
    if output_min >= 0 and frame_index < output_min:
        return False
    if output_max >= 0 and frame_index > output_max:
        return False
    return True


def screen_error_frame_map(args, root):
    path = getattr(args, "screen_error_gap_summary", None)
    if not path:
        return {}, None
    gap_path = require_file(resolve_path(path), "screen error gap summary")
    gap = read_json(gap_path)
    if gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_renderer_target_gap schema")
    return (
        {frame.get("output_frame"): frame for frame in gap.get("frames") or [] if frame.get("output_frame") is not None},
        {
            "path": gap_path,
            "repo_path": posix_rel(gap_path, root),
            "sha256": sha256_file(gap_path),
            "checks": gap.get("checks") or {},
        },
    )


def luma_from_pixel(pixel):
    return 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]


def sample_luma(image, x, y, radius):
    width, height = image.size
    px = int(round(float(x)))
    py = int(round(float(y)))
    radius = max(0, int(radius))
    total = 0.0
    count = 0
    for yy in range(max(0, py - radius), min(height - 1, py + radius) + 1):
        for xx in range(max(0, px - radius), min(width - 1, px + radius) + 1):
            total += luma_from_pixel(image.getpixel((xx, yy)))
            count += 1
    return total / float(max(1, count))


def load_screen_error_images(output_frame, screen_error_frames):
    frame = screen_error_frames.get(output_frame)
    if not frame:
        return None, None
    actual_path = resolve_path(frame.get("actual_repo_path"))
    target_path = resolve_path(frame.get("target_repo_path"))
    if not actual_path or not os.path.isfile(actual_path) or not target_path or not os.path.isfile(target_path):
        return None, None
    from PIL import Image

    actual = Image.open(actual_path).convert("RGB")
    target = Image.open(target_path).convert("RGB")
    if actual.size != target.size:
        actual = actual.resize(target.size, Image.Resampling.BICUBIC)
    return actual, target


def apply_screen_error_attenuation(selected, output_frame, mask_frame, screen_error_frames, args):
    strength = arg_float(args, "screen_error_attenuation_strength", 0.0)
    threshold = arg_float(args, "screen_error_negative_threshold", 8.0)
    width = max(1.0e-9, arg_float(args, "screen_error_negative_width", 48.0))
    max_drop_fraction = arg_float(args, "screen_error_max_drop_fraction", 1.0)
    sample_radius = arg_int(args, "screen_error_sample_radius", 0)
    coverage = coverage_float(mask_frame, "layer_coverage")
    coverage_min = arg_float(args, "screen_error_coverage_min", 0.0)
    coverage_max = arg_float(args, "screen_error_coverage_max", 1.0)
    stats = {
        "enabled": strength > 0.0 and bool(screen_error_frames),
        "active": False,
        "strength": strength,
        "negative_threshold": threshold,
        "negative_width": width,
        "max_drop_fraction": max_drop_fraction,
        "sample_radius": sample_radius,
        "layer_coverage": coverage,
        "coverage_min": coverage_min,
        "coverage_max": coverage_max,
        "output_min": arg_int(args, "screen_error_output_min", -1),
        "output_max": arg_int(args, "screen_error_output_max", -1),
        "sampled_faces": 0,
        "candidate_faces": 0,
        "dropped_faces": 0,
        "kept_faces": len(selected),
        "mean_candidate_delta": 0.0,
        "min_delta": 0.0,
        "max_delta": 0.0,
        "drop_fraction": 0.0,
        "fallback_kept_one": False,
    }
    if not selected or strength <= 0.0 or not screen_error_frames:
        return selected, stats
    if coverage < coverage_min or coverage > coverage_max:
        return selected, stats
    if not screen_error_output_enabled(output_frame, args):
        return selected, stats

    actual, target = load_screen_error_images(output_frame, screen_error_frames)
    if actual is None or target is None:
        return selected, stats

    drop_items = []
    candidate_deltas = []
    all_deltas = []
    for item in selected:
        sx, sy = item["screen"]
        actual_luma = sample_luma(actual, sx, sy, sample_radius)
        target_luma = sample_luma(target, sx, sy, sample_radius)
        delta = target_luma - actual_luma
        all_deltas.append(delta)
        if delta > -threshold:
            continue
        candidate_deltas.append(delta)
        response = clamp((-delta - threshold) / width, 0.0, 1.0)
        probability = clamp(strength * response, 0.0, 1.0)
        if probability <= 0.0:
            continue
        bucket = screen_region_face_bucket(item["face_index"])
        if bucket < probability:
            priority = bucket / max(1.0e-9, probability)
            drop_items.append((priority, item))

    if not candidate_deltas:
        stats["sampled_faces"] = len(all_deltas)
        stats["min_delta"] = min(all_deltas) if all_deltas else 0.0
        stats["max_delta"] = max(all_deltas) if all_deltas else 0.0
        return selected, stats

    max_drop = int(round(len(selected) * max_drop_fraction)) if max_drop_fraction > 0.0 else 0
    if max_drop_fraction > 0.0:
        max_drop = max(1, max_drop)
    drop_items.sort(key=lambda item: item[0])
    drop_indices = {item["face_index"] for _priority, item in drop_items[:max_drop]}
    kept = [item for item in selected if item["face_index"] not in drop_indices]
    if drop_indices and not kept:
        kept.append(selected[0])
        drop_indices.discard(selected[0]["face_index"])
        stats["fallback_kept_one"] = True
    stats["active"] = bool(drop_indices)
    stats["sampled_faces"] = len(all_deltas)
    stats["candidate_faces"] = len(candidate_deltas)
    stats["dropped_faces"] = len(drop_indices)
    stats["kept_faces"] = len(kept)
    stats["mean_candidate_delta"] = sum(candidate_deltas) / float(max(1, len(candidate_deltas)))
    stats["min_delta"] = min(all_deltas) if all_deltas else 0.0
    stats["max_delta"] = max(all_deltas) if all_deltas else 0.0
    stats["drop_fraction"] = len(drop_indices) / float(max(1, len(selected)))
    return kept, stats


def apply_screen_error_material_attenuation(selected, output_frame, mask_frame, screen_error_frames, args):
    strength = arg_float(args, "screen_error_material_attenuation_strength", 0.0)
    threshold = arg_float(args, "screen_error_negative_threshold", 8.0)
    width = max(1.0e-9, arg_float(args, "screen_error_negative_width", 48.0))
    min_scale = arg_float(args, "screen_error_material_min_scale", 0.25)
    sample_radius = arg_int(args, "screen_error_sample_radius", 0)
    coverage = coverage_float(mask_frame, "layer_coverage")
    coverage_min = arg_float(args, "screen_error_coverage_min", 0.0)
    coverage_max = arg_float(args, "screen_error_coverage_max", 1.0)
    stats = {
        "enabled": strength > 0.0 and bool(screen_error_frames),
        "active": False,
        "strength": strength,
        "negative_threshold": threshold,
        "negative_width": width,
        "min_scale": min_scale,
        "sample_radius": sample_radius,
        "layer_coverage": coverage,
        "coverage_min": coverage_min,
        "coverage_max": coverage_max,
        "output_min": arg_int(args, "screen_error_output_min", -1),
        "output_max": arg_int(args, "screen_error_output_max", -1),
        "sampled_faces": 0,
        "candidate_faces": 0,
        "attenuated_faces": 0,
        "mean_candidate_delta": 0.0,
        "min_delta": 0.0,
        "max_delta": 0.0,
        "mean_scale": 1.0,
        "min_applied_scale": 1.0,
    }
    if not selected or strength <= 0.0 or not screen_error_frames:
        return selected, stats
    if coverage < coverage_min or coverage > coverage_max:
        return selected, stats
    if not screen_error_output_enabled(output_frame, args):
        return selected, stats

    actual, target = load_screen_error_images(output_frame, screen_error_frames)
    if actual is None or target is None:
        return selected, stats

    all_deltas = []
    candidate_deltas = []
    applied_scales = []
    for item in selected:
        sx, sy = item["screen"]
        actual_luma = sample_luma(actual, sx, sy, sample_radius)
        target_luma = sample_luma(target, sx, sy, sample_radius)
        delta = target_luma - actual_luma
        all_deltas.append(delta)
        item["screen_error_luma_delta"] = delta
        item["screen_error_material_scale"] = 1.0
        if delta > -threshold:
            continue
        candidate_deltas.append(delta)
        response = clamp((-delta - threshold) / width, 0.0, 1.0)
        scale = clamp(1.0 - strength * response, min_scale, 1.0)
        if scale < 0.999:
            item["screen_error_material_scale"] = scale
            applied_scales.append(scale)

    if not candidate_deltas:
        stats["sampled_faces"] = len(all_deltas)
        stats["min_delta"] = min(all_deltas) if all_deltas else 0.0
        stats["max_delta"] = max(all_deltas) if all_deltas else 0.0
        return selected, stats

    stats["active"] = bool(applied_scales)
    stats["sampled_faces"] = len(all_deltas)
    stats["candidate_faces"] = len(candidate_deltas)
    stats["attenuated_faces"] = len(applied_scales)
    stats["mean_candidate_delta"] = sum(candidate_deltas) / float(max(1, len(candidate_deltas)))
    stats["min_delta"] = min(all_deltas) if all_deltas else 0.0
    stats["max_delta"] = max(all_deltas) if all_deltas else 0.0
    stats["mean_scale"] = sum(applied_scales) / float(max(1, len(applied_scales))) if applied_scales else 1.0
    stats["min_applied_scale"] = min(applied_scales) if applied_scales else 1.0
    return selected, stats


def resolved_bin_specs(args, control=None):
    count = max(1, int(args.response_bin_count))
    strong_alpha = args.response_bin_alpha_strong
    weak_alpha = args.response_bin_alpha_weak
    if strong_alpha is None:
        strong_alpha = args.response_alpha
    if weak_alpha is None:
        weak_alpha = args.response_alpha
    strong_reflectance = args.response_bin_specular_reflectance_strong_vec
    weak_reflectance = args.response_bin_specular_reflectance_weak_vec
    if strong_reflectance is None:
        strong_reflectance = args.response_specular_reflectance_vec
    if weak_reflectance is None:
        weak_reflectance = args.response_specular_reflectance_vec
    strong_transmittance = args.response_bin_specular_transmittance_strong_vec
    weak_transmittance = args.response_bin_specular_transmittance_weak_vec
    if strong_transmittance is None:
        strong_transmittance = args.response_specular_transmittance_vec
    if weak_transmittance is None:
        weak_transmittance = args.response_specular_transmittance_vec

    if isinstance(control, dict):
        alpha_scale = float(control.get("alpha_scale") or 1.0)
        reflectance_scale = float(control.get("reflectance_scale") or 1.0)
        transmittance_scale = float(control.get("transmittance_scale") or 1.0)
    else:
        attenuation = float(control or 0.0)
        alpha_scale = 1.0 + attenuation * float(getattr(args, "coverage_alpha_boost", 0.0) or 0.0)
        reflectance_scale = max(
            0.0,
            1.0 - attenuation * float(getattr(args, "coverage_reflectance_attenuation", 0.0) or 0.0),
        )
        transmittance_scale = max(
            0.0,
            1.0 - attenuation * float(getattr(args, "coverage_transmittance_attenuation", 0.0) or 0.0),
        )
    specs = []
    for index in range(count):
        t = index / float(max(1, count - 1))
        specs.append({
            "index": index,
            "bsdf_id": args.response_bsdf_id_prefix if count == 1 else f"{args.response_bsdf_id_prefix}_{index:02d}",
            "alpha": lerp(strong_alpha, weak_alpha, t) * alpha_scale,
            "specular_reflectance": scale_vec3(lerp_vec3(strong_reflectance, weak_reflectance, t), reflectance_scale),
            "specular_transmittance": scale_vec3(lerp_vec3(strong_transmittance, weak_transmittance, t), transmittance_scale),
        })
    return specs


def attenuated_spec(spec, scale, args):
    result = copy.deepcopy(spec)
    alpha_boost = arg_float(args, "screen_error_material_alpha_boost", 0.0)
    result["alpha"] = float(result["alpha"]) * (1.0 + alpha_boost * (1.0 - scale))
    result["specular_reflectance"] = scale_vec3(result.get("specular_reflectance"), scale)
    result["screen_error_material_scale"] = scale
    return result


def finalize_partition_specs(partitions, args):
    total = len(partitions)
    for index, item in enumerate(partitions):
        spec = copy.deepcopy(item["spec"])
        spec["source_bin_index"] = spec.get("index")
        spec["index"] = index
        spec["bsdf_id"] = args.response_bsdf_id_prefix if total == 1 else f"{args.response_bsdf_id_prefix}_{index:02d}"
        item["spec"] = spec
    return partitions


def partition_selected_faces(selected, specs, args=None):
    if len(specs) <= 1:
        bins = [{"spec": specs[0], "faces": selected}]
    else:
        bins = [{"spec": spec, "faces": []} for spec in specs]
        for index, item in enumerate(selected):
            bin_index = min(len(specs) - 1, int(index * len(specs) / max(1, len(selected))))
            bins[bin_index]["faces"].append(item)
        bins = [item for item in bins if item["faces"]]
    if args is None or arg_float(args, "screen_error_material_attenuation_strength", 0.0) <= 0.0:
        return bins

    partitions = []
    for bin_item in bins:
        normal = []
        attenuated = []
        for item in bin_item["faces"]:
            scale = float(item.get("screen_error_material_scale", 1.0) or 1.0)
            if scale < 0.999:
                attenuated.append(item)
            else:
                normal.append(item)
        if normal:
            partitions.append({"spec": copy.deepcopy(bin_item["spec"]), "faces": normal})
        if attenuated:
            scale = sum(float(item.get("screen_error_material_scale", 1.0) or 1.0) for item in attenuated) / float(len(attenuated))
            partitions.append({"spec": attenuated_spec(bin_item["spec"], scale, args), "faces": attenuated})
    if not partitions:
        return bins
    return finalize_partition_specs(partitions, args)


def insert_response_bsdf(xml_text, block):
    pattern = re.compile(
        r'(<bsdf\s+type="roughdielectric"\s+id="lsfs_water_surface">.*?</bsdf>)',
        flags=re.DOTALL,
    )
    match = pattern.search(xml_text)
    if not match:
        raise ValueError("missing lsfs_water_surface roughdielectric BSDF")
    return xml_text[:match.end()] + "\n" + block + xml_text[match.end():], 1


def shape_block(shape_id, mesh_path, bsdf_id):
    return "\n".join([
        f'  <shape type="obj" id="{shape_id}">',
        f'    <string name="filename" value="{xml_path(mesh_path)}"/>',
        '    <boolean name="face_normals" value="true"/>',
        f'    <ref name="bsdf" id="{bsdf_id}"/>',
        "  </shape>",
    ])


def replace_water_shape(xml_text, source_mesh, remainder_mesh, response_shapes, frame_index, args):
    source_norm = normalized_path(source_mesh)
    pattern = re.compile(r'(?P<block>\s*<shape\s+type="obj"(?:\s+id="[^"]+")?>.*?</shape>)', re.DOTALL)
    for match in pattern.finditer(xml_text):
        block = match.group("block")
        if 'id="lsfs_water_surface"' not in block:
            continue
        filename = re.search(r'<string\s+name="filename"\s+value="([^"]+)"\s*/>', block)
        if not filename:
            continue
        if normalized_path(filename.group(1)) != source_norm:
            continue
        replacement_shapes = [
            shape_block(f"{args.remainder_shape_id_prefix}_{frame_index:04d}", remainder_mesh, "lsfs_water_surface"),
        ]
        for response_shape in response_shapes:
            replacement_shapes.append(
                shape_block(
                    f"{args.response_shape_id_prefix}_{frame_index:04d}_{response_shape['bin_index']:02d}",
                    response_shape["mesh_path"],
                    response_shape["bsdf_id"],
                )
            )
        replacement = "\n".join(replacement_shapes)
        return xml_text[:match.start()] + "\n" + replacement + xml_text[match.end():], 1
    raise ValueError(f"missing water shape for {source_mesh}")


def remainder_faces(vertices, faces, selected):
    selected_indices = {item["face_index"] for item in selected}
    return [
        {
            "face": face,
            "face_index": face_index,
            "centroid": (0.0, 0.0, 0.0),
            "screen": (0.0, 0.0),
            "depth": 0.0,
            "mask_value": 0,
            "source_luma": None,
            "score": 0.0,
        }
        for face_index, face in enumerate(faces)
        if face_index not in selected_indices
    ]


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    settings = export.get("water_mask_material_response") or {}
    lines = [
        f"# {export['title']}",
        "",
        f"Generated UTC: `{export['generated_utc']}`",
        f"Export JSON: `{posix_rel(export_path, root)}`",
        f"Status: `{export['status']}`",
        "",
        "## Inputs",
        "",
        f"- Base export: `{export['sources']['base_export']['repo_path']}`",
        f"- Mask source: `{export['sources']['mask_source']['repo_path']}`",
        "",
        "## Water Mask Material Response",
        "",
        f"- Face limit: `{settings.get('face_limit')}`",
        f"- Face stride: `{settings.get('face_stride')}`",
        f"- Response alpha: `{settings.get('response_alpha')}`",
        f"- Response bins: `{settings.get('response_bin_count')}`",
        f"- Distribution: `{settings.get('distribution')}`",
        f"- IOR: `{settings.get('ext_ior')} -> {settings.get('int_ior')}`",
        f"- Specular reflectance: `{settings.get('response_specular_reflectance')}`",
        f"- Specular transmittance: `{settings.get('response_specular_transmittance')}`",
        f"- Mask threshold: `{settings.get('mask_threshold')}`",
        f"- Source luma gate: `{settings.get('source_luma_min')}..{settings.get('source_luma_max')}`",
        "- Coverage attenuation: "
        f"strength=`{settings.get('coverage_attenuation_strength')}`, "
        f"pivot=`{settings.get('coverage_attenuation_pivot')}`, "
        f"width=`{settings.get('coverage_attenuation_width')}`, "
        f"max=`{settings.get('coverage_attenuation_max')}`",
        "- Coverage material scale: "
        f"alpha_boost=`{settings.get('coverage_alpha_boost')}`, "
        f"reflectance_attenuation=`{settings.get('coverage_reflectance_attenuation')}`, "
        f"transmittance_attenuation=`{settings.get('coverage_transmittance_attenuation')}`",
        "- Low-coverage rescue: "
        f"strength=`{settings.get('low_coverage_rescue_strength')}`, "
        f"pivot=`{settings.get('low_coverage_rescue_pivot')}`, "
        f"width=`{settings.get('low_coverage_rescue_width')}`",
        "- Coverage-band rescue: "
        f"strength=`{settings.get('coverage_band_rescue_strength')}`, "
        f"center=`{settings.get('coverage_band_rescue_center')}`, "
        f"width=`{settings.get('coverage_band_rescue_width')}`",
        "- Screen-region attenuation: "
        f"strength=`{settings.get('screen_region_attenuation_strength')}`, "
        f"x=`{settings.get('screen_region_x_min')}..{settings.get('screen_region_x_max')}`, "
        f"y=`{settings.get('screen_region_y_min')}..{settings.get('screen_region_y_max')}`, "
        f"coverage=`{settings.get('screen_region_coverage_min')}..{settings.get('screen_region_coverage_max')}`, "
        f"output=`{settings.get('screen_region_output_min')}..{settings.get('screen_region_output_max')}`",
        "- Screen-error attenuation: "
        f"strength=`{settings.get('screen_error_attenuation_strength')}`, "
        f"threshold=`{settings.get('screen_error_negative_threshold')}`, "
        f"width=`{settings.get('screen_error_negative_width')}`, "
        f"coverage=`{settings.get('screen_error_coverage_min')}..{settings.get('screen_error_coverage_max')}`, "
        f"output=`{settings.get('screen_error_output_min')}..{settings.get('screen_error_output_max')}`, "
        f"gap=`{settings.get('screen_error_gap_summary')}`",
        "- Screen-error material attenuation: "
        f"strength=`{settings.get('screen_error_material_attenuation_strength')}`, "
        f"min_scale=`{settings.get('screen_error_material_min_scale')}`, "
        f"alpha_boost=`{settings.get('screen_error_material_alpha_boost')}`",
        "- Low-coverage rescue scale: "
        f"face_limit_boost=`{settings.get('low_coverage_rescue_face_limit_boost')}`, "
        f"alpha_tighten=`{settings.get('low_coverage_rescue_alpha_tighten')}`, "
        f"reflectance_boost=`{settings.get('low_coverage_rescue_reflectance_boost')}`, "
        f"transmittance_boost=`{settings.get('low_coverage_rescue_transmittance_boost')}`",
        f"- Use current water shape: `{settings.get('use_current_water_shape')}`",
        f"- Response shape ID prefix: `{settings.get('response_shape_id_prefix')}`",
        f"- Response BSDF ID prefix: `{settings.get('response_bsdf_id_prefix')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Empty mask frames ignored: `{checks.get('empty_mask_frames_ignored')}`",
        f"- Candidate faces: `{checks.get('candidate_faces')}`",
        f"- Response faces: `{checks.get('response_faces')}`",
        f"- Remainder faces: `{checks.get('remainder_faces')}`",
        f"- Water shape replacements: `{checks.get('water_shape_replacements')}`",
        f"- Response BSDF insertions: `{checks.get('response_bsdf_insertions')}`",
        f"- Coverage-control attenuated frames: `{checks.get('coverage_control_attenuated_frames')}`",
        f"- Coverage-control max attenuation: `{checks.get('coverage_control_max_attenuation')}`",
        f"- Low-coverage rescue frames: `{checks.get('low_coverage_rescue_frames')}`",
        f"- Low-coverage max rescue: `{checks.get('low_coverage_max_rescue')}`",
        f"- Coverage-band rescue frames: `{checks.get('coverage_band_rescue_frames')}`",
        f"- Coverage-band max rescue: `{checks.get('coverage_band_max_rescue')}`",
        f"- Screen-region attenuated frames: `{checks.get('screen_region_attenuated_frames')}`",
        f"- Screen-region candidate faces: `{checks.get('screen_region_candidate_faces')}`",
        f"- Screen-region dropped faces: `{checks.get('screen_region_dropped_faces')}`",
        f"- Screen-region max drop fraction: `{checks.get('screen_region_max_drop_fraction')}`",
        f"- Screen-error attenuated frames: `{checks.get('screen_error_attenuated_frames')}`",
        f"- Screen-error sampled faces: `{checks.get('screen_error_sampled_faces')}`",
        f"- Screen-error candidate faces: `{checks.get('screen_error_candidate_faces')}`",
        f"- Screen-error dropped faces: `{checks.get('screen_error_dropped_faces')}`",
        f"- Screen-error max drop fraction: `{checks.get('screen_error_max_drop_fraction')}`",
        f"- Screen-error material attenuated frames: `{checks.get('screen_error_material_attenuated_frames')}`",
        f"- Screen-error material sampled faces: `{checks.get('screen_error_material_sampled_faces')}`",
        f"- Screen-error material candidate faces: `{checks.get('screen_error_material_candidate_faces')}`",
        f"- Screen-error material attenuated faces: `{checks.get('screen_error_material_attenuated_faces')}`",
        f"- Screen-error material min scale: `{checks.get('screen_error_material_min_scale')}`",
        f"- Screen-error material mean scale: `{checks.get('screen_error_material_mean_scale')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Coverage | Atten | Low Rescue | Band Rescue | Region Drop | Error Drop | Material Faces | Limit | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("water_mask_material_response") or {}
        control = item.get("coverage_control") or {}
        region = control.get("screen_region_attenuation") or {}
        error = control.get("screen_error_attenuation") or {}
        material = control.get("screen_error_material_attenuation") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {control.get('layer_coverage')} | "
            f"{control.get('attenuation')} | {control.get('low_coverage_rescue')} | "
            f"{control.get('coverage_band_rescue')} | "
            f"{region.get('dropped_faces')} | "
            f"{error.get('dropped_faces')} | "
            f"{material.get('attenuated_faces')} | "
            f"{control.get('effective_face_limit')} | "
            f"{item.get('water_faces')} | "
            f"{item.get('response_faces')} | {item.get('remainder_faces')} | "
            f"`{item.get('mask_layer_repo_path')}` | `{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def split_material(args):
    require_pillow()
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    mask_source_path = require_file(args.mask_source, "mask source")
    base = read_json(base_export_path)
    mask_source = read_json(mask_source_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if mask_source.get("schema") not in MASK_SCHEMAS:
        expected = ", ".join(sorted(MASK_SCHEMAS))
        raise SystemExit(f"{args.mask_source}: expected one of {expected}")
    if mask_source.get("status") and mask_source.get("status") != "ready":
        raise SystemExit(f"{args.mask_source}: mask source status is {mask_source.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    mesh_dir = os.path.join(out_dir, "meshes")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)
    os.makedirs(mesh_dir, exist_ok=True)

    mask_frames = output_frame_map(mask_source.get("frames") or [])
    screen_error_frames, screen_error_source = screen_error_frame_map(args, root)
    bin_specs = resolved_bin_specs(args)
    frames = []
    failures = []
    totals = {
        "xml_scene_bytes": 0,
        "candidate_faces": 0,
        "empty_mask_frames_ignored": 0,
        "response_faces": 0,
        "response_vertices": 0,
        "response_bytes": 0,
        "remainder_faces": 0,
        "remainder_vertices": 0,
        "remainder_bytes": 0,
        "water_shape_replacements": 0,
        "response_bsdf_insertions": 0,
        "coverage_control_attenuated_frames": 0,
        "coverage_control_max_attenuation": 0.0,
        "low_coverage_rescue_frames": 0,
        "low_coverage_max_rescue": 0.0,
        "coverage_band_rescue_frames": 0,
        "coverage_band_max_rescue": 0.0,
        "screen_region_attenuated_frames": 0,
        "screen_region_candidate_faces": 0,
        "screen_region_dropped_faces": 0,
        "screen_region_max_drop_fraction": 0.0,
        "screen_error_attenuated_frames": 0,
        "screen_error_sampled_faces": 0,
        "screen_error_candidate_faces": 0,
        "screen_error_dropped_faces": 0,
        "screen_error_max_drop_fraction": 0.0,
        "screen_error_material_attenuated_frames": 0,
        "screen_error_material_sampled_faces": 0,
        "screen_error_material_candidate_faces": 0,
        "screen_error_material_attenuated_faces": 0,
        "screen_error_material_min_scale": 1.0,
        "screen_error_material_mean_scale": 1.0,
        "screen_error_material_scale_sum": 0.0,
    }
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        water_mesh = resolve_path(((frame.get("water_mesh") or {}).get("path") or (frame.get("water_mesh") or {}).get("repo_path")))
        xml_text = None
        if source_xml and os.path.isfile(source_xml):
            with open(source_xml, encoding="utf-8") as f:
                xml_text = f.read()
            if args.use_current_water_shape:
                current_mesh = current_water_shape_mesh(xml_text)
                if current_mesh:
                    water_mesh = current_mesh
        mask_frame = mask_frames.get(output_frame)
        mask_path = resolve_path(mask_layer_ref(mask_frame))
        source_path = resolve_path((mask_frame or {}).get("source_path") or (mask_frame or {}).get("source_repo_path"))
        missing = []
        for role, path in (("source_xml", source_xml), ("water_mesh", water_mesh), ("mask_layer", mask_path)):
            if not path or not os.path.isfile(path):
                missing.append({"role": role, "path": path})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        vertices, faces = read_obj_mesh(water_mesh)
        frame_control = coverage_control(mask_frame, args)
        frame_args = copy.copy(args)
        frame_args.face_limit = frame_control["effective_face_limit"]
        from PIL import Image

        mask = load_mask_luma(mask_path)
        source = Image.open(source_path).convert("RGB") if source_path and os.path.isfile(source_path) else None
        camera = parse_camera(source_xml)
        selected = select_faces(vertices, faces, camera, mask, source, frame_args)
        selected, screen_region = apply_screen_region_attenuation(
            selected,
            mask.size[0],
            mask.size[1],
            output_frame,
            mask_frame,
            args,
        )
        frame_control["screen_region_attenuation"] = screen_region
        selected, screen_error_material = apply_screen_error_material_attenuation(
            selected,
            output_frame,
            mask_frame,
            screen_error_frames,
            args,
        )
        frame_control["screen_error_material_attenuation"] = screen_error_material
        selected, screen_error = apply_screen_error_attenuation(
            selected,
            output_frame,
            mask_frame,
            screen_error_frames,
            args,
        )
        frame_control["screen_error_attenuation"] = screen_error
        if not selected:
            if args.allow_empty_mask_frames:
                patched = add_response_comment(
                    xml_text,
                    f"<!-- S421 water_mask_material_response empty mask source_faces={len(faces)} -->",
                )
                xml_out = os.path.join(scene_dir, f"frame_{index:04d}.xml")
                write_text(xml_out, patched)
                totals["xml_scene_bytes"] += os.path.getsize(xml_out)
                totals["empty_mask_frames_ignored"] += 1
                out_frame = copy.deepcopy(frame)
                out_frame["xml_scene"] = {
                    "path": xml_out,
                    "repo_path": posix_rel(xml_out, root),
                    "sha256": sha256_file(xml_out),
                    "size": os.path.getsize(xml_out),
                }
                expected = os.path.join(render_dir, f"frame_{index:04d}.exr")
                out_frame["expected_output"] = {
                    "path": expected,
                    "repo_path": posix_rel(expected, root),
                }
                out_frame["water_mask_material_response"] = {
                    "enabled": False,
                    "empty_mask_frame_ignored": True,
                    "water_mesh_repo_path": posix_rel(water_mesh, root),
                    "mask_layer_path": mask_path,
                    "mask_layer_repo_path": posix_rel(mask_path, root),
                    "source_repo_path": posix_rel(source_path, root) if source_path else None,
                    "water_vertices": len(vertices),
                    "water_faces": len(faces),
                    "candidate_faces": 0,
                    "response_faces": 0,
                    "remainder_faces": len(faces),
                    "coverage_control": frame_control,
                }
                frames.append(out_frame)
                continue
            failures.append({"output_frame": output_frame, "missing": [{"role": "selected_faces", "path": None}]})
            continue
        remainder = remainder_faces(vertices, faces, selected)
        if not remainder:
            failures.append({"output_frame": output_frame, "missing": [{"role": "remainder_faces", "path": None}]})
            continue

        base_name = f"frame_{index:04d}"
        remainder_mesh = os.path.join(mesh_dir, f"{base_name}_water_remainder.obj")
        response_shapes = []
        response_bins = []
        frame_bin_specs = resolved_bin_specs(args, frame_control)
        frame_partitions = partition_selected_faces(selected, frame_bin_specs, args)
        for bin_item in frame_partitions:
            spec = bin_item["spec"]
            bin_selected = bin_item["faces"]
            suffix = "" if len(frame_partitions) == 1 else f"_bin{spec['index']:02d}"
            response_mesh = os.path.join(mesh_dir, f"{base_name}_water_mask_material{suffix}.obj")
            response_stats = write_selected_obj(response_mesh, vertices, bin_selected, args.response_y_lift, args.reverse_faces)
            response_shapes.append({
                "bin_index": spec["index"],
                "mesh_path": response_mesh,
                "bsdf_id": spec["bsdf_id"],
            })
            response_bins.append({
                "bin_index": spec["index"],
                "bsdf_id": spec["bsdf_id"],
                "response_mesh_repo_path": posix_rel(response_mesh, root),
                "response_mesh_sha256": sha256_file(response_mesh),
                "faces": response_stats["faces"],
                "vertices": response_stats["vertices"],
                "bytes": response_stats["bytes"],
                "alpha": spec["alpha"],
                "specular_reflectance": spec["specular_reflectance"],
                "specular_transmittance": spec["specular_transmittance"],
                "screen_error_material_scale": spec.get("screen_error_material_scale", 1.0),
                "source_bin_index": spec.get("source_bin_index"),
                "face_samples": [
                    {
                        "centroid": [float(v) for v in item["centroid"]],
                        "screen": [float(item["screen"][0]), float(item["screen"][1])],
                        "depth": float(item["depth"]),
                        "mask_value": int(item["mask_value"]),
                        "source_luma": item["source_luma"],
                    }
                    for item in bin_selected[:4]
                ],
            })
            totals["response_faces"] += response_stats["faces"]
            totals["response_vertices"] += response_stats["vertices"]
            totals["response_bytes"] += response_stats["bytes"]
        remainder_stats = write_selected_obj(remainder_mesh, vertices, remainder, 0.0, args.reverse_faces)

        bsdf_blocks = "\n".join(
            response_bsdf_block(
                args,
                bin_item["spec"]["bsdf_id"],
                bin_item["spec"]["alpha"],
                bin_item["spec"]["specular_reflectance"],
                bin_item["spec"]["specular_transmittance"],
            )
            for bin_item in frame_partitions
        )
        patched, count = insert_response_bsdf(xml_text, bsdf_blocks)
        totals["response_bsdf_insertions"] += count
        patched, count = replace_water_shape(patched, water_mesh, remainder_mesh, response_shapes, index, args)
        totals["water_shape_replacements"] += count
        patched = add_response_comment(
            patched,
            f"<!-- S421 water_mask_material_response faces={len(selected)} source_faces={len(faces)} -->",
        )

        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["candidate_faces"] += len(selected)
        totals["remainder_faces"] += remainder_stats["faces"]
        totals["remainder_vertices"] += remainder_stats["vertices"]
        totals["remainder_bytes"] += remainder_stats["bytes"]
        if frame_control["attenuation"] > 0.0:
            totals["coverage_control_attenuated_frames"] += 1
        totals["coverage_control_max_attenuation"] = max(
            totals["coverage_control_max_attenuation"],
            frame_control["attenuation"],
        )
        if frame_control["low_coverage_rescue"] > 0.0:
            totals["low_coverage_rescue_frames"] += 1
        totals["low_coverage_max_rescue"] = max(
            totals["low_coverage_max_rescue"],
            frame_control["low_coverage_rescue"],
        )
        if frame_control["coverage_band_rescue"] > 0.0:
            totals["coverage_band_rescue_frames"] += 1
        totals["coverage_band_max_rescue"] = max(
            totals["coverage_band_max_rescue"],
            frame_control["coverage_band_rescue"],
        )
        screen_region = frame_control.get("screen_region_attenuation") or {}
        totals["screen_region_candidate_faces"] += int(screen_region.get("candidate_faces") or 0)
        totals["screen_region_dropped_faces"] += int(screen_region.get("dropped_faces") or 0)
        if int(screen_region.get("dropped_faces") or 0) > 0:
            totals["screen_region_attenuated_frames"] += 1
        totals["screen_region_max_drop_fraction"] = max(
            totals["screen_region_max_drop_fraction"],
            float(screen_region.get("drop_fraction") or 0.0),
        )
        screen_error = frame_control.get("screen_error_attenuation") or {}
        totals["screen_error_sampled_faces"] += int(screen_error.get("sampled_faces") or 0)
        totals["screen_error_candidate_faces"] += int(screen_error.get("candidate_faces") or 0)
        totals["screen_error_dropped_faces"] += int(screen_error.get("dropped_faces") or 0)
        if int(screen_error.get("dropped_faces") or 0) > 0:
            totals["screen_error_attenuated_frames"] += 1
        totals["screen_error_max_drop_fraction"] = max(
            totals["screen_error_max_drop_fraction"],
            float(screen_error.get("drop_fraction") or 0.0),
        )
        screen_error_material = frame_control.get("screen_error_material_attenuation") or {}
        material_faces = int(screen_error_material.get("attenuated_faces") or 0)
        totals["screen_error_material_sampled_faces"] += int(screen_error_material.get("sampled_faces") or 0)
        totals["screen_error_material_candidate_faces"] += int(screen_error_material.get("candidate_faces") or 0)
        totals["screen_error_material_attenuated_faces"] += material_faces
        if material_faces > 0:
            totals["screen_error_material_attenuated_frames"] += 1
            totals["screen_error_material_min_scale"] = min(
                totals["screen_error_material_min_scale"],
                float(screen_error_material.get("min_applied_scale") or 1.0),
            )
            totals["screen_error_material_scale_sum"] += (
                float(screen_error_material.get("mean_scale") or 1.0) * material_faces
            )
            totals["screen_error_material_mean_scale"] = (
                totals["screen_error_material_scale_sum"]
                / float(max(1, totals["screen_error_material_attenuated_faces"]))
            )

        out_frame = copy.deepcopy(frame)
        out_frame["xml_scene"] = {
            "path": xml_out,
            "repo_path": posix_rel(xml_out, root),
            "sha256": sha256_file(xml_out),
            "size": os.path.getsize(xml_out),
        }
        expected = os.path.join(render_dir, f"{base_name}.exr")
        out_frame["expected_output"] = {
            "path": expected,
            "repo_path": posix_rel(expected, root),
        }
        out_frame["water_mask_material_response"] = {
            "enabled": True,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "response_mesh_repo_path": response_bins[0]["response_mesh_repo_path"] if len(response_bins) == 1 else None,
            "remainder_mesh_repo_path": posix_rel(remainder_mesh, root),
            "response_mesh_sha256": response_bins[0]["response_mesh_sha256"] if len(response_bins) == 1 else None,
            "remainder_mesh_sha256": sha256_file(remainder_mesh),
            "mask_layer_path": mask_path,
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "source_repo_path": posix_rel(source_path, root) if source_path else None,
            "water_vertices": len(vertices),
            "water_faces": len(faces),
            "candidate_faces": len(selected),
            "response_faces": sum(item["faces"] for item in response_bins),
            "response_vertices": sum(item["vertices"] for item in response_bins),
            "response_bytes": sum(item["bytes"] for item in response_bins),
            "response_bins": response_bins,
            "coverage_control": frame_control,
            "remainder_faces": remainder_stats["faces"],
            "remainder_vertices": remainder_stats["vertices"],
            "remainder_bytes": remainder_stats["bytes"],
            "face_samples": [
                {
                    "centroid": [float(v) for v in item["centroid"]],
                    "screen": [float(item["screen"][0]), float(item["screen"][1])],
                    "depth": float(item["depth"]),
                    "mask_value": int(item["mask_value"]),
                    "source_luma": item["source_luma"],
                }
                for item in selected[:8]
            ],
        }
        frames.append(out_frame)

    command_list = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_command_list(
        command_list,
        frames,
        (base.get("render_settings") or {}).get("mitsuba_command") or "mitsuba",
        (base.get("render_settings") or {}).get("mitsuba_mode"),
    )
    export = copy.deepcopy(base)
    export.update({
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if frames and not failures and totals["response_faces"] > 0 else "review",
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "mask_source": source_entry(mask_source_path, root, "water highlight mask source", mask_source),
            "screen_error_gap": screen_error_source,
        },
        "frames": frames,
        "failures": failures,
        "water_mask_material_response": {
            "enabled": True,
            "face_limit": args.face_limit,
            "face_stride": args.face_stride,
            "response_bin_count": args.response_bin_count,
            "response_bin_alpha_strong": args.response_bin_alpha_strong,
            "response_bin_alpha_weak": args.response_bin_alpha_weak,
            "response_bin_specular_reflectance_strong": args.response_bin_specular_reflectance_strong_vec,
            "response_bin_specular_reflectance_weak": args.response_bin_specular_reflectance_weak_vec,
            "response_bin_specular_transmittance_strong": args.response_bin_specular_transmittance_strong_vec,
            "response_bin_specular_transmittance_weak": args.response_bin_specular_transmittance_weak_vec,
            "response_bin_specs": bin_specs,
            "response_alpha": args.response_alpha,
            "response_y_lift": args.response_y_lift,
            "distribution": args.distribution,
            "int_ior": args.int_ior,
            "ext_ior": args.ext_ior,
            "response_specular_reflectance": args.response_specular_reflectance_vec,
            "response_specular_transmittance": args.response_specular_transmittance_vec,
            "reverse_faces": args.reverse_faces,
            "mask_threshold": args.mask_threshold,
            "mask_sample_radius": args.mask_sample_radius,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
            "coverage_attenuation_strength": args.coverage_attenuation_strength,
            "coverage_attenuation_pivot": args.coverage_attenuation_pivot,
            "coverage_attenuation_width": args.coverage_attenuation_width,
            "coverage_attenuation_max": args.coverage_attenuation_max,
            "coverage_alpha_boost": args.coverage_alpha_boost,
            "coverage_reflectance_attenuation": args.coverage_reflectance_attenuation,
            "coverage_transmittance_attenuation": args.coverage_transmittance_attenuation,
            "low_coverage_rescue_strength": args.low_coverage_rescue_strength,
            "low_coverage_rescue_pivot": args.low_coverage_rescue_pivot,
            "low_coverage_rescue_width": args.low_coverage_rescue_width,
            "coverage_band_rescue_strength": args.coverage_band_rescue_strength,
            "coverage_band_rescue_center": args.coverage_band_rescue_center,
            "coverage_band_rescue_width": args.coverage_band_rescue_width,
            "screen_region_attenuation_strength": args.screen_region_attenuation_strength,
            "screen_region_x_min": args.screen_region_x_min,
            "screen_region_x_max": args.screen_region_x_max,
            "screen_region_y_min": args.screen_region_y_min,
            "screen_region_y_max": args.screen_region_y_max,
            "screen_region_coverage_min": args.screen_region_coverage_min,
            "screen_region_coverage_max": args.screen_region_coverage_max,
            "screen_region_output_min": args.screen_region_output_min,
            "screen_region_output_max": args.screen_region_output_max,
            "screen_error_gap_summary": (screen_error_source or {}).get("repo_path"),
            "screen_error_attenuation_strength": args.screen_error_attenuation_strength,
            "screen_error_negative_threshold": args.screen_error_negative_threshold,
            "screen_error_negative_width": args.screen_error_negative_width,
            "screen_error_sample_radius": args.screen_error_sample_radius,
            "screen_error_max_drop_fraction": args.screen_error_max_drop_fraction,
            "screen_error_coverage_min": args.screen_error_coverage_min,
            "screen_error_coverage_max": args.screen_error_coverage_max,
            "screen_error_output_min": args.screen_error_output_min,
            "screen_error_output_max": args.screen_error_output_max,
            "screen_error_material_attenuation_strength": args.screen_error_material_attenuation_strength,
            "screen_error_material_min_scale": args.screen_error_material_min_scale,
            "screen_error_material_alpha_boost": args.screen_error_material_alpha_boost,
            "low_coverage_rescue_face_limit_boost": args.low_coverage_rescue_face_limit_boost,
            "low_coverage_rescue_alpha_tighten": args.low_coverage_rescue_alpha_tighten,
            "low_coverage_rescue_reflectance_boost": args.low_coverage_rescue_reflectance_boost,
            "low_coverage_rescue_transmittance_boost": args.low_coverage_rescue_transmittance_boost,
            "allow_empty_mask_frames": args.allow_empty_mask_frames,
            "use_current_water_shape": args.use_current_water_shape,
            "response_shape_id_prefix": args.response_shape_id_prefix,
            "remainder_shape_id_prefix": args.remainder_shape_id_prefix,
            "response_bsdf_id_prefix": args.response_bsdf_id_prefix,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["water_mask_material_response_enabled"] = True
    export["checks"] = copy.deepcopy(base.get("checks") or {})
    export["checks"].update({
        "frames_exported": len(frames),
        "missing_references": len(failures),
        **totals,
    })

    export_path = os.path.join(out_dir, "mitsuba_export.json")
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root, args.next))
    print(
        f"status={export['status']} frames={len(frames)} "
        f"response_faces={totals['response_faces']} remainder_faces={totals['remainder_faces']} "
        f"export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Split original water mesh faces into a localized Mitsuba material response")
    parser.add_argument("base_export")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--face-limit", type=int, default=0)
    parser.add_argument("--face-stride", type=int, default=1)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--mask-sample-radius", type=int, default=5)
    parser.add_argument("--source-luma-min", type=float, default=0.0)
    parser.add_argument("--source-luma-max", type=float, default=255.0)
    parser.add_argument("--coverage-attenuation-strength", type=float, default=0.0)
    parser.add_argument("--coverage-attenuation-pivot", type=float, default=0.12)
    parser.add_argument("--coverage-attenuation-width", type=float, default=0.08)
    parser.add_argument("--coverage-attenuation-max", type=float, default=0.35)
    parser.add_argument("--coverage-alpha-boost", type=float, default=0.0)
    parser.add_argument("--coverage-reflectance-attenuation", type=float, default=0.0)
    parser.add_argument("--coverage-transmittance-attenuation", type=float, default=0.0)
    parser.add_argument("--low-coverage-rescue-strength", type=float, default=0.0)
    parser.add_argument("--low-coverage-rescue-pivot", type=float, default=0.07)
    parser.add_argument("--low-coverage-rescue-width", type=float, default=0.02)
    parser.add_argument("--coverage-band-rescue-strength", type=float, default=0.0)
    parser.add_argument("--coverage-band-rescue-center", type=float, default=0.113)
    parser.add_argument("--coverage-band-rescue-width", type=float, default=0.004)
    parser.add_argument("--screen-region-attenuation-strength", type=float, default=0.0)
    parser.add_argument("--screen-region-x-min", type=float, default=0.0)
    parser.add_argument("--screen-region-x-max", type=float, default=1.0)
    parser.add_argument("--screen-region-y-min", type=float, default=0.0)
    parser.add_argument("--screen-region-y-max", type=float, default=1.0)
    parser.add_argument("--screen-region-coverage-min", type=float, default=0.0)
    parser.add_argument("--screen-region-coverage-max", type=float, default=1.0)
    parser.add_argument("--screen-region-output-min", type=int, default=-1)
    parser.add_argument("--screen-region-output-max", type=int, default=-1)
    parser.add_argument("--screen-error-gap-summary")
    parser.add_argument("--screen-error-attenuation-strength", type=float, default=0.0)
    parser.add_argument("--screen-error-negative-threshold", type=float, default=8.0)
    parser.add_argument("--screen-error-negative-width", type=float, default=48.0)
    parser.add_argument("--screen-error-sample-radius", type=int, default=0)
    parser.add_argument("--screen-error-max-drop-fraction", type=float, default=0.15)
    parser.add_argument("--screen-error-coverage-min", type=float, default=0.0)
    parser.add_argument("--screen-error-coverage-max", type=float, default=1.0)
    parser.add_argument("--screen-error-output-min", type=int, default=-1)
    parser.add_argument("--screen-error-output-max", type=int, default=-1)
    parser.add_argument("--screen-error-material-attenuation-strength", type=float, default=0.0)
    parser.add_argument("--screen-error-material-min-scale", type=float, default=0.25)
    parser.add_argument("--screen-error-material-alpha-boost", type=float, default=0.0)
    parser.add_argument("--low-coverage-rescue-face-limit-boost", type=float, default=0.0)
    parser.add_argument("--low-coverage-rescue-alpha-tighten", type=float, default=0.0)
    parser.add_argument("--low-coverage-rescue-reflectance-boost", type=float, default=0.0)
    parser.add_argument("--low-coverage-rescue-transmittance-boost", type=float, default=0.0)
    parser.add_argument("--response-alpha", type=float, default=0.006)
    parser.add_argument("--response-bin-count", type=int, default=1)
    parser.add_argument("--response-bin-alpha-strong", type=float)
    parser.add_argument("--response-bin-alpha-weak", type=float)
    parser.add_argument("--response-y-lift", type=float, default=0.0)
    parser.add_argument("--distribution", choices=["ggx", "beckmann", "none"], default="ggx")
    parser.add_argument("--int-ior", type=float, default=1.333)
    parser.add_argument("--ext-ior", type=float, default=1.0)
    parser.add_argument("--response-specular-reflectance")
    parser.add_argument("--response-specular-transmittance")
    parser.add_argument("--response-bin-specular-reflectance-strong")
    parser.add_argument("--response-bin-specular-reflectance-weak")
    parser.add_argument("--response-bin-specular-transmittance-strong")
    parser.add_argument("--response-bin-specular-transmittance-weak")
    parser.add_argument("--response-shape-id-prefix", default="lsfs_s421_water_mask_material")
    parser.add_argument("--remainder-shape-id-prefix", default="lsfs_s421_water_remainder")
    parser.add_argument("--response-bsdf-id-prefix", default=RESPONSE_BSDF_ID)
    parser.add_argument("--allow-empty-mask-frames", action="store_true")
    parser.add_argument("--use-current-water-shape", action="store_true")
    parser.add_argument("--reverse-faces", action="store_true")
    parser.add_argument("--depth-penalty", type=float, default=0.01)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S421 Mitsuba Water Mask Material Split")
    parser.add_argument("--next", default="Render and compare this split-water material response against S420, S417, S409, and S401.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.face_limit < 0:
        parser.error("face-limit must be non-negative")
    if args.face_stride <= 0:
        parser.error("face-stride must be positive")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.mask_sample_radius < 0:
        parser.error("mask-sample-radius must be non-negative")
    if args.source_luma_min < 0.0 or args.source_luma_max > 255.0:
        parser.error("source luma bounds must be in [0, 255]")
    if args.source_luma_min > args.source_luma_max:
        parser.error("source-luma-min cannot exceed source-luma-max")
    if args.coverage_attenuation_strength < 0.0:
        parser.error("coverage-attenuation-strength must be non-negative")
    if args.coverage_attenuation_pivot < 0.0:
        parser.error("coverage-attenuation-pivot must be non-negative")
    if args.coverage_attenuation_width <= 0.0:
        parser.error("coverage-attenuation-width must be positive")
    if args.coverage_attenuation_max < 0.0 or args.coverage_attenuation_max > 1.0:
        parser.error("coverage-attenuation-max must be in [0, 1]")
    if args.coverage_alpha_boost < 0.0:
        parser.error("coverage-alpha-boost must be non-negative")
    if args.coverage_reflectance_attenuation < 0.0 or args.coverage_reflectance_attenuation > 1.0:
        parser.error("coverage-reflectance-attenuation must be in [0, 1]")
    if args.coverage_transmittance_attenuation < 0.0 or args.coverage_transmittance_attenuation > 1.0:
        parser.error("coverage-transmittance-attenuation must be in [0, 1]")
    if args.low_coverage_rescue_strength < 0.0:
        parser.error("low-coverage-rescue-strength must be non-negative")
    if args.low_coverage_rescue_pivot < 0.0:
        parser.error("low-coverage-rescue-pivot must be non-negative")
    if args.low_coverage_rescue_width <= 0.0:
        parser.error("low-coverage-rescue-width must be positive")
    if args.coverage_band_rescue_strength < 0.0:
        parser.error("coverage-band-rescue-strength must be non-negative")
    if args.coverage_band_rescue_center < 0.0:
        parser.error("coverage-band-rescue-center must be non-negative")
    if args.coverage_band_rescue_width <= 0.0:
        parser.error("coverage-band-rescue-width must be positive")
    if args.screen_region_attenuation_strength < 0.0 or args.screen_region_attenuation_strength > 1.0:
        parser.error("screen-region-attenuation-strength must be in [0, 1]")
    for label, value in (
        ("screen-region-x-min", args.screen_region_x_min),
        ("screen-region-x-max", args.screen_region_x_max),
        ("screen-region-y-min", args.screen_region_y_min),
        ("screen-region-y-max", args.screen_region_y_max),
        ("screen-region-coverage-min", args.screen_region_coverage_min),
        ("screen-region-coverage-max", args.screen_region_coverage_max),
    ):
        if value < 0.0 or value > 1.0:
            parser.error(f"{label} must be in [0, 1]")
    if args.screen_region_x_min > args.screen_region_x_max:
        parser.error("screen-region-x-min cannot exceed screen-region-x-max")
    if args.screen_region_y_min > args.screen_region_y_max:
        parser.error("screen-region-y-min cannot exceed screen-region-y-max")
    if args.screen_region_coverage_min > args.screen_region_coverage_max:
        parser.error("screen-region-coverage-min cannot exceed screen-region-coverage-max")
    if (
        args.screen_region_output_min >= 0
        and args.screen_region_output_max >= 0
        and args.screen_region_output_min > args.screen_region_output_max
    ):
        parser.error("screen-region-output-min cannot exceed screen-region-output-max")
    if args.screen_error_attenuation_strength < 0.0 or args.screen_error_attenuation_strength > 1.0:
        parser.error("screen-error-attenuation-strength must be in [0, 1]")
    if args.screen_error_negative_threshold < 0.0:
        parser.error("screen-error-negative-threshold must be non-negative")
    if args.screen_error_negative_width <= 0.0:
        parser.error("screen-error-negative-width must be positive")
    if args.screen_error_sample_radius < 0:
        parser.error("screen-error-sample-radius must be non-negative")
    if args.screen_error_max_drop_fraction < 0.0 or args.screen_error_max_drop_fraction > 1.0:
        parser.error("screen-error-max-drop-fraction must be in [0, 1]")
    for label, value in (
        ("screen-error-coverage-min", args.screen_error_coverage_min),
        ("screen-error-coverage-max", args.screen_error_coverage_max),
    ):
        if value < 0.0 or value > 1.0:
            parser.error(f"{label} must be in [0, 1]")
    if args.screen_error_coverage_min > args.screen_error_coverage_max:
        parser.error("screen-error-coverage-min cannot exceed screen-error-coverage-max")
    if (
        args.screen_error_output_min >= 0
        and args.screen_error_output_max >= 0
        and args.screen_error_output_min > args.screen_error_output_max
    ):
        parser.error("screen-error-output-min cannot exceed screen-error-output-max")
    if args.screen_error_material_attenuation_strength < 0.0 or args.screen_error_material_attenuation_strength > 1.0:
        parser.error("screen-error-material-attenuation-strength must be in [0, 1]")
    if args.screen_error_material_min_scale < 0.0 or args.screen_error_material_min_scale > 1.0:
        parser.error("screen-error-material-min-scale must be in [0, 1]")
    if args.screen_error_material_alpha_boost < 0.0:
        parser.error("screen-error-material-alpha-boost must be non-negative")
    if args.low_coverage_rescue_face_limit_boost < 0.0:
        parser.error("low-coverage-rescue-face-limit-boost must be non-negative")
    if args.low_coverage_rescue_alpha_tighten < 0.0 or args.low_coverage_rescue_alpha_tighten > 1.0:
        parser.error("low-coverage-rescue-alpha-tighten must be in [0, 1]")
    if args.low_coverage_rescue_reflectance_boost < 0.0:
        parser.error("low-coverage-rescue-reflectance-boost must be non-negative")
    if args.low_coverage_rescue_transmittance_boost < 0.0:
        parser.error("low-coverage-rescue-transmittance-boost must be non-negative")
    if args.response_alpha <= 0.0:
        parser.error("response-alpha must be positive")
    if args.response_bin_count <= 0:
        parser.error("response-bin-count must be positive")
    if args.response_bin_alpha_strong is not None and args.response_bin_alpha_strong <= 0.0:
        parser.error("response-bin-alpha-strong must be positive")
    if args.response_bin_alpha_weak is not None and args.response_bin_alpha_weak <= 0.0:
        parser.error("response-bin-alpha-weak must be positive")
    if args.response_y_lift < 0.0:
        parser.error("response-y-lift must be non-negative")
    if args.int_ior <= 0.0 or args.ext_ior <= 0.0:
        parser.error("int-ior and ext-ior must be positive")
    if args.depth_penalty < 0.0:
        parser.error("depth-penalty must be non-negative")
    args.response_specular_reflectance_vec = None
    args.response_specular_transmittance_vec = None
    args.response_bin_specular_reflectance_strong_vec = None
    args.response_bin_specular_reflectance_weak_vec = None
    args.response_bin_specular_transmittance_strong_vec = None
    args.response_bin_specular_transmittance_weak_vec = None
    if args.response_specular_reflectance:
        args.response_specular_reflectance_vec = parse_vec3(args.response_specular_reflectance, "response-specular-reflectance")
    if args.response_specular_transmittance:
        args.response_specular_transmittance_vec = parse_vec3(args.response_specular_transmittance, "response-specular-transmittance")
    if args.response_bin_specular_reflectance_strong:
        args.response_bin_specular_reflectance_strong_vec = parse_vec3(
            args.response_bin_specular_reflectance_strong,
            "response-bin-specular-reflectance-strong",
        )
    if args.response_bin_specular_reflectance_weak:
        args.response_bin_specular_reflectance_weak_vec = parse_vec3(
            args.response_bin_specular_reflectance_weak,
            "response-bin-specular-reflectance-weak",
        )
    if args.response_bin_specular_transmittance_strong:
        args.response_bin_specular_transmittance_strong_vec = parse_vec3(
            args.response_bin_specular_transmittance_strong,
            "response-bin-specular-transmittance-strong",
        )
    if args.response_bin_specular_transmittance_weak:
        args.response_bin_specular_transmittance_weak_vec = parse_vec3(
            args.response_bin_specular_transmittance_weak,
            "response-bin-specular-transmittance-weak",
        )
    for label, vec in (
        ("response-specular-reflectance", args.response_specular_reflectance_vec),
        ("response-specular-transmittance", args.response_specular_transmittance_vec),
        ("response-bin-specular-reflectance-strong", args.response_bin_specular_reflectance_strong_vec),
        ("response-bin-specular-reflectance-weak", args.response_bin_specular_reflectance_weak_vec),
        ("response-bin-specular-transmittance-strong", args.response_bin_specular_transmittance_strong_vec),
        ("response-bin-specular-transmittance-weak", args.response_bin_specular_transmittance_weak_vec),
    ):
        if vec is not None and min(vec) < 0.0:
            parser.error(f"{label} values must be non-negative")
        if vec is not None and max(vec) > 1.0:
            parser.error(f"{label} values must be in [0, 1]")
    split_material(args)


if __name__ == "__main__":
    main()
