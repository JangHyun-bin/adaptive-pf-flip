#!/usr/bin/env python
"""Replace water mesh assets in an LSFS external renderer job."""

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


WATER_MESH_RE = re.compile(r"frame_(\d+)_water\.obj$", re.IGNORECASE)


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def frame_mesh_index(frame):
    water_mesh = ((frame.get("assets") or {}).get("water_mesh") or {})
    path = water_mesh.get("repo_path") or water_mesh.get("path") or ""
    match = WATER_MESH_RE.search(path.replace("\\", "/"))
    if match:
        return int(match.group(1))
    return frame.get("output_frame")


def reconstruction_mesh_path(reconstruction_path, frame):
    mesh = frame.get("mesh")
    if not mesh:
        return None
    if os.path.isabs(mesh):
        return os.path.abspath(mesh)
    return os.path.abspath(os.path.join(os.path.dirname(reconstruction_path), mesh.replace("/", os.sep)))


def mesh_quality(reconstruction, frame):
    return {
        "label": f"{reconstruction.get('surface_mode', frame.get('surface_mode', 'unknown'))}_reconstruction",
        "source": "replace_external_job_water_mesh",
        "surface_mode": frame.get("surface_mode"),
        "threshold": reconstruction.get("threshold"),
        "implicit_iso": reconstruction.get("implicit_iso"),
        "implicit_blur_iterations": reconstruction.get("implicit_blur_iterations"),
        "smooth_iterations": reconstruction.get("smooth_iterations"),
        "smooth_alpha": reconstruction.get("smooth_alpha"),
        "occupied_cell_count": frame.get("occupied_cell_count"),
        "component_count": frame.get("component_count"),
        "largest_component_face_ratio": frame.get("largest_component_face_ratio"),
        "largest_component_vertex_ratio": frame.get("largest_component_vertex_ratio"),
        "pre_filter_component_count": frame.get("pre_filter_component_count"),
        "pre_filter_largest_component_face_ratio": frame.get("pre_filter_largest_component_face_ratio"),
        "component_filter": frame.get("component_filter"),
    }


def replacement_asset(mesh_path, root):
    present = bool(mesh_path and os.path.isfile(mesh_path))
    return {
        "role": "water_surface_mesh",
        "encoding": "obj",
        "status": "present" if present else "missing",
        "path": mesh_path,
        "repo_path": posix_rel(mesh_path, root) if mesh_path else None,
        "size": os.path.getsize(mesh_path) if present else 0,
        "sha256": sha256_file(mesh_path) if present else None,
    }


def replace_water_mesh(args):
    root = os.getcwd()
    job_path = require_file(args.job, "external renderer job")
    reconstruction_path = require_file(args.reconstruction, "water reconstruction")
    job = read_json(job_path)
    reconstruction = read_json(reconstruction_path)
    if job.get("schema") != "lsfs_external_renderer_job":
        raise SystemExit(f"{args.job}: expected lsfs_external_renderer_job schema")
    if reconstruction.get("reconstructor") != "lsfs_water_reconstruction":
        raise SystemExit(f"{args.reconstruction}: expected lsfs_water_reconstruction reconstructor")

    reconstruction_frames = {
        int(frame.get("frame")): frame
        for frame in reconstruction.get("frames", [])
        if frame.get("frame") is not None
    }
    updated = copy.deepcopy(job)
    updated["generated_utc"] = datetime.now(timezone.utc).isoformat()
    updated["title"] = args.title
    updated["water_mesh_replacement"] = {
        "source_job": {
            "path": job_path,
            "repo_path": posix_rel(job_path, root),
            "sha256": sha256_file(job_path),
        },
        "reconstruction": {
            "path": reconstruction_path,
            "repo_path": posix_rel(reconstruction_path, root),
            "sha256": sha256_file(reconstruction_path),
            "surface_mode": reconstruction.get("surface_mode"),
            "threshold": reconstruction.get("threshold"),
            "implicit_iso": reconstruction.get("implicit_iso"),
            "implicit_blur_iterations": reconstruction.get("implicit_blur_iterations"),
            "smooth_iterations": reconstruction.get("smooth_iterations"),
            "smooth_alpha": reconstruction.get("smooth_alpha"),
            "frame_count": reconstruction.get("frame_count"),
        },
    }
    updated["next"] = args.next

    failures = []
    water_mesh_bytes = 0
    min_faces = None
    quality_labels = {}
    replaced = 0
    for frame in updated.get("frames", []):
        mesh_index = frame_mesh_index(frame)
        replacement = reconstruction_frames.get(mesh_index)
        if not replacement:
            failures.append({
                "output_frame": frame.get("output_frame"),
                "mesh_index": mesh_index,
                "reason": "missing_reconstruction_frame",
            })
            continue
        mesh_path = reconstruction_mesh_path(reconstruction_path, replacement)
        asset = replacement_asset(mesh_path, root)
        if asset["status"] != "present":
            failures.append({
                "output_frame": frame.get("output_frame"),
                "mesh_index": mesh_index,
                "path": mesh_path,
                "reason": "missing_mesh_asset",
            })
            continue
        frame.setdefault("assets", {})["water_mesh"] = asset
        frame["water_mesh_face_count"] = replacement.get("face_count")
        frame["water_mesh_vertex_count"] = replacement.get("vertex_count")
        frame["water_mesh_surface_quality"] = mesh_quality(reconstruction, replacement)
        frame["water_mesh_replacement"] = {
            "source_mesh_index": mesh_index,
            "reconstruction_frame": replacement.get("frame"),
            "source_frame": replacement.get("source_frame"),
            "source_time": replacement.get("source_time"),
        }
        water_mesh_bytes += asset["size"]
        faces = replacement.get("face_count")
        if isinstance(faces, int):
            min_faces = faces if min_faces is None else min(min_faces, faces)
        label = frame["water_mesh_surface_quality"]["label"]
        quality_labels[label] = quality_labels.get(label, 0) + 1
        replaced += 1

    totals = updated.setdefault("input_footprint", {})
    previous_water_mesh_bytes = totals.get("water_mesh_bytes", 0)
    totals["water_mesh_bytes"] = water_mesh_bytes
    totals["total_bytes"] = totals.get("total_bytes", 0) - previous_water_mesh_bytes + water_mesh_bytes

    gates = updated.setdefault("quality_gates", {})
    gates["water_mesh_replacement_failures"] = len(failures)
    gates["water_mesh_replaced_frames"] = replaced
    gates["min_water_mesh_faces"] = min_faces
    gates["quality_labels"] = quality_labels
    gates["min_water_mesh_faces_required"] = args.min_water_mesh_faces
    if (min_faces or 0) < args.min_water_mesh_faces:
        failures.append({
            "reason": "min_water_mesh_faces",
            "required": args.min_water_mesh_faces,
            "actual": min_faces,
        })
    updated["water_mesh_replacement_failures"] = failures
    updated["status"] = "ready" if replaced == len(updated.get("frames", [])) and not failures else "failed"

    related = updated.setdefault("related_artifacts", [])
    related.append({
        "label": "water_mesh_replacement_reconstruction",
        "path": reconstruction_path,
        "repo_path": posix_rel(reconstruction_path, root),
        "schema": reconstruction.get("reconstructor"),
        "version": reconstruction.get("version"),
        "sha256": sha256_file(reconstruction_path),
    })
    return updated


