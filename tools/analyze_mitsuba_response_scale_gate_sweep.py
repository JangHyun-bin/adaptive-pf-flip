#!/usr/bin/env python
"""Evaluate response-scale candidates against S577/S585 visual gates."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import ImageChops
except ImportError:  # pragma: no cover - require_pillow reports this.
    ImageChops = None

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    write_json,
    write_text,
)
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    copy_asset,
    labeled_strip,
    require_pillow,
    resolve_path,
    write_gif,
)
from compare_mitsuba_renderer_scene_depth_material_native_stage import by_frame, diff_block, file_entry, ref_path


RESPONSE_SCHEMA = "lsfs_mitsuba_response_delta_buffer"
TARGET_SCHEMA = "lsfs_mitsuba_renderer_scene_depth_material_target"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_scale_gate_sweep"


def rows_by_scale(response):
    rows = {}
    for row in ((response.get("scale_sweep") or {}).get("rows") or []):
        rows.setdefault(float(row.get("scale")), []).append(row)
    return {scale: sorted(items, key=lambda item: int(item.get("output_frame") or 0)) for scale, items in rows.items()}


def html_page(summary):
    selected = summary.get("selected_candidate") or {}
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "Selected Response Scale Gate GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Selected Response Scale Gate Strip ")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Decision", summary.get("decision")),
            ("Candidates", checks.get("candidates")),
            ("Selected", selected.get("scale")),
            ("S577 max MAD", f"{(selected.get('checks') or {}).get('max_scaled_accepted_mean_diff', 0.0):.4f}"),
            ("S585 max MAD", f"{(selected.get('checks') or {}).get('max_scaled_target_mean_diff', 0.0):.4f}"),
            ("S585/S577 MAD", f"{checks.get('max_target_accepted_mean_diff', 0.0):.4f}"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="selected response scale gate gif"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
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
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 16px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; overflow-x: auto; margin: 0 0 12px; }}
    img {{ display: block; max-width: none; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Response-scale gate sweep comparing existing S616 scale candidates against the S585 target and S577 accepted composite.</p>
  <section class="tiles">{tiles}</section>
  {hero}
  <section>{figures}</section>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    selected = summary.get("selected_candidate") or {}
    selected_checks = selected.get("checks") or {}
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        f"Decision: `{summary['decision']}`",
        "",
        "## Selected Scale",
        "",
        f"- Scale: `{selected.get('scale')}`",
        f"- Frames: `{selected_checks.get('frames')}`",
        f"- Failed frames: `{selected_checks.get('failed_frames')}`",
        f"- Max scale-vs-S577 abs diff: `{selected_checks.get('max_scaled_accepted_abs_diff')}`",
        f"- Max scale-vs-S577 mean diff: `{selected_checks.get('max_scaled_accepted_mean_diff')}`",
        f"- Mean scale-vs-S577 mean diff: `{selected_checks.get('mean_scaled_accepted_mean_diff')}`",
        f"- Max scale-vs-S585 abs diff: `{selected_checks.get('max_scaled_target_abs_diff')}`",
        f"- Max scale-vs-S585 mean diff: `{selected_checks.get('max_scaled_target_mean_diff')}`",
        f"- Mean scale-vs-S585 mean diff: `{selected_checks.get('mean_scaled_target_mean_diff')}`",
        f"- Max S585-vs-S577 mean diff: `{checks.get('max_target_accepted_mean_diff')}`",
        f"- GIF bytes: `{format_bytes(selected_checks.get('gif_bytes', 0))}`",
        "",
        "## Scale Sweep",
        "",
        "| Scale | Frames | Failed | S577 Max | S577 Max MAD | S577 Mean MAD | S585 Max | S585 Max MAD | S585 Mean MAD | Decision |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for candidate in summary.get("candidates") or []:
        c = candidate.get("checks") or {}
        lines.append(
            f"| {candidate.get('scale')} | {c.get('frames')} | {c.get('failed_frames')} | "
            f"{c.get('max_scaled_accepted_abs_diff')} | {c.get('max_scaled_accepted_mean_diff')} | "
            f"{c.get('mean_scaled_accepted_mean_diff')} | {c.get('max_scaled_target_abs_diff')} | "
            f"{c.get('max_scaled_target_mean_diff')} | {c.get('mean_scaled_target_mean_diff')} | "
            f"`{candidate.get('decision')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def compare_row(row, target_frame, root, strips_dir=None):
    output_frame = int(row.get("output_frame") or 0)
    scaled_path = resolve_path(row.get("scaled_repo_path"), root)
    target_path = ref_path((target_frame.get("references") or {}).get("target_preview"), root)
    accepted_path = ref_path((target_frame.get("references") or {}).get("source_composite"), root)
    missing = [
        name for name, path in (
            ("scaled_response", scaled_path),
            ("s585_target_preview", target_path),
            ("s577_accepted_composite", accepted_path),
        )
        if not path or not os.path.isfile(path)
    ]
    if missing:
        return {"status": "failed", "output_frame": output_frame, "missing": missing}

    scaled = Image.open(scaled_path).convert("RGB")
    target = Image.open(target_path).convert("RGB")
    accepted = Image.open(accepted_path).convert("RGB")
    if scaled.size != target.size or scaled.size != accepted.size:
        return {"status": "failed", "output_frame": output_frame, "missing": ["dimension_mismatch"]}

    if strips_dir:
        scaled_target = diff_block(scaled, target)
        scaled_accepted = diff_block(scaled, accepted)
        target_accepted = diff_block(target, accepted)
    else:
        scaled_target = diff_metrics(scaled, target)
        scaled_accepted = diff_metrics(scaled, accepted)
        target_accepted = diff_metrics(target, accepted)
    strip = None
    if strips_dir:
        strip_path = os.path.abspath(os.path.join(strips_dir, f"frame_{output_frame:04d}_response_scale_gate.png"))
        labeled_strip(
            [accepted, scaled, target, scaled_accepted["diff_image"], scaled_target["diff_image"]],
            ["S577 accepted", f"scale {row.get('scale'):g}", "S585 target", "scale-S577 x8", "scale-S585 x8"],
            strip_path,
        )
        strip = file_entry(strip_path, root)
    for block in (scaled_target, scaled_accepted, target_accepted):
        block.pop("diff_image", None)
    item = {
        "status": "measured",
        "output_frame": output_frame,
        "scale": row.get("scale"),
        "scaled_repo_path": posix_rel(scaled_path, root),
        "scaled_vs_target": scaled_target,
        "scaled_vs_accepted": scaled_accepted,
        "target_vs_accepted": target_accepted,
    }
    if strip:
        item["strip"] = strip
    return item


def diff_metrics(actual, expected):
    diff = ImageChops.difference(actual.convert("RGB"), expected.convert("RGB"))
    histogram = diff.histogram()
    total = 0
    count = 0
    nonzero = 0
    for channel in range(3):
        offset = channel * 256
        for value in range(256):
            samples = histogram[offset + value]
            total += value * samples
            count += samples
            if value:
                nonzero += samples
    return {
        "max_abs_diff": max(channel[1] for channel in diff.getextrema()),
        "mean_abs_diff": total / float(max(1, count)),
        "mismatched_coverage": nonzero / float(max(1, count)),
    }


def stat_values(frames, key, stat):
    values = [frame.get(key, {}).get(stat) for frame in frames if frame.get("status") == "measured"]
    return [float(value) for value in values if value is not None]


def aggregate(frames, key, stat):
    values = stat_values(frames, key, stat)
    if not values:
        return {"max": 999.0, "mean": 999.0}
    return {"max": max(values), "mean": sum(values) / float(len(values))}


def summarize_scale(scale, rows, target_frames, root):
    frames = [compare_row(row, target_frames.get(int(row.get("output_frame") or 0), {}), root) for row in rows]
    failed = [frame for frame in frames if frame.get("status") != "measured"]
    accepted_abs = aggregate(frames, "scaled_vs_accepted", "max_abs_diff")
    accepted_mean = aggregate(frames, "scaled_vs_accepted", "mean_abs_diff")
    target_abs = aggregate(frames, "scaled_vs_target", "max_abs_diff")
    target_mean = aggregate(frames, "scaled_vs_target", "mean_abs_diff")
    baseline_abs = aggregate(frames, "target_vs_accepted", "max_abs_diff")
    baseline_mean = aggregate(frames, "target_vs_accepted", "mean_abs_diff")
    return {
        "scale": scale,
        "decision": "measured" if not failed else "hold_missing_refs",
        "checks": {
            "frames": len(frames),
            "measured_frames": len(frames) - len(failed),
            "failed_frames": len(failed),
            "missing_references": sum(len(frame.get("missing") or []) for frame in failed),
            "max_scaled_accepted_abs_diff": int(accepted_abs["max"]),
            "max_scaled_accepted_mean_diff": accepted_mean["max"],
            "mean_scaled_accepted_mean_diff": accepted_mean["mean"],
            "max_scaled_target_abs_diff": int(target_abs["max"]),
            "max_scaled_target_mean_diff": target_mean["max"],
            "mean_scaled_target_mean_diff": target_mean["mean"],
            "max_target_accepted_abs_diff": int(baseline_abs["max"]),
            "max_target_accepted_mean_diff": baseline_mean["max"],
            "mean_target_accepted_mean_diff": baseline_mean["mean"],
        },
    }


def select_candidate(candidates):
    measured = [candidate for candidate in candidates if (candidate.get("checks") or {}).get("failed_frames") == 0]
    if not measured:
        return None
    return min(
        measured,
        key=lambda candidate: (
            float((candidate.get("checks") or {}).get("max_scaled_accepted_mean_diff") or 999.0),
            float((candidate.get("checks") or {}).get("mean_scaled_accepted_mean_diff") or 999.0),
            int((candidate.get("checks") or {}).get("max_scaled_accepted_abs_diff") or 999),
        ),
    )


def selected_with_strips(selected, rows, target_frames, root, out_dir, fps, keyframes):
    strips_dir = os.path.join(out_dir, f"scale_{selected['scale']:.3f}".replace(".", "p"), "strips")
    os.makedirs(strips_dir, exist_ok=True)
    frames = [compare_row(row, target_frames.get(int(row.get("output_frame") or 0), {}), root, strips_dir) for row in rows]
    measured = [frame for frame in frames if frame.get("status") == "measured"]
    strip_paths = [resolve_path(frame["strip"]["repo_path"], root) for frame in measured if frame.get("strip")]
    gif_path = os.path.join(out_dir, "selected_response_scale_gate_strips.gif")
    if strip_paths:
        write_gif(strip_paths, gif_path, fps)
    key_indices = sorted(set(round(i * (len(measured) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes))) if measured else []
    result = dict(selected)
    result["frames"] = frames
    result["gif_repo_path"] = posix_rel(gif_path, root) if os.path.isfile(gif_path) else None
    result["sample_strip_paths"] = [strip_paths[index] for index in key_indices] if strip_paths else []
    result["checks"] = dict(result["checks"])
    result["checks"]["gif_bytes"] = os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0
    return result


def run(args):
    require_pillow()
    root = os.getcwd()
    response_path = require_file(resolve_path(args.response_summary, root), "response delta buffer summary")
    target_path = require_file(resolve_path(args.target_summary, root), "S585 target summary")
    response = read_json(response_path)
    target = read_json(target_path)
    if response.get("schema") != RESPONSE_SCHEMA:
        raise SystemExit(f"{args.response_summary}: expected {RESPONSE_SCHEMA}")
    if response.get("status") != "ready":
        raise SystemExit(f"{args.response_summary}: response summary status is {response.get('status')!r}")
    if target.get("schema") != TARGET_SCHEMA:
        raise SystemExit(f"{args.target_summary}: expected {TARGET_SCHEMA}")
    if target.get("status") != "ready":
        raise SystemExit(f"{args.target_summary}: target status is {target.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (out_dir, gallery_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    target_frames = by_frame(target.get("frames"))
    grouped = rows_by_scale(response)
    candidates = [summarize_scale(scale, rows, target_frames, root) for scale, rows in sorted(grouped.items())]
    selected = select_candidate(candidates)
    selected_rows = grouped.get(selected["scale"], []) if selected else []
    selected_full = selected_with_strips(selected, selected_rows, target_frames, root, out_dir, args.fps, args.keyframes) if selected else {}

    baseline_checks = (selected_full.get("checks") or {}) if selected_full else {}
    decision = "response_scale_still_outside_gate"
    if selected_full and baseline_checks.get("max_scaled_accepted_mean_diff", 999.0) <= baseline_checks.get("max_target_accepted_mean_diff", 0.0):
        decision = "response_scale_matches_accepted_gate"
    status = "ready" if selected_full else "failed"

    assets = []
    if selected_full.get("gif_repo_path"):
        assets.append(copy_asset(resolve_path(selected_full["gif_repo_path"], root), assets_dir, "selected_response_scale_gate_strips.gif", "Selected Response Scale Gate GIF", root))
    for index, strip_path in enumerate(selected_full.get("sample_strip_paths") or []):
        assets.append(copy_asset(strip_path, assets_dir, f"selected_response_scale_gate_strip_{index:02d}.png", f"Selected Response Scale Gate Strip {index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "decision": decision,
        "inputs": {
            "response_summary": posix_rel(response_path, root),
            "target_summary": posix_rel(target_path, root),
            "accepted_gate": "S577 source composite referenced by S585 target frames",
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "candidates": len(candidates),
            "selected_scale": selected_full.get("scale"),
            "frames": (selected_full.get("checks") or {}).get("frames"),
            "max_target_accepted_abs_diff": (selected_full.get("checks") or {}).get("max_target_accepted_abs_diff"),
            "max_target_accepted_mean_diff": (selected_full.get("checks") or {}).get("max_target_accepted_mean_diff"),
            "mean_target_accepted_mean_diff": (selected_full.get("checks") or {}).get("mean_target_accepted_mean_diff"),
        },
        "selected_candidate": selected_full,
        "candidates": candidates,
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
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_scale_gate_sweep_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        "status={status} decision={decision} candidates={candidates} selected={selected} "
        "s577_max_mad={s577_mad} baseline_mad={baseline_mad} summary={summary}".format(
            status=status,
            decision=decision,
            candidates=len(candidates),
            selected=selected_full.get("scale"),
            s577_mad=(selected_full.get("checks") or {}).get("max_scaled_accepted_mean_diff"),
            baseline_mad=(selected_full.get("checks") or {}).get("max_target_accepted_mean_diff"),
            summary=summary_path,
        )
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_summary", help="S616 response delta buffer summary")
    parser.add_argument("target_summary", help="S585 depth/material target summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S631 Response Scale Gate Sweep")
    parser.add_argument(
        "--next",
        default="Response-scale backoff alone does not recover the accepted S577/S585 envelope; branch the next renderer candidate from the S585 target contract instead of S617 response scale.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
