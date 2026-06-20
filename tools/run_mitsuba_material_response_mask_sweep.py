#!/usr/bin/env python
"""Run a bounded Mitsuba material-response mask calibration sweep."""

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
        "label": "mrms1_tiny_neutral",
        "base_alpha": 0.02,
        "strength_alpha_gain": 0.90,
        "scattering_alpha_gain": 0.25,
        "albedo_alpha_gain": 0.20,
        "bbox_pad": 0.0,
        "blur_pad_scale": 0.15,
        "blur_radius": 0.8,
        "dilate_radius": 0,
        "face_limit": 240,
        "response_alpha": 0.006,
        "response_bin_count": 1,
        "response_specular_reflectance": "0.30,0.36,0.46",
        "response_specular_transmittance": "0.98,0.99,1.00",
    },
    {
        "label": "mrms2_core_soft",
        "base_alpha": 0.04,
        "strength_alpha_gain": 1.10,
        "scattering_alpha_gain": 0.35,
        "albedo_alpha_gain": 0.30,
        "bbox_pad": 0.5,
        "blur_pad_scale": 0.25,
        "blur_radius": 1.2,
        "dilate_radius": 0,
        "face_limit": 360,
        "response_alpha": 0.008,
        "response_bin_count": 1,
        "response_specular_reflectance": "0.34,0.42,0.56",
        "response_specular_transmittance": "0.94,0.97,1.00",
    },
    {
        "label": "mrms3_narrow_bins",
        "base_alpha": 0.03,
        "strength_alpha_gain": 1.20,
        "scattering_alpha_gain": 0.40,
        "albedo_alpha_gain": 0.40,
        "bbox_pad": 0.5,
        "blur_pad_scale": 0.30,
        "blur_radius": 1.5,
        "dilate_radius": 0,
        "face_limit": 450,
        "response_alpha": 0.008,
        "response_bin_count": 2,
        "response_specular_reflectance": "0.34,0.42,0.56",
        "response_specular_transmittance": "0.94,0.97,1.00",
        "response_bin_alpha_strong": 0.010,
        "response_bin_alpha_weak": 0.006,
        "response_bin_specular_reflectance_strong": "0.38,0.48,0.65",
        "response_bin_specular_reflectance_weak": "0.28,0.34,0.44",
        "response_bin_specular_transmittance_strong": "0.90,0.95,1.00",
        "response_bin_specular_transmittance_weak": "0.98,0.99,1.00",
    },
    {
        "label": "mrms4_minimal_clear",
        "base_alpha": 0.015,
        "strength_alpha_gain": 0.70,
        "scattering_alpha_gain": 0.15,
        "albedo_alpha_gain": 0.12,
        "bbox_pad": 0.0,
        "blur_pad_scale": 0.0,
        "blur_radius": 0.4,
        "dilate_radius": 0,
        "face_limit": 160,
        "response_alpha": 0.006,
        "response_bin_count": 1,
        "response_specular_reflectance": "0.24,0.28,0.34",
        "response_specular_transmittance": "1.00,1.00,1.00",
    },
]


VARIANT_KEYS = set(DEFAULT_VARIANTS[0]) | {
    "response_bin_alpha_strong",
    "response_bin_alpha_weak",
    "response_bin_specular_reflectance_strong",
    "response_bin_specular_reflectance_weak",
    "response_bin_specular_transmittance_strong",
    "response_bin_specular_transmittance_weak",
}


FLOAT_KEYS = {
    "base_alpha",
    "strength_alpha_gain",
    "scattering_alpha_gain",
    "albedo_alpha_gain",
    "bbox_pad",
    "blur_pad_scale",
    "blur_radius",
    "response_alpha",
    "response_bin_alpha_strong",
    "response_bin_alpha_weak",
}


