#!/usr/bin/env python
"""Filter a Mitsuba secondary 3D sidecar by a per-frame alpha mask source."""

import argparse
import json
import os
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)

SECONDARY_CHANNELS = ("spray", "foam", "bubble", "droplet")


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to filter a sidecar by masks")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def sidecar_ref(frame):
    sidecar = frame.get("sidecar") or {}
    return sidecar.get("path") or sidecar.get("repo_path")


def mask_ref(frame):
    return frame.get("layer_path") or frame.get("layer_repo_path")


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def max_alpha_near(alpha, x, y, radius):
    width, height = alpha.size
    px = int(round(x))
    py = int(round(y))
    lo_x = max(0, px - radius)
    hi_x = min(width - 1, px + radius)
    lo_y = max(0, py - radius)
    hi_y = min(height - 1, py + radius)
    pixels = alpha.load()
    best = 0
    for yy in range(lo_y, hi_y + 1):
        for xx in range(lo_x, hi_x + 1):
            best = max(best, int(pixels[xx, yy]))
    return best


def row_hits_mask(row, alpha, args):
    camera = row.get("camera") or {}
    if args.require_in_frame and not camera.get("in_frame"):
        return False
    ndc = camera.get("ndc") or []
    if len(ndc) != 2:
        return False
    width, height = alpha.size
    x = float(ndc[0]) * (width - 1)
    y = float(ndc[1]) * (height - 1)
    if x < 0.0 or y < 0.0 or x > width - 1 or y > height - 1:
        return False
    return max_alpha_near(alpha, x, y, args.sample_radius) >= args.alpha_threshold


