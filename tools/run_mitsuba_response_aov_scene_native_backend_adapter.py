#!/usr/bin/env python
"""Run BOLD_SAFE native backend promotion smoke through subprocesses."""

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
from build_mitsuba_low_frequency_parity_texture_package import write_gif
from run_mitsuba_response_aov_scene_native_probe_sweep import metric_bounds, resolve_path
from run_mitsuba_response_aov_scene_job_dry_run import copy_asset


JOB_SCHEMA = "lsfs_mitsuba_response_aov_scene_job_manifest"
SWEEP_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_probe_sweep"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_backend_adapter"


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


def image_entry(path, root, label=None):
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


def file_exists(path):
    return bool(path and os.path.isfile(path))


def load_inputs(job_path_arg, sweep_path_arg, root):
    job_path = require_file(resolve_path(job_path_arg, root), "response-AOV scene job manifest")
    sweep_path = require_file(resolve_path(sweep_path_arg, root), "native probe sweep summary")
    job = read_json(job_path)
    sweep = read_json(sweep_path)
    if job.get("schema") != JOB_SCHEMA:
        raise SystemExit(f"{job_path_arg}: expected {JOB_SCHEMA} schema")
    if job.get("status") != "ready":
        raise SystemExit(f"{job_path_arg}: job status is {job.get('status')!r}")
    if sweep.get("schema") != SWEEP_SCHEMA:
        raise SystemExit(f"{sweep_path_arg}: expected {SWEEP_SCHEMA} schema")
    if sweep.get("status") != "ready":
        raise SystemExit(f"{sweep_path_arg}: sweep status is {sweep.get('status')!r}")
    selected = sweep.get("selected_candidate") or {}
    if selected.get("label") != "BOLD_SAFE":
        raise SystemExit(f"{sweep_path_arg}: expected selected BOLD_SAFE, got {selected.get('label')!r}")
    return job_path, job, sweep_path, sweep, selected


def descriptor_path(frame_job, root):
    ref = frame_job.get("descriptor") or {}
    return require_file(resolve_path(ref.get("repo_path") or ref.get("path"), root), "response-AOV scene descriptor")


def target_by_frame(selected):
    return {int(frame.get("frame") or 0): frame for frame in selected.get("frames") or []}


def bounds_from_descriptors(frame_jobs, root):
    y_values = []
    z_values = []
    secondary_values = []
    for frame_job in frame_jobs:
        descriptor = read_json(descriptor_path(frame_job, root))
        render_data = descriptor.get("render_data") or {}
        y_values.append(render_data.get("water_depth_y_span"))
        z_values.append(render_data.get("water_depth_z_span"))
        secondary_values.append(((render_data.get("secondary_counts") or {}).get("total") or 0))
    return {
        "water_y_bounds": metric_bounds(y_values),
        "water_z_bounds": metric_bounds(z_values),
        "secondary_bounds": metric_bounds(secondary_values),
    }


def bounds_text(bounds):
    return f"{bounds[0]},{bounds[1]}"


