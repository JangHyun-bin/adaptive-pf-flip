#!/usr/bin/env python
"""Summarize Mitsuba response candidates for local calibration decisions."""

import argparse
import csv
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


def parse_candidate(value):
    if "=" not in value:
        path = value
        label = os.path.splitext(os.path.basename(os.path.dirname(path)))[0]
        return label, path
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("candidate label cannot be empty")
    return label, path.strip()


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def csv_vec(values):
    if not values:
        return ""
    return ",".join(f"{safe_float(item):.8g}" for item in values)


def render_manifest_from_gap(gap):
    source = gap.get("source") or {}
    actual = source.get("actual_source") or {}
    return actual.get("path") or actual.get("repo_path")


def export_manifest_from_render(render):
    export = render.get("mitsuba_export") or {}
    return export.get("path") or export.get("repo_path")


def read_optional_json(path):
    resolved = resolve_path(path)
    if not resolved or not os.path.isfile(resolved):
        return None, None
    return read_json(resolved), resolved


def load_candidate(label, gap_path, root):
    gap_path = require_file(gap_path, f"{label} target-gap summary")
    gap = read_json(gap_path)
    if gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{gap_path}: expected lsfs_mitsuba_renderer_target_gap schema")
    actual_source, actual_source_path = read_optional_json(render_manifest_from_gap(gap))
    render = None
    render_path = None
    if actual_source and actual_source.get("schema") == "lsfs_mitsuba_xml_render":
        render = actual_source
        render_path = actual_source_path
    export = None
    export_path = None
    if render:
        export, export_path = read_optional_json(export_manifest_from_render(render))

    checks = gap.get("checks") or {}
    export_checks = (export or {}).get("checks") or {}
    material = (export or {}).get("water_mask_material_response") or {}
    patches = (export or {}).get("water_mask_patches") or {}
    render_checks = (render or {}).get("checks") or {}
    candidate = {
        "label": label,
        "status": gap.get("status"),
        "frames": safe_int(checks.get("frames")),
        "mean_gap_mad": safe_float(checks.get("mean_gap_mean_abs_diff")),
        "max_gap_mad": safe_float(checks.get("max_gap_mean_abs_diff")),
        "max_gap_abs": safe_int(checks.get("max_gap_max_abs_diff")),
        "gif_bytes": safe_int(checks.get("gif_bytes")),
        "render_elapsed_ms": safe_int(render_checks.get("total_elapsed_ms")),
        "patches_inserted": safe_int(export_checks.get("patches_inserted")),
        "candidate_vertices": safe_int(export_checks.get("candidate_vertices")),
        "response_faces": safe_int(export_checks.get("response_faces")),
        "candidate_faces": safe_int(export_checks.get("candidate_faces")),
        "response_bin_count": safe_int(material.get("response_bin_count"), 0),
        "face_limit": safe_int(material.get("face_limit")),
        "int_ior": safe_float(material.get("int_ior")),
        "response_alpha": safe_float(material.get("response_alpha")),
        "patch_limit": safe_int(patches.get("patch_limit")),
        "cluster_screen_radius": safe_float(patches.get("cluster_screen_radius")),
        "patch_min_radius": safe_float(patches.get("min_radius")),
        "patch_base_radius": safe_float(patches.get("base_radius")),
        "patch_max_radius": safe_float(patches.get("max_radius")),
        "patch_radiance": patches.get("radiance") or [],
        "patch_radiance_sum": sum(safe_float(item) for item in (patches.get("radiance") or [])),
        "has_material_response": bool(material.get("enabled")),
        "has_patch_response": bool(patches.get("enabled")),
        "gap_summary": {
            "path": gap_path,
            "repo_path": posix_rel(gap_path, root),
            "sha256": sha256_file(gap_path),
        },
        "actual_source_manifest": None,
        "render_manifest": None,
        "export_manifest": None,
    }
    candidate["response_complexity"] = (
        candidate["patches_inserted"]
        + candidate["response_faces"] / 100.0
        + candidate["response_bin_count"]
    )
    candidate["artifact_proxy"] = (
        candidate["max_gap_abs"]
        + candidate["patch_radiance_sum"] * max(1, candidate["patches_inserted"])
    )
    if actual_source_path:
        candidate["actual_source_manifest"] = {
            "path": actual_source_path,
            "repo_path": posix_rel(actual_source_path, root),
            "sha256": sha256_file(actual_source_path),
            "schema": (actual_source or {}).get("schema"),
        }
    if render_path:
        candidate["render_manifest"] = {
            "path": render_path,
            "repo_path": posix_rel(render_path, root),
            "sha256": sha256_file(render_path),
        }
    if export_path:
        candidate["export_manifest"] = {
            "path": export_path,
            "repo_path": posix_rel(export_path, root),
            "sha256": sha256_file(export_path),
        }
    return candidate


