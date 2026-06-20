#!/usr/bin/env python
"""Summarize and rank Mitsuba secondary native candidate gap summaries."""

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
        label = os.path.splitext(os.path.basename(os.path.dirname(path)))[0] or os.path.splitext(os.path.basename(path))[0]
    return label.strip(), path.strip()


def candidate_entry(value, root):
    label, path = parse_candidate(value)
    resolved = require_file(path, f"{label} candidate gap summary")
    payload = read_json(resolved)
    if payload.get("schema") != "lsfs_mitsuba_secondary_native_candidate_gap":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_secondary_native_candidate_gap schema")
    checks = payload.get("checks") or {}
    verdict = payload.get("verdict") or {}
    gallery = payload.get("gallery") or {}
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "status": payload.get("status"),
        "decision": verdict.get("decision"),
        "frames": checks.get("frames"),
        "missing_references": checks.get("missing_references"),
        "mean_candidate_contract_mean_abs_diff": checks.get("mean_candidate_contract_mean_abs_diff"),
        "max_candidate_contract_mean_abs_diff": checks.get("max_candidate_contract_mean_abs_diff"),
        "mean_candidate_target_mean_abs_diff": checks.get("mean_candidate_target_mean_abs_diff"),
        "max_candidate_target_mean_abs_diff": checks.get("max_candidate_target_mean_abs_diff"),
        "max_candidate_target_max_abs_diff": checks.get("max_candidate_target_max_abs_diff"),
        "contract_mean_overlay_mean_abs_diff": checks.get("contract_mean_overlay_mean_abs_diff"),
        "contract_max_overlay_mean_abs_diff": checks.get("contract_max_overlay_mean_abs_diff"),
        "gif_bytes": checks.get("gif_bytes"),
        "gallery_index": gallery.get("index_repo_path"),
    }


def sort_key(item):
    return (
        item.get("max_candidate_target_mean_abs_diff") if item.get("max_candidate_target_mean_abs_diff") is not None else 1e9,
        item.get("mean_candidate_target_mean_abs_diff") if item.get("mean_candidate_target_mean_abs_diff") is not None else 1e9,
    )


def markdown_report(summary, out_path, root):
    best = summary.get("best") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(out_path, root)}`",
        f"Status: `{summary['status']}`",
        f"Best candidate: `{best.get('label')}`",
        f"Best max target MAD: `{best.get('max_candidate_target_mean_abs_diff')}`",
        f"Contract max target MAD: `{summary.get('contract', {}).get('max_overlay_mean_abs_diff')}`",
        "",
        "## Ranking",
        "",
        "| Rank | Candidate | Decision | Frames | Mean Target MAD | Max Target MAD | Max Target Diff | Mean Contract MAD | Gallery |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for index, item in enumerate(summary.get("ranking", []), start=1):
        lines.append(
            f"| {index} | `{item.get('label')}` | `{item.get('decision')}` | {item.get('frames')} | "
            f"{item.get('mean_candidate_target_mean_abs_diff')} | {item.get('max_candidate_target_mean_abs_diff')} | "
            f"{item.get('max_candidate_target_max_abs_diff')} | {item.get('mean_candidate_contract_mean_abs_diff')} | "
            f"`{item.get('gallery_index')}` |"
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
    parser = argparse.ArgumentParser(description="Summarize Mitsuba secondary native candidate gaps")
    parser.add_argument("candidate", nargs="+", help="label=path or path to lsfs_mitsuba_secondary_native_candidate_gap summary")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Secondary Native Candidate Sweep")
    parser.add_argument(
        "--next",
        default="Use the best ranked candidate as the current native secondary baseline.",
    )
    args = parser.parse_args(argv)
    root = os.getcwd()
    candidates = [candidate_entry(value, root) for value in args.candidate]
    ranking = sorted(candidates, key=sort_key)
    best = ranking[0] if ranking else None
    contract = {
        "mean_overlay_mean_abs_diff": best.get("contract_mean_overlay_mean_abs_diff") if best else None,
        "max_overlay_mean_abs_diff": best.get("contract_max_overlay_mean_abs_diff") if best else None,
    }
    summary = {
        "schema": "lsfs_mitsuba_secondary_native_candidate_sweep_summary",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if best else "failed",
        "best": best,
        "contract": contract,
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
        f"best={best.get('label') if best else 'n/a'} "
        f"best_max_target_mad={best.get('max_candidate_target_mean_abs_diff') if best else 'n/a'} out={out_path}"
    )
    print(f"report={report_path}")
    if summary["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
