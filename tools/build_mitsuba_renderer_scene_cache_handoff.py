#!/usr/bin/env python
"""Build a renderer scene-cache handoff from LSFS scene and visual caches.

The handoff intentionally keeps the heavy simulation cache files and texture
layers in place. It writes a compact manifest that maps renderer-neutral scene
assets (camera, particles, phase cells, optional water meshes) onto the current
low-frequency visual texture contract.
"""

import argparse
import os
import shutil
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


REQUIRED_TEXTURES = [
    "base_rgb",
    "target_rgb",
    "parity_composite_rgb",
    "applied_positive_delta_rgb",
    "applied_negative_delta_rgb",
    "applied_magnitude_luma",
    "dark_damping_weight_luma",
]


def resolve_path(value, root, base_dir=None):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    if base_dir:
        candidate = os.path.abspath(os.path.join(base_dir, text))
        if os.path.exists(candidate):
            return candidate
    return os.path.abspath(os.path.join(root, text))


def file_reference(path, root, label, existing=None, require=True, hash_file=False):
    resolved = resolve_path(path, root)
    if not resolved or not os.path.isfile(resolved):
        if require:
            return {
                "label": label,
                "status": "missing",
                "repo_path": path,
            }
        return None
    entry = {
        "label": label,
        "status": "ready",
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "size": os.path.getsize(resolved),
    }
    if isinstance(existing, dict):
        if existing.get("sha256"):
            entry["sha256"] = existing.get("sha256")
        if existing.get("dimensions"):
            entry["dimensions"] = existing.get("dimensions")
    if hash_file and "sha256" not in entry:
        entry["sha256"] = sha256_file(resolved)
    dims = image_dimensions(resolved)
    if dims and "dimensions" not in entry:
        entry["dimensions"] = dims
    return entry


