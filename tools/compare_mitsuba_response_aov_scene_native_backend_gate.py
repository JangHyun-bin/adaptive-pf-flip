#!/usr/bin/env python
"""Compare the response-AOV native backend output against S577/S585 gates."""

import argparse
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
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
from compare_mitsuba_renderer_scene_depth_material_native_stage import by_frame, diff_block, file_entry, ref_path


BACKEND_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_backend_adapter"
TARGET_SCHEMA = "lsfs_mitsuba_renderer_scene_depth_material_target"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_backend_gate_compare"


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "Response AOV Backend Gate Strip GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Response AOV Backend Gate Strip ")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Decision", summary.get("decision")),
            ("Frames", checks.get("frames")),
            ("S629 vs S585 max", checks.get("max_backend_target_abs_diff")),
            ("S629 vs S577 max", checks.get("max_backend_accepted_abs_diff")),
            ("S629 vs S577 MAD", f"{checks.get('max_backend_accepted_mean_diff', 0.0):.4f}"),
            ("S585 vs S577 MAD", f"{checks.get('max_target_accepted_mean_diff', 0.0):.4f}"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="response AOV backend gate strip gif"></section>' if gif else ""
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
  <p>Review gate comparing the promoted S629 response-AOV native backend output against the S585 target and S577 accepted composite.</p>
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
        f"- Measured frames: `{checks.get('measured_frames')}`",
        f"- Failed frames: `{checks.get('failed_frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max backend-vs-S585 abs diff: `{checks.get('max_backend_target_abs_diff')}`",
        f"- Max backend-vs-S585 mean diff: `{checks.get('max_backend_target_mean_diff')}`",
        f"- Mean backend-vs-S585 mean diff: `{checks.get('mean_backend_target_mean_diff')}`",
        f"- Max backend-vs-S577 abs diff: `{checks.get('max_backend_accepted_abs_diff')}`",
        f"- Max backend-vs-S577 mean diff: `{checks.get('max_backend_accepted_mean_diff')}`",
        f"- Mean backend-vs-S577 mean diff: `{checks.get('mean_backend_accepted_mean_diff')}`",
        f"- Max S585-vs-S577 abs diff: `{checks.get('max_target_accepted_abs_diff')}`",
        f"- Max S585-vs-S577 mean diff: `{checks.get('max_target_accepted_mean_diff')}`",
        f"- Mean S585-vs-S577 mean diff: `{checks.get('mean_target_accepted_mean_diff')}`",
        f"- Strip GIF bytes: `{format_bytes(checks.get('strip_gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | S629/S585 Max | S629/S577 Max | S629/S577 Mean | S585/S577 Mean | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = [frame for frame in summary.get("frames") or [] if frame.get("status") == "measured"]
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('backend_vs_target', {}).get('max_abs_diff')} | "
            f"{frame.get('backend_vs_accepted', {}).get('max_abs_diff')} | "
            f"{frame.get('backend_vs_accepted', {}).get('mean_abs_diff')} | "
            f"{frame.get('target_vs_accepted', {}).get('mean_abs_diff')} | "
            f"`{frame.get('strip', {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def compare_frame(backend_frame, target_frame, root, strips_dir):
    frame_id = int(backend_frame.get("frame") or 0)
    backend_path = resolve_path(backend_frame.get("output_image_repo_path"), root)
    target_path = ref_path((target_frame.get("references") or {}).get("target_preview"), root)
    accepted_path = ref_path((target_frame.get("references") or {}).get("source_composite"), root)
    missing = [
        name for name, path in (
            ("backend_output", backend_path),
            ("s585_target_preview", target_path),
            ("s577_accepted_composite", accepted_path),
        )
        if not path or not os.path.isfile(path)
    ]
    if missing:
        return {"status": "failed", "frame": frame_id, "missing": missing}

    backend = Image.open(backend_path).convert("RGB")
    target = Image.open(target_path).convert("RGB")
    accepted = Image.open(accepted_path).convert("RGB")
    if backend.size != target.size or backend.size != accepted.size:
        return {"status": "failed", "frame": frame_id, "missing": ["dimension_mismatch"]}

    backend_target = diff_block(backend, target)
    backend_accepted = diff_block(backend, accepted)
    target_accepted = diff_block(target, accepted)
    strip_path = os.path.abspath(os.path.join(strips_dir, f"frame_{frame_id:04d}_response_aov_backend_gate.png"))
    labeled_strip(
        [accepted, backend, target, backend_target["diff_image"], backend_accepted["diff_image"]],
        ["S577 accepted", "S629 backend", "S585 target", "S629-S585 x8", "S629-S577 x8"],
        strip_path,
    )
    for block in (backend_target, backend_accepted, target_accepted):
        block.pop("diff_image", None)
    return {
        "status": "measured",
        "frame": frame_id,
        "output_frame": backend_frame.get("output_frame"),
        "scene_frame": backend_frame.get("scene_frame"),
        "source_frame": backend_frame.get("source_frame"),
        "backend_vs_target": backend_target,
        "backend_vs_accepted": backend_accepted,
        "target_vs_accepted": target_accepted,
        "references": {
            "backend_output": posix_rel(backend_path, root),
            "s585_target_preview": posix_rel(target_path, root),
            "s577_accepted_composite": posix_rel(accepted_path, root),
        },
        "strip": file_entry(strip_path, root),
    }


