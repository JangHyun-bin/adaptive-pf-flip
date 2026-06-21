#!/usr/bin/env python
"""Build a base-only Mitsuba XML export from a split water response export."""

import argparse
import copy
import os
import re
from datetime import datetime, timezone

from add_mitsuba_water_mask_highlights import write_command_list
from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


SHAPE_RE = re.compile(r"\n?\s*<shape\b[^>]*>.*?</shape>\s*", re.DOTALL)
BSDF_RE = re.compile(r"\n?\s*<bsdf\b[^>]*\bid=\"([^\"]+)\"[^>]*>.*?</bsdf>\s*", re.DOTALL)


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def response_bins(frame):
    response = frame.get("water_mask_material_response") or {}
    return response.get("response_bins") or []


def response_bsdf_ids(frame):
    ids = []
    for item in response_bins(frame):
        bsdf_id = item.get("bsdf_id")
        if bsdf_id:
            ids.append(str(bsdf_id))
    return sorted(set(ids))


def response_mesh_markers(frame):
    markers = []
    for item in response_bins(frame):
        for key in ("response_mesh_path", "response_mesh_repo_path"):
            value = item.get(key)
            if value:
                normalized = str(value).replace("\\", "/")
                markers.append(normalized)
                markers.append(os.path.basename(normalized))
    return sorted(set(marker for marker in markers if marker))


def remove_response_shapes(xml_text, markers, bsdf_ids):
    removed = []
    marker_set = set(markers)
    bsdf_set = set(bsdf_ids)

    def replace(match):
        block = match.group(0)
        normalized = block.replace("\\", "/")
        if any(marker in normalized for marker in marker_set):
            removed.append({"kind": "mesh_marker"})
            return "\n"
        if any(f'id="{bsdf_id}"' in block for bsdf_id in bsdf_set):
            removed.append({"kind": "bsdf_ref"})
            return "\n"
        if any(f"id='{bsdf_id}'" in block for bsdf_id in bsdf_set):
            removed.append({"kind": "bsdf_ref"})
            return "\n"
        return block

    return SHAPE_RE.sub(replace, xml_text), len(removed)


def remove_response_bsdfs(xml_text, bsdf_ids):
    removed = []
    bsdf_set = set(bsdf_ids)

    def replace(match):
        bsdf_id = match.group(1)
        if bsdf_id in bsdf_set:
            removed.append(bsdf_id)
            return "\n"
        return match.group(0)

    return BSDF_RE.sub(replace, xml_text), len(removed)


