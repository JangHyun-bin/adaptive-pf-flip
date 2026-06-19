#!/usr/bin/env python
"""Build renderer-neutral scene descriptors from an LSFS external renderer job."""

import argparse
import os
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


REQUIRED_ASSETS = ("camera", "water_mesh", "phase_cells", "particles")


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def asset_path(asset):
    path = (asset or {}).get("path") or (asset or {}).get("repo_path")
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def artifact_json(path, label, root):
    if not path:
        return None
    resolved = require_file(path, label)
    payload = read_json(resolved)
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "sha256": sha256_file(resolved),
    }


def select_indices(count, requested):
    requested = max(1, min(as_int(requested, count), count))
    if requested == count:
        return list(range(count))
    if requested == 1:
        return [0]
    return sorted(set(round(i * (count - 1) / float(requested - 1)) for i in range(requested)))


def selected_frames(frames, requested=None, start_index=None, end_index=None):
    if not frames:
        return []
    start = 0 if start_index is None else max(0, min(len(frames) - 1, start_index))
    end = len(frames) - 1 if end_index is None else max(0, min(len(frames) - 1, end_index))
    if end < start:
        raise SystemExit(f"invalid frame window: start_index={start} end_index={end}")
    window = frames[start:end + 1]
    if requested is None or requested <= 0 or requested >= len(window):
        return window
    return [window[index] for index in select_indices(len(window), requested)]


def read_job(path):
    resolved = require_file(path, "external renderer job")
    job = read_json(resolved)
    if job.get("schema") != "lsfs_external_renderer_job":
        raise SystemExit(f"{path}: expected lsfs_external_renderer_job schema")
    if job.get("status") != "ready":
        raise SystemExit(f"{path}: job status is {job.get('status')!r}")
    if not job.get("frames"):
        raise SystemExit(f"{path}: job has no frames")
    return resolved, job


def asset_descriptor(asset, root, role, required=False, hash_assets=False):
    path = asset_path(asset)
    present = bool(path and os.path.isfile(path))
    desc = {
        "role": role,
        "required": bool(required),
        "encoding": (asset or {}).get("encoding"),
        "fields": (asset or {}).get("fields", []),
        "status": "present" if present else "missing",
        "path": path,
        "repo_path": posix_rel(path, root) if path else None,
        "size": os.path.getsize(path) if present else 0,
    }
    if present and hash_assets:
        desc["sha256"] = sha256_file(path)
    return desc


def compact_look_reference(look):
    if not look:
        return {}
    keys = (
        "render_preset_name",
        "water_material",
        "water_surface_detail",
        "water_surface_glint_pass",
        "water_reflection_pass",
        "water_volume_scattering_pass",
        "water_volume_occlusion_pass",
        "secondary_direct_pass",
        "secondary_soft_pass",
        "secondary_streak_pass",
        "secondary_channel_radius_scales",
        "surface_contact_foam_counts",
        "water_impact_ripple_counts",
        "visual_qa",
    )
    return {key: look[key] for key in keys if key in look}


def material_contract(look):
    water_material = (look or {}).get("water_material") or {}
    radius_scales = (look or {}).get("secondary_channel_radius_scales") or {}
    return {
        "water_surface": {
            "source_asset": "water_mesh",
            "material": "lsfs_water_surface",
            "model": "dielectric_surface",
            "ior": water_material.get("ior", 1.333),
            "roughness": water_material.get("roughness", 0.035),
            "transmission": water_material.get("transmission", 1.0),
            "notes": "Use the OBJ mesh as the primary liquid surface.",
        },
        "phase_volume": {
            "source_asset": "phase_cells",
            "material": "lsfs_phase_volume",
            "model": "sparse_volume_or_mask",
            "density_field": "liquid_volume",
            "notes": "CSV cells can drive volumetric fill, masks, or holdout diagnostics.",
        },
        "secondary_particles": {
            "source_asset": "particles",
            "model": "csv_particle_channels",
            "channels": {
                "spray": {
                    "material": "lsfs_spray_mist",
                    "radius_scale": radius_scales.get("spray", 1.0),
                    "filter": "render_channel == spray",
                },
                "foam": {
                    "material": "lsfs_surface_foam",
                    "radius_scale": radius_scales.get("foam", 1.0),
                    "filter": "render_channel == foam",
                },
                "bubble": {
                    "material": "lsfs_subsurface_bubble",
                    "radius_scale": radius_scales.get("bubble", 1.0),
                    "filter": "render_channel == bubble",
                },
                "droplet": {
                    "material": "lsfs_free_droplet",
                    "radius_scale": radius_scales.get("droplet", 1.0),
                    "filter": "render_channel == droplet",
                },
            },
        },
    }


