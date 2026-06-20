#!/usr/bin/env python
"""Run a scene-depth material target through a backend executable sample."""

import argparse
import os
import subprocess
import sys
import time
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
    copy_asset,
    resolve_path,
    write_gif,
)


SCENE_SCHEMA = "lsfs_mitsuba_renderer_scene_depth_material_backend_scene_descriptor"
STAGE = "renderer_scene_depth_material_tonemap_sample"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def log_entry(path, root, label):
    entry = {
        "label": label,
        "repo_path": posix_rel(path, root),
        "size": os.path.getsize(path) if os.path.isfile(path) else 0,
    }
    if os.path.isfile(path):
        entry["sha256"] = sha256_file(path)
    return entry


def file_entry(path, root, label=None):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if label:
        entry["label"] = label
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def ref_path(ref, root):
    if isinstance(ref, dict):
        return resolve_path(ref.get("path") or ref.get("repo_path"), root)
    return resolve_path(ref, root)


def selected_frames(frames, count):
    ordered = sorted(frames or [], key=lambda item: int(item.get("frame") or 0))
    if count <= 0 or count >= len(ordered):
        return ordered
    indices = sorted(set(round(i * (len(ordered) - 1) / float(max(1, count - 1))) for i in range(count)))
    return [ordered[index] for index in indices]


def target_file_ref(ref, root, role):
    path = ref_path(ref, root)
    if not path or not os.path.isfile(path):
        return {"role": role, "status": "missing", "repo_path": (ref or {}).get("repo_path") if isinstance(ref, dict) else ref}
    entry = file_entry(path, root, role)
    entry["role"] = role
    entry["status"] = "present"
    return entry


def scene_descriptor(target_frame, job_index, root, out_dir, backend_script):
    frame_id = int(target_frame.get("frame") or 0)
    frame_name = f"frame_{frame_id:04d}"
    scene_path = os.path.abspath(os.path.join(out_dir, "scenes", f"{frame_name}_scene_depth_material_backend_scene.json"))
    output_image = os.path.abspath(os.path.join(out_dir, "backend_frames", f"{frame_name}.png"))
    output_metadata = os.path.abspath(os.path.join(out_dir, "backend_metadata", f"{frame_name}_metadata.json"))
    output_validation = os.path.abspath(os.path.join(out_dir, "backend_validation", f"{frame_name}_validation.json"))
    refs = target_frame.get("references") or {}
    descriptor = {
        "schema": SCENE_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "job_index": job_index,
        "frame": frame_id,
        "output_frame": target_frame.get("output_frame"),
        "stage": STAGE,
        "backend": {
            "kind": "scene_depth_material_tonemap_backend",
            "command": posix_rel(backend_script, root),
            "adapter_mode": "external_backend_executable_sample",
        },
        "controls": target_frame.get("control") or {},
        "inputs": {
            "source_composite": target_file_ref(refs.get("source_composite"), root, "source_composite"),
            "magnitude_mask": target_file_ref(refs.get("magnitude_mask"), root, "magnitude_mask"),
            "target_preview": target_file_ref(refs.get("target_preview"), root, "target_preview"),
        },
        "outputs": {
            "image": {"repo_path": posix_rel(output_image, root), "format": "png", "semantics": "backend tonemap output"},
            "metadata": {"repo_path": posix_rel(output_metadata, root), "format": "json", "semantics": "backend metadata"},
            "validation": {"repo_path": posix_rel(output_validation, root), "format": "json", "semantics": "backend validation"},
        },
        "validation_expectations": {
            "max_abs_diff": 0,
            "max_mean_diff": 0.0,
        },
    }
    ensure_dir(os.path.dirname(scene_path))
    write_json(scene_path, descriptor)
    return scene_path, descriptor


def command_for_frame(backend_script, scene_path, result_path, strip_path):
    return [
        sys.executable,
        backend_script,
        "--scene",
        scene_path,
        "--result",
        result_path,
        "--strip",
        strip_path,
        "--fail-on-review",
    ]


def file_exists(path):
    return bool(path and os.path.isfile(path))


