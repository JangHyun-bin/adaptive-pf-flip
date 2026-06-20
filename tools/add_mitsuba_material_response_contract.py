#!/usr/bin/env python
"""Consume an LSFS Mitsuba material-response contract into water response meshes."""

import argparse
import copy
import os
from datetime import datetime, timezone

from add_mitsuba_water_mask_highlights import add_response_comment, insert_before_scene_end
from add_mitsuba_water_mask_mesh_response import (
    face_centroid,
    grow_selected_faces,
    read_obj_mesh,
    write_selected_obj,
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


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def selected_frames(frames, requested=None):
    if not frames:
        return []
    if requested is None or requested <= 0 or requested >= len(frames):
        return frames
    if requested == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(requested - 1)) for i in range(requested)))
    return [frames[index] for index in indices]


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def controls_by_output(controls):
    grouped = {}
    for control in controls or []:
        grouped.setdefault(control.get("output_frame"), []).append(control)
    for values in grouped.values():
        values.sort(key=lambda item: (int(item.get("rank") or 0), item.get("control_id") or ""))
    return grouped


def frame_path(frame, key):
    entry = frame.get(key) or {}
    return entry.get("path") or entry.get("repo_path")


def fmt(value):
    return f"{float(value):.8g}"


def csv3(values):
    return ", ".join(fmt(item) for item in values)


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def xml_path(path):
    return os.path.abspath(path).replace(os.sep, "/")


