#!/usr/bin/env python
"""Run a narrow Mitsuba residual-response energy sweep."""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


DEFAULT_VARIANTS = [
    {
        "label": "rr5_hint_low",
        "output_frames": "13",
        "request_limit": 16,
        "per_frame_request_limit": 4,
        "patch_limit": 8,
        "bbox_padding": 12.0,
        "max_vertices_per_request": 2400,
        "radius_scale": 0.23,
        "radiance_scale": 1.4,
        "min_radius": 0.045,
        "max_radius": 0.65,
        "aspect": 0.55,
        "y_lift": 0.026,
    },
    {
        "label": "rr6_mid",
        "output_frames": "13",
        "request_limit": 16,
        "per_frame_request_limit": 4,
        "patch_limit": 8,
        "bbox_padding": 12.0,
        "max_vertices_per_request": 2400,
        "radius_scale": 0.25,
        "radiance_scale": 1.8,
        "min_radius": 0.045,
        "max_radius": 0.65,
        "aspect": 0.55,
        "y_lift": 0.026,
    },
    {
        "label": "rr7_rr4_soft",
        "output_frames": "13",
        "request_limit": 16,
        "per_frame_request_limit": 4,
        "patch_limit": 8,
        "bbox_padding": 12.0,
        "max_vertices_per_request": 2400,
        "radius_scale": 0.28,
        "radiance_scale": 2.0,
        "min_radius": 0.045,
        "max_radius": 0.65,
        "aspect": 0.55,
        "y_lift": 0.026,
    },
    {
        "label": "rr8_rr4_plus",
        "output_frames": "13",
        "request_limit": 16,
        "per_frame_request_limit": 4,
        "patch_limit": 8,
        "bbox_padding": 12.0,
        "max_vertices_per_request": 2400,
        "radius_scale": 0.30,
        "radiance_scale": 2.2,
        "min_radius": 0.045,
        "max_radius": 0.65,
        "aspect": 0.55,
        "y_lift": 0.026,
    },
]


VARIANT_KEYS = {
    "label",
    "output_frames",
    "request_limit",
    "per_frame_request_limit",
    "patch_limit",
    "bbox_padding",
    "max_vertices_per_request",
    "radius_scale",
    "radiance_scale",
    "min_radius",
    "max_radius",
    "aspect",
    "y_lift",
}


def resolve_path(path):
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def default_render_python():
    candidate = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Programs",
        "Python",
        "Python311",
        "python.exe",
    )
    if candidate and os.path.isfile(candidate):
        return candidate
    return sys.executable


def parse_variant(value):
    if ":" not in value:
        raise argparse.ArgumentTypeError("variant must be LABEL:key=value,key=value")
    label, raw_settings = value.split(":", 1)
    variant = {"label": label.strip()}
    if not variant["label"]:
        raise argparse.ArgumentTypeError("variant label cannot be empty")
    for token in raw_settings.split(","):
        if not token.strip():
            continue
        if "=" not in token:
            raise argparse.ArgumentTypeError(f"variant setting must be key=value: {token}")
        key, raw = token.split("=", 1)
        key = key.strip().replace("-", "_")
        raw = raw.strip()
        if key not in VARIANT_KEYS or key == "label":
            raise argparse.ArgumentTypeError(f"unsupported variant key: {key}")
        if key == "output_frames":
            variant[key] = raw
        elif key in {"request_limit", "per_frame_request_limit", "patch_limit", "max_vertices_per_request"}:
            variant[key] = int(raw)
        else:
            variant[key] = float(raw)
    missing = set(DEFAULT_VARIANTS[0]).difference(variant)
    if missing:
        raise argparse.ArgumentTypeError(f"{variant['label']}: missing settings {sorted(missing)}")
    return variant


def variants(raw_variants):
    items = [dict(item) for item in DEFAULT_VARIANTS] if not raw_variants else [parse_variant(item) for item in raw_variants]
    labels = set()
    for item in items:
        label = item["label"]
        if label in labels:
            raise SystemExit(f"duplicate variant label: {label}")
        labels.add(label)
    return items