def run_frame(backend_script, scene_path, descriptor, root, out_dir, timeout):
    job_index = int(descriptor.get("job_index") or 0)
    frame_id = int(descriptor.get("frame") or 0)
    strip_path = os.path.abspath(os.path.join(out_dir, "strips", f"frame_{frame_id:04d}_backend_sample.png"))
    result_path = os.path.abspath(os.path.join(out_dir, "results", f"frame_{frame_id:04d}_backend_sample_result.json"))
    stdout_path = os.path.abspath(os.path.join(out_dir, "logs", f"frame_{frame_id:04d}_stdout.log"))
    stderr_path = os.path.abspath(os.path.join(out_dir, "logs", f"frame_{frame_id:04d}_stderr.log"))
    for path in (strip_path, result_path, stdout_path, stderr_path):
        ensure_dir(os.path.dirname(path))

    command = command_for_frame(backend_script, scene_path, result_path, strip_path)
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=timeout, check=False)
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    write_text(stdout_path, proc.stdout or "")
    write_text(stderr_path, proc.stderr or "")
    result = read_json(result_path) if os.path.isfile(result_path) else {}
    outputs = descriptor.get("outputs") or {}
    output_image = resolve_path((outputs.get("image") or {}).get("repo_path"), root)
    output_metadata = resolve_path((outputs.get("metadata") or {}).get("repo_path"), root)
    output_validation = resolve_path((outputs.get("validation") or {}).get("repo_path"), root)
    validation = read_json(output_validation) if file_exists(output_validation) else {}
    diff = validation.get("diff") or {}
    status = "passed" if (
        proc.returncode == 0
        and result.get("status") == "passed"
        and validation.get("status") == "passed"
        and file_exists(output_image)
        and file_exists(output_metadata)
        and file_exists(output_validation)
        and file_exists(strip_path)
        and diff.get("max_abs_diff") == 0
        and diff.get("mean_abs_diff") == 0.0
    ) else "failed"
    entry = {
        "status": status,
        "frame": frame_id,
        "output_frame": descriptor.get("output_frame"),
        "job_index": job_index,
        "scene_descriptor": file_entry(scene_path, root, "scene descriptor"),
        "command": command,
        "process": {
            "returncode": proc.returncode,
            "elapsed_ms": elapsed_ms,
            "stdout": log_entry(stdout_path, root, "stdout"),
            "stderr": log_entry(stderr_path, root, "stderr"),
        },
        "result_json": log_entry(result_path, root, "backend result"),
        "result_schema": result.get("schema"),
        "result_status": result.get("status"),
        "backend_kind": result.get("backend_kind"),
        "output_image_repo_path": posix_rel(output_image, root) if output_image else None,
        "metadata_repo_path": posix_rel(output_metadata, root) if output_metadata else None,
        "validation_repo_path": posix_rel(output_validation, root) if output_validation else None,
        "strip_repo_path": posix_rel(strip_path, root),
        "mean_abs_diff": diff.get("mean_abs_diff", result.get("mean_abs_diff", 999.0)),
        "max_abs_diff": diff.get("max_abs_diff", result.get("max_abs_diff", 999)),
        "mismatched_coverage": diff.get("mismatched_coverage", result.get("mismatched_coverage")),
        "delta_from_source": result.get("delta_from_source") or (validation.get("delta_from_source") or {}),
        "effective_strength": result.get("effective_strength"),
    }
    if file_exists(output_image):
        entry["output"] = file_entry(output_image, root, "backend output")
        entry["output_sha256"] = entry["output"]["sha256"]
    return entry


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "Tonemap Backend Sample GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Tonemap Backend Sample Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in (summary.get("gallery") or {}).get("metadata_files") or [])
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Passed", checks.get("passed_frames")),
            ("Proc Failures", checks.get("process_failures")),
            ("Max Diff", checks.get("max_abs_diff")),
            ("Mean Diff", f"{checks.get('max_mean_abs_diff', 0.0):.6f}"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="tonemap backend sample gif"></section>' if gif else ""
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
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 26px; font-weight: 650; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
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
  <header><h1>{summary['title']}</h1><nav>{links}</nav></header>
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
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Passed frames: `{checks.get('passed_frames')}`",
        f"- Failed frames: `{checks.get('failed_frames')}`",
        f"- Process failures: `{checks.get('process_failures')}`",
        f"- Max abs diff vs S585 target: `{checks.get('max_abs_diff')}`",
        f"- Max mean diff vs S585 target: `{checks.get('max_mean_abs_diff')}`",
        f"- Max backend delta from source: `{checks.get('max_delta_from_source')}`",
        f"- Output bytes: `{format_bytes(checks.get('output_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Results",
        "",
        "| Job | Frame | Output | Status | Return | Strength | Max Diff | Output | Strip |",
        "| ---: | ---: | ---: | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('output_frame')} | "
            f"`{frame.get('status')}` | {(frame.get('process') or {}).get('returncode')} | "
            f"{frame.get('effective_strength')} | {frame.get('max_abs_diff')} | "
            f"`{frame.get('output_image_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def run(args):
    root = os.getcwd()
    target_path = require_file(resolve_path(args.target_summary, root), "depth/material target summary")
    backend_script = require_file(resolve_path(args.backend_script, root), "scene-depth material backend script")
    target = read_json(target_path)
    if target.get("schema") != "lsfs_mitsuba_renderer_scene_depth_material_target":
        raise SystemExit(f"{args.target_summary}: expected lsfs_mitsuba_renderer_scene_depth_material_target schema")
    if target.get("status") != "ready":
        raise SystemExit(f"{args.target_summary}: target status is {target.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    for sub in ("scenes", "backend_frames", "backend_metadata", "backend_validation", "strips", "results", "logs"):
        ensure_dir(os.path.join(out_dir, sub))

    chosen = selected_frames(target.get("frames") or [], args.frames)
    results = []
    for job_index, target_frame in enumerate(chosen):
        scene_path, descriptor = scene_descriptor(target_frame, job_index, root, out_dir, backend_script)
        results.append(run_frame(backend_script, scene_path, descriptor, root, out_dir, args.frame_timeout))

    passed = [item for item in results if item.get("status") == "passed"]
    failed = [item for item in results if item.get("status") != "passed"]
    output_paths = [resolve_path(item.get("output_image_repo_path"), root) for item in passed]
    strip_paths = [resolve_path(item.get("strip_repo_path"), root) for item in passed]
    gif_path = os.path.join(out_dir, "tonemap_backend_sample.gif")
    strip_gif_path = os.path.join(out_dir, "tonemap_backend_sample_strips.gif")
    if output_paths:
        write_gif(output_paths, gif_path, args.fps)
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(gif_path):
        assets.append(copy_asset(gif_path, assets_dir, "tonemap_backend_sample.gif", "Tonemap Backend Sample GIF", root))
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "tonemap_backend_sample_strips.gif", "Tonemap Backend Sample Strip GIF", root))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["strip_repo_path"], assets_dir, f"tonemap_backend_sample_strip_{out_index:02d}.png", f"Tonemap Backend Sample Strip {out_index + 1}", root))

    checks = {
        "frames": len(results),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "process_failures": sum(1 for item in results if (item.get("process") or {}).get("returncode") != 0),
        "max_abs_diff": max((item.get("max_abs_diff", 999) for item in results), default=999),
        "max_mean_abs_diff": max((item.get("mean_abs_diff", 999.0) for item in results), default=999.0),
        "max_mismatched_coverage": max((item.get("mismatched_coverage", 1.0) for item in results), default=1.0),
        "max_delta_from_source": max(((item.get("delta_from_source") or {}).get("max_abs_delta", 0) for item in results), default=0),
        "output_bytes": sum(os.path.getsize(path) for path in output_paths if path and os.path.isfile(path)),
        "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
        "stdout_bytes": sum((item.get("process") or {}).get("stdout", {}).get("size", 0) for item in results),
        "stderr_bytes": sum((item.get("process") or {}).get("stderr", {}).get("size", 0) for item in results),
    }
    status = "passed" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["process_failures"] == 0
        and checks["max_abs_diff"] == 0
        and checks["max_mean_abs_diff"] == 0.0
    ) else "failed"

    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_asset(target_path, assets_dir, "depth_material_target_summary.json", "Depth Material Target Summary", root),
        copy_asset(backend_script, assets_dir, os.path.basename(backend_script), "Tonemap Backend Script", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_backend_sample",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "backend": {
            "kind": "scene_depth_material_tonemap_backend",
            "script": posix_rel(backend_script, root),
            "mode": "external_backend_executable_sample",
        },
        "inputs": {
            "target_summary": posix_rel(target_path, root),
            "target_schema": target.get("schema"),
            "target_status": target.get("status"),
            "selected_label": (target.get("selected") or {}).get("label"),
        },
        "settings": {
            "frames_requested": args.frames,
            "frames_selected": [item.get("frame") for item in chosen],
            "fps": args.fps,
            "keyframes": args.keyframes,
            "frame_timeout": args.frame_timeout,
        },
        "checks": checks,
        "frames": results,
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
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "tonemap_backend_sample_summary.json", "Tonemap Backend Sample Summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    summary_asset = resolve_path(metadata_files[0]["repo_path"], root)
    write_json(summary_asset, summary)
    write_text(index_path, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_backend_sample_gallery",
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
        f"status={status} frames={checks['frames']} passed={checks['passed_frames']} "
        f"process_failures={checks['process_failures']} max_diff={checks['max_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "passed":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a scene-depth material backend executable sample")
    parser.add_argument("target_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--backend-script", default="tools/mitsuba_scene_depth_material_tonemap_backend.py")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--frame-timeout", type=float, default=60.0)
    parser.add_argument("--title", default="S589 Mitsuba Renderer Scene Depth Material Tonemap Backend Sample")
    parser.add_argument(
        "--next",
        default="Compare this backend executable sample against S587, then extend the same descriptor/backend path to a real material-renderer sample.",
    )
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.frame_timeout <= 0.0:
        parser.error("frame-timeout must be positive")
    run(args)


if __name__ == "__main__":
    main()