def scene_descriptor(args, root, out_dir, frame, index, render_settings, materials):
    frame_name = f"frame_{index:04d}"
    scene_path = os.path.abspath(os.path.join(out_dir, "scenes", f"{frame_name}_scene.json"))
    output_image = os.path.abspath(os.path.join(out_dir, "renders", f"{frame_name}.{args.output_format}"))
    output_metadata = os.path.abspath(os.path.join(out_dir, "render_metadata", f"{frame_name}.json"))
    assets = frame.get("assets") or {}
    scene_assets = {
        "camera": asset_descriptor(assets.get("camera"), root, "camera", True, args.hash_assets),
        "water_surface": asset_descriptor(assets.get("water_mesh"), root, "water_surface", True, args.hash_assets),
        "phase_volume": asset_descriptor(assets.get("phase_cells"), root, "phase_volume", True, args.hash_assets),
        "particle_stream": asset_descriptor(assets.get("particles"), root, "particle_stream", True, args.hash_assets),
    }
    descriptor = {
        "schema": "lsfs_external_renderer_scene_descriptor",
        "version": 1,
        "target_renderer": args.target_renderer,
        "adapter_kind": "renderer_neutral_scene_json",
        "output_frame": index,
        "source_output_frame": frame.get("output_frame"),
        "sequence_frame": frame.get("sequence_frame"),
        "time": frame.get("time"),
        "render_settings": render_settings,
        "camera": frame.get("camera", {}),
        "assets": scene_assets,
        "materials": materials,
        "diagnostics": {
            "particle_count": frame.get("particle_count"),
            "phase_cell_count": frame.get("phase_cell_count"),
            "water_mesh_face_count": frame.get("water_mesh_face_count"),
            "water_mesh_vertex_count": frame.get("water_mesh_vertex_count"),
            "water_mesh_surface_quality": frame.get("water_mesh_surface_quality", {}),
            "secondary_counts": frame.get("secondary_counts")
            or (frame.get("render_data") or {}).get("secondary_counts", {}),
            "render_data": frame.get("render_data", {}),
        },
        "expected_outputs": {
            "image": {
                "path": output_image,
                "repo_path": posix_rel(output_image, root),
                "format": args.output_format,
            },
            "metadata": {
                "path": output_metadata,
                "repo_path": posix_rel(output_metadata, root),
                "format": "json",
            },
        },
    }
    return scene_path, descriptor


def command_line(renderer_command, scene_path, output_image, samples):
    return (
        f'{renderer_command} --scene "{scene_path}" '
        f'--output "{output_image}" --samples {samples}'
    )