def cmd_text(cmd):
    return " ".join(f'"{item}"' if " " in str(item) else str(item) for item in cmd)


def run_cmd(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return {
        "command": cmd,
        "command_text": cmd_text(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def require_success(step, result):
    if result["returncode"] != 0:
        raise SystemExit(
            f"{step} failed with code {result['returncode']}\n"
            f"command: {result['command_text']}\n"
            f"stdout:\n{result['stdout']}\n"
            f"stderr:\n{result['stderr']}"
        )


def variant_energy(variant):
    return float(variant["radius_scale"]) * float(variant["radiance_scale"])


def run_variant(args, variant, root):
    label = variant["label"]
    shot_dir = os.path.join(args.out_dir, label)
    validation_dir = os.path.join(args.out_dir, f"{label}_validation")
    render_dir = os.path.join(args.out_dir, f"{label}_render")
    gap_dir = os.path.join(args.out_dir, f"{label}_target_gap")
    report_prefix = f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_{label}"
    reports = {
        "export": os.path.join("docs", "reports", f"{report_prefix}_export_s456.md"),
        "validate": os.path.join("docs", "reports", f"{report_prefix}_validate_s456.md"),
        "render": os.path.join("docs", "reports", f"{report_prefix}_render_s456.md"),
        "target_gap": os.path.join("docs", "reports", f"{report_prefix}_target_gap_s456.md"),
    }
    export_cmd = [
        sys.executable,
        "tools/add_mitsuba_residual_response_patches.py",
        args.base_export,
        args.residual_analysis,
        shot_dir,
        "--frames",
        str(args.frames),
        "--output-frames",
        str(variant["output_frames"]),
        "--request-limit",
        str(variant["request_limit"]),
        "--per-frame-request-limit",
        str(variant["per_frame_request_limit"]),
        "--patch-limit",
        str(variant["patch_limit"]),
        "--bbox-padding",
        str(variant["bbox_padding"]),
        "--max-vertices-per-request",
        str(variant["max_vertices_per_request"]),
        "--radius-scale",
        str(variant["radius_scale"]),
        "--min-radius",
        str(variant["min_radius"]),
        "--max-radius",
        str(variant["max_radius"]),
        "--aspect",
        str(variant["aspect"]),
        "--y-lift",
        str(variant["y_lift"]),
        "--radiance-scale",
        str(variant["radiance_scale"]),
        "--report",
        reports["export"],
        "--title",
        f"S456 Mitsuba Residual Response {label} Export",
        "--next",
        f"Validate, render, and compare S456 {label}.",
        "--fail-on-review",
    ]
    validate_cmd = [
        sys.executable,
        "tools/validate_mitsuba_xml_export.py",
        os.path.join(shot_dir, "mitsuba_export.json"),
        "--out",
        os.path.join(validation_dir, "mitsuba_export_validation.json"),
        "--report",
        reports["validate"],
        "--title",
        f"S456 Mitsuba Residual Response {label} Validation",
        "--next",
        f"Render S456 {label}.",
    ]
    render_cmd = [
        args.render_python,
        "tools/render_mitsuba_xml_export.py",
        os.path.join(shot_dir, "mitsuba_export.json"),
        render_dir,
        "--frames",
        str(args.frames),
        "--spp",
        str(args.spp),
        "--write-png",
        "--llvm-dll",
        args.llvm_dll,
        "--report",
        reports["render"],
        "--title",
        f"S456 Mitsuba Residual Response {label} Render",
        "--next",
        f"Compare S456 {label} target gap.",
    ]
    compare_cmd = [
        sys.executable,
        "tools/compare_mitsuba_renderer_target_gap.py",
        args.handoff_manifest,
        args.target_summary,
        gap_dir,
        "--actual-render-manifest",
        os.path.join(render_dir, "mitsuba_render.json"),
        "--fps",
        str(args.fps),
        "--keyframes",
        str(args.keyframes),
        "--report",
        reports["target_gap"],
        "--title",
        f"S456 Mitsuba Residual Response {label} Target Gap",
        "--next",
        f"Rank S456 {label} against RR4 and the S456 sweep.",
    ]
    command_results = []
    for step, cmd in (
        ("export", export_cmd),
        ("validate", validate_cmd),
        ("render", render_cmd),
        ("target_gap", compare_cmd),
    ):
        result = run_cmd(cmd, root)
        command_results.append({"step": step, **result})
        require_success(f"{label}:{step}", result)
    export_path = os.path.join(shot_dir, "mitsuba_export.json")
    gap_path = os.path.join(gap_dir, "renderer_target_gap_summary.json")
    gap = read_json(gap_path)
    export = read_json(export_path)
    return {
        "label": label,
        "energy": variant_energy(variant),
        "variant": variant,
        "paths": {
            "export": posix_rel(resolve_path(export_path), root),
            "validation": posix_rel(resolve_path(os.path.join(validation_dir, "mitsuba_export_validation.json")), root),
            "render": posix_rel(resolve_path(os.path.join(render_dir, "mitsuba_render.json")), root),
            "target_gap": posix_rel(resolve_path(gap_path), root),
        },
        "reports": reports,
        "checks": {
            "export": export.get("checks") or {},
            "target_gap": gap.get("checks") or {},
        },
        "commands": command_results,
    }


def parse_reference_candidate(value):
    if len(value) != 3:
        raise argparse.ArgumentTypeError("reference-candidate requires LABEL GAP_SUMMARY EXPORT_MANIFEST")
    return {
        "label": value[0],
        "gap_summary": value[1],
        "export_manifest": value[2],
    }


def run_fit(args, results, root):
    fit_dir = os.path.join(args.out_dir, "fit")
    fit_report = os.path.join("docs", "reports", f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_fit_s456.md")
    cmd = [
        sys.executable,
        "tools/fit_mitsuba_residual_response_candidates.py",
        args.baseline_gap_summary,
        fit_dir,
        "--max-abs-gap-limit",
        str(args.max_abs_gap_limit),
        "--report",
        fit_report,
        "--title",
        "S456 Mitsuba Residual Response Energy Fit",
        "--next",
        "Use the best safe energy candidate as the current target-driven response preset.",
    ]
    for reference in args.reference_candidate or []:
        cmd.extend(["--candidate", reference["label"], reference["gap_summary"], reference["export_manifest"]])
    for result in results:
        cmd.extend([
            "--candidate",
            result["label"],
            resolve_path(result["paths"]["target_gap"]),
            resolve_path(result["paths"]["export"]),
        ])
    fit_result = run_cmd(cmd, root)
    require_success("fit", fit_result)
    fit_summary_path = os.path.join(fit_dir, "residual_response_fit_summary.json")
    fit_summary = read_json(fit_summary_path)
    return {
        "path": posix_rel(resolve_path(fit_summary_path), root),
        "report": fit_report,
        "sha256": sha256_file(fit_summary_path),
        "best_safe_candidate": (fit_summary.get("best_safe_candidate") or {}).get("label"),
        "command": fit_result,
    }


def markdown_report(summary, summary_path, root):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Base export: `{summary['sources']['base_export']['repo_path']}`",
        f"- Residual analysis: `{summary['sources']['residual_analysis']['repo_path']}`",
        f"- Baseline gap: `{summary['sources']['baseline_gap_summary']['repo_path']}`",
        "",
        "## Variants",
        "",
        "| Candidate | Energy | Mean Gap MAD | Max Gap MAD | Max Gap | Export Patches | Target Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("variants") or []:
        gap = item["checks"]["target_gap"]
        export = item["checks"]["export"]
        lines.append(
            f"| `{item['label']}` | {item['energy']} | "
            f"{gap.get('mean_gap_mean_abs_diff')} | {gap.get('max_gap_mean_abs_diff')} | "
            f"{gap.get('max_gap_max_abs_diff')} | {export.get('patches_inserted')} | "
            f"`{item['paths']['target_gap']}` |"
        )
    fit = summary.get("fit") or {}
    lines.extend([
        "",
        "## Fit",
        "",
        f"- Fit summary: `{fit.get('path')}`",
        f"- Fit report: `{fit.get('report')}`",
        f"- Best safe candidate: `{fit.get('best_safe_candidate')}`",
        "",
        "## Next",
        "",
        summary.get("next", ""),
        "",
    ])
    return "\n".join(lines)


def source_entry(path, root):
    resolved = require_file(resolve_path(path), "source")
    return {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
    }


def run_sweep(args):
    root = os.getcwd()
    args.base_export = require_file(resolve_path(args.base_export), "base export")
    args.residual_analysis = require_file(resolve_path(args.residual_analysis), "residual analysis")
    args.baseline_gap_summary = require_file(resolve_path(args.baseline_gap_summary), "baseline gap summary")
    args.handoff_manifest = require_file(resolve_path(args.handoff_manifest), "handoff manifest")
    args.target_summary = require_file(resolve_path(args.target_summary), "target summary")
    args.render_python = resolve_path(args.render_python)
    args.llvm_dll = resolve_path(args.llvm_dll)
    if not os.path.isfile(args.render_python):
        raise SystemExit(f"Missing render Python: {args.render_python}")
    if not os.path.isfile(args.llvm_dll):
        raise SystemExit(f"Missing LLVM DLL: {args.llvm_dll}")
    args.out_dir = os.path.abspath(args.out_dir)
    os.makedirs(args.out_dir, exist_ok=True)

    items = variants(args.variant)
    results = [run_variant(args, item, root) for item in items]
    fit = run_fit(args, results, root)
    summary = {
        "schema": "lsfs_mitsuba_residual_response_energy_sweep",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "sources": {
            "base_export": source_entry(args.base_export, root),
            "residual_analysis": source_entry(args.residual_analysis, root),
            "baseline_gap_summary": source_entry(args.baseline_gap_summary, root),
            "handoff_manifest": source_entry(args.handoff_manifest, root),
            "target_summary": source_entry(args.target_summary, root),
        },
        "settings": {
            "frames": args.frames,
            "spp": args.spp,
            "fps": args.fps,
            "keyframes": args.keyframes,
            "max_abs_gap_limit": args.max_abs_gap_limit,
        },
        "variants": results,
        "fit": fit,
        "next": args.next,
    }
    summary_path = os.path.join(args.out_dir, "residual_response_energy_sweep_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status=ready variants={len(results)} best_safe={fit.get('best_safe_candidate')} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a narrow Mitsuba residual-response energy sweep")
    parser.add_argument("base_export")
    parser.add_argument("residual_analysis")
    parser.add_argument("baseline_gap_summary")
    parser.add_argument("handoff_manifest")
    parser.add_argument("target_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--variant", action="append")
    parser.add_argument("--reference-candidate", nargs=3, action="append", metavar=("LABEL", "GAP_SUMMARY", "EXPORT_MANIFEST"))
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--spp", type=int, default=12)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-gap-limit", type=float, default=177.0)
    parser.add_argument("--render-python", default=default_render_python())
    parser.add_argument("--llvm-dll", default=os.path.join("build", "envs", "llvm18_runtime", "Library", "bin", "LLVM-C.dll"))
    parser.add_argument("--report-slug", default="residual_response_energy_sweep")
    parser.add_argument("--report")
    parser.add_argument("--title", default="S456 Mitsuba Residual Response Energy Sweep")
    parser.add_argument("--next", default="Use the best safe energy sweep candidate as the current residual response preset.")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_gap_limit <= 0.0:
        parser.error("max-abs-gap-limit must be positive")
    args.reference_candidate = [
        parse_reference_candidate(item) for item in args.reference_candidate or []
    ]
    run_sweep(args)


if __name__ == "__main__":
    main()
