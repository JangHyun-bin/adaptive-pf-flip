#!/usr/bin/env python
"""Run a bounded scene-depth material strength sweep over a renderer handoff."""

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
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    ImageOps,
    consumer_ref,
    copy_asset,
    diff_image,
    labeled_strip,
    metric_bounds,
    normalized,
    preview_image,
    render_data_by_output,
    require_pillow,
    resolve_path,
    texture_ref,
    write_gif,
)


def slug_strength(value):
    return f"strength_{str(value).replace('.', '_')}"


def parse_strengths(text):
    values = []
    for item in str(text).split(","):
        item = item.strip()
        if not item:
            continue
        value = float(item)
        if value <= 0.0 or value > 1.0:
            raise argparse.ArgumentTypeError("strengths must be in (0, 1.0]")
        values.append(value)
    if not values:
        raise argparse.ArgumentTypeError("at least one strength is required")
    return values


def load_inputs(handoff_manifest, render_data_summary, root):
    handoff_path = require_file(handoff_manifest, "renderer scene-cache handoff")
    render_data_path = require_file(render_data_summary, "render data summary")
    handoff = read_json(handoff_path)
    render_data = read_json(render_data_path)
    if handoff.get("schema") != "lsfs_mitsuba_renderer_scene_cache_handoff":
        raise SystemExit(f"{handoff_manifest}: expected lsfs_mitsuba_renderer_scene_cache_handoff schema")
    if render_data.get("schema") != "lsfs_render_data_summary":
        raise SystemExit(f"{render_data_summary}: expected lsfs_render_data_summary schema")

    data_by_output = render_data_by_output(render_data)
    data_frames = render_data.get("frames") or []
    y_bounds = metric_bounds(data_frames, "water_depth_y_span")
    z_bounds = metric_bounds(data_frames, "water_depth_z_span")
    frame_inputs = []
    missing = []
    for index, frame in enumerate(handoff.get("frames") or []):
        output = frame.get("output_frame")
        data = data_by_output.get(output, {})
        composite_path = resolve_path(consumer_ref(frame, "composite"), root)
        magnitude_path = resolve_path(texture_ref(frame, "applied_magnitude_luma"), root)
        absent = []
        if not composite_path or not os.path.isfile(composite_path):
            absent.append("consumer_composite")
        if not magnitude_path or not os.path.isfile(magnitude_path):
            absent.append("applied_magnitude_luma")
        if absent:
            missing.append({"frame": index, "output_frame": output, "missing": absent})
            continue
        frame_inputs.append({
            "frame": index,
            "output_frame": output,
            "composite_path": composite_path,
            "magnitude_path": magnitude_path,
            "water_y_factor": normalized(data.get("water_depth_y_span"), y_bounds),
            "water_z_factor": normalized(data.get("water_depth_z_span"), z_bounds),
        })
    return {
        "handoff_path": handoff_path,
        "render_data_path": render_data_path,
        "handoff": handoff,
        "render_data": render_data,
        "frames": frame_inputs,
        "missing": missing,
    }


