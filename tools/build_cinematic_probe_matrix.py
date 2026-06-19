#!/usr/bin/env python3
"""Build a multi-candidate probe matrix for LSFS cinematic renders."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageStat
except ImportError:  # pragma: no cover
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageStat = None


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def frame_number(path: Path):
    match = re.search(r"(\d+)(?=\.png$)", path.name, re.IGNORECASE)
    return int(match.group(1)) if match else None


def sorted_pngs(directory: Path):
    files = list(directory.glob("*.png"))
    files.sort(key=lambda item: (frame_number(item) is None, frame_number(item) or 0, item.name))
    if not files:
        raise RuntimeError(f"no PNG frames found in {directory}")
    return files


def selected_indices(count, requested):
    requested = max(1, min(int(requested), count))
    if requested == 1:
        return [0]
    return sorted(set(round(i * (count - 1) / float(requested - 1)) for i in range(requested)))


def scalar_at(summary, *keys):
    value = summary
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def metric_delta(base, candidate, metric, stat="mean"):
    left = scalar_at(base, "visual_qa", metric, stat)
    right = scalar_at(candidate, "visual_qa", metric, stat)
    return None if left is None or right is None else right - left


def diff_metrics(base_path: Path, candidate_path: Path):
    with Image.open(base_path) as base_img, Image.open(candidate_path) as candidate_img:
        base = base_img.convert("RGB")
        candidate = candidate_img.convert("RGB")
        if candidate.size != base.size:
            candidate = candidate.resize(base.size)
        diff = ImageChops.difference(base, candidate).convert("L")
        stat = ImageStat.Stat(diff)
        hist = diff.histogram()
        pixels = max(1, diff.width * diff.height)
        return {
            "mean_abs_luma": stat.mean[0],
            "changed_ratio": sum(hist[8:]) / float(pixels),
            "strong_changed_ratio": sum(hist[32:]) / float(pixels),
        }


def thumbnail(path: Path, width):
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    with Image.open(path) as img:
        panel = img.convert("RGB")
        scale = width / float(panel.width)
        return panel.resize((width, max(1, int(round(panel.height * scale)))), resample_filter)


def make_sheet(candidates, indices, out_path: Path, thumb_width):
    label_h = 30
    pad = 12
    panels = []
    for candidate in candidates:
        frames = candidate["frames"]
        panels.append([thumbnail(frames[index], thumb_width) for index in indices])
    panel_h = max(panel.height for column in panels for panel in column)
    sheet_w = pad + len(candidates) * (thumb_width + pad)
    sheet_h = pad + len(indices) * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for col, candidate in enumerate(candidates):
        x = pad + col * (thumb_width + pad)
        for row, index in enumerate(indices):
            y = pad + row * (label_h + panel_h + pad)
            label = f"{candidate['label']} / frame {index:04d}"
            draw.text((x + 6, y + 8), label, fill=(224, 234, 240))
            cell = Image.new("RGB", (thumb_width, panel_h), (8, 10, 12))
            panel = panels[col][row]
            cell.paste(panel, ((thumb_width - panel.width) // 2, (panel_h - panel.height) // 2))
            sheet.paste(cell, (x, y + label_h))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def summarize(candidates, indices, sheet_path: Path):
    base = candidates[0]
    base_summary = base["summary"]
    rows = []
    for candidate in candidates:
        summary = candidate["summary"]
        diffs = []
        if candidate is not base:
            for index in indices:
                diffs.append(diff_metrics(base["frames"][index], candidate["frames"][index]))
        rows.append({
            "label": candidate["label"],
            "frame_dir": str(candidate["frame_dir"]),
            "summary": str(candidate["summary_path"]),
            "preset": summary.get("render_preset_name"),
            "visual_qa": summary.get("visual_qa", {}),
            "water_mesh_smoothing_pass": summary.get("water_mesh_smoothing_pass", {}),
            "water_volume_occlusion_pass": summary.get("water_volume_occlusion_pass", {}),
            "metric_deltas_from_baseline": {
                "mean_luminance": metric_delta(base_summary, summary, "mean_luminance"),
                "contrast_min": metric_delta(base_summary, summary, "contrast", "min"),
                "bright_ratio": metric_delta(base_summary, summary, "bright_ratio"),
                "highlight_ratio": metric_delta(base_summary, summary, "highlight_ratio"),
                "nonblank_ratio": metric_delta(base_summary, summary, "nonblank_ratio"),
            },
            "selected_frame_diff_from_baseline": {
                "mean_abs_luma": None if not diffs else sum(item["mean_abs_luma"] for item in diffs) / float(len(diffs)),
                "changed_ratio": None if not diffs else sum(item["changed_ratio"] for item in diffs) / float(len(diffs)),
                "strong_changed_ratio": None if not diffs else sum(item["strong_changed_ratio"] for item in diffs) / float(len(diffs)),
            },
        })
    return {
        "schema": "lsfs_cinematic_probe_matrix",
        "version": 1,
        "baseline": base["label"],
        "selected_indices": indices,
        "matrix_sheet": str(sheet_path),
        "candidates": rows,
    }


def write_report(path: Path, summary, title, next_text):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        "## Status",
        "",
        "Passed.",
        "",
        "## Artifacts",
        "",
        f"- Matrix sheet: `{summary['matrix_sheet']}`",
        "",
        "## Candidate Metrics",
        "",
        "| Candidate | Preset | Min contrast | Mean luminance | Bright ratio | Highlight ratio | Nonblank | Mean diff | Changed ratio |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in summary["candidates"]:
        qa = candidate.get("visual_qa", {})
        deltas = candidate.get("selected_frame_diff_from_baseline", {})
        lines.append(
            f"| {candidate['label']} | `{candidate.get('preset')}` | "
            f"{qa.get('contrast', {}).get('min')} | "
            f"{qa.get('mean_luminance', {}).get('mean')} | "
            f"{qa.get('bright_ratio', {}).get('mean')} | "
            f"{qa.get('highlight_ratio', {}).get('mean')} | "
            f"{qa.get('nonblank_ratio', {}).get('mean')} | "
            f"{deltas.get('mean_abs_luma')} | "
            f"{deltas.get('changed_ratio')} |"
        )
    lines.extend([
        "",
        "## Candidate Passes",
        "",
    ])
    for candidate in summary["candidates"]:
        lines.extend([
            f"### {candidate['label']}",
            "",
            f"- Smoothing: `{candidate.get('water_mesh_smoothing_pass')}`",
            f"- Volume occlusion: `{candidate.get('water_volume_occlusion_pass')}`",
            "",
        ])
    lines.extend([
        "## Next",
        "",
        next_text,
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", nargs=3, metavar=("LABEL", "FRAME_DIR", "SUMMARY"),
                        required=True, help="Candidate label, frame directory, and bridge summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=360)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Cinematic Probe Matrix")
    parser.add_argument("--next", dest="next_text",
                        default="Use this probe matrix to select one candidate for a full render.")
    return parser.parse_args()


def main():
    if Image is None:
        raise RuntimeError("Pillow is required to build a probe matrix")
    args = parse_args()
    candidates = []
    for label, frame_dir, summary_path in args.candidate:
        frame_path = Path(frame_dir)
        summary_file = Path(summary_path)
        candidates.append({
            "label": label,
            "frame_dir": frame_path,
            "summary_path": summary_file,
            "frames": sorted_pngs(frame_path),
            "summary": read_json(summary_file),
        })
    min_count = min(len(candidate["frames"]) for candidate in candidates)
    indices = selected_indices(min_count, args.frames)
    out_dir = Path(args.out_dir)
    sheet_path = out_dir / "probe_matrix.png"
    summary_path = out_dir / "probe_matrix_summary.json"
    make_sheet(candidates, indices, sheet_path, args.thumb_width)
    summary = summarize(candidates, indices, sheet_path)
    write_json(summary_path, summary)
    if args.report:
        write_report(Path(args.report), summary, args.title, args.next_text)
    print(f"status=ok candidates={len(candidates)} frames={len(indices)}")
    print(f"sheet={sheet_path}")
    print(f"summary={summary_path}")
    if args.report:
        print(f"report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
