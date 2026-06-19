#!/usr/bin/env python
"""Run a bounded preview benchmark from an external-render bundle."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

from build_bridge_review_package import format_bytes, posix_rel, read_json, require_file, write_json, write_text


def run_step(name, cmd, cwd):
    start = time.perf_counter()
    completed = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def require_ok(step):
    if step["returncode"] != 0:
        sys.stderr.write(step["stdout"])
        sys.stderr.write(step["stderr"])
        raise SystemExit(f"{step['name']} failed with exit code {step['returncode']}")


def preflight_status(path):
    if not path:
        return {"enabled": False}
    resolved = require_file(path, "preflight gate")
    gate = read_json(resolved)
    return {
        "enabled": True,
        "path": resolved,
        "repo_path": posix_rel(resolved, os.getcwd()),
        "schema": gate.get("schema"),
        "status": gate.get("status"),
        "check_count": gate.get("check_count"),
        "failed_count": gate.get("failed_count"),
    }


def build_summary(args, steps, root):
    preview_summary_path = os.path.abspath(os.path.join(args.out_dir, "preview", "render_summary.json"))
    gallery_manifest_path = os.path.abspath(os.path.join(args.out_dir, "gallery", "gallery_manifest.json"))
    gif_path = os.path.abspath(os.path.join(args.out_dir, "preview.gif"))
    preview_summary = read_json(preview_summary_path)
    gallery_manifest = read_json(gallery_manifest_path)
    gif_size = os.path.getsize(gif_path)
    step_summaries = [
        {
            "name": step["name"],
            "returncode": step["returncode"],
            "elapsed_ms": step["elapsed_ms"],
        }
        for step in steps
    ]
    return {
        "schema": "lsfs_external_bundle_preview_benchmark",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed",
        "preflight": preflight_status(args.preflight_gate),
        "bundle": {
            "path": os.path.abspath(args.bundle),
            "repo_path": posix_rel(os.path.abspath(args.bundle), root),
        },
        "config": {
            "frames": args.frames,
            "width": args.width,
            "height": args.height,
            "min_occupancy": args.min_occupancy,
            "secondary_channel": args.secondary_channel,
        },
        "preview": {
            "summary": preview_summary_path,
            "summary_repo_path": posix_rel(preview_summary_path, root),
            "frame_count": preview_summary.get("frame_count"),
            "width": preview_summary.get("width"),
            "height": preview_summary.get("height"),
            "min_occupancy": preview_summary.get("min_occupancy"),
            "secondary_channel": preview_summary.get("secondary_channel"),
        },
        "gif": {
            "path": gif_path,
            "repo_path": posix_rel(gif_path, root),
            "size": gif_size,
        },
        "gallery": {
            "manifest": gallery_manifest_path,
            "manifest_repo_path": posix_rel(gallery_manifest_path, root),
            "index": gallery_manifest.get("index"),
            "index_repo_path": gallery_manifest.get("index_repo_path"),
            "asset_count": len(gallery_manifest.get("assets", [])),
            "metadata_count": len(gallery_manifest.get("metadata_files", [])),
        },
        "steps": step_summaries,
        "total_elapsed_ms": sum(step["elapsed_ms"] for step in steps),
    }


def markdown_report(summary, report_path, root, next_text):
    lines = [
        "# S280 External Bundle Preview Benchmark",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary['summary_path'], root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Config",
        "",
        f"- Frames: `{summary['config']['frames']}`",
        f"- Resolution: `{summary['config']['width']} x {summary['config']['height']}`",
        f"- Secondary channel: `{summary['config']['secondary_channel']}`",
        f"- Min occupancy gate: `{summary['config']['min_occupancy']}`",
        "",
        "## Result",
        "",
        f"- Preview min occupancy: `{summary['preview']['min_occupancy']}`",
        f"- GIF: `{summary['gif']['repo_path']}` ({format_bytes(summary['gif']['size'])})",
        f"- Gallery: `{summary['gallery']['index_repo_path']}`",
        f"- Gallery assets: `{summary['gallery']['asset_count']}`",
        f"- Total elapsed: `{summary['total_elapsed_ms'] / 1000.0:.2f}s`",
        "",
        "## Steps",
        "",
        "| Step | Return | Elapsed |",
        "| --- | ---: | ---: |",
    ]
    for step in summary.get("steps", []):
        lines.append(f"| {step['name']} | {step['returncode']} | {step['elapsed_ms'] / 1000.0:.2f}s |")
    lines.extend([
        "",
        "## Next",
        "",
        next_text,
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run external bundle preview benchmark")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--preflight-gate")
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--min-occupancy", type=float, default=0.01)
    parser.add_argument("--secondary-channel", default="all", choices=("all", "droplet", "spray", "foam", "bubble"))
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("--keyframes", type=int, default=8)
    parser.add_argument("--summary")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this benchmark before scaling the external bundle preview path further.")
    args = parser.parse_args(argv)

    root = os.getcwd()
    if args.preflight_gate:
        preflight = preflight_status(args.preflight_gate)
        if preflight.get("status") != "passed":
            raise SystemExit(f"preflight gate is not passed: {preflight}")
    bundle = require_file(args.bundle, "external bundle")
    out_dir = os.path.abspath(args.out_dir)
    preview_dir = os.path.join(out_dir, "preview")
    gif_path = os.path.join(out_dir, "preview.gif")
    gallery_dir = os.path.join(out_dir, "gallery")
    os.makedirs(out_dir, exist_ok=True)

    steps = []
    commands = [
        (
            "render_preview",
            [
                sys.executable,
                "tools/cinematic_render_stub.py",
                bundle,
                preview_dir,
                "--frames",
                str(args.frames),
                "--width",
                str(args.width),
                "--height",
                str(args.height),
                "--min-occupancy",
                str(args.min_occupancy),
                "--secondary-channel",
                args.secondary_channel,
            ],
        ),
        (
            "assemble_gif",
            [
                sys.executable,
                "tools/assemble_frames.py",
                preview_dir,
                gif_path,
                "--fps",
                str(args.fps),
            ],
        ),
        (
            "build_gallery",
            [
                sys.executable,
                "tools/build_preview_gallery.py",
                "--render-summary",
                os.path.join(preview_dir, "render_summary.json"),
                "--gif",
                gif_path,
                "--preview-dir",
                preview_dir,
                "--out",
                gallery_dir,
                "--title",
                "S280 External Bundle Preview Benchmark",
                "--keyframes",
                str(args.keyframes),
                "--next",
                args.next,
            ],
        ),
    ]
    for name, cmd in commands:
        step = run_step(name, cmd, root)
        steps.append(step)
        require_ok(step)

    summary = build_summary(args, steps, root)
    summary_path = os.path.abspath(args.summary or os.path.join(out_dir, "benchmark_summary.json"))
    summary["summary_path"] = summary_path
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, args.report, root, args.next))
    print(f"status={summary['status']} frames={summary['preview']['frame_count']} min_occupancy={summary['preview']['min_occupancy']}")
    print(f"summary={summary_path}")
    if args.report:
        print(f"report={os.path.abspath(args.report)}")


if __name__ == "__main__":
    main()
