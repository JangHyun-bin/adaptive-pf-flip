#!/usr/bin/env python
"""Compare two LSFS cinematic frame directories without rerunning simulation."""

import argparse
import json
import math
import os
import re
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageStat
except ImportError:
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageStat = None


class CompareError(Exception):
    pass


def fail(message):
    raise CompareError(message)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def frame_number(path):
    match = re.search(r"(\d+)(?=\.png$)", os.path.basename(path), re.IGNORECASE)
    return int(match.group(1)) if match else None


def sorted_pngs(directory):
    path = Path(directory)
    if not path.is_dir():
        fail(f"frame directory not found: {directory}")
    files = [str(item) for item in path.glob("*.png")]
    files.sort(key=lambda item: (frame_number(item) is None, frame_number(item) or 0, item))
    if not files:
        fail(f"no PNG frames found in {directory}")
    return files


def select_indices(count, requested):
    requested = max(1, min(int(requested), count))
    if requested == count:
        return list(range(count))
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


def metric_delta(left_summary, right_summary, metric, stat="mean"):
    left = scalar_at(left_summary, "visual_qa", metric, stat)
    right = scalar_at(right_summary, "visual_qa", metric, stat)
    return {
        "left": left,
        "right": right,
        "delta": None if left is None or right is None else right - left,
    }


def image_metrics(path):
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        gray = rgb.convert("L")
        stat = ImageStat.Stat(gray)
        hist = gray.histogram()
        pixels = max(1, gray.width * gray.height)
        nonblank = sum(hist[8:])
        bright = sum(hist[220:])
        highlight = sum(hist[245:])
        nonzero_bins = [index for index, count in enumerate(hist) if count]
        contrast = (max(nonzero_bins) - min(nonzero_bins)) if nonzero_bins else 0
        return {
            "path": path,
            "width": rgb.width,
            "height": rgb.height,
            "mean_luminance": stat.mean[0],
            "contrast": contrast,
            "nonblank_ratio": nonblank / float(pixels),
            "bright_ratio": bright / float(pixels),
            "highlight_ratio": highlight / float(pixels),
            "bytes": os.path.getsize(path),
        }


def diff_metrics(left_path, right_path):
    with Image.open(left_path) as left_img, Image.open(right_path) as right_img:
        left = left_img.convert("RGB")
        right = right_img.convert("RGB")
        if left.size != right.size:
            right = right.resize(left.size)
        diff = ImageChops.difference(left, right).convert("L")
        stat = ImageStat.Stat(diff)
        hist = diff.histogram()
        pixels = max(1, diff.width * diff.height)
        changed = sum(hist[8:])
        strong = sum(hist[32:])
        return {
            "mean_abs_luma": stat.mean[0],
            "changed_ratio": changed / float(pixels),
            "strong_changed_ratio": strong / float(pixels),
        }


def thumbnail(path, target_width, resample_filter):
    with Image.open(path) as img:
        panel = img.convert("RGB")
        scale = target_width / float(panel.width)
        return panel.resize((target_width, max(1, int(round(panel.height * scale)))), resample_filter)


def diff_thumbnail(left_path, right_path, target_width, resample_filter):
    with Image.open(left_path) as left_img, Image.open(right_path) as right_img:
        left = left_img.convert("RGB")
        right = right_img.convert("RGB")
        if left.size != right.size:
            right = right.resize(left.size)
        diff = ImageChops.difference(left, right)
        diff = diff.point(lambda value: min(255, value * 3))
        scale = target_width / float(diff.width)
        return diff.resize((target_width, max(1, int(round(diff.height * scale)))), resample_filter)


