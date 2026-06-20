#!/usr/bin/env python
"""Run a Mitsuba XML export through a real backend command adapter."""

import argparse
import os
import subprocess
import sys
import time
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


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


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


def file_entry(path, root, label):
    resolved = require_file(path, label)
    return {
        "label": label,
        "repo_path": posix_rel(resolved, root),
        "size": os.path.getsize(resolved),
        "sha256": sha256_file(resolved),
    }


def run_command(command, root, stdout_path, stderr_path, timeout):
    start = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        result = exc
        timed_out = True
    elapsed_ms = round((time.perf_counter() - start) * 1000.0, 3)
    write_text(stdout_path, result.stdout or "")
    write_text(stderr_path, result.stderr or "")
    return {
        "command": command,
        "returncode": None if timed_out else result.returncode,
        "timed_out": timed_out,
        "elapsed_ms": elapsed_ms,
        "stdout": log_entry(stdout_path, root, "stdout"),
        "stderr": log_entry(stderr_path, root, "stderr"),
    }


def selected_python(args, root):
    if args.python:
        return require_file(resolve_path(args.python, root), "renderer python")
    return sys.executable


def render_command(args, root, python_path, export_path, render_dir, render_manifest, render_report):
    command = [
        python_path,
        require_file(resolve_path(args.render_script, root), "render script"),
        export_path,
        render_dir,
        "--frames",
        str(args.frames),
        "--spp",
        str(args.spp),
        "--variant",
        args.variant,
        "--output-format",
        args.output_format,
        "--manifest-name",
        os.path.basename(render_manifest),
        "--report",
        render_report,
        "--title",
        args.render_title,
        "--next",
        args.render_next,
    ]
    if args.write_png:
        command.append("--write-png")
    if args.llvm_dll:
        command.extend(["--llvm-dll", require_file(resolve_path(args.llvm_dll, root), "LLVM DLL")])
    if args.llvm_dir:
        command.extend(["--llvm-dir", resolve_path(args.llvm_dir, root)])
    if args.no_hard_exit_on_success:
        command.append("--no-hard-exit-on-success")
    return command


def gallery_command(args, root, render_manifest, gallery_dir, gallery_report):
    return [
        sys.executable,
        require_file(resolve_path(args.gallery_script, root), "gallery script"),
        render_manifest,
        "--out",
        gallery_dir,
        "--title",
        args.gallery_title,
        "--keyframes",
        str(args.keyframes),
        "--fps",
        str(args.fps),
        "--report",
        gallery_report,
        "--next",
        args.gallery_next,
    ]


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    render = summary.get("render_manifest") or {}
    gallery = summary.get("gallery_manifest") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Mitsuba export: `{summary['source_export']['repo_path']}`",
        f"- Renderer Python: `{summary['runtime']['python']}`",
        f"- LLVM DLL: `{summary['runtime'].get('llvm_dll') or 'n/a'}`",
        "",
        "## Checks",
        "",
        f"- Frames requested: `{checks.get('frames_requested')}`",
        f"- Frames rendered: `{checks.get('frames_rendered')}`",
        f"- Render failures: `{checks.get('render_failures')}`",
        f"- Process failures: `{checks.get('process_failures')}`",
        f"- Image bytes: `{format_bytes(checks.get('image_bytes', 0))}`",
        f"- Preview bytes: `{format_bytes(checks.get('preview_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Outputs",
        "",
        f"- Render manifest: `{render.get('repo_path')}`",
        f"- Gallery manifest: `{gallery.get('repo_path')}`",
        f"- Gallery index: `{summary.get('gallery_index_repo_path')}`",
        "",
        "## Processes",
        "",
        f"- Render return code: `{summary['processes']['render']['returncode']}`",
        f"- Render elapsed ms: `{summary['processes']['render']['elapsed_ms']}`",
        f"- Gallery return code: `{summary['processes']['gallery']['returncode']}`",
        f"- Gallery elapsed ms: `{summary['processes']['gallery']['elapsed_ms']}`",
        "",
        "## Next",
        "",
        summary.get("next") or "Publish this real Mitsuba command adapter gallery for external review.",
        "",
    ]
    return "\n".join(lines)


