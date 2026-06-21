#!/usr/bin/env python
"""Bind response-AOV scene descriptors to the S585 near-accepted visual anchor."""

import argparse
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
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    copy_asset,
    labeled_strip,
    require_pillow,
    resolve_path,
    write_gif,
)
from compare_mitsuba_renderer_scene_depth_material_native_stage import by_frame, diff_block, ref_path


JOB_SCHEMA = "lsfs_mitsuba_response_aov_scene_job_manifest"
TARGET_SCHEMA = "lsfs_mitsuba_renderer_scene_depth_material_target"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_s585_anchor_handoff"


def descriptor_path(frame_job, root):
    ref = frame_job.get("descriptor") or {}
    return require_file(resolve_path(ref.get("repo_path") or ref.get("path"), root), "response-AOV scene descriptor")


def file_entry(path, root):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "S585 Anchor Handoff GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("S585 Anchor Handoff Strip ")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Decision", summary.get("decision")),
            ("Frames", checks.get("frames")),
            ("Missing", checks.get("missing_references")),
            ("S585/S577 max", checks.get("max_anchor_accepted_abs_diff")),
            ("S585/S577 MAD", f"{checks.get('max_anchor_accepted_mean_diff', 0.0):.4f}"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="S585 anchor handoff gif"></section>' if gif else ""
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
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
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
  <p>S585-anchored response-AOV scene handoff. Future native-backend candidates should branch from this near-accepted anchor instead of the stronger S617 response-scale output.</p>
  <section class="tiles">{tiles}</section>
  {hero}
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
        f"Decision: `{summary['decision']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max S585-anchor-vs-S577 abs diff: `{checks.get('max_anchor_accepted_abs_diff')}`",
        f"- Max S585-anchor-vs-S577 mean diff: `{checks.get('max_anchor_accepted_mean_diff')}`",
        f"- Mean S585-anchor-vs-S577 mean diff: `{checks.get('mean_anchor_accepted_mean_diff')}`",
        f"- Strip GIF bytes: `{format_bytes(checks.get('strip_gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Scene | S585/S577 Max | S585/S577 Mean | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        diff = frame.get("anchor_vs_accepted") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('scene_frame')} | "
            f"{diff.get('max_abs_diff')} | {diff.get('mean_abs_diff')} | "
            f"`{frame.get('strip', {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def compare_frame(frame_job, target_frame, root, strips_dir):
    frame_id = int(frame_job.get("frame") or 0)
    descriptor = descriptor_path(frame_job, root)
    anchor_path = ref_path((target_frame.get("references") or {}).get("target_preview"), root)
    accepted_path = ref_path((target_frame.get("references") or {}).get("source_composite"), root)
    missing = [
        name for name, path in (
            ("descriptor", descriptor),
            ("s585_anchor", anchor_path),
            ("s577_accepted", accepted_path),
        )
        if not path or not os.path.isfile(path)
    ]
    if missing:
        return {"status": "failed", "frame": frame_id, "missing": missing}

    anchor = Image.open(anchor_path).convert("RGB")
    accepted = Image.open(accepted_path).convert("RGB")
    if anchor.size != accepted.size:
        return {"status": "failed", "frame": frame_id, "missing": ["dimension_mismatch"]}

    anchor_accepted = diff_block(anchor, accepted)
    strip_path = os.path.abspath(os.path.join(strips_dir, f"frame_{frame_id:04d}_s585_anchor_handoff.png"))
    labeled_strip(
        [accepted, anchor, anchor_accepted["diff_image"]],
        ["S577 accepted", "S585 anchor", "S585-S577 x8"],
        strip_path,
    )
    anchor_accepted.pop("diff_image", None)
    descriptor_json = read_json(descriptor)
    render_data = descriptor_json.get("render_data") or {}
    return {
        "status": "ready",
        "frame": frame_id,
        "output_frame": frame_job.get("output_frame"),
        "scene_frame": frame_job.get("scene_frame"),
        "source_frame": frame_job.get("source_frame"),
        "scene_time": frame_job.get("scene_time"),
        "job_index": frame_job.get("job_index"),
        "descriptor": file_entry(descriptor, root),
        "anchor": file_entry(anchor_path, root),
        "accepted": file_entry(accepted_path, root),
        "anchor_vs_accepted": anchor_accepted,
        "target_control": target_frame.get("control") or {},
        "render_data": {
            "water_depth_y_span": render_data.get("water_depth_y_span"),
            "water_depth_z_span": render_data.get("water_depth_z_span"),
            "water_mesh_face_count": render_data.get("water_mesh_face_count"),
            "secondary_total": ((render_data.get("secondary_counts") or {}).get("total") or 0),
        },
        "strip": file_entry(strip_path, root),
    }


def aggregate(frames, key):
    values = [float((frame.get("anchor_vs_accepted") or {}).get(key)) for frame in frames if frame.get("status") == "ready"]
    if not values:
        return {"max": 999.0, "mean": 999.0}
    return {"max": max(values), "mean": sum(values) / float(len(values))}


def run(args):
    require_pillow()
    root = os.getcwd()
    job_path = require_file(resolve_path(args.job_manifest, root), "S621 response-AOV scene job manifest")
    target_path = require_file(resolve_path(args.target_summary, root), "S585 target summary")
    job = read_json(job_path)
    target = read_json(target_path)
    if job.get("schema") != JOB_SCHEMA:
        raise SystemExit(f"{args.job_manifest}: expected {JOB_SCHEMA}")
    if job.get("status") != "ready":
        raise SystemExit(f"{args.job_manifest}: job manifest status is {job.get('status')!r}")
    if target.get("schema") != TARGET_SCHEMA:
        raise SystemExit(f"{args.target_summary}: expected {TARGET_SCHEMA}")
    if target.get("status") != "ready":
        raise SystemExit(f"{args.target_summary}: target status is {target.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    strips_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (strips_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    target_frames = by_frame(target.get("frames"))
    frames = [
        compare_frame(frame_job, target_frames.get(int(frame_job.get("frame") or 0), {}), root, strips_dir)
        for frame_job in sorted(job.get("frames") or [], key=lambda item: int(item.get("frame") or 0))
    ]
    ready = [frame for frame in frames if frame.get("status") == "ready"]
    failed = [frame for frame in frames if frame.get("status") != "ready"]
    strip_paths = [resolve_path(frame["strip"]["repo_path"], root) for frame in ready if frame.get("strip")]
    strip_gif_path = os.path.join(out_dir, "s585_anchor_handoff_strips.gif")
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "s585_anchor_handoff_strips.gif", "S585 Anchor Handoff GIF", root))
    key_indices = sorted(set(round(i * (len(ready) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if ready else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(ready[frame_index]["strip"]["repo_path"], assets_dir, f"s585_anchor_handoff_strip_{out_index:02d}.png", f"S585 Anchor Handoff Strip {out_index + 1}", root))

    max_abs = aggregate(frames, "max_abs_diff")
    mean_abs = aggregate(frames, "mean_abs_diff")
    checks = {
        "frames": len(frames),
        "ready_frames": len(ready),
        "failed_frames": len(failed),
        "missing_references": sum(len(frame.get("missing") or []) for frame in failed),
        "max_anchor_accepted_abs_diff": int(max_abs["max"]),
        "max_anchor_accepted_mean_diff": mean_abs["max"],
        "mean_anchor_accepted_mean_diff": mean_abs["mean"],
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
    }
    status = "ready" if checks["frames"] > 0 and checks["ready_frames"] == checks["frames"] and checks["failed_frames"] == 0 else "failed"
    decision = "s585_anchor_handoff_ready" if status == "ready" else "hold_missing_refs"

    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "decision": decision,
        "inputs": {
            "job_manifest": posix_rel(job_path, root),
            "target_summary": posix_rel(target_path, root),
            "accepted_gate": "S577 source composite referenced by S585 target frames",
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": index_path,
            "index_repo_path": posix_rel(index_path, root),
            "assets": assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(index_path, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_aov_s585_anchor_handoff_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        "status={status} decision={decision} frames={frames} max_mad={max_mad} summary={summary}".format(
            status=status,
            decision=decision,
            frames=checks["frames"],
            max_mad=checks["max_anchor_accepted_mean_diff"],
            summary=summary_path,
        )
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_manifest", help="S621 response-AOV scene job manifest")
    parser.add_argument("target_summary", help="S585 depth/material target summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S632 Response AOV S585 Anchor Handoff")
    parser.add_argument(
        "--next",
        default="Use this S585 anchor handoff as the input boundary for the next bounded native-backend candidate.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
