#!/usr/bin/env python
"""Add clustered water-surface disk emitters from a projected mask."""

import argparse
import copy
import math
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
    mask_layer_ref,
    mask_value,
    output_frame_map,
    parse_vec3,
    read_obj_vertices,
    resolve_path,
    selected_frames,
    source_entry,
    source_luma,
    insert_before_scene_end,
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
        raise SystemExit("Pillow is required to add water patch emitters")


def collect_candidates(vertices, camera, mask, source, args):
    candidates = []
    width = int(camera.get("width") or mask.size[0])
    height = int(camera.get("height") or mask.size[1])
    for vertex in vertices:
        projected = project(vertex, camera, width, height)
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
        candidates.append({
            "position": vertex,
            "screen": (px, py),
            "depth": depth,
            "mask_value": value,
            "source_luma": luma,
            "score": score,
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    if args.candidate_limit > 0:
        candidates = candidates[:args.candidate_limit]
    return candidates


def weighted_average(items, key, weight_sum):
    return sum(item[key] * item["cluster_weight"] for item in items) / weight_sum


def cluster_candidates(candidates, args):
    patches = []
    used = [False] * len(candidates)
    radius2 = args.cluster_screen_radius * args.cluster_screen_radius
    for seed_index, seed in enumerate(candidates):
        if len(patches) >= args.patch_limit:
            break
        if used[seed_index]:
            continue
        sx, sy = seed["screen"]
        cluster = []
        for index, item in enumerate(candidates):
            if used[index]:
                continue
            px, py = item["screen"]
            if (px - sx) ** 2 + (py - sy) ** 2 <= radius2:
                item = copy.deepcopy(item)
                item["cluster_weight"] = max(1.0, float(item["mask_value"])) + max(0.0, (item.get("source_luma") or 0.0) - args.source_luma_min)
                cluster.append((index, item))
        if len(cluster) < args.min_cluster_candidates:
            continue
        for index, _item in cluster:
            used[index] = True
        items = [item for _index, item in cluster]
        weight_sum = sum(item["cluster_weight"] for item in items)
        center = [
            sum(item["position"][axis] * item["cluster_weight"] for item in items) / weight_sum
            for axis in range(3)
        ]
        screen = [
            weighted_average([{"screen_x": item["screen"][0], "cluster_weight": item["cluster_weight"]} for item in items], "screen_x", weight_sum),
            weighted_average([{"screen_y": item["screen"][1], "cluster_weight": item["cluster_weight"]} for item in items], "screen_y", weight_sum),
        ]
        depth = sum(item["depth"] * item["cluster_weight"] for item in items) / weight_sum
        radius = args.base_radius + args.radius_per_sqrt_candidate * math.sqrt(float(len(items)))
        if args.depth_radius_scale > 0.0:
            radius *= max(0.5, min(2.0, args.reference_depth / max(1.0, depth))) ** args.depth_radius_scale
        radius = max(args.min_radius, min(args.max_radius, radius))
        patches.append({
            "position": center,
            "screen": screen,
            "depth": depth,
            "radius": radius,
            "count": len(items),
            "max_mask_value": max(item["mask_value"] for item in items),
            "mean_source_luma": sum((item.get("source_luma") or 0.0) for item in items) / float(len(items)),
            "score": sum(item["score"] for item in items) / float(len(items)),
        })
    return patches


def patch_emitter_block(patches, args, frame_index, camera):
    lines = []
    radiance = csv3(args.radiance_vec)
    target = csv3(camera.get("origin") or [0.0, 0.0, 0.0])
    up = csv3(camera.get("up") or [0.0, 1.0, 0.0])
    for index, patch in enumerate(patches):
        x, y, z = patch["position"]
        y += args.y_lift
        rx = patch["radius"]
        ry = patch["radius"] * args.aspect
        lines.extend([
            f'  <shape type="disk" id="lsfs_s418_water_patch_{frame_index:04d}_{index:03d}">',
            '    <transform name="to_world">',
            f'      <lookat origin="{csv3([x, y, z])}" target="{target}" up="{up}"/>',
            f'      <scale x="{fmt(rx)}" y="{fmt(ry)}" z="1"/>',
            '    </transform>',
            '    <emitter type="area">',
            f'      <rgb name="radiance" value="{radiance}"/>',
            '    </emitter>',
            '  </shape>',
        ])
    return "\n".join(lines)


def markdown_report(export, export_path, root, next_text):
    checks = export.get("checks", {})
    response = export.get("water_mask_patches") or {}
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
        "## Water Patch Emitters",
        "",
        f"- Patch limit: `{response.get('patch_limit')}`",
        f"- Cluster screen radius: `{response.get('cluster_screen_radius')}`",
        f"- Radius range: `{response.get('min_radius')}..{response.get('max_radius')}`",
        f"- Radiance: `{response.get('radiance')}`",
        f"- Mask threshold: `{response.get('mask_threshold')}`",
        f"- Source luma gate: `{response.get('source_luma_min')}..{response.get('source_luma_max')}`",
        "",
        "## Checks",
        "",
        f"- Frames exported: `{checks.get('frames_exported')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Candidate vertices: `{checks.get('candidate_vertices')}`",
        f"- Patches inserted: `{checks.get('patches_inserted')}`",
        f"- XML scene bytes: `{format_bytes(checks.get('xml_scene_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Vertices | Candidates | Patches | Mask | XML Scene |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = export.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        item = frame.get("water_mask_patches") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {item.get('vertices_tested')} | "
            f"{item.get('candidate_vertices')} | {item.get('patches_inserted')} | "
            f"`{item.get('mask_layer_repo_path')}` | `{(frame.get('xml_scene') or {}).get('repo_path')}` |"
        )
    if export.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in export["failures"]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def add_patches(args):
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
    os.makedirs(scene_dir, exist_ok=True)
    os.makedirs(render_dir, exist_ok=True)

    mask_frames = output_frame_map(mask_source.get("frames") or [])
    frames = []
    failures = []
    totals = {
        "xml_scene_bytes": 0,
        "vertices_tested": 0,
        "candidate_vertices": 0,
        "patches_inserted": 0,
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

        vertices = read_obj_vertices(water_mesh, args.vertex_stride)
        mask = Image.open(mask_path).convert("L")
        source = Image.open(source_path).convert("RGB") if source_path and os.path.isfile(source_path) else None
        camera = parse_camera(source_xml)
        candidates = collect_candidates(vertices, camera, mask, source, args)
        patches = cluster_candidates(candidates, args)
        with open(source_xml, encoding="utf-8") as f:
            xml_text = f.read()
        block = patch_emitter_block(patches, args, index, camera)
        patched = insert_before_scene_end(xml_text, block)
        patched = add_response_comment(
            patched,
            f"<!-- S418 water_mask_patch_emitters patches={len(patches)} candidates={len(candidates)} -->",
        )
        base_name = f"frame_{index:04d}"
        xml_out = os.path.join(scene_dir, f"{base_name}.xml")
        write_text(xml_out, patched)
        totals["xml_scene_bytes"] += os.path.getsize(xml_out)
        totals["vertices_tested"] += len(vertices)
        totals["candidate_vertices"] += len(candidates)
        totals["patches_inserted"] += len(patches)

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
        out_frame["water_mask_patches"] = {
            "enabled": True,
            "water_mesh_repo_path": posix_rel(water_mesh, root),
            "mask_layer_path": mask_path,
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "source_repo_path": posix_rel(source_path, root) if source_path else None,
            "vertices_tested": len(vertices),
            "candidate_vertices": len(candidates),
            "patches_inserted": len(patches),
            "patch_samples": [
                {
                    "position": [float(v) for v in patch["position"]],
                    "screen": [float(patch["screen"][0]), float(patch["screen"][1])],
                    "depth": float(patch["depth"]),
                    "radius": float(patch["radius"]),
                    "candidate_count": int(patch["count"]),
                    "max_mask_value": int(patch["max_mask_value"]),
                    "mean_source_luma": float(patch["mean_source_luma"]),
                }
                for patch in patches[:8]
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
        "status": "ready" if frames and not failures and totals["patches_inserted"] > 0 else "review",
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
        "water_mask_patches": {
            "enabled": True,
            "patch_limit": args.patch_limit,
            "candidate_limit": args.candidate_limit,
            "cluster_screen_radius": args.cluster_screen_radius,
            "min_cluster_candidates": args.min_cluster_candidates,
            "min_radius": args.min_radius,
            "base_radius": args.base_radius,
            "radius_per_sqrt_candidate": args.radius_per_sqrt_candidate,
            "max_radius": args.max_radius,
            "aspect": args.aspect,
            "y_lift": args.y_lift,
            "radiance": args.radiance_vec,
            "mask_threshold": args.mask_threshold,
            "mask_sample_radius": args.mask_sample_radius,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
            "vertex_stride": args.vertex_stride,
        },
        "next": args.next,
    })
    export["render_settings"] = copy.deepcopy(base.get("render_settings") or {})
    export["render_settings"]["water_mask_patch_emitters_enabled"] = True
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
        f"patches={totals['patches_inserted']} candidates={totals['candidate_vertices']} "
        f"export={export_path}"
    )
    if export["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Add clustered water-surface Mitsuba disk emitters from a mask")
    parser.add_argument("base_export")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--patch-limit", type=int, default=16)
    parser.add_argument("--candidate-limit", type=int, default=2000)
    parser.add_argument("--vertex-stride", type=int, default=1)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--mask-sample-radius", type=int, default=5)
    parser.add_argument("--source-luma-min", type=float, default=0.0)
    parser.add_argument("--source-luma-max", type=float, default=255.0)
    parser.add_argument("--cluster-screen-radius", type=float, default=42.0)
    parser.add_argument("--min-cluster-candidates", type=int, default=1)
    parser.add_argument("--min-radius", type=float, default=0.08)
    parser.add_argument("--base-radius", type=float, default=0.18)
    parser.add_argument("--radius-per-sqrt-candidate", type=float, default=0.018)
    parser.add_argument("--max-radius", type=float, default=0.55)
    parser.add_argument("--aspect", type=float, default=0.55)
    parser.add_argument("--y-lift", type=float, default=0.03)
    parser.add_argument("--radiance", default="0.55,0.75,0.95")
    parser.add_argument("--reference-depth", type=float, default=45.0)
    parser.add_argument("--depth-radius-scale", type=float, default=0.0)
    parser.add_argument("--depth-penalty", type=float, default=0.01)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S418 Mitsuba Water Mask Patch Emitters")
    parser.add_argument("--next", default="Render and compare this clustered water-patch candidate against WP4, S417 light-only, S409 SF12_H18, and S401 CR21.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.patch_limit < 0:
        parser.error("patch-limit must be non-negative")
    if args.candidate_limit < 0:
        parser.error("candidate-limit must be non-negative")
    if args.vertex_stride <= 0:
        parser.error("vertex-stride must be positive")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.mask_sample_radius < 0:
        parser.error("mask-sample-radius must be non-negative")
    if args.source_luma_min < 0.0 or args.source_luma_max > 255.0:
        parser.error("source luma bounds must be in [0, 255]")
    if args.source_luma_min > args.source_luma_max:
        parser.error("source-luma-min cannot exceed source-luma-max")
    if args.cluster_screen_radius <= 0.0:
        parser.error("cluster-screen-radius must be positive")
    if args.min_cluster_candidates <= 0:
        parser.error("min-cluster-candidates must be positive")
    if args.min_radius <= 0.0 or args.base_radius <= 0.0 or args.max_radius <= 0.0:
        parser.error("radius values must be positive")
    if args.min_radius > args.max_radius:
        parser.error("min-radius cannot exceed max-radius")
    if args.radius_per_sqrt_candidate < 0.0:
        parser.error("radius-per-sqrt-candidate must be non-negative")
    if args.aspect <= 0.0:
        parser.error("aspect must be positive")
    if args.reference_depth <= 0.0:
        parser.error("reference-depth must be positive")
    if args.depth_radius_scale < 0.0:
        parser.error("depth-radius-scale must be non-negative")
    if args.depth_penalty < 0.0:
        parser.error("depth-penalty must be non-negative")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    if min(args.radiance_vec) < 0.0:
        parser.error("radiance values must be non-negative")
    add_patches(args)


if __name__ == "__main__":
    main()
