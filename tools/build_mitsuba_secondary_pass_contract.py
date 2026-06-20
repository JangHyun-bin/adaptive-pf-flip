#!/usr/bin/env python
"""Build a renderer-facing contract for the Mitsuba secondary overlay pass."""

import argparse
import os
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


def json_source(path, label, root):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, payload


def file_entry(path, label, root, role):
    resolved = require_file(path, label)
    return {
        "label": label,
        "role": role,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }


def optional_json_source(path, label, root):
    if not path:
        return None, {}
    return json_source(path, label, root)


def resolve_repo_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def collect_gallery_artifacts(overlay, root):
    gallery = overlay.get("gallery") or {}
    artifacts = []
    index = gallery.get("index_path") or gallery.get("index_repo_path")
    if index:
        artifacts.append(file_entry(index, "gallery index", root, "review_page"))
    for asset in gallery.get("assets") or []:
        if asset.get("label") == "Overlay GIF":
            artifacts.append(file_entry(asset.get("asset") or asset.get("repo_path"), "overlay gif", root, "animated_review"))
        elif asset.get("label", "").startswith("Overlay Strip"):
            artifacts.append(file_entry(asset.get("asset") or asset.get("repo_path"), asset.get("label"), root, "review_strip"))
    return artifacts


def build_frames(overlay, root):
    frames = []
    missing = []
    for frame in overlay.get("frames") or []:
        frame_id = frame.get("frame")
        paths = {
            "actual": frame.get("actual_repo_path"),
            "secondary_layer": frame.get("secondary_layer_repo_path"),
            "overlay": frame.get("overlay_repo_path"),
            "overlay_graded": frame.get("overlay_graded_repo_path"),
            "target": frame.get("target_repo_path"),
            "diff": frame.get("diff_repo_path"),
            "strip": frame.get("strip_repo_path"),
        }
        entries = {}
        for label, path in paths.items():
            resolved = resolve_repo_path(path)
            if not resolved or not os.path.isfile(resolved):
                missing.append({"frame": frame_id, "role": label, "path": path})
                entries[label] = {"status": "missing", "repo_path": path}
                continue
            entries[label] = {
                "status": "present",
                "path": resolved,
                "repo_path": posix_rel(resolved, root),
                "sha256": sha256_file(resolved),
                "size": os.path.getsize(resolved),
            }
        frames.append({
            "frame": frame_id,
            "output_frame": frame.get("output_frame"),
            "metrics": {
                "overlay_mean_abs_diff": frame.get("overlay_mean_abs_diff"),
                "overlay_max_abs_diff": frame.get("overlay_max_abs_diff"),
            },
            "expected_overlay_sha256": frame.get("overlay_graded_sha256"),
            "assets": entries,
        })
    return frames, missing


def build_contract(args):
    root = os.getcwd()
    overlay_source, overlay = json_source(args.overlay_summary, "secondary overlay summary", root)
    if overlay.get("schema") != "lsfs_mitsuba_render_secondary_overlay":
        raise SystemExit(f"{args.overlay_summary}: expected lsfs_mitsuba_render_secondary_overlay schema")
    source = overlay.get("source") or {}
    actual_source, actual_render = optional_json_source(
        args.actual_render_manifest or source.get("actual_render_manifest"),
        "actual Mitsuba render manifest",
        root,
    )
    handoff_source, handoff = optional_json_source(
        args.handoff_manifest or source.get("handoff_manifest"),
        "renderer handoff manifest",
        root,
    )
    target_source, target = optional_json_source(
        args.target_summary or source.get("target_summary"),
        "renderer target summary",
        root,
    )
    publish_source, publish = optional_json_source(args.publish_manifest, "publish manifest", root)
    frames, missing = build_frames(overlay, root)
    artifacts = collect_gallery_artifacts(overlay, root)
    checks = overlay.get("checks") or {}
    status = "ready" if (
        overlay.get("status") == "ready"
        and len(frames) == checks.get("frames")
        and not missing
        and checks.get("missing_references") == 0
        and checks.get("max_overlay_mean_abs_diff", 999.0) <= args.max_overlay_mean_abs_diff
    ) else "review"
    return {
        "schema": "lsfs_mitsuba_secondary_pass_contract",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "sources": {
            "overlay_summary": overlay_source,
            "actual_render_manifest": actual_source,
            "handoff_manifest": handoff_source,
            "target_summary": target_source,
            "publish_manifest": publish_source,
        },
        "public_review": {
            "url": publish.get("public_url"),
            "local_url": publish.get("local_url"),
            "status": publish.get("status"),
            "checks": publish.get("checks", []),
        },
        "secondary_pass_contract": {
            "base_renderer": "mitsuba",
            "base_render_schema": actual_render.get("schema"),
            "handoff_schema": handoff.get("schema"),
            "target_schema": target.get("schema"),
            "implementation_stage": "screen_space_secondary_overlay_hybrid",
            "base_input": "actual_mitsuba_preview",
            "secondary_input": "handoff_secondary_layer_rgba",
            "grade_input": "target_preview_grade_settings",
            "composition": "alpha_composite_secondary_layer_then_apply_grade",
            "current_role": "closest_visual_bridge",
            "future_renderer_expectation": [
                "replace the screen-space overlay with renderer-native secondary data",
                "preserve the same frame mapping and target-diff checks",
                "keep the S334 overlay as the regression target until a native pass beats it",
            ],
            "grade_settings": (overlay.get("settings") or {}).get("grade", {}),
        },
        "checks": {
            "frames": len(frames),
            "missing_frame_assets": len(missing),
            "overlay_frames": checks.get("frames"),
            "overlay_missing_references": checks.get("missing_references"),
            "mean_overlay_mean_abs_diff": checks.get("mean_overlay_mean_abs_diff"),
            "max_overlay_mean_abs_diff": checks.get("max_overlay_mean_abs_diff"),
            "max_overlay_max_abs_diff": checks.get("max_overlay_max_abs_diff"),
            "threshold_max_overlay_mean_abs_diff": args.max_overlay_mean_abs_diff,
            "public_url_present": bool(publish.get("public_url")),
        },
        "artifacts": artifacts,
        "missing_frame_assets": missing,
        "frames": frames,
        "next": args.next,
    }