def run_frame(frame_job, target_frame, root, out_dir, backend_script, bounds, frame_timeout):
    job_index = int(frame_job.get("job_index") or 0)
    frame_id = int(frame_job.get("frame") or job_index)
    scene_path = descriptor_path(frame_job, root)
    target_path = require_file(resolve_path(target_frame.get("preview_repo_path"), root), "S626 native probe target")
    name = f"frame_{job_index:04d}"
    output_path = os.path.abspath(os.path.join(out_dir, "backend_frames", f"{name}.png"))
    metadata_path = os.path.abspath(os.path.join(out_dir, "backend_metadata", f"{name}_metadata.json"))
    validation_path = os.path.abspath(os.path.join(out_dir, "backend_validation", f"{name}_validation.json"))
    result_path = os.path.abspath(os.path.join(out_dir, "results", f"{name}_native_backend_result.json"))
    strip_path = os.path.abspath(os.path.join(out_dir, "strips", f"{name}_native_backend.png"))
    stdout_path = os.path.abspath(os.path.join(out_dir, "logs", f"{name}_stdout.log"))
    stderr_path = os.path.abspath(os.path.join(out_dir, "logs", f"{name}_stderr.log"))
    for path in (output_path, metadata_path, validation_path, result_path, strip_path, stdout_path, stderr_path):
        ensure_dir(os.path.dirname(path))
    command = [
        sys.executable,
        backend_script,
        "--scene", scene_path,
        "--target", target_path,
        "--output", output_path,
        "--metadata", metadata_path,
        "--validation", validation_path,
        "--result", result_path,
        "--strip", strip_path,
        "--water-y-bounds", bounds_text(bounds["water_y_bounds"]),
        "--water-z-bounds", bounds_text(bounds["water_z_bounds"]),
        "--secondary-bounds", bounds_text(bounds["secondary_bounds"]),
        "--fail-on-review",
    ]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=frame_timeout, check=False)
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    write_text(stdout_path, proc.stdout or "")
    write_text(stderr_path, proc.stderr or "")
    result = read_json(result_path) if file_exists(result_path) else {}
    validation = read_json(validation_path) if file_exists(validation_path) else {}
    diff = validation.get("diff_vs_s626") or {}
    delta = validation.get("delta_from_s623") or result.get("delta_from_s623") or {}
    status = "passed" if (
        proc.returncode == 0
        and result.get("status") == "passed"
        and validation.get("status") == "passed"
        and file_exists(output_path)
        and file_exists(metadata_path)
        and file_exists(validation_path)
        and file_exists(strip_path)
        and diff.get("max_abs_diff") == 0
        and diff.get("mean_abs_diff") == 0.0
    ) else "failed"
    entry = {
        "status": status,
        "frame": frame_id,
        "output_frame": frame_job.get("output_frame"),
        "scene_frame": frame_job.get("scene_frame"),
        "source_frame": frame_job.get("source_frame"),
        "job_index": job_index,
        "command": command,
        "scene_descriptor": {
            "repo_path": posix_rel(scene_path, root),
            "sha256": sha256_file(scene_path),
            "size": os.path.getsize(scene_path),
        },
        "target_repo_path": posix_rel(target_path, root),
        "process": {
            "returncode": proc.returncode,
            "elapsed_ms": elapsed_ms,
            "stdout": log_entry(stdout_path, root, "stdout"),
            "stderr": log_entry(stderr_path, root, "stderr"),
        },
        "result_json": log_entry(result_path, root, "backend result"),
        "result_status": result.get("status"),
        "result_schema": result.get("schema"),
        "backend_kind": result.get("backend_kind"),
        "output_image_repo_path": posix_rel(output_path, root),
        "metadata_repo_path": posix_rel(metadata_path, root),
        "validation_repo_path": posix_rel(validation_path, root),
        "strip_repo_path": posix_rel(strip_path, root),
        "mean_abs_diff": diff.get("mean_abs_diff", result.get("mean_abs_diff", 999.0)),
        "max_abs_diff": diff.get("max_abs_diff", result.get("max_abs_diff", 999)),
        "mismatched_coverage": diff.get("mismatched_coverage", result.get("mismatched_coverage")),
        "delta_from_s623": delta,
    }
    if file_exists(output_path):
        entry["output"] = image_entry(output_path, root, "native backend output")
        entry["output_sha256"] = entry["output"]["sha256"]
    return entry


