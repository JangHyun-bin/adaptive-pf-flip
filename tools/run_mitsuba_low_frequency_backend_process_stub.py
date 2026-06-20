#!/usr/bin/env python
"""Run low-frequency backend scene descriptors through an external process stub."""

import argparse
import os
import re
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
from run_mitsuba_low_frequency_backend_adapter_dry_run import copy_asset, resolve_path


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


def image_entry(path, root):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
        "dimensions": image_dimensions(path),
    }
    return entry


def slugify(value):
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "backend_process"


def summary_metadata_entry(summary_path, assets_dir, root, label, slug):
    dest = os.path.join(assets_dir, f"{slug}_summary.json")
    return {
        "label": f"{label} Summary",
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{slug}_summary.json",
        "source_repo_path": posix_rel(summary_path, root),
    }


def file_exists(path):
    return bool(path and os.path.isfile(path))


def command_for_frame(args, root, scene_path, result_path, strip_path):
    script_path = resolve_path(args.backend_script, root)
    return [
        sys.executable,
        script_path,
        "--scene",
        scene_path,
        "--result",
        result_path,
        "--strip",
        strip_path,
        "--fail-on-review",
    ]


def run_frame(args, frame, root, out_dir):
    job_index = int(frame.get("job_index") or 0)
    frame_id = frame.get("frame")
    scene_path = require_file(resolve_path((frame.get("scene_descriptor") or {}).get("repo_path"), root), "backend scene descriptor")
    scene = read_json(scene_path)
    strip_path = os.path.abspath(os.path.join(out_dir, "strips", f"frame_{job_index:04d}_{args.backend_slug}.png"))
    result_path = os.path.abspath(os.path.join(out_dir, "results", f"frame_{job_index:04d}_backend_process_result.json"))
    stdout_path = os.path.abspath(os.path.join(out_dir, "logs", f"frame_{job_index:04d}_stdout.log"))
    stderr_path = os.path.abspath(os.path.join(out_dir, "logs", f"frame_{job_index:04d}_stderr.log"))
    for path in (strip_path, result_path, stdout_path, stderr_path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    command = command_for_frame(args, root, scene_path, result_path, strip_path)
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        timeout=args.frame_timeout,
        check=False,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    write_text(stdout_path, proc.stdout or "")
    write_text(stderr_path, proc.stderr or "")
    result = read_json(result_path) if os.path.isfile(result_path) else {}
    output_image = resolve_path((scene.get("outputs") or {}).get("image", {}).get("repo_path"), root)
    output_metadata = resolve_path((scene.get("outputs") or {}).get("metadata", {}).get("repo_path"), root)
    output_validation = resolve_path((scene.get("outputs") or {}).get("validation", {}).get("repo_path"), root)
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
        "output_frame": frame.get("output_frame"),
        "job_index": job_index,
        "scene_repo_path": posix_rel(scene_path, root),
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
        "reference_sha256": result.get("reference_sha256"),
        "expected_reference_sha256": result.get("expected_reference_sha256"),
    }
    if file_exists(output_image):
        entry["output"] = image_entry(output_image, root)
        entry["output_sha256"] = entry["output"]["sha256"]
    return entry


def html_page(title, summary, assets, metadata_files):
    label = (summary.get("settings") or {}).get("backend_label") or "Backend Process Stub"
    shot = next((item for item in assets if item.get("label") == f"{label} GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith(f"{label} Strip")]
    checks = summary.get("checks") or {}
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Passed", checks.get("passed_frames")),
        ("Proc Failures", checks.get("process_failures")),
        ("Max Diff", checks.get("max_abs_diff")),
        ("Mean Diff", checks.get("max_mean_abs_diff")),
    ]
    metrics = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in tiles)
    hero = f'<section class="hero"><img src="{shot["href"]}" alt="{label} GIF"></section>' if shot else ""
    frame_html = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #070c10; --panel: #101820; --line: #2b3942; --ink: #edf7fb; --muted: #9cadb7; --accent: #8bdcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 42px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111; margin-bottom: 14px; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{metrics}</section>
    <section class="grid">{frame_html}</section>
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
        f"- Max abs diff: `{checks.get('max_abs_diff')}`",
        f"- Max mean abs diff: `{checks.get('max_mean_abs_diff')}`",
        f"- Output bytes: `{format_bytes(checks.get('output_bytes', 0))}`",
        f"- Stdout bytes: `{checks.get('stdout_bytes')}`",
        f"- Stderr bytes: `{checks.get('stderr_bytes')}`",
        "",
        "## Frame Results",
        "",
        "| Job | Frame | Output | Status | Return | Max Diff | Scene | Output |",
        "| ---: | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('output_frame')} | `{frame.get('status')}` | "
            f"{(frame.get('process') or {}).get('returncode')} | {frame.get('max_abs_diff')} | "
            f"`{frame.get('scene_repo_path')}` | `{frame.get('output_image_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Swap the executable stub for a real renderer backend while preserving this process contract.", ""])
    return "\n".join(lines)


