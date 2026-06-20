#!/usr/bin/env python
"""Bind S594 scene-depth material package snippets into a Mitsuba XML sample."""

import argparse
import copy
import os
import re
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


def resolve_path(path, root=None):
    if not path:
        return None
    text = str(path).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root or os.getcwd(), text))


def selected_frames(frames, count):
    frames = list(frames or [])
    if count <= 0 or count >= len(frames):
        return frames
    if count == 1:
        return [frames[len(frames) // 2]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(count - 1)) for i in range(count)))
    return [frames[index] for index in indices]


def by_output_frame(frames):
    return {
        int(frame.get("output_frame")): frame
        for frame in frames or []
        if frame.get("output_frame") is not None
    }


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def insert_after_scene_open(xml_text, block):
    match = re.search(r"<scene\b[^>]*>", xml_text)
    if not match:
        raise ValueError("missing <scene> root")
    return xml_text[:match.end()] + "\n" + block + xml_text[match.end():]


def replace_water_refs(xml_text, bsdf_id):
    return re.subn(
        r'<ref\s+name="bsdf"\s+id="lsfs_water_surface"\s*/>',
        f'<ref name="bsdf" id="{bsdf_id}"/>',
        xml_text,
    )


def snippet_ref(frame):
    snippet = frame.get("snippet") or {}
    return resolve_path(snippet.get("path") or snippet.get("repo_path"))


def bsdf_id_for_frame(frame_id):
    return f"lsfs_scene_depth_material_water_{int(frame_id):04d}"


def command_lines(frames, command, mode):
    mode_arg = f" -m {mode}" if mode else ""
    lines = []
    for frame in frames:
        xml_scene = (frame.get("xml_scene") or {}).get("repo_path")
        output = (frame.get("expected_output") or {}).get("repo_path")
        lines.append(f'{command}{mode_arg} "{xml_scene}" -o "{output}"')
    return "\n".join(lines) + ("\n" if lines else "")


def source_entry(path, root, label, payload):
    return {
        "label": label,
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def markdown_report(export, export_path, root):
    checks = export.get("checks") or {}
    lines = [
        f"# {export['title']}",
        "",
        f"Generated UTC: `{export['generated_utc']}`",
        f"Export JSON: `{posix_rel(export_path, root)}`",
        f"Status: `{export['status']}`",
        "",
        "## Inputs",
        "",
        f"- Base export: `{export['sources']['base_export']['repo_path']}`",
        f"- Material package: `{export['sources']['native_material_package']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Snippet insertions: `{checks.get('snippet_insertions')}`",
        f"- Water ref replacements: `{checks.get('water_ref_replacements')}`",
        f"- Package frames matched: `{checks.get('package_frames_matched')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Base XML | Bound XML | Snippet | Water Refs |",
        "| ---: | --- | --- | --- | ---: |",
    ]
    frames = export.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        bind = frame.get("scene_depth_material_binding") or {}
        lines.append(
            f"| {frame.get('output_frame')} | `{bind.get('base_xml_repo_path')}` | "
            f"`{(frame.get('xml_scene') or {}).get('repo_path')}` | `{bind.get('snippet_repo_path')}` | "
            f"{bind.get('water_ref_replacements')} |"
        )
    lines.extend(["", "## Next", "", export.get("next", ""), ""])
    return "\n".join(lines)


def bind(args):
    root = os.getcwd()
    base_path = require_file(resolve_path(args.base_export, root), "base Mitsuba XML export")
    package_path = require_file(resolve_path(args.material_package, root), "native material package")
    base = read_json(base_path)
    package = read_json(package_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: export status is {base.get('status')!r}")
    if package.get("schema") != "lsfs_mitsuba_renderer_scene_depth_material_native_material_package":
        raise SystemExit(f"{args.material_package}: expected native material package schema")
    if package.get("status") != "ready":
        raise SystemExit(f"{args.material_package}: package status is {package.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)
    package_by_output = by_output_frame(package.get("frames"))
    out_frames = []
    missing = []
    snippet_insertions = 0
    water_ref_replacements = 0
    xml_scene_bytes = 0
    for index, base_frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = int(base_frame.get("output_frame") or 0)
        package_frame = package_by_output.get(output_frame)
        if not package_frame:
            missing.append({"output_frame": output_frame, "missing": "package_frame"})
            continue
        base_xml = resolve_path((base_frame.get("xml_scene") or {}).get("path") or (base_frame.get("xml_scene") or {}).get("repo_path"), root)
        snippet_path = snippet_ref(package_frame)
        if not base_xml or not os.path.isfile(base_xml):
            missing.append({"output_frame": output_frame, "missing": "base_xml", "path": base_xml})
            continue
        if not snippet_path or not os.path.isfile(snippet_path):
            missing.append({"output_frame": output_frame, "missing": "snippet", "path": snippet_path})
            continue
        snippet = read_text(snippet_path)
        bsdf_id = bsdf_id_for_frame(package_frame.get("frame"))
        xml_text = read_text(base_xml)
        comment = (
            f"  <!-- S595 scene-depth native material binding output_frame={output_frame} "
            f"package_frame={package_frame.get('frame')} bsdf={bsdf_id} -->"
        )
        patched = insert_after_scene_open(xml_text, comment + "\n" + snippet)
        patched, replacements = replace_water_refs(patched, bsdf_id)
        if replacements <= 0:
            missing.append({"output_frame": output_frame, "missing": "water_ref_replacement", "path": base_xml})
            continue
        out_xml = os.path.join(scene_dir, f"frame_{index:04d}.xml")
        write_text(out_xml, patched)
        snippet_insertions += 1
        water_ref_replacements += replacements
        xml_scene_bytes += os.path.getsize(out_xml)
        out_frame = copy.deepcopy(base_frame)
        out_frame["xml_scene"] = {
            "path": out_xml,
            "repo_path": posix_rel(out_xml, root),
            "sha256": sha256_file(out_xml),
            "size": os.path.getsize(out_xml),
        }
        out_frame["expected_output"] = {
            "path": os.path.join(render_dir, f"frame_{index:04d}.exr"),
            "repo_path": posix_rel(os.path.join(render_dir, f"frame_{index:04d}.exr"), root),
        }
        out_frame["scene_depth_material_binding"] = {
            "base_xml_repo_path": posix_rel(base_xml, root),
            "snippet_repo_path": posix_rel(snippet_path, root),
            "package_frame": package_frame.get("frame"),
            "bsdf_id": bsdf_id,
            "water_ref_replacements": replacements,
            "material_parameters": package_frame.get("material_parameters") or {},
            "texture_bindings": package_frame.get("texture_bindings") or {},
        }
        out_frames.append(out_frame)

    command_list = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_text(command_list, command_lines(out_frames, args.render_command, args.render_mode))
    checks = {
        "frames_exported": len(out_frames),
        "missing_references": len(missing),
        "snippet_insertions": snippet_insertions,
        "water_ref_replacements": water_ref_replacements,
        "package_frames_matched": len(out_frames),
        "xml_scene_bytes": xml_scene_bytes,
        "command_list_bytes": os.path.getsize(command_list),
    }
    status = "ready" if (
        checks["frames_exported"] > 0
        and checks["missing_references"] == 0
        and checks["snippet_insertions"] == checks["frames_exported"]
        and checks["water_ref_replacements"] >= checks["frames_exported"]
    ) else "failed"
    export = {
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "execution_mode": "xml_export_only",
        "target_renderer": "mitsuba",
        "sources": {
            "base_export": source_entry(base_path, root, "base Mitsuba XML export", base),
            "native_material_package": source_entry(package_path, root, "scene-depth native material package", package),
        },
        "scene_depth_material_native_material_binding": {
            "enabled": True,
            "package_schema": package.get("schema"),
            "binding_mode": "insert_frame_local_material_snippet_and_redirect_water_bsdf_ref",
        },
        "checks": checks,
        "missing_references": missing,
        "frames": out_frames,
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "next": args.next,
    }
    export_path = os.path.abspath(args.out)
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root))
    print(
        f"status={status} frames={checks['frames_exported']} snippets={checks['snippet_insertions']} "
        f"water_refs={checks['water_ref_replacements']} export={export_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bind scene-depth native material package into a Mitsuba XML export sample")
    parser.add_argument("base_export")
    parser.add_argument("material_package")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--render-command", default="mitsuba")
    parser.add_argument("--render-mode", default="")
    parser.add_argument("--title", default="S595 Mitsuba Scene Depth Native Material XML Sample")
    parser.add_argument(
        "--next",
        default="Validate this XML export and render a bounded sample through the native Mitsuba backend.",
    )
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    bind(args)


if __name__ == "__main__":
    main()
