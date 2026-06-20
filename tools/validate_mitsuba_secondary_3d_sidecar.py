#!/usr/bin/env python
"""Validate a Mitsuba depth-aware 3D secondary-particle sidecar."""

import argparse
import json
import math
import os
from datetime import datetime, timezone

from build_bridge_review_package import posix_rel, read_json, sha256_file, write_json, write_text

SECONDARY_CHANNELS = ("spray", "foam", "bubble", "droplet")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def is_finite_vec(values, length):
    if not isinstance(values, list) or len(values) != length:
        return False
    return all(isinstance(value, (int, float)) and math.isfinite(value) for value in values)


def validate_particle(row, frame_index, line_index):
    errors = []
    label = f"frame:{frame_index}:particle:{line_index}"
    channel = row.get("channel")
    if channel not in SECONDARY_CHANNELS:
        errors.append({"id": f"{label}:channel", "status": "failed", "detail": channel})
    if not is_finite_vec(row.get("position"), 3):
        errors.append({"id": f"{label}:position", "status": "failed", "detail": row.get("position")})
    if not is_finite_vec(row.get("velocity"), 3):
        errors.append({"id": f"{label}:velocity", "status": "failed", "detail": row.get("velocity")})
    radius = row.get("radius")
    if not isinstance(radius, (int, float)) or not math.isfinite(radius) or radius <= 0.0:
        errors.append({"id": f"{label}:radius", "status": "failed", "detail": radius})
    camera = row.get("camera") or {}
    depth = camera.get("depth")
    if not isinstance(depth, (int, float)) or not math.isfinite(depth):
        errors.append({"id": f"{label}:depth", "status": "failed", "detail": depth})
    ndc = camera.get("ndc")
    if camera.get("in_front") and not (
        isinstance(ndc, list)
        and len(ndc) == 2
        and all(value is None or (isinstance(value, (int, float)) and math.isfinite(value)) for value in ndc)
    ):
        errors.append({"id": f"{label}:ndc", "status": "failed", "detail": ndc})
    return errors


def count_jsonl(path, frame_index, max_reported_errors):
    errors = []
    counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    projected = 0
    in_frame = 0
    total = 0
    with open(path, encoding="utf-8") as handle:
        for line_index, line in enumerate(handle, start=1):
            total += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append({"id": f"frame:{frame_index}:particle:{line_index}:json", "status": "failed", "detail": str(exc)})
                continue
            row_errors = validate_particle(row, frame_index, line_index)
            if len(errors) < max_reported_errors:
                errors.extend(row_errors[: max(0, max_reported_errors - len(errors))])
            channel = row.get("channel")
            if channel in counts:
                counts[channel] += 1
            camera = row.get("camera") or {}
            if camera.get("in_front"):
                projected += 1
            if camera.get("in_frame"):
                in_frame += 1
    return total, counts, projected, in_frame, errors


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
        f"- Frames: `{checks['frames']}`",
        f"- Particles: `{checks['particles']}`",
        f"- In-front particles: `{checks['in_front_particles']}`",
        f"- In-frame particles: `{checks['in_frame_particles']}`",
        f"- Failed checks: `{checks['failed']}`",
        "",
        "## Channel Counts",
        "",
        "| Channel | Count |",
        "| --- | ---: |",
    ]
    for channel in SECONDARY_CHANNELS:
        lines.append(f"| {channel} | `{checks['channel_counts'].get(channel, 0)}` |")
    if validation["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in validation["failures"][:20]:
            lines.append(f"- `{failure['id']}` {failure.get('detail')}")
    lines.extend(["", "## Next", "", validation.get("next", "")])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sidecar")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary 3D Sidecar Validation")
    parser.add_argument("--max-reported-errors", type=int, default=50)
    parser.add_argument("--next", default="Use the validated sidecar as input for a native Mitsuba secondary import pass.")
    args = parser.parse_args()

    if args.max_reported_errors < 0:
        parser.error("max-reported-errors must be non-negative")

    root = os.getcwd()
    sidecar_path = resolve_path(args.sidecar)
    payload = read_json(sidecar_path)
    failures = []
    channel_counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    particle_count = 0
    in_front_count = 0
    in_frame_count = 0

    if payload.get("schema") != "lsfs_mitsuba_secondary_3d_sidecar":
        failures.append({"id": "schema", "status": "failed", "detail": payload.get("schema")})

    for frame_index, frame in enumerate(payload.get("frames", [])):
        sidecar_ref = (frame.get("sidecar") or {}).get("path") or (frame.get("sidecar") or {}).get("repo_path")
        frame_path = resolve_path(sidecar_ref)
        if not frame_path or not os.path.isfile(frame_path):
            failures.append({"id": f"frame:{frame_index}:sidecar", "status": "failed", "detail": sidecar_ref})
            continue
        total, counts, projected, in_frame, row_errors = count_jsonl(
            frame_path,
            frame_index,
            max(0, args.max_reported_errors - len(failures)),
        )
        failures.extend(row_errors[: max(0, args.max_reported_errors - len(failures))])
        particle_count += total
        in_front_count += projected
        in_frame_count += in_frame
        for channel in SECONDARY_CHANNELS:
            channel_counts[channel] += counts[channel]
        expected_total = (frame.get("counts") or {}).get("total")
        if expected_total != total:
            failures.append({"id": f"frame:{frame_index}:count", "status": "failed", "detail": {"expected": expected_total, "actual": total}})

    validation_path = resolve_path(args.out)
    validation = {
        "schema": "lsfs_mitsuba_secondary_3d_sidecar_validation",
        "version": 1,
        "title": args.title,
        "status": "passed" if not failures else "failed",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": sidecar_path,
            "repo_path": posix_rel(sidecar_path, root),
            "schema": payload.get("schema"),
            "sha256": sha256_file(sidecar_path),
        },
        "checks": {
            "frames": len(payload.get("frames", [])),
            "particles": particle_count,
            "in_front_particles": in_front_count,
            "in_frame_particles": in_frame_count,
            "channel_counts": channel_counts,
            "failed": len(failures),
        },
        "failures": failures,
        "next": args.next,
    }
    write_json(validation_path, validation)
    if args.report:
        write_text(resolve_path(args.report), markdown_report(validation, validation_path, root))
    print(
        "status={status} frames={frames} particles={particles} failed={failed} out={out}".format(
            status=validation["status"],
            frames=validation["checks"]["frames"],
            particles=particle_count,
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
