#!/usr/bin/env python
"""Split masked water faces into a localized Mitsuba material response."""

import argparse
import copy
import os
import re
from datetime import datetime, timezone

from add_mitsuba_water_mask_highlights import (
    MASK_SCHEMAS,
    add_response_comment,
    csv3,
    fmt,
    mask_layer_ref,
    output_frame_map,
    parse_vec3,
    resolve_path,
    selected_frames,
    source_entry,
    write_command_list,
)
from add_mitsuba_water_mask_mesh_response import (
    read_obj_mesh,
    require_pillow,
    select_faces,
    write_selected_obj,
    xml_path,
)
from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from composite_mitsuba_secondary_layer import parse_camera


RESPONSE_BSDF_ID = "lsfs_water_surface_masked_response"


def normalized_path(path):
    return os.path.normcase(os.path.abspath(str(path).replace("/", os.sep)))


def response_bsdf_block(args):
    lines = [
        f'  <bsdf type="roughdielectric" id="{RESPONSE_BSDF_ID}">',
    ]
    if args.distribution != "none":
        lines.append(f'    <string name="distribution" value="{args.distribution}"/>')
    lines.extend([
        f'    <float name="alpha" value="{fmt(args.response_alpha)}"/>',
        f'    <float name="int_ior" value="{fmt(args.int_ior)}"/>',
        f'    <float name="ext_ior" value="{fmt(args.ext_ior)}"/>',
    ])
    if args.response_specular_reflectance_vec is not None:
        lines.append(
            f'    <rgb name="specular_reflectance" value="{csv3(args.response_specular_reflectance_vec)}"/>'
        )
    if args.response_specular_transmittance_vec is not None:
        lines.append(
            f'    <rgb name="specular_transmittance" value="{csv3(args.response_specular_transmittance_vec)}"/>'
        )
    lines.append("  </bsdf>")
    return "\n".join(lines)


def insert_response_bsdf(xml_text, block):
    pattern = re.compile(
        r'(<bsdf\s+type="roughdielectric"\s+id="lsfs_water_surface">.*?</bsdf>)',
        flags=re.DOTALL,
    )
    match = pattern.search(xml_text)
    if not match:
        raise ValueError("missing lsfs_water_surface roughdielectric BSDF")
    return xml_text[:match.end()] + "\n" + block + xml_text[match.end():], 1


def shape_block(shape_id, mesh_path, bsdf_id):
    return "\n".join([
        f'  <shape type="obj" id="{shape_id}">',
        f'    <string name="filename" value="{xml_path(mesh_path)}"/>',
        '    <boolean name="face_normals" value="true"/>',
        f'    <ref name="bsdf" id="{bsdf_id}"/>',
        "  </shape>",
    ])


def replace_water_shape(xml_text, source_mesh, remainder_mesh, response_mesh, frame_index):
    source_norm = normalized_path(source_mesh)
    pattern = re.compile(r'(?P<block>\s*<shape\s+type="obj"(?:\s+id="[^"]+")?>.*?</shape>)', re.DOTALL)
    for match in pattern.finditer(xml_text):
        block = match.group("block")
        if 'id="lsfs_water_surface"' not in block:
            continue
        filename = re.search(r'<string\s+name="filename"\s+value="([^"]+)"\s*/>', block)
        if not filename:
            continue
        if normalized_path(filename.group(1)) != source_norm:
            continue
        replacement = "\n".join([
            shape_block(f"lsfs_s421_water_remainder_{frame_index:04d}", remainder_mesh, "lsfs_water_surface"),
            shape_block(f"lsfs_s421_water_mask_material_{frame_index:04d}", response_mesh, RESPONSE_BSDF_ID),
        ])
        return xml_text[:match.start()] + "\n" + replacement + xml_text[match.end():], 1
    raise ValueError(f"missing water shape for {source_mesh}")


