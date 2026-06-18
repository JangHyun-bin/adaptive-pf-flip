#!/usr/bin/env python
"""Run the LSFS cinematic shot pipeline end to end.

The runner orchestrates existing tools; it does not change simulation or render
formats. It writes a durable shot_summary.json with commands, timings, and
artifact paths so a shot can be inspected or rerun.

Usage:
  python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/bubble_cinematic --frames 24 --width 1280 --height 720
"""

import argparse
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone


PRESETS = {
    "bubble_cinematic": {
        "kind": "sparse",
        "nx": 12,
        "ny": 18,
        "nz": 12,
        "dt": 0.02,
        "cg_iters": None,
        "physics_preset": False,
        "description": "Small sparse 3D two-phase bubble tank cinematic smoke preset.",
    },
}


class ShotError(Exception):
    pass


def fail(message):
    raise ShotError(message)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, payload):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def tool_path(root, name):
    return os.path.join(root, "tools", name)


def executable_name(base):
    return base + (".exe" if os.name == "nt" else "")


def exporter_candidates(build_dir, config):
    name = executable_name("export_render_cache3d")
    return [
        os.path.join(build_dir, config, name),
        os.path.join(build_dir, name),
    ]


def find_exporter(build_dir, config):
    for path in exporter_candidates(build_dir, config):
        if os.path.isfile(path):
            return os.path.abspath(path)
    return None


def command_for_summary(command):
    return [str(item) for item in command]


