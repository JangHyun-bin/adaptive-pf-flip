#!/usr/bin/env python
"""Validate an LSFS Mitsuba renderer scene-cache handoff manifest."""

import argparse
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    write_json,
    write_text,
)


REQUIRED_SCENE_ASSETS = ("camera", "particles", "phase_cells")
REQUIRED_TEXTURES = (
    "base_rgb",
    "target_rgb",
    "parity_composite_rgb",
    "applied_positive_delta_rgb",
    "applied_negative_delta_rgb",
    "applied_magnitude_luma",
    "dark_damping_weight_luma",
)


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def check_ref(checks, ref, label, root, require_size_match=True):
    path = None
    if isinstance(ref, dict):
        path = ref.get("path") or ref.get("repo_path") or ref.get("source_repo_path")
    elif isinstance(ref, str):
        path = ref
    resolved = resolve_path(path, root)
    if not resolved or not os.path.isfile(resolved):
        checks.append({
            "name": label,
            "status": "failed",
            "detail": "missing file",
            "path": path,
        })
        return False
    expected_size = ref.get("size") if isinstance(ref, dict) else None
    actual_size = os.path.getsize(resolved)
    if require_size_match and isinstance(expected_size, int) and expected_size >= 0 and expected_size != actual_size:
        checks.append({
            "name": label,
            "status": "failed",
            "detail": "size mismatch",
            "path": posix_rel(resolved, root),
            "expected": expected_size,
            "actual": actual_size,
        })
        return False
    checks.append({
        "name": label,
        "status": "passed",
        "detail": "file exists",
        "path": posix_rel(resolved, root),
        "size": actual_size,
    })
    return True


def validate(args):
    root = os.getcwd()
    manifest_path = require_file(args.handoff_manifest, "renderer scene-cache handoff")
    handoff = read_json(manifest_path)
    if handoff.get("schema") != "lsfs_mitsuba_renderer_scene_cache_handoff":
        raise SystemExit(f"{args.handoff_manifest}: expected lsfs_mitsuba_renderer_scene_cache_handoff schema")

    checks = []
    failures = []
    frames = handoff.get("frames") or []
    summary_checks = handoff.get("checks") or {}
    if handoff.get("status") != "ready":
        failures.append({"name": "handoff.status", "detail": f"expected ready, got {handoff.get('status')}"})
    if summary_checks.get("missing_references") != 0:
        failures.append({"name": "handoff.missing_references", "detail": summary_checks.get("missing_references")})
    if summary_checks.get("handoff_frames") != len(frames):
        failures.append({"name": "handoff.frame_count", "detail": "summary count does not match frame list"})

    for key, source in (handoff.get("sources") or {}).items():
        if source:
            check_ref(checks, source, f"source:{key}", root)

    for index, frame in enumerate(frames):
        scene = frame.get("scene") or {}
        scene_assets = scene.get("assets") or {}
        for role in REQUIRED_SCENE_ASSETS:
            check_ref(checks, scene_assets.get(role), f"frame:{index}:scene:{role}", root)
        water_mesh = scene_assets.get("water_mesh")
        if water_mesh:
            check_ref(checks, water_mesh, f"frame:{index}:scene:water_mesh", root)
        textures = frame.get("textures") or {}
        for role in REQUIRED_TEXTURES:
            check_ref(checks, textures.get(role), f"frame:{index}:texture:{role}", root)
        consumer = frame.get("consumer") or {}
        check_ref(checks, consumer.get("composite"), f"frame:{index}:consumer:composite", root)

    if args.max_texture_reconstruction_abs_diff is not None:
        actual = summary_checks.get("max_texture_reconstruction_abs_diff")
        if actual is None or actual > args.max_texture_reconstruction_abs_diff:
            failures.append({
                "name": "max_texture_reconstruction_abs_diff",
                "detail": f"{actual} > {args.max_texture_reconstruction_abs_diff}",
            })
    if args.max_visual_expected_abs_diff is not None:
        actual = summary_checks.get("max_visual_expected_abs_diff")
        if actual is None or actual > args.max_visual_expected_abs_diff:
            failures.append({
                "name": "max_visual_expected_abs_diff",
                "detail": f"{actual} > {args.max_visual_expected_abs_diff}",
            })

    failed_checks = [item for item in checks if item.get("status") != "passed"]
    failures.extend({"name": item["name"], "detail": item.get("detail")} for item in failed_checks)
    status = "passed" if not failures else "failed"
    validation = {
        "schema": "lsfs_mitsuba_renderer_scene_cache_handoff_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "handoff_manifest": {
            "path": manifest_path,
            "repo_path": posix_rel(manifest_path, root),
            "schema": handoff.get("schema"),
            "status": handoff.get("status"),
        },
        "checks": {
            "total": len(checks),
            "passed": sum(1 for item in checks if item.get("status") == "passed"),
            "failed": len(failed_checks),
            "frames": len(frames),
            "scene_frames": summary_checks.get("scene_frames"),
            "visual_frames": summary_checks.get("visual_frames"),
            "unique_scene_frames": summary_checks.get("unique_scene_frames"),
            "mapping_mode": summary_checks.get("mapping_mode"),
            "texture_bytes": summary_checks.get("texture_bytes", 0),
        },
        "failures": failures,
        "check_items": checks,
        "next": args.next,
    }
    if args.summary:
        write_json(args.summary, validation)
    if args.report:
        write_text(args.report, markdown_report(validation, args.summary or manifest_path, root))
    print(
        f"status={status} total={validation['checks']['total']} failed={validation['checks']['failed']} "
        f"frames={validation['checks']['frames']}"
    )
    if status != "passed":
        raise SystemExit(1)


def markdown_report(validation, validation_path, root):
    checks = validation.get("checks") or {}
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(os.path.abspath(validation_path), root)}`",
        f"Status: `{validation['status']}`",
        "",
        "## Checks",
        "",
        f"- Total: `{checks.get('total')}`",
        f"- Passed: `{checks.get('passed')}`",
        f"- Failed: `{checks.get('failed')}`",
        f"- Frames: `{checks.get('frames')}`",
        f"- Scene frames: `{checks.get('scene_frames')}`",
        f"- Visual frames: `{checks.get('visual_frames')}`",
        f"- Unique scene frames: `{checks.get('unique_scene_frames')}`",
        f"- Mapping mode: `{checks.get('mapping_mode')}`",
        f"- Texture bytes: `{format_bytes(checks.get('texture_bytes', 0))}`",
    ]
    if validation.get("failures"):
        lines.extend(["", "## Failures", ""])
        for item in validation["failures"][:50]:
            lines.append(f"- `{item.get('name')}`: {item.get('detail')}")
    lines.extend(["", "## Next", "", validation.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a renderer scene-cache handoff")
    parser.add_argument("handoff_manifest")
    parser.add_argument("--summary")
    parser.add_argument("--report")
    parser.add_argument("--max-texture-reconstruction-abs-diff", type=int, default=0)
    parser.add_argument("--max-visual-expected-abs-diff", type=int, default=0)
    parser.add_argument("--title", default="S579 Renderer Scene Cache Handoff Validation")
    parser.add_argument(
        "--next",
        default="Use the validated handoff as the input contract for the next metadata-driven renderer depth/material pass.",
    )
    args = parser.parse_args(argv)
    validate(args)


if __name__ == "__main__":
    main()
