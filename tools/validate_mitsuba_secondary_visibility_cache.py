#!/usr/bin/env python
"""Validate a renderer-facing Mitsuba secondary visibility cache."""

import argparse
import math
import os
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    sha256_file,
    write_json,
    write_text,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to validate secondary visibility caches")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def layer_metrics(path):
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        alpha = rgba.split()[3]
        hist = alpha.histogram()
        nonzero = sum(hist[1:])
        pixels = max(1, rgba.size[0] * rgba.size[1])
        return {
            "mode": image.mode,
            "dimensions": list(rgba.size),
            "coverage": nonzero / float(pixels),
        }


def close_enough(a, b, tolerance):
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tolerance


def markdown_report(validation, validation_path, root):
    checks = validation["checks"]
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(validation_path, root)}`",
        f"Status: `{validation['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Projected particles: `{checks.get('particles_projected')}`",
        f"- Max layer coverage: `{checks.get('max_layer_coverage')}`",
        f"- Layer bytes: `{format_bytes(checks.get('layer_bytes', 0))}`",
        f"- Failed checks: `{checks.get('failed')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Coverage | Layer |",
        "| ---: | ---: | ---: | --- |",
    ]
    frames = validation.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('layer_coverage')} | `{frame.get('layer_repo_path')}` |"
        )
    if validation["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in validation["failures"][:20]:
            lines.append(f"- `{failure['id']}` {failure.get('detail')}")
    lines.extend(["", "## Next", "", validation.get("next", "")])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Visibility Cache Validation")
    parser.add_argument("--coverage-tolerance", type=float, default=1.0e-6)
    parser.add_argument("--max-layer-coverage", type=float, default=0.25)
    parser.add_argument("--min-projected-particles", type=int, default=1)
    parser.add_argument("--max-reported-errors", type=int, default=50)
    parser.add_argument("--next", default="Use the validated visibility cache as input for the next renderer-facing secondary pass.")
    args = parser.parse_args()

    if args.coverage_tolerance < 0.0:
        parser.error("coverage-tolerance must be non-negative")
    if args.max_layer_coverage <= 0.0:
        parser.error("max-layer-coverage must be positive")
    if args.min_projected_particles < 0:
        parser.error("min-projected-particles must be non-negative")
    if args.max_reported_errors < 0:
        parser.error("max-reported-errors must be non-negative")

    require_pillow()
    root = os.getcwd()
    cache_path = resolve_path(args.cache)
    payload = read_json(cache_path)
    failures = []
    frames = []
    total_projected = 0
    total_layer_bytes = 0
    observed_max_coverage = 0.0

    def fail(check_id, detail):
        if len(failures) < args.max_reported_errors:
            failures.append({"id": check_id, "status": "failed", "detail": detail})

    if payload.get("schema") != "lsfs_mitsuba_secondary_visibility_cache":
        fail("schema", payload.get("schema"))

    cache_checks = payload.get("checks") or {}
    if cache_checks.get("failures") not in (None, 0):
        fail("checks:failures", cache_checks.get("failures"))

    for index, frame in enumerate(payload.get("frames") or []):
        layer_ref = frame.get("layer_path") or frame.get("layer_repo_path")
        layer_path = resolve_path(layer_ref)
        if not layer_path or not os.path.isfile(layer_path):
            fail(f"frame:{index}:layer", layer_ref)
            continue
        actual_sha = sha256_file(layer_path)
        if frame.get("layer_sha256") and frame.get("layer_sha256") != actual_sha:
            fail(f"frame:{index}:sha256", {"expected": frame.get("layer_sha256"), "actual": actual_sha})
        layer_size = os.path.getsize(layer_path)
        if frame.get("layer_size") is not None and frame.get("layer_size") != layer_size:
            fail(f"frame:{index}:size", {"expected": frame.get("layer_size"), "actual": layer_size})
        metrics = layer_metrics(layer_path)
        if metrics["mode"] not in ("RGBA", "LA", "P"):
            fail(f"frame:{index}:mode", metrics["mode"])
        expected_coverage = float(frame.get("layer_coverage") or 0.0)
        if not close_enough(expected_coverage, metrics["coverage"], args.coverage_tolerance):
            fail(f"frame:{index}:coverage", {"expected": expected_coverage, "actual": metrics["coverage"]})
        if metrics["coverage"] <= 0.0:
            fail(f"frame:{index}:empty_alpha", metrics["coverage"])
        if metrics["coverage"] > args.max_layer_coverage:
            fail(f"frame:{index}:max_layer_coverage", metrics["coverage"])
        projected = int(frame.get("particles_projected") or 0)
        total_projected += projected
        total_layer_bytes += layer_size
        observed_max_coverage = max(observed_max_coverage, metrics["coverage"])
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "sequence_frame": frame.get("sequence_frame"),
            "layer_repo_path": posix_rel(layer_path, root),
            "layer_sha256": actual_sha,
            "layer_size": layer_size,
            "layer_coverage": metrics["coverage"],
            "dimensions": metrics["dimensions"],
            "particles_projected": projected,
        })

    if len(frames) != len(payload.get("frames") or []):
        fail("frames:resolved", {"expected": len(payload.get("frames") or []), "actual": len(frames)})
    if cache_checks.get("frames") is not None and cache_checks.get("frames") != len(frames):
        fail("checks:frames", {"expected": cache_checks.get("frames"), "actual": len(frames)})
    if total_projected < args.min_projected_particles:
        fail("checks:min_projected_particles", total_projected)
    if cache_checks.get("particles_projected") is not None and cache_checks.get("particles_projected") != total_projected:
        fail("checks:particles_projected", {"expected": cache_checks.get("particles_projected"), "actual": total_projected})
    if cache_checks.get("layer_bytes") is not None and cache_checks.get("layer_bytes") != total_layer_bytes:
        fail("checks:layer_bytes", {"expected": cache_checks.get("layer_bytes"), "actual": total_layer_bytes})
    expected_max = float(cache_checks.get("max_layer_coverage") or 0.0)
    if not close_enough(expected_max, observed_max_coverage, args.coverage_tolerance):
        fail("checks:max_layer_coverage", {"expected": expected_max, "actual": observed_max_coverage})

    validation_path = resolve_path(args.out)
    validation = {
        "schema": "lsfs_mitsuba_secondary_visibility_cache_validation",
        "version": 1,
        "title": args.title,
        "status": "passed" if not failures else "failed",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": cache_path,
            "repo_path": posix_rel(cache_path, root),
            "schema": payload.get("schema"),
            "profile_name": payload.get("profile_name"),
            "sha256": sha256_file(cache_path),
        },
        "settings": {
            "coverage_tolerance": args.coverage_tolerance,
            "max_layer_coverage": args.max_layer_coverage,
            "min_projected_particles": args.min_projected_particles,
        },
        "checks": {
            "frames": len(frames),
            "particles_projected": total_projected,
            "max_layer_coverage": observed_max_coverage,
            "layer_bytes": total_layer_bytes,
            "failed": len(failures),
        },
        "frames": frames,
        "failures": failures,
        "next": args.next,
    }
    write_json(validation_path, validation)
    if args.report:
        write_text(resolve_path(args.report), markdown_report(validation, validation_path, root))
    print(
        "status={status} frames={frames} projected={projected} failed={failed} out={out}".format(
            status=validation["status"],
            frames=validation["checks"]["frames"],
            projected=validation["checks"]["particles_projected"],
            failed=len(failures),
            out=validation_path,
        )
    )
    if args.report:
        print(f"report={resolve_path(args.report)}")
    if validation["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
