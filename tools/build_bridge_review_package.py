#!/usr/bin/env python
"""Build a compact review package for direct Blender bridge cinematic outputs."""

import argparse
import hashlib
import json
import os
import re
import struct
from datetime import datetime, timezone
from pathlib import Path


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def posix_rel(path, root):
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def slug(value):
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "summary"


def format_bytes(size):
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"


def image_dimensions(path):
    try:
        with open(path, "rb") as f:
            header = f.read(24)
    except OSError:
        return None
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        return list(struct.unpack(">II", header[16:24]))
    if header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
        return list(struct.unpack("<HH", header[6:10]))
    return None


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path, label):
    resolved = os.path.abspath(path)
    if not os.path.isfile(resolved):
        raise SystemExit(f"Missing {label}: {resolved}")
    return resolved


def default_path(shot_dir, *parts):
    return os.path.join(shot_dir, *parts)


def parse_labeled_path(value):
    if "=" in value:
        label, path = value.split("=", 1)
        return slug(label), path
    path = value
    return slug(Path(path).stem), path


def artifact_entry(item, root, kind):
    asset = item.get("asset") or item.get("source")
    if not asset:
        return None
    path = require_file(asset, item.get("label", kind))
    entry = {
        "kind": kind,
        "label": item.get("label", kind),
        "path": path,
        "repo_path": posix_rel(path, root),
        "size": os.path.getsize(path),
        "sha256": sha256_file(path),
    }
    dims = item.get("dimensions") or image_dimensions(path)
    if dims:
        entry["dimensions"] = list(dims)
    href = item.get("href")
    if href:
        entry["href"] = href
    source = item.get("source")
    if source:
        entry["source"] = os.path.abspath(source)
        entry["source_repo_path"] = posix_rel(os.path.abspath(source), root)
    return entry


def collect_gallery_artifacts(gallery_manifest, root):
    artifacts = []
    for item in gallery_manifest.get("assets", []):
        entry = artifact_entry(item, root, "asset")
        if entry:
            artifacts.append(entry)
    for item in gallery_manifest.get("metadata_files", []):
        entry = artifact_entry(item, root, "metadata")
        if entry:
            artifacts.append(entry)
    return artifacts


def pick(mapping, keys):
    return {key: mapping[key] for key in keys if key in mapping}


def curated_bridge_summary(summary):
    return {
        "status": summary.get("status"),
        "render_preset_name": summary.get("render_preset_name"),
        "frame_count": summary.get("frame_count"),
        "resolution": {
            "width": summary.get("width"),
            "height": summary.get("height"),
            "samples": summary.get("samples"),
        },
        "source_window": summary.get("source_window"),
        "camera": pick(summary, ["camera_framing", "camera_motion", "camera_path_metrics"]),
        "water": pick(
            summary,
            [
                "water_material",
                "metadata_depth_attenuation",
                "water_volume_scattering_pass",
                "water_volume_occlusion_pass",
                "water_surface_detail",
                "water_surface_glint_pass",
                "water_reflection_pass",
            ],
        ),
        "secondary": pick(
            summary,
            [
                "secondary_direct_pass",
                "secondary_soft_pass",
                "secondary_streak_pass",
                "surface_contact_foam_counts",
                "water_impact_ripple_counts",
                "secondary_streak_counts",
            ],
        ),
        "quality": pick(summary, ["visual_qa", "min_contrast", "min_nonblank_ratio"]),
    }


def comparison_digest(summary):
    return {
        "title": summary.get("title"),
        "left_label": summary.get("left_label"),
        "right_label": summary.get("right_label"),
        "frame_count": summary.get("frame_count"),
        "metric_deltas": summary.get("metric_deltas", {}),
        "calibration_deltas": summary.get("calibration_deltas", {}),
        "finding": summary.get("finding"),
        "next": summary.get("next"),
    }


def generic_summary_digest(summary):
    schema = summary.get("schema", "")
    if schema == "lsfs_cinematic_frame_comparison":
        return comparison_digest(summary)
    return summary


def collect_labeled_summaries(values, root):
    summaries = {}
    sources = []
    for value in values:
        label, path = parse_labeled_path(value)
        resolved = require_file(path, f"{label} summary")
        payload = read_json(resolved)
        summaries[label] = generic_summary_digest(payload)
        sources.append({
            "label": label,
            "path": resolved,
            "repo_path": posix_rel(resolved, root),
            "schema": payload.get("schema"),
            "size": os.path.getsize(resolved),
            "sha256": sha256_file(resolved),
        })
    return summaries, sources


