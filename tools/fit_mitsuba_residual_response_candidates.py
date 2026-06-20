#!/usr/bin/env python
"""Rank Mitsuba residual-response candidates and fit the next safe search range."""

import argparse
import math
import os
from datetime import datetime, timezone

from build_bridge_review_package import (
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


def candidate_arg(values):
    if len(values) != 3:
        raise argparse.ArgumentTypeError("candidate requires LABEL GAP_SUMMARY EXPORT_MANIFEST")
    return {
        "label": values[0],
        "gap_summary": values[1],
        "export_manifest": values[2],
    }


def resolve_path(path):
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def read_gap(path):
    path = require_file(resolve_path(path), "target gap summary")
    payload = read_json(path)
    if payload.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_renderer_target_gap schema")
    return path, payload


def read_export(path):
    path = require_file(resolve_path(path), "Mitsuba export")
    payload = read_json(path)
    if payload.get("schema") != "lsfs_mitsuba_xml_export":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_xml_export schema")
    return path, payload


def frame_map(gap):
    return {frame.get("output_frame"): frame for frame in gap.get("frames") or []}


def gap_checks(gap):
    checks = gap.get("checks") or {}
    return {
        "mean_gap_mad": float(checks.get("mean_gap_mean_abs_diff") or 0.0),
        "max_gap_mad": float(checks.get("max_gap_mean_abs_diff") or 0.0),
        "max_abs_gap": float(checks.get("max_gap_max_abs_diff") or 0.0),
        "frames": int(checks.get("frames") or 0),
        "missing_references": int(checks.get("missing_references") or 0),
    }


def response_settings(export):
    response = export.get("residual_response_patches") or {}
    return {
        "output_frames": response.get("output_frames"),
        "request_limit": response.get("request_limit"),
        "per_frame_request_limit": response.get("per_frame_request_limit"),
        "patch_limit": response.get("patch_limit"),
        "radius_scale": response.get("radius_scale"),
        "radiance_scale": response.get("radiance_scale"),
        "min_radius": response.get("min_radius"),
        "max_radius": response.get("max_radius"),
        "bbox_padding": response.get("bbox_padding"),
    }


def frame_deltas(baseline_gap, candidate_gap):
    baseline = frame_map(baseline_gap)
    rows = []
    for output_frame, candidate in frame_map(candidate_gap).items():
        base = baseline.get(output_frame)
        if not base:
            continue
        rows.append({
            "output_frame": output_frame,
            "baseline_gap_mad": base.get("gap_mean_abs_diff"),
            "candidate_gap_mad": candidate.get("gap_mean_abs_diff"),
            "delta_gap_mad": candidate.get("gap_mean_abs_diff") - base.get("gap_mean_abs_diff"),
            "baseline_max_abs_gap": base.get("gap_max_abs_diff"),
            "candidate_max_abs_gap": candidate.get("gap_max_abs_diff"),
            "delta_max_abs_gap": candidate.get("gap_max_abs_diff") - base.get("gap_max_abs_diff"),
        })
    rows.sort(key=lambda item: item["delta_gap_mad"])
    return rows


def candidate_row(label, gap_path, gap, export_path, export, baseline_gap, baseline_checks, args, root):
    checks = gap_checks(gap)
    settings = response_settings(export)
    safe = (
        checks["missing_references"] == 0
        and checks["max_abs_gap"] <= args.max_abs_gap_limit
        and checks["max_gap_mad"] <= baseline_checks["max_gap_mad"] + args.max_gap_mad_tolerance
    )
    return {
        "label": label,
        "safe": safe,
        "status": gap.get("status"),
        "gap_summary": {
            "path": gap_path,
            "repo_path": posix_rel(gap_path, root),
            "sha256": sha256_file(gap_path),
        },
        "export_manifest": {
            "path": export_path,
            "repo_path": posix_rel(export_path, root),
            "sha256": sha256_file(export_path),
        },
        "settings": settings,
        "checks": checks,
        "deltas": {
            "mean_gap_mad": checks["mean_gap_mad"] - baseline_checks["mean_gap_mad"],
            "max_gap_mad": checks["max_gap_mad"] - baseline_checks["max_gap_mad"],
            "max_abs_gap": checks["max_abs_gap"] - baseline_checks["max_abs_gap"],
        },
        "frame_deltas": frame_deltas(baseline_gap, gap),
    }


def objective_key(row):
    checks = row["checks"]
    deltas = row["deltas"]
    safety_penalty = 0 if row["safe"] else 1
    return (
        safety_penalty,
        checks["max_gap_mad"],
        checks["mean_gap_mad"],
        checks["max_abs_gap"],
        deltas["max_gap_mad"],
    )


def fit_energy_hint(candidates, baseline_checks):
    points = []
    for item in candidates:
        settings = item.get("settings") or {}
        output_frames = settings.get("output_frames")
        radius_scale = settings.get("radius_scale")
        radiance_scale = settings.get("radiance_scale")
        if output_frames != [13] or radius_scale is None or radiance_scale is None:
            continue
        energy = float(radius_scale) * float(radiance_scale)
        points.append((energy, item["checks"]["max_gap_mad"], item["label"], radius_scale, radiance_scale))
    if len(points) < 2:
        return None
    points.append((0.0, baseline_checks["max_gap_mad"], "baseline", 0.0, 0.0))
    points.sort()
    best = min(points, key=lambda item: item[1])
    hint = {
        "fit_kind": "output13_energy_scan",
        "sample_points": [
            {
                "label": label,
                "energy": energy,
                "max_gap_mad": value,
                "radius_scale": radius,
                "radiance_scale": radiance,
            }
            for energy, value, label, radius, radiance in points
        ],
        "best_sample": {
            "label": best[2],
            "energy": best[0],
            "max_gap_mad": best[1],
        },
    }
    if len(points) >= 3:
        x1, y1 = points[0][0], points[0][1]
        x2, y2 = points[1][0], points[1][1]
        x3, y3 = points[-1][0], points[-1][1]
        denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
        if abs(denom) > 1.0e-12:
            a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
            b = (x3 * x3 * (y1 - y2) + x2 * x2 * (y3 - y1) + x1 * x1 * (y2 - y3)) / denom
            if a > 0.0:
                optimum = -b / (2.0 * a)
                lo = min(point[0] for point in points)
                hi = max(point[0] for point in points)
                optimum = max(lo, min(hi, optimum))
                hint["quadratic_energy_hint"] = {
                    "energy": optimum,
                    "note": "Use as a narrow search center, not as a direct preset.",
                }
    return hint


def markdown_report(summary, summary_path, root):
    baseline = summary["baseline"]["checks"]
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Baseline",
        "",
        f"- Gap summary: `{summary['baseline']['gap_summary']['repo_path']}`",
        f"- Mean gap MAD: `{baseline['mean_gap_mad']}`",
        f"- Max gap MAD: `{baseline['max_gap_mad']}`",
        f"- Max absolute gap: `{baseline['max_abs_gap']}`",
        "",
        "## Candidate Ranking",
        "",
        "| Rank | Candidate | Safe | Mean Gap MAD | Max Gap MAD | Max Gap | Delta Max MAD | Delta Mean MAD |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, item in enumerate(summary.get("ranking") or [], start=1):
        checks = item["checks"]
        deltas = item["deltas"]
        lines.append(
            f"| {rank} | `{item['label']}` | `{item['safe']}` | "
            f"{checks['mean_gap_mad']} | {checks['max_gap_mad']} | {checks['max_abs_gap']} | "
            f"{deltas['max_gap_mad']} | {deltas['mean_gap_mad']} |"
        )
    best = summary.get("best_safe_candidate")
    if best:
        lines.extend([
            "",
            "## Best Safe Candidate",
            "",
            f"- Label: `{best['label']}`",
            f"- Max gap MAD: `{best['checks']['max_gap_mad']}`",
            f"- Mean gap MAD: `{best['checks']['mean_gap_mad']}`",
            f"- Max absolute gap: `{best['checks']['max_abs_gap']}`",
        ])
    hint = summary.get("fit_hint")
    if hint:
        lines.extend(["", "## Fit Hint", ""])
        lines.append(f"- Kind: `{hint.get('fit_kind')}`")
        lines.append(f"- Best sampled energy: `{(hint.get('best_sample') or {}).get('energy')}`")
        q = hint.get("quadratic_energy_hint")
        if q:
            lines.append(f"- Quadratic energy center: `{q.get('energy')}`")
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def fit(args):
    root = os.getcwd()
    baseline_path, baseline_gap = read_gap(args.baseline_gap_summary)
    baseline_checks = gap_checks(baseline_gap)
    candidates = []
    for label, gap_path, export_path in args.candidate:
        resolved_gap_path, gap = read_gap(gap_path)
        resolved_export_path, export = read_export(export_path)
        candidates.append(candidate_row(
            label,
            resolved_gap_path,
            gap,
            resolved_export_path,
            export,
            baseline_gap,
            baseline_checks,
            args,
            root,
        ))
    ranking = sorted(candidates, key=objective_key)
    safe_candidates = [item for item in ranking if item["safe"]]
    best = safe_candidates[0] if safe_candidates else None
    summary = {
        "schema": "lsfs_mitsuba_residual_response_fit",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if candidates else "review",
        "baseline": {
            "gap_summary": {
                "path": baseline_path,
                "repo_path": posix_rel(baseline_path, root),
                "sha256": sha256_file(baseline_path),
            },
            "checks": baseline_checks,
        },
        "settings": {
            "max_abs_gap_limit": args.max_abs_gap_limit,
            "max_gap_mad_tolerance": args.max_gap_mad_tolerance,
        },
        "ranking": ranking,
        "best_safe_candidate": best,
        "fit_hint": fit_energy_hint(candidates, baseline_checks),
        "next": args.next,
    }
    os.makedirs(os.path.abspath(args.out_dir), exist_ok=True)
    summary_path = os.path.join(os.path.abspath(args.out_dir), "residual_response_fit_summary.json")
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={summary['status']} candidates={len(candidates)} "
        f"best_safe={(best or {}).get('label')} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fit and rank Mitsuba residual-response candidates")
    parser.add_argument("baseline_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", nargs=3, action="append", metavar=("LABEL", "GAP_SUMMARY", "EXPORT_MANIFEST"), required=True)
    parser.add_argument("--max-abs-gap-limit", type=float, default=177.0)
    parser.add_argument("--max-gap-mad-tolerance", type=float, default=0.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S455 Mitsuba Residual Response Fit")
    parser.add_argument("--next", default="Use the best safe candidate and fitted range to drive the next residual-response search.")
    args = parser.parse_args(argv)
    if args.max_abs_gap_limit <= 0.0:
        parser.error("max-abs-gap-limit must be positive")
    if args.max_gap_mad_tolerance < 0.0:
        parser.error("max-gap-mad-tolerance must be non-negative")
    fit(args)


if __name__ == "__main__":
    main()