def markdown_report(job, out_path, root):
    replacement = job.get("water_mesh_replacement") or {}
    reconstruction = replacement.get("reconstruction") or {}
    gates = job.get("quality_gates") or {}
    footprint = job.get("input_footprint") or {}
    lines = [
        f"# {job.get('title')}",
        "",
        f"Generated UTC: `{job.get('generated_utc')}`",
        f"Job JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{job.get('status')}`",
        "",
        "## Replacement",
        "",
        f"- Source job: `{(replacement.get('source_job') or {}).get('repo_path')}`",
        f"- Reconstruction: `{reconstruction.get('repo_path')}`",
        f"- Surface mode: `{reconstruction.get('surface_mode')}`",
        f"- Threshold: `{reconstruction.get('threshold')}`",
        f"- Implicit iso: `{reconstruction.get('implicit_iso')}`",
        f"- Implicit blur iterations: `{reconstruction.get('implicit_blur_iterations')}`",
        f"- Smooth iterations: `{reconstruction.get('smooth_iterations')}`",
        f"- Smooth alpha: `{reconstruction.get('smooth_alpha')}`",
        "",
        "## Gates",
        "",
        f"- Replaced frames: `{gates.get('water_mesh_replaced_frames')}`",
        f"- Replacement failures: `{gates.get('water_mesh_replacement_failures')}`",
        f"- Minimum water mesh faces: `{gates.get('min_water_mesh_faces')}`",
        f"- Minimum water mesh faces required: `{gates.get('min_water_mesh_faces_required')}`",
        f"- Quality labels: `{gates.get('quality_labels')}`",
        "",
        "## Input Footprint",
        "",
        f"- Water mesh OBJ: `{format_bytes(footprint.get('water_mesh_bytes', 0))}`",
        f"- Total: `{format_bytes(footprint.get('total_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Sequence | Mesh Index | Recon Frame | Source Frame | Water Faces | Water Vertices |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    frames = job.get("frames", [])
    indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in indices:
        frame = frames[index]
        item = frame.get("water_mesh_replacement") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('sequence_frame')} | "
            f"{item.get('source_mesh_index')} | {item.get('reconstruction_frame')} | "
            f"{item.get('source_frame')} | {frame.get('water_mesh_face_count')} | "
            f"{frame.get('water_mesh_vertex_count')} |"
        )
    failures = job.get("water_mesh_replacement_failures") or []
    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures[:12]:
            lines.append(f"- `{failure}`")
    lines.extend(["", "## Next", "", job.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Replace water mesh assets in an LSFS external renderer job")
    parser.add_argument("job")
    parser.add_argument("reconstruction")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="External Renderer Job With Replacement Water Mesh")
    parser.add_argument("--min-water-mesh-faces", type=int, default=1000)
    parser.add_argument(
        "--next",
        default="Build a renderer adapter from this job and compare the replacement water mesh against the baseline.",
    )
    args = parser.parse_args(argv)
    if args.min_water_mesh_faces <= 0:
        parser.error("min-water-mesh-faces must be positive")
    job = replace_water_mesh(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, job)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(job, out_path, os.getcwd()))
    print(
        f"status={job['status']} frames={len(job.get('frames', []))} "
        f"replaced={job.get('quality_gates', {}).get('water_mesh_replaced_frames')} "
        f"failures={job.get('quality_gates', {}).get('water_mesh_replacement_failures')} job={out_path}"
    )
    print(f"report={report_path}")
    if job["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
