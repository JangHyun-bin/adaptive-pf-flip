#!/usr/bin/env python
"""Dry-run validate an LSFS external renderer adapter manifest."""

import argparse
import os
import shutil
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


DEFAULT_ENCODINGS = ("json_camera", "obj", "csv")
REQUIRED_SCENE_ASSETS = ("camera", "water_surface", "phase_volume", "particle_stream")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def first_token(command_line):
    text = (command_line or "").strip()
    if not text:
        return None
    if text[0] == '"':
        end = text.find('"', 1)
        return text[1:end] if end >= 0 else text.strip('"')
    return text.split()[0]


def command_lines(path):
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def manifest_path_ref(manifest, key):
    ref = manifest.get(key, {})
    return resolve_path(ref.get("path") or ref.get("repo_path"))


def validate_scene(frame, manifest, supported_encodings, root):
    failures = []
    warnings = []
    scene_ref = frame.get("scene_descriptor", {})
    scene_path = resolve_path(scene_ref.get("path") or scene_ref.get("repo_path"))
    if not scene_path or not os.path.isfile(scene_path):
        failures.append({
            "kind": "missing_scene_descriptor",
            "output_frame": frame.get("output_frame"),
            "path": scene_path,
        })
        return None, failures, warnings
    scene = read_json(scene_path)
    if scene.get("schema") != "lsfs_external_renderer_scene_descriptor":
        failures.append({
            "kind": "invalid_scene_schema",
            "output_frame": frame.get("output_frame"),
            "schema": scene.get("schema"),
        })
    if scene.get("target_renderer") != manifest.get("target_renderer"):
        failures.append({
            "kind": "target_renderer_mismatch",
            "output_frame": frame.get("output_frame"),
            "scene_target": scene.get("target_renderer"),
            "manifest_target": manifest.get("target_renderer"),
        })
    if scene.get("output_frame") != frame.get("output_frame"):
        failures.append({
            "kind": "output_frame_mismatch",
            "manifest_output_frame": frame.get("output_frame"),
            "scene_output_frame": scene.get("output_frame"),
        })

    assets = scene.get("assets") or {}
    asset_bytes = 0
    for role in REQUIRED_SCENE_ASSETS:
        asset = assets.get(role) or {}
        path = resolve_path(asset.get("path") or asset.get("repo_path"))
        encoding = asset.get("encoding")
        if asset.get("required") is not True:
            failures.append({
                "kind": "asset_not_required",
                "output_frame": frame.get("output_frame"),
                "asset": role,
            })
        if encoding not in supported_encodings:
            failures.append({
                "kind": "unsupported_encoding",
                "output_frame": frame.get("output_frame"),
                "asset": role,
                "encoding": encoding,
            })
        if not path or not os.path.isfile(path):
            failures.append({
                "kind": "missing_asset",
                "output_frame": frame.get("output_frame"),
                "asset": role,
                "path": path,
            })
        else:
            asset_bytes += os.path.getsize(path)

    outputs = scene.get("expected_outputs") or {}
    for name in ("image", "metadata"):
        output = outputs.get(name) or {}
        path = resolve_path(output.get("path") or output.get("repo_path"))
        if not path:
            failures.append({
                "kind": "missing_output_path",
                "output_frame": frame.get("output_frame"),
                "output": name,
            })
            continue
        if not os.path.isdir(os.path.dirname(path)):
            failures.append({
                "kind": "missing_output_dir",
                "output_frame": frame.get("output_frame"),
                "output": name,
                "path": os.path.dirname(path),
            })

    render_settings = scene.get("render_settings") or {}
    manifest_settings = manifest.get("render_settings") or {}
    for key in ("width", "height", "samples", "output_format"):
        if render_settings.get(key) != manifest_settings.get(key):
            warnings.append({
                "kind": "render_setting_mismatch",
                "output_frame": frame.get("output_frame"),
                "setting": key,
                "scene": render_settings.get(key),
                "manifest": manifest_settings.get(key),
            })

    return {
        "output_frame": frame.get("output_frame"),
        "scene_descriptor": posix_rel(scene_path, root),
        "asset_bytes": asset_bytes,
        "water_mesh_face_count": (scene.get("diagnostics") or {}).get("water_mesh_face_count"),
        "secondary_total": ((scene.get("diagnostics") or {}).get("secondary_counts") or {}).get("total"),
    }, failures, warnings