def source_json(path, label, root):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "subschema": payload.get("subschema"),
        "version": payload.get("version"),
        "status": payload.get("status"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, payload


def resolve_sequence_asset(frame, key, sequence_dir, root):
    return resolve_path(frame.get(key), root, base_dir=sequence_dir)


def inspect_scene_frame(frame, sequence_dir, root, missing):
    refs = {}
    for role in ("camera", "particles", "phase_cells"):
        resolved = resolve_sequence_asset(frame, role, sequence_dir, root)
        ref = file_reference(resolved, root, role, require=True)
        if ref.get("status") != "ready":
            missing.append({"frame": frame.get("frame"), "role": role, "path": frame.get(role)})
        refs[role] = ref

    water_mesh = frame.get("water_mesh")
    if water_mesh:
        resolved = resolve_sequence_asset(frame, "water_mesh", sequence_dir, root)
        ref = file_reference(resolved, root, "water_mesh", require=True)
        if ref.get("status") != "ready":
            missing.append({"frame": frame.get("frame"), "role": "water_mesh", "path": water_mesh})
        refs["water_mesh"] = ref

    camera_payload = {}
    if refs["camera"].get("status") == "ready":
        camera_payload = read_json(refs["camera"]["path"])

    water = camera_payload.get("water_volume") or {}
    cinematic = camera_payload.get("cinematic_metadata") or {}
    secondary = camera_payload.get("secondary_channels") or {}
    return {
        "frame": frame.get("frame"),
        "step": frame.get("step"),
        "time": frame.get("time"),
        "source_cache": frame.get("source_cache"),
        "assets": refs,
        "counts": {
            "particle_count": frame.get("particle_count", camera_payload.get("particle_count", 0)),
            "phase_cell_count": frame.get("phase_cell_count", camera_payload.get("phase_cell_count", 0)),
            "secondary_particle_count": water.get("secondary_particle_count", secondary.get("total_count", 0)),
            "secondary_spray_count": secondary.get("spray_count", cinematic.get("secondary_spray_count", 0)),
            "secondary_foam_count": secondary.get("foam_count", cinematic.get("secondary_foam_count", 0)),
            "secondary_bubble_count": secondary.get("bubble_count", cinematic.get("secondary_bubble_count", 0)),
            "water_mesh_vertex_count": frame.get("water_mesh_vertex_count", 0),
            "water_mesh_face_count": frame.get("water_mesh_face_count", 0),
        },
        "cinematic": {
            "water_bounds_valid": cinematic.get("water_bounds_valid"),
            "secondary_bounds_valid": cinematic.get("secondary_bounds_valid"),
            "water_bounds_min": cinematic.get("water_bounds_min"),
            "water_bounds_max": cinematic.get("water_bounds_max"),
            "secondary_bounds_min": cinematic.get("secondary_bounds_min"),
            "secondary_bounds_max": cinematic.get("secondary_bounds_max"),
            "world_units": cinematic.get("world_units"),
        },
    }


def texture_entry(frame, name, root, missing, output_frame):
    source = ((frame.get("textures") or {}).get(name) or {})
    path = source.get("path") or source.get("repo_path")
    ref = file_reference(path, root, name, existing=source, require=True)
    if ref.get("status") != "ready":
        missing.append({"frame": output_frame, "role": name, "path": path})
    return ref


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def nearest_index(index, src_count, dst_count):
    if src_count <= 1 or dst_count <= 1:
        return 0
    return int(round(index * float(src_count - 1) / float(dst_count - 1)))


def copy_gallery_asset(src, assets_dir, name, label, root):
    resolved = require_file(src, label)
    os.makedirs(assets_dir, exist_ok=True)
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(resolved) != os.path.abspath(dest):
        shutil.copy2(resolved, dest)
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def summary_stats(values):
    nums = [float(v) for v in values if isinstance(v, (int, float))]
    if not nums:
        return {"min": 0, "max": 0, "mean": 0.0}
    return {
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / float(len(nums)),
    }


def build_frames(scene_frames, texture_frames, consumer_frames, root, missing):
    consumer_by_output = output_frame_map(consumer_frames)
    frames = []
    used_scene_indices = set()
    for index, texture_frame in enumerate(texture_frames):
        scene_index = nearest_index(index, len(scene_frames), len(texture_frames))
        used_scene_indices.add(scene_index)
        scene = scene_frames[scene_index]
        output = texture_frame.get("output_frame", texture_frame.get("frame", index))
        textures = {
            name: texture_entry(texture_frame, name, root, missing, output)
            for name in REQUIRED_TEXTURES
        }
        consumer = consumer_by_output.get(output)
        composite = None
        strip = None
        if consumer:
            composite = file_reference(consumer.get("composite_repo_path") or consumer.get("composite_path"),
                                       root,
                                       "consumer_composite",
                                       require=True)
            strip = file_reference(consumer.get("strip_repo_path"), root, "consumer_strip", require=False)
            if composite.get("status") != "ready":
                missing.append({"frame": output, "role": "consumer_composite", "path": consumer.get("composite_repo_path")})
        else:
            missing.append({"frame": output, "role": "consumer_frame", "path": None})
        frames.append({
            "frame": index,
            "output_frame": output,
            "scene_frame_index": scene_index,
            "scene_frame": scene.get("frame"),
            "scene_time": scene.get("time"),
            "scene": scene,
            "textures": textures,
            "consumer": {
                "composite": composite,
                "strip": strip,
                "expected": (consumer or {}).get("expected", {}),
                "response": (consumer or {}).get("response", {}),
            },
        })
    return frames, used_scene_indices


def html_page(summary):
    checks = summary.get("checks") or {}
    gallery = summary.get("gallery") or {}
    assets = gallery.get("assets") or []
    hero = next((item for item in assets if item["label"] == "Texture Consumer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Mapped Frame Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Scene frames", checks.get("scene_frames")),
            ("Visual frames", checks.get("visual_frames")),
            ("Unique scene frames", checks.get("unique_scene_frames")),
            ("Missing", checks.get("missing_references")),
            ("Scene/visual", checks.get("mapping_mode")),
            ("Texture bytes", format_bytes(checks.get("texture_bytes", 0))),
            ("Max visual diff", checks.get("max_visual_expected_abs_diff")),
        )
    )
    hero_html = f'<section class="hero"><img src="{hero["href"]}" alt="texture consumer gif"></section>' if hero else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1500px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 16px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; overflow-x: auto; margin: 0 0 12px; }}
    img {{ display: block; max-width: none; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Renderer handoff manifest that maps scene cache assets to the current low-frequency visual texture contract without copying the heavy caches.</p>
  <section class="tiles">{tiles}</section>
  {hero_html}
  <section>{figures}</section>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Scene frames: `{checks.get('scene_frames')}`",
        f"- Visual frames: `{checks.get('visual_frames')}`",
        f"- Handoff frames: `{checks.get('handoff_frames')}`",
        f"- Unique scene frames mapped: `{checks.get('unique_scene_frames')}`",
        f"- Mapping mode: `{checks.get('mapping_mode')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Camera assets: `{checks.get('camera_assets')}`",
        f"- Particle assets: `{checks.get('particle_assets')}`",
        f"- Phase-cell assets: `{checks.get('phase_cell_assets')}`",
        f"- Water meshes: `{checks.get('water_mesh_assets')}`",
        f"- Texture bytes: `{format_bytes(checks.get('texture_bytes', 0))}`",
        f"- Max texture reconstruction diff: `{checks.get('max_texture_reconstruction_abs_diff')}`",
        f"- Max visual expected diff: `{checks.get('max_visual_expected_abs_diff')}`",
        "",
        "## Scene Statistics",
        "",
        f"- Particle count: `{checks.get('particle_count')}`",
        f"- Phase-cell count: `{checks.get('phase_cell_count')}`",
        f"- Secondary count: `{checks.get('secondary_particle_count')}`",
        "",
        "## Frame Samples",
        "",
        "| Visual | Scene | Time | Particles | Phase Cells | Secondary | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        scene = frame.get("scene") or {}
        counts = scene.get("counts") or {}
        strip = (((frame.get("consumer") or {}).get("strip") or {}).get("repo_path") or "")
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('scene_frame')} | {frame.get('scene_time')} | "
            f"{counts.get('particle_count')} | {counts.get('phase_cell_count')} | "
            f"{counts.get('secondary_particle_count')} | `{strip}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    sequence_source, sequence = source_json(args.scene_sequence, "converted scene sequence", root)
    if sequence.get("converter") != "lsfs_render_cache_converter":
        raise SystemExit(f"{args.scene_sequence}: expected lsfs_render_cache_converter sequence")
    texture_source, texture_package = source_json(args.texture_package_summary, "low-frequency texture package", root)
    if texture_package.get("schema") != "lsfs_mitsuba_low_frequency_parity_texture_package":
        raise SystemExit(f"{args.texture_package_summary}: expected lsfs_mitsuba_low_frequency_parity_texture_package schema")
    consumer_source, consumer = source_json(args.texture_consumer_summary, "low-frequency texture consumer", root)
    if consumer.get("subschema") != "lsfs_mitsuba_low_frequency_parity_texture_consumer":
        raise SystemExit(f"{args.texture_consumer_summary}: expected low-frequency texture consumer subschema")

    sequence_dir = os.path.dirname(os.path.abspath(args.scene_sequence))
    missing = []
    scene_frames = [
        inspect_scene_frame(frame, sequence_dir, root, missing)
        for frame in (sequence.get("frames") or [])
    ]
    texture_frames = texture_package.get("frames") or []
    consumer_frames = consumer.get("frames") or []
    frames, used_scene_indices = build_frames(scene_frames, texture_frames, consumer_frames, root, missing)

    scene_counts = [frame.get("counts") or {} for frame in scene_frames]
    texture_checks = texture_package.get("checks") or {}
    consumer_checks = consumer.get("checks") or {}
    checks = {
        "scene_frames": len(scene_frames),
        "visual_frames": len(texture_frames),
        "consumer_frames": len(consumer_frames),
        "handoff_frames": len(frames),
        "unique_scene_frames": len(used_scene_indices),
        "frame_count_mismatch": len(scene_frames) != len(texture_frames),
        "mapping_mode": "one_to_one" if len(scene_frames) == len(texture_frames) else "nearest_normalized_scene_frame",
        "missing_references": len(missing),
        "camera_assets": sum(1 for frame in scene_frames if ((frame.get("assets") or {}).get("camera") or {}).get("status") == "ready"),
        "particle_assets": sum(1 for frame in scene_frames if ((frame.get("assets") or {}).get("particles") or {}).get("status") == "ready"),
        "phase_cell_assets": sum(1 for frame in scene_frames if ((frame.get("assets") or {}).get("phase_cells") or {}).get("status") == "ready"),
        "water_mesh_assets": sum(1 for frame in scene_frames if ((frame.get("assets") or {}).get("water_mesh") or {}).get("status") == "ready"),
        "texture_bytes": texture_checks.get("texture_bytes", 0),
        "max_texture_reconstruction_abs_diff": texture_checks.get("max_reconstruction_abs_diff"),
        "max_visual_expected_abs_diff": consumer_checks.get("max_expected_abs_diff"),
        "particle_count": summary_stats(counts.get("particle_count") for counts in scene_counts),
        "phase_cell_count": summary_stats(counts.get("phase_cell_count") for counts in scene_counts),
        "secondary_particle_count": summary_stats(counts.get("secondary_particle_count") for counts in scene_counts),
    }
    status = "ready"
    if not scene_frames or not texture_frames or not consumer_frames:
        status = "failed"
    if texture_package.get("status") != "ready" or consumer.get("status") != "ready":
        status = "failed"
    if missing:
        status = "failed"

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_cache_handoff",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "bundle_root": {
            "path": out_dir,
            "repo_path": posix_rel(out_dir, root),
        },
        "sources": {
            "scene_sequence": sequence_source,
            "texture_package": texture_source,
            "texture_consumer": consumer_source,
        },
        "scene_sequence": {
            "sim_kind": sequence.get("sim_kind"),
            "dims": sequence.get("dims"),
            "dx": sequence.get("dx"),
            "renderer_assets": sequence.get("renderer_assets"),
            "water_reconstruction": sequence.get("water_reconstruction"),
        },
        "visual_contract": {
            "texture_names": texture_package.get("textures"),
            "required_textures": REQUIRED_TEXTURES,
            "texture_package_checks": texture_checks,
            "texture_consumer_checks": consumer_checks,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": [],
            "metadata_files": [],
        },
        "next": args.next,
    }
    write_json(summary_path, summary)

    assets = []
    consumer_gallery_assets = ((consumer.get("gallery") or {}).get("assets") or [])
    gif_source = next((item.get("asset") or item.get("repo_path") for item in consumer_gallery_assets if item.get("label") == "Texture Consumer GIF"), None)
    if gif_source:
        assets.append(copy_gallery_asset(gif_source, assets_dir, "texture_consumer.gif", "Texture Consumer GIF", root))
    key_indices = sorted(set(round(i * (len(frames) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if frames else []
    for out_index, frame_index in enumerate(key_indices):
        strip_ref = (((frames[frame_index].get("consumer") or {}).get("strip") or {}).get("path") or
                     ((frames[frame_index].get("consumer") or {}).get("strip") or {}).get("repo_path"))
        if strip_ref:
            assets.append(copy_gallery_asset(strip_ref, assets_dir, f"mapped_frame_strip_{out_index:02d}.png", f"Mapped Frame Strip {out_index + 1}", root))
    metadata_files = [
        copy_gallery_asset(args.scene_sequence, assets_dir, "scene_sequence.json", "Scene sequence", root),
        copy_gallery_asset(args.texture_package_summary, assets_dir, "texture_package_summary.json", "Texture package summary", root),
        copy_gallery_asset(args.texture_consumer_summary, assets_dir, "texture_consumer_summary.json", "Texture consumer summary", root),
        copy_gallery_asset(summary_path, assets_dir, "renderer_scene_cache_handoff_summary.json", "Scene-cache handoff summary", root),
    ]
    summary["gallery"]["assets"] = assets
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_cache_handoff_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))

    print(
        f"status={status} scene_frames={checks['scene_frames']} visual_frames={checks['visual_frames']} "
        f"handoff_frames={checks['handoff_frames']} missing={checks['missing_references']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a renderer scene-cache handoff manifest")
    parser.add_argument("scene_sequence")
    parser.add_argument("texture_package_summary")
    parser.add_argument("texture_consumer_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S578 Renderer Scene Cache Handoff")
    parser.add_argument(
        "--next",
        default="Validate this handoff, then consume scene depth and water metadata in a bounded renderer-side depth/material pass.",
    )
    args = parser.parse_args(argv)
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    build(args)


if __name__ == "__main__":
    main()