def markdown_report(package, package_path, root):
    bridge = package["bridge_summary"]
    resolution = bridge.get("resolution", {})
    lines = [
        f"# {package['title']}",
        "",
        f"Generated UTC: `{package['generated_utc']}`",
        f"Package JSON: `{posix_rel(package_path, root)}`",
        f"Shot directory: `{package['shot']['repo_path']}`",
        f"Gallery: `{package['gallery'].get('index_repo_path', 'n/a')}`",
        "",
        "## Render Summary",
        "",
        f"- Status: `{bridge.get('status', 'n/a')}`",
        f"- Preset: `{bridge.get('render_preset_name', 'n/a')}`",
        f"- Frames: `{bridge.get('frame_count', 'n/a')}`",
        f"- Resolution: `{resolution.get('width', 'n/a')} x {resolution.get('height', 'n/a')}`",
        f"- Samples: `{resolution.get('samples', 'n/a')}`",
        "",
        "## Key Deltas",
        "",
    ]
    for label, summary in package.get("summaries", {}).items():
        deltas = summary.get("metric_deltas")
        if not isinstance(deltas, dict):
            continue
        lines.append(f"### {label}")
        for key in ("mean_luminance", "contrast_min", "bright_ratio", "highlight_ratio", "nonblank_ratio"):
            value = deltas.get(key, {})
            if isinstance(value, dict) and "delta" in value:
                lines.append(f"- {key}: `{value.get('delta')}`")
        lines.append("")

    lines.extend([
        "## Artifact Index",
        "",
        "| Label | Kind | Size | Dimensions | Path |",
        "| --- | --- | ---: | --- | --- |",
    ])
    for item in package.get("artifacts", []):
        dims = item.get("dimensions")
        dims_text = f"{dims[0]} x {dims[1]}" if dims else "n/a"
        lines.append(
            f"| {item['label']} | `{item['kind']}` | {format_bytes(item['size'])} | `{dims_text}` | `{item['repo_path']}` |"
        )

    lines.extend([
        "",
        "## Summary Sources",
        "",
        "| Label | Schema | Size | Path |",
        "| --- | --- | ---: | --- |",
    ])
    for item in package.get("summary_sources", []):
        lines.append(
            f"| {item['label']} | `{item.get('schema') or 'n/a'}` | {format_bytes(item['size'])} | `{item['repo_path']}` |"
        )

    lines.extend([
        "",
        "## Next",
        "",
        package.get("next", "Use this package as the current review baseline."),
        "",
    ])
    return "\n".join(lines)


def build_package(args):
    root = os.getcwd()
    shot_dir = os.path.abspath(args.shot_dir)
    gallery_manifest_path = require_file(
        args.gallery_manifest or default_path(shot_dir, "gallery", "gallery_manifest.json"),
        "gallery manifest",
    )
    bridge_summary_path = require_file(
        args.bridge_summary or default_path(shot_dir, "blender", "bridge_summary.json"),
        "bridge summary",
    )
    gallery_manifest = read_json(gallery_manifest_path)
    bridge_summary = read_json(bridge_summary_path)
    summaries, summary_sources = collect_labeled_summaries(args.summary or [], root)
    artifacts = collect_gallery_artifacts(gallery_manifest, root)

    gallery_index = gallery_manifest.get("index")
    gallery = {
        "manifest_path": gallery_manifest_path,
        "manifest_repo_path": posix_rel(gallery_manifest_path, root),
        "title": gallery_manifest.get("title"),
        "schema": gallery_manifest.get("schema"),
        "version": gallery_manifest.get("version"),
    }
    if gallery_index:
        index_path = os.path.abspath(gallery_index)
        gallery["index_path"] = index_path
        gallery["index_repo_path"] = posix_rel(index_path, root)

    return {
        "schema": "lsfs_bridge_cinematic_review_package",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "next": args.next,
        "shot": {
            "path": shot_dir,
            "repo_path": posix_rel(shot_dir, root),
        },
        "gallery": gallery,
        "bridge_summary_source": {
            "path": bridge_summary_path,
            "repo_path": posix_rel(bridge_summary_path, root),
            "schema": bridge_summary.get("schema"),
            "size": os.path.getsize(bridge_summary_path),
            "sha256": sha256_file(bridge_summary_path),
        },
        "bridge_summary": curated_bridge_summary(bridge_summary),
        "artifacts": artifacts,
        "summaries": summaries,
        "summary_sources": summary_sources,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a direct bridge cinematic review package")
    parser.add_argument("shot_dir")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--title", default="S246 Accepted Cinematic Review")
    parser.add_argument("--bridge-summary")
    parser.add_argument("--gallery-manifest")
    parser.add_argument(
        "--summary",
        action="append",
        default=[],
        help="Additional labeled JSON summary as label=path. Can be repeated.",
    )
    parser.add_argument("--report", help="Optional Markdown report path")
    parser.add_argument("--next", default="Use this package as the current review baseline.")
    args = parser.parse_args(argv)

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    package = build_package(args)
    package_path = os.path.join(out_dir, "review_package.json")
    write_json(package_path, package)
    report_path = os.path.abspath(args.report) if args.report else os.path.join(out_dir, "review_package.md")
    write_text(report_path, markdown_report(package, package_path, os.getcwd()))
    print(f"status=ok package={package_path}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