def run_process_stub(args):
    root = os.getcwd()
    manifest_path = require_file(resolve_path(args.adapter_manifest, root), "backend adapter manifest")
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "lsfs_mitsuba_low_frequency_backend_adapter_manifest":
        raise SystemExit(f"{args.adapter_manifest}: expected lsfs_mitsuba_low_frequency_backend_adapter_manifest schema")
    if manifest.get("status") != "ready":
        raise SystemExit(f"{args.adapter_manifest}: adapter status is {manifest.get('status')!r}")
    backend_script = require_file(resolve_path(args.backend_script, root), "backend script")
    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    ensure_dir(os.path.join(out_dir, "strips"))
    ensure_dir(os.path.join(out_dir, "logs"))
    ensure_dir(os.path.join(out_dir, "results"))
    args.backend_script = backend_script
    results = [run_frame(args, frame, root, out_dir) for frame in manifest.get("frames") or []]
    passed = [item for item in results if item.get("status") == "passed"]
    failed = [item for item in results if item.get("status") != "passed"]
    output_paths = [resolve_path(item.get("output_image_repo_path"), root) for item in passed]
    strip_paths = [resolve_path(item.get("strip_repo_path"), root) for item in passed]
    gif_path = os.path.join(assets_dir, "shot.gif")
    label = args.backend_label
    slug = args.backend_slug
    strip_gif_path = os.path.join(assets_dir, f"{slug}_strips.gif")
    if output_paths:
        write_gif(output_paths, gif_path, args.fps)
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(gif_path):
        assets.append(copy_asset(gif_path, assets_dir, "shot.gif", f"{label} GIF", root))
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, f"{slug}_strips.gif", f"{label} Strip GIF", root))
    keyframes = max(1, min(args.keyframes, len(passed)))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["output_image_repo_path"], assets_dir, f"keyframe_{out_index:02d}.png", f"{label} Keyframe {out_index + 1}", root))
        assets.append(copy_asset(passed[frame_index]["strip_repo_path"], assets_dir, f"{slug}_strip_{out_index:02d}.png", f"{label} Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    checks = {
        "frames": len(results),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "process_failures": sum(1 for item in results if (item.get("process") or {}).get("returncode") != 0),
        "max_abs_diff": max((item.get("max_abs_diff", 999) for item in results), default=999),
        "max_mean_abs_diff": max((item.get("mean_abs_diff", 999.0) for item in results), default=999.0),
        "output_bytes": sum(os.path.getsize(path) for path in output_paths if path and os.path.isfile(path)),
        "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
        "stdout_bytes": sum((item.get("process") or {}).get("stdout", {}).get("size", 0) for item in results),
        "stderr_bytes": sum((item.get("process") or {}).get("stderr", {}).get("size", 0) for item in results),
        "result_json_bytes": sum((item.get("result_json") or {}).get("size", 0) for item in results),
    }
    status = "passed" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["process_failures"] == 0
        and checks["max_abs_diff"] == 0
        and checks["max_mean_abs_diff"] == 0.0
    ) else "failed"
    summary = {
        "schema": args.summary_schema,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source_adapter": {
            "repo_path": posix_rel(manifest_path, root),
            "schema": manifest.get("schema"),
            "status": manifest.get("status"),
            "sha256": sha256_file(manifest_path),
            "size": os.path.getsize(manifest_path),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
            "frame_timeout": args.frame_timeout,
            "backend_script": posix_rel(backend_script, root),
            "backend_label": label,
            "backend_slug": slug,
            "backend_result_schemas": sorted(set(item.get("result_schema") for item in results if item.get("result_schema"))),
            "backend_kinds": sorted(set(item.get("backend_kind") for item in results if item.get("backend_kind"))),
            "stage": "renderer_post_tonemap_low_frequency_runtime_consumer",
        },
        "checks": checks,
        "frames": results,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        summary_metadata_entry(summary_path, assets_dir, root, label, slug),
        copy_asset(manifest_path, assets_dir, "backend_adapter_manifest.json", "Backend Adapter Manifest", root),
        copy_asset(backend_script, assets_dir, os.path.basename(backend_script), f"{label} Script", root),
    ]
    index_path = os.path.join(gallery_dir, "index.html")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    summary_asset = resolve_path(metadata_files[0]["repo_path"], root)
    write_json(summary_asset, summary)
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": args.gallery_schema or f"{args.summary_schema}_gallery",
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
        f"process_failures={checks['process_failures']} max_diff={checks['max_abs_diff']} summary={summary_path}"
    )
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run backend scene descriptors through an external process stub")
    parser.add_argument("adapter_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--backend-script", default="tools/mitsuba_low_frequency_backend_stub.py")
    parser.add_argument("--backend-label", default="Backend Process Stub")
    parser.add_argument("--summary-schema", default="lsfs_mitsuba_low_frequency_backend_process_stub")
    parser.add_argument("--gallery-schema")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--frame-timeout", type=float, default=60.0)
    parser.add_argument("--title", default="S505 Mitsuba Low Frequency Backend Process Stub")
    parser.add_argument("--next", default="Swap the executable stub for a real renderer backend while preserving this process contract.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.frame_timeout <= 0.0:
        parser.error("frame-timeout must be positive")
    args.backend_slug = slugify(args.backend_label)
    run_process_stub(args)


if __name__ == "__main__":
    main()