class Pipeline:
    def __init__(self, out_dir, cwd):
        self.out_dir = os.path.abspath(out_dir)
        self.cwd = cwd
        self.logs_dir = os.path.join(self.out_dir, "logs")
        self.commands = []
        os.makedirs(self.logs_dir, exist_ok=True)

    def run(self, label, command, allow_failure=False):
        index = len(self.commands) + 1
        safe_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label)
        stdout_path = os.path.join(self.logs_dir, f"{index:02d}_{safe_label}.stdout.log")
        stderr_path = os.path.join(self.logs_dir, f"{index:02d}_{safe_label}.stderr.log")
        started = time.perf_counter()
        result = subprocess.run(command,
                                cwd=self.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=False)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        with open(stdout_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(result.stdout)
        with open(stderr_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(result.stderr)
        item = {
            "label": label,
            "command": command_for_summary(command),
            "returncode": result.returncode,
            "elapsed_ms": elapsed_ms,
            "stdout_log": stdout_path,
            "stderr_log": stderr_path,
        }
        self.commands.append(item)
        if result.returncode != 0 and not allow_failure:
            tail = result.stderr.strip() or result.stdout.strip()
            if len(tail) > 500:
                tail = tail[-500:]
            fail(f"{label} failed with exit code {result.returncode}: {tail}")
        return result, item


def parse_positive_int(value, label):
    try:
        out = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"{label} must be an integer")
    if out <= 0:
        raise argparse.ArgumentTypeError(f"{label} must be positive")
    return out


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run an LSFS cinematic shot pipeline")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="bubble_cinematic")
    parser.add_argument("--out", required=True, help="output shot directory")
    parser.add_argument("--frames", type=lambda v: parse_positive_int(v, "frames"), default=24)
    parser.add_argument("--width", type=lambda v: parse_positive_int(v, "width"), default=1280)
    parser.add_argument("--height", type=lambda v: parse_positive_int(v, "height"), default=720)
    parser.add_argument("--renderer", choices=("auto", "preview", "blender"), default="auto")
    parser.add_argument("--kind", choices=("sparse", "mr"), help="override preset simulation kind")
    parser.add_argument("--nx", type=lambda v: parse_positive_int(v, "nx"))
    parser.add_argument("--ny", type=lambda v: parse_positive_int(v, "ny"))
    parser.add_argument("--nz", type=lambda v: parse_positive_int(v, "nz"))
    parser.add_argument("--sim-steps", type=lambda v: parse_positive_int(v, "sim-steps"),
                        help="simulation steps to export; defaults to --frames")
    parser.add_argument("--cache-every", type=lambda v: parse_positive_int(v, "cache-every"), default=1)
    parser.add_argument("--dt", type=float, help="simulation dt override")
    parser.add_argument("--cg-iters", type=int, help="pressure CG iteration override")
    parser.add_argument("--physics-preset", action="store_true", help="enable full physics preset in exporter")
    parser.add_argument("--build-dir", default="build", help="CMake build directory")
    parser.add_argument("--config", default="Release", help="CMake build config")
    parser.add_argument("--no-build", action="store_true", help="do not build exporter if missing")
    parser.add_argument("--rebuild", action="store_true", help="build exporter target before running")
    parser.add_argument("--threshold", type=float, default=0.02, help="water reconstruction threshold")
    parser.add_argument("--fps", type=float, default=12.0, help="output GIF frame rate")
    parser.add_argument("--samples", type=int, default=24, help="Blender render samples")
    parser.add_argument("--blender", help="explicit Blender executable path")
    parser.add_argument("--max-secondary-particles", type=int, default=512)
    parser.add_argument("--min-occupancy", type=float, default=0.01,
                        help="preview renderer minimum occupancy")
    parser.add_argument("--min-nonblank-ratio", type=float, default=0.05,
                        help="Blender frame nonblank gate")
    parser.add_argument("--timeout-seconds", type=int, default=300,
                        help="Blender subprocess timeout")
    args = parser.parse_args(argv)
    if args.dt is not None and (args.dt <= 0.0 or not math.isfinite(args.dt)):
        parser.error("dt must be finite and positive")
    if args.cg_iters is not None and args.cg_iters < 0:
        parser.error("cg-iters must be non-negative")
    if args.threshold < 0.0 or not math.isfinite(args.threshold):
        parser.error("threshold must be finite and non-negative")
    if args.fps <= 0.0 or not math.isfinite(args.fps):
        parser.error("fps must be finite and positive")
    if args.samples <= 0:
        parser.error("samples must be positive")
    if args.max_secondary_particles < 0:
        parser.error("max-secondary-particles must be non-negative")
    if args.min_occupancy < 0.0 or not math.isfinite(args.min_occupancy):
        parser.error("min-occupancy must be finite and non-negative")
    if args.min_nonblank_ratio < 0.0 or not math.isfinite(args.min_nonblank_ratio):
        parser.error("min-nonblank-ratio must be finite and non-negative")
    if args.timeout_seconds <= 0:
        parser.error("timeout-seconds must be positive")
    return args


def effective_config(args):
    preset = PRESETS[args.preset]
    return {
        "preset": args.preset,
        "description": preset["description"],
        "kind": args.kind or preset["kind"],
        "nx": args.nx or preset["nx"],
        "ny": args.ny or preset["ny"],
        "nz": args.nz or preset["nz"],
        "dt": args.dt if args.dt is not None else preset["dt"],
        "cg_iters": args.cg_iters if args.cg_iters is not None else preset["cg_iters"],
        "physics_preset": bool(args.physics_preset or preset["physics_preset"]),
        "sim_steps": args.sim_steps or args.frames,
        "cache_every": args.cache_every,
        "frames": args.frames,
        "width": args.width,
        "height": args.height,
    }


def ensure_exporter(pipeline, root, build_dir, config, no_build, rebuild):
    build_dir_abs = os.path.abspath(build_dir)
    exporter = find_exporter(build_dir_abs, config)
    if rebuild or (exporter is None and not no_build):
        pipeline.run("build_exporter", [
            "cmake", "--build", build_dir_abs, "--config", config, "--target", "export_render_cache3d"
        ])
        exporter = find_exporter(build_dir_abs, config)
    if exporter is None:
        candidates = ", ".join(exporter_candidates(build_dir_abs, config))
        fail(f"export_render_cache3d executable not found; checked {candidates}")
    return exporter


def parse_blender_check(stdout):
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {"available": False, "error": "invalid check JSON"}
    return payload if isinstance(payload, dict) else {"available": False, "error": "invalid check payload"}


def choose_renderer(args, pipeline, root):
    if args.renderer != "auto":
        return args.renderer, None
    command = [sys.executable, tool_path(root, "render_bridge_blender.py"), "--check"]
    if args.blender:
        command.extend(["--blender", args.blender])
    result, _ = pipeline.run("check_blender", command, allow_failure=True)
    report = parse_blender_check(result.stdout)
    return ("blender" if report.get("available") else "preview"), report


def require_file(path, label):
    if not os.path.isfile(path):
        fail(f"{label} was not created: {path}")
    return path


def require_dir(path, label):
    if not os.path.isdir(path):
        fail(f"{label} was not created: {path}")
    return path


def run_pipeline(args):
    root = repo_root()
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    pipeline = Pipeline(out_dir, root)
    started = utc_now()
    config = effective_config(args)
    cache_dir = os.path.join(out_dir, "cache")
    converted_dir = os.path.join(out_dir, "converted")
    water_dir = os.path.join(out_dir, "water_mesh")
    preview_dir = os.path.join(out_dir, "preview")
    blender_dir = os.path.join(out_dir, "blender")
    os.makedirs(cache_dir, exist_ok=True)

    manifest_path = os.path.join(cache_dir, "manifest.json")
    cache_prefix = os.path.join(cache_dir, "render_cache")
    water_index = os.path.join(water_dir, "water_reconstruction.json")
    sequence_path = os.path.join(converted_dir, "sequence.json")
    gif_path = os.path.join(out_dir, "shot.gif")
    summary_path = os.path.join(out_dir, "shot_summary.json")
    summary = {
        "runner": "lsfs_cinematic_shot_pipeline",
        "version": 1,
        "status": "running",
        "started_utc": started,
        "finished_utc": None,
        "out_dir": out_dir,
        "config": config,
        "requested_renderer": args.renderer,
        "selected_renderer": None,
        "artifacts": {
            "manifest": manifest_path,
            "sequence": sequence_path,
            "water_reconstruction": water_index,
            "gif": gif_path,
        },
        "commands": pipeline.commands,
    }

    def finish(status, error=None):
        summary["status"] = status
        summary["finished_utc"] = utc_now()
        summary["commands"] = pipeline.commands
        if error:
            summary["error"] = str(error)
        write_json(summary_path, summary)

    try:
        exporter = ensure_exporter(pipeline,
                                   root,
                                   args.build_dir,
                                   args.config,
                                   args.no_build,
                                   args.rebuild)
        summary["exporter"] = exporter
        export_cmd = [
            exporter,
            "--kind", config["kind"],
            "--nx", str(config["nx"]),
            "--ny", str(config["ny"]),
            "--nz", str(config["nz"]),
            "--steps", str(config["sim_steps"]),
            "--every", str(config["cache_every"]),
            "--dt", str(config["dt"]),
            "--out-prefix", cache_prefix,
            "--manifest", manifest_path,
        ]
        if config["cg_iters"] is not None:
            export_cmd.extend(["--cg-iters", str(config["cg_iters"])])
        if config["physics_preset"]:
            export_cmd.append("--physics-preset")
        pipeline.run("export_render_cache", export_cmd)
        require_file(manifest_path, "render cache manifest")

        pipeline.run("validate_render_cache", [
            sys.executable,
            tool_path(root, "validate_render_cache.py"),
            manifest_path,
            "--require-cinematic",
        ])

        pipeline.run("reconstruct_water", [
            sys.executable,
            tool_path(root, "reconstruct_water.py"),
            manifest_path,
            water_dir,
            "--frames", str(config["frames"]),
            "--threshold", str(args.threshold),
        ])
        require_file(water_index, "water reconstruction index")

        pipeline.run("convert_render_cache", [
            sys.executable,
            tool_path(root, "convert_render_cache.py"),
            manifest_path,
            converted_dir,
            "--require-cinematic",
            "--water-reconstruction", water_index,
        ])
        require_file(sequence_path, "converted sequence")

        selected_renderer, blender_report = choose_renderer(args, pipeline, root)
        summary["selected_renderer"] = selected_renderer
        if blender_report is not None:
            summary["blender_check"] = blender_report

        if selected_renderer == "blender":
            render_dir = blender_dir
            command = [
                sys.executable,
                tool_path(root, "render_bridge_blender.py"),
                sequence_path,
                render_dir,
                "--frames", str(config["frames"]),
                "--width", str(config["width"]),
                "--height", str(config["height"]),
                "--samples", str(args.samples),
                "--max-secondary-particles", str(args.max_secondary_particles),
                "--min-nonblank-ratio", str(args.min_nonblank_ratio),
                "--timeout-seconds", str(args.timeout_seconds),
            ]
            if args.blender:
                command.extend(["--blender", args.blender])
            pipeline.run("render_blender", command)
            frame_dir = os.path.join(render_dir, "frames")
            summary["artifacts"]["render_summary"] = os.path.join(render_dir, "bridge_summary.json")
        else:
            render_dir = preview_dir
            pipeline.run("render_preview", [
                sys.executable,
                tool_path(root, "cinematic_render_stub.py"),
                manifest_path,
                render_dir,
                "--frames", str(config["frames"]),
                "--width", str(config["width"]),
                "--height", str(config["height"]),
                "--min-occupancy", str(args.min_occupancy),
                "--water-reconstruction", water_index,
            ])
            frame_dir = render_dir
            summary["artifacts"]["render_summary"] = os.path.join(render_dir, "render_summary.json")
        require_dir(frame_dir, "render frame directory")
        summary["artifacts"]["render_frame_dir"] = frame_dir

        pipeline.run("assemble_gif", [
            sys.executable,
            tool_path(root, "assemble_frames.py"),
            frame_dir,
            gif_path,
            "--fps", str(args.fps),
        ])
        require_file(gif_path, "shot GIF")

        manifest = read_json(manifest_path)
        sequence = read_json(sequence_path)
        water = read_json(water_index)
        summary["metrics"] = {
            "cache_frame_count": len(manifest.get("frames", [])),
            "converted_frame_count": sequence.get("frame_count"),
            "water_mesh_frame_count": water.get("frame_count"),
            "shot_gif_bytes": os.path.getsize(gif_path),
        }
        finish("ok")
        print(f"status=ok renderer={selected_renderer} frames={config['frames']}")
        print(f"summary={summary_path}")
        print(f"gif={gif_path}")
        return 0
    except ShotError as exc:
        finish("failed", exc)
        print(f"status=fail error={exc} summary={summary_path}", file=sys.stderr)
        return 1
    except OSError as exc:
        finish("failed", exc)
        print(f"status=fail error={exc} summary={summary_path}", file=sys.stderr)
        return 1


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())
