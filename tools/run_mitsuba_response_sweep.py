#!/usr/bin/env python
"""Run a bounded Mitsuba local-response sweep."""

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
        "label": "sw1_compact_mid",
        "patch_limit": 18,
        "candidate_limit": 1800,
        "cluster_screen_radius": 26.0,
        "min_cluster_candidates": 1,
        "min_radius": 0.04,
        "base_radius": 0.09,
        "radius_per_sqrt_candidate": 0.009,
        "max_radius": 0.28,
        "aspect": 0.55,
        "y_lift": 0.026,
        "radiance": "0.62,0.80,1.08",
    },
    {
        "label": "sw2_compact_high",
        "patch_limit": 24,
        "candidate_limit": 2000,
        "cluster_screen_radius": 24.0,
        "min_cluster_candidates": 1,
        "min_radius": 0.035,
        "base_radius": 0.075,
        "radius_per_sqrt_candidate": 0.008,
        "max_radius": 0.24,
        "aspect": 0.52,
        "y_lift": 0.026,
        "radiance": "0.82,1.02,1.34",
    },
    {
        "label": "sw3_sparse_high",
        "patch_limit": 10,
        "candidate_limit": 1400,
        "cluster_screen_radius": 34.0,
        "min_cluster_candidates": 2,
        "min_radius": 0.055,
        "base_radius": 0.11,
        "radius_per_sqrt_candidate": 0.010,
        "max_radius": 0.34,
        "aspect": 0.58,
        "y_lift": 0.026,
        "radiance": "0.95,1.18,1.52",
    },
]


