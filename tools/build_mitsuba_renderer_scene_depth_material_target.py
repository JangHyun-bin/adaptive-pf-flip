#!/usr/bin/env python
"""Build a native-renderer target manifest from an S584 depth/material sweep."""

import argparse
import os
import shutil
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


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def file_ref(path, root, label, missing, frame=None, hash_file=False):
    resolved = resolve_path(path, root)
    if not resolved or not os.path.isfile(resolved):
        missing.append({"frame": frame, "label": label, "path": path})
        return {"label": label, "status": "missing", "repo_path": path}
    entry = {
        "label": label,
        "status": "ready",
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "size": os.path.getsize(resolved),
    }
    if hash_file:
        entry["sha256"] = sha256_file(resolved)
    dims = image_dimensions(resolved)
    if dims:
        entry["dimensions"] = dims
    return entry


def copy_asset(src, assets_dir, name, label, root):
    resolved = require_file(src, label)
    os.makedirs(assets_dir, exist_ok=True)
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(resolved) != os.path.abspath(dest):
        shutil.copy2(resolved, dest)
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def selected_candidate(sweep):
    selected = sweep.get("selected_candidate")
    if isinstance(selected, dict) and selected.get("label"):
        return selected
    selected_label = selected.get("label") if isinstance(selected, dict) else selected
    for candidate in sweep.get("candidates") or []:
        if candidate.get("label") == selected_label:
            return candidate
    return None


def build_frames(candidate, root, missing):
    frames = []
    for row in candidate.get("frames") or []:
        frame = row.get("frame")
        source = file_ref(row.get("source_composite_repo_path"), root, "source_composite", missing, frame=frame)
        magnitude = file_ref(row.get("magnitude_repo_path"), root, "magnitude_mask", missing, frame=frame)
        preview = file_ref(row.get("preview_repo_path"), root, "target_preview", missing, frame=frame, hash_file=True)
        strip = file_ref(row.get("strip_repo_path"), root, "review_strip", missing, frame=frame)
        frames.append({
            "frame": frame,
            "output_frame": row.get("output_frame"),
            "control": {
                "base_strength": row.get("base_strength"),
                "effective_strength": row.get("strength"),
                "water_y_factor": row.get("water_y_factor"),
                "water_z_factor": row.get("water_z_factor"),
                "formula": "base_strength * (0.30 + 0.45 * water_z_factor + 0.25 * water_y_factor)",
            },
            "expected_delta": {
                "max_abs_delta": row.get("max_abs_delta"),
                "mean_abs_delta": row.get("mean_abs_delta"),
                "changed_coverage": row.get("changed_coverage"),
            },
            "references": {
                "source_composite": source,
                "magnitude_mask": magnitude,
                "target_preview": preview,
                "review_strip": strip,
            },
        })
    return frames


