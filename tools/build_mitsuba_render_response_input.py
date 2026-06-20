#!/usr/bin/env python
"""Build a secondary-composite wrapper around Mitsuba render previews."""

import argparse
import copy
import os
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


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {
        int(frame.get("output_frame")): frame
        for frame in frames
        if frame.get("output_frame") is not None
    }


def render_preview_path(frame):
    preview = frame.get("preview") or {}
    return preview.get("path") or preview.get("repo_path")


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks", {})
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Base composite: `{summary['source']['base_composite_summary']}`",
        f"- Render manifest: `{summary['source']['render_manifest']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing base frames: `{checks.get('missing_base_frames')}`",
        f"- Missing render previews: `{checks.get('missing_render_previews')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- Layer bytes: `{format_bytes(checks.get('layer_bytes', 0))}`",
        f"- Max layer coverage: `{checks.get('max_layer_coverage')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Source Preview | Layer |",
        "| ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"`{frame.get('composite_repo_path')}` | `{frame.get('layer_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wrap Mitsuba render previews as secondary composite input")
    parser.add_argument("base_composite_summary", help="existing lsfs_mitsuba_secondary_composite summary")
    parser.add_argument("render_manifest", help="lsfs_mitsuba_xml_render manifest")
    parser.add_argument("out_json", help="output secondary composite summary")
    parser.add_argument("--title", default="Mitsuba Render Response Input")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Apply a source-region response to this render-preview wrapper.")
    args = parser.parse_args()

    root = os.getcwd()
    base_path = require_file(args.base_composite_summary, "base composite summary")
    render_path = require_file(args.render_manifest, "render manifest")
    base = read_json(base_path)
    render = read_json(render_path)
    if base.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.base_composite_summary}: expected lsfs_mitsuba_secondary_composite schema")
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.render_manifest}: expected lsfs_mitsuba_xml_render schema")

    base_frames = output_frame_map(base.get("frames") or [])
    render_frames = output_frame_map(render.get("frames") or [])
    frames = []
    missing_base = []
    missing_previews = []
    composite_bytes = 0
    layer_bytes = 0

    for frame_index, output_frame in enumerate(sorted(render_frames)):
        render_frame = render_frames[output_frame]
        base_frame = base_frames.get(output_frame)
        if not base_frame:
            missing_base.append(output_frame)
            continue
        preview_path = resolve_path(render_preview_path(render_frame))
        if not preview_path or not os.path.exists(preview_path):
            missing_previews.append(output_frame)
            continue
        layer_file = require_file(base_frame.get("layer_path") or base_frame.get("layer_repo_path"), "secondary layer")
        item = copy.deepcopy(base_frame)
        item["frame"] = frame_index
        item["output_frame"] = output_frame
        item["sequence_frame"] = render_frame.get("sequence_frame", base_frame.get("sequence_frame"))
        item["composite_repo_path"] = posix_rel(preview_path, root)
        item["composite_sha256"] = sha256_file(preview_path)
        item["composite_size"] = os.path.getsize(preview_path)
        item["preview_repo_path"] = item["composite_repo_path"]
        image_path = resolve_path((render_frame.get("image") or {}).get("path") or (render_frame.get("image") or {}).get("repo_path"))
        if image_path:
            item["render_image_repo_path"] = posix_rel(image_path, root)
        dims = image_dimensions(preview_path)
        if dims:
            item["dimensions"] = dims
        composite_bytes += item["composite_size"]
        layer_bytes += os.path.getsize(layer_file)
        frames.append(item)

    status = "ready" if frames and not missing_base and not missing_previews else "failed"
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source": {
            "base_composite_summary": posix_rel(base_path, root),
            "render_manifest": posix_rel(render_path, root),
        },
        "checks": {
            "frames": len(frames),
            "missing_base_frames": missing_base,
            "missing_render_previews": missing_previews,
            "composite_bytes": composite_bytes,
            "layer_bytes": layer_bytes,
            "max_layer_coverage": max((frame.get("layer_coverage") or 0.0 for frame in frames), default=0.0),
        },
        "frames": frames,
        "next": args.next,
    }

    out_path = os.path.abspath(args.out_json)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_json(out_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, out_path, root, args.next))
    if status != "ready":
        raise SystemExit(f"status={status} summary={out_path}")
    print(f"status=ready frames={len(frames)} summary={out_path}")


if __name__ == "__main__":
    main()
