"""Render a validated LSFS Mitsuba XML export with the Mitsuba Python API."""

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


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def selected_frames(frames, requested=None):
    if not frames:
        return []
    if requested is None or requested <= 0 or requested >= len(frames):
        return frames
    if requested == 1:
        return [frames[0]]
    indices = sorted(set(round(i * (len(frames) - 1) / float(requested - 1)) for i in range(requested)))
    return [frames[index] for index in indices]


def configure_llvm(args):
    env = {
        "drjit_libllvm_path": None,
        "path_prepend": None,
    }
    if args.llvm_dll:
        dll_path = resolve_path(args.llvm_dll)
        os.environ["DRJIT_LIBLLVM_PATH"] = dll_path
        dll_dir = os.path.dirname(dll_path)
        os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(dll_dir)
        env["drjit_libllvm_path"] = dll_path
        env["path_prepend"] = dll_dir
    elif args.llvm_dir:
        llvm_dir = resolve_path(args.llvm_dir)
        os.environ["DRJIT_LIBLLVM_PATH"] = llvm_dir
        os.environ["PATH"] = llvm_dir + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(llvm_dir)
        env["drjit_libllvm_path"] = llvm_dir
        env["path_prepend"] = llvm_dir
    return env


def bitmap_to_png(mi, bitmap, png_path):
    converted = bitmap.convert(mi.Bitmap.PixelFormat.RGB, mi.Struct.Type.UInt8, True)
    converted.write(png_path)


