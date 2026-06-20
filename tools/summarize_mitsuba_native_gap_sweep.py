#!/usr/bin/env python
"""Summarize and rank Mitsuba native target-gap sweep candidates."""

import argparse
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


def parse_candidate(value):
    if "=" in value:
        label, path = value.split("=", 1)
    else:
        path = value
        label = os.path.splitext(os.path.basename(path))[0]
    return label.strip(), path.strip()


def candidate_entry(value, root):
    label, path = parse_candidate(value)
    resolved = require_file(path, f"{label} gap summary")
    payload = read_json(resolved)
    if payload.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_renderer_target_gap schema")
    checks = payload.get("checks") or {}
    source = payload.get("source") or {}
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "status": payload.get("status"),
        "frames": checks.get("frames"),
        "missing_references": checks.get("missing_references"),
        "mean_gap_mean_abs_diff": checks.get("mean_gap_mean_abs_diff"),
        "max_gap_mean_abs_diff": checks.get("max_gap_mean_abs_diff"),
        "max_gap_max_abs_diff": checks.get("max_gap_max_abs_diff"),
        "gif_bytes": checks.get("gif_bytes"),
        "actual_source_kind": ((source.get("actual_source") or {}).get("kind") or "handoff_base_preview"),
        "public_target_url": source.get("public_target_url"),
        "gallery_index": (payload.get("gallery") or {}).get("index_repo_path"),
    }


def sort_key(item):
    return (
        item.get("max_gap_mean_abs_diff") if item.get("max_gap_mean_abs_diff") is not None else 1e9,
        item.get("mean_gap_mean_abs_diff") if item.get("mean_gap_mean_abs_diff") is not None else 1e9,
    )


def markdown_report(summary, out_path, root):
    best = summary.get("best") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(out_path, root)}`",
        f"Best candidate: `{best.get('label')}`",
        f"Best max gap MAD: `{best.get('max_gap_mean_abs_diff')}`",
        "",
        "## Ranking",
        "",
        "| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for index, item in enumerate(summary.get("ranking", []), start=1):
        lines.append(
            f"| {index} | `{item.get('label')}` | `{item.get('status')}` | {item.get('frames')} | "
            f"{item.get('mean_gap_mean_abs_diff')} | {item.get('max_gap_mean_abs_diff')} | "
            f"{item.get('max_gap_max_abs_diff')} | `{item.get('actual_source_kind')}` |"
        )
    lines.extend([
        "",
        "## Inputs",
        "",
    ])
    for item in summary.get("candidates", []):
        lines.append(
            f"- `{item.get('label')}`: `{item.get('repo_path')}` "
            f"({format_bytes(item.get('gif_bytes') or 0)} GIF)"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize Mitsuba native target-gap sweep candidates")
    parser.add_argument("candidate", nargs="+", help="label=path or path to lsfs_mitsuba_renderer_target_gap summary")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Native Gap Sweep Summary")
    parser.add_argument(
        "--next",
        default="Use the best ranked candidate as the next renderer-native baseline.",
    )
    args = parser.parse_args(argv)
    root = os.getcwd()
    candidates = [candidate_entry(value, root) for value in args.candidate]
    ranking = sorted(candidates, key=sort_key)
    best = ranking[0] if ranking else None
    summary = {
        "schema": "lsfs_mitsuba_native_gap_sweep_summary",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if best else "failed",
        "best": best,
        "ranking": ranking,
        "candidates": candidates,
        "next": args.next,
    }
    out_path = os.path.abspath(args.out)
    write_json(out_path, summary)
    report_path = os.path.abspath(args.report) if args.report else os.path.splitext(out_path)[0] + ".md"
    write_text(report_path, markdown_report(summary, out_path, root))
    print(
        f"status={summary['status']} candidates={len(candidates)} "
        f"best={best.get('label') if best else 'n/a'} max_gap={best.get('max_gap_mean_abs_diff') if best else 'n/a'} "
        f"out={out_path}"
    )
    print(f"report={report_path}")
    if summary["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
