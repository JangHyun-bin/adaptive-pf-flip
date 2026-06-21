#!/usr/bin/env python
"""Analyze peak and late-frame guards for a native probe sweep candidate."""

import argparse
import os
import shutil
from datetime import datetime, timezone

from build_bridge_review_package import (
    format_bytes,
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


SWEEP_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_probe_sweep"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_probe_guard"


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def load_sweep(path, root):
    resolved = require_file(resolve_path(path, root), "native probe sweep summary")
    summary = read_json(resolved)
    if summary.get("schema") != SWEEP_SCHEMA:
        raise SystemExit(f"{path}: expected {SWEEP_SCHEMA} schema")
    if summary.get("status") != "ready":
        raise SystemExit(f"{path}: sweep status is {summary.get('status')!r}")
    selected = summary.get("selected_candidate") or {}
    if not selected.get("frames"):
        raise SystemExit(f"{path}: selected candidate has no frames")
    return resolved, summary, selected


def copy_asset(src, assets_dir, name, label, root):
    source = require_file(resolve_path(src, root), label)
    dest = os.path.join(assets_dir, name)
    ensure_dir(os.path.dirname(dest))
    if os.path.abspath(source) != os.path.abspath(dest):
        shutil.copy2(source, dest)
    entry = {
        "label": label,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source_repo_path": posix_rel(source, root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def sort_frames(frames, key, reverse=True):
    return sorted(frames, key=lambda frame: (float(frame.get(key) or 0.0), int(frame.get("frame") or 0)), reverse=reverse)


def unique_guard_items(items, limit):
    seen = set()
    out = []
    for item in items:
        frame = item["frame"]
        frame_id = int(frame.get("frame") or 0)
        if frame_id in seen:
            continue
        seen.add(frame_id)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def late_frames(frames, fraction):
    ordered = sorted(frames, key=lambda frame: int(frame.get("frame") or 0))
    if not ordered:
        return []
    start = max(0, int(round(len(ordered) * (1.0 - fraction))))
    return ordered[start:]


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in assets
        if item.get("label", "").startswith("Guard Strip")
    )
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Candidate", summary.get("candidate", {}).get("label")),
            ("Max Delta", checks.get("max_abs_delta_from_s623")),
            ("Max MAD", checks.get("max_mean_abs_delta_from_s623")),
            ("Late Max Delta", checks.get("late_max_abs_delta_from_s623")),
            ("Late Max MAD", checks.get("late_max_mean_abs_delta_from_s623")),
            ("Guard", checks.get("guard_status")),
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 27px; font-weight: 670; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; min-height: 58px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    strong {{ display: block; font-size: 15px; word-break: break-word; }}
    figure {{ border: 1px solid var(--line); background: #0d1820; margin: 0 0 12px; }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Peak and late-frame guard strips for the selected native-probe sweep candidate.</p>
  <section class="tiles">{tiles}</section>
  <section>{figures}</section>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        f"Candidate: `{summary['candidate']['label']}`",
        "",
        "## Guard Checks",
        "",
        f"- Max abs delta from S623: `{checks.get('max_abs_delta_from_s623')}`",
        f"- Max mean abs delta from S623: `{checks.get('max_mean_abs_delta_from_s623')}`",
        f"- Late max abs delta from S623: `{checks.get('late_max_abs_delta_from_s623')}`",
        f"- Late max mean abs delta from S623: `{checks.get('late_max_mean_abs_delta_from_s623')}`",
        f"- Peak frame count: `{checks.get('peak_frame_count')}`",
        f"- Late frame count: `{checks.get('late_frame_count')}`",
        f"- Max abs tolerance: `{checks.get('max_abs_tolerance')}`",
        f"- Max MAD tolerance: `{checks.get('max_mad_tolerance')}`",
        f"- Late max MAD tolerance: `{checks.get('late_max_mad_tolerance')}`",
        f"- Guard status: `{checks.get('guard_status')}`",
        "",
        "## Guard Frames",
        "",
        "| Kind | Frame | Scene | Source | Max Delta | Max MAD | Strip |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("guard_frames") or []:
        frame = item.get("frame") or {}
        lines.append(
            f"| `{item.get('kind')}` | {frame.get('frame')} | {frame.get('scene_frame')} | "
            f"{frame.get('source_frame')} | {frame.get('max_abs_delta_from_s623')} | "
            f"{frame.get('mean_abs_delta_from_s623')} | `{item.get('asset', {}).get('source_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def analyze(args):
    root = os.getcwd()
    sweep_path, sweep_summary, selected = load_sweep(args.sweep_summary, root)
    frames = selected.get("frames") or []
    late = late_frames(frames, args.late_fraction)
    peak = sort_frames(frames, "max_abs_delta_from_s623")[:args.peak_count]
    mad_peak = sort_frames(frames, "mean_abs_delta_from_s623")[:args.peak_count]
    late_peak = sort_frames(late, "mean_abs_delta_from_s623")[:args.late_count]
    guard_frame_items = []
    for kind, group in (
        ("peak_delta", peak),
        ("peak_mad", mad_peak),
        ("late_mad", late_peak),
    ):
        for frame in group:
            guard_frame_items.append({"kind": kind, "frame": frame})
    guard_frame_items = unique_guard_items(guard_frame_items, args.max_gallery_strips)

    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = ensure_dir(os.path.join(out_dir, "gallery"))
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    assets = []
    guard_frames = []
    for index, item in enumerate(guard_frame_items):
        frame = item["frame"]
        asset = copy_asset(
            frame.get("strip_repo_path"),
            assets_dir,
            f"guard_strip_{index:02d}_frame_{int(frame.get('frame') or 0):04d}.png",
            f"Guard Strip {index + 1} {item['kind']} frame {frame.get('frame')}",
            root,
        )
        guard_frames.append({"kind": item["kind"], "frame": frame, "asset": asset})
        assets.append(asset)

    max_abs = max((int(frame.get("max_abs_delta_from_s623") or 0) for frame in frames), default=999)
    max_mad = max((float(frame.get("mean_abs_delta_from_s623") or 0.0) for frame in frames), default=999.0)
    late_max_abs = max((int(frame.get("max_abs_delta_from_s623") or 0) for frame in late), default=999)
    late_max_mad = max((float(frame.get("mean_abs_delta_from_s623") or 0.0) for frame in late), default=999.0)
    guard_ok = (
        max_abs <= args.max_abs_tolerance
        and max_mad <= args.max_mad_tolerance
        and late_max_mad <= args.late_max_mad_tolerance
    )
    checks = {
        "frames": len(frames),
        "late_frame_count": len(late),
        "peak_frame_count": len(peak),
        "max_abs_delta_from_s623": max_abs,
        "max_mean_abs_delta_from_s623": max_mad,
        "late_max_abs_delta_from_s623": late_max_abs,
        "late_max_mean_abs_delta_from_s623": late_max_mad,
        "max_abs_tolerance": args.max_abs_tolerance,
        "max_mad_tolerance": args.max_mad_tolerance,
        "late_max_mad_tolerance": args.late_max_mad_tolerance,
        "guard_status": "passed" if guard_ok else "review",
    }
    index_path = os.path.join(gallery_dir, "index.html")
    summary_path = os.path.abspath(args.summary) if args.summary else os.path.join(out_dir, "response_aov_scene_native_probe_guard_summary.json")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if guard_ok else "review",
        "source_sweep": {
            "repo_path": posix_rel(sweep_path, root),
            "schema": sweep_summary.get("schema"),
            "status": sweep_summary.get("status"),
            "sha256": sha256_file(sweep_path),
            "size": os.path.getsize(sweep_path),
        },
        "candidate": {
            "label": selected.get("label"),
            "strength": selected.get("strength"),
            "mask_size": selected.get("mask_size"),
            "mask_blur": selected.get("mask_blur"),
            "mask_power": selected.get("mask_power"),
            "volume_scale": selected.get("volume_scale"),
            "sparkle_scale": selected.get("sparkle_scale"),
        },
        "checks": checks,
        "guard_frames": guard_frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": index_path,
            "index_repo_path": posix_rel(index_path, root),
            "assets": assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(index_path, html_page(summary))
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        "status={status} guard={guard} max_abs={max_abs} max_mad={max_mad} late_mad={late_mad} summary={summary}".format(
            status=summary["status"],
            guard=checks["guard_status"],
            max_abs=max_abs,
            max_mad=max_mad,
            late_mad=late_max_mad,
            summary=summary_path,
        )
    )
    if summary["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sweep_summary", help="S626 native probe sweep summary JSON")
    parser.add_argument("out_dir", help="Output directory for guard report/gallery")
    parser.add_argument("--summary", help="Output summary JSON")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--peak-count", type=int, default=4)
    parser.add_argument("--late-count", type=int, default=4)
    parser.add_argument("--late-fraction", type=float, default=0.25)
    parser.add_argument("--max-gallery-strips", type=int, default=8)
    parser.add_argument("--max-abs-tolerance", type=int, default=10)
    parser.add_argument("--max-mad-tolerance", type=float, default=0.75)
    parser.add_argument("--late-max-mad-tolerance", type=float, default=0.75)
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Native Probe Guard")
    parser.add_argument(
        "--next",
        default="Use this guard result to decide whether to promote the selected sweep candidate into the backend adapter.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()
    if args.peak_count <= 0 or args.late_count <= 0 or args.max_gallery_strips <= 0:
        parser.error("counts must be positive")
    if args.late_fraction <= 0.0 or args.late_fraction > 1.0:
        parser.error("late-fraction must be in (0, 1]")
    analyze(args)


if __name__ == "__main__":
    main()