def source_entry(path, root, label, payload=None):
    resolved = require_file(path, label)
    entry = {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
        entry["status"] = payload.get("status")
    return entry


def parse_vec3(value, label):
    parts = [part.strip() for part in str(value).split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{label} must be r,g,b")
    return [float(part) for part in parts]


def padded_bbox(control, args):
    x0, y0, x1, y1 = [float(item) for item in (control.get("bbox_px") or control.get("bbox") or [0, 0, -1, -1])]
    response = control.get("native_response") or {}
    pad = args.bbox_pad + float(response.get("mask_blur_px") or 0.0) * args.blur_pad_scale
    return [x0 - pad, y0 - pad, x1 + pad, y1 + pad]


def point_in_bbox(px, py, bbox):
    return bbox[0] <= px <= bbox[2] and bbox[1] <= py <= bbox[3]


def select_faces_for_control(vertices, faces, camera, control, args):
    width = int(camera.get("width") or 960)
    height = int(camera.get("height") or 540)
    bbox = padded_bbox(control, args)
    selected = []
    fit_strength = float(control.get("fit_strength") or 0.0)
    for face_index, face in enumerate(faces):
        if args.face_stride > 1 and face_index % args.face_stride != 0:
            continue
        centroid = face_centroid(face, vertices)
        projected = project(centroid, camera, width, height)
        if projected is None:
            continue
        px, py, depth = projected
        if not point_in_bbox(px, py, bbox):
            continue
        cx = (bbox[0] + bbox[2]) * 0.5
        cy = (bbox[1] + bbox[3]) * 0.5
        dx = abs(px - cx) / max(1.0, (bbox[2] - bbox[0]) * 0.5)
        dy = abs(py - cy) / max(1.0, (bbox[3] - bbox[1]) * 0.5)
        center_weight = max(0.0, 1.0 - 0.5 * (dx + dy))
        score = center_weight + fit_strength * args.strength_score_gain - depth * args.depth_penalty
        selected.append({
            "face": face,
            "face_index": face_index,
            "centroid": centroid,
            "screen": (px, py),
            "depth": depth,
            "score": score,
            "control_id": control.get("control_id"),
        })
    selected.sort(key=lambda item: item["score"], reverse=True)
    if args.face_limit > 0:
        selected = selected[:args.face_limit]
    return selected


def response_color(control, args, key, fallback):
    response = control.get("native_response") or {}
    strength = float(control.get("fit_strength") or 0.0)
    albedo = float(response.get("albedo_lift") or 0.0)
    scatter = float(response.get("scattering_scale") or 0.0)
    if key == "reflectance":
        base = args.reflectance_vec
        scale = strength * args.reflectance_strength_gain + albedo * args.albedo_gain
    else:
        base = args.radiance_vec
        scale = strength * args.radiance_strength_gain + scatter * args.scattering_gain
    values = [clamp(channel * scale, 0.0, args.max_channel_value) for channel in base]
    if max(values) <= 0.0:
        return fallback
    return values


def response_mesh_block(mesh_path, control, args, frame_index, control_index):
    safe_control = str(control.get("control_id") or f"c{control_index:02d}").replace("-", "_")
    shape_id = f"lsfs_s482_material_response_{frame_index:04d}_{safe_control}"
    reflectance = response_color(control, args, "reflectance", [0.0, 0.0, 0.0])
    radiance = response_color(control, args, "radiance", [0.0, 0.0, 0.0])
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
    else:
        lines.extend([
            '    <bsdf type="diffuse">',
            f'      <rgb name="reflectance" value="{csv3(reflectance)}"/>',
            '    </bsdf>',
        ])
    if max(radiance) > 0.0:
        lines.extend([
            '    <emitter type="area">',
            f'      <rgb name="radiance" value="{csv3(radiance)}"/>',
            '    </emitter>',
        ])
    lines.append("  </shape>")
    return "\n".join(lines)


def write_command_list(path, frames, command, mode):
    mode_arg = f" -m {mode}" if mode else ""
    lines = []
    for frame in frames:
        xml_scene = (frame.get("xml_scene") or {}).get("repo_path")
        output = (frame.get("expected_output") or {}).get("repo_path")
        lines.append(f'{command}{mode_arg} "{xml_scene}" -o "{output}"')
    write_text(path, "\n".join(lines) + "\n")


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks") or {}
    settings = export.get("material_response_contract_consumer") or {}
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
        f"- Material response contract: `{export['sources']['material_response_contract']['repo_path']}`",
        "",
        "## Material Response Contract",
        "",
        f"- Face limit: `{settings.get('face_limit')}`",
        f"- Face grow steps: `{settings.get('face_grow_steps')}`",
        f"- Face grow max faces: `{settings.get('face_grow_max_faces')}`",
        f"- Face stride: `{settings.get('face_stride')}`",
        f"- BBox pad: `{settings.get('bbox_pad')}`",
        f"- Blur pad scale: `{settings.get('blur_pad_scale')}`",
        f"- BSDF mode: `{settings.get('bsdf_mode')}`",
        f"- Reflectance base: `{settings.get('reflectance')}`",
        f"- Radiance base: `{settings.get('radiance')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Contract frames matched: `{checks.get('contract_frames_matched')}`",
        f"- Contract frames missing ignored: `{checks.get('contract_frames_missing_ignored')}`",
        f"- Controls consumed: `{checks.get('controls_consumed')}`",
        f"- Candidate faces: `{checks.get('candidate_faces')}`",
        f"- Mesh response faces: `{checks.get('mesh_response_faces')}`",
        f"- Mesh response vertices: `{checks.get('mesh_response_vertices')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Controls | Mesh Faces | Ignored | XML Scene |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("material_response_contract") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('controls_consumed')} | "
            f"{item.get('mesh_response_faces')} | `{item.get('missing_contract_frame_ignored')}` | "
            f"`{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def add_material_response(args):
    root = os.getcwd()
    base_export_path = require_file(args.base_export, "base Mitsuba XML export")
    contract_path = require_file(args.material_response_contract, "material response contract")
    base = read_json(base_export_path)
    contract = read_json(contract_path)
    if base.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.base_export}: expected lsfs_mitsuba_xml_export schema")
    if base.get("status") != "ready":
        raise SystemExit(f"{args.base_export}: base export status is {base.get('status')!r}")
    if contract.get("schema") != "lsfs_mitsuba_material_response_contract":
        raise SystemExit(f"{args.material_response_contract}: expected lsfs_mitsuba_material_response_contract schema")
    if contract.get("status") != "ready":
        raise SystemExit(f"{args.material_response_contract}: contract status is {contract.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    scene_dir = os.path.join(out_dir, "scenes")
    render_dir = os.path.join(out_dir, "renders")
    mesh_dir = os.path.join(out_dir, "meshes")
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)
    os.makedirs(mesh_dir, exist_ok=True)

    controls_map = controls_by_output(contract.get("controls") or [])
    frames = []
    failures = []
    mesh_cache = {}
    totals = {
        "xml_scene_bytes": 0,
        "contract_frames_matched": 0,
        "contract_frames_missing_ignored": 0,
        "controls_consumed": 0,
        "candidate_faces": 0,
        "grown_response_faces": 0,
        "mesh_response_faces": 0,
        "mesh_response_vertices": 0,
        "mesh_response_bytes": 0,
    }

    for index, frame in enumerate(selected_frames(base.get("frames") or [], args.frames)):
        output_frame = frame.get("output_frame")
        source_xml = resolve_path(frame_path(frame, "xml_scene"))
        water_mesh = resolve_path(frame_path(frame, "water_mesh"))
        controls = controls_map.get(output_frame, [])
        missing = []
        for role, path in (("source_xml", source_xml), ("water_mesh", water_mesh)):
            if role == "water_mesh" and not controls and args.allow_missing_contract_frames:
                continue
            if not path or not os.path.isfile(path):
                missing.append({"role": role, "path": path})
        if not controls:
            if args.allow_missing_contract_frames:
                totals["contract_frames_missing_ignored"] += 1
            else:
                missing.append({"role": "contract_frame", "path": f"output_frame={output_frame}"})
        if missing:
            failures.append({"output_frame": output_frame, "missing": missing})
            continue

        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        frame_mesh_faces = 0
        frame_mesh_vertices = 0
        frame_candidate_faces = 0
        frame_meshes = []
        control_summaries = []
        if controls:
            if water_mesh not in mesh_cache:
                mesh_cache[water_mesh] = read_obj_mesh(water_mesh)
            vertices, faces = mesh_cache[water_mesh]
            camera = parse_camera(source_xml)
            totals["contract_frames_matched"] += 1
            blocks = []
            for control_index, control in enumerate(controls):
                selected = select_faces_for_control(vertices, faces, camera, control, args)
                if not selected:
                    failures.append({
                        "output_frame": output_frame,
                        "missing": [{"role": "selected_faces", "path": control.get("control_id")}],
                    })
                    continue
                original_count = len(selected)
                selected = grow_selected_faces(vertices, faces, selected, camera, args)
                safe_control = str(control.get("control_id") or f"control_{control_index:02d}").replace("-", "_")
                mesh_out = os.path.join(mesh_dir, f"frame_{index:04d}_{safe_control}.obj")
                mesh_stats = write_selected_obj(mesh_out, vertices, selected, args.y_lift, args.reverse_faces)
                blocks.append(response_mesh_block(mesh_out, control, args, index, control_index))
                frame_meshes.append(posix_rel(mesh_out, root))
                frame_candidate_faces += original_count
                frame_mesh_faces += mesh_stats["faces"]
                frame_mesh_vertices += mesh_stats["vertices"]
                totals["controls_consumed"] += 1
                totals["candidate_faces"] += original_count
                totals["grown_response_faces"] += len(selected)
                totals["mesh_response_faces"] += mesh_stats["faces"]
                totals["mesh_response_vertices"] += mesh_stats["vertices"]
                totals["mesh_response_bytes"] += mesh_stats["bytes"]
                control_summaries.append({
                    "control_id": control.get("control_id"),
                    "source_faces": original_count,
                    "mesh_faces": mesh_stats["faces"],
                    "mesh_vertices": mesh_stats["vertices"],
                    "response_mesh_repo_path": posix_rel(mesh_out, root),
                    "bbox_px": control.get("bbox_px"),
                    "fit_strength": control.get("fit_strength"),
                    "native_response": control.get("native_response"),
                    "face_samples": [
                        {
                            "centroid": [float(v) for v in item["centroid"]],
                            "screen": [float(item["screen"][0]), float(item["screen"][1])],
                            "depth": float(item["depth"]),
                        }
                        for item in selected[:8]
                    ],
                })
            if blocks:
                xml_text = insert_before_scene_end(xml_text, "\n".join(blocks))
        patched = add_response_comment(
            xml_text,
            f"<!-- S482 material_response_contract controls={len(controls)} faces={frame_mesh_faces} -->",
        )
        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)

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
        out_frame["material_response_contract"] = {
            "enabled": bool(controls),
            "contract_output_frame": output_frame if controls else None,
            "missing_contract_frame_ignored": not controls and args.allow_missing_contract_frames,
            "water_mesh_repo_path": posix_rel(water_mesh, root) if water_mesh else None,
            "controls_consumed": len(control_summaries),
            "candidate_faces": frame_candidate_faces,
            "mesh_response_faces": frame_mesh_faces,
            "mesh_response_vertices": frame_mesh_vertices,
            "response_meshes": frame_meshes,
            "controls": control_summaries,
        }
        frames.append(out_frame)

    command_list = os.path.join(out_dir, "mitsuba_render_commands.txt")
    write_command_list(
        command_list,
        frames,
        (base.get("render_settings") or {}).get("mitsuba_command") or "mitsuba",
        (base.get("render_settings") or {}).get("mitsuba_mode"),
    )
    status = "ready" if frames and not failures and totals["mesh_response_faces"] > 0 else "review"
    export = copy.deepcopy(base)
    export.update({
        "schema": "lsfs_mitsuba_xml_export",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "command_list": {
            "path": command_list,
            "repo_path": posix_rel(command_list, root),
            "sha256": sha256_file(command_list),
            "size": os.path.getsize(command_list),
        },
        "sources": {
            "base_export": source_entry(base_export_path, root, "base Mitsuba XML export", base),
            "material_response_contract": source_entry(contract_path, root, "material response contract", contract),
        },
        "frames": frames,
        "failures": failures,
        "material_response_contract_consumer": {
            "enabled": True,
            "allow_missing_contract_frames": args.allow_missing_contract_frames,
            "face_limit": args.face_limit,
            "face_grow_steps": args.face_grow_steps,
            "face_grow_max_faces": args.face_grow_max_faces,
            "face_stride": args.face_stride,
            "bbox_pad": args.bbox_pad,
            "blur_pad_scale": args.blur_pad_scale,
            "strength_score_gain": args.strength_score_gain,
            "depth_penalty": args.depth_penalty,
            "y_lift": args.y_lift,
            "bsdf_mode": args.bsdf_mode,
            "rough_alpha": args.rough_alpha,
            "int_ior": args.int_ior,
            "ext_ior": args.ext_ior,
            "reflectance": args.reflectance_vec,
            "radiance": args.radiance_vec,
            "reflectance_strength_gain": args.reflectance_strength_gain,
            "radiance_strength_gain": args.radiance_strength_gain,
            "albedo_gain": args.albedo_gain,
            "scattering_gain": args.scattering_gain,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["material_response_contract_enabled"] = True
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
        f"status={status} frames={len(frames)} controls={totals['controls_consumed']} "
        f"faces={totals['mesh_response_faces']} export={export_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Add material-response contract meshes to a Mitsuba XML export")
    parser.add_argument("base_export")
    parser.add_argument("material_response_contract")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--allow-missing-contract-frames", action="store_true")
    parser.add_argument("--face-limit", type=int, default=550)
    parser.add_argument("--face-grow-steps", type=int, default=0)
    parser.add_argument("--face-grow-max-faces", type=int, default=900)
    parser.add_argument("--face-stride", type=int, default=1)
    parser.add_argument("--bbox-pad", type=float, default=4.0)
    parser.add_argument("--blur-pad-scale", type=float, default=1.0)
    parser.add_argument("--strength-score-gain", type=float, default=1.0)
    parser.add_argument("--depth-penalty", type=float, default=0.01)
    parser.add_argument("--y-lift", type=float, default=0.014)
    parser.add_argument("--bsdf-mode", choices=["diffuse", "roughdielectric"], default="roughdielectric")
    parser.add_argument("--rough-alpha", type=float, default=0.012)
    parser.add_argument("--int-ior", type=float, default=1.333)
    parser.add_argument("--ext-ior", type=float, default=1.0)
    parser.add_argument("--reflectance", default="0.55,0.72,1.0")
    parser.add_argument("--radiance", default="0,0,0")
    parser.add_argument("--reflectance-strength-gain", type=float, default=0.15)
    parser.add_argument("--radiance-strength-gain", type=float, default=0.30)
    parser.add_argument("--albedo-gain", type=float, default=0.55)
    parser.add_argument("--scattering-gain", type=float, default=1.25)
    parser.add_argument("--max-channel-value", type=float, default=1.0)
    parser.add_argument("--reverse-faces", action="store_true")
    parser.add_argument("--report")
    parser.add_argument("--title", default="S482 Mitsuba Material Response Contract Consumer")
    parser.add_argument("--next", default="Render and compare this light-plus-material native candidate against the S478 p4 proxy gate.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("frames must be non-negative")
    if args.face_limit < 0:
        parser.error("face-limit must be non-negative")
    if args.face_grow_steps < 0:
        parser.error("face-grow-steps must be non-negative")
    if args.face_grow_max_faces < 0:
        parser.error("face-grow-max-faces must be non-negative")
    if args.face_stride <= 0:
        parser.error("face-stride must be positive")
    if args.rough_alpha <= 0.0:
        parser.error("rough-alpha must be positive")
    if args.int_ior <= 0.0 or args.ext_ior <= 0.0:
        parser.error("ior values must be positive")
    if args.max_channel_value < 0.0:
        parser.error("max-channel-value must be non-negative")
    args.reflectance_vec = parse_vec3(args.reflectance, "reflectance")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    add_material_response(args)


if __name__ == "__main__":
    main()
