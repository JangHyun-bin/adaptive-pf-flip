#!/usr/bin/env python
"""Tonemap backend executable for scene-depth material target descriptors."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

from build_bridge_review_package import (
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
)
from build_mitsuba_low_frequency_parity_texture_package import diff_stats
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    ImageOps,
    labeled_strip,
    preview_image,
    require_pillow,
    resolve_path,
)


RESULT_SCHEMA = "lsfs_mitsuba_renderer_scene_depth_material_tonemap_backend_result"
SCENE_SCHEMA = "lsfs_mitsuba_renderer_scene_depth_material_backend_scene_descriptor"
STAGE = "renderer_scene_depth_material_tonemap_sample"


def ensure_parent(path):
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)


def file_path(ref, root):
    if not isinstance(ref, dict):
        return None
    return resolve_path(ref.get("path") or ref.get("repo_path"), root)


def output_path(args_value, output_ref, root):
    if args_value:
        return resolve_path(args_value, root)
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


def write_result(path, result):
    if path:
        ensure_parent(path)
        write_json(path, result)
    print(json.dumps(result, indent=2, sort_keys=True))


def failure_result(scene, scene_path, root, failures, started):
    return {
        "schema": RESULT_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "backend_kind": "scene_depth_material_tonemap_backend",
        "scene_descriptor": posix_rel(scene_path, root) if scene_path else None,
        "frame": scene.get("frame") if isinstance(scene, dict) else None,
        "output_frame": scene.get("output_frame") if isinstance(scene, dict) else None,
        "job_index": scene.get("job_index") if isinstance(scene, dict) else None,
        "failures": failures,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def scene_failures(scene):
    failures = []
    if scene.get("schema") != SCENE_SCHEMA:
        failures.append({"kind": "scene_schema", "expected": SCENE_SCHEMA, "actual": scene.get("schema")})
    if scene.get("stage") != STAGE:
        failures.append({"kind": "scene_stage", "expected": STAGE, "actual": scene.get("stage")})
    controls = scene.get("controls") or {}
    if "effective_strength" not in controls:
        failures.append({"kind": "missing_control", "control": "effective_strength"})
    return failures


def run_backend(args):
    require_pillow()
    started = time.perf_counter()
    root = os.getcwd()
    scene_path = require_file(resolve_path(args.scene, root), "scene-depth material backend scene descriptor")
    scene = read_json(scene_path)
    failures = scene_failures(scene)
    inputs = scene.get("inputs") or {}
    outputs = scene.get("outputs") or {}
    source_path = file_path(inputs.get("source_composite"), root)
    magnitude_path = file_path(inputs.get("magnitude_mask"), root)
    target_path = file_path(inputs.get("target_preview"), root)
    output_image = output_path(args.output, outputs.get("image"), root)
    output_metadata = output_path(args.metadata, outputs.get("metadata"), root)
    output_validation = output_path(args.validation, outputs.get("validation"), root)
    result_path = resolve_path(args.result, root) if args.result else None
    strip_path = resolve_path(args.strip, root) if args.strip else None

    for name, path in (
        ("source_composite", source_path),
        ("magnitude_mask", magnitude_path),
        ("target_preview", target_path),
    ):
        if not path or not os.path.isfile(path):
            failures.append({"kind": "missing_input", "input": name, "path": path})
    for name, path in (
        ("image", output_image),
        ("metadata", output_metadata),
        ("validation", output_validation),
    ):
        if not path:
            failures.append({"kind": "missing_output", "output": name})
    if failures:
        result = failure_result(scene, scene_path, root, failures, started)
        write_result(result_path, result)
        raise SystemExit(1)

    source = Image.open(source_path).convert("RGB")
    magnitude = Image.open(magnitude_path).convert("L")
    target = Image.open(target_path).convert("RGB")
    if source.size != magnitude.size or source.size != target.size:
        result = failure_result(scene, scene_path, root, [{"kind": "dimension_mismatch"}], started)
        write_result(result_path, result)
        raise SystemExit(1)

    controls = scene.get("controls") or {}
    strength = float(controls.get("effective_strength") or 0.0)
    rendered, source_delta = preview_image(source, magnitude, strength)
    ensure_parent(output_image)
    rendered.save(output_image)
    stats = diff_stats(rendered, target)
    expectations = scene.get("validation_expectations") or {}
    max_threshold = int(expectations.get("max_abs_diff", 0))
    mean_threshold = float(expectations.get("max_mean_diff", 0.0))
    status = "passed" if stats["max_abs_diff"] <= max_threshold and stats["mean_abs_diff"] <= mean_threshold else "failed"

    metadata = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_backend_scene_metadata",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "stage": scene.get("stage"),
        "backend": {
            **(scene.get("backend") or {}),
            "backend_kind": "scene_depth_material_tonemap_backend",
            "backend_executable": posix_rel(os.path.abspath(__file__), root),
            "process_mode": "external_scene_depth_material_tonemap_backend",
        },
        "controls": controls,
        "output": image_entry(output_image, root),
    }
    validation = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_backend_scene_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "status": status,
        "reference": {
            "repo_path": posix_rel(target_path, root),
            "expected_sha256": (inputs.get("target_preview") or {}).get("sha256"),
            "sha256": sha256_file(target_path),
        },
        "output": image_entry(output_image, root),
        "diff": {
            "mean_abs_diff": stats["mean_abs_diff"],
            "max_abs_diff": stats["max_abs_diff"],
            "mismatched_coverage": stats["mismatched_coverage"],
        },
        "thresholds": {
            "max_abs_diff": max_threshold,
            "max_mean_diff": mean_threshold,
        },
        "delta_from_source": source_delta,
    }
    ensure_parent(output_metadata)
    ensure_parent(output_validation)
    write_json(output_metadata, metadata)
    write_json(output_validation, validation)
    if strip_path:
        mask_visual = ImageOps.colorize(magnitude, black=(6, 12, 18), white=(255, 218, 120))
        labeled_strip(
            [source, mask_visual, rendered, target, stats["diff_image"]],
            ["source composite", "magnitude mask", "backend output", "S585 target", "target diff x8"],
            strip_path,
        )

    result = {
        "schema": RESULT_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "backend_kind": "scene_depth_material_tonemap_backend",
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "job_index": scene.get("job_index"),
        "output_image_repo_path": posix_rel(output_image, root),
        "metadata_repo_path": posix_rel(output_metadata, root),
        "validation_repo_path": posix_rel(output_validation, root),
        "strip_repo_path": posix_rel(strip_path, root) if strip_path else None,
        "output_sha256": sha256_file(output_image),
        "reference_sha256": sha256_file(target_path),
        "expected_reference_sha256": (inputs.get("target_preview") or {}).get("sha256"),
        "mean_abs_diff": stats["mean_abs_diff"],
        "max_abs_diff": stats["max_abs_diff"],
        "mismatched_coverage": stats["mismatched_coverage"],
        "delta_from_source": source_delta,
        "effective_strength": strength,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    write_result(result_path, result)
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one scene-depth material backend descriptor")
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output")
    parser.add_argument("--metadata")
    parser.add_argument("--validation")
    parser.add_argument("--strip")
    parser.add_argument("--result")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_backend(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