def remainder_faces(vertices, faces, selected):
    selected_indices = {item["face_index"] for item in selected}
    return [
        {
            "face": face,
            "face_index": face_index,
            "centroid": (0.0, 0.0, 0.0),
            "screen": (0.0, 0.0),
            "depth": 0.0,
            "mask_value": 0,
            "source_luma": None,
            "score": 0.0,
        }
        for face_index, face in enumerate(faces)
        if face_index not in selected_indices
    ]


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    settings = export.get("water_mask_material_response") or {}
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
        f"- Mask source: `{export['sources']['mask_source']['repo_path']}`",
        "",
        "## Water Mask Material Response",
        "",
        f"- Face limit: `{settings.get('face_limit')}`",
        f"- Face stride: `{settings.get('face_stride')}`",
        f"- Response alpha: `{settings.get('response_alpha')}`",
        f"- Distribution: `{settings.get('distribution')}`",
        f"- IOR: `{settings.get('ext_ior')} -> {settings.get('int_ior')}`",
        f"- Specular reflectance: `{settings.get('response_specular_reflectance')}`",
        f"- Specular transmittance: `{settings.get('response_specular_transmittance')}`",
        f"- Mask threshold: `{settings.get('mask_threshold')}`",
        f"- Source luma gate: `{settings.get('source_luma_min')}..{settings.get('source_luma_max')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Candidate faces: `{checks.get('candidate_faces')}`",
        f"- Response faces: `{checks.get('response_faces')}`",
        f"- Remainder faces: `{checks.get('remainder_faces')}`",
        f"- Water shape replacements: `{checks.get('water_shape_replacements')}`",
        f"- Response BSDF insertions: `{checks.get('response_bsdf_insertions')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("water_mask_material_response") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('water_faces')} | "
            f"{item.get('response_faces')} | {item.get('remainder_faces')} | "
            f"`{item.get('mask_layer_repo_path')}` | `{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def split_material(args):
    require_pillow()
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    mask_source_path = require_file(args.mask_source, "mask source")
    base = read_json(base_export_path)
    mask_source = read_json(mask_source_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if mask_source.get("schema") not in MASK_SCHEMAS:
        expected = ", ".join(sorted(MASK_SCHEMAS))
        raise SystemExit(f"{args.mask_source}: expected one of {expected}")
    if mask_source.get("status") and mask_source.get("status") != "ready":
        raise SystemExit(f"{args.mask_source}: mask source status is {mask_source.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    mesh_dir = os.path.join(out_dir, "meshes")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)
    os.makedirs(mesh_dir, exist_ok=True)

    mask_frames = output_frame_map(mask_source.get("frames") or [])
    frames = []
    failures = []
    totals = {
        "xml_scene_bytes": 0,
        "candidate_faces": 0,
        "response_faces": 0,
        "response_vertices": 0,
        "response_bytes": 0,
        "remainder_faces": 0,
        "remainder_vertices": 0,
        "remainder_bytes": 0,
        "water_shape_replacements": 0,
        "response_bsdf_insertions": 0,
    }
    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")))
        water_mesh = resolve_path(((frame.get("water_mesh") or {}).get("path") or (frame.get("water_mesh") or {}).get("repo_path")))
        mask_frame = mask_frames.get(output_frame)
        mask_path = resolve_path(mask_layer_ref(mask_frame))
        source_path = resolve_path((mask_frame or {}).get("source_path") or (mask_frame or {}).get("source_repo_path"))
        missing = []
        for role, path in (("source_xml", source_xml), ("water_mesh", water_mesh), ("mask_layer", mask_path)):
            if not path or not os.path.isfile(path):
                missing.append({"role": role, "path": path})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        vertices, faces = read_obj_mesh(water_mesh)
        from PIL import Image

        mask = Image.open(mask_path).convert("L")
        source = Image.open(source_path).convert("RGB") if source_path and os.path.isfile(source_path) else None
        camera = parse_camera(source_xml)
        selected = select_faces(vertices, faces, camera, mask, source, args)
        if not selected:
            failures.append({"output_frame": output_frame, "missing": [{"role": "selected_faces", "path": None}]})
            continue
        remainder = remainder_faces(vertices, faces, selected)
        if not remainder:
            failures.append({"output_frame": output_frame, "missing": [{"role": "remainder_faces", "path": None}]})
            continue

        base_name = f"frame_{index:04d}"
        response_mesh = os.path.join(mesh_dir, f"{base_name}_water_mask_material.obj")
        remainder_mesh = os.path.join(mesh_dir, f"{base_name}_water_remainder.obj")
        response_stats = write_selected_obj(response_mesh, vertices, selected, args.response_y_lift, args.reverse_faces)
        remainder_stats = write_selected_obj(remainder_mesh, vertices, remainder, 0.0, args.reverse_faces)

        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        patched, count = insert_response_bsdf(xml_text, response_bsdf_block(args))
        totals["response_bsdf_insertions"] += count
        patched, count = replace_water_shape(patched, water_mesh, remainder_mesh, response_mesh, index)
        totals["water_shape_replacements"] += count
        patched = add_response_comment(
            patched,
            f"<!-- S421 water_mask_material_response faces={len(selected)} source_faces={len(faces)} -->",
        )

        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["candidate_faces"] += len(selected)
        totals["response_faces"] += response_stats["faces"]
        totals["response_vertices"] += response_stats["vertices"]
        totals["response_bytes"] += response_stats["bytes"]
        totals["remainder_faces"] += remainder_stats["faces"]
        totals["remainder_vertices"] += remainder_stats["vertices"]
        totals["remainder_bytes"] += remainder_stats["bytes"]

        out_frame = copy.deepcopy(frame)
        out_frame["xml_scene"] = {
            "path": xml_out,
            "repo_path": posix_rel(xml_out, root),
            "sha256": sha256_file(xml_out),
            "size": os.path.getsize(xml_out),
        }
        expected = os.path.join(render_dir, f"{base_name}.exr")
        out_frame["expected_output"] = {
            "path": expected,
            "repo_path": posix_rel(expected, root),
        }
        out_frame["water_mask_material_response"] = {
            "enabled": True,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "response_mesh_repo_path": posix_rel(response_mesh, root),
            "remainder_mesh_repo_path": posix_rel(remainder_mesh, root),
            "response_mesh_sha256": sha256_file(response_mesh),
            "remainder_mesh_sha256": sha256_file(remainder_mesh),
            "mask_layer_path": mask_path,
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "source_repo_path": posix_rel(source_path, root) if source_path else None,
            "water_vertices": len(vertices),
            "water_faces": len(faces),
            "candidate_faces": len(selected),
            "response_faces": response_stats["faces"],
            "response_vertices": response_stats["vertices"],
            "response_bytes": response_stats["bytes"],
            "remainder_faces": remainder_stats["faces"],
            "remainder_vertices": remainder_stats["vertices"],
            "remainder_bytes": remainder_stats["bytes"],
            "face_samples": [
                {
                    "centroid": [float(v) for v in item["centroid"]],
                    "screen": [float(item["screen"][0]), float(item["screen"][1])],
                    "depth": float(item["depth"]),
                    "mask_value": int(item["mask_value"]),
                    "source_luma": item["source_luma"],
                }
                for item in selected[:8]
            ],
        }
        frames.append(out_frame)

    command_list = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_command_list(
        command_list,
        frames,
        (base.get("render_settings") or {}).get("mitsuba_command") or "mitsuba",
        (base.get("render_settings") or {}).get("mitsuba_mode"),
    )
    export = copy.deepcopy(base)
    export.update({
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if frames and not failures and totals["response_faces"] > 0 else "review",
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "mask_source": source_entry(mask_source_path, root, "water highlight mask source", mask_source),
        },
        "frames": frames,
        "failures": failures,
        "water_mask_material_response": {
            "enabled": True,
            "face_limit": args.face_limit,
            "face_stride": args.face_stride,
            "response_alpha": args.response_alpha,
            "response_y_lift": args.response_y_lift,
            "distribution": args.distribution,
            "int_ior": args.int_ior,
            "ext_ior": args.ext_ior,
            "response_specular_reflectance": args.response_specular_reflectance_vec,
            "response_specular_transmittance": args.response_specular_transmittance_vec,
            "reverse_faces": args.reverse_faces,
            "mask_threshold": args.mask_threshold,
            "mask_sample_radius": args.mask_sample_radius,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["water_mask_material_response_enabled"] = True
    export["checks"] = copy.deepcopy(base.get("checks") or {})
    export["checks"].update({
        "frames_exported": len(frames),
        "missing_references": len(failures),
        **totals,
    })

    export_path = os.path.join(out_dir, "mitsuba_export.json")
    write_json(export_path, export)
    if args.report:
        write_text(args.report, markdown_report(export, export_path, root, args.next))
    print(
        f"status={export['status']} frames={len(frames)} "
        f"response_faces={totals['response_faces']} remainder_faces={totals['remainder_faces']} "
        f"export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Split original water mesh faces into a localized Mitsuba material response")
    parser.add_argument("base_export")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--face-limit", type=int, default=0)
    parser.add_argument("--face-stride", type=int, default=1)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--mask-sample-radius", type=int, default=5)
    parser.add_argument("--source-luma-min", type=float, default=0.0)
    parser.add_argument("--source-luma-max", type=float, default=255.0)
    parser.add_argument("--response-alpha", type=float, default=0.006)
    parser.add_argument("--response-y-lift", type=float, default=0.0)
    parser.add_argument("--distribution", choices=["ggx", "beckmann", "none"], default="ggx")
    parser.add_argument("--int-ior", type=float, default=1.333)
    parser.add_argument("--ext-ior", type=float, default=1.0)
    parser.add_argument("--response-specular-reflectance")
    parser.add_argument("--response-specular-transmittance")
    parser.add_argument("--reverse-faces", action="store_true")
    parser.add_argument("--depth-penalty", type=float, default=0.01)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S421 Mitsuba Water Mask Material Split")
    parser.add_argument("--next", default="Render and compare this split-water material response against S420, S417, S409, and S401.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.face_limit < 0:
        parser.error("face-limit must be non-negative")
    if args.face_stride <= 0:
        parser.error("face-stride must be positive")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.mask_sample_radius < 0:
        parser.error("mask-sample-radius must be non-negative")
    if args.source_luma_min < 0.0 or args.source_luma_max > 255.0:
        parser.error("source luma bounds must be in [0, 255]")
    if args.source_luma_min > args.source_luma_max:
        parser.error("source-luma-min cannot exceed source-luma-max")
    if args.response_alpha <= 0.0:
        parser.error("response-alpha must be positive")
    if args.response_y_lift < 0.0:
        parser.error("response-y-lift must be non-negative")
    if args.int_ior <= 0.0 or args.ext_ior <= 0.0:
        parser.error("int-ior and ext-ior must be positive")
    if args.depth_penalty < 0.0:
        parser.error("depth-penalty must be non-negative")
    args.response_specular_reflectance_vec = None
    args.response_specular_transmittance_vec = None
    if args.response_specular_reflectance:
        args.response_specular_reflectance_vec = parse_vec3(args.response_specular_reflectance, "response-specular-reflectance")
    if args.response_specular_transmittance:
        args.response_specular_transmittance_vec = parse_vec3(args.response_specular_transmittance, "response-specular-transmittance")
    for label, vec in (
        ("response-specular-reflectance", args.response_specular_reflectance_vec),
        ("response-specular-transmittance", args.response_specular_transmittance_vec),
    ):
        if vec is not None and min(vec) < 0.0:
            parser.error(f"{label} values must be non-negative")
        if vec is not None and max(vec) > 1.0:
            parser.error(f"{label} values must be in [0, 1]")
    split_material(args)


if __name__ == "__main__":
    main()
