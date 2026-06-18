#!/usr/bin/env python
"""Summarize LSFS cinematic gate shot_summary.json files as a Markdown table."""

import argparse
import json
import os
from datetime import datetime, timezone


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def nested(data, *keys, default=None):
    cur = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def fmt_float(value, digits=3):
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def fmt_seconds(value):
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.2f}s"
    except (TypeError, ValueError):
        return "n/a"


def stage_seconds(summary):
    out = {}
    total = 0.0
    for item in summary.get("commands", []):
        label = item.get("label")
        elapsed = item.get("elapsed_ms")
        if not label or elapsed is None:
            continue
        seconds = float(elapsed) / 1000.0
        out[label] = seconds
        total += seconds
    out["total"] = total
    return out


def row_for_summary(path, root):
    summary = read_json(path)
    config = summary.get("config", {})
    metrics = summary.get("metrics", {})
    stages = stage_seconds(summary)
    grid = f"{config.get('nx', 'n/a')}x{config.get('ny', 'n/a')}x{config.get('nz', 'n/a')}"
    rel = os.path.relpath(os.path.abspath(path), root).replace("\\", "/")
    return {
        "summary": rel,
        "status": summary.get("status", "unknown"),
        "preset": summary.get("shot_preset", config.get("preset", "unknown")),
        "grid": grid,
        "frames": config.get("frames", "n/a"),
        "secondary": config.get("secondary_physical_particles", "n/a"),
        "visual_luma": nested(metrics, "visual_qa", "mean_luminance", "mean"),
        "visual_contrast": nested(metrics, "visual_qa", "contrast", "min"),
        "focus_contrast": nested(metrics, "focus_review", "summary", "contrast", "min"),
        "secondary_crop": nested(metrics, "secondary_depth_review", "summary", "crop_particles", "mean"),
        "secondary_span": nested(metrics, "secondary_depth_review", "summary", "normalized_depth_span", "mean"),
        "framing_inside": nested(metrics, "secondary_framing", "mean_inside_ratio"),
        "framing_min": nested(metrics, "secondary_framing", "min_inside_ratio"),
        "export_s": stages.get("export_render_cache"),
        "validate_s": stages.get("validate_render_cache"),
        "reconstruct_s": stages.get("reconstruct_water"),
        "convert_s": stages.get("convert_render_cache"),
        "render_s": stages.get("render_blender"),
        "total_s": stages.get("total"),
        "gif_mb": (nested(metrics, "shot_gif_bytes") or 0) / (1024.0 * 1024.0),
    }


def markdown(rows):
    lines = [
        "# Cinematic Benchmark Summary",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "| Gate | Status | Grid | Frames | Secondary | Visual mean | Min contrast | Focus contrast | Secondary crop | Norm depth | Framing mean | Framing min | Export | Validate | Reconstruct | Convert | Render | Total | GIF MB |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join([
                f"`{row['preset']}`",
                f"`{row['status']}`",
                f"`{row['grid']}`",
                str(row["frames"]),
                str(row["secondary"]),
                fmt_float(row["visual_luma"], 3),
                fmt_float(row["visual_contrast"], 1),
                fmt_float(row["focus_contrast"], 1),
                fmt_float(row["secondary_crop"], 3),
                fmt_float(row["secondary_span"], 3),
                fmt_float(row["framing_inside"], 3),
                fmt_float(row["framing_min"], 3),
                fmt_seconds(row["export_s"]),
                fmt_seconds(row["validate_s"]),
                fmt_seconds(row["reconstruct_s"]),
                fmt_seconds(row["convert_s"]),
                fmt_seconds(row["render_s"]),
                fmt_seconds(row["total_s"]),
                fmt_float(row["gif_mb"], 2),
            ])
            + " |"
        )
    lines.extend([
        "",
        "## Sources",
        "",
    ])
    for row in rows:
        lines.append(f"- `{row['preset']}`: `{row['summary']}`")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("summaries", nargs="+", help="shot_summary.json files to summarize")
    parser.add_argument("--out", required=True, help="Markdown output path")
    args = parser.parse_args(argv)

    root = os.getcwd()
    rows = [row_for_summary(path, root) for path in args.summaries]
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown(rows))
    print(out)


if __name__ == "__main__":
    main()
