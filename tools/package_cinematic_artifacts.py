#!/usr/bin/env python
"""Create a compact inspection package for a cinematic shot directory."""

import argparse
import json
import os
import struct
from datetime import datetime, timezone


ARTIFACTS = [
    ("gif", "Shot GIF", "Primary animated review output.", True, True),
    ("contact_sheet", "Contact sheet", "Key rendered frames in one sheet.", True, True),
    ("comparison_sheet", "Baseline comparison", "Current contact sheet beside the baseline run.", True, True),
    ("focus_comparison_sheet", "Focus comparison", "Water-body focus crop beside the baseline run.", True, True),
    (
        "secondary_depth_comparison_sheet",
        "Secondary depth comparison",
        "Spray, foam, and bubble depth diagnostic beside the baseline run.",
        True,
        True,
    ),
    (
        "ripple_readability_comparison_sheet",
        "Ripple readability comparison",
        "Surface ripple diagnostic beside the baseline run.",
        True,
        True,
    ),
    ("focus_sheet", "Focus sheet", "Current water-body focus diagnostic.", False, True),
    ("secondary_depth_sheet", "Secondary depth sheet", "Current secondary depth diagnostic.", False, True),
    ("ripple_readability_sheet", "Ripple readability sheet", "Current ripple readability diagnostic.", False, True),
    ("temporal_diff_sheet", "Temporal diff sheet", "Current motion-readability diagnostic.", False, True),
    ("review_manifest", "Review manifest", "Review-pack metadata and metrics.", False, False),
    ("render_summary", "Render summary", "Renderer bridge summary.", False, False),
]


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def format_bytes(size):
    if size is None:
        return "missing"
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"


def posix_rel(path, root):
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def md_path(path, out_dir):
    return posix_rel(path, out_dir)


def repo_path(path, root):
    return posix_rel(path, root)


def resolve_artifact(artifacts, key, shot_dir):
    value = artifacts.get(key)
    if value:
        return os.path.abspath(value)
    fallbacks = {
        "gif": os.path.join(shot_dir, "shot.gif"),
        "contact_sheet": os.path.join(shot_dir, "review", "contact_sheet.png"),
        "comparison_sheet": os.path.join(shot_dir, "review", "comparison_sheet.png"),
        "focus_comparison_sheet": os.path.join(shot_dir, "review", "focus_comparison_sheet.png"),
        "secondary_depth_comparison_sheet": os.path.join(shot_dir, "review", "secondary_depth_comparison_sheet.png"),
        "ripple_readability_comparison_sheet": os.path.join(shot_dir, "review", "ripple_readability_comparison_sheet.png"),
        "focus_sheet": os.path.join(shot_dir, "review", "focus_sheet.png"),
        "secondary_depth_sheet": os.path.join(shot_dir, "review", "secondary_depth_sheet.png"),
        "ripple_readability_sheet": os.path.join(shot_dir, "review", "ripple_readability_sheet.png"),
        "temporal_diff_sheet": os.path.join(shot_dir, "review", "temporal_diff_sheet.png"),
        "review_manifest": os.path.join(shot_dir, "review", "review_manifest.json"),
        "render_summary": os.path.join(shot_dir, "blender", "bridge_summary.json"),
    }
    return os.path.abspath(fallbacks[key])


def image_dimensions(path):
    try:
        with open(path, "rb") as f:
            header = f.read(24)
    except OSError:
        return None
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        return struct.unpack(">II", header[16:24])
    if header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
        return struct.unpack("<HH", header[6:10])
    return None


def collect_artifacts(summary, shot_dir, strict):
    artifacts = summary.get("artifacts", {})
    rows = []
    missing_required = []
    for key, label, description, required, preview in ARTIFACTS:
        path = resolve_artifact(artifacts, key, shot_dir)
        exists = os.path.isfile(path)
        if required and not exists:
            missing_required.append(path)
        size = os.path.getsize(path) if exists else None
        dims = image_dimensions(path) if exists and preview else None
        rows.append({
            "key": key,
            "label": label,
            "description": description,
            "required": required,
            "preview": preview,
            "path": path,
            "exists": exists,
            "size": size,
            "dimensions": dims,
        })
    if strict and missing_required:
        formatted = "\n".join(f"- {path}" for path in missing_required)
        raise SystemExit(f"Missing required cinematic artifacts:\n{formatted}")
    return rows


def count_files(path, suffix):
    if not os.path.isdir(path):
        return 0
    return sum(1 for name in os.listdir(path) if name.lower().endswith(suffix))