def html_page(summary):
    checks = summary.get("checks") or {}
    selected = summary.get("selected") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in assets
        if item["label"].startswith("Target")
    )
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Target", selected.get("label")),
            ("Frames", checks.get("frames")),
            ("Missing", checks.get("missing_references")),
            ("Max delta", selected.get("checks", {}).get("max_abs_delta")),
            ("Max mean", f"{selected.get('checks', {}).get('max_mean_abs_delta', 0.0):.4f}"),
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
  <p>Native renderer implementation target extracted from the selected S584 sweep candidate.</p>
  <section class="tiles">{tiles}</section>
  <section>{figures}</section>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    selected = summary.get("selected") or {}
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Selected Target",
        "",
        f"- Label: `{selected.get('label')}`",
        f"- Base strength: `{selected.get('base_strength')}`",
        f"- Max absolute delta: `{(selected.get('checks') or {}).get('max_abs_delta')}`",
        f"- Max mean absolute delta: `{(selected.get('checks') or {}).get('max_mean_abs_delta')}`",
        f"- Max changed coverage: `{(selected.get('checks') or {}).get('max_changed_coverage')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Ready target previews: `{checks.get('ready_target_previews')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Effective Strength | Max Delta | Mean Delta | Target | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        control = frame.get("control") or {}
        delta = frame.get("expected_delta") or {}
        refs = frame.get("references") or {}
        target = (refs.get("target_preview") or {}).get("repo_path")
        strip = (refs.get("review_strip") or {}).get("repo_path")
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {control.get('effective_strength')} | "
            f"{delta.get('max_abs_delta')} | {delta.get('mean_abs_delta')} | `{target}` | `{strip}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    sweep_path = require_file(args.sweep_summary, "scene-depth material sweep summary")
    sweep = read_json(sweep_path)
    if sweep.get("schema") != "lsfs_mitsuba_renderer_scene_depth_material_sweep":
        raise SystemExit(f"{args.sweep_summary}: expected lsfs_mitsuba_renderer_scene_depth_material_sweep schema")
    selected = selected_candidate(sweep)
    if not selected:
        raise SystemExit(f"{args.sweep_summary}: no selected candidate")
    if not selected.get("feasible", False):
        raise SystemExit(f"{args.sweep_summary}: selected candidate is not feasible")

    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    missing = []
    frames = build_frames(selected, root, missing)
    ready_target_previews = sum(
        1 for frame in frames
        if ((frame.get("references") or {}).get("target_preview") or {}).get("status") == "ready"
    )
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "ready_target_previews": ready_target_previews,
    }
    status = "ready" if frames and not missing and ready_target_previews == len(frames) else "failed"
    summary_path = os.path.abspath(args.summary)
    assets = []
    selected_gif = selected.get("gif_path") or selected.get("gif_repo_path")
    if selected_gif:
        assets.append(copy_asset(selected_gif, assets_dir, "selected_depth_material_target.gif", "Target GIF", root))
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for out_index, frame_index in enumerate(sample_indices):
        strip = ((frames[frame_index].get("references") or {}).get("review_strip") or {}).get("path")
        if strip:
            assets.append(copy_asset(strip, assets_dir, f"target_strip_{out_index:02d}.png", f"Target Strip {out_index + 1}", root))
    metadata_files = [
        copy_asset(sweep_path, assets_dir, "depth_material_sweep_summary.json", "Depth material sweep summary", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_target",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "inputs": {
            "sweep_summary": posix_rel(sweep_path, root),
            "handoff_manifest": (sweep.get("inputs") or {}).get("handoff_manifest"),
            "render_data_summary": (sweep.get("inputs") or {}).get("render_data_summary"),
        },
        "selected": {
            "label": selected.get("label"),
            "base_strength": selected.get("base_strength"),
            "checks": selected.get("checks", {}),
        },
        "renderer_contract": {
            "control_kind": "scene_depth_material",
            "implementation_target": "native_renderer_material_or_tonemap_stage",
            "formula": "effective_strength = base_strength * (0.30 + 0.45 * water_z_factor + 0.25 * water_y_factor)",
            "localization_texture": "applied_magnitude_luma",
            "source_image": "S577 accepted low-frequency texture consumer composite",
        },
        "checks": checks,
        "missing_references": missing,
        "frames": frames,
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
    gallery_metadata_files = [
        copy_asset(summary_path, assets_dir, "depth_material_target_summary.json", "Depth material target summary", root),
        *metadata_files,
    ]
    write_text(summary["gallery"]["index_path"], html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_target_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": summary["gallery"]["index_repo_path"],
        "assets": assets,
        "metadata_files": gallery_metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} selected={selected.get('label')} frames={checks['frames']} "
        f"missing={checks['missing_references']} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a renderer scene-depth material implementation target")
    parser.add_argument("sweep_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S585 Mitsuba Renderer Scene Depth Material Target")
    parser.add_argument(
        "--next",
        default="Implement this target in the native renderer path and compare the native result against the S585 preview references.",
    )
    args = parser.parse_args(argv)
    build(args)


if __name__ == "__main__":
    main()
