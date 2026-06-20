#!/usr/bin/env python
"""Convert signed Mitsuba target-gap requests into residual patch requests."""

import argparse
import math
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


def parse_csv(value):
    return {item.strip() for item in str(value).split(",") if item.strip()}


def scaled_radiance(request, args):
    response = request.get("suggested_response") or {}
    strength = max(0.0, float(response.get("strength") or 0.0))
    mean_abs = max(0.0, float(request.get("mean_abs_luma") or 0.0))
    scale = args.radiance_scale * (args.radiance_strength_base + strength * args.radiance_strength_scale)
    scale *= max(args.min_luma_scale, min(args.max_luma_scale, mean_abs / 128.0))
    return [max(0.0, value * scale) for value in args.radiance_vec]


def convert_request(request, args):
    response = request.get("suggested_response") or {}
    center = response.get("screen_center_px") or request.get("weighted_center_px") or request.get("center_px")
    radius = response.get("screen_radius_px") or request.get("radius_px")
    if not center or radius is None:
        return None
    radius = max(args.min_screen_radius, min(args.max_screen_radius, float(radius) * args.radius_scale))
    mean_abs = max(0.0, float(request.get("mean_abs_luma") or 0.0))
    max_abs = max(0.0, float(request.get("max_abs_luma") or 0.0))
    return {
        "frame": request.get("frame"),
        "output_frame": request.get("output_frame"),
        "region": request.get("region"),
        "direction": request.get("direction"),
        "bbox": request.get("bbox"),
        "center_px": request.get("center_px"),
        "weighted_center_px": request.get("weighted_center_px"),
        "radius_px": radius,
        "area_px": request.get("area_px"),
        "mean_residual": mean_abs,
        "max_residual": max_abs,
        "score": float(request.get("score") or 0.0),
        "signed_gap_source": {
            "mean_signed_luma": request.get("mean_signed_luma"),
            "mean_abs_luma": mean_abs,
            "max_abs_luma": max_abs,
            "frame_weight": request.get("frame_weight"),
            "suggested_response": response,
        },
        "suggested_patch": {
            "screen_center_px": center,
            "screen_radius_px": radius,
            "radiance_scalar": max(scaled_radiance(request, args)),
            "radiance_rgb": scaled_radiance(request, args),
            "source_luma_min": args.source_luma_min,
        },
        "notes": "converted from signed target-gap highlight brighten request",
    }


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
        f"- Source requests: `{checks.get('source_requests')}`",
        f"- Converted requests: `{checks.get('requests')}`",
        f"- Max residual: `{checks.get('max_residual')}`",
        f"- Mean selected residual: `{checks.get('mean_selected_residual')}`",
        "",
        "## Top Requests",
        "",
        "| Rank | Output | Region | Direction | Score | Mean Residual | Radius | Radiance | BBox |",
        "| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for rank, request in enumerate(summary.get("requests") or [], start=1):
        patch = request.get("suggested_patch") or {}
        lines.append(
            f"| {rank} | {request.get('output_frame')} | `{request.get('region')}` | "
            f"`{request.get('direction')}` | {request.get('score', 0.0):.3f} | "
            f"{request.get('mean_residual', 0.0):.3f} | {request.get('radius_px', 0.0):.3f} | "
            f"{patch.get('radiance_scalar', 0.0):.4f} | `{request.get('bbox')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def convert(args):
    root = os.getcwd()
    source_path = require_file(args.signed_gap_analysis, "signed gap analysis")
    source = read_json(source_path)
    if source.get("schema") != "lsfs_mitsuba_signed_target_gap_analysis":
        raise SystemExit(f"{args.signed_gap_analysis}: expected lsfs_mitsuba_signed_target_gap_analysis schema")
    if source.get("status") != "ready":
        raise SystemExit(f"{args.signed_gap_analysis}: source status is {source.get('status')!r}")

    regions = parse_csv(args.regions)
    directions = parse_csv(args.directions)
    requests = []
    source_requests = source.get("requests") or []
    for request in source_requests:
        if request.get("region") not in regions:
            continue
        if request.get("direction") not in directions:
            continue
        if float(request.get("score") or 0.0) < args.min_score:
            continue
        converted = convert_request(request, args)
        if converted is not None:
            requests.append(converted)
        if len(requests) >= args.max_requests:
            break
    requests.sort(key=lambda item: item.get("score") or 0.0, reverse=True)

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    selected_pixels = sum(int(request.get("area_px") or 0) for request in requests)
    residual_sum = sum(float(request.get("mean_residual") or 0.0) * int(request.get("area_px") or 0) for request in requests)
    summary = {
        "schema": "lsfs_mitsuba_target_residual_analysis",
        "subschema": "lsfs_mitsuba_signed_gap_residual_requests",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if requests else "review",
        "sources": {
            "signed_gap_analysis": {
                "path": source_path,
                "repo_path": posix_rel(source_path, root),
                "sha256": sha256_file(source_path),
            },
        },
        "settings": {
            "regions": sorted(regions),
            "directions": sorted(directions),
            "max_requests": args.max_requests,
            "min_score": args.min_score,
            "radius_scale": args.radius_scale,
            "min_screen_radius": args.min_screen_radius,
            "max_screen_radius": args.max_screen_radius,
            "radiance": args.radiance_vec,
            "radiance_scale": args.radiance_scale,
            "radiance_strength_base": args.radiance_strength_base,
            "radiance_strength_scale": args.radiance_strength_scale,
            "min_luma_scale": args.min_luma_scale,
            "max_luma_scale": args.max_luma_scale,
        },
        "checks": {
            "source_requests": len(source_requests),
            "requests": len(requests),
            "selected_pixels": selected_pixels,
            "mean_selected_residual": residual_sum / float(max(1, selected_pixels)),
            "max_residual": max((float(request.get("max_residual") or 0.0) for request in requests), default=0.0),
            "estimated_request_bytes": 0,
        },
        "requests": requests,
        "frames": source.get("frames") or [],
        "gallery": source.get("gallery") or {},
        "next": args.next,
    }
    summary_path = os.path.join(out_dir, "target_residual_analysis.json")
    write_json(summary_path, summary)
    summary["checks"]["estimated_request_bytes"] = os.path.getsize(summary_path)
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} requests={len(requests)} "
        f"max_residual={summary['checks']['max_residual']:.3f} "
        f"bytes={format_bytes(summary['checks']['estimated_request_bytes'])} summary={summary_path}"
    )
    if summary["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def parse_vec3(value, name):
    parts = [part.strip() for part in str(value).split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"{name} must contain three comma-separated numbers")
    try:
        vec = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} contains non-numeric values") from exc
    return vec


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert signed target-gap requests to residual patch requests")
    parser.add_argument("signed_gap_analysis")
    parser.add_argument("out_dir")
    parser.add_argument("--regions", default="highlight")
    parser.add_argument("--directions", default="brighten")
    parser.add_argument("--max-requests", type=int, default=12)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--min-screen-radius", type=float, default=8.0)
    parser.add_argument("--max-screen-radius", type=float, default=84.0)
    parser.add_argument("--radiance", default="0.82,1.02,1.34")
    parser.add_argument("--radiance-scale", type=float, default=0.75)
    parser.add_argument("--radiance-strength-base", type=float, default=0.40)
    parser.add_argument("--radiance-strength-scale", type=float, default=0.95)
    parser.add_argument("--min-luma-scale", type=float, default=0.35)
    parser.add_argument("--max-luma-scale", type=float, default=1.15)
    parser.add_argument("--source-luma-min", type=float, default=120.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Signed Gap Residual Requests")
    parser.add_argument("--next", default="Use these requests with add_mitsuba_residual_response_patches.py.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.max_requests <= 0:
        parser.error("max-requests must be positive")
    if args.min_score < 0.0:
        parser.error("min-score must be non-negative")
    if args.radius_scale <= 0.0:
        parser.error("radius-scale must be positive")
    if args.min_screen_radius <= 0.0 or args.max_screen_radius <= 0.0:
        parser.error("screen radius bounds must be positive")
    if args.min_screen_radius > args.max_screen_radius:
        parser.error("min-screen-radius cannot exceed max-screen-radius")
    if args.radiance_scale < 0.0:
        parser.error("radiance-scale must be non-negative")
    if args.radiance_strength_base < 0.0 or args.radiance_strength_scale < 0.0:
        parser.error("radiance strength factors must be non-negative")
    if args.min_luma_scale < 0.0 or args.max_luma_scale <= 0.0:
        parser.error("luma scale bounds must be non-negative and positive")
    if args.min_luma_scale > args.max_luma_scale:
        parser.error("min-luma-scale cannot exceed max-luma-scale")
    args.radiance_vec = parse_vec3(args.radiance, "radiance")
    if min(args.radiance_vec) < 0.0:
        parser.error("radiance values must be non-negative")
    convert(args)


if __name__ == "__main__":
    main()