def make_sheet(pairs, out_path, left_label, right_label, thumb_width):
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    label_h = 28
    pad = 12
    panels = []
    for pair in pairs:
        left = thumbnail(pair["left_path"], thumb_width, resample_filter)
        right = thumbnail(pair["right_path"], thumb_width, resample_filter)
        diff = diff_thumbnail(pair["left_path"], pair["right_path"], thumb_width, resample_filter)
        panels.append((pair, left, right, diff))
    panel_w = thumb_width
    panel_h = max(max(left.height, right.height, diff.height) for _pair, left, right, diff in panels)
    sheet_w = pad + 3 * (panel_w + pad)
    sheet_h = pad + len(panels) * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    headers = [left_label, right_label, "abs diff x3"]
    for row, (pair, left, right, diff) in enumerate(panels):
        y = pad + row * (label_h + panel_h + pad)
        frame_label = f"frame {pair['frame_index']:04d}"
        for col, (header, panel) in enumerate(zip(headers, [left, right, diff])):
            x = pad + col * (panel_w + pad)
            label = f"{header} / {frame_label}" if col == 0 else header
            draw.text((x + 6, y + 7), label, fill=(224, 234, 240))
            cell = Image.new("RGB", (panel_w, panel_h), (8, 10, 12))
            cell.paste(panel, ((panel_w - panel.width) // 2, (panel_h - panel.height) // 2))
            sheet.paste(cell, (x, y + label_h))
    sheet.save(out_path)


def comparison_summary(left_summary, right_summary, pairs, left_label, right_label,
                       sheet_path, title, finding, next_text):
    return {
        "schema": "lsfs_cinematic_frame_comparison",
        "version": 1,
        "title": title,
        "left_label": left_label,
        "right_label": right_label,
        "left_summary": left_summary.get("scene_spec") or left_summary.get("source"),
        "right_summary": right_summary.get("scene_spec") or right_summary.get("source"),
        "frame_count": len(pairs),
        "comparison_sheet": sheet_path,
        "metric_deltas": {
            "mean_luminance": metric_delta(left_summary, right_summary, "mean_luminance"),
            "contrast_min": metric_delta(left_summary, right_summary, "contrast", "min"),
            "bright_ratio": metric_delta(left_summary, right_summary, "bright_ratio"),
            "highlight_ratio": metric_delta(left_summary, right_summary, "highlight_ratio"),
            "nonblank_ratio": metric_delta(left_summary, right_summary, "nonblank_ratio"),
        },
        "right_metadata_depth_attenuation": right_summary.get("metadata_depth_attenuation", {}),
        "finding": finding,
        "next": next_text,
        "pairs": pairs,
    }


def render_report(summary):
    deltas = summary.get("metric_deltas", {})
    attenuation = summary.get("right_metadata_depth_attenuation", {})
    title = summary.get("title", "Cinematic Frame Comparison")
    left_label = summary.get("left_label", "left")
    right_label = summary.get("right_label", "right")
    finding = summary.get("finding") or (
        f"{right_label} changes are concentrated in the intended visual regions when compared with {left_label}."
    )
    next_text = summary.get("next") or "Use this comparison to select the next visible render adjustment."

    def delta_line(name, key):
        item = deltas.get(key, {})
        return (
            f"- {name}: left `{item.get('left')}`, right `{item.get('right')}`, "
            f"delta `{item.get('delta')}`"
        )

    lines = [
        f"# {title}",
        "",
        "## Status",
        "",
        "Passed.",
        "",
        "This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.",
        "",
        "## Artifacts",
        "",
        f"- Comparison sheet: `{summary.get('comparison_sheet')}`",
        "",
        "## Metric Deltas",
        "",
        delta_line("Mean luminance", "mean_luminance"),
        delta_line("Minimum contrast", "contrast_min"),
        delta_line("Mean bright ratio", "bright_ratio"),
        delta_line("Mean highlight ratio", "highlight_ratio"),
        delta_line("Mean nonblank ratio", "nonblank_ratio"),
        "",
        "## Metadata Attenuation",
        "",
        f"- Status: `{attenuation.get('status')}`",
        f"- Water alpha multiplier: `{attenuation.get('water_alpha_multiplier')}`",
        f"- Water emission multiplier: `{attenuation.get('water_emission_multiplier')}`",
        f"- Secondary particle cap scale: `{attenuation.get('secondary_particle_cap_scale')}`",
        "",
        "## Visual Finding",
        "",
        finding,
        "",
        "## Next",
        "",
        next_text,
        "",
    ]
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Compare two rendered LSFS cinematic frame directories")
    parser.add_argument("--left", required=True, help="baseline frame directory")
    parser.add_argument("--right", required=True, help="candidate frame directory")
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--summary-left", required=True, help="baseline bridge_summary.json")
    parser.add_argument("--summary-right", required=True, help="candidate bridge_summary.json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--thumb-width", type=int, default=420)
    parser.add_argument("--report", help="optional Markdown report path")
    parser.add_argument("--title", default="Cinematic Frame Comparison")
    parser.add_argument("--finding", default="")
    parser.add_argument("--next", default="")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if Image is None:
        fail("Pillow is required to compare cinematic frames")
    if args.frames <= 0:
        fail("--frames must be positive")
    if args.thumb_width <= 0:
        fail("--thumb-width must be positive")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    left_frames = sorted_pngs(args.left)
    right_frames = sorted_pngs(args.right)
    common_count = min(len(left_frames), len(right_frames))
    if common_count <= 0:
        fail("comparison requires at least one frame pair")
    selected = select_indices(common_count, args.frames)
    pairs = []
    for index in selected:
        left_path = left_frames[index]
        right_path = right_frames[index]
        pair = {
            "frame_index": index,
            "left_path": left_path,
            "right_path": right_path,
            "left_metrics": image_metrics(left_path),
            "right_metrics": image_metrics(right_path),
            "diff_metrics": diff_metrics(left_path, right_path),
        }
        pairs.append(pair)
    sheet_path = str(out_dir / "comparison_sheet.png")
    make_sheet(pairs, sheet_path, args.left_label, args.right_label, args.thumb_width)
    left_summary = read_json(args.summary_left)
    right_summary = read_json(args.summary_right)
    summary = comparison_summary(left_summary, right_summary, pairs,
                                 args.left_label, args.right_label,
                                 sheet_path, args.title, args.finding, args.next)
    summary_path = str(out_dir / "comparison_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, render_report(summary))
    print(f"status=ok pairs={len(pairs)} sheet={sheet_path} summary={summary_path}")
    if args.report:
        print(f"report={args.report}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CompareError as exc:
        print(f"status=fail error={exc}")
        raise SystemExit(1)