def dominates(a, b, objectives):
    better_or_equal = all(a[key] <= b[key] for key in objectives)
    strictly_better = any(a[key] < b[key] for key in objectives)
    return better_or_equal and strictly_better


def mark_pareto(candidates, objectives):
    for item in candidates:
        item["pareto"] = not any(
            other is not item and dominates(other, item, objectives)
            for other in candidates
        )


def write_csv(path, candidates):
    fieldnames = [
        "rank_max_gap",
        "pareto",
        "label",
        "status",
        "frames",
        "mean_gap_mad",
        "max_gap_mad",
        "max_gap_abs",
        "artifact_proxy",
        "response_complexity",
        "patches_inserted",
        "response_faces",
        "response_bin_count",
        "face_limit",
        "int_ior",
        "response_alpha",
        "patch_limit",
        "cluster_screen_radius",
        "patch_min_radius",
        "patch_base_radius",
        "patch_max_radius",
        "patch_radiance",
        "render_elapsed_ms",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rank, item in enumerate(candidates, start=1):
            row = {key: item.get(key) for key in fieldnames}
            row["rank_max_gap"] = rank
            row["patch_radiance"] = csv_vec(item.get("patch_radiance"))
            writer.writerow(row)


def markdown_report(summary, summary_path, csv_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"CSV: `{posix_rel(csv_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Ranking",
        "",
        "| Rank | Pareto | Candidate | Max Gap MAD | Mean Gap MAD | Max Gap | Patches | Response Faces | Artifact Proxy |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, item in enumerate(summary.get("candidates") or [], start=1):
        lines.append(
            f"| {rank} | `{item.get('pareto')}` | `{item.get('label')}` | "
            f"{item.get('max_gap_mad')} | {item.get('mean_gap_mad')} | "
            f"{item.get('max_gap_abs')} | {item.get('patches_inserted')} | "
            f"{item.get('response_faces')} | {item.get('artifact_proxy')} |"
        )
    lines.extend(["", "## Pareto Front", ""])
    for item in summary.get("pareto_front") or []:
        lines.append(
            f"- `{item.get('label')}`: max MAD `{item.get('max_gap_mad')}`, "
            f"mean MAD `{item.get('mean_gap_mad')}`, complexity `{item.get('response_complexity')}`"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    candidates = [
        load_candidate(label, path, root)
        for label, path in (parse_candidate(raw) for raw in args.candidate)
    ]
    if not candidates:
        raise SystemExit("no candidates were loaded")
    candidates.sort(key=lambda item: (item["max_gap_mad"], item["mean_gap_mad"], item["artifact_proxy"]))
    mark_pareto(candidates, ["max_gap_mad", "mean_gap_mad", "max_gap_abs", "response_complexity"])
    pareto_front = [item for item in candidates if item["pareto"]]
    generated = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "response_calibration_summary.json")
    csv_path = os.path.join(out_dir, "response_calibration_candidates.csv")
    summary = {
        "schema": "lsfs_mitsuba_response_calibration_summary",
        "version": 1,
        "generated_utc": generated,
        "title": args.title,
        "status": "ready",
        "objectives": ["max_gap_mad", "mean_gap_mad", "max_gap_abs", "response_complexity"],
        "candidate_count": len(candidates),
        "pareto_count": len(pareto_front),
        "best_max_gap": candidates[0]["label"],
        "best_mean_gap": min(candidates, key=lambda item: item["mean_gap_mad"])["label"],
        "candidates": candidates,
        "pareto_front": pareto_front,
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_csv(csv_path, candidates)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, csv_path, root, args.next))
    print(
        f"status=ready candidates={len(candidates)} pareto={len(pareto_front)} "
        f"best_max_gap={summary['best_max_gap']} csv={csv_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize Mitsuba response candidates for calibration")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", action="append", required=True, help="LABEL=renderer_target_gap_summary.json")
    parser.add_argument("--title", default="Mitsuba Response Calibration Summary")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this calibration summary to choose the next bounded renderer response sweep.")
    args = parser.parse_args(argv)
    build(args)


if __name__ == "__main__":
    main()