def validate_manifest(args):
    root = os.getcwd()
    manifest_path = require_file(args.manifest, "adapter manifest")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_external_renderer_adapter_manifest":
        raise SystemExit(f"{args.manifest}: expected lsfs_external_renderer_adapter_manifest schema")
    if manifest.get("status") != "ready":
        raise SystemExit(f"{args.manifest}: adapter manifest status is {manifest.get('status')!r}")

    supported_encodings = set(args.supported_encoding or DEFAULT_ENCODINGS)
    frames = manifest.get("frames") or []
    failures = []
    warnings = []
    frame_results = []
    total_asset_bytes = 0
    for frame in frames:
        result, frame_failures, frame_warnings = validate_scene(frame, manifest, supported_encodings, root)
        failures.extend(frame_failures)
        warnings.extend(frame_warnings)
        if result:
            frame_results.append(result)
            total_asset_bytes += result.get("asset_bytes", 0)

    command_path = manifest_path_ref(manifest, "command_list")
    commands = command_lines(command_path)
    if len(commands) != len(frames):
        failures.append({
            "kind": "command_count_mismatch",
            "expected": len(frames),
            "actual": len(commands),
            "path": command_path,
        })
    command_mismatches = 0
    for index, frame in enumerate(frames):
        if index >= len(commands):
            break
        scene_path = resolve_path((frame.get("scene_descriptor") or {}).get("path"))
        image_path = resolve_path(((frame.get("expected_outputs") or {}).get("image") or {}).get("path"))
        command = commands[index]
        if (scene_path and scene_path not in command) or (image_path and image_path not in command):
            command_mismatches += 1
            failures.append({
                "kind": "command_path_mismatch",
                "output_frame": frame.get("output_frame"),
                "command": command,
            })

    renderer_command = args.renderer_command or first_token(commands[0] if commands else manifest.get("renderer_command_template"))
    renderer_path = shutil.which(renderer_command) if renderer_command else None
    if not renderer_path:
        item = {
            "kind": "renderer_executable_missing",
            "renderer_command": renderer_command,
            "required": args.require_renderer,
        }
        if args.require_renderer:
            failures.append(item)
        else:
            warnings.append(item)

    frame_numbers = [frame.get("output_frame") for frame in frames]
    sequential = frame_numbers == list(range(len(frames)))
    if not sequential:
        failures.append({
            "kind": "non_sequential_output_frames",
            "frames": frame_numbers[:12],
        })

    status = "failed" if failures else "ready"
    return {
        "schema": "lsfs_external_renderer_backend_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "title": args.title,
        "adapter_manifest": {
            "path": manifest_path,
            "repo_path": posix_rel(manifest_path, root),
            "schema": manifest.get("schema"),
            "version": manifest.get("version"),
            "sha256": sha256_file(manifest_path),
        },
        "target_renderer": manifest.get("target_renderer"),
        "renderer_command": renderer_command,
        "renderer_executable": {
            "required": args.require_renderer,
            "found": bool(renderer_path),
            "path": renderer_path,
        },
        "supported_encodings": sorted(supported_encodings),
        "checks": {
            "frame_count": len(frames),
            "scene_descriptors_read": len(frame_results),
            "command_count": len(commands),
            "command_mismatches": command_mismatches,
            "output_frames_sequential": sequential,
            "failures": len(failures),
            "warnings": len(warnings),
            "referenced_asset_bytes": total_asset_bytes,
        },
        "failures": failures,
        "warnings": warnings,
        "frame_samples": [
            frame_results[index]
            for index in sorted(set([0, len(frame_results) // 2, len(frame_results) - 1]))
            if frame_results
        ],
        "next": args.next,
    }


def markdown_report(validation, out_path, root):
    checks = validation.get("checks", {})
    renderer = validation.get("renderer_executable", {})
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        f"Target renderer: `{validation.get('target_renderer')}`",
        f"Renderer command: `{validation.get('renderer_command')}`",
        f"Renderer executable found: `{renderer.get('found')}`",
        f"Renderer executable required: `{renderer.get('required')}`",
        "",
        "## Adapter Manifest",
        "",
        f"- Manifest: `{validation.get('adapter_manifest', {}).get('repo_path')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frame_count')}`",
        f"- Scene descriptors read: `{checks.get('scene_descriptors_read')}`",
        f"- Command count: `{checks.get('command_count')}`",
        f"- Command mismatches: `{checks.get('command_mismatches')}`",
        f"- Output frames sequential: `{checks.get('output_frames_sequential')}`",
        f"- Failures: `{checks.get('failures')}`",
        f"- Warnings: `{checks.get('warnings')}`",
        f"- Referenced asset bytes: `{format_bytes(checks.get('referenced_asset_bytes', 0))}`",
        "",
        "## Supported Encodings",
        "",
    ]
    for encoding in validation.get("supported_encodings", []):
        lines.append(f"- `{encoding}`")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Scene Descriptor | Asset Bytes | Water Faces | Secondary Total |",
        "| ---: | --- | ---: | ---: | ---: |",
    ])
    for frame in validation.get("frame_samples", []):
        lines.append(
            f"| {frame.get('output_frame')} | `{frame.get('scene_descriptor')}` | "
            f"{frame.get('asset_bytes')} | {frame.get('water_mesh_face_count')} | "
            f"{frame.get('secondary_total')} |"
        )
    if validation.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        for warning in validation["warnings"][:12]:
            lines.append(f"- `{warning.get('kind')}`")
    if validation.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in validation["failures"][:12]:
            lines.append(f"- `{failure.get('kind')}`")
    lines.extend([
        "",
        "## Next",
        "",
        validation.get("next", "Resolve validation failures before invoking an offline renderer."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Dry-run validate an external renderer adapter manifest")
    parser.add_argument("manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--renderer-command")
    parser.add_argument("--require-renderer", action="store_true")
    parser.add_argument("--supported-encoding", action="append", default=list(DEFAULT_ENCODINGS))
    parser.add_argument("--title", default="External Renderer Adapter Backend Validation")
    parser.add_argument(
        "--next",
        default="Use this validation as the gate before implementing or invoking a renderer-specific backend.",
    )
    args = parser.parse_args(argv)
    validation = validate_manifest(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, validation)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(validation, out_path, os.getcwd()))
    print(
        f"status={validation['status']} frames={validation['checks']['frame_count']} "
        f"failures={validation['checks']['failures']} warnings={validation['checks']['warnings']} out={out_path}"
    )
    print(f"report={report_path}")
    if validation["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
