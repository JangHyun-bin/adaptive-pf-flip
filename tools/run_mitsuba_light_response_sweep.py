#!/usr/bin/env python
"""Run a bounded Mitsuba light/glint response calibration sweep."""

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
        "label": "lrs0_s480_default",
        "anchor_limit": 8,
        "vertex_stride": 1,
        "bbox_pad": 18.0,
        "max_nearest_screen_distance": 48.0,
        "outside_bbox_penalty": 64.0,
        "world_average_count": 8,
        "radius": 0.045,
        "min_radius": 0.018,
        "max_radius": 0.13,
        "radius_weight_base": 0.8,
        "radius_weight_scale": 1.4,
        "y_lift": 0.035,
        "radiance": "0.55,0.70,0.95",
        "radiance_scale": 1.0,
        "radiance_weight_base": 0.65,
        "radiance_weight_scale": 1.6,
    },
    {
        "label": "lrs1_warm_compact",
        "anchor_limit": 8,
        "vertex_stride": 1,
        "bbox_pad": 12.0,
        "max_nearest_screen_distance": 34.0,
        "outside_bbox_penalty": 58.0,
        "world_average_count": 6,
        "radius": 0.038,
        "min_radius": 0.014,
        "max_radius": 0.10,
        "radius_weight_base": 0.7,
        "radius_weight_scale": 1.1,
        "y_lift": 0.026,
        "radiance": "0.64,0.72,0.86",
        "radiance_scale": 0.85,
        "radiance_weight_base": 0.60,
        "radiance_weight_scale": 1.35,
    },
    {
        "label": "lrs2_bright_glint",
        "anchor_limit": 8,
        "vertex_stride": 1,
        "bbox_pad": 10.0,
        "max_nearest_screen_distance": 30.0,
        "outside_bbox_penalty": 62.0,
        "world_average_count": 4,
        "radius": 0.032,
        "min_radius": 0.012,
        "max_radius": 0.085,
        "radius_weight_base": 0.65,
        "radius_weight_scale": 0.95,
        "y_lift": 0.030,
        "radiance": "0.72,0.86,1.14",
        "radiance_scale": 1.35,
        "radiance_weight_base": 0.70,
        "radiance_weight_scale": 1.75,
    },
    {
        "label": "lrs3_soft_area",
        "anchor_limit": 8,
        "vertex_stride": 1,
        "bbox_pad": 24.0,
        "max_nearest_screen_distance": 58.0,
        "outside_bbox_penalty": 72.0,
        "world_average_count": 12,
        "radius": 0.065,
        "min_radius": 0.022,
        "max_radius": 0.18,
        "radius_weight_base": 0.85,
        "radius_weight_scale": 1.65,
        "y_lift": 0.026,
        "radiance": "0.46,0.60,0.82",
        "radiance_scale": 0.75,
        "radiance_weight_base": 0.58,
        "radiance_weight_scale": 1.20,
    },
    {
        "label": "lrs4_sparse_spec",
        "anchor_limit": 4,
        "vertex_stride": 1,
        "bbox_pad": 8.0,
        "max_nearest_screen_distance": 26.0,
        "outside_bbox_penalty": 60.0,
        "world_average_count": 4,
        "radius": 0.028,
        "min_radius": 0.010,
        "max_radius": 0.072,
        "radius_weight_base": 0.58,
        "radius_weight_scale": 0.85,
        "y_lift": 0.032,
        "radiance": "0.82,0.98,1.32",
        "radiance_scale": 1.60,
        "radiance_weight_base": 0.75,
        "radiance_weight_scale": 1.90,
    },
]


VARIANT_KEYS = set(DEFAULT_VARIANTS[0])
INT_KEYS = {"anchor_limit", "vertex_stride", "world_average_count"}
STRING_KEYS = {"label", "radiance"}


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
        if "=" in token and key in VARIANT_KEYS:
            parts.append(token)
        elif parts:
            parts[-1] += "," + token
        else:
            raise argparse.ArgumentTypeError(f"variant setting must be key=value: {token}")
    for part in parts:
        key, raw = part.split("=", 1)
        key = key.strip().replace("-", "_")
        raw = raw.strip()
        if key not in VARIANT_KEYS or key == "label":
            raise argparse.ArgumentTypeError(f"unsupported variant key: {key}")
        if key in INT_KEYS:
            variant[key] = int(raw)
        elif key in STRING_KEYS:
            variant[key] = raw
        else:
            variant[key] = float(raw)
    missing = set(DEFAULT_VARIANTS[0]).difference(variant)
    if missing:
        raise argparse.ArgumentTypeError(f"{label}: missing settings {sorted(missing)}")
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


