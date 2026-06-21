#!/usr/bin/env python
"""Attach response-AOV import results to the renderer scene-cache handoff."""

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


def resolve_path(path, root):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(root, str(path).replace("/", os.sep)))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def source_entry(path, root, payload):
    return {
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "subschema": payload.get("subschema"),
        "status": payload.get("status"),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def ref_repo(frame, role):
    ref = ((frame.get("references") or {}).get(role) or {})
    return ref.get("repo_path") or ref.get("source_repo_path") or ref.get("path")


def path_status(repo_path, root):
    resolved = resolve_path(repo_path, root)
    return {
        "repo_path": repo_path,
        "status": "ready" if resolved and os.path.isfile(resolved) else "missing",
        "size": os.path.getsize(resolved) if resolved and os.path.isfile(resolved) else 0,
        "sha256": sha256_file(resolved) if resolved and os.path.isfile(resolved) else None,
    }


def compact_scene(handoff_frame):
    scene = handoff_frame.get("scene") or {}
    return {
        "scene_frame": handoff_frame.get("scene_frame"),
        "scene_frame_index": handoff_frame.get("scene_frame_index"),
        "scene_time": handoff_frame.get("scene_time"),
        "source_cache": scene.get("source_cache"),
        "step": scene.get("step"),
        "time": scene.get("time"),
        "assets": scene.get("assets") or {},
        "counts": scene.get("counts") or {},
        "cinematic": scene.get("cinematic") or {},
    }


def compact_render_data(frame):
    keys = [
        "source_frame",
        "source_time",
        "water_bounds_min",
        "water_bounds_max",
        "water_depth_y_span",
        "water_depth_z_span",
        "water_mesh",
        "water_mesh_face_count",
        "water_mesh_vertex_count",
        "phase_field_cells",
        "phase_field_liquid_volume",
        "primary_liquid_count",
        "primary_gas_count",
        "secondary_counts",
    ]
    return {key: frame.get(key) for key in keys if key in frame}


def gap_metrics(gap):
    if not gap:
        return None
    checks = gap.get("checks") or {}
    return {
        "frames": checks.get("frames"),
        "missing_references": checks.get("missing_references"),
        "mean_gap_mean_abs_diff": checks.get("mean_gap_mean_abs_diff"),
        "max_gap_mean_abs_diff": checks.get("max_gap_mean_abs_diff"),
        "max_gap_max_abs_diff": checks.get("max_gap_max_abs_diff"),
    }


def html_page(summary):
    checks = summary.get("checks") or {}
    frame_rows = "\n".join(
        f"<tr><td>{frame.get('output_frame')}</td><td>{frame.get('scene_frame')}</td>"
        f"<td>{frame.get('source_frame')}</td><td>{frame.get('response_scale')}</td>"
        f"<td>{(frame.get('response_aov_import') or {}).get('max_import_abs_diff')}</td>"
        f"<td>{(frame.get('visual_gate') or {}).get('s585_max_gap_abs')}</td></tr>"
        for frame in (summary.get("frames") or [])[:12]
    )
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Missing", checks.get("missing_references")),
            ("Scale", checks.get("response_scale")),
            ("Import Max", checks.get("max_import_abs_diff")),
            ("S585 Max", checks.get("s585_max_gap_abs")),
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #111a21; --ink: #edf7fb; --muted: #a2b5bf; --line: #2e3d47; --accent: #9fd9ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 16px; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin-bottom: 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    table {{ width: 100%; border-collapse: collapse; border: 1px solid var(--line); background: var(--panel); }}
    th, td {{ text-align: left; border-bottom: 1px solid var(--line); padding: 8px 10px; font-size: 13px; }}
    th {{ color: var(--muted); font-weight: 620; }}
  </style>
</head>
<body>
  <main>
    <h1>{summary['title']}</h1>
    <section class="metrics">{tiles}</section>
    <table>
      <thead><tr><th>Output</th><th>Scene</th><th>Source</th><th>Scale</th><th>Import Max</th><th>S585 Max</th></tr></thead>
      <tbody>{frame_rows}</tbody>
    </table>
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
        "## Inputs",
        "",
        f"- Scene-cache handoff: `{summary['sources']['renderer_scene_cache_handoff']['repo_path']}`",
        f"- Render-data summary: `{summary['sources']['render_data_summary']['repo_path']}`",
        f"- Response AOV contract: `{summary['sources']['response_aov_contract']['repo_path']}`",
        f"- Response AOV consumer: `{summary['sources']['response_aov_consumer']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Response scale: `{checks.get('response_scale')}`",
        f"- Max import abs diff: `{checks.get('max_import_abs_diff')}`",
        f"- Max import mean abs diff: `{checks.get('max_import_mean_abs_diff')}`",
        f"- S577 mean/max/maxabs: `{checks.get('s577_mean_gap_mad')}` / `{checks.get('s577_max_gap_mad')}` / `{checks.get('s577_max_gap_abs')}`",
        f"- S585 mean/max/maxabs: `{checks.get('s585_mean_gap_mad')}` / `{checks.get('s585_max_gap_mad')}` / `{checks.get('s585_max_gap_abs')}`",
        f"- Unique scene frames: `{checks.get('unique_scene_frames')}`",
        f"- Scene frame count mismatch: `{checks.get('scene_frame_count_mismatch')}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Scene | Source | Scale | Import Max | Composite |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('scene_frame')} | {frame.get('source_frame')} | "
            f"{frame.get('response_scale')} | {(frame.get('response_aov_import') or {}).get('max_import_abs_diff')} | "
            f"`{(frame.get('response_aov_import') or {}).get('composite_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    root = os.getcwd()
    handoff_path = require_file(args.handoff_manifest, "scene-cache handoff")
    render_data_path = require_file(args.render_data_summary, "render-data summary")
    contract_path = require_file(args.response_aov_contract, "response AOV contract")
    consumer_path = require_file(args.response_aov_consumer, "response AOV consumer")
    s577_gap_path = require_file(args.s577_gap_summary, "S577 gap summary")
    s585_gap_path = require_file(args.s585_gap_summary, "S585 gap summary")
    handoff = read_json(handoff_path)
    render_data = read_json(render_data_path)
    contract = read_json(contract_path)
    consumer = read_json(consumer_path)
    s577_gap = read_json(s577_gap_path)
    s585_gap = read_json(s585_gap_path)
    if handoff.get("schema") != "lsfs_mitsuba_renderer_scene_cache_handoff":
        raise SystemExit(f"{args.handoff_manifest}: expected lsfs_mitsuba_renderer_scene_cache_handoff")
    if render_data.get("schema") != "lsfs_render_data_summary":
        raise SystemExit(f"{args.render_data_summary}: expected lsfs_render_data_summary")
    if contract.get("schema") != "lsfs_mitsuba_response_aov_contract":
        raise SystemExit(f"{args.response_aov_contract}: expected lsfs_mitsuba_response_aov_contract")
    if consumer.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.response_aov_consumer}: expected lsfs_mitsuba_secondary_composite")

    handoff_by_output = output_frame_map(handoff.get("frames") or [])
    render_by_output = output_frame_map(render_data.get("frames") or [])
    contract_by_output = output_frame_map(contract.get("frames") or [])
    consumer_by_output = output_frame_map(consumer.get("frames") or [])
    frames = []
    missing = []
    for output in sorted(set(handoff_by_output) | set(render_by_output) | set(contract_by_output) | set(consumer_by_output)):
        handoff_frame = handoff_by_output.get(output)
        render_frame = render_by_output.get(output)
        contract_frame = contract_by_output.get(output)
        consumer_frame = consumer_by_output.get(output)
        absent = []
        if not handoff_frame:
            absent.append("handoff_frame")
        if not render_frame:
            absent.append("render_data_frame")
        if not contract_frame:
            absent.append("contract_frame")
        if not consumer_frame:
            absent.append("consumer_frame")
        if absent:
            missing.append({"output_frame": output, "missing": absent})
            continue
        aov_refs = {}
        for role in ("base_rgb", "response_positive_rgb", "response_negative_rgb", "selected_composite_rgb", "full_render_rgb"):
            repo_path = ref_repo(contract_frame, role)
            aov_refs[role] = path_status(repo_path, root)
            if aov_refs[role]["status"] != "ready":
                missing.append({"output_frame": output, "missing": [role], "repo_path": repo_path})
        consumer_composite = consumer_frame.get("composite_repo_path")
        consumer_status = path_status(consumer_composite, root)
        if consumer_status["status"] != "ready":
            missing.append({"output_frame": output, "missing": ["consumer_composite"], "repo_path": consumer_composite})
        frames.append({
            "output_frame": output,
            "frame": handoff_frame.get("frame"),
            "scene_frame": handoff_frame.get("scene_frame"),
            "source_frame": render_frame.get("source_frame"),
            "scene_time": handoff_frame.get("scene_time"),
            "response_scale": (contract.get("settings") or {}).get("response_scale"),
            "scene": compact_scene(handoff_frame),
            "render_data": compact_render_data(render_frame),
            "response_aov_contract": {
                "references": aov_refs,
                "stats": contract_frame.get("stats") or {},
            },
            "response_aov_import": {
                "composite_repo_path": consumer_composite,
                "composite_status": consumer_status["status"],
                "max_import_abs_diff": consumer_frame.get("import_max_abs_diff"),
                "mean_import_abs_diff": consumer_frame.get("import_mean_abs_diff"),
                "mismatched_coverage": consumer_frame.get("import_mismatched_coverage"),
                "strip_repo_path": consumer_frame.get("strip_repo_path"),
            },
            "visual_gate": {
                "s577_mean_gap_mad": (s577_gap.get("checks") or {}).get("mean_gap_mean_abs_diff"),
                "s577_max_gap_mad": (s577_gap.get("checks") or {}).get("max_gap_mean_abs_diff"),
                "s577_max_gap_abs": (s577_gap.get("checks") or {}).get("max_gap_max_abs_diff"),
                "s585_mean_gap_mad": (s585_gap.get("checks") or {}).get("mean_gap_mean_abs_diff"),
                "s585_max_gap_mad": (s585_gap.get("checks") or {}).get("max_gap_mean_abs_diff"),
                "s585_max_gap_abs": (s585_gap.get("checks") or {}).get("max_gap_max_abs_diff"),
            },
        })

    s577 = gap_metrics(s577_gap)
    s585 = gap_metrics(s585_gap)
    unique_scene_frames = len(set(frame.get("scene_frame") for frame in frames))
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "response_scale": (contract.get("settings") or {}).get("response_scale"),
        "max_import_abs_diff": max(((frame.get("response_aov_import") or {}).get("max_import_abs_diff") or 0 for frame in frames), default=0),
        "max_import_mean_abs_diff": max(((frame.get("response_aov_import") or {}).get("mean_import_abs_diff") or 0.0 for frame in frames), default=0.0),
        "s577_mean_gap_mad": (s577 or {}).get("mean_gap_mean_abs_diff"),
        "s577_max_gap_mad": (s577 or {}).get("max_gap_mean_abs_diff"),
        "s577_max_gap_abs": (s577 or {}).get("max_gap_max_abs_diff"),
        "s585_mean_gap_mad": (s585 or {}).get("mean_gap_mean_abs_diff"),
        "s585_max_gap_mad": (s585 or {}).get("max_gap_mean_abs_diff"),
        "s585_max_gap_abs": (s585 or {}).get("max_gap_max_abs_diff"),
        "unique_scene_frames": unique_scene_frames,
        "scene_frame_count_mismatch": unique_scene_frames != len(frames),
    }
    status = "ready" if not missing and checks["max_import_abs_diff"] == 0 else "review"
    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    os.makedirs(gallery_dir, exist_ok=True)
    summary_path = os.path.join(out_dir, args.summary_name)
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_response_aov_scene_handoff",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "sources": {
            "renderer_scene_cache_handoff": source_entry(handoff_path, root, handoff),
            "render_data_summary": source_entry(render_data_path, root, render_data),
            "response_aov_contract": source_entry(contract_path, root, contract),
            "response_aov_consumer": source_entry(consumer_path, root, consumer),
            "s577_gap_summary": source_entry(s577_gap_path, root, s577_gap),
            "s585_gap_summary": source_entry(s585_gap_path, root, s585_gap),
        },
        "checks": checks,
        "missing_references": missing,
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    index_path = os.path.join(gallery_dir, "index.html")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
    }
    write_json(summary_path, summary)
    write_text(index_path, html_page(summary))
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} missing={checks['missing_references']} "
        f"scale={checks['response_scale']} out={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a response-AOV scene-cache handoff")
    parser.add_argument("handoff_manifest")
    parser.add_argument("render_data_summary")
    parser.add_argument("response_aov_contract")
    parser.add_argument("response_aov_consumer")
    parser.add_argument("s577_gap_summary")
    parser.add_argument("s585_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary-name", default="response_aov_scene_handoff_summary.json")
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Handoff")
    parser.add_argument(
        "--next",
        default="Use this handoff to drive renderer/cache jobs with scene data and signed response-AOV visuals together.",
    )
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main()