def count_channels(rows):
    counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    for row in rows:
        channel = (row.get("channel") or "").strip()
        if channel in counts:
            counts[channel] += 1
    return counts


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Source particles: `{checks.get('source_particles')}`",
        f"- Filtered particles: `{checks.get('filtered_particles')}`",
        f"- Retention ratio: `{checks.get('retention_ratio')}`",
        f"- Sidecar bytes: `{format_bytes(checks.get('sidecar_bytes', 0))}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        "",
        "## Channel Counts",
        "",
        "| Channel | Source | Filtered |",
        "| --- | ---: | ---: |",
    ]
    source_counts = checks.get("source_channel_counts") or {}
    filtered_counts = checks.get("filtered_channel_counts") or {}
    for channel in SECONDARY_CHANNELS:
        lines.append(f"| `{channel}` | {source_counts.get(channel, 0)} | {filtered_counts.get(channel, 0)} |")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Source | Filtered | Mask | Sidecar |",
        "| ---: | ---: | ---: | --- | --- |",
    ])
    for frame in summary.get("frames", []):
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('source_count')} | "
            f"{frame.get('filtered_count')} | `{frame.get('mask_repo_path')}` | "
            f"`{(frame.get('sidecar') or {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    sidecar_path = require_file(args.sidecar_summary, "secondary 3D sidecar")
    mask_path = require_file(args.mask_source, "mask source")
    sidecar = read_json(sidecar_path)
    masks = read_json(mask_path)
    if sidecar.get("schema") != "lsfs_mitsuba_secondary_3d_sidecar":
        raise SystemExit(f"{args.sidecar_summary}: expected lsfs_mitsuba_secondary_3d_sidecar")
    if masks.get("schema") not in ("lsfs_mitsuba_secondary_composite", "lsfs_mitsuba_composite_grade"):
        raise SystemExit(f"{args.mask_source}: expected mask-source compatible summary")

    sidecar_frames = frame_map(sidecar)
    mask_frames = frame_map(masks)
    outputs = sorted(set(sidecar_frames) & set(mask_frames))
    if not outputs:
        raise SystemExit("no overlapping sidecar/mask output frames")

    out_dir = resolve_path(args.out_dir)
    sidecar_dir = os.path.join(out_dir, "secondary_3d")
    os.makedirs(sidecar_dir, exist_ok=True)

    output_frames = []
    failures = []
    source_channel_counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    filtered_channel_counts = {channel: 0 for channel in SECONDARY_CHANNELS}
    sidecar_bytes = 0
    source_particles = 0
    filtered_particles = 0

    for index, output_frame in enumerate(outputs):
        source_frame = sidecar_frames[output_frame]
        mask_frame = mask_frames[output_frame]
        source_jsonl = resolve_path(sidecar_ref(source_frame))
        alpha_image = resolve_path(mask_ref(mask_frame))
        if not source_jsonl or not os.path.isfile(source_jsonl):
            failures.append({"kind": "missing_sidecar_jsonl", "output_frame": output_frame, "path": source_jsonl})
            continue
        if not alpha_image or not os.path.isfile(alpha_image):
            failures.append({"kind": "missing_mask_image", "output_frame": output_frame, "path": alpha_image})
            continue

        rows = read_jsonl(source_jsonl)
        alpha = Image.open(alpha_image).convert("RGBA").split()[3]
        kept = [row for row in rows if row_hits_mask(row, alpha, args)]
        out_path = os.path.join(sidecar_dir, f"frame_{index:04d}_secondary_3d.jsonl")
        write_jsonl(out_path, kept)
        sidecar_bytes += os.path.getsize(out_path)
        source_count = len(rows)
        filtered_count = len(kept)
        source_particles += source_count
        filtered_particles += filtered_count
        source_counts = count_channels(rows)
        filtered_counts = count_channels(kept)
        for channel in SECONDARY_CHANNELS:
            source_channel_counts[channel] += source_counts[channel]
            filtered_channel_counts[channel] += filtered_counts[channel]
        frame_item = dict(source_frame)
        frame_item.update({
            "sidecar": {
                "path": out_path,
                "repo_path": posix_rel(out_path, root),
                "sha256": sha256_file(out_path),
                "size": os.path.getsize(out_path),
            },
            "source_sidecar_repo_path": posix_rel(source_jsonl, root),
            "mask_repo_path": posix_rel(alpha_image, root),
            "source_count": source_count,
            "filtered_count": filtered_count,
            "counts": {
                "total": filtered_count,
                **filtered_counts,
            },
            "available_counts": source_counts,
            "projected_counts": filtered_counts,
            "in_frame_counts": filtered_counts,
            "retention_ratio": filtered_count / float(max(1, source_count)),
        })
        output_frames.append(frame_item)

    retention_ratio = filtered_particles / float(max(1, source_particles))
    summary_path = os.path.join(out_dir, "secondary_3d_sidecar.json")
    summary = {
        "schema": "lsfs_mitsuba_secondary_3d_sidecar",
        "version": 1,
        "title": args.title,
        "status": "ready" if output_frames and not failures else "review",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_sidecar": {
            "path": sidecar_path,
            "repo_path": posix_rel(sidecar_path, root),
            "schema": sidecar.get("schema"),
            "sha256": sha256_file(sidecar_path),
        },
        "mask_source": {
            "path": mask_path,
            "repo_path": posix_rel(mask_path, root),
            "schema": masks.get("schema"),
            "sha256": sha256_file(mask_path),
        },
        "settings": {
            "alpha_threshold": args.alpha_threshold,
            "sample_radius": args.sample_radius,
            "require_in_frame": args.require_in_frame,
        },
        "checks": {
            "frames": len(output_frames),
            "source_particles": source_particles,
            "filtered_particles": filtered_particles,
            "retention_ratio": retention_ratio,
            "missing_references": len(failures),
            "sidecar_bytes": sidecar_bytes,
            "source_channel_counts": source_channel_counts,
            "filtered_channel_counts": filtered_channel_counts,
            "secondary_particles": filtered_particles,
            "in_front_particles": filtered_particles,
            "in_frame_particles": filtered_particles,
            "channel_counts": filtered_channel_counts,
            "channel_projected_counts": filtered_channel_counts,
            "channel_in_frame_counts": filtered_channel_counts,
        },
        "frames": output_frames,
        "failures": failures,
        "next": args.next,
    }
    write_json(summary_path, summary)
    if args.report:
        write_text(resolve_path(args.report), markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} frames={len(output_frames)} "
        f"filtered={filtered_particles}/{source_particles} ratio={retention_ratio:.6f} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sidecar_summary")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--alpha-threshold", type=int, default=8)
    parser.add_argument("--sample-radius", type=int, default=2)
    parser.add_argument("--allow-out-of-frame", action="store_false", dest="require_in_frame")
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Mask-Filtered Secondary 3D Sidecar")
    parser.add_argument("--next", default="Use this filtered sidecar in a native Mitsuba secondary material/pass candidate.")
    args = parser.parse_args(argv)
    if not (0 <= args.alpha_threshold <= 255):
        parser.error("alpha-threshold must be in [0, 255]")
    if args.sample_radius < 0:
        parser.error("sample-radius must be non-negative")
    build(args)


if __name__ == "__main__":
    main()