def gate_status(metrics, key):
    value = metrics.get(key)
    if isinstance(value, dict) and "passed" in value:
        return value["passed"]
    return "n/a"


def summary_lines(summary):
    config = summary.get("config", {})
    metrics = summary.get("metrics", {})
    export_metrics = summary.get("export_metrics", {})
    validation = summary.get("validation_metrics", {})
    grid = " x ".join(str(config.get(key, "n/a")) for key in ("nx", "ny", "nz"))
    frames = config.get("frames", metrics.get("cache_frame_count", "n/a"))
    return [
        f"- Status: `{summary.get('status', 'n/a')}`",
        f"- Renderer: `{summary.get('selected_renderer', summary.get('requested_renderer', 'n/a'))}`",
        f"- Preset: `{summary.get('shot_preset', config.get('preset', 'n/a'))}`",
        f"- Grid: `{grid}`",
        f"- Frames: `{frames}`",
        f"- Samples: `{config.get('samples', 'n/a')}`",
        f"- Export particles: `{export_metrics.get('particles', 'n/a')}`",
        f"- Validated particles: `{validation.get('particles', 'n/a')}`",
        f"- GIF bytes: `{metrics.get('shot_gif_bytes', 'n/a')}`",
        f"- Visual gate: `{gate_status(metrics, 'visual_qa_gate')}`",
        f"- Focus gate: `{gate_status(metrics, 'focus_review_gate')}`",
        f"- Secondary depth gate: `{gate_status(metrics, 'secondary_depth_review_gate')}`",
        f"- Ripple gate: `{gate_status(metrics, 'ripple_readability_gate')}`",
        f"- Comparison sources: `{metrics.get('comparison_source_count', 'n/a')}`",
    ]


def markdown(summary, summary_path, shot_dir, rows, out_path, root):
    out_dir = os.path.dirname(out_path)
    render_frame_dir = summary.get("artifacts", {}).get("render_frame_dir")
    review_keyframes = summary.get("artifacts", {}).get("review_keyframes", [])
    render_frame_count = count_files(render_frame_dir, ".png") if render_frame_dir else 0

    lines = [
        "# Cinematic Artifact Inspection Package",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Shot directory: `{repo_path(shot_dir, root)}`",
        f"Source summary: `{repo_path(summary_path, root)}`",
        "",
        "## Shot Summary",
        "",
        *summary_lines(summary),
        f"- Render frame PNGs: `{render_frame_count}`",
        f"- Review keyframes: `{len(review_keyframes)}`",
        "",
        "## Artifact Index",
        "",
        "| Artifact | Required | Status | Size | Dimensions | Link |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]

    for row in rows:
        status = "present" if row["exists"] else "missing"
        required = "yes" if row["required"] else "no"
        dims = "n/a"
        if row["dimensions"]:
            dims = f"{row['dimensions'][0]} x {row['dimensions'][1]}"
        if row["exists"]:
            link = f"[{row['label']}]({md_path(row['path'], out_dir)})"
        else:
            link = f"`{repo_path(row['path'], root)}`"
        lines.append(
            f"| {row['label']} | `{required}` | `{status}` | {format_bytes(row['size'])} | `{dims}` | {link} |"
        )

    lines.extend([
        "",
        "## Inline Preview",
        "",
    ])

    for row in rows:
        if not row["preview"] or not row["exists"]:
            continue
        lines.extend([
            f"### {row['label']}",
            "",
            f"![{row['label']}]({md_path(row['path'], out_dir)})",
            "",
        ])

    lines.extend([
        "## Notes",
        "",
        "- The package links to ignored build artifacts in the current workspace, so regenerate it when the shot directory changes.",
        "- The required set is the GIF, contact sheet, and four baseline comparison sheets used for quick visual inspection.",
        "",
        "## Next",
        "",
        "S129 should review the S127 public gallery and choose the next concrete visible improvement from current evidence.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("shot_dir", help="Cinematic shot directory")
    parser.add_argument("--out", required=True, help="Markdown output path")
    parser.add_argument("--allow-missing", action="store_true", help="Write the package even if required artifacts are absent")
    args = parser.parse_args(argv)

    root = os.getcwd()
    shot_dir = os.path.abspath(args.shot_dir)
    summary_path = os.path.join(shot_dir, "shot_summary.json")
    if not os.path.isfile(summary_path):
        raise SystemExit(f"Missing shot summary: {summary_path}")

    summary = read_json(summary_path)
    rows = collect_artifacts(summary, shot_dir, strict=not args.allow_missing)
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown(summary, summary_path, shot_dir, rows, out_path, root))
    print(out_path)


if __name__ == "__main__":
    main()
