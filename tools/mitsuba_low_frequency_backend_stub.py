#!/usr/bin/env python
"""Executable stub for one low-frequency backend scene descriptor."""

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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required by mitsuba_low_frequency_backend_stub")


def open_rgb(path):
    return Image.open(path).convert("RGB")


def result_path(value, root):
    return resolve_path(value, root) if value else None


def write_result(path, result):
    if path:
        write_json(path, result)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_backend(args):
    require_pillow()
    started = time.perf_counter()
    root = os.getcwd()
    scene_path = require_file(resolve_path(args.scene, root), "backend scene descriptor")
    scene = read_json(scene_path)
    if scene.get("schema") != "lsfs_mitsuba_low_frequency_backend_scene_descriptor":
        raise SystemExit(f"{args.scene}: expected lsfs_mitsuba_low_frequency_backend_scene_descriptor schema")

    inputs = scene.get("inputs") or {}
    paths = {
        "base_rgb": file_path(inputs.get("base_rgb"), root),
        "positive_delta_rgb": file_path(inputs.get("positive_delta_rgb"), root),
        "negative_delta_rgb": file_path(inputs.get("negative_delta_rgb"), root),
        "accepted_reference": file_path(scene.get("accepted_reference"), root),
    }
    missing = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
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
    if missing or missing_outputs:
        result = {
            "schema": "lsfs_mitsuba_low_frequency_backend_stub_result",
            "version": 1,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "scene_descriptor": posix_rel(scene_path, root),
            "frame": scene.get("frame"),
            "missing_inputs": missing,
            "missing_outputs": missing_outputs,
            "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }
        write_result(result_path(args.result, root), result)
        raise SystemExit(1)

    base = open_rgb(paths["base_rgb"])
    positive = open_rgb(paths["positive_delta_rgb"])
    negative = open_rgb(paths["negative_delta_rgb"])
    reference = open_rgb(paths["accepted_reference"])
    if any(image.size != base.size for image in (positive, negative, reference)):
        result = {
            "schema": "lsfs_mitsuba_low_frequency_backend_stub_result",
            "version": 1,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "scene_descriptor": posix_rel(scene_path, root),
            "frame": scene.get("frame"),
            "dimension_mismatch": True,
            "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
        }
        write_result(result_path(args.result, root), result)
        raise SystemExit(1)

    gain = float(((scene.get("runtime_contract") or {}).get("parameters") or {}).get("texture_gain", args.texture_gain))
    rendered = blend_delta(base, positive, negative, gain)
    ensure_parent(output_image)
    rendered.save(output_image)
    stats = diff_stats(rendered, reference)
    status = "passed" if stats["max_abs_diff"] == 0 and stats["mean_abs_diff"] == 0.0 else "failed"

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
            "stub_executable": posix_rel(os.path.abspath(__file__), root),
            "process_mode": "external_stub",
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
        "schema": "lsfs_mitsuba_low_frequency_backend_stub_result",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
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
        "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    write_result(result_path(args.result, root), result)
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one low-frequency backend scene descriptor through an executable stub")
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
