#!/usr/bin/env python
"""Add a masked water-surface mesh response from a projected highlight mask."""

import argparse
import copy
import os
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from add_mitsuba_water_mask_highlights import (
    MASK_SCHEMAS,
    add_response_comment,
    csv3,
    fmt,
    insert_before_scene_end,
    mask_layer_ref,
    mask_value,
    output_frame_map,
    parse_vec3,
    resolve_path,
    selected_frames,
    source_entry,
    source_luma,
    write_command_list,
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
from composite_mitsuba_secondary_layer import parse_camera, project


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to add water mesh response")


def xml_path(path):
    return os.path.abspath(path).replace(os.sep, "/")


def parse_face_token(token):
    head = token.split("/", 1)[0]
    return int(head)


def read_obj_mesh(path):
    vertices = []
    faces = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                indices = [parse_face_token(token) for token in line.split()[1:]]
                if len(indices) >= 3:
                    faces.append(indices)
    return vertices, faces


def face_centroid(face, vertices):
    count = float(len(face))
    return (
        sum(vertices[index - 1][0] for index in face) / count,
        sum(vertices[index - 1][1] for index in face) / count,
        sum(vertices[index - 1][2] for index in face) / count,
    )


def select_faces(vertices, faces, camera, mask, source, args):
    width = int(camera.get("width") or mask.size[0])
    height = int(camera.get("height") or mask.size[1])
    selected = []
    for face_index, face in enumerate(faces):
        if args.face_stride > 1 and face_index % args.face_stride != 0:
            continue
        centroid = face_centroid(face, vertices)
        projected = project(centroid, camera, width, height)
        if projected is None:
            continue
        px, py, depth = projected
        value = mask_value(mask, px, py, width, height, args.mask_sample_radius)
        if value < args.mask_threshold:
            continue
        luma = source_luma(source, px, py, width, height)
        if luma is not None and (luma < args.source_luma_min or luma > args.source_luma_max):
            continue
        score = value + max(0.0, (luma or 0.0) - args.source_luma_min) * 0.01 - depth * args.depth_penalty
        selected.append({
            "face": face,
            "face_index": face_index,
            "centroid": centroid,
            "screen": (px, py),
            "depth": depth,
            "mask_value": value,
            "source_luma": luma,
            "score": score,
        })
    selected.sort(key=lambda item: item["score"], reverse=True)
    if args.face_limit > 0:
        selected = selected[:args.face_limit]
    return selected


def write_selected_obj(path, vertices, selected, y_lift, reverse_faces):
    used = []
    seen = set()
    for item in selected:
        for index in item["face"]:
            if index not in seen:
                seen.add(index)
                used.append(index)
    remap = {old: new for new, old in enumerate(used, start=1)}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("# LSFS masked water mesh response\n")
        handle.write(f"# selected_faces {len(selected)}\n")
        for old_index in used:
            x, y, z = vertices[old_index - 1]
            handle.write(f"v {fmt(x)} {fmt(y + y_lift)} {fmt(z)}\n")
        for item in selected:
            face = list(reversed(item["face"])) if reverse_faces else item["face"]
            handle.write("f " + " ".join(str(remap[index]) for index in face) + "\n")
    return {
        "vertices": len(used),
        "faces": len(selected),
        "bytes": os.path.getsize(path),
    }


def mesh_response_block(mesh_path, args, frame_index):
    shape_id = f"lsfs_s419_water_mesh_response_{frame_index:04d}"
    lines = [
        f'  <shape type="obj" id="{shape_id}">',
        f'    <string name="filename" value="{xml_path(mesh_path)}"/>',
        '    <boolean name="face_normals" value="true"/>',
    ]
    if args.bsdf_mode == "roughdielectric":
        lines.extend([
            '    <bsdf type="roughdielectric">',
            '      <string name="distribution" value="ggx"/>',
            f'      <float name="alpha" value="{fmt(args.rough_alpha)}"/>',
            f'      <float name="int_ior" value="{fmt(args.int_ior)}"/>',
            f'      <float name="ext_ior" value="{fmt(args.ext_ior)}"/>',
            '    </bsdf>',
        ])
    elif max(args.reflectance_vec) > 0.0:
        lines.extend([
            '    <bsdf type="diffuse">',
            f'      <rgb name="reflectance" value="{csv3(args.reflectance_vec)}"/>',
            '    </bsdf>',
        ])
    if max(args.radiance_vec) > 0.0:
        lines.extend([
            '    <emitter type="area">',
            f'      <rgb name="radiance" value="{csv3(args.radiance_vec)}"/>',
            '    </emitter>',
        ])
    lines.append("  </shape>")
    return "\n".join(lines)


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    response = export.get("water_mask_mesh_response") or {}
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
        "## Water Mesh Response",
        "",
        f"- Face limit: `{response.get('face_limit')}`",
        f"- Face stride: `{response.get('face_stride')}`",
        f"- Y lift: `{response.get('y_lift')}`",
        f"- BSDF mode: `{response.get('bsdf_mode')}`",
        f"- Rough alpha: `{response.get('rough_alpha')}`",
        f"- IOR: `{response.get('ext_ior')} -> {response.get('int_ior')}`",
        f"- Radiance: `{response.get('radiance')}`",
        f"- Reflectance: `{response.get('reflectance')}`",
        f"- Mask threshold: `{response.get('mask_threshold')}`",
        f"- Source luma gate: `{response.get('source_luma_min')}..{response.get('source_luma_max')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Candidate faces: `{checks.get('candidate_faces')}`",
        f"- Mesh response faces: `{checks.get('mesh_response_faces')}`",
        f"- Mesh response vertices: `{checks.get('mesh_response_vertices')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Water Faces | Selected Faces | Mesh Faces | Mask | XML Scene |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("water_mask_mesh_response") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('water_faces')} | "
            f"{item.get('candidate_faces')} | {item.get('mesh_faces')} | "
            f"`{item.get('mask_layer_repo_path')}` | `{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def add_mesh_response(args):
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
        "mesh_response_faces": 0,
        "mesh_response_vertices": 0,
        "mesh_response_bytes": 0,
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
        mask = Image.open(mask_path).convert("L")
        source = Image.open(source_path).convert("RGB") if source_path and os.path.isfile(source_path) else None
        camera = parse_camera(source_xml)
        selected = select_faces(vertices, faces, camera, mask, source, args)
        if not selected:
            failures.append({"output_frame": output_frame, "missing": [{"role": "selected_faces", "path": None}]})
            continue
        base_name = f"frame_{index:04d}"
        mesh_out = os.path.join(mesh_dir, f"{base_name}_water_mask_response.obj")
        mesh_stats = write_selected_obj(mesh_out, vertices, selected, args.y_lift, args.reverse_faces)
        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        block = mesh_response_block(mesh_out, args, index)
        patched = insert_before_scene_end(xml_text, block)
        patched = add_response_comment(
            patched,
            f"<!-- S419 water_mask_mesh_response faces={len(selected)} source_faces={len(faces)} -->",
        )
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["candidate_faces"] += len(selected)
        totals["mesh_response_faces"] += mesh_stats["faces"]
        totals["mesh_response_vertices"] += mesh_stats["vertices"]
        totals["mesh_response_bytes"] += mesh_stats["bytes"]

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
        out_frame["water_mask_mesh_response"] = {
            "enabled": True,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "response_mesh_repo_path": posix_rel(mesh_out, root),
            "response_mesh_sha256": sha256_file(mesh_out),
            "mask_layer_path": mask_path,
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "source_repo_path": posix_rel(source_path, root) if source_path else None,
            "water_vertices": len(vertices),
            "water_faces": len(faces),
            "candidate_faces": len(selected),
            "mesh_faces": mesh_stats["faces"],
            "mesh_vertices": mesh_stats["vertices"],
            "mesh_bytes": mesh_stats["bytes"],
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
        "status": "ready" if frames and not failures and totals["mesh_response_faces"] > 0 else "review",
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
        "water_mask_mesh_response": {
            "enabled": True,
            "face_limit": args.face_limit,
            "face_stride": args.face_stride,
            "y_lift": args.y_lift,
            "bsdf_mode": args.bsdf_mode,
            "rough_alpha": args.rough_alpha,
            "int_ior": args.int_ior,
            "ext_ior": args.ext_ior,
            "radiance": args.radiance_vec,
            "reflectance": args.reflectance_vec,
            "reverse_faces": args.reverse_faces,
            "mask_threshold": args.mask_threshold,
            "mask_sample_radius": args.mask_sample_radius,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["water_mask_mesh_response_enabled"] = True
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
        f"faces={totals['mesh_response_faces']} candidates={totals['candidate_faces']} "
        f"export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Add a masked water-surface mesh response to a Mitsuba XML export")
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
    parser.add_argument("--y-lift", type=float, default=0.025)
    parser.add_argument("--bsdf-mode", choices=["diffuse", "roughdielectric"], default="diffuse")
    parser.add_argument("--rough-alpha", type=float, default=0.006)
    parser.add_argument("--int-ior", type=float, default=1.333)
    parser.add_argument("--ext-ior", type=float, default=1.0)
    parser.add_argument("--radiance", default="0.65,0.85,1.10")
    parser.add_argument("--reflectance", default="0.0,0.0,0.0")
    parser.add_argument("--reverse-faces", action="store_true")
    parser.add_argument("--depth-penalty", type=float, default=0.01)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S419 Mitsuba Water Mask Mesh Response")
    parser.add_argument("--next", default="Render and compare this masked water-mesh response against S417 light-only, WP4, S409 SF12_H18, and S401 CR21.")
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
    if args.depth_penalty < 0.0:
        parser.error("depth-penalty must be non-negative")
    if args.rough_alpha <= 0.0:
        parser.error("rough-alpha must be positive")
    if args.int_ior <= 0.0 or args.ext_ior <= 0.0:
        parser.error("int-ior and ext-ior must be positive")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    args.reflectance_vec = parse_vec3(args.reflectance, "reflectance")
    if min(args.radiance_vec) < 0.0 or min(args.reflectance_vec) < 0.0:
        parser.error("radiance and reflectance values must be non-negative")
    if max(args.reflectance_vec) > 1.0:
        parser.error("diffuse reflectance values must be in [0, 1]")
    add_mesh_response(args)


if __name__ == "__main__":
    main()