def build_summary(args):
    root = os.getcwd()
    export_path = require_file(resolve_path(args.export, root), "Mitsuba export")
    export = read_json(export_path)
    if export.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.export}: expected lsfs_mitsuba_xml_export schema")
    if export.get("status") != "ready":
        raise SystemExit(f"{args.export}: export status is {export.get('status')!r}")
    if args.llvm_dll and args.llvm_dir:
        raise SystemExit("pass only one of --llvm-dll or --llvm-dir")

    out_dir = os.path.abspath(args.out_dir)
    render_dir = ensure_dir(os.path.join(out_dir, "render"))
    gallery_dir = ensure_dir(os.path.join(out_dir, "gallery"))
    log_dir = ensure_dir(os.path.join(out_dir, "logs"))
    render_manifest = os.path.join(render_dir, "mitsuba_render.json")
    render_report = os.path.join(out_dir, "mitsuba_render_report.md")
    gallery_report = os.path.join(out_dir, "mitsuba_render_gallery_report.md")
    python_path = selected_python(args, root)

    render_proc = run_command(
        render_command(args, root, python_path, export_path, render_dir, render_manifest, render_report),
        root,
        os.path.join(log_dir, "render_stdout.log"),
        os.path.join(log_dir, "render_stderr.log"),
        args.timeout,
    )
    render = read_json(render_manifest) if os.path.isfile(render_manifest) else {}
    gallery_proc = {
        "command": [],
        "returncode": None,
        "timed_out": False,
        "elapsed_ms": 0.0,
        "stdout": log_entry(os.path.join(log_dir, "gallery_stdout.log"), root, "stdout"),
        "stderr": log_entry(os.path.join(log_dir, "gallery_stderr.log"), root, "stderr"),
    }
    if render.get("status") == "ready":
        gallery_proc = run_command(
            gallery_command(args, root, render_manifest, gallery_dir, gallery_report),
            root,
            os.path.join(log_dir, "gallery_stdout.log"),
            os.path.join(log_dir, "gallery_stderr.log"),
            args.timeout,
        )
    gallery_manifest = os.path.join(gallery_dir, "gallery_manifest.json")
    gallery = read_json(gallery_manifest) if os.path.isfile(gallery_manifest) else {}
    render_checks = render.get("checks") or {}
    process_failures = sum(
        1
        for proc in (render_proc, gallery_proc)
        if proc.get("timed_out") or proc.get("returncode") not in (0, None)
    )
    gif_asset = next((item for item in gallery.get("assets") or [] if item.get("label") == "Shot GIF"), {})
    checks = {
        "frames_requested": render_checks.get("frames_requested", args.frames),
        "frames_rendered": render_checks.get("frames_rendered", 0),
        "render_failures": render_checks.get("failures", 999),
        "process_failures": process_failures,
        "image_bytes": render_checks.get("image_bytes", 0),
        "preview_bytes": render_checks.get("preview_bytes", 0),
        "gallery_assets": len(gallery.get("assets") or []),
        "gallery_metadata_files": len(gallery.get("metadata_files") or []),
        "gif_bytes": gif_asset.get("size", 0),
        "stdout_bytes": (render_proc.get("stdout") or {}).get("size", 0) + (gallery_proc.get("stdout") or {}).get("size", 0),
        "stderr_bytes": (render_proc.get("stderr") or {}).get("size", 0) + (gallery_proc.get("stderr") or {}).get("size", 0),
    }
    status = "ready" if (
        render.get("status") == "ready"
        and os.path.isfile(gallery_manifest)
        and checks["frames_rendered"] == checks["frames_requested"]
        and checks["render_failures"] == 0
        and checks["process_failures"] == 0
        and checks["gif_bytes"] > 0
    ) else "failed"
    summary_path = os.path.abspath(args.summary)
    summary = {
        "schema": "lsfs_mitsuba_xml_backend_command_adapter",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source_export": file_entry(export_path, root, "Mitsuba XML export"),
        "runtime": {
            "python": python_path,
            "render_script": posix_rel(resolve_path(args.render_script, root), root),
            "gallery_script": posix_rel(resolve_path(args.gallery_script, root), root),
            "variant": args.variant,
            "spp": args.spp,
            "output_format": args.output_format,
            "write_png": args.write_png,
            "llvm_dll": posix_rel(resolve_path(args.llvm_dll, root), root) if args.llvm_dll else None,
            "llvm_dir": posix_rel(resolve_path(args.llvm_dir, root), root) if args.llvm_dir else None,
        },
        "processes": {
            "render": render_proc,
            "gallery": gallery_proc,
        },
        "render_manifest": file_entry(render_manifest, root, "Mitsuba render manifest") if os.path.isfile(render_manifest) else {},
        "gallery_manifest": file_entry(gallery_manifest, root, "Mitsuba render gallery manifest") if os.path.isfile(gallery_manifest) else {},
        "gallery_index_repo_path": gallery.get("index_repo_path"),
        "checks": checks,
        "next": args.next,
    }
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames_rendered']}/{checks['frames_requested']} "
        f"process_failures={checks['process_failures']} summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a real Mitsuba XML backend command adapter")
    parser.add_argument("export")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--python", help="Python executable with the Mitsuba package installed")
    parser.add_argument("--render-script", default="tools/render_mitsuba_xml_export.py")
    parser.add_argument("--gallery-script", default="tools/build_mitsuba_render_gallery.py")
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--spp", type=int, default=1)
    parser.add_argument("--variant", default="scalar_rgb")
    parser.add_argument("--output-format", default="exr")
    parser.add_argument("--write-png", action="store_true")
    parser.add_argument("--llvm-dll")
    parser.add_argument("--llvm-dir")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--no-hard-exit-on-success", action="store_true")
    parser.add_argument("--title", default="S506 Mitsuba XML Backend Command Adapter")
    parser.add_argument("--render-title", default="S506 Mitsuba XML Backend Render")
    parser.add_argument("--gallery-title", default="S506 Mitsuba XML Backend Render Gallery")
    parser.add_argument("--render-next", default="Package this render through the command-adapter gallery.")
    parser.add_argument("--gallery-next", default="Publish this real Mitsuba command adapter gallery for external review.")
    parser.add_argument("--next", default="Publish this real Mitsuba command adapter gallery for external review.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.timeout <= 0.0:
        parser.error("timeout must be positive")
    build_summary(args)


if __name__ == "__main__":
    main()
