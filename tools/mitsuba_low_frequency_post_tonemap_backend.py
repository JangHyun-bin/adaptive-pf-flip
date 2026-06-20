#!/usr/bin/env python
"""Production-style post-tonemap backend for low-frequency scene descriptors."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from build_bridge_review_package import (
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
)
from build_mitsuba_low_frequency_parity_texture_package import diff_stats
from run_mitsuba_low_frequency_backend_adapter_dry_run import (
    blend_delta,
    ensure_parent,
    file_path,
    image_entry,
    labeled_strip,
    resolve_path,
)


RESULT_SCHEMA = "lsfs_mitsuba_low_frequency_post_tonemap_backend_result"
SCENE_SCHEMA = "lsfs_mitsuba_low_frequency_backend_scene_descriptor"
STAGE = "renderer_post_tonemap_low_frequency_runtime_consumer"


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required by mitsuba_low_frequency_post_tonemap_backend")


def open_rgb(path):
    return Image.open(path).convert("RGB")


def result_path(value, root):
    return resolve_path(value, root) if value else None


def write_result(path, result):
    if path:
        write_json(path, result)
    print(json.dumps(result, indent=2, sort_keys=True))


def scene_contract_failures(scene):
    failures = []
    contract = scene.get("runtime_contract") or {}
    if scene.get("stage") != STAGE:
        failures.append({"kind": "scene_stage", "expected": STAGE, "actual": scene.get("stage")})
    if contract.get("stage") != STAGE:
        failures.append({"kind": "contract_stage", "expected": STAGE, "actual": contract.get("stage")})
    required = set(contract.get("required_bindings") or [])
    for binding in ("base_rgb", "positive_delta_rgb", "negative_delta_rgb"):
        if binding not in required:
            failures.append({"kind": "missing_required_binding", "binding": binding})
    if "positive_delta_rgb - negative_delta_rgb" not in (contract.get("expression") or ""):
        failures.append({"kind": "unsupported_expression", "expression": contract.get("expression")})
    return failures


def failure_result(scene, scene_path, root, status, failures, started):
    return {
        "schema": RESULT_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "backend_kind": "post_tonemap_texture_backend",
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "job_index": scene.get("job_index"),
        "failures": failures,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }


def run_backend(args):
    require_pillow()
    started = time.perf_counter()
    root = os.getcwd()
    scene_path = require_file(resolve_path(args.scene, root), "backend scene descriptor")
    scene = read_json(scene_path)
    if scene.get("schema") != SCENE_SCHEMA:
        raise SystemExit(f"{args.scene}: expected {SCENE_SCHEMA} schema")

    contract_failures = scene_contract_failures(scene)
    inputs = scene.get("inputs") or {}
    paths = {
        "base_rgb": file_path(inputs.get("base_rgb"), root),
        "positive_delta_rgb": file_path(inputs.get("positive_delta_rgb"), root),
        "negative_delta_rgb": file_path(inputs.get("negative_delta_rgb"), root),
        "accepted_reference": file_path(scene.get("accepted_reference"), root),
    }
    missing_inputs = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
    outputs = scene.get("outputs") or {}
    output_image = result_path(args.output, root) or resolve_path((outputs.get("image") or {}).get("repo_path"), root)
    output_metadata = result_path(args.metadata, root) or resolve_path((outputs.get("metadata") or {}).get("repo_path"), root)
    output_validation = result_path(args.validation, root) or resolve_path((outputs.get("validation") or {}).get("repo_path"), root)
    missing_outputs = [
        name
        for name, path in (
            ("output", output_image),
            ("metadata", output_metadata),
            ("validation", output_validation),
        )
        if not path
    ]
    failures = []
    failures.extend(contract_failures)
    failures.extend({"kind": "missing_input", "binding": item} for item in missing_inputs)
    failures.extend({"kind": "missing_output", "output": item} for item in missing_outputs)
    if failures:
        result = failure_result(scene, scene_path, root, "failed", failures, started)
        write_result(result_path(args.result, root), result)
        raise SystemExit(1)

    base = open_rgb(paths["base_rgb"])
    positive = open_rgb(paths["positive_delta_rgb"])
    negative = open_rgb(paths["negative_delta_rgb"])
    reference = open_rgb(paths["accepted_reference"])
    if any(image.size != base.size for image in (positive, negative, reference)):
        result = failure_result(
            scene,
            scene_path,
            root,
            "failed",
            [{"kind": "dimension_mismatch"}],
            started,
        )
        write_result(result_path(args.result, root), result)
        raise SystemExit(1)

    contract = scene.get("runtime_contract") or {}
    gain = float((contract.get("parameters") or {}).get("texture_gain", args.texture_gain))
    rendered = blend_delta(base, positive, negative, gain)
    ensure_parent(output_image)
    rendered.save(output_image)
    stats = diff_stats(rendered, reference)
    thresholds = contract.get("thresholds") or {}
    max_threshold = int(thresholds.get("max_abs_diff", 0))
    mean_threshold = float(thresholds.get("max_mean_diff", 0.0))
    status = "passed" if stats["max_abs_diff"] <= max_threshold and stats["mean_abs_diff"] <= mean_threshold else "failed"

    metadata = {
        "schema": "lsfs_mitsuba_low_frequency_backend_scene_metadata",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "stage": scene.get("stage"),
        "backend": {
            **(scene.get("backend") or {}),
            "backend_kind": "post_tonemap_texture_backend",
            "backend_executable": posix_rel(os.path.abspath(__file__), root),
            "process_mode": "external_post_tonemap_backend",
        },
        "runtime_contract": {
            "stage": contract.get("stage"),
            "expression": contract.get("expression"),
            "required_bindings": contract.get("required_bindings") or [],
            "thresholds": thresholds,
        },
        "output": image_entry(output_image, root),
    }
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_backend_scene_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "status": status,
        "reference": {
            "repo_path": posix_rel(paths["accepted_reference"], root),
            "expected_sha256": (scene.get("accepted_reference") or {}).get("expected_sha256"),
            "sha256": sha256_file(paths["accepted_reference"]),
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
    }
    write_json(output_metadata, metadata)
    write_json(output_validation, validation)
    strip_path = result_path(args.strip, root)
    if strip_path:
        labeled_strip(
            [base, positive, negative, rendered, reference, stats["diff_image"]],
            ["base", "positive", "negative", "backend output", "accepted reference", "diff x8"],
            strip_path,
        )

    result = {
        "schema": RESULT_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "backend_kind": "post_tonemap_texture_backend",
        "scene_descriptor": posix_rel(scene_path, root),
        "frame": scene.get("frame"),
        "output_frame": scene.get("output_frame"),
        "job_index": scene.get("job_index"),
        "output_image_repo_path": posix_rel(output_image, root),
        "metadata_repo_path": posix_rel(output_metadata, root),
        "validation_repo_path": posix_rel(output_validation, root),
        "strip_repo_path": posix_rel(strip_path, root) if strip_path else None,
        "output_sha256": sha256_file(output_image),
        "reference_sha256": sha256_file(paths["accepted_reference"]),
        "expected_reference_sha256": (scene.get("accepted_reference") or {}).get("expected_sha256"),
        "mean_abs_diff": stats["mean_abs_diff"],
        "max_abs_diff": stats["max_abs_diff"],
        "mismatched_coverage": stats["mismatched_coverage"],
        "texture_gain": gain,
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    write_result(result_path(args.result, root), result)
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one low-frequency descriptor through the post-tonemap backend")
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output")
    parser.add_argument("--metadata")
    parser.add_argument("--validation")
    parser.add_argument("--strip")
    parser.add_argument("--result")
    parser.add_argument("--texture-gain", type=float, default=1.0)
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_backend(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