def aggregate(frames, key, stat):
    values = [frame.get(key, {}).get(stat) for frame in frames if frame.get("status") == "measured"]
    values = [float(value) for value in values if value is not None]
    if not values:
        return {"max": 999.0, "mean": 999.0}
    return {"max": max(values), "mean": sum(values) / float(len(values))}


def decision_from_checks(checks):
    if checks["failed_frames"] or checks["missing_references"]:
        return "hold_missing_refs"
    if checks["max_backend_accepted_mean_diff"] <= checks["max_target_accepted_mean_diff"]:
        return "matches_or_improves_s585_accepted_gap"
    return "review_candidate_needs_visual_decision"


def run(args):
    require_pillow()
    root = os.getcwd()
    backend_path = require_file(resolve_path(args.backend_summary, root), "S629 backend summary")
    target_path = require_file(resolve_path(args.target_summary, root), "S585 target summary")
    backend = read_json(backend_path)
    target = read_json(target_path)
    if backend.get("schema") != BACKEND_SCHEMA:
        raise SystemExit(f"{args.backend_summary}: expected {BACKEND_SCHEMA}")
    if backend.get("status") != "passed":
        raise SystemExit(f"{args.backend_summary}: backend status is {backend.get('status')!r}")
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
        compare_frame(frame, target_frames.get(int(frame.get("frame") or 0), {}), root, strips_dir)
        for frame in sorted(backend.get("frames") or [], key=lambda item: int(item.get("frame") or 0))
    ]
    measured = [frame for frame in frames if frame.get("status") == "measured"]
    failed = [frame for frame in frames if frame.get("status") != "measured"]
    strip_paths = [resolve_path(frame["strip"]["repo_path"], root) for frame in measured if frame.get("strip")]
    strip_gif_path = os.path.join(out_dir, "response_aov_backend_gate_strips.gif")
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "response_aov_backend_gate_strips.gif", "Response AOV Backend Gate Strip GIF", root))
    key_indices = sorted(set(round(i * (len(measured) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if measured else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(measured[frame_index]["strip"]["repo_path"], assets_dir, f"response_aov_backend_gate_strip_{out_index:02d}.png", f"Response AOV Backend Gate Strip {out_index + 1}", root))

    backend_target_abs = aggregate(frames, "backend_vs_target", "max_abs_diff")
    backend_target_mean = aggregate(frames, "backend_vs_target", "mean_abs_diff")
    backend_accepted_abs = aggregate(frames, "backend_vs_accepted", "max_abs_diff")
    backend_accepted_mean = aggregate(frames, "backend_vs_accepted", "mean_abs_diff")
    target_accepted_abs = aggregate(frames, "target_vs_accepted", "max_abs_diff")
    target_accepted_mean = aggregate(frames, "target_vs_accepted", "mean_abs_diff")
    checks = {
        "frames": len(frames),
        "measured_frames": len(measured),
        "failed_frames": len(failed),
        "missing_references": sum(len(frame.get("missing") or []) for frame in failed),
        "max_backend_target_abs_diff": int(backend_target_abs["max"]),
        "max_backend_target_mean_diff": backend_target_mean["max"],
        "mean_backend_target_mean_diff": backend_target_mean["mean"],
        "max_backend_accepted_abs_diff": int(backend_accepted_abs["max"]),
        "max_backend_accepted_mean_diff": backend_accepted_mean["max"],
        "mean_backend_accepted_mean_diff": backend_accepted_mean["mean"],
        "max_target_accepted_abs_diff": int(target_accepted_abs["max"]),
        "max_target_accepted_mean_diff": target_accepted_mean["max"],
        "mean_target_accepted_mean_diff": target_accepted_mean["mean"],
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
    }
    status = "ready" if checks["frames"] > 0 and checks["measured_frames"] == checks["frames"] and checks["failed_frames"] == 0 else "failed"
    decision = decision_from_checks(checks)

    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_asset(backend_path, assets_dir, "response_aov_native_backend_summary.json", "Response AOV Native Backend Summary", root),
        copy_asset(target_path, assets_dir, "depth_material_target_summary.json", "Depth Material Target Summary", root),
    ]
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "decision": decision,
        "inputs": {
            "backend_summary": posix_rel(backend_path, root),
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
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "response_aov_backend_gate_compare_summary.json", "Response AOV Backend Gate Compare Summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    summary_asset = resolve_path(metadata_files[0]["repo_path"], root)
    write_json(summary_asset, summary)
    write_text(index_path, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_aov_scene_native_backend_gate_compare_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        "status={status} decision={decision} frames={frames} "
        "s629_s585_max={target_max} s629_s577_max={accepted_max} summary={summary}".format(
            status=status,
            decision=decision,
            frames=checks["frames"],
            target_max=checks["max_backend_target_abs_diff"],
            accepted_max=checks["max_backend_accepted_abs_diff"],
            summary=summary_path,
        )
    )
    if status != "ready" and args.fail_on_missing:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend_summary", help="S629 response-AOV native backend summary")
    parser.add_argument("target_summary", help="S585 depth/material target summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S630 Response AOV Native Backend Gate Compare")
    parser.add_argument(
        "--next",
        default="Use this S577/S585 gap report to decide whether BOLD_SAFE should be tuned, published, or kept as a review-only candidate.",
    )
    parser.add_argument("--fail-on-missing", action="store_true")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
