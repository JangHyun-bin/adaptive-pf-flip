#!/usr/bin/env python
"""Create upper-tail highlight gain/loss masks from two cinematic frame sets."""

import argparse
import json
import math
import os
import re
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


class DiagnosticError(Exception):
    pass


def fail(message):
    raise DiagnosticError(message)


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


def percentile_from_hist(hist, percentile):
    total = sum(hist)
    if total <= 0:
        return 0
    target = max(1, int(math.ceil(total * percentile)))
    cumulative = 0
    for value, count in enumerate(hist):
        cumulative += count
        if cumulative >= target:
            return value
    return len(hist) - 1


def mean(values):
    values = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return None if not values else sum(values) / float(len(values))


def thumbnail(path, target_width, resample_filter):
    with Image.open(path) as img:
        panel = img.convert("RGB")
        scale = target_width / float(panel.width)
        return panel.resize((target_width, max(1, int(round(panel.height * scale)))), resample_filter)


def mask_thumbnail(path, target_width, resample_filter):
    with Image.open(path) as img:
        panel = img.convert("RGB")
        scale = target_width / float(panel.width)
        return panel.resize((target_width, max(1, int(round(panel.height * scale)))), resample_filter)


def make_diagnostic_mask(left_path, right_path, mask_path, tail_percentile, min_tail_luma,
                         gain_threshold):
    with Image.open(left_path) as left_img, Image.open(right_path) as right_img:
        left_rgb = left_img.convert("RGB")
        right_rgb = right_img.convert("RGB")
        if left_rgb.size != right_rgb.size:
            right_rgb = right_rgb.resize(left_rgb.size)
        left_gray = left_rgb.convert("L")
        right_gray = right_rgb.convert("L")
        left_hist = left_gray.histogram()
        right_hist = right_gray.histogram()
        tail_threshold = max(
            min_tail_luma,
            percentile_from_hist(left_hist, tail_percentile),
            percentile_from_hist(right_hist, tail_percentile),
        )
        left_values = left_gray.tobytes()
        right_values = right_gray.tobytes()
        pixels = max(1, len(left_values))
        mask_pixels = []
        gain_count = 0
        loss_count = 0
        gain_sum = 0.0
        loss_sum = 0.0
        strongest_gain = 0
        strongest_loss = 0
        for left, right in zip(left_values, right_values):
            delta = int(right) - int(left)
            gain = delta if right >= tail_threshold and delta >= gain_threshold else 0
            loss = -delta if left >= tail_threshold and -delta >= gain_threshold else 0
            if gain:
                gain_count += 1
                gain_sum += gain
                strongest_gain = max(strongest_gain, gain)
                mask_pixels.append((min(255, 42 + gain * 9), min(235, 64 + gain * 5), 24))
            elif loss:
                loss_count += 1
                loss_sum += loss
                strongest_loss = max(strongest_loss, loss)
                mask_pixels.append((18, min(190, 52 + loss * 5), min(255, 72 + loss * 9)))
            else:
                base = max(0, min(44, int(right) // 8))
                mask_pixels.append((base, base, base))
        mask = Image.new("RGB", left_gray.size)
        mask.putdata(mask_pixels)
        mask.save(mask_path)
        return {
            "left_path": left_path,
            "right_path": right_path,
            "mask_path": str(mask_path),
            "tail_threshold": tail_threshold,
            "pixels": pixels,
            "gain_count": gain_count,
            "loss_count": loss_count,
            "gain_ratio": gain_count / float(pixels),
            "loss_ratio": loss_count / float(pixels),
            "net_gain_ratio": (gain_count - loss_count) / float(pixels),
            "mean_gain_luma": None if gain_count == 0 else gain_sum / float(gain_count),
            "mean_loss_luma": None if loss_count == 0 else loss_sum / float(loss_count),
            "strongest_gain_luma": strongest_gain,
            "strongest_loss_luma": strongest_loss,
        }


def make_sheet(pairs, out_path, left_label, right_label, thumb_width):
    resampling = getattr(Image, "Resampling", Image)
    resample_filter = getattr(resampling, "LANCZOS", getattr(Image, "BICUBIC", 3))
    label_h = 28
    pad = 12
    panels = []
    for pair in pairs:
        left = thumbnail(pair["left_path"], thumb_width, resample_filter)
        right = thumbnail(pair["right_path"], thumb_width, resample_filter)
        mask = mask_thumbnail(pair["mask_path"], thumb_width, resample_filter)
        panels.append((pair, left, right, mask))
    panel_w = thumb_width
    panel_h = max(max(left.height, right.height, mask.height) for _pair, left, right, mask in panels)
    sheet_w = pad + 3 * (panel_w + pad)
    sheet_h = pad + len(panels) * (label_h + panel_h + pad)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (14, 18, 22))
    draw = ImageDraw.Draw(sheet)
    headers = [left_label, right_label, "upper-tail gain/loss"]
    for row, (pair, left, right, mask) in enumerate(panels):
        y = pad + row * (label_h + panel_h + pad)
        frame_label = f"frame {pair['frame_index']:04d}"
        for col, (header, panel) in enumerate(zip(headers, [left, right, mask])):
            x = pad + col * (panel_w + pad)
            label = f"{header} / {frame_label}" if col == 0 else header
            draw.text((x + 6, y + 7), label, fill=(224, 234, 240))
            cell = Image.new("RGB", (panel_w, panel_h), (8, 10, 12))
            cell.paste(panel, ((panel_w - panel.width) // 2, (panel_h - panel.height) // 2))
            sheet.paste(cell, (x, y + label_h))
    sheet.save(out_path)


def aggregate(pairs):
    total_pixels = sum(pair["pixels"] for pair in pairs)
    total_gain = sum(pair["gain_count"] for pair in pairs)
    total_loss = sum(pair["loss_count"] for pair in pairs)
    total_pixels = max(1, total_pixels)
    return {
        "frame_count": len(pairs),
        "mean_tail_threshold": mean(pair["tail_threshold"] for pair in pairs),
        "gain_ratio": total_gain / float(total_pixels),
        "loss_ratio": total_loss / float(total_pixels),
        "net_gain_ratio": (total_gain - total_loss) / float(total_pixels),
        "mean_frame_gain_ratio": mean(pair["gain_ratio"] for pair in pairs),
        "mean_frame_loss_ratio": mean(pair["loss_ratio"] for pair in pairs),
        "mean_gain_luma": mean(pair["mean_gain_luma"] for pair in pairs),
        "mean_loss_luma": mean(pair["mean_loss_luma"] for pair in pairs),
        "strongest_gain_luma": max(pair["strongest_gain_luma"] for pair in pairs),
        "strongest_loss_luma": max(pair["strongest_loss_luma"] for pair in pairs),
    }


def render_report(summary):
    agg = summary["aggregate"]
    lines = [
        f"# {summary['title']}",
        "",
        "## Status",
        "",
        "Passed.",
        "",
        "This diagnostic uses existing rendered frame directories only; no simulation or Blender render was rerun.",
        "",
        "## Artifacts",
        "",
        f"- Diagnostic sheet: `{summary['diagnostic_sheet']}`",
        f"- Summary JSON: `{summary['summary_path']}`",
        f"- Mask directory: `{summary['mask_dir']}`",
        "",
        "## Thresholds",
        "",
        f"- Tail percentile: `{summary['thresholds']['tail_percentile']}`",
        f"- Minimum tail luminance: `{summary['thresholds']['min_tail_luma']}`",
        f"- Gain/loss delta threshold: `{summary['thresholds']['gain_threshold']}`",
        f"- Mean active tail threshold: `{agg['mean_tail_threshold']}`",
        "",
        "## Aggregate",
        "",
        f"- Gain ratio: `{agg['gain_ratio']}`",
        f"- Loss ratio: `{agg['loss_ratio']}`",
        f"- Net gain ratio: `{agg['net_gain_ratio']}`",
        f"- Mean gain luma delta: `{agg['mean_gain_luma']}`",
        f"- Mean loss luma delta: `{agg['mean_loss_luma']}`",
        f"- Strongest gain luma delta: `{agg['strongest_gain_luma']}`",
        f"- Strongest loss luma delta: `{agg['strongest_loss_luma']}`",
        "",
        "## Finding",
        "",
        summary.get("finding") or "Use amber pixels as upper-tail gain and blue pixels as upper-tail loss.",
        "",
        "## Next",
        "",
        summary.get("next") or "Use this mask to decide the next visible render adjustment.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Create upper-tail highlight gain/loss diagnostics")
    parser.add_argument("--left", required=True, help="baseline frame directory")
    parser.add_argument("--right", required=True, help="candidate frame directory")
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--frames", type=int, default=16)
    parser.add_argument("--thumb-width", type=int, default=320)
    parser.add_argument("--tail-percentile", type=float, default=0.95)
    parser.add_argument("--min-tail-luma", type=int, default=80)
    parser.add_argument("--gain-threshold", type=int, default=4)
    parser.add_argument("--report", help="optional Markdown report path")
    parser.add_argument("--title", default="Highlight Contribution Diagnostics")
    parser.add_argument("--finding", default="")
    parser.add_argument("--next", default="")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if Image is None:
        fail("Pillow is required to create highlight diagnostics")
    if not 0.0 < args.tail_percentile < 1.0:
        fail("--tail-percentile must be between 0 and 1")
    if args.frames <= 0:
        fail("--frames must be positive")
    if args.thumb_width <= 0:
        fail("--thumb-width must be positive")
    out_dir = Path(args.out_dir)
    mask_dir = out_dir / "masks"
    out_dir.mkdir(parents=True, exist_ok=True)
    mask_dir.mkdir(parents=True, exist_ok=True)
    left_frames = sorted_pngs(args.left)
    right_frames = sorted_pngs(args.right)
    common_count = min(len(left_frames), len(right_frames))
    if common_count <= 0:
        fail("diagnostic requires at least one frame pair")
    pairs = []
    for index in select_indices(common_count, args.frames):
        mask_path = mask_dir / f"mask_{index:04d}.png"
        pair = make_diagnostic_mask(
            left_frames[index],
            right_frames[index],
            mask_path,
            args.tail_percentile,
            args.min_tail_luma,
            args.gain_threshold,
        )
        pair["frame_index"] = index
        pairs.append(pair)
    sheet_path = str(out_dir / "diagnostic_sheet.png")
    make_sheet(pairs, sheet_path, args.left_label, args.right_label, args.thumb_width)
    summary_path = str(out_dir / "diagnostic_summary.json")
    summary = {
        "schema": "lsfs_highlight_contribution_diagnostics",
        "version": 1,
        "title": args.title,
        "left_label": args.left_label,
        "right_label": args.right_label,
        "frame_count": len(pairs),
        "diagnostic_sheet": sheet_path,
        "summary_path": summary_path,
        "mask_dir": str(mask_dir),
        "thresholds": {
            "tail_percentile": args.tail_percentile,
            "min_tail_luma": args.min_tail_luma,
            "gain_threshold": args.gain_threshold,
        },
        "aggregate": aggregate(pairs),
        "finding": args.finding,
        "next": args.next,
        "pairs": pairs,
    }
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
    except DiagnosticError as exc:
        print(f"status=fail error={exc}")
        raise SystemExit(1)