def render_candidate(inputs, strength, out_dir, root, fps, keyframes):
    candidate_dir = os.path.join(out_dir, slug_strength(strength))
    frames_dir = os.path.join(candidate_dir, "frames")
    strips_dir = os.path.join(candidate_dir, "strips")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(strips_dir, exist_ok=True)

    rows = []
    preview_paths = []
    strip_paths = []
    for item in inputs["frames"]:
        base = Image.open(item["composite_path"]).convert("RGB")
        magnitude = Image.open(item["magnitude_path"]).convert("L")
        if base.size != magnitude.size:
            raise SystemExit(f"frame {item['frame']}: base and magnitude dimensions differ")
        effective_strength = strength * (0.30 + 0.45 * item["water_z_factor"] + 0.25 * item["water_y_factor"])
        preview, stats = preview_image(base, magnitude, effective_strength)
        preview_path = os.path.join(frames_dir, f"frame_{item['frame']:04d}.png")
        preview.save(preview_path)
        preview_paths.append(preview_path)

        mask_visual = ImageOps.colorize(magnitude, black=(6, 12, 18), white=(255, 218, 120))
        diff = diff_image(preview, base)
        strip_path = os.path.join(strips_dir, f"frame_{item['frame']:04d}_depth_material_sweep.png")
        labeled_strip(
            [base, mask_visual, preview, diff],
            ["accepted input", "lf magnitude mask", "sweep preview", "preview diff x16"],
            strip_path,
        )
        strip_paths.append(strip_path)
        rows.append({
            "frame": item["frame"],
            "output_frame": item["output_frame"],
            "preview_repo_path": posix_rel(preview_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "source_composite_repo_path": posix_rel(item["composite_path"], root),
            "magnitude_repo_path": posix_rel(item["magnitude_path"], root),
            "strength": effective_strength,
            "base_strength": strength,
            "water_y_factor": item["water_y_factor"],
            "water_z_factor": item["water_z_factor"],
            "max_abs_delta": stats["max_abs_delta"],
            "mean_abs_delta": stats["mean_abs_delta"],
            "changed_coverage": stats["changed_coverage"],
            "sha256": sha256_file(preview_path),
            "size": os.path.getsize(preview_path),
        })

    gif_path = os.path.join(candidate_dir, "depth_material_sweep.gif")
    write_gif(preview_paths, gif_path, fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes)))
    return {
        "label": slug_strength(strength),
        "base_strength": strength,
        "path": candidate_dir,
        "repo_path": posix_rel(candidate_dir, root),
        "gif_path": gif_path,
        "gif_repo_path": posix_rel(gif_path, root),
        "frames": rows,
        "sample_strips": [strip_paths[index] for index in key_indices],
        "checks": {
            "frames": len(rows),
            "missing_references": len(inputs["missing"]),
            "max_abs_delta": max((row["max_abs_delta"] for row in rows), default=0),
            "max_mean_abs_delta": max((row["mean_abs_delta"] for row in rows), default=0.0),
            "mean_mean_abs_delta": sum((row["mean_abs_delta"] for row in rows), 0.0) / float(max(1, len(rows))),
            "max_changed_coverage": max((row["changed_coverage"] for row in rows), default=0.0),
            "gif_bytes": os.path.getsize(gif_path),
        },
    }


def candidate_score(candidate):
    checks = candidate.get("checks") or {}
    return (
        float(checks.get("max_mean_abs_delta") or 0.0),
        float(checks.get("max_changed_coverage") or 0.0),
        float(checks.get("max_abs_delta") or 0.0),
    )


def select_candidate(candidates, max_abs_tolerance, mean_abs_tolerance):
    feasible = [
        c for c in candidates
        if (c.get("checks") or {}).get("max_abs_delta", 999999) <= max_abs_tolerance
        and (c.get("checks") or {}).get("max_mean_abs_delta", 999999.0) <= mean_abs_tolerance
        and (c.get("checks") or {}).get("missing_references", 1) == 0
    ]
    if not feasible:
        return None
    return max(feasible, key=candidate_score)


