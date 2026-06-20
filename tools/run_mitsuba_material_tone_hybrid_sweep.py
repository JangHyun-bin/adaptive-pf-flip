#!/usr/bin/env python
"""Run a bounded Mitsuba material/tone hybrid sweep."""

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
        "label": "mt1_soft_key",
        "secondary_channels": "spray,foam",
        "secondary_reflectance_drop": 0.08,
        "secondary_opacity_drop": 0.05,
        "water_alpha_drop": 0.08,
        "water_alpha_min": 0.004,
        "highlight_key_light_radiance": "0.025,0.032,0.042",
        "highlight_key_light_strength": 0.5,
    },
    {
        "label": "mt2_key_alpha",
        "secondary_channels": "spray,foam",
        "secondary_reflectance_drop": 0.0,
        "secondary_opacity_drop": 0.0,
        "water_alpha_drop": 0.10,
        "water_alpha_min": 0.004,
        "highlight_key_light_radiance": "0.035,0.045,0.060",
        "highlight_key_light_strength": 0.75,
    },
    {
        "label": "mt3_secondary_dim",
        "secondary_channels": "spray,foam",
        "secondary_reflectance_drop": 0.14,
        "secondary_opacity_drop": 0.09,
        "water_alpha_drop": 0.04,
        "water_alpha_min": 0.004,
        "highlight_key_light_radiance": "0.012,0.016,0.022",
        "highlight_key_light_strength": 0.4,
    },
    {
        "label": "mt4_balanced",
        "secondary_channels": "spray,foam",
        "secondary_reflectance_drop": 0.10,
        "secondary_opacity_drop": 0.06,
        "water_alpha_drop": 0.12,
        "water_alpha_min": 0.004,
        "highlight_key_light_radiance": "0.032,0.042,0.056",
        "highlight_key_light_strength": 0.65,
    },
]