def run_variant(args, variant, root):
    label = variant["label"]
    base_dir = os.path.join(args.out_dir, label)
    export_dir = os.path.join(base_dir, "light_export")
    validate_dir = os.path.join(base_dir, "validation")
    render_dir = os.path.join(base_dir, "render")
    gap_dir = os.path.join(base_dir, "target_gap")
    prefix = f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_{label}"
    reports = {
        "export": os.path.join("docs", "reports", f"{prefix}_export_{args.stage_id}.md"),
        "validate": os.path.join("docs", "reports", f"{prefix}_validate_{args.stage_id}.md"),
        "render": os.path.join("docs", "reports", f"{prefix}_render_{args.stage_id}.md"),
        "target_gap": os.path.join("docs", "reports", f"{prefix}_target_gap_{args.stage_id}.md"),
    }
    export_cmd = [
        sys.executable,
        "tools/add_mitsuba_light_response_contract.py",
        args.base_export,
        args.light_response_contract,
        export_dir,
        "--frames",
        str(args.frames),
        "--anchor-limit",
        str(variant["anchor_limit"]),
        "--vertex-stride",
        str(variant["vertex_stride"]),
        "--bbox-pad",
        str(variant["bbox_pad"]),
        "--max-nearest-screen-distance",
        str(variant["max_nearest_screen_distance"]),
        "--outside-bbox-penalty",
        str(variant["outside_bbox_penalty"]),
        "--world-average-count",
        str(variant["world_average_count"]),
        "--radius",
        str(variant["radius"]),
        "--min-radius",
        str(variant["min_radius"]),
        "--max-radius",
        str(variant["max_radius"]),
        "--radius-weight-base",
        str(variant["radius_weight_base"]),
        "--radius-weight-scale",
        str(variant["radius_weight_scale"]),
        "--y-lift",
        str(variant["y_lift"]),
        "--radiance",
        str(variant["radiance"]),
        "--radiance-scale",
        str(variant["radiance_scale"]),
        "--radiance-weight-base",
        str(variant["radiance_weight_base"]),
        "--radiance-weight-scale",
        str(variant["radiance_weight_scale"]),
        "--report",
        reports["export"],
        "--title",
        f"{args.stage_label} Mitsuba Light Response {label} Export",
        "--next",
        f"Validate, render, and compare {label}.",
        "--fail-on-review",
    ]
    if args.allow_missing_contract_frames:
        export_cmd.append("--allow-missing-contract-frames")
    validate_cmd = [
        sys.executable,
        "tools/validate_mitsuba_xml_export.py",
        os.path.join(export_dir, "mitsuba_export.json"),
        "--out",
        os.path.join(validate_dir, "validation.json"),
        "--report",
        reports["validate"],
        "--title",
        f"{args.stage_label} Mitsuba Light Response {label} Validation",
        "--next",
        f"Render {label}.",
    ]
    render_cmd = [
        args.render_python,
        "tools/render_mitsuba_xml_export.py",
        os.path.join(export_dir, "mitsuba_export.json"),
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
        f"{args.stage_label} Mitsuba Light Response {label} Render",
        "--next",
        f"Compare target gap for {label}.",
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
        f"{args.stage_label} Mitsuba Light Response {label} Target Gap",
        "--next",
        f"Rank {label} against the S485 light response sweep.",
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

    export_path = os.path.join(export_dir, "mitsuba_export.json")
    validation_path = os.path.join(validate_dir, "validation.json")
    render_path = os.path.join(render_dir, "mitsuba_render.json")
    gap_path = os.path.join(gap_dir, "renderer_target_gap_summary.json")
    export = read_json(export_path)
    render = read_json(render_path)
    gap = read_json(gap_path)
    return {
        "label": label,
        "variant": variant,
        "paths": {
            "export": posix_rel(resolve_path(export_path), root),
            "validation": posix_rel(resolve_path(validation_path), root),
            "render": posix_rel(resolve_path(render_path), root),
            "target_gap": posix_rel(resolve_path(gap_path), root),
        },
        "reports": reports,
        "checks": {
            "export": export.get("checks") or {},
            "consumer": export.get("light_response_contract_consumer") or {},
            "render": render.get("checks") or {},
            "target_gap": gap.get("checks") or {},
        },
        "commands": command_results,
    }


def run_gap_gallery(args, results, root):
    out_dir = os.path.join(args.out_dir, "gap_gallery")
    report = os.path.join("docs", "reports", f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_gap_gallery_{args.stage_id}.md")
    cmd = [
        sys.executable,
        "tools/build_mitsuba_gap_summary_gallery.py",
        out_dir,
        "--title",
        f"{args.stage_label} Mitsuba Light Response Gap Gallery",
        "--report",
        report,
        "--next",
        "Use this gallery to decide whether light/glint contract tuning can replace proxy response controls.",
    ]
    for label, path in args.reference_candidate:
        cmd.extend(["--candidate", f"{label}={path}"])
    for item in results:
        cmd.extend(["--candidate", f"{item['label']}={resolve_path(item['paths']['target_gap'])}"])
    result = run_cmd(cmd, root)
    require_success("gap_gallery", result)
    summary_path = os.path.join(out_dir, "gap_summary_gallery.json")
    summary = read_json(summary_path)
    return {
        "path": posix_rel(resolve_path(summary_path), root),
        "report": report,
        "sha256": sha256_file(summary_path),
        "best_candidate": summary.get("best_candidate"),
        "best_max_gap_mean_abs_diff": summary.get("best_max_gap_mean_abs_diff"),
        "command": result,
    }


def source_entry(path, root):
    resolved = require_file(resolve_path(path), "source")
    return {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
    }


def markdown_report(summary, summary_path, root):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Variants",
        "",
        "| Candidate | Lights | Localized | Radius | Radiance Scale | Mean Gap MAD | Max Gap MAD | Max Gap | Target Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("variants") or []:
        export = item["checks"]["export"]
        consumer = item["checks"]["consumer"]
        gap = item["checks"]["target_gap"]
        lines.append(
            f"| `{item['label']}` | {export.get('lights_inserted')} | "
            f"{export.get('localized_anchors')} | {consumer.get('radius')} | "
            f"{consumer.get('radiance_scale')} | {gap.get('mean_gap_mean_abs_diff')} | "
            f"{gap.get('max_gap_mean_abs_diff')} | {gap.get('max_gap_max_abs_diff')} | "
            f"`{item['paths']['target_gap']}` |"
        )
    lines.extend([
        "",
        "## Gallery",
        "",
        f"- Gap gallery: `{(summary.get('gap_gallery') or {}).get('path')}`",
        f"- Gap gallery report: `{(summary.get('gap_gallery') or {}).get('report')}`",
        f"- Gap gallery best: `{(summary.get('gap_gallery') or {}).get('best_candidate')}`",
        "",
        "## Next",
        "",
        summary.get("next", ""),
        "",
    ])
    return "\n".join(lines)


def parse_reference(value):
    if len(value) != 2:
        raise argparse.ArgumentTypeError("reference-candidate requires LABEL GAP_SUMMARY")
    return [value[0], value[1]]


def run_sweep(args):
    root = os.getcwd()
    args.base_export = require_file(resolve_path(args.base_export), "base export")
    args.light_response_contract = require_file(resolve_path(args.light_response_contract), "light response contract")
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
    gap_gallery = run_gap_gallery(args, results, root)
    summary = {
        "schema": "lsfs_mitsuba_light_response_sweep",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "sources": {
            "base_export": source_entry(args.base_export, root),
            "light_response_contract": source_entry(args.light_response_contract, root),
            "handoff_manifest": source_entry(args.handoff_manifest, root),
            "target_summary": source_entry(args.target_summary, root),
        },
        "settings": {
            "frames": args.frames,
            "spp": args.spp,
            "fps": args.fps,
            "keyframes": args.keyframes,
            "allow_missing_contract_frames": args.allow_missing_contract_frames,
        },
        "reference_candidates": args.reference_candidate,
        "variants": results,
        "gap_gallery": gap_gallery,
        "next": args.next,
    }
    summary_path = os.path.join(args.out_dir, "light_response_sweep_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status=ready variants={len(results)} gallery_best={gap_gallery.get('best_candidate')} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a bounded Mitsuba light/glint response calibration sweep")
    parser.add_argument("base_export")
    parser.add_argument("light_response_contract")
    parser.add_argument("handoff_manifest")
    parser.add_argument("target_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--variant", action="append")
    parser.add_argument("--reference-candidate", nargs=2, action="append", metavar=("LABEL", "GAP_SUMMARY"))
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--spp", type=int, default=1)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--render-python", default=default_render_python())
    parser.add_argument("--llvm-dll", default=os.path.join("build", "envs", "llvm18_runtime", "Library", "bin", "LLVM-C.dll"))
    parser.add_argument("--report-slug", default="light_response_sweep")
    parser.add_argument("--stage-id", default="s485")
    parser.add_argument("--stage-label", default="S485")
    parser.add_argument("--strict-contract-frames", action="store_true")
    parser.add_argument("--report")
    parser.add_argument("--title", default="S485 Mitsuba Light Response Sweep")
    parser.add_argument("--next", default="Use this sweep to decide whether native light/glint tuning can close the proxy-response gap.")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    args.allow_missing_contract_frames = not args.strict_contract_frames
    args.reference_candidate = [
        parse_reference(item) for item in args.reference_candidate or []
    ]
    run_sweep(args)


if __name__ == "__main__":
    main()