def build_manifest(args):
    root = os.getcwd()
    job_path, job = read_job(args.job)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(os.path.join(out_dir, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "renders"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "render_metadata"), exist_ok=True)

    frames = selected_frames(
        job.get("frames", []),
        requested=args.frames,
        start_index=args.source_start_index,
        end_index=args.source_end_index,
    )
    look = read_json(require_file(args.look_reference, "look reference")) if args.look_reference else {}
    materials = material_contract(compact_look_reference(look))
    source_settings = job.get("render_settings", {})
    render_settings = {
        "width": args.width or source_settings.get("width") or 1920,
        "height": args.height or source_settings.get("height") or 1080,
        "fps": args.fps or source_settings.get("fps") or 8.0,
        "samples": args.samples or source_settings.get("samples") or 64,
        "output_format": args.output_format,
        "world_units": source_settings.get("world_units", "cell"),
        "coordinate_note": source_settings.get(
            "coordinate_note",
            "Input assets use LSFS cell-space coordinates; renderer adapters may convert axes.",
        ),
    }

    manifest_frames = []
    commands = []
    missing_assets = []
    min_water_mesh_faces = None
    sequence_frames = []
    total_bytes = 0
    for index, frame in enumerate(frames):
        scene_path, descriptor = scene_descriptor(args, root, out_dir, frame, index, render_settings, materials)
        write_json(scene_path, descriptor)
        scene_assets = descriptor["assets"]
        for name, asset in scene_assets.items():
            total_bytes += asset.get("size", 0)
            if asset.get("required") and asset.get("status") != "present":
                missing_assets.append({
                    "output_frame": index,
                    "asset": name,
                    "path": asset.get("path"),
                })
        faces = frame.get("water_mesh_face_count")
        if isinstance(faces, int):
            min_water_mesh_faces = faces if min_water_mesh_faces is None else min(min_water_mesh_faces, faces)
        sequence_frames.append(frame.get("sequence_frame"))
        output_image = descriptor["expected_outputs"]["image"]["path"]
        commands.append(command_line(args.renderer_command, scene_path, output_image, render_settings["samples"]))
        manifest_frames.append({
            "output_frame": index,
            "source_output_frame": frame.get("output_frame"),
            "sequence_frame": frame.get("sequence_frame"),
            "time": frame.get("time"),
            "scene_descriptor": {
                "path": scene_path,
                "repo_path": posix_rel(scene_path, root),
                "sha256": sha256_file(scene_path),
            },
            "expected_outputs": descriptor["expected_outputs"],
            "asset_status": {name: asset.get("status") for name, asset in scene_assets.items()},
            "particle_count": frame.get("particle_count"),
            "phase_cell_count": frame.get("phase_cell_count"),
            "water_mesh_face_count": frame.get("water_mesh_face_count"),
            "secondary_counts": descriptor["diagnostics"]["secondary_counts"],
            "render_command": commands[-1],
        })

    sequence_monotonic = all(
        sequence_frames[i] is None
        or sequence_frames[i + 1] is None
        or sequence_frames[i] <= sequence_frames[i + 1]
        for i in range(max(0, len(sequence_frames) - 1))
    )
    gates = {
        "frame_count": len(frames),
        "missing_assets": len(missing_assets),
        "sequence_monotonic": sequence_monotonic,
        "min_water_mesh_faces": min_water_mesh_faces,
        "min_water_mesh_faces_required": args.min_water_mesh_faces,
        "scene_descriptors": len(manifest_frames),
    }
    failed = (
        not manifest_frames
        or gates["missing_assets"] > 0
        or not sequence_monotonic
        or (min_water_mesh_faces or 0) < args.min_water_mesh_faces
    )
    command_list_path = os.path.abspath(os.path.join(out_dir, "render_commands.txt"))
    write_text(command_list_path, "\n".join(commands) + ("\n" if commands else ""))

    related = []
    for path, label in (
        (args.look_reference, "look_reference"),
        (args.proof_package, "proof_package"),
        (args.public_manifest, "public_manifest"),
    ):
        item = artifact_json(path, label, root)
        if item:
            related.append(item)

    return {
        "schema": "lsfs_external_renderer_adapter_manifest",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed" if failed else "ready",
        "title": args.title,
        "target_renderer": args.target_renderer,
        "adapter_kind": "renderer_neutral_scene_json",
        "execution_mode": "manifest_only",
        "source_job": {
            "path": job_path,
            "repo_path": posix_rel(job_path, root),
            "schema": job.get("schema"),
            "version": job.get("version"),
            "sha256": sha256_file(job_path),
            "target_renderer": job.get("target_renderer"),
        },
        "render_settings": render_settings,
        "renderer_command_template": (
            f'{args.renderer_command} --scene "{{scene_descriptor}}" '
            f'--output "{{output_image}}" --samples {render_settings["samples"]}'
        ),
        "command_list": {
            "path": command_list_path,
            "repo_path": posix_rel(command_list_path, root),
            "sha256": sha256_file(command_list_path),
        },
        "material_contract": materials,
        "related_artifacts": related,
        "input_footprint": {
            "referenced_asset_bytes": total_bytes,
            "scene_descriptor_bytes": sum(
                os.path.getsize(frame["scene_descriptor"]["path"]) for frame in manifest_frames
            ),
        },
        "quality_gates": gates,
        "missing_assets": missing_assets,
        "frames": manifest_frames,
        "next": args.next,
    }


