#!/usr/bin/env python
"""Compare a scene-depth material backend summary against target and accepted gates."""

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
    resolve_path,
    write_gif,
)
from compare_mitsuba_renderer_scene_depth_material_native_stage import by_frame, diff_block, ref_path


ALLOWED_BACKEND_SCHEMAS = {
    "lsfs_mitsuba_renderer_scene_depth_material_backend_sample",
    "lsfs_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample",
}


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
    gif = next((item for item in assets if item.get("label") == "Backend Compare Strip GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Backend Compare Strip ")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Decision", summary.get("decision")),
            ("Frames", checks.get("frames")),
            ("Backend vs target", checks.get("max_backend_target_abs_diff")),
            ("Backend vs accepted", checks.get("max_backend_accepted_abs_diff")),
            ("Mean accepted", f"{checks.get('max_backend_accepted_mean_diff', 0.0):.4f}"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="backend compare strip gif"></section>' if gif else ""
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
  <p>Promotion gate comparing backend output to the S585 target and S577 accepted composite.</p>
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
        f"- Max backend-vs-target abs diff: `{checks.get('max_backend_target_abs_diff')}`",
        f"- Max backend-vs-target mean diff: `{checks.get('max_backend_target_mean_diff')}`",
        f"- Max backend-vs-accepted abs diff: `{checks.get('max_backend_accepted_abs_diff')}`",
        f"- Max backend-vs-accepted mean diff: `{checks.get('max_backend_accepted_mean_diff')}`",
        f"- Max target-vs-accepted abs diff: `{checks.get('max_target_accepted_abs_diff')}`",
        f"- Max target-vs-accepted mean diff: `{checks.get('max_target_accepted_mean_diff')}`",
        f"- Strip GIF bytes: `{format_bytes(checks.get('strip_gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Backend/Target Max | Backend/Accepted Max | Backend/Accepted Mean | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('backend_vs_target', {}).get('max_abs_diff')} | "
            f"{frame.get('backend_vs_accepted', {}).get('max_abs_diff')} | "
            f"{frame.get('backend_vs_accepted', {}).get('mean_abs_diff')} | "
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
            ("target_preview", target_path),
            ("accepted_composite", accepted_path),
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
    strip_path = os.path.abspath(os.path.join(strips_dir, f"frame_{frame_id:04d}_backend_compare.png"))
    labeled_strip(
        [accepted, backend, target, backend_target["diff_image"], backend_accepted["diff_image"]],
        ["S577 accepted", "backend output", "S585 target", "backend-target x8", "backend-accepted x8"],
        strip_path,
    )
    for block in (backend_target, backend_accepted, target_accepted):
        block.pop("diff_image", None)
    return {
        "status": "passed" if backend_target["max_abs_diff"] == 0 and backend_target["mean_abs_diff"] == 0.0 else "failed",
        "frame": frame_id,
        "output_frame": backend_frame.get("output_frame"),
        "backend_vs_target": backend_target,
        "backend_vs_accepted": backend_accepted,
        "target_vs_accepted": target_accepted,
        "references": {
            "backend_output": posix_rel(backend_path, root),
            "target_preview": posix_rel(target_path, root),
            "accepted_composite": posix_rel(accepted_path, root),
        },
        "strip": file_entry(strip_path, root),
    }


def run(args):
    root = os.getcwd()
    backend_path = require_file(resolve_path(args.backend_summary, root), "backend summary")
    target_path = require_file(resolve_path(args.target_summary, root), "target summary")
    backend = read_json(backend_path)
    target = read_json(target_path)
    if backend.get("schema") not in ALLOWED_BACKEND_SCHEMAS:
        raise SystemExit(f"{args.backend_summary}: expected one of {sorted(ALLOWED_BACKEND_SCHEMAS)}")
    if backend.get("status") != "passed":
        raise SystemExit(f"{args.backend_summary}: backend status is {backend.get('status')!r}")
    if target.get("schema") != "lsfs_mitsuba_renderer_scene_depth_material_target":
        raise SystemExit(f"{args.target_summary}: expected target schema")
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
    passed = [frame for frame in frames if frame.get("status") == "passed"]
    failed = [frame for frame in frames if frame.get("status") != "passed"]
    strip_paths = [resolve_path(frame["strip"]["repo_path"], root) for frame in passed if frame.get("strip")]
    strip_gif_path = os.path.join(out_dir, "backend_compare_strips.gif")
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "backend_compare_strips.gif", "Backend Compare Strip GIF", root))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["strip"]["repo_path"], assets_dir, f"backend_compare_strip_{out_index:02d}.png", f"Backend Compare Strip {out_index + 1}", root))

    checks = {
        "frames": len(frames),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "missing_references": sum(len(frame.get("missing") or []) for frame in failed),
        "max_backend_target_abs_diff": max((frame.get("backend_vs_target", {}).get("max_abs_diff", 999) for frame in frames), default=999),
        "max_backend_target_mean_diff": max((frame.get("backend_vs_target", {}).get("mean_abs_diff", 999.0) for frame in frames), default=999.0),
        "max_backend_accepted_abs_diff": max((frame.get("backend_vs_accepted", {}).get("max_abs_diff", 999) for frame in frames), default=999),
        "max_backend_accepted_mean_diff": max((frame.get("backend_vs_accepted", {}).get("mean_abs_diff", 999.0) for frame in frames), default=999.0),
        "max_target_accepted_abs_diff": max((frame.get("target_vs_accepted", {}).get("max_abs_diff", 999) for frame in frames), default=999),
        "max_target_accepted_mean_diff": max((frame.get("target_vs_accepted", {}).get("mean_abs_diff", 999.0) for frame in frames), default=999.0),
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
    }
    status = "ready" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["max_backend_target_abs_diff"] <= args.max_backend_target_abs_tolerance
        and checks["max_backend_target_mean_diff"] <= args.max_backend_target_mean_tolerance
    ) else "failed"
    decision = "renderer_native_material_ready" if status == "ready" else "hold"

    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_asset(backend_path, assets_dir, "backend_summary.json", "Backend Summary", root),
        copy_asset(target_path, assets_dir, "depth_material_target_summary.json", "Depth Material Target Summary", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_backend_output_compare",
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
            "max_backend_target_abs_tolerance": args.max_backend_target_abs_tolerance,
            "max_backend_target_mean_tolerance": args.max_backend_target_mean_tolerance,
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
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "backend_output_compare_summary.json", "Backend Output Compare Summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    summary_asset = resolve_path(metadata_files[0]["repo_path"], root)
    write_json(summary_asset, summary)
    write_text(index_path, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_backend_output_compare_gallery",
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
        f"status={status} decision={decision} frames={checks['frames']} "
        f"backend_target_max={checks['max_backend_target_abs_diff']} "
        f"backend_accepted_max={checks['max_backend_accepted_abs_diff']} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare a scene-depth material backend output summary")
    parser.add_argument("backend_summary")
    parser.add_argument("target_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-backend-target-abs-tolerance", type=int, default=0)
    parser.add_argument("--max-backend-target-mean-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="S592 Mitsuba Renderer Scene Depth Material Backend Output Compare")
    parser.add_argument(
        "--next",
        default="Use this full48 backend gate before attempting a renderer-native material implementation.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_backend_target_abs_tolerance < 0:
        parser.error("max-backend-target-abs-tolerance must be non-negative")
    if args.max_backend_target_mean_tolerance < 0.0:
        parser.error("max-backend-target-mean-tolerance must be non-negative")
    run(args)


if __name__ == "__main__":
    main()