INT_KEYS = {
    "dilate_radius",
    "face_limit",
    "response_bin_count",
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
        if key not in VARIANT_KEYS:
            raise argparse.ArgumentTypeError(f"unsupported variant key: {key}")
        if key in FLOAT_KEYS:
            variant[key] = float(raw)
        elif key in INT_KEYS:
            variant[key] = int(raw)
        else:
            variant[key] = raw
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


def variant_arg(cmd, name, value):
    if value is None:
        return
    cmd.extend([name, str(value)])


def run_variant(args, variant, root):
    label = variant["label"]
    base_dir = os.path.join(args.out_dir, label)
    mask_dir = os.path.join(base_dir, "mask_source")
    split_dir = os.path.join(base_dir, "split_export")
    validate_dir = os.path.join(base_dir, "validation")
    render_dir = os.path.join(base_dir, "render")
    gap_dir = os.path.join(base_dir, "target_gap")
    prefix = f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_{label}"
    reports = {
        "mask": os.path.join("docs", "reports", f"{prefix}_mask_{args.stage_id}.md"),
        "split": os.path.join("docs", "reports", f"{prefix}_split_{args.stage_id}.md"),
        "validate": os.path.join("docs", "reports", f"{prefix}_validate_{args.stage_id}.md"),
        "render": os.path.join("docs", "reports", f"{prefix}_render_{args.stage_id}.md"),
        "target_gap": os.path.join("docs", "reports", f"{prefix}_target_gap_{args.stage_id}.md"),
    }
    mask_cmd = [
        sys.executable,
        "tools/build_mitsuba_material_response_mask_source.py",
        args.material_response_contract,
        args.aov_summary,
        mask_dir,
        "--base-alpha",
        str(variant["base_alpha"]),
        "--strength-alpha-gain",
        str(variant["strength_alpha_gain"]),
        "--scattering-alpha-gain",
        str(variant["scattering_alpha_gain"]),
        "--albedo-alpha-gain",
        str(variant["albedo_alpha_gain"]),
        "--bbox-pad",
        str(variant["bbox_pad"]),
        "--blur-pad-scale",
        str(variant["blur_pad_scale"]),
        "--blur-radius",
        str(variant["blur_radius"]),
        "--dilate-radius",
        str(variant["dilate_radius"]),
        "--report",
        reports["mask"],
        "--title",
        f"{args.stage_label} Mitsuba Material Response Mask {label}",
        "--next",
        f"Feed {label} into split-water material response.",
    ]
    split_cmd = [
        sys.executable,
        "tools/split_mitsuba_water_mask_material.py",
        args.base_export,
        os.path.join(mask_dir, "material_response_mask_source_summary.json"),
        split_dir,
        "--allow-empty-mask-frames",
        "--use-current-water-shape",
        "--response-shape-id-prefix",
        f"lsfs_{args.stage_id}_{label}_water_mask_material",
        "--remainder-shape-id-prefix",
        f"lsfs_{args.stage_id}_{label}_water_remainder",
        "--response-bsdf-id-prefix",
        f"lsfs_{args.stage_id}_{label}_water_surface_masked_response",
        "--face-limit",
        str(variant["face_limit"]),
        "--response-alpha",
        str(variant["response_alpha"]),
        "--response-bin-count",
        str(variant["response_bin_count"]),
        "--response-specular-reflectance",
        str(variant["response_specular_reflectance"]),
        "--response-specular-transmittance",
        str(variant["response_specular_transmittance"]),
        "--report",
        reports["split"],
        "--title",
        f"{args.stage_label} Mitsuba Material Response Mask Split {label}",
        "--next",
        f"Validate, render, and compare {label}.",
    ]
    for key, option in (
        ("response_bin_alpha_strong", "--response-bin-alpha-strong"),
        ("response_bin_alpha_weak", "--response-bin-alpha-weak"),
        ("response_bin_specular_reflectance_strong", "--response-bin-specular-reflectance-strong"),
        ("response_bin_specular_reflectance_weak", "--response-bin-specular-reflectance-weak"),
        ("response_bin_specular_transmittance_strong", "--response-bin-specular-transmittance-strong"),
        ("response_bin_specular_transmittance_weak", "--response-bin-specular-transmittance-weak"),
    ):
        variant_arg(split_cmd, option, variant.get(key))
    validate_cmd = [
        sys.executable,
        "tools/validate_mitsuba_xml_export.py",
        os.path.join(split_dir, "mitsuba_export.json"),
        "--out",
        os.path.join(validate_dir, "validation.json"),
        "--report",
        reports["validate"],
        "--title",
        f"{args.stage_label} Mitsuba Material Response Mask Split {label} Validation",
        "--next",
        f"Render {label}.",
    ]
    render_cmd = [
        args.render_python,
        "tools/render_mitsuba_xml_export.py",
        os.path.join(split_dir, "mitsuba_export.json"),
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
        f"{args.stage_label} Mitsuba Material Response Mask Split {label} Render",
        "--next",
        f"Compare {label} target gap.",
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
        f"{args.stage_label} Mitsuba Material Response Mask Split {label} Target Gap",
        "--next",
        f"Rank {label} against the material-response mask sweep.",
    ]
    command_results = []
    for step, cmd in (
        ("mask", mask_cmd),
        ("split", split_cmd),
        ("validate", validate_cmd),
        ("render", render_cmd),
        ("target_gap", compare_cmd),
    ):
        result = run_cmd(cmd, root)
        command_results.append({"step": step, **result})
        require_success(f"{label}:{step}", result)
    mask_summary_path = os.path.join(mask_dir, "material_response_mask_source_summary.json")
    split_export_path = os.path.join(split_dir, "mitsuba_export.json")
    render_manifest_path = os.path.join(render_dir, "mitsuba_render.json")
    gap_path = os.path.join(gap_dir, "renderer_target_gap_summary.json")
    mask = read_json(mask_summary_path)
    split = read_json(split_export_path)
    render = read_json(render_manifest_path)
    gap = read_json(gap_path)
    return {
        "label": label,
        "variant": variant,
        "paths": {
            "mask_source": posix_rel(resolve_path(mask_summary_path), root),
            "split_export": posix_rel(resolve_path(split_export_path), root),
            "validation": posix_rel(resolve_path(os.path.join(validate_dir, "validation.json")), root),
            "render": posix_rel(resolve_path(render_manifest_path), root),
            "target_gap": posix_rel(resolve_path(gap_path), root),
        },
        "reports": reports,
        "checks": {
            "mask": mask.get("checks") or {},
            "split": split.get("checks") or {},
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
        f"{args.stage_label} Mitsuba Material Response Mask Gap Gallery",
        "--report",
        report,
        "--next",
        "Use this gallery to choose the next material-response mask calibration direction.",
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


def run_calibration_summary(args, results, root):
    out_dir = os.path.join(args.out_dir, "response_calibration")
    report = os.path.join("docs", "reports", f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_calibration_{args.stage_id}.md")
    cmd = [
        sys.executable,
        "tools/summarize_mitsuba_response_calibration.py",
        out_dir,
        "--title",
        f"{args.stage_label} Mitsuba Material Response Mask Calibration",
        "--report",
        report,
        "--next",
        "Use the Pareto summary to decide whether to narrow the mask further or return to light-only native controls.",
    ]
    for label, path in args.reference_candidate:
        cmd.extend(["--candidate", f"{label}={path}"])
    for item in results:
        cmd.extend(["--candidate", f"{item['label']}={resolve_path(item['paths']['target_gap'])}"])
    result = run_cmd(cmd, root)
    require_success("calibration_summary", result)
    summary_path = os.path.join(out_dir, "response_calibration_summary.json")
    summary = read_json(summary_path)
    return {
        "path": posix_rel(resolve_path(summary_path), root),
        "report": report,
        "sha256": sha256_file(summary_path),
        "best_max_gap": summary.get("best_max_gap"),
        "best_mean_gap": summary.get("best_mean_gap"),
        "pareto_count": summary.get("pareto_count"),
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
        "| Candidate | Mask Max Cov | Response Faces | Mean Gap MAD | Max Gap MAD | Max Gap | Target Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("variants") or []:
        mask = item["checks"]["mask"]
        split = item["checks"]["split"]
        gap = item["checks"]["target_gap"]
        lines.append(
            f"| `{item['label']}` | {mask.get('max_mask_coverage')} | "
            f"{split.get('response_faces')} | {gap.get('mean_gap_mean_abs_diff')} | "
            f"{gap.get('max_gap_mean_abs_diff')} | {gap.get('max_gap_max_abs_diff')} | "
            f"`{item['paths']['target_gap']}` |"
        )
    lines.extend([
        "",
        "## Summaries",
        "",
        f"- Gap gallery: `{(summary.get('gap_gallery') or {}).get('path')}`",
        f"- Gap gallery report: `{(summary.get('gap_gallery') or {}).get('report')}`",
        f"- Gap gallery best: `{(summary.get('gap_gallery') or {}).get('best_candidate')}`",
        f"- Calibration summary: `{(summary.get('calibration_summary') or {}).get('path')}`",
        f"- Calibration report: `{(summary.get('calibration_summary') or {}).get('report')}`",
        f"- Calibration best max-gap: `{(summary.get('calibration_summary') or {}).get('best_max_gap')}`",
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
    args.material_response_contract = require_file(resolve_path(args.material_response_contract), "material response contract")
    args.aov_summary = require_file(resolve_path(args.aov_summary), "AOV summary")
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
    calibration_summary = run_calibration_summary(args, results, root)
    summary = {
        "schema": "lsfs_mitsuba_material_response_mask_sweep",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "sources": {
            "base_export": source_entry(args.base_export, root),
            "material_response_contract": source_entry(args.material_response_contract, root),
            "aov_summary": source_entry(args.aov_summary, root),
            "handoff_manifest": source_entry(args.handoff_manifest, root),
            "target_summary": source_entry(args.target_summary, root),
        },
        "settings": {
            "frames": args.frames,
            "spp": args.spp,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "reference_candidates": args.reference_candidate,
        "variants": results,
        "gap_gallery": gap_gallery,
        "calibration_summary": calibration_summary,
        "next": args.next,
    }
    summary_path = os.path.join(args.out_dir, "material_response_mask_sweep_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status=ready variants={len(results)} gallery_best={gap_gallery.get('best_candidate')} "
        f"calibration_best={calibration_summary.get('best_max_gap')} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a bounded Mitsuba material-response mask calibration sweep")
    parser.add_argument("base_export")
    parser.add_argument("material_response_contract")
    parser.add_argument("aov_summary")
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
    parser.add_argument("--report-slug", default="material_response_mask_sweep")
    parser.add_argument("--stage-id", default="s484")
    parser.add_argument("--stage-label", default="S484")
    parser.add_argument("--report")
    parser.add_argument("--title", default="S484 Mitsuba Material Response Mask Sweep")
    parser.add_argument("--next", default="Use this sweep to decide whether material masks should stay active or the native path should return to light-only controls.")
    args = parser.parse_args(argv)
    if args.frames <= 0:
        parser.error("frames must be positive")
    if args.spp <= 0:
        parser.error("spp must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    args.reference_candidate = [
        parse_reference(item) for item in args.reference_candidate or []
    ]
    run_sweep(args)


if __name__ == "__main__":
    main()
