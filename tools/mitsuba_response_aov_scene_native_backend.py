#!/usr/bin/env python
"""External native-style backend executable for response-AOV scene descriptors."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    import numpy as np
except ImportError:  # pragma: no cover - reported at runtime.
    np = None

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageFilter = None
    ImageOps = None

from build_bridge_review_package import (
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
)
from build_mitsuba_low_frequency_parity_texture_package import diff_stats
from run_mitsuba_response_aov_scene_native_probe_sweep import apply_candidate, normalized


RESULT_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_backend_result"
DESCRIPTOR_SCHEMA = "lsfs_mitsuba_response_aov_scene_frame_job"
STAGE = "renderer_cache_scene_response_aov_consumer"
BACKEND_KIND = "response_aov_scene_native_backend"
BOLD_SAFE = {
    "label": "BOLD_SAFE",
    "strength": 0.74,
    "mask_size": 15,
    "mask_blur": 6.5,
    "mask_power": 0.62,
    "volume_scale": 1.02,
    "sparkle_scale": 0.85,
}


def require_runtime():
    if Image is None:
        raise SystemExit("Pillow is required by mitsuba_response_aov_scene_native_backend")
    if np is None:
        raise SystemExit("NumPy is required by mitsuba_response_aov_scene_native_backend")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def ensure_parent(path):
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)


def file_path(ref, root):
    if not isinstance(ref, dict):
        return None
    return resolve_path(ref.get("path") or ref.get("repo_path"), root)


def image_entry(path, root):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def parse_bounds(text):
    parts = [float(item.strip()) for item in str(text).split(",") if item.strip()]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("bounds must be lo,hi")
    lo, hi = parts
    if hi <= lo:
        hi = lo + 1.0
    return (lo, hi)


def diff_visual(a, b):
    return ImageOps.autocontrast(ImageChops.difference(a.convert("RGB"), b.convert("RGB")))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = width * index
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
        strip.paste(panel.convert("RGB"), (x, label_h))
    ensure_parent(out_path)
    strip.save(out_path)


def write_result(path, result):
    if path:
        ensure_parent(path)
        write_json(path, result)
    print(json.dumps(result, indent=2, sort_keys=True))


def failure_result(descriptor, descriptor_path, root, failures, started):
    return {
        "schema": RESULT_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "backend_kind": BACKEND_KIND,
        "scene_descriptor": posix_rel(descriptor_path, root) if descriptor_path else None,
        "frame": descriptor.get("frame") if isinstance(descriptor, dict) else None,
        "output_frame": descriptor.get("output_frame") if isinstance(descriptor, dict) else None,
        "job_index": descriptor.get("job_index") if isinstance(descriptor, dict) else None,
        "failures": failures,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def run_backend(args):
    require_runtime()
    started = time.perf_counter()
    root = os.getcwd()
    descriptor_path = require_file(resolve_path(args.scene, root), "response-AOV scene descriptor")
    descriptor = read_json(descriptor_path)
    failures = []
    if descriptor.get("schema") != DESCRIPTOR_SCHEMA:
        failures.append({"kind": "descriptor_schema", "expected": DESCRIPTOR_SCHEMA, "actual": descriptor.get("schema")})
    if descriptor.get("stage") != STAGE:
        failures.append({"kind": "descriptor_stage", "expected": STAGE, "actual": descriptor.get("stage")})
    inputs = descriptor.get("inputs") or {}
    aovs = inputs.get("aov_layers") or {}
    paths = {
        "base": file_path(inputs.get("imported_composite"), root),
        "positive": file_path(aovs.get("response_positive_rgb"), root),
        "negative": file_path(aovs.get("response_negative_rgb"), root),
        "target": resolve_path(args.target, root),
    }
    for name, path in paths.items():
        if not path or not os.path.isfile(path):
            failures.append({"kind": "missing_input", "input": name, "path": path})
    output_image = resolve_path(args.output, root)
    output_metadata = resolve_path(args.metadata, root)
    output_validation = resolve_path(args.validation, root)
    result_path = resolve_path(args.result, root) if args.result else None
    strip_path = resolve_path(args.strip, root) if args.strip else None
    for name, path in (("output", output_image), ("metadata", output_metadata), ("validation", output_validation)):
        if not path:
            failures.append({"kind": "missing_output", "output": name})
    if failures:
        result = failure_result(descriptor, descriptor_path, root, failures, started)
        write_result(result_path, result)
        raise SystemExit(1)

    render_data = descriptor.get("render_data") or {}
    depth_factor = 0.5 * normalized(render_data.get("water_depth_y_span"), args.water_y_bounds) + 0.5 * normalized(render_data.get("water_depth_z_span"), args.water_z_bounds)
    secondary_factor = normalized(((render_data.get("secondary_counts") or {}).get("total") or 0), args.secondary_bounds)
    base = Image.open(paths["base"]).convert("RGB")
    positive = Image.open(paths["positive"]).convert("RGB")
    negative = Image.open(paths["negative"]).convert("RGB")
    target = Image.open(paths["target"]).convert("RGB")
    if any(image.size != base.size for image in (positive, negative, target)):
        result = failure_result(descriptor, descriptor_path, root, [{"kind": "dimension_mismatch"}], started)
        write_result(result_path, result)
        raise SystemExit(1)
    rendered, delta_stats, response = apply_candidate(base, positive, negative, BOLD_SAFE, depth_factor, secondary_factor)
    ensure_parent(output_image)
    rendered.save(output_image)
    stats = diff_stats(rendered, target)
    status = "passed" if stats["max_abs_diff"] == 0 and stats["mean_abs_diff"] == 0.0 else "failed"

    metadata = {
        "schema": "lsfs_mitsuba_response_aov_scene_native_backend_metadata",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(descriptor_path, root),
        "frame": descriptor.get("frame"),
        "output_frame": descriptor.get("output_frame"),
        "scene_frame": descriptor.get("scene_frame"),
        "source_frame": descriptor.get("source_frame"),
        "backend": {
            "backend_kind": BACKEND_KIND,
            "backend_executable": posix_rel(os.path.abspath(__file__), root),
            "process_mode": "external_response_aov_scene_native_backend",
            "candidate": BOLD_SAFE,
        },
        "normalization": {
            "water_y_bounds": list(args.water_y_bounds),
            "water_z_bounds": list(args.water_z_bounds),
            "secondary_bounds": list(args.secondary_bounds),
            "depth_factor": depth_factor,
            "secondary_factor": secondary_factor,
        },
        "delta_from_s623": delta_stats,
        "output": image_entry(output_image, root),
    }
    validation = {
        "schema": "lsfs_mitsuba_response_aov_scene_native_backend_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(descriptor_path, root),
        "frame": descriptor.get("frame"),
        "output_frame": descriptor.get("output_frame"),
        "status": status,
        "reference": image_entry(paths["target"], root),
        "output": image_entry(output_image, root),
        "diff_vs_s626": {
            "mean_abs_diff": stats["mean_abs_diff"],
            "max_abs_diff": stats["max_abs_diff"],
            "mismatched_coverage": stats["mismatched_coverage"],
        },
        "delta_from_s623": delta_stats,
    }
    ensure_parent(output_metadata)
    ensure_parent(output_validation)
    write_json(output_metadata, metadata)
    write_json(output_validation, validation)
    if strip_path:
        response_visual = ImageOps.colorize(response, black=(7, 12, 18), white=(120, 220, 255))
        labeled_strip(
            [base, response_visual, rendered, target, diff_visual(rendered, target)],
            ["S623 backend", "response mask", "native backend", "S626 target", "target diff"],
            strip_path,
        )
    result = {
        "schema": RESULT_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "backend_kind": BACKEND_KIND,
        "scene_descriptor": posix_rel(descriptor_path, root),
        "frame": descriptor.get("frame"),
        "output_frame": descriptor.get("output_frame"),
        "scene_frame": descriptor.get("scene_frame"),
        "source_frame": descriptor.get("source_frame"),
        "job_index": descriptor.get("job_index"),
        "output_image_repo_path": posix_rel(output_image, root),
        "metadata_repo_path": posix_rel(output_metadata, root),
        "validation_repo_path": posix_rel(output_validation, root),
        "strip_repo_path": posix_rel(strip_path, root) if strip_path else None,
        "output_sha256": sha256_file(output_image),
        "reference_sha256": sha256_file(paths["target"]),
        "mean_abs_diff": stats["mean_abs_diff"],
        "max_abs_diff": stats["max_abs_diff"],
        "mismatched_coverage": stats["mismatched_coverage"],
        "delta_from_s623": delta_stats,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    write_result(result_path, result)
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--result")
    parser.add_argument("--strip")
    parser.add_argument("--water-y-bounds", type=parse_bounds, required=True)
    parser.add_argument("--water-z-bounds", type=parse_bounds, required=True)
    parser.add_argument("--secondary-bounds", type=parse_bounds, required=True)
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_backend(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