def markdown_report(contract, out_path, root):
    checks = contract.get("checks") or {}
    public = contract.get("public_review") or {}
    lines = [
        f"# {contract['title']}",
        "",
        f"Generated UTC: `{contract['generated_utc']}`",
        f"Contract JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{contract['status']}`",
        f"Public URL: `{public.get('url') or 'n/a'}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing frame assets: `{checks.get('missing_frame_assets')}`",
        f"- Mean overlay MAD: `{checks.get('mean_overlay_mean_abs_diff')}`",
        f"- Max overlay MAD: `{checks.get('max_overlay_mean_abs_diff')}`",
        f"- Max overlay max diff: `{checks.get('max_overlay_max_abs_diff')}`",
        f"- Public URL present: `{checks.get('public_url_present')}`",
        "",
        "## Sources",
        "",
    ]
    for label, source in (contract.get("sources") or {}).items():
        if not source:
            continue
        lines.append(f"- {label}: `{source.get('repo_path')}` (`{source.get('schema') or 'n/a'}`)")
    lines.extend([
        "",
        "## Artifacts",
        "",
        "| Label | Role | Size | Path |",
        "| --- | --- | ---: | --- |",
    ])
    for item in contract.get("artifacts") or []:
        lines.append(f"| {item['label']} | `{item['role']}` | {format_bytes(item['size'])} | `{item['repo_path']}` |")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Overlay MAD | Overlay | Target |",
        "| ---: | ---: | ---: | --- | --- |",
    ])
    frames = contract.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        assets = frame.get("assets") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{(frame.get('metrics') or {}).get('overlay_mean_abs_diff')} | "
            f"`{(assets.get('overlay_graded') or {}).get('repo_path')}` | "
            f"`{(assets.get('target') or {}).get('repo_path')}` |"
        )
    if contract.get("missing_frame_assets"):
        lines.extend(["", "## Missing Frame Assets", ""])
        for item in contract["missing_frame_assets"]:
            lines.append(f"- frame `{item.get('frame')}` {item.get('role')}: `{item.get('path')}`")
    lines.extend(["", "## Next", "", contract.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Mitsuba secondary pass contract")
    parser.add_argument("overlay_summary")
    parser.add_argument("--actual-render-manifest")
    parser.add_argument("--handoff-manifest")
    parser.add_argument("--target-summary")
    parser.add_argument("--publish-manifest")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Pass Contract")
    parser.add_argument("--max-overlay-mean-abs-diff", type=float, default=20.0)
    parser.add_argument(
        "--next",
        default="Use this contract as the bridge target for a renderer-native secondary pass.",
    )
    args = parser.parse_args(argv)
    contract = build_contract(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, contract)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(contract, out_path, os.getcwd()))
    print(
        f"status={contract['status']} frames={contract['checks']['frames']} "
        f"missing={contract['checks']['missing_frame_assets']} "
        f"max_mad={contract['checks']['max_overlay_mean_abs_diff']} out={out_path}"
    )
    print(f"report={report_path}")
    if contract["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