def source_entry(path, root, payload):
    return {
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks") or {}
    settings = export.get("split_response_base") or {}
    lines = [
        f"# {export['title']}",
        "",
        f"Generated UTC: `{export['generated_utc']}`",
        f"Export JSON: `{posix_rel(export_path, root)}`",
        f"Status: `{export['status']}`",
        "",
        "## Inputs",
        "",
        f"- Split export: `{export['sources']['split_export']['repo_path']}`",
        "",
        "## Base-Only Export",
        "",
        f"- Remove response shapes: `{settings.get('remove_response_shapes')}`",
        f"- Remove response BSDFs: `{settings.get('remove_response_bsdfs')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Response shapes removed: `{checks.get('response_shapes_removed')}`",
        f"- Response BSDFs removed: `{checks.get('response_bsdfs_removed')}`",
        f"- Response faces removed: `{checks.get('response_faces_removed')}`",
        f"- XML bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        f"- Failures: `{checks.get('failures')}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Removed Shapes | Removed BSDFs | Response Faces | XML |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    frames = export.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        base = frame.get("split_response_base") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {base.get('response_shapes_removed')} | "
            f"{base.get('response_bsdfs_removed')} | {base.get('response_faces_removed')} | "
            f"`{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def run(args):
    root = os.getcwd()
    split_path = require_file(args.split_export, "split export")
    split = read_json(split_path)
    if split.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.split_export}: expected lsfs_mitsuba_xml_export schema")
    if split.get("status") != "ready":
        raise SystemExit(f"{args.split_export}: split export status is {split.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    failures = []
    frames = []
    checks = {
        "frames_exported": 0,
        "missing_references": 0,
        "response_shapes_removed": 0,
        "response_bsdfs_removed": 0,
        "response_faces_removed": 0,
        "xml_scene_bytes": 0,
    }
    for frame in split.get("frames") or []:
        xml_ref = frame.get("xml_scene") or {}
        xml_path = resolve_path(xml_ref.get("path") or xml_ref.get("repo_path"))
        output_frame = int(frame.get("output_frame", len(frames)))
        if not xml_path or not os.path.isfile(xml_path):
            checks["missing_references"] += 1
            failures.append({
                "kind": "missing_xml_scene",
                "output_frame": frame.get("output_frame"),
                "path": xml_path,
            })
            continue
        bsdf_ids = response_bsdf_ids(frame)
        markers = response_mesh_markers(frame)
        with open(xml_path, encoding="utf-8", errors="replace") as handle:
            xml_text = handle.read()
        stripped, removed_shapes = remove_response_shapes(xml_text, markers, bsdf_ids)
        stripped, removed_bsdfs = remove_response_bsdfs(stripped, bsdf_ids)
        if removed_shapes == 0 and (response_bins(frame) or bsdf_ids):
            failures.append({
                "kind": "response_shapes_not_removed",
                "output_frame": frame.get("output_frame"),
                "xml_scene": posix_rel(xml_path, root),
            })
        out_xml = os.path.join(scene_dir, f"frame_{output_frame:04d}.xml")
        write_text(out_xml, stripped)
        out_frame = copy.deepcopy(frame)
        out_frame["xml_scene"] = {
            "path": out_xml,
            "repo_path": posix_rel(out_xml, root),
            "sha256": sha256_file(out_xml),
            "size": os.path.getsize(out_xml),
        }
        out_frame["expected_output"] = {
            "path": os.path.join(render_dir, f"frame_{output_frame:04d}.exr"),
            "repo_path": posix_rel(os.path.join(render_dir, f"frame_{output_frame:04d}.exr"), root),
        }
        removed_faces = sum(int(item.get("faces") or 0) for item in response_bins(frame))
        out_frame["split_response_base"] = {
            "source_xml_repo_path": posix_rel(xml_path, root),
            "response_shapes_removed": removed_shapes,
            "response_bsdfs_removed": removed_bsdfs,
            "response_faces_removed": removed_faces,
            "response_bsdf_ids": bsdf_ids,
        }
        frames.append(out_frame)
        checks["frames_exported"] += 1
        checks["response_shapes_removed"] += removed_shapes
        checks["response_bsdfs_removed"] += removed_bsdfs
        checks["response_faces_removed"] += removed_faces
        checks["xml_scene_bytes"] += os.path.getsize(out_xml)

    command_path = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_command_list(command_path, frames, args.mitsuba_command, args.mitsuba_mode)
    checks["failures"] = len(failures)
    status = "failed" if failures else "ready"
    export = copy.deepcopy(split)
    export.update({
        "schema": "lsfs_mitsuba_xml_export",
        "version": int(split.get("version") or 1),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "execution_mode": "xml_export_only",
        "sources": {
            "split_export": source_entry(split_path, root, split),
        },
        "split_response_base": {
            "enabled": True,
            "remove_response_shapes": True,
            "remove_response_bsdfs": True,
        },
        "checks": checks,
        "failures": failures,
        "frames": frames,
        "command_list": {
            "path": command_path,
            "repo_path": posix_rel(command_path, root),
            "sha256": sha256_file(command_path),
            "size": os.path.getsize(command_path),
        },
        "next": args.next,
    })

    export_path = os.path.join(out_dir, args.manifest_name)
    write_json(export_path, export)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(export_path)[0] + ".md"
    write_text(report_path, markdown_report(export, export_path, root, args.next))
    print(
        f"status={status} frames={checks['frames_exported']} "
        f"removed_shapes={checks['response_shapes_removed']} "
        f"removed_faces={checks['response_faces_removed']} out={export_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a base-only export from a split response Mitsuba export")
    parser.add_argument("split_export")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest-name", default="mitsuba_base_export.json")
    parser.add_argument("--report")
    parser.add_argument("--mitsuba-command", default="mitsuba")
    parser.add_argument("--mitsuba-mode", default=None)
    parser.add_argument("--title", default="Mitsuba Split Response Base Export")
    parser.add_argument(
        "--next",
        default="Render this base-only export and subtract it from the split full render to inspect response contribution.",
    )
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main()