def markdown_report(manifest, out_path, root):
    settings = manifest.get("render_settings", {})
    gates = manifest.get("quality_gates", {})
    footprint = manifest.get("input_footprint", {})
    lines = [
        f"# {manifest['title']}",
        "",
        f"Generated UTC: `{manifest['generated_utc']}`",
        f"Adapter manifest: `{posix_rel(out_path, root)}`",
        f"Status: `{manifest['status']}`",
        f"Target renderer: `{manifest['target_renderer']}`",
        f"Adapter kind: `{manifest['adapter_kind']}`",
        f"Execution mode: `{manifest['execution_mode']}`",
        "",
        "## Source",
        "",
        f"- Source job: `{manifest.get('source_job', {}).get('repo_path')}`",
        f"- Source job target: `{manifest.get('source_job', {}).get('target_renderer')}`",
        f"- Command list: `{manifest.get('command_list', {}).get('repo_path')}`",
        "",
        "## Render Settings",
        "",
        f"- Resolution: `{settings.get('width')} x {settings.get('height')}`",
        f"- FPS: `{settings.get('fps')}`",
        f"- Samples: `{settings.get('samples')}`",
        f"- Output format: `{settings.get('output_format')}`",
        "",
        "## Gates",
        "",
        f"- Frames: `{gates.get('frame_count')}`",
        f"- Scene descriptors: `{gates.get('scene_descriptors')}`",
        f"- Missing assets: `{gates.get('missing_assets')}`",
        f"- Sequence monotonic: `{gates.get('sequence_monotonic')}`",
        f"- Minimum water mesh faces: `{gates.get('min_water_mesh_faces')}`",
        f"- Required minimum water mesh faces: `{gates.get('min_water_mesh_faces_required')}`",
        "",
        "## Footprint",
        "",
        f"- Referenced asset bytes: `{format_bytes(footprint.get('referenced_asset_bytes', 0))}`",
        f"- Scene descriptor bytes: `{format_bytes(footprint.get('scene_descriptor_bytes', 0))}`",
        "",
        "## Material Contract",
        "",
    ]
    for name, material in manifest.get("material_contract", {}).items():
        lines.append(f"- `{name}`: `{material.get('model')}` from `{material.get('source_asset')}`")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Source Output | Sequence | Time | Particles | Phase Cells | Water Faces | Secondary Total |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    frames = manifest.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        secondary = frame.get("secondary_counts", {}) or {}
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('source_output_frame')} | "
            f"{frame.get('sequence_frame')} | {frame.get('time')} | "
            f"{frame.get('particle_count')} | {frame.get('phase_cell_count')} | "
            f"{frame.get('water_mesh_face_count')} | {secondary.get('total')} |"
        )
    lines.extend([
        "",
        "## Related Artifacts",
        "",
    ])
    for item in manifest.get("related_artifacts", []):
        lines.append(f"- `{item['label']}`: `{item['repo_path']}`")
    lines.extend([
        "",
        "## Next",
        "",
        manifest.get("next", "Use this manifest to implement a renderer-specific adapter."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a renderer-neutral adapter manifest")
    parser.add_argument("job", help="lsfs_external_renderer_job JSON")
    parser.add_argument("out_dir")
    parser.add_argument("--target-renderer", default="generic_path_tracer")
    parser.add_argument("--renderer-command", default="generic_path_tracer")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--source-start-index", type=int)
    parser.add_argument("--source-end-index", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=float)
    parser.add_argument("--samples", type=int)
    parser.add_argument("--output-format", default="png")
    parser.add_argument("--look-reference")
    parser.add_argument("--proof-package")
    parser.add_argument("--public-manifest")
    parser.add_argument("--hash-assets", action="store_true")
    parser.add_argument("--min-water-mesh-faces", type=int, default=1000)
    parser.add_argument("--manifest-name", default="adapter_manifest.json")
    parser.add_argument("--report")
    parser.add_argument("--title", default="External Renderer Adapter Manifest")
    parser.add_argument(
        "--next",
        default="Use this adapter manifest as the scene-descriptor contract for a renderer-specific implementation.",
    )
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames <= 0:
        parser.error("frames must be positive")
    if args.width is not None and args.width <= 0:
        parser.error("width must be positive")
    if args.height is not None and args.height <= 0:
        parser.error("height must be positive")
    if args.fps is not None and args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.samples is not None and args.samples <= 0:
        parser.error("samples must be positive")
    if args.min_water_mesh_faces <= 0:
        parser.error("min-water-mesh-faces must be positive")

    manifest = build_manifest(args)
    out_path = os.path.abspath(os.path.join(args.out_dir, args.manifest_name))
    write_json(out_path, manifest)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(manifest, out_path, os.getcwd()))
    print(
        f"status={manifest['status']} renderer={manifest['target_renderer']} "
        f"frames={manifest['quality_gates']['frame_count']} "
        f"missing_assets={manifest['quality_gates']['missing_assets']} manifest={out_path}"
    )
    print(f"report={report_path}")
    if manifest["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