PATCH_KEYS = {
    "patch_limit",
    "candidate_limit",
    "cluster_screen_radius",
    "min_cluster_candidates",
    "min_radius",
    "base_radius",
    "radius_per_sqrt_candidate",
    "max_radius",
    "aspect",
    "y_lift",
    "radiance",
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
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("variant label cannot be empty")
    variant = {"label": label}
    parts = []
    for token in raw_settings.split(","):
        key = token.split("=", 1)[0].strip().replace("-", "_")
        if "=" in token and key in PATCH_KEYS:
            parts.append(token)
        elif parts:
            parts[-1] += "," + token
        else:
            raise argparse.ArgumentTypeError(f"variant setting must be key=value: {token}")
    for part in parts:
        if not part.strip():
            continue
        key, raw = part.split("=", 1)
        key = key.strip().replace("-", "_")
        raw = raw.strip()
        if key not in PATCH_KEYS:
            raise argparse.ArgumentTypeError(f"unsupported variant key: {key}")
        if key == "radiance":
            variant[key] = raw
        elif key in {"patch_limit", "candidate_limit", "min_cluster_candidates"}:
            variant[key] = int(raw)
        else:
            variant[key] = float(raw)
    return variant


def merged_variants(raw_variants):
    variants = [dict(item) for item in DEFAULT_VARIANTS] if not raw_variants else []
    variants.extend(parse_variant(item) for item in raw_variants or [])
    labels = set()
    for variant in variants:
        missing = PATCH_KEYS.difference(variant)
        if missing:
            raise SystemExit(f"{variant.get('label')}: missing settings {sorted(missing)}")
        label = variant["label"]
        if label in labels:
            raise SystemExit(f"duplicate variant label: {label}")
        labels.add(label)
    return variants


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


def run_variant(args, variant, root):
    label = variant["label"]
    shot_dir = os.path.join(args.out_dir, label)
    validation_dir = os.path.join(args.out_dir, f"{label}_validation")
    render_dir = os.path.join(args.out_dir, f"{label}_render")
    gap_dir = os.path.join(args.out_dir, f"{label}_target_gap")
    report_prefix = f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_{label}"
    reports = {
        "export": os.path.join("docs", "reports", f"{report_prefix}_export_s452.md"),
        "validate": os.path.join("docs", "reports", f"{report_prefix}_validate_s452.md"),
        "render": os.path.join("docs", "reports", f"{report_prefix}_render_s452.md"),
        "target_gap": os.path.join("docs", "reports", f"{report_prefix}_target_gap_s452.md"),
    }

    export_cmd = [
        sys.executable,
        "tools/add_mitsuba_water_mask_patch_emitters.py",
        args.base_export,
        args.mask_source,
        shot_dir,
        "--frames",
        str(args.frames),
        "--patch-limit",
        str(variant["patch_limit"]),
        "--candidate-limit",
        str(variant["candidate_limit"]),
        "--mask-threshold",
        str(args.mask_threshold),
        "--source-luma-min",
        str(args.source_luma_min),
        "--source-luma-max",
        str(args.source_luma_max),
        "--cluster-screen-radius",
        str(variant["cluster_screen_radius"]),
        "--min-cluster-candidates",
        str(variant["min_cluster_candidates"]),
        "--min-radius",
        str(variant["min_radius"]),
        "--base-radius",
        str(variant["base_radius"]),
        "--radius-per-sqrt-candidate",
        str(variant["radius_per_sqrt_candidate"]),
        "--max-radius",
        str(variant["max_radius"]),
        "--aspect",
        str(variant["aspect"]),
        "--y-lift",
        str(variant["y_lift"]),
        "--radiance",
        str(variant["radiance"]),
        "--report",
        reports["export"],
        "--title",
        f"S452 Mitsuba Response Sweep {label} Export",
        "--next",
        f"Validate, render, and compare S452 {label}.",
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
        f"S452 Mitsuba Response Sweep {label} Validation",
        "--next",
        f"Render S452 {label}.",
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
        f"S452 Mitsuba Response Sweep {label} Render",
        "--next",
        f"Compare S452 {label} target gap.",
    ]
    compare_cmd = [
        sys.executable,
        "tools/compare_mitsuba_renderer_target_gap.py",
        args.handoff_manifest,
        args.target_summary,
        gap_dir,
        "--actual-render-manifest",
        os.path.join(render_dir, "mitsuba_render.json"),
        "--report",
        reports["target_gap"],
        "--title",
        f"S452 Mitsuba Response Sweep {label} Target Gap",
        "--next",
        "Rank this sweep candidate against the current references.",
    ]

    steps = []
    for step, cmd in (
        ("export", export_cmd),
        ("validate", validate_cmd),
        ("render", render_cmd),
        ("target_gap", compare_cmd),
    ):
        result = run_cmd(cmd, root)
        require_success(f"{label} {step}", result)
        steps.append({"step": step, **result})

    gap_summary_path = os.path.join(gap_dir, "renderer_target_gap_summary.json")
    gap_summary = read_json(gap_summary_path)
    export_summary = read_json(os.path.join(shot_dir, "mitsuba_export.json"))
    return {
        "label": label,
        "variant": variant,
        "steps": steps,
        "reports": {key: posix_rel(resolve_path(path), root) for key, path in reports.items()},
        "paths": {
            "export": posix_rel(resolve_path(os.path.join(shot_dir, "mitsuba_export.json")), root),
            "validation": posix_rel(resolve_path(os.path.join(validation_dir, "mitsuba_export_validation.json")), root),
            "render": posix_rel(resolve_path(os.path.join(render_dir, "mitsuba_render.json")), root),
            "target_gap": posix_rel(resolve_path(gap_summary_path), root),
        },
        "checks": gap_summary.get("checks") or {},
        "export_checks": export_summary.get("checks") or {},
        "status": gap_summary.get("status"),
    }


def run_post_reports(args, candidates, root):
    candidate_args = []
    for raw in args.baseline:
        candidate_args.extend(["--candidate", raw])
    for item in candidates:
        candidate_args.extend(["--candidate", f"{item['label']}={resolve_path(item['paths']['target_gap'])}"])

    gallery_report = os.path.join("docs", "reports", f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_decision_gallery_s452.md")
    gallery_cmd = [
        sys.executable,
        "tools/build_mitsuba_gap_summary_gallery.py",
        os.path.join(args.out_dir, "decision_gallery"),
        *candidate_args,
        "--report",
        gallery_report,
        "--title",
        "S452 Mitsuba Response Sweep Decision Gallery",
        "--next",
        "Use this gallery and calibration table to pick the next bounded renderer response.",
    ]
    calibration_report = os.path.join("docs", "reports", f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_calibration_s452.md")
    calibration_cmd = [
        sys.executable,
        "tools/summarize_mitsuba_response_calibration.py",
        os.path.join(args.out_dir, "calibration"),
        *candidate_args,
        "--report",
        calibration_report,
        "--title",
        "S452 Mitsuba Response Sweep Calibration",
        "--next",
        "Promote only candidates that improve target gap without adding visible local-response artifacts.",
    ]
    outputs = []
    for step, cmd in (("decision_gallery", gallery_cmd), ("calibration", calibration_cmd)):
        result = run_cmd(cmd, root)
        require_success(step, result)
        outputs.append({"step": step, **result})
    return {
        "steps": outputs,
        "decision_gallery_report": posix_rel(resolve_path(gallery_report), root),
        "calibration_report": posix_rel(resolve_path(calibration_report), root),
    }


def markdown_report(summary, summary_path, root):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Candidates",
        "",
        "| Candidate | Status | Max Gap MAD | Mean Gap MAD | Max Gap | Patches | Report |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("candidates") or []:
        checks = item.get("checks") or {}
        export_checks = item.get("export_checks") or {}
        lines.append(
            f"| `{item['label']}` | `{item.get('status')}` | "
            f"{checks.get('max_gap_mean_abs_diff')} | {checks.get('mean_gap_mean_abs_diff')} | "
            f"{checks.get('max_gap_max_abs_diff')} | {export_checks.get('patches_inserted')} | "
            f"`{item['reports']['target_gap']}` |"
        )
    lines.extend([
        "",
        "## Aggregate Reports",
        "",
        f"- Decision gallery: `{summary['aggregate']['decision_gallery_report']}`",
        f"- Calibration: `{summary['aggregate']['calibration_report']}`",
        "",
        "## Next",
        "",
        summary.get("next", ""),
        "",
    ])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    args.base_export = require_file(args.base_export, "base export")
    args.mask_source = require_file(args.mask_source, "mask source")
    args.handoff_manifest = require_file(args.handoff_manifest, "handoff manifest")
    args.target_summary = require_file(args.target_summary, "target summary")
    args.llvm_dll = require_file(args.llvm_dll, "LLVM-C runtime DLL")
    args.out_dir = os.path.abspath(args.out_dir)
    args.render_python = resolve_path(args.render_python)
    if not os.path.isfile(args.render_python):
        raise SystemExit(f"Missing render Python: {args.render_python}")
    os.makedirs(args.out_dir, exist_ok=True)

    variants = merged_variants(args.variant)
    candidates = [run_variant(args, variant, root) for variant in variants]
    aggregate = run_post_reports(args, candidates, root)
    generated = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_response_sweep",
        "version": 1,
        "generated_utc": generated,
        "title": args.title,
        "status": "ready",
        "settings": {
            "frames": args.frames,
            "spp": args.spp,
            "mask_threshold": args.mask_threshold,
            "source_luma_min": args.source_luma_min,
            "source_luma_max": args.source_luma_max,
            "render_python": args.render_python,
            "llvm_dll": args.llvm_dll,
        },
        "sources": {
            "base_export": {
                "path": args.base_export,
                "repo_path": posix_rel(args.base_export, root),
                "sha256": sha256_file(args.base_export),
            },
            "mask_source": {
                "path": args.mask_source,
                "repo_path": posix_rel(args.mask_source, root),
                "sha256": sha256_file(args.mask_source),
            },
        },
        "candidates": candidates,
        "aggregate": aggregate,
        "next": args.next,
    }
    summary_path = os.path.join(args.out_dir, "response_sweep_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status=ready candidates={len(candidates)} "
        f"summary={summary_path} report={args.report or ''}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a bounded Mitsuba response sweep")
    parser.add_argument("base_export")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--handoff-manifest", required=True)
    parser.add_argument("--target-summary", required=True)
    parser.add_argument("--baseline", action="append", default=[])
    parser.add_argument("--variant", action="append", default=[])
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--spp", type=int, default=12)
    parser.add_argument("--mask-threshold", type=int, default=8)
    parser.add_argument("--source-luma-min", type=float, default=145.0)
    parser.add_argument("--source-luma-max", type=float, default=255.0)
    parser.add_argument("--render-python", default=default_render_python())
    parser.add_argument("--llvm-dll", default=os.path.join("build", "envs", "llvm18_runtime", "Library", "bin", "LLVM-C.dll"))
    parser.add_argument("--report")
    parser.add_argument("--report-slug", default="response_sweep")
    parser.add_argument("--title", default="S452 Mitsuba Response Sweep")
    parser.add_argument("--next", default="Use this sweep to select the next bounded renderer response candidate.")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.mask_threshold < 0 or args.mask_threshold > 255:
        parser.error("mask-threshold must be in [0, 255]")
    if args.source_luma_min < 0.0 or args.source_luma_max > 255.0:
        parser.error("source luma bounds must be in [0, 255]")
    if args.source_luma_min > args.source_luma_max:
        parser.error("source-luma-min cannot exceed source-luma-max")
    build(args)


if __name__ == "__main__":
    main()
