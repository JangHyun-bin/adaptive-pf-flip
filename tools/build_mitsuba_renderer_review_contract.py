#!/usr/bin/env python
"""Build a renderer-review contract from Mitsuba render/composite/grade proofs."""

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


def optional_file(path, label):
    if not path:
        return None
    return require_file(path, label)


def json_source(path, label, root):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, payload


def file_artifact(path, label, root, role):
    resolved = require_file(path, label)
    return {
        "label": label,
        "role": role,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }


def source_frame_map(frames, key):
    return {frame.get("frame"): frame for frame in frames if frame.get("frame") is not None}


def build_frames(grade, composite, render, root):
    composite_frames = source_frame_map(composite.get("frames") or [], "frame")
    render_frames = source_frame_map(render.get("frames") or [], "frame")
    frames = []
    missing = []
    for frame in grade.get("frames") or []:
        frame_index = frame.get("frame")
        composite_frame = composite_frames.get(frame_index)
        render_frame = render_frames.get(frame_index)
        graded_path = require_file(frame.get("graded_repo_path"), "graded frame")
        composite_path = require_file(frame.get("source_repo_path"), "composite frame")
        layer_path = None
        base_preview_path = None
        if composite_frame:
            layer_path = composite_frame.get("layer_repo_path")
            base_preview_path = composite_frame.get("preview_repo_path")
        for candidate, label in ((layer_path, "secondary layer"), (base_preview_path, "base preview")):
            if candidate and not os.path.isfile(os.path.abspath(candidate.replace("/", os.sep))):
                missing.append({"frame": frame_index, "label": label, "path": candidate})
        item = {
            "frame": frame_index,
            "output_frame": frame.get("output_frame"),
            "sequence_frame": render_frame.get("sequence_frame") if render_frame else None,
            "base_preview": posix_rel(os.path.abspath(base_preview_path.replace("/", os.sep)), root) if base_preview_path else None,
            "secondary_layer": posix_rel(os.path.abspath(layer_path.replace("/", os.sep)), root) if layer_path else None,
            "composite": posix_rel(composite_path, root),
            "graded": posix_rel(graded_path, root),
            "graded_sha256": sha256_file(graded_path),
            "secondary_counts": composite_frame.get("projected_counts", {}) if composite_frame else {},
            "particles_projected": composite_frame.get("particles_projected") if composite_frame else None,
            "layer_coverage": composite_frame.get("layer_coverage") if composite_frame else None,
        }
        frames.append(item)
    return frames, missing


