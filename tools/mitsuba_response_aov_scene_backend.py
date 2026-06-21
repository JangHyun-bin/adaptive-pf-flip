#!/usr/bin/env python
"""External backend executable for response-AOV scene descriptors."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None

from build_bridge_review_package import (
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
)
from build_mitsuba_low_frequency_parity_texture_package import diff_stats


RESULT_SCHEMA = "lsfs_mitsuba_response_aov_scene_backend_result"
DESCRIPTOR_SCHEMA = "lsfs_mitsuba_response_aov_scene_frame_job"
STAGE = "renderer_cache_scene_response_aov_consumer"
BACKEND_KIND = "response_aov_scene_backend"
REQUIRED_AOVS = (
    "base_rgb",
    "response_positive_rgb",
    "response_negative_rgb",
    "selected_composite_rgb",
)
REQUIRED_SCENE_ASSETS = ("camera", "particles", "phase_cells", "water_mesh")


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required by mitsuba_response_aov_scene_backend")


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


def output_path(cli_value, output_ref, root):
    if cli_value:
        return resolve_path(cli_value, root)
    if isinstance(output_ref, dict):
        return resolve_path(output_ref.get("path") or output_ref.get("repo_path"), root)
    return None


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


def file_entry(path, root, role):
    return {
        "role": role,
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def clamp(value):
    return max(0, min(255, int(value)))


def reconstruct(base_img, positive_img, negative_img):
    base = base_img.convert("RGB").tobytes()
    positive = positive_img.convert("RGB").tobytes()
    negative = negative_img.convert("RGB").tobytes()
    out = bytearray(len(base))
    for index in range(len(base)):
        out[index] = clamp(int(base[index]) + int(positive[index]) - int(negative[index]))
    return Image.frombytes("RGB", base_img.size, bytes(out))


def layer_visual(image, gain):
    rgb = image.convert("RGB")
    if gain <= 1.0:
        return rgb
    return Image.eval(rgb, lambda value: clamp(round(value * gain)))


def diff_visual(diff_image):
    return ImageChops.multiply(diff_image.convert("RGB"), Image.new("RGB", diff_image.size, (8, 8, 8)))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        draw.rectangle((x, 0, x + width, label_h), fill=(17, 27, 35))
        draw.text((x + 8, 8), labels[index], fill=(229, 242, 248))
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


def descriptor_failures(descriptor):
    failures = []
    if descriptor.get("schema") != DESCRIPTOR_SCHEMA:
        failures.append({"kind": "descriptor_schema", "expected": DESCRIPTOR_SCHEMA, "actual": descriptor.get("schema")})
    if descriptor.get("stage") != STAGE:
        failures.append({"kind": "descriptor_stage", "expected": STAGE, "actual": descriptor.get("stage")})
    return failures


def run_backend(args):
    require_pillow()
    started = time.perf_counter()
    root = os.getcwd()
    descriptor_path = require_file(resolve_path(args.scene, root), "response-AOV scene descriptor")
    descriptor = read_json(descriptor_path)
    failures = descriptor_failures(descriptor)
    inputs = descriptor.get("inputs") or {}
    aovs = inputs.get("aov_layers") or {}
    scene_assets = inputs.get("scene_assets") or {}
    paths = {name: file_path(aovs.get(name), root) for name in REQUIRED_AOVS}
    paths["imported_composite"] = file_path(inputs.get("imported_composite"), root)
    scene_asset_paths = {name: file_path(scene_assets.get(name), root) for name in REQUIRED_SCENE_ASSETS}
    outputs = descriptor.get("outputs") or {}
    output_image = output_path(args.output, outputs.get("renderer_candidate"), root)
    output_metadata = output_path(args.metadata, outputs.get("metadata"), root)
    output_validation = output_path(args.validation, outputs.get("validation"), root)
    result_path = resolve_path(args.result, root) if args.result else None
    strip_path = resolve_path(args.strip, root) if args.strip else None

    for name, path in paths.items():
        if not path or not os.path.isfile(path):
            failures.append({"kind": "missing_input", "input": name, "path": path})
    for name, path in scene_asset_paths.items():
        if not path or not os.path.isfile(path):
            failures.append({"kind": "missing_scene_asset", "asset": name, "path": path})
    for name, path in (
        ("image", output_image),
        ("metadata", output_metadata),
        ("validation", output_validation),
    ):
        if not path:
            failures.append({"kind": "missing_output", "output": name})
    if failures:
        result = failure_result(descriptor, descriptor_path, root, failures, started)
        write_result(result_path, result)
        raise SystemExit(1)

    base = Image.open(paths["base_rgb"]).convert("RGB")
    positive = Image.open(paths["response_positive_rgb"]).convert("RGB")
    negative = Image.open(paths["response_negative_rgb"]).convert("RGB")
    selected = Image.open(paths["selected_composite_rgb"]).convert("RGB")
    imported = Image.open(paths["imported_composite"]).convert("RGB")
    if any(image.size != base.size for image in (positive, negative, selected, imported)):
        result = failure_result(descriptor, descriptor_path, root, [{"kind": "dimension_mismatch"}], started)
        write_result(result_path, result)
        raise SystemExit(1)

    rendered = reconstruct(base, positive, negative)
    ensure_parent(output_image)
    rendered.save(output_image)
    selected_stats = diff_stats(rendered, selected)
    imported_stats = diff_stats(rendered, imported)
    expectations = descriptor.get("validation_expectations") or {}
    max_abs_threshold = int(expectations.get("aov_import_max_abs_diff", 0))
    max_mean_threshold = float(expectations.get("aov_import_max_mean_abs_diff", 0.0))
    status = "passed" if (
        selected_stats["max_abs_diff"] <= max_abs_threshold
        and selected_stats["mean_abs_diff"] <= max_mean_threshold
        and imported_stats["max_abs_diff"] <= max_abs_threshold
        and imported_stats["mean_abs_diff"] <= max_mean_threshold
    ) else "failed"

    metadata = {
        "schema": "lsfs_mitsuba_response_aov_scene_backend_metadata",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(descriptor_path, root),
        "frame": descriptor.get("frame"),
        "output_frame": descriptor.get("output_frame"),
        "scene_frame": descriptor.get("scene_frame"),
        "source_frame": descriptor.get("source_frame"),
        "stage": descriptor.get("stage"),
        "backend": {
            "backend_kind": BACKEND_KIND,
            "backend_executable": posix_rel(os.path.abspath(__file__), root),
            "process_mode": "external_response_aov_scene_backend",
        },
        "scene_assets": {
            name: file_entry(path, root, f"scene:{name}")
            for name, path in scene_asset_paths.items()
        },
        "render_data": descriptor.get("render_data") or {},
        "visual_gate": descriptor.get("visual_gate") or {},
        "output": image_entry(output_image, root),
    }
    validation = {
        "schema": "lsfs_mitsuba_response_aov_scene_backend_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(descriptor_path, root),
        "frame": descriptor.get("frame"),
        "output_frame": descriptor.get("output_frame"),
        "status": status,
        "references": {
            "selected_composite": image_entry(paths["selected_composite_rgb"], root),
            "imported_composite": image_entry(paths["imported_composite"], root),
        },
        "output": image_entry(output_image, root),
        "diff": {
            "selected_mean_abs_diff": selected_stats["mean_abs_diff"],
            "selected_max_abs_diff": selected_stats["max_abs_diff"],
            "selected_mismatched_coverage": selected_stats["mismatched_coverage"],
            "imported_mean_abs_diff": imported_stats["mean_abs_diff"],
            "imported_max_abs_diff": imported_stats["max_abs_diff"],
            "imported_mismatched_coverage": imported_stats["mismatched_coverage"],
        },
        "thresholds": {
            "max_abs_diff": max_abs_threshold,
            "max_mean_abs_diff": max_mean_threshold,
        },
    }
    ensure_parent(output_metadata)
    ensure_parent(output_validation)
    write_json(output_metadata, metadata)
    write_json(output_validation, validation)
    if strip_path:
        labeled_strip(
            [
                base,
                layer_visual(positive, args.preview_gain),
                layer_visual(negative, args.preview_gain),
                rendered,
                selected,
                diff_visual(selected_stats["diff_image"]),
            ],
            ["base", "+response", "-response", "backend", "selected", "diff"],
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
        "selected_reference_sha256": sha256_file(paths["selected_composite_rgb"]),
        "imported_reference_sha256": sha256_file(paths["imported_composite"]),
        "selected_mean_abs_diff": selected_stats["mean_abs_diff"],
        "selected_max_abs_diff": selected_stats["max_abs_diff"],
        "selected_mismatched_coverage": selected_stats["mismatched_coverage"],
        "imported_mean_abs_diff": imported_stats["mean_abs_diff"],
        "imported_max_abs_diff": imported_stats["max_abs_diff"],
        "imported_mismatched_coverage": imported_stats["mismatched_coverage"],
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    write_result(result_path, result)
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one response-AOV scene backend descriptor")
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output")
    parser.add_argument("--metadata")
    parser.add_argument("--validation")
    parser.add_argument("--strip")
    parser.add_argument("--result")
    parser.add_argument("--preview-gain", type=float, default=4.0)
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.preview_gain <= 0.0:
        parser.error("preview-gain must be positive")
    try:
        run_backend(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
