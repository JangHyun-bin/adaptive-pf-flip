#!/usr/bin/env python
"""Validate a Mitsuba XML export bundle without requiring Mitsuba to be installed."""

import argparse
import os
import shlex
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def command_lines(path):
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def command_tokens(command):
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return []


def command_syntax_failures(commands, path):
    failures = []
    for index, command in enumerate(commands):
        tokens = command_tokens(command)
        if not tokens:
            failures.append({
                "kind": "command_parse_error",
                "command_index": index,
                "path": path,
            })
            continue
        if len(tokens) >= 2 and tokens[1].lower() == "render":
            failures.append({
                "kind": "legacy_mitsuba_render_subcommand",
                "command_index": index,
                "path": path,
            })
            continue
        if "-o" not in tokens:
            failures.append({
                "kind": "missing_output_option",
                "command_index": index,
                "path": path,
            })
    return failures


def xml_shape_counts(path):
    root = ET.parse(path).getroot()
    shapes = list(root.iter("shape"))
    obj_count = sum(1 for item in shapes if item.attrib.get("type") == "obj")
    sphere_count = sum(1 for item in shapes if item.attrib.get("type") == "sphere")
    bsdf_count = sum(1 for _item in root.iter("bsdf"))
    return {
        "obj": obj_count,
        "sphere": sphere_count,
        "bsdf": bsdf_count,
    }


def validate_export(args):
    root = os.getcwd()
    export_path = require_file(args.export, "mitsuba export")
    export = read_json(export_path)
    if export.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.export}: expected lsfs_mitsuba_xml_export schema")
    if export.get("status") != "ready":
        raise SystemExit(f"{args.export}: export status is {export.get('status')!r}")

    failures = []
    warnings = []
    frame_results = []
    total_obj = 0
    total_sphere = 0
    total_bsdf = 0
    for frame in export.get("frames") or []:
        xml_path = resolve_path((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path"))
        if not xml_path or not os.path.isfile(xml_path):
            failures.append({
                "kind": "missing_xml_scene",
                "output_frame": frame.get("output_frame"),
                "path": xml_path,
            })
            continue
        try:
            counts = xml_shape_counts(xml_path)
        except ET.ParseError as exc:
            failures.append({
                "kind": "xml_parse_error",
                "output_frame": frame.get("output_frame"),
                "path": xml_path,
                "error": str(exc),
            })
            continue
        if counts["obj"] < 1:
            failures.append({
                "kind": "missing_water_obj_shape",
                "output_frame": frame.get("output_frame"),
                "path": xml_path,
            })
        expected_output = resolve_path((frame.get("expected_output") or {}).get("path"))
        if expected_output and not os.path.isdir(os.path.dirname(expected_output)):
            failures.append({
                "kind": "missing_output_dir",
                "output_frame": frame.get("output_frame"),
                "path": os.path.dirname(expected_output),
            })
        total_obj += counts["obj"]
        total_sphere += counts["sphere"]
        total_bsdf += counts["bsdf"]
        frame_results.append({
            "output_frame": frame.get("output_frame"),
            "xml_scene": posix_rel(xml_path, root),
            "obj_shapes": counts["obj"],
            "sphere_shapes": counts["sphere"],
            "bsdfs": counts["bsdf"],
        })

    command_path = resolve_path((export.get("command_list") or {}).get("path") or (export.get("command_list") or {}).get("repo_path"))
    commands = command_lines(command_path)
    if len(commands) != len(export.get("frames") or []):
        failures.append({
            "kind": "command_count_mismatch",
            "expected": len(export.get("frames") or []),
            "actual": len(commands),
            "path": command_path,
        })
    failures.extend(command_syntax_failures(commands, command_path))

    mitsuba_path = shutil.which(args.mitsuba_command)
    if not mitsuba_path:
        item = {
            "kind": "mitsuba_executable_missing",
            "command": args.mitsuba_command,
            "required": args.require_mitsuba,
        }
        if args.require_mitsuba:
            failures.append(item)
        else:
            warnings.append(item)

    status = "failed" if failures else "ready"
    return {
        "schema": "lsfs_mitsuba_xml_export_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "title": args.title,
        "mitsuba_export": {
            "path": export_path,
            "repo_path": posix_rel(export_path, root),
            "sha256": sha256_file(export_path),
        },
        "mitsuba_executable": {
            "command": args.mitsuba_command,
            "required": args.require_mitsuba,
            "found": bool(mitsuba_path),
            "path": mitsuba_path,
        },
        "checks": {
            "frames": len(export.get("frames") or []),
            "xml_parsed": len(frame_results),
            "command_count": len(commands),
            "obj_shapes": total_obj,
            "sphere_shapes": total_sphere,
            "bsdfs": total_bsdf,
            "failures": len(failures),
            "warnings": len(warnings),
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
    executable = validation.get("mitsuba_executable", {})
    lines = [
        f"# {validation['title']}",
        "",
        f"Generated UTC: `{validation['generated_utc']}`",
        f"Validation JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{validation['status']}`",
        "",
        "## Mitsuba",
        "",
        f"- Command: `{executable.get('command')}`",
        f"- Found: `{executable.get('found')}`",
        f"- Required: `{executable.get('required')}`",
        f"- Path: `{executable.get('path') or 'n/a'}`",
        "",
        "## Export",
        "",
        f"- Export manifest: `{validation.get('mitsuba_export', {}).get('repo_path')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- XML parsed: `{checks.get('xml_parsed')}`",
        f"- Command count: `{checks.get('command_count')}`",
        f"- OBJ shapes: `{checks.get('obj_shapes')}`",
        f"- Sphere shapes: `{checks.get('sphere_shapes')}`",
        f"- BSDFs: `{checks.get('bsdfs')}`",
        f"- Failures: `{checks.get('failures')}`",
        f"- Warnings: `{checks.get('warnings')}`",
        "",
        "## Frame Samples",
        "",
        "| Output | XML Scene | OBJ Shapes | Sphere Shapes | BSDFs |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    for frame in validation.get("frame_samples", []):
        lines.append(
            f"| {frame.get('output_frame')} | `{frame.get('xml_scene')}` | "
            f"{frame.get('obj_shapes')} | {frame.get('sphere_shapes')} | {frame.get('bsdfs')} |"
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
        validation.get("next", "Install Mitsuba or pass --require-mitsuba after configuring the executable."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a Mitsuba XML export bundle")
    parser.add_argument("export")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--mitsuba-command", default="mitsuba")
    parser.add_argument("--require-mitsuba", action="store_true")
    parser.add_argument("--title", default="Mitsuba XML Export Validation")
    parser.add_argument(
        "--next",
        default="Install Mitsuba to turn this validated XML bundle into rendered frames.",
    )
    args = parser.parse_args(argv)
    validation = validate_export(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, validation)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(validation, out_path, os.getcwd()))
    print(
        f"status={validation['status']} frames={validation['checks']['frames']} "
        f"xml_parsed={validation['checks']['xml_parsed']} failures={validation['checks']['failures']} "
        f"warnings={validation['checks']['warnings']} out={out_path}"
    )
    print(f"report={report_path}")
    if validation["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