def render_export(args):
    root = os.getcwd()
    export_path = require_file(args.export, "mitsuba export")
    export = read_json(export_path)
    if export.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{args.export}: expected lsfs_mitsuba_xml_export schema")
    if export.get("status") != "ready":
        raise SystemExit(f"{args.export}: export status is {export.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    render_dir = os.path.join(out_dir, "renders")
    preview_dir = os.path.join(out_dir, "previews")
    os.makedirs(render_dir, exist_ok=True)
    if args.write_png:
        os.makedirs(preview_dir, exist_ok=True)

    failures = []
    rendered = []
    env = configure_llvm(args)
    try:
        import mitsuba as mi

        mi.set_variant(args.variant)
    except Exception as exc:
        failures.append({
            "kind": "mitsuba_import_or_variant_error",
            "variant": args.variant,
            "error": str(exc),
        })
        mi = None

    start = time.perf_counter()
    if mi is not None:
        for index, frame in enumerate(selected_frames(export.get("frames") or [], args.frames)):
            xml_path = resolve_path((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path"))
            if not xml_path or not os.path.isfile(xml_path):
                failures.append({
                    "kind": "missing_xml_scene",
                    "output_frame": frame.get("output_frame"),
                    "path": xml_path,
                })
                continue
            base = f"frame_{index:04d}"
            image_path = os.path.join(render_dir, f"{base}.{args.output_format}")
            png_path = os.path.join(preview_dir, f"{base}.png") if args.write_png else None
            frame_start = time.perf_counter()
            try:
                scene = mi.load_file(xml_path)
                image = mi.render(scene, spp=args.spp)
                bitmap = mi.Bitmap(image)
                bitmap.write(image_path)
                if png_path:
                    bitmap_to_png(mi, bitmap, png_path)
                elapsed_ms = int(round((time.perf_counter() - frame_start) * 1000.0))
                rendered.append({
                    "output_frame": frame.get("output_frame"),
                    "sequence_frame": frame.get("sequence_frame"),
                    "xml_scene": {
                        "path": xml_path,
                        "repo_path": posix_rel(xml_path, root),
                    },
                    "image": {
                        "path": image_path,
                        "repo_path": posix_rel(image_path, root),
                        "sha256": sha256_file(image_path),
                        "size": os.path.getsize(image_path),
                    },
                    "preview": {
                        "path": png_path,
                        "repo_path": posix_rel(png_path, root) if png_path else None,
                        "sha256": sha256_file(png_path) if png_path else None,
                        "size": os.path.getsize(png_path) if png_path else 0,
                    },
                    "elapsed_ms": elapsed_ms,
                })
            except Exception as exc:
                failures.append({
                    "kind": "frame_render_error",
                    "output_frame": frame.get("output_frame"),
                    "xml_scene": posix_rel(xml_path, root),
                    "error": str(exc),
                })
                if args.fail_fast:
                    break

    total_elapsed_ms = int(round((time.perf_counter() - start) * 1000.0))
    status = "failed" if failures or not rendered else "ready"
    return {
        "schema": "lsfs_mitsuba_xml_render",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "title": args.title,
        "mitsuba_export": {
            "path": export_path,
            "repo_path": posix_rel(export_path, root),
            "sha256": sha256_file(export_path),
        },
        "runtime": {
            "variant": args.variant,
            "spp": args.spp,
            "output_format": args.output_format,
            "write_png": args.write_png,
            "drjit_libllvm_path": env.get("drjit_libllvm_path"),
            "path_prepend": env.get("path_prepend"),
        },
        "checks": {
            "frames_requested": args.frames,
            "frames_rendered": len(rendered),
            "failures": len(failures),
            "total_elapsed_ms": total_elapsed_ms,
            "image_bytes": sum(item["image"]["size"] for item in rendered),
            "preview_bytes": sum(item["preview"]["size"] for item in rendered),
        },
        "failures": failures,
        "frames": rendered,
        "next": args.next,
    }


def markdown_report(render, out_path, root):
    checks = render.get("checks", {})
    runtime = render.get("runtime", {})
    lines = [
        f"# {render['title']}",
        "",
        f"Generated UTC: `{render['generated_utc']}`",
        f"Render JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{render['status']}`",
        "",
        "## Runtime",
        "",
        f"- Variant: `{runtime.get('variant')}`",
        f"- SPP: `{runtime.get('spp')}`",
        f"- Output format: `{runtime.get('output_format')}`",
        f"- PNG preview: `{runtime.get('write_png')}`",
        f"- DRJIT_LIBLLVM_PATH: `{runtime.get('drjit_libllvm_path') or 'n/a'}`",
        "",
    ]
    supervisor = render.get("supervisor") or {}
    if supervisor:
        lines.extend([
            "## Supervisor",
            "",
            f"- Worker exit code: `{supervisor.get('worker_exit_code')}`",
            f"- Accepted ready manifest: `{supervisor.get('accepted_ready_manifest')}`",
            "",
        ])
    lines.extend([
        "## Inputs",
        "",
        f"- Mitsuba export: `{render.get('mitsuba_export', {}).get('repo_path')}`",
        "",
        "## Checks",
        "",
        f"- Frames requested: `{checks.get('frames_requested')}`",
        f"- Frames rendered: `{checks.get('frames_rendered')}`",
        f"- Failures: `{checks.get('failures')}`",
        f"- Total elapsed ms: `{checks.get('total_elapsed_ms')}`",
        f"- Image bytes: `{format_bytes(checks.get('image_bytes', 0))}`",
        f"- Preview bytes: `{format_bytes(checks.get('preview_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Sequence | Image | Preview | Elapsed ms |",
        "| ---: | ---: | --- | --- | ---: |",
    ])
    frames = render.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('sequence_frame')} | "
            f"`{frame.get('image', {}).get('repo_path')}` | "
            f"`{frame.get('preview', {}).get('repo_path') or 'n/a'}` | "
            f"{frame.get('elapsed_ms')} |"
        )
    if render.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in render["failures"][:12]:
            detail = failure.get("error") or failure.get("path") or ""
            lines.append(f"- `{failure.get('kind')}` {detail}")
    lines.extend([
        "",
        "## Next",
        "",
        render.get("next", "Scale this render probe to more frames after the runtime path is stable."),
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description="Render a Mitsuba XML export via the Python API")
    parser.add_argument("export")
    parser.add_argument("out_dir")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--spp", type=int, default=1)
    parser.add_argument("--variant", default="scalar_rgb")
    parser.add_argument("--output-format", default="exr")
    parser.add_argument("--write-png", action="store_true")
    parser.add_argument("--llvm-dll")
    parser.add_argument("--llvm-dir")
    parser.add_argument("--manifest-name", default="mitsuba_render.json")
    parser.add_argument("--report")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-supervise", action="store_true",
                        help="run rendering in this process instead of supervising a worker process")
    parser.add_argument("--no-hard-exit-on-success", action="store_true",
                        help="allow normal Mitsuba/Dr.Jit teardown after a successful render")
    parser.add_argument("--title", default="Mitsuba XML Render Probe")
    parser.add_argument(
        "--next",
        default="Scale the Mitsuba render path to a longer frame range and package the visual output.",
    )
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames <= 0:
        parser.error("frames must be positive")
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.llvm_dll and args.llvm_dir:
        parser.error("pass only one of --llvm-dll or --llvm-dir")

    if not args.worker and not args.no_supervise:
        child_argv = [sys.executable, os.path.abspath(__file__), *argv, "--worker"]
        child = subprocess.run(child_argv)
        out_path = os.path.abspath(os.path.join(args.out_dir, args.manifest_name))
        if child.returncode != 0 and os.path.isfile(out_path):
            try:
                render = read_json(out_path)
            except Exception:
                render = {}
            if render.get("schema") == "lsfs_mitsuba_xml_render" and render.get("status") == "ready":
                render["supervisor"] = {
                    "worker_exit_code": child.returncode,
                    "accepted_ready_manifest": True,
                }
                write_json(out_path, render)
                report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
                write_text(report_path, markdown_report(render, out_path, os.getcwd()))
                print(f"worker_exit={child.returncode} accepted_ready_manifest={out_path}")
                raise SystemExit(0)
        raise SystemExit(child.returncode)

    render = render_export(args)
    out_path = os.path.abspath(os.path.join(args.out_dir, args.manifest_name))
    write_json(out_path, render)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(render, out_path, os.getcwd()))
    print(
        f"status={render['status']} rendered={render['checks']['frames_rendered']} "
        f"failures={render['checks']['failures']} out={out_path}"
    )
    print(f"report={report_path}")
    sys.stdout.flush()
    sys.stderr.flush()
    if render["status"] != "ready":
        raise SystemExit(1)
    if not args.no_hard_exit_on_success:
        os._exit(0)


if __name__ == "__main__":
    main()
