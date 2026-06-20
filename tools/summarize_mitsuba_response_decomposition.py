#!/usr/bin/env python
"""Summarize source-response decomposition into renderer-native decisions."""

import argparse
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


def parse_labeled_path(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected LABEL=PATH")
    label, path = value.split("=", 1)
    label = label.strip()
    path = path.strip()
    if not label or not path:
        raise argparse.ArgumentTypeError("expected LABEL=PATH")
    return label, path


def source_entry(path, root, label):
    return {
        "label": label,
        "path": os.path.abspath(path),
        "repo_path": posix_rel(path, root),
        "size": os.path.getsize(path),
        "sha256": sha256_file(path),
    }


def top_channel_row(channel_summary, region):
    rows = (channel_summary.get("top_by_mask") or {}).get(region) or []
    if not rows:
        return None
    row = dict(rows[0])
    for key in ("precision", "recall", "f1", "candidate_coverage", "target_coverage"):
        if key in row:
            row[key] = float(row[key])
    return row


def mask_source_record(label, path, root):
    payload = read_json(path)
    if payload.get("schema") != "lsfs_mitsuba_source_response_mask_source":
        raise SystemExit(f"{path}: expected lsfs_mitsuba_source_response_mask_source schema")
    checks = payload.get("checks") or {}
    return {
        "label": label,
        "candidate": payload.get("candidate"),
        "mask_kind": payload.get("mask_kind"),
        "status": payload.get("status"),
        "summary": source_entry(path, root, label),
        "checks": {
            "frames": int(checks.get("frames") or 0),
            "max_mask_coverage": float(checks.get("max_mask_coverage") or 0.0),
            "mean_mask_coverage": float(checks.get("mean_mask_coverage") or 0.0),
            "mask_bytes": int(checks.get("mask_bytes") or 0),
            "gif_bytes": int(checks.get("gif_bytes") or 0),
        },
        "gallery": payload.get("gallery") or {},
    }


def verdict_for(region, top_row, mask_record, args):
    if not top_row:
        return {
            "decision": "missing-channel-evidence",
            "native_cause": "unknown",
            "reason": "No channel overlap row was found for this response mask.",
        }
    f1 = float(top_row.get("f1") or 0.0)
    precision = float(top_row.get("precision") or 0.0)
    recall = float(top_row.get("recall") or 0.0)
    mean_coverage = float((mask_record.get("checks") or {}).get("mean_mask_coverage") or 0.0)
    mask_kind = mask_record.get("mask_kind") or ""

    if f1 >= args.accept_f1 and precision >= args.accept_precision:
        return {
            "decision": "portable-secondary-response",
            "native_cause": "projected secondary channel overlap",
            "reason": (
                f"Best channel `{top_row.get('candidate')}` clears F1/precision gates "
                f"({f1:.6f}/{precision:.6f}) with recall {recall:.6f}."
            ),
        }
    if "highlight" in mask_kind:
        return {
            "decision": "keep-as-light-or-response-reference",
            "native_cause": "not explained by secondary channels",
            "reason": (
                f"Highlight mask coverage is {mean_coverage:.6f}, but best secondary "
                f"overlap F1 is only {f1:.6f}."
            ),
        }
    if f1 < args.weak_f1:
        return {
            "decision": "representation-needed",
            "native_cause": "not explained by current secondary/material channels",
            "reason": (
                f"Best channel `{top_row.get('candidate')}` has weak F1 {f1:.6f}; "
                "another low-level overlay is unlikely to close this response."
            ),
        }
    return {
        "decision": "weak-secondary-correlation",
        "native_cause": "partial projected secondary overlap",
        "reason": (
            f"Best channel `{top_row.get('candidate')}` has recall {recall:.6f} "
            f"but precision {precision:.6f}, so it is too broad for direct porting."
        ),
    }


def candidate_rank(gap_gallery, label):
    for index, item in enumerate(gap_gallery.get("candidates") or [], start=1):
        if item.get("label") == label:
            checks = item.get("checks") or {}
            return {
                "rank": index,
                "label": label,
                "max_gap_mean_abs_diff": float(checks.get("max_gap_mean_abs_diff") or 0.0),
                "mean_gap_mean_abs_diff": float(checks.get("mean_gap_mean_abs_diff") or 0.0),
                "frames": int(checks.get("frames") or 0),
            }
    return None


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Status: `{summary['status']}`",
        "",
        "## Score Context",
        "",
    ]
    for item in summary.get("score_context") or []:
        lines.append(
            f"- `{item['label']}` rank `{item['rank']}` max-gap MAD "
            f"`{item['max_gap_mean_abs_diff']}`"
        )
    lines.extend([
        "",
        "## Decomposition",
        "",
        "| Region | Mask Kind | Mean Coverage | Top Channel | Precision | Recall | F1 | Decision |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ])
    for item in summary.get("regions") or []:
        top = item.get("top_channel") or {}
        checks = item.get("mask_source", {}).get("checks") or {}
        decision = item.get("decision") or {}
        lines.append(
            f"| `{item['region']}` | `{item['mask_source'].get('mask_kind')}` | "
            f"{checks.get('mean_mask_coverage')} | `{top.get('candidate')}` | "
            f"{top.get('precision')} | {top.get('recall')} | {top.get('f1')} | "
            f"`{decision.get('decision')}` |"
        )
    lines.extend(["", "## Decisions", ""])
    for item in summary.get("regions") or []:
        decision = item.get("decision") or {}
        lines.extend([
            f"### {item['region']}",
            "",
            f"- Decision: `{decision.get('decision')}`",
            f"- Native cause: `{decision.get('native_cause')}`",
            f"- Reason: {decision.get('reason')}",
            "",
        ])
    lines.extend(["## Overall", ""])
    lines.extend(summary.get("overall") or [])
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    channel_path = require_file(args.channel_summary, "channel summary")
    gap_path = require_file(args.gap_gallery, "gap gallery")
    channel_summary = read_json(channel_path)
    gap_gallery = read_json(gap_path)
    if channel_summary.get("schema") != "lsfs_mitsuba_source_response_mask_channel_analysis":
        raise SystemExit(f"{channel_path}: expected lsfs_mitsuba_source_response_mask_channel_analysis schema")
    if gap_gallery.get("schema") != "lsfs_mitsuba_gap_summary_gallery":
        raise SystemExit(f"{gap_path}: expected lsfs_mitsuba_gap_summary_gallery schema")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    regions = []
    for region, mask_path in args.region:
        resolved = require_file(mask_path, f"{region} mask source")
        mask_record = mask_source_record(region, resolved, root)
        top = top_channel_row(channel_summary, region)
        regions.append({
            "region": region,
            "mask_source": mask_record,
            "top_channel": top,
            "decision": verdict_for(region, top, mask_record, args),
        })

    score_context = []
    for label in args.score_candidate:
        rank = candidate_rank(gap_gallery, label)
        if rank:
            score_context.append(rank)

    weak_regions = [
        item["region"] for item in regions
        if (item.get("decision") or {}).get("decision") != "portable-secondary-response"
    ]
    portable_regions = [
        item["region"] for item in regions
        if (item.get("decision") or {}).get("decision") == "portable-secondary-response"
    ]
    overall = [
        (
            "S401 CR21 should remain an upper-bound response reference for now; "
            "its decomposed masks do not clear secondary-channel portability gates."
        ),
        (
            "Weak or nonsecondary regions: "
            + (", ".join(f"`{name}`" for name in weak_regions) if weak_regions else "`none`")
            + "."
        ),
        (
            "Portable regions: "
            + (", ".join(f"`{name}`" for name in portable_regions) if portable_regions else "`none`")
            + "."
        ),
        (
            "The next implementation path should change the primary water surface/volume "
            "or isolate a physical highlight/light response, not add more broad secondary overlays."
        ),
    ]
    summary_path = os.path.join(out_dir, "response_decomposition_summary.json")
    summary = {
        "schema": "lsfs_mitsuba_response_decomposition_summary",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready",
        "sources": {
            "channel_summary": source_entry(channel_path, root, "channel summary"),
            "gap_gallery": source_entry(gap_path, root, "gap gallery"),
        },
        "settings": {
            "accept_f1": args.accept_f1,
            "accept_precision": args.accept_precision,
            "weak_f1": args.weak_f1,
        },
        "score_context": score_context,
        "regions": regions,
        "overall": overall,
        "next": args.next,
    }
    write_json(summary_path, summary)
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready regions={len(regions)} portable={len(portable_regions)} "
        f"summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize Mitsuba response decomposition decisions")
    parser.add_argument("out_dir")
    parser.add_argument("--channel-summary", required=True)
    parser.add_argument("--gap-gallery", required=True)
    parser.add_argument("--region", action="append", required=True, type=parse_labeled_path,
                        help="REGION=source_response_mask_source_summary.json")
    parser.add_argument("--score-candidate", action="append", default=[],
                        help="Candidate label to include from the gap gallery")
    parser.add_argument("--accept-f1", type=float, default=0.25)
    parser.add_argument("--accept-precision", type=float, default=0.2)
    parser.add_argument("--weak-f1", type=float, default=0.1)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Response Decomposition Summary")
    parser.add_argument("--next", default="Use the decomposition verdicts to choose the next renderer-native representation step.")
    args = parser.parse_args(argv)
    build(args)


if __name__ == "__main__":
    main()
