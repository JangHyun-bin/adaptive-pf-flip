#!/usr/bin/env python
"""Build an external-renderer bundle manifest from a bridge handoff manifest."""

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


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def select_resampled(items, out_index, out_count, window=None):
    if not items:
        return None
    start_index = 0
    end_index = len(items) - 1
    if window:
        start_index = max(0, min(len(items) - 1, as_int(window.get("start_index"), 0)))
        end_index = max(0, min(len(items) - 1, as_int(window.get("end_index"), len(items) - 1)))
        if end_index < start_index:
            raise SystemExit(f"invalid source window: start_index={start_index} end_index={end_index}")
    if out_count <= 1 or len(items) == 1:
        return items[start_index]
    src_index = start_index + round(out_index * (end_index - start_index) / max(1, out_count - 1))
    return items[src_index]


def resolve_asset(path, base_dir):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(base_dir, path.replace("/", os.sep)))


def asset_entry(path, base_dir, root, hash_file=False):
    resolved = resolve_asset(path, base_dir)
    if not resolved:
        return {"status": "missing_path"}
    entry = {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "status": "present" if os.path.isfile(resolved) else "missing",
    }
    if os.path.isfile(resolved):
        entry["size"] = os.path.getsize(resolved)
        if hash_file:
            entry["sha256"] = sha256_file(resolved)
    return entry


def source_from_handoff(handoff, key):
    source = (handoff.get("sources") or {}).get(key) or {}
    return source.get("path") or source.get("repo_path")


def sequence_window(handoff):
    return handoff.get("review_package", {}).get("bridge_summary", {}).get("source_window") or {}


def frame_count(handoff):
    return as_int(handoff.get("review_package", {}).get("bridge_summary", {}).get("frame_count"), 0)


def build_bundle(args):
    root = os.getcwd()
    handoff_path = require_file(args.handoff_manifest, "handoff manifest")
    handoff = read_json(handoff_path)
    public_review = handoff.get("public_review", {})
    if args.public_review_manifest:
        public_review_path = require_file(args.public_review_manifest, "public review manifest")
        public_review = read_json(public_review_path)

    sequence_path = require_file(args.sequence or source_from_handoff(handoff, "sequence"), "converted sequence")
    render_data_path = args.render_data_summary or source_from_handoff(handoff, "render_data_summary")
    render_data_path = require_file(render_data_path, "render data summary") if render_data_path else None

    sequence = read_json(sequence_path)
    render_data = read_json(render_data_path) if render_data_path else {"frames": []}
    sequence_dir = os.path.dirname(sequence_path)
    out_count = args.frames or frame_count(handoff)
    if out_count <= 0:
        out_count = len(sequence.get("frames", []))
    window = {
        "start_index": args.source_start_index if args.source_start_index is not None else sequence_window(handoff).get("start_index"),
        "end_index": args.source_end_index if args.source_end_index is not None else sequence_window(handoff).get("end_index"),
    }

    frames = []
    totals = {
        "camera_bytes": 0,
        "particle_csv_bytes": 0,
        "phase_cell_csv_bytes": 0,
        "water_mesh_bytes": 0,
        "missing_assets": 0,
    }
    for out_index in range(out_count):
        seq_frame = select_resampled(sequence.get("frames", []), out_index, out_count, window)
        data_frame = select_resampled(render_data.get("frames", []), out_index, out_count)
        assets = {}
        for key, field in (
            ("camera", "camera"),
            ("particles", "particles"),
            ("phase_cells", "phase_cells"),
            ("water_mesh", "water_mesh"),
        ):
            entry = asset_entry(seq_frame.get(field) if seq_frame else None, sequence_dir, root, args.hash_frame_files)
            assets[key] = entry
            if entry.get("status") != "present":
                totals["missing_assets"] += 1
        totals["camera_bytes"] += assets["camera"].get("size", 0)
        totals["particle_csv_bytes"] += assets["particles"].get("size", 0)
        totals["phase_cell_csv_bytes"] += assets["phase_cells"].get("size", 0)
        totals["water_mesh_bytes"] += assets["water_mesh"].get("size", 0)
        frames.append({
            "output_frame": out_index,
            "sequence_frame": seq_frame.get("frame") if seq_frame else None,
            "step": seq_frame.get("step") if seq_frame else None,
            "time": seq_frame.get("time") if seq_frame else None,
            "particle_count": seq_frame.get("particle_count") if seq_frame else None,
            "phase_cell_count": seq_frame.get("phase_cell_count") if seq_frame else None,
            "water_mesh_face_count": seq_frame.get("water_mesh_face_count") if seq_frame else None,
            "water_mesh_vertex_count": seq_frame.get("water_mesh_vertex_count") if seq_frame else None,
            "water_mesh_surface_quality": seq_frame.get("water_mesh_surface_quality", {}) if seq_frame else {},
            "render_data": {
                "source_frame": data_frame.get("source_frame") if data_frame else None,
                "source_time": data_frame.get("source_time") if data_frame else None,
                "secondary_counts": data_frame.get("secondary_counts", {}) if data_frame else {},
                "water_depth_y_span": data_frame.get("water_depth_y_span") if data_frame else None,
                "water_depth_z_span": data_frame.get("water_depth_z_span") if data_frame else None,
            },
            "assets": assets,
        })

    return {
        "schema": "lsfs_bridge_external_render_bundle",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "handoff_manifest": {
            "path": handoff_path,
            "repo_path": posix_rel(handoff_path, root),
            "sha256": sha256_file(handoff_path),
        },
        "accepted_preset": handoff.get("accepted_preset"),
        "git": handoff.get("git", {}),
        "public_review": public_review,
        "source_window": window,
        "frame_count": out_count,
        "sequence": {
            "path": sequence_path,
            "repo_path": posix_rel(sequence_path, root),
            "schema": sequence.get("schema"),
            "version": sequence.get("version"),
            "source_frame_count": len(sequence.get("frames", [])),
            "sha256": sha256_file(sequence_path),
        },
        "render_data_summary": {
            "path": render_data_path,
            "repo_path": posix_rel(render_data_path, root) if render_data_path else None,
            "schema": render_data.get("schema"),
            "version": render_data.get("version"),
            "source_frame_count": len(render_data.get("frames", [])),
            "sha256": sha256_file(render_data_path) if render_data_path else None,
        },
        "asset_hash_mode": "sha256" if args.hash_frame_files else "size_only",
        "totals": totals,
        "frames": frames,
        "next": args.next,
    }