VARIANT_KEYS = {
    "secondary_channels",
    "secondary_reflectance_drop",
    "secondary_opacity_drop",
    "water_alpha_drop",
    "water_alpha_min",
    "highlight_key_light_radiance",
    "highlight_key_light_strength",
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
        if key in {"secondary_channels", "highlight_key_light_radiance"}:
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
    shot_dir = os.path.join(args.out_dir, label)
    validation_dir = os.path.join(args.out_dir, f"{label}_validation")
    render_dir = os.path.join(args.out_dir, f"{label}_render")
    gap_dir = os.path.join(args.out_dir, f"{label}_target_gap")
    report_prefix = f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_{label}"
    reports = {
        "export": os.path.join("docs", "reports", f"{report_prefix}_export_{args.stage_id}.md"),
        "validate": os.path.join("docs", "reports", f"{report_prefix}_validate_{args.stage_id}.md"),
        "render": os.path.join("docs", "reports", f"{report_prefix}_render_{args.stage_id}.md"),
        "target_gap": os.path.join("docs", "reports", f"{report_prefix}_target_gap_{args.stage_id}.md"),
    }
    export_cmd = [
        sys.executable,
        "tools/modulate_mitsuba_material_response.py",
        args.base_export,
        args.channel_mask_source,
        args.highlight_mask_source,
        shot_dir,
        "--frames",
        str(args.frames),
        "--secondary-channels",
        str(variant["secondary_channels"]),
        "--secondary-reflectance-drop",
        str(variant["secondary_reflectance_drop"]),
        "--secondary-opacity-drop",
        str(variant["secondary_opacity_drop"]),
        "--water-alpha-drop",
        str(variant["water_alpha_drop"]),
        "--water-alpha-min",
        str(variant["water_alpha_min"]),
        "--highlight-key-light-radiance",
        str(variant["highlight_key_light_radiance"]),
        "--highlight-key-light-strength",
        str(variant["highlight_key_light_strength"]),
        "--report",
        reports["export"],
        "--title",
        f"{args.stage_label} Mitsuba Material Tone {label} Export",
        "--next",
        f"Validate, render, and compare {args.stage_label} {label}.",
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
        f"{args.stage_label} Mitsuba Material Tone {label} Validation",
        "--next",
        f"Render {args.stage_label} {label}.",
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
        f"{args.stage_label} Mitsuba Material Tone {label} Render",
        "--next",
        f"Compare {args.stage_label} {label} target gap.",
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
        f"{args.stage_label} Mitsuba Material Tone {label} Target Gap",
        "--next",
        f"Rank {args.stage_label} {label} against the material/tone sweep.",
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
    export = read_json(export_path)
    gap = read_json(gap_path)
    return {
        "label": label,
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


def run_gallery(args, results, root):
    gallery_dir = os.path.join(args.out_dir, "decision_gallery")
    gallery_report = os.path.join("docs", "reports", f"cinematic_larger_external_renderer_mitsuba_{args.report_slug}_decision_gallery_{args.stage_id}.md")
    cmd = [
        sys.executable,
        "tools/build_mitsuba_gap_summary_gallery.py",
        gallery_dir,
        "--title",
        f"{args.stage_label} Mitsuba Material Tone Decision Gallery",
        "--report",
        gallery_report,
        "--next",
        "Use this gallery to decide whether material/tone modulation should replace the residual-response preset.",
    ]
    for reference in args.reference_candidate or []:
        cmd.extend(["--candidate", f"{reference['label']}={reference['gap_summary']}"])
    for result in results:
        cmd.extend(["--candidate", f"{result['label']}={resolve_path(result['paths']['target_gap'])}"])
    gallery_result = run_cmd(cmd, root)
    require_success("decision_gallery", gallery_result)
    gallery_summary_path = os.path.join(gallery_dir, "gap_summary_gallery.json")
    gallery_summary = read_json(gallery_summary_path)
    return {
        "path": posix_rel(resolve_path(gallery_summary_path), root),
        "report": gallery_report,
        "sha256": sha256_file(gallery_summary_path),
        "best_candidate": gallery_summary.get("best_candidate"),
        "best_max_gap_mean_abs_diff": gallery_summary.get("best_max_gap_mean_abs_diff"),
        "command": gallery_result,
    }


def parse_reference_candidate(value):
    if len(value) != 2:
        raise argparse.ArgumentTypeError("reference-candidate requires LABEL GAP_SUMMARY")
    return {"label": value[0], "gap_summary": value[1]}


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
        "## Inputs",
        "",
        f"- Base export: `{summary['sources']['base_export']['repo_path']}`",
        f"- Channel mask: `{summary['sources']['channel_mask_source']['repo_path']}`",
        f"- Highlight mask: `{summary['sources']['highlight_mask_source']['repo_path']}`",
        "",
        "## Variants",
        "",
        "| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Key Lights | Water Alpha Replacements | Target Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("variants") or []:
        gap = item["checks"]["target_gap"]
        export = item["checks"]["export"]
        lines.append(
            f"| `{item['label']}` | {gap.get('mean_gap_mean_abs_diff')} | "
            f"{gap.get('max_gap_mean_abs_diff')} | {gap.get('max_gap_max_abs_diff')} | "
            f"{export.get('key_lights_inserted')} | {export.get('water_alpha_replacements')} | "
            f"`{item['paths']['target_gap']}` |"
        )
    gallery = summary.get("decision_gallery") or {}
    lines.extend([
        "",
        "## Decision Gallery",
        "",
        f"- Summary: `{gallery.get('path')}`",
        f"- Report: `{gallery.get('report')}`",
        f"- Best candidate: `{gallery.get('best_candidate')}`",
        f"- Best max gap MAD: `{gallery.get('best_max_gap_mean_abs_diff')}`",
        "",
        "## Next",
        "",
        summary.get("next", ""),
        "",
    ])
    return "\n".join(lines)


def run_sweep(args):
    root = os.getcwd()
    args.base_export = require_file(resolve_path(args.base_export), "base export")
    args.channel_mask_source = require_file(resolve_path(args.channel_mask_source), "channel mask source")
    args.highlight_mask_source = require_file(resolve_path(args.highlight_mask_source), "highlight mask source")
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
    gallery = run_gallery(args, results, root)
    summary = {
        "schema": "lsfs_mitsuba_material_tone_hybrid_sweep",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "sources": {
            "base_export": source_entry(args.base_export, root),
            "channel_mask_source": source_entry(args.channel_mask_source, root),
            "highlight_mask_source": source_entry(args.highlight_mask_source, root),
            "handoff_manifest": source_entry(args.handoff_manifest, root),
            "target_summary": source_entry(args.target_summary, root),
        },
        "settings": {
            "frames": args.frames,
            "spp": args.spp,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "variants": results,
        "decision_gallery": gallery,
        "next": args.next,
    }
    summary_path = os.path.join(args.out_dir, "material_tone_hybrid_sweep_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status=ready variants={len(results)} best={gallery.get('best_candidate')} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a bounded Mitsuba material/tone hybrid sweep")
    parser.add_argument("base_export")
    parser.add_argument("channel_mask_source")
    parser.add_argument("highlight_mask_source")
    parser.add_argument("handoff_manifest")
    parser.add_argument("target_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--variant", action="append")
    parser.add_argument("--reference-candidate", nargs=2, action="append", metavar=("LABEL", "GAP_SUMMARY"))
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--spp", type=int, default=12)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--render-python", default=default_render_python())
    parser.add_argument("--llvm-dll", default=os.path.join("build", "envs", "llvm18_runtime", "Library", "bin", "LLVM-C.dll"))
    parser.add_argument("--report-slug", default="material_tone_hybrid_sweep")
    parser.add_argument("--stage-id", default="s459")
    parser.add_argument("--stage-label", default="S459")
    parser.add_argument("--report")
    parser.add_argument("--title", default="S459 Mitsuba Material Tone Hybrid Sweep")
    parser.add_argument("--next", default="Use this sweep to decide whether broader material/tone modulation should replace the residual-response preset.")
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
        parse_reference_candidate(item) for item in args.reference_candidate or []
    ]
    run_sweep(args)


if __name__ == "__main__":
    main()