def build_contract(args):
    root = os.getcwd()
    grade_source, grade = json_source(args.grade_summary, "grade summary", root)
    if grade.get("schema") != "lsfs_mitsuba_composite_grade":
        raise SystemExit(f"{args.grade_summary}: expected lsfs_mitsuba_composite_grade schema")
    composite_path = (grade.get("source") or {}).get("composite_summary")
    composite_source, composite = json_source(composite_path, "secondary composite summary", root)
    if composite.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{composite_path}: expected lsfs_mitsuba_secondary_composite schema")
    render_path = (composite.get("source") or {}).get("render_manifest")
    render_source, render = json_source(render_path, "mitsuba render manifest", root)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{render_path}: expected lsfs_mitsuba_xml_render schema")
    export_path = (render.get("mitsuba_export") or {}).get("path") or (render.get("mitsuba_export") or {}).get("repo_path")
    export_source, export = json_source(export_path, "mitsuba export manifest", root)
    if export.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{export_path}: expected lsfs_mitsuba_xml_export schema")

    publish_manifest_path = optional_file(args.publish_manifest, "publish manifest")
    publish = read_json(publish_manifest_path) if publish_manifest_path else {}
    gallery_index = (grade.get("gallery") or {}).get("index_path") or (grade.get("gallery") or {}).get("index_repo_path")
    gallery_gif = None
    for asset in (grade.get("gallery") or {}).get("assets") or []:
        if asset.get("label") == "Shot GIF":
            gallery_gif = asset.get("asset") or asset.get("repo_path")
            break

    frames, missing_frame_assets = build_frames(grade, composite, render, root)
    artifacts = [
        file_artifact(gallery_index, "gallery_index", root, "review_page"),
        file_artifact(gallery_gif, "shot_gif", root, "animated_review"),
    ]

    checks = {
        "frames": len(frames),
        "missing_frame_assets": len(missing_frame_assets),
        "grade_frames": (grade.get("checks") or {}).get("frames"),
        "composite_frames": (composite.get("checks") or {}).get("frames"),
        "render_frames": (render.get("checks") or {}).get("frames_rendered"),
        "public_url_present": bool(publish.get("public_url")),
    }
    status = "ready" if (
        checks["frames"] > 0
        and checks["missing_frame_assets"] == 0
        and checks["frames"] == checks["grade_frames"] == checks["composite_frames"] == checks["render_frames"]
    ) else "failed"

    return {
        "schema": "lsfs_mitsuba_renderer_review_contract",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "sources": {
            "grade_summary": grade_source,
            "secondary_composite_summary": composite_source,
            "mitsuba_render": render_source,
            "mitsuba_export": export_source,
            "publish_manifest": {
                "path": publish_manifest_path,
                "repo_path": posix_rel(publish_manifest_path, root) if publish_manifest_path else None,
                "sha256": sha256_file(publish_manifest_path) if publish_manifest_path else None,
                "schema": publish.get("schema"),
                "version": publish.get("version"),
            } if publish_manifest_path else None,
        },
        "public_review": {
            "url": publish.get("public_url"),
            "local_url": publish.get("local_url"),
            "status": publish.get("status"),
            "checks": publish.get("checks", []),
        },
        "renderer_contract": {
            "base_renderer": "mitsuba",
            "base_render_schema": render.get("schema"),
            "xml_export_schema": export.get("schema"),
            "secondary_layer": {
                "source": "particle_stream_csv",
                "representation": "screen_space_soft_layer",
                "settings": composite.get("settings", {}),
                "checks": composite.get("checks", {}),
            },
            "grade": {
                "representation": "post_render_review_grade",
                "settings": grade.get("settings", {}),
                "checks": grade.get("checks", {}),
            },
            "future_renderer_expectation": [
                "consume water mesh and phase data from the Mitsuba export chain",
                "consume secondary particles as a layer or volume rather than opaque sphere-only geometry",
                "apply equivalent grade/material intent as renderer settings, not only post-process",
            ],
        },
        "artifacts": artifacts,
        "checks": checks,
        "missing_frame_assets": missing_frame_assets,
        "frames": frames,
        "next": args.next,
    }


def markdown_report(contract, out_path, root):
    checks = contract.get("checks", {})
    public = contract.get("public_review", {})
    lines = [
        f"# {contract['title']}",
        "",
        f"Generated UTC: `{contract['generated_utc']}`",
        f"Contract JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{contract['status']}`",
        f"Public URL: `{public.get('url') or 'n/a'}`",
        "",
        "## Sources",
        "",
    ]
    for key, source in (contract.get("sources") or {}).items():
        if not source:
            continue
        lines.append(f"- {key}: `{source.get('repo_path')}` (`{source.get('schema') or 'n/a'}`)")
    lines.extend([
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Grade frames: `{checks.get('grade_frames')}`",
        f"- Composite frames: `{checks.get('composite_frames')}`",
        f"- Render frames: `{checks.get('render_frames')}`",
        f"- Missing frame assets: `{checks.get('missing_frame_assets')}`",
        f"- Public URL present: `{checks.get('public_url_present')}`",
        "",
        "## Artifacts",
        "",
        "| Label | Role | Size | Path |",
        "| --- | --- | ---: | --- |",
    ])
    for item in contract.get("artifacts", []):
        lines.append(f"| {item['label']} | `{item['role']}` | {format_bytes(item['size'])} | `{item['repo_path']}` |")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Projected | Coverage | Graded |",
        "| ---: | ---: | ---: | ---: | --- |",
    ])
    frames = contract.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('particles_projected')} | "
            f"{frame.get('layer_coverage')} | `{frame.get('graded')}` |"
        )
    if contract.get("missing_frame_assets"):
        lines.extend(["", "## Missing Frame Assets", ""])
        for item in contract["missing_frame_assets"][:12]:
            lines.append(f"- frame `{item.get('frame')}` {item.get('label')}: `{item.get('path')}`")
    lines.extend(["", "## Next", "", contract.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Mitsuba renderer review contract")
    parser.add_argument("grade_summary")
    parser.add_argument("--publish-manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Renderer Review Contract")
    parser.add_argument(
        "--next",
        default="Use this contract to move secondary layer and grade settings into renderer-facing handoff data.",
    )
    args = parser.parse_args(argv)
    contract = build_contract(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, contract)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(contract, out_path, os.getcwd()))
    print(
        f"status={contract['status']} frames={contract['checks']['frames']} "
        f"missing={contract['checks']['missing_frame_assets']} out={out_path}"
    )
    print(f"report={report_path}")
    if contract["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
