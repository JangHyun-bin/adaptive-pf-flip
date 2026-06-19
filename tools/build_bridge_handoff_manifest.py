#!/usr/bin/env python
"""Build an accepted bridge cinematic handoff manifest.

The review package is optimized for humans. This manifest is optimized for the
next engineering handoff: external renderer experiments, large-shot reruns, or
benchmark gates that need a precise accepted baseline fingerprint.
"""

import argparse
import json
import os
import subprocess
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


def json_source(path, root, label):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    return {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "size": os.path.getsize(resolved),
        "sha256": sha256_file(resolved),
    }, payload


def optional_json_source(path, root, label):
    if not path:
        return None, None
    return json_source(path, root, label)


def file_source(path, root, label):
    resolved = require_file(path, label)
    return {
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "size": os.path.getsize(resolved),
        "sha256": sha256_file(resolved),
    }


def git_info(root):
    def run_git(*args):
        try:
            return subprocess.check_output(
                ["git", *args],
                cwd=root,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except Exception:
            return None

    return {
        "commit": run_git("rev-parse", "HEAD"),
        "branch": run_git("rev-parse", "--abbrev-ref", "HEAD"),
        "status_short": run_git("status", "--short"),
    }


def metric_delta_value(summary, key):
    value = summary.get("metric_deltas", {}).get(key, {})
    return value.get("delta") if isinstance(value, dict) else None


def calibration_delta_value(summary, key):
    value = summary.get("calibration_deltas", {}).get(key, {})
    return value.get("delta") if isinstance(value, dict) else None


def summary_digest(summary):
    return {
        "title": summary.get("title"),
        "left_label": summary.get("left_label"),
        "right_label": summary.get("right_label"),
        "frame_count": summary.get("frame_count"),
        "metric_deltas": {
            key: metric_delta_value(summary, key)
            for key in (
                "mean_luminance",
                "contrast_min",
                "bright_ratio",
                "highlight_ratio",
                "nonblank_ratio",
            )
        },
        "calibration_deltas": {
            key: calibration_delta_value(summary, key)
            for key in (
                "luma_p95",
                "luma_p99",
                "luma_p995",
                "contrast",
                "specular_ratio",
            )
        },
        "finding": summary.get("finding"),
        "next": summary.get("next"),
    }


def review_package_digest(package):
    summaries = {}
    for label, summary in package.get("summaries", {}).items():
        if isinstance(summary, dict) and "metric_deltas" in summary:
            summaries[label] = summary_digest(summary)
        else:
            summaries[label] = summary

    artifacts = []
    for item in package.get("artifacts", []):
        artifacts.append({
            "label": item.get("label"),
            "kind": item.get("kind"),
            "repo_path": item.get("repo_path"),
            "size": item.get("size"),
            "dimensions": item.get("dimensions"),
            "sha256": item.get("sha256"),
        })

    return {
        "schema": package.get("schema"),
        "version": package.get("version"),
        "title": package.get("title"),
        "generated_utc": package.get("generated_utc"),
        "shot": package.get("shot"),
        "gallery": package.get("gallery"),
        "bridge_summary": package.get("bridge_summary"),
        "summary_sources": package.get("summary_sources", []),
        "summaries": summaries,
        "artifacts": artifacts,
    }


def publish_digest(manifest):
    if not manifest:
        return {"enabled": False}
    return {
        "enabled": True,
        "status": manifest.get("status"),
        "local_url": manifest.get("local_url"),
        "public_url": manifest.get("public_url"),
        "gallery_dir": manifest.get("gallery_dir"),
        "checks": manifest.get("checks", []),
        "processes": manifest.get("processes", {}),
        "logs": manifest.get("logs", {}),
    }


def render_data_digest(payload):
    if not payload:
        return {"enabled": False}
    return {
        "enabled": True,
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "status": payload.get("status"),
        "frame_count": payload.get("frame_count"),
        "simulation": payload.get("simulation", {}),
        "summary": payload.get("summary", {}),
    }


def sequence_digest(payload):
    if not payload:
        return {"enabled": False}
    frames = payload.get("frames") if isinstance(payload.get("frames"), list) else []
    return {
        "enabled": True,
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "frame_count": payload.get("frame_count", len(frames)),
        "first_frame": frames[0] if frames else None,
        "last_frame": frames[-1] if frames else None,
    }


def markdown_report(manifest, out_path, root):
    review = manifest["review_package"]
    bridge = review.get("bridge_summary", {})
    resolution = bridge.get("resolution", {})
    public = manifest.get("public_review", {})
    sources = manifest.get("sources", {})
    lines = [
        f"# {manifest['title']}",
        "",
        f"Generated UTC: `{manifest['generated_utc']}`",
        f"Manifest JSON: `{posix_rel(out_path, root)}`",
        f"Accepted preset: `{manifest['accepted_preset']}`",
        f"Git commit: `{manifest.get('git', {}).get('commit') or 'n/a'}`",
        "",
        "## Review Target",
        "",
        f"- Shot: `{review.get('shot', {}).get('repo_path', 'n/a')}`",
        f"- Gallery: `{review.get('gallery', {}).get('index_repo_path', 'n/a')}`",
        f"- Public URL: `{public.get('public_url') or 'n/a'}`",
        f"- Local URL: `{public.get('local_url') or 'n/a'}`",
        f"- Publish status: `{public.get('status') or 'n/a'}`",
        "",
        "## Render Summary",
        "",
        f"- Status: `{bridge.get('status', 'n/a')}`",
        f"- Preset: `{bridge.get('render_preset_name', 'n/a')}`",
        f"- Frames: `{bridge.get('frame_count', 'n/a')}`",
        f"- Resolution: `{resolution.get('width', 'n/a')} x {resolution.get('height', 'n/a')}`",
        f"- Samples: `{resolution.get('samples', 'n/a')}`",
        "",
        "## Key Metrics",
        "",
    ]
    for label, summary in review.get("summaries", {}).items():
        metric_deltas = summary.get("metric_deltas") if isinstance(summary, dict) else None
        if not isinstance(metric_deltas, dict):
            continue
        lines.append(f"### {label}")
        for key in ("mean_luminance", "contrast_min", "bright_ratio", "highlight_ratio", "nonblank_ratio"):
            lines.append(f"- {key}: `{metric_deltas.get(key)}`")
        lines.append("")

    lines.extend([
        "## Source Fingerprints",
        "",
        "| Source | Schema | Size | Path |",
        "| --- | --- | ---: | --- |",
    ])
    for label, source in sources.items():
        if not isinstance(source, dict):
            continue
        schema = source.get("schema") or "n/a"
        size = source.get("size")
        size_text = format_bytes(size) if isinstance(size, int) else "n/a"
        path = source.get("repo_path") or "n/a"
        lines.append(f"| {label} | `{schema}` | {size_text} | `{path}` |")

    lines.extend([
        "",
        "## Next",
        "",
        manifest.get("next", "Use this handoff manifest as the accepted baseline pointer."),
        "",
    ])
    return "\n".join(lines)


def build_manifest(args):
    root = os.getcwd()
    review_source, review_package = json_source(args.review_package, root, "review package")
    publish_source, publish_manifest = optional_json_source(args.publish_manifest, root, "publish manifest")
    render_source, render_data = optional_json_source(args.render_data_summary, root, "render data summary")
    sequence_source, sequence = optional_json_source(args.sequence, root, "converted sequence")
    preset_source = file_source(args.preset_config, root, "preset config") if args.preset_config else None

    sources = {"review_package": review_source}
    if publish_source:
        sources["publish_manifest"] = publish_source
    if render_source:
        sources["render_data_summary"] = render_source
    if sequence_source:
        sources["sequence"] = sequence_source
    if preset_source:
        sources["preset_config"] = preset_source

    return {
        "schema": "lsfs_bridge_cinematic_handoff_manifest",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "accepted_preset": args.accepted_preset,
        "next": args.next,
        "git": git_info(root),
        "sources": sources,
        "review_package": review_package_digest(review_package),
        "public_review": publish_digest(publish_manifest),
        "render_data_summary": render_data_digest(render_data),
        "sequence": sequence_digest(sequence),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build an accepted bridge cinematic handoff manifest")
    parser.add_argument("--review-package", required=True)
    parser.add_argument("--publish-manifest")
    parser.add_argument("--render-data-summary")
    parser.add_argument("--sequence")
    parser.add_argument("--preset-config", default="configs/cinematic_presets.json")
    parser.add_argument("--accepted-preset", default="dam_break_water_mesh_smoothing")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Accepted Bridge Cinematic Handoff Manifest")
    parser.add_argument(
        "--next",
        default="Use this handoff manifest as the accepted baseline pointer for external rendering and large-shot benchmark work.",
    )
    args = parser.parse_args(argv)

    manifest = build_manifest(args)
    out_path = os.path.abspath(args.out)
    write_json(out_path, manifest)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(manifest, out_path, os.getcwd()))
    print(f"status=ok manifest={out_path}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