def markdown_report(bundle, out_path, root):
    totals = bundle.get("totals", {})
    lines = [
        f"# {bundle['title']}",
        "",
        f"Generated UTC: `{bundle['generated_utc']}`",
        f"Bundle JSON: `{posix_rel(out_path, root)}`",
        f"Accepted preset: `{bundle.get('accepted_preset')}`",
        f"Frame count: `{bundle.get('frame_count')}`",
        f"Source window: `{bundle.get('source_window', {}).get('start_index')}..{bundle.get('source_window', {}).get('end_index')}`",
        f"Asset hash mode: `{bundle.get('asset_hash_mode')}`",
        f"Public URL: `{bundle.get('public_review', {}).get('public_url') or 'n/a'}`",
        "",
        "## Inputs",
        "",
        f"- Handoff manifest: `{bundle.get('handoff_manifest', {}).get('repo_path')}`",
        f"- Sequence: `{bundle.get('sequence', {}).get('repo_path')}`",
        f"- Render data summary: `{bundle.get('render_data_summary', {}).get('repo_path')}`",
        "",
        "## Totals",
        "",
        f"- Camera JSON bytes: `{format_bytes(totals.get('camera_bytes', 0))}`",
        f"- Particle CSV bytes: `{format_bytes(totals.get('particle_csv_bytes', 0))}`",
        f"- Phase-cell CSV bytes: `{format_bytes(totals.get('phase_cell_csv_bytes', 0))}`",
        f"- Water mesh OBJ bytes: `{format_bytes(totals.get('water_mesh_bytes', 0))}`",
        f"- Missing assets: `{totals.get('missing_assets', 0)}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Sequence | Particles | Phase Cells | Water Faces | Quality |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = bundle.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        quality = frame.get("water_mesh_surface_quality", {}).get("label", "n/a")
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('sequence_frame')} | "
            f"{frame.get('particle_count')} | {frame.get('phase_cell_count')} | "
            f"{frame.get('water_mesh_face_count')} | `{quality}` |"
        )
    lines.extend([
        "",
        "## Next",
        "",
        bundle.get("next", "Use this bundle as the accepted external-render input list."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build an external-renderer bundle manifest")
    parser.add_argument("--handoff-manifest", required=True)
    parser.add_argument("--sequence")
    parser.add_argument("--render-data-summary")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--source-start-index", type=int)
    parser.add_argument("--source-end-index", type=int)
    parser.add_argument("--hash-frame-files", action="store_true")
    parser.add_argument("--public-review-manifest",
                        help="optional publish manifest to override the handoff public_review block")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Accepted Bridge External Render Bundle")
    parser.add_argument(
        "--next",
        default="Use this bundle as the frame-level accepted input list for external renderer work.",
    )
    args = parser.parse_args(argv)

    bundle = build_bundle(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, bundle)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(bundle, out_path, os.getcwd()))
    print(
        "status=ok "
        f"frames={bundle['frame_count']} "
        f"missing_assets={bundle['totals']['missing_assets']} "
        f"bundle={out_path}"
    )
    print(f"report={report_path}")
    if bundle["totals"]["missing_assets"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
