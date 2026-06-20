#!/usr/bin/env python
"""Probe local Mitsuba Python/LLVM runtime combinations."""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

from build_bridge_review_package import posix_rel, read_json, require_file, write_json, write_text


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def unique_existing(items):
    seen = set()
    out = []
    for item in items:
        if not item:
            continue
        resolved = os.path.abspath(os.path.expandvars(item))
        key = os.path.normcase(resolved)
        if key in seen:
            continue
        seen.add(key)
        if os.path.exists(resolved):
            out.append(resolved)
    return out


def default_pythons():
    return unique_existing([
        os.environ.get("MITSUBA_PYTHON"),
        sys.executable,
        r"C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe",
    ])


def default_llvm_dirs():
    return unique_existing([
        os.environ.get("DRJIT_LIBLLVM_PATH"),
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\Llvm\x64\bin",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\Llvm\bin",
        r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin",
        r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\bin",
    ])


def first_xml_scene(export):
    frames = export.get("frames") or []
    if not frames:
        return None
    scene = frames[0].get("xml_scene") or {}
    return resolve_path(scene.get("path") or scene.get("repo_path"))


def run_python(python_path, snippet, env_extra, timeout):
    env = os.environ.copy()
    env.update(env_extra)
    try:
        result = subprocess.run(
            [python_path, "-c", snippet],
            capture_output=True,
            env=env,
            text=True,
            timeout=timeout,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def import_probe_snippet():
    return "\n".join([
        "import mitsuba as mi",
        "print('mitsuba_version=' + str(mi.__version__))",
        "print('variants=' + ','.join(mi.variants()))",
        "mi.set_variant('scalar_rgb')",
        "print('variant=scalar_rgb')",
    ])


def load_probe_snippet(xml_scene):
    return "\n".join([
        "import mitsuba as mi",
        "mi.set_variant('scalar_rgb')",
        f"scene = mi.load_file({xml_scene!r})",
        "print('loaded=' + type(scene).__name__)",
    ])


def render_probe_snippet(xml_scene, output_path, spp):
    return "\n".join([
        "import os",
        "import mitsuba as mi",
        "mi.set_variant('scalar_rgb')",
        f"scene = mi.load_file({xml_scene!r})",
        f"image = mi.render(scene, spp={int(spp)})",
        f"out = {output_path!r}",
        "os.makedirs(os.path.dirname(out), exist_ok=True)",
        "mi.Bitmap(image).write(out)",
        "print('rendered=' + out)",
        "print('bytes=' + str(os.path.getsize(out)))",
    ])


def llvm_env(llvm_dir):
    if not llvm_dir:
        return {}
    path = os.path.abspath(llvm_dir)
    env = {"DRJIT_LIBLLVM_PATH": path}
    if os.path.isdir(path):
        env["PATH"] = path + os.pathsep + os.environ.get("PATH", "")
    else:
        env["PATH"] = os.path.dirname(path) + os.pathsep + os.environ.get("PATH", "")
    return env


def candidate_label(path):
    if not path:
        return "none"
    resolved = os.path.abspath(path)
    parts = [part for part in resolved.split(os.sep) if part and part != ":"]
    if len(parts) > 7:
        parts = parts[-7:]
    label = "_".join(parts)
    for old, new in (("Program Files", "pf"), ("Microsoft Visual Studio", "vs")):
        label = label.replace(old, new)
    return label.replace(" ", "_").replace(".", "_").replace(":", "")


def markdown_report(payload, report_path, root):
    checks = payload.get("checks") or {}
    lines = [
        f"# {payload['title']}",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Diagnostics JSON: `{posix_rel(payload['diagnostics_path'], root)}`",
        f"Status: `{payload['status']}`",
        "",
        "## Inputs",
        "",
        f"- Mitsuba export: `{payload['mitsuba_export']['repo_path']}`",
        f"- XML scene: `{payload.get('xml_scene_repo_path')}`",
        "",
        "## Checks",
        "",
        f"- Python candidates: `{checks.get('python_candidates')}`",
        f"- LLVM candidates: `{checks.get('llvm_candidates')}`",
        f"- Import-ready Python entries: `{checks.get('import_ready')}`",
        f"- Scene-load-ready entries: `{checks.get('load_ready')}`",
        f"- Render-ready entries: `{checks.get('render_ready')}`",
        "",
        "## Python Probe",
        "",
        "| Python | Exit | Result |",
        "| --- | ---: | --- |",
    ]
    for item in payload.get("python_probes") or []:
        result = "ok" if item["import_probe"].get("exit_code") == 0 else "failed"
        lines.append(f"| `{item['python']}` | {item['import_probe'].get('exit_code')} | `{result}` |")
    lines.extend([
        "",
        "## Render Probe",
        "",
        "| Python | LLVM | Load Exit | Render Exit | Rendered Bytes |",
        "| --- | --- | ---: | ---: | ---: |",
    ])
    for item in payload.get("runtime_probes") or []:
        lines.append(
            f"| `{item['python']}` | `{item.get('llvm_label')}` | "
            f"{item['load_probe'].get('exit_code')} | {item['render_probe'].get('exit_code')} | "
            f"{item.get('rendered_bytes', 0)} |"
        )
    if payload.get("notable_failures"):
        lines.extend(["", "## Notable Failures", ""])
        for failure in payload["notable_failures"][:12]:
            lines.append(
                f"- `{failure.get('stage')}` python=`{failure.get('python')}` "
                f"llvm=`{failure.get('llvm_label')}` exit=`{failure.get('exit_code')}` "
                f"{failure.get('message')}"
            )
    lines.extend(["", "## Next", "", payload.get("next") or "Fix the runtime path, then rerun this probe.", ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    export_path = require_file(args.export, "Mitsuba export")
    export = read_json(export_path)
    xml_scene = first_xml_scene(export)
    if not xml_scene or not os.path.isfile(xml_scene):
        raise SystemExit(f"{args.export}: could not resolve first XML scene")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    pythons = unique_existing(args.python or []) or default_pythons()
    llvm_dirs = unique_existing(args.llvm_dir or []) or default_llvm_dirs()
    llvm_entries = [None] + llvm_dirs

    python_probes = []
    import_ready = []
    for python_path in pythons:
        probe = run_python(python_path, import_probe_snippet(), {}, args.timeout)
        item = {"python": python_path, "import_probe": probe}
        python_probes.append(item)
        if probe.get("exit_code") == 0:
            import_ready.append(python_path)

    runtime_probes = []
    render_ready = []
    load_ready = []
    notable = []
    for py_index, python_path in enumerate(import_ready):
        for llvm_index, llvm_dir in enumerate(llvm_entries):
            label = candidate_label(llvm_dir)
            env = llvm_env(llvm_dir)
            render_path = os.path.join(out_dir, "renders", f"probe_{py_index:02d}_{llvm_index:02d}_{label}.exr")
            load_probe = run_python(python_path, load_probe_snippet(xml_scene), env, args.timeout)
            render_probe = run_python(
                python_path,
                render_probe_snippet(xml_scene, render_path, args.spp),
                env,
                args.timeout,
            )
            rendered_bytes = os.path.getsize(render_path) if os.path.isfile(render_path) else 0
            item = {
                "python": python_path,
                "llvm": llvm_dir,
                "llvm_label": label,
                "load_probe": load_probe,
                "render_probe": render_probe,
                "rendered_output": render_path if rendered_bytes else None,
                "rendered_repo_path": posix_rel(render_path, root) if rendered_bytes else None,
                "rendered_bytes": rendered_bytes,
            }
            runtime_probes.append(item)
            if load_probe.get("exit_code") == 0:
                load_ready.append(item)
            if render_probe.get("exit_code") == 0 and rendered_bytes > 0:
                render_ready.append(item)
            elif render_probe.get("exit_code") != 0 or render_probe.get("timed_out"):
                message = render_probe.get("stderr") or render_probe.get("stdout") or "render probe failed"
                notable.append({
                    "stage": "render",
                    "python": python_path,
                    "llvm_label": label,
                    "exit_code": render_probe.get("exit_code"),
                    "message": message.splitlines()[-1] if message else "",
                })

    status = "ready" if render_ready else "blocked"
    out_path = os.path.join(out_dir, args.manifest_name)
    payload = {
        "schema": "lsfs_mitsuba_runtime_diagnostics",
        "version": 1,
        "title": args.title,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "diagnostics_path": out_path,
        "mitsuba_export": {
            "path": export_path,
            "repo_path": posix_rel(export_path, root),
        },
        "xml_scene": xml_scene,
        "xml_scene_repo_path": posix_rel(xml_scene, root),
        "python_probes": python_probes,
        "runtime_probes": runtime_probes,
        "notable_failures": notable,
        "checks": {
            "python_candidates": len(pythons),
            "llvm_candidates": len(llvm_dirs),
            "import_ready": len(import_ready),
            "load_ready": len(load_ready),
            "render_ready": len(render_ready),
        },
        "next": args.next,
    }
    write_json(out_path, payload)
    if args.report:
        write_text(args.report, markdown_report(payload, out_path, root))
    print(
        f"status={status} python={len(pythons)} import_ready={len(import_ready)} "
        f"load_ready={len(load_ready)} render_ready={len(render_ready)} out={out_path}"
    )
    if status != "ready" and args.fail_on_blocked:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Probe local Mitsuba Python/LLVM runtime combinations")
    parser.add_argument("export")
    parser.add_argument("out_dir")
    parser.add_argument("--python", action="append")
    parser.add_argument("--llvm-dir", action="append")
    parser.add_argument("--spp", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--manifest-name", default="mitsuba_runtime_diagnostics.json")
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Runtime Diagnostics")
    parser.add_argument(
        "--next",
        default="Fix or isolate the first render-ready Mitsuba runtime, then rerun the LR1 render.",
    )
    parser.add_argument("--fail-on-blocked", action="store_true")
    args = parser.parse_args(argv)
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    build(args)


if __name__ == "__main__":
    main()