def html_page(summary, assets, metadata_files):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item.get("label") == "Native Backend GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Native Backend Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Passed", checks.get("passed_frames")),
            ("Proc Failures", checks.get("process_failures")),
            ("Max Diff", checks.get("max_abs_diff_vs_s626")),
            ("Max S623 Delta", checks.get("max_abs_delta_from_s623")),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="native backend GIF"></section>' if gif else ""
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
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 27px; font-weight: 670; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; min-height: 58px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    strong {{ display: block; font-size: 15px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; margin: 0 0 12px; }}
    .hero img, figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <header><h1>{summary['title']}</h1><nav>{links}</nav></header>
  {hero}
  <section class="tiles">{tiles}</section>
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
        f"- Max abs diff vs S626: `{checks.get('max_abs_diff_vs_s626')}`",
        f"- Max mean abs diff vs S626: `{checks.get('max_mean_abs_diff_vs_s626')}`",
        f"- Max abs delta from S623: `{checks.get('max_abs_delta_from_s623')}`",
        f"- Max mean abs delta from S623: `{checks.get('max_mean_abs_delta_from_s623')}`",
        f"- Output bytes: `{format_bytes(checks.get('output_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Job | Frame | Scene | Source | Status | Return | Max Diff | S623 Delta | Output |",
        "| ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        delta = frame.get("delta_from_s623") or {}
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('scene_frame')} | "
            f"{frame.get('source_frame')} | `{frame.get('status')}` | "
            f"{(frame.get('process') or {}).get('returncode')} | {frame.get('max_abs_diff')} | "
            f"{delta.get('max_abs_delta')} | `{frame.get('output_image_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    root = os.getcwd()
    backend_script = require_file(resolve_path(args.backend_script, root), "native backend script")
    job_path, job, sweep_path, sweep, selected = load_inputs(args.job_manifest, args.sweep_summary, root)
    targets = target_by_frame(selected)
    bounds = bounds_from_descriptors(job.get("frames") or [], root)
    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    for subdir in ("backend_frames", "backend_metadata", "backend_validation", "results", "strips", "logs"):
        ensure_dir(os.path.join(out_dir, subdir))
    results = []
    for frame_job in job.get("frames") or []:
        frame_id = int(frame_job.get("frame") or 0)
        if frame_id not in targets:
            raise SystemExit(f"S626 target is missing frame {frame_id}")
        results.append(run_frame(frame_job, targets[frame_id], root, out_dir, backend_script, bounds, args.frame_timeout))
    passed = [item for item in results if item.get("status") == "passed"]
    failed = [item for item in results if item.get("status") != "passed"]
    output_paths = [resolve_path(item.get("output_image_repo_path"), root) for item in passed]
    strip_paths = [resolve_path(item.get("strip_repo_path"), root) for item in passed]
    gif_path = os.path.join(assets_dir, "native_backend.gif")
    strip_gif_path = os.path.join(assets_dir, "native_backend_strips.gif")
    if output_paths:
        write_gif(output_paths, gif_path, args.fps)
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)
    assets = []
    if os.path.isfile(gif_path):
        assets.append(copy_asset(gif_path, assets_dir, "native_backend.gif", "Native Backend GIF", root))
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "native_backend_strips.gif", "Native Backend Strip GIF", root))
    keyframes = max(1, min(args.keyframes, len(passed)))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["strip_repo_path"], assets_dir, f"native_backend_strip_{out_index:02d}.png", f"Native Backend Strip {out_index + 1}", root))
    stdout_bytes = sum((item.get("process") or {}).get("stdout", {}).get("size", 0) for item in results)
    stderr_bytes = sum((item.get("process") or {}).get("stderr", {}).get("size", 0) for item in results)
    checks = {
        "frames": len(results),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "process_failures": sum(1 for item in results if (item.get("process") or {}).get("returncode") != 0),
        "max_abs_diff_vs_s626": max((item.get("max_abs_diff", 999) for item in results), default=999),
        "max_mean_abs_diff_vs_s626": max((item.get("mean_abs_diff", 999.0) for item in results), default=999.0),
        "max_abs_delta_from_s623": max(((item.get("delta_from_s623") or {}).get("max_abs_delta", 999) for item in results), default=999),
        "max_mean_abs_delta_from_s623": max(((item.get("delta_from_s623") or {}).get("mean_abs_delta", 999.0) for item in results), default=999.0),
        "output_bytes": sum(os.path.getsize(path) for path in output_paths if path and os.path.isfile(path)),
        "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
    }
    status = "passed" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["process_failures"] == 0
        and checks["max_abs_diff_vs_s626"] == 0
        and checks["max_mean_abs_diff_vs_s626"] == 0.0
    ) else "failed"
    summary_path = os.path.abspath(args.summary) if args.summary else os.path.join(out_dir, "response_aov_scene_native_backend_adapter_summary.json")
    metadata_files = [
        {
            "label": "Native Backend Adapter Summary",
            "repo_path": posix_rel(os.path.join(assets_dir, "response_aov_scene_native_backend_adapter_summary.json"), root),
            "href": "assets/response_aov_scene_native_backend_adapter_summary.json",
            "source_repo_path": posix_rel(summary_path, root),
        },
        copy_asset(job_path, assets_dir, "response_aov_scene_job_manifest.json", "Response AOV Scene Job Manifest", root),
        copy_asset(sweep_path, assets_dir, "response_aov_scene_native_probe_sweep_summary.json", "Native Probe Sweep Summary", root),
    ]
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source_job": {
            "repo_path": posix_rel(job_path, root),
            "schema": job.get("schema"),
            "status": job.get("status"),
            "sha256": sha256_file(job_path),
            "size": os.path.getsize(job_path),
        },
        "source_sweep": {
            "repo_path": posix_rel(sweep_path, root),
            "schema": sweep.get("schema"),
            "status": sweep.get("status"),
            "selected_label": selected.get("label"),
            "sha256": sha256_file(sweep_path),
            "size": os.path.getsize(sweep_path),
        },
        "backend": {
            "repo_path": posix_rel(backend_script, root),
            "sha256": sha256_file(backend_script),
            "size": os.path.getsize(backend_script),
        },
        "normalization": {key: list(value) for key, value in bounds.items()},
        "settings": {
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
    ensure_dir(os.path.dirname(resolve_path(metadata_files[0]["repo_path"], root)))
    with open(summary_path, "rb") as src, open(resolve_path(metadata_files[0]["repo_path"], root), "wb") as dst:
        dst.write(src.read())
    write_text(index_path, html_page(summary, assets, metadata_files))
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        "status={status} frames={frames} passed={passed} max_diff={max_diff} max_delta={max_delta} summary={summary}".format(
            status=status,
            frames=checks["frames"],
            passed=checks["passed_frames"],
            max_diff=checks["max_abs_diff_vs_s626"],
            max_delta=checks["max_abs_delta_from_s623"],
            summary=summary_path,
        )
    )
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_manifest", help="S621 response-AOV scene job manifest")
    parser.add_argument("sweep_summary", help="S626 native-probe sweep summary")
    parser.add_argument("out_dir", help="Output directory for S629")
    parser.add_argument("--backend-script", default="tools/mitsuba_response_aov_scene_native_backend.py")
    parser.add_argument("--summary", help="Output summary JSON")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--frame-timeout", type=float, default=30.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Native Backend Adapter")
    parser.add_argument(
        "--next",
        default="Compare the promoted native backend output against S577/S585 before treating it as a visual gate candidate.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()
    if args.frame_timeout <= 0.0:
        parser.error("frame-timeout must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