def html_page(summary):
    checks = summary.get("checks") or {}
    selected = summary.get("selected_candidate") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in assets
        if item["label"].startswith("Candidate Strip") or item["label"].startswith("Candidate GIF")
    )
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Candidates", checks.get("candidates")),
            ("Selected", selected.get("label")),
            ("Max delta", selected.get("checks", {}).get("max_abs_delta")),
            ("Max mean", f"{selected.get('checks', {}).get('max_mean_abs_delta', 0.0):.4f}"),
            ("Coverage", f"{selected.get('checks', {}).get('max_changed_coverage', 0.0):.4f}"),
        )
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
    figure {{ border: 1px solid var(--line); background: #0d1820; overflow-x: auto; margin: 0 0 12px; }}
    img {{ display: block; max-width: none; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Bounded S584 sweep over the S578/S580 scene-depth material control.</p>
  <section class="tiles">{tiles}</section>
  <section>{figures}</section>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    selected = summary.get("selected_candidate") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        f"Selected candidate: `{selected.get('label')}`",
        "",
        "## Candidates",
        "",
        "| Candidate | Strength | Feasible | Max Delta | Max Mean | Coverage | GIF |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for candidate in summary.get("candidates") or []:
        checks = candidate.get("checks") or {}
        lines.append(
            f"| `{candidate.get('label')}` | {candidate.get('base_strength')} | "
            f"`{candidate.get('feasible')}` | {checks.get('max_abs_delta')} | "
            f"{checks.get('max_mean_abs_delta')} | {checks.get('max_changed_coverage')} | "
            f"`{candidate.get('gif_repo_path')}` |"
        )
    lines.extend([
        "",
        "## Selected",
        "",
        f"- Label: `{selected.get('label')}`",
        f"- Base strength: `{selected.get('base_strength')}`",
        f"- Max absolute delta: `{(selected.get('checks') or {}).get('max_abs_delta')}`",
        f"- Max mean absolute delta: `{(selected.get('checks') or {}).get('max_mean_abs_delta')}`",
        f"- Max changed coverage: `{(selected.get('checks') or {}).get('max_changed_coverage')}`",
        "",
        "## Next",
        "",
        summary.get("next", ""),
        "",
    ])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    candidate_root = os.path.join(out_dir, "candidates")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(candidate_root, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    inputs = load_inputs(args.handoff_manifest, args.render_data_summary, root)
    candidates = [
        render_candidate(inputs, strength, candidate_root, root, args.fps, args.keyframes)
        for strength in args.strengths
    ]
    for candidate in candidates:
        checks = candidate.get("checks") or {}
        candidate["feasible"] = (
            checks.get("missing_references", 1) == 0
            and checks.get("max_abs_delta", 999999) <= args.max_abs_tolerance
            and checks.get("max_mean_abs_delta", 999999.0) <= args.mean_abs_tolerance
        )
    selected = select_candidate(candidates, args.max_abs_tolerance, args.mean_abs_tolerance)
    status = "ready" if selected else "failed"
    summary_path = os.path.abspath(args.summary)
    assets = []
    for candidate in candidates:
        label = candidate["label"]
        assets.append(copy_asset(candidate["gif_path"], assets_dir, f"{label}.gif", f"Candidate GIF {label}", root))
        for index, strip in enumerate(candidate["sample_strips"]):
            assets.append(copy_asset(strip, assets_dir, f"{label}_strip_{index:02d}.png", f"Candidate Strip {label} #{index + 1}", root))
    metadata_files = [
        copy_asset(inputs["handoff_path"], assets_dir, "renderer_scene_cache_handoff_summary.json", "Renderer scene-cache handoff", root),
        copy_asset(inputs["render_data_path"], assets_dir, "render_data_summary.json", "Render data summary", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_sweep",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "inputs": {
            "handoff_manifest": posix_rel(inputs["handoff_path"], root),
            "render_data_summary": posix_rel(inputs["render_data_path"], root),
        },
        "settings": {
            "strengths": args.strengths,
            "fps": args.fps,
            "keyframes": args.keyframes,
            "max_abs_tolerance": args.max_abs_tolerance,
            "mean_abs_tolerance": args.mean_abs_tolerance,
        },
        "checks": {
            "candidates": len(candidates),
            "frames_per_candidate": len(inputs["frames"]),
            "input_missing_references": len(inputs["missing"]),
            "feasible_candidates": sum(1 for candidate in candidates if candidate.get("feasible")),
        },
        "selected_candidate": selected or {},
        "candidates": candidates,
        "missing_references": inputs["missing"],
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": os.path.join(gallery_dir, "index.html"),
            "index_repo_path": posix_rel(os.path.join(gallery_dir, "index.html"), root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "depth_material_sweep_summary.json", "Depth material sweep summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(summary["gallery"]["index_path"], html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_sweep_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": summary["gallery"]["index_repo_path"],
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} candidates={len(candidates)} feasible={summary['checks']['feasible_candidates']} "
        f"selected={(selected or {}).get('label')} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a bounded scene-depth material strength sweep")
    parser.add_argument("handoff_manifest")
    parser.add_argument("render_data_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--strengths", type=parse_strengths, default=parse_strengths("0.35,0.65,0.85,1.0"))
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=8)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.8)
    parser.add_argument("--title", default="S584 Mitsuba Renderer Scene Depth Material Sweep")
    parser.add_argument(
        "--next",
        default="Use the selected sweep candidate as the target for a native renderer-side depth/material implementation, then compare it against S577 and S582.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    build(args)


if __name__ == "__main__":
    main()
