#!/usr/bin/env python
"""Run bounded native-style response candidates from the S585 anchor handoff."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import ImageChops, ImageDraw, ImageOps
except ImportError:  # pragma: no cover - require_pillow reports this.
    ImageChops = None
    ImageDraw = None
    ImageOps = None

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
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    copy_asset,
    require_pillow,
    resolve_path,
    write_gif,
)
from run_mitsuba_response_aov_scene_native_probe_sweep import apply_candidate, metric_bounds, normalized


ANCHOR_SCHEMA = "lsfs_mitsuba_response_aov_s585_anchor_handoff"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_s585_anchor_native_candidate"


def parse_candidate(text):
    if "=" not in text:
        raise argparse.ArgumentTypeError("candidate must be label=strength,mask_size,blur,power,volume,sparkle")
    label, spec = text.split("=", 1)
    label = label.strip()
    parts = [item.strip() for item in spec.split(",") if item.strip()]
    if len(parts) != 6:
        raise argparse.ArgumentTypeError("candidate spec needs 6 comma-separated values")
    strength = float(parts[0])
    mask_size = int(parts[1])
    blur = float(parts[2])
    power = float(parts[3])
    volume = float(parts[4])
    sparkle = float(parts[5])
    if not label:
        raise argparse.ArgumentTypeError("candidate label is empty")
    if strength <= 0.0 or strength > 2.0:
        raise argparse.ArgumentTypeError("strength must be in (0, 2.0]")
    if mask_size < 1 or mask_size % 2 == 0:
        raise argparse.ArgumentTypeError("mask_size must be a positive odd integer")
    if blur < 0.0:
        raise argparse.ArgumentTypeError("blur must be non-negative")
    if power <= 0.0:
        raise argparse.ArgumentTypeError("power must be positive")
    if volume < 0.0 or sparkle < 0.0:
        raise argparse.ArgumentTypeError("volume and sparkle must be non-negative")
    return {
        "label": label,
        "strength": strength,
        "mask_size": mask_size,
        "mask_blur": blur,
        "mask_power": power,
        "volume_scale": volume,
        "sparkle_scale": sparkle,
    }


def default_candidates():
    return [
        parse_candidate("ANCHOR_EDGE_20=0.20,7,3.0,0.82,0.58,0.20"),
        parse_candidate("ANCHOR_EDGE_26=0.26,7,3.0,0.82,0.58,0.20"),
        parse_candidate("ANCHOR_EDGE_32=0.32,7,3.0,0.82,0.58,0.20"),
        parse_candidate("ANCHOR_EDGE_38=0.38,7,3.0,0.82,0.58,0.20"),
        parse_candidate("ANCHOR_EDGE_44=0.44,7,3.0,0.82,0.58,0.20"),
        parse_candidate("ANCHOR_SOFT_18=0.18,11,5.0,0.70,0.72,0.25"),
        parse_candidate("ANCHOR_SOFT_22=0.22,11,5.0,0.70,0.72,0.25"),
        parse_candidate("ANCHOR_SOFT_26=0.26,11,5.0,0.70,0.72,0.25"),
        parse_candidate("ANCHOR_SOFT_30=0.30,11,5.0,0.70,0.72,0.25"),
        parse_candidate("ANCHOR_SOFT_34=0.34,11,5.0,0.70,0.72,0.25"),
        parse_candidate("ANCHOR_SOFT_40=0.40,11,5.0,0.70,0.72,0.25"),
    ]


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def file_path(ref, root):
    if not isinstance(ref, dict):
        return None
    return resolve_path(ref.get("path") or ref.get("repo_path"), root)


def image_entry(path, root):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


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


def diff_visual(actual, expected):
    return ImageOps.autocontrast(ImageChops.difference(actual.convert("RGB"), expected.convert("RGB")))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = width * index
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
        strip.paste(panel.convert("RGB"), (x, label_h))
    ensure_dir(os.path.dirname(out_path))
    strip.save(out_path)


def load_inputs(anchor_summary, root):
    frames = []
    missing = []
    y_values = []
    z_values = []
    secondary_values = []
    for item in anchor_summary.get("frames") or []:
        descriptor_path = resolve_path((item.get("descriptor") or {}).get("repo_path"), root)
        anchor_path = resolve_path((item.get("anchor") or {}).get("repo_path"), root)
        accepted_path = resolve_path((item.get("accepted") or {}).get("repo_path"), root)
        absent = [
            name for name, path in (
                ("descriptor", descriptor_path),
                ("s585_anchor", anchor_path),
                ("s577_accepted", accepted_path),
            )
            if not path or not os.path.isfile(path)
        ]
        if absent:
            missing.append({"frame": item.get("frame"), "missing": absent})
            continue
        descriptor = read_json(descriptor_path)
        aovs = ((descriptor.get("inputs") or {}).get("aov_layers") or {})
        positive_path = file_path(aovs.get("response_positive_rgb"), root)
        negative_path = file_path(aovs.get("response_negative_rgb"), root)
        absent = [
            name for name, path in (
                ("response_positive_rgb", positive_path),
                ("response_negative_rgb", negative_path),
            )
            if not path or not os.path.isfile(path)
        ]
        if absent:
            missing.append({"frame": item.get("frame"), "missing": absent})
            continue
        render_data = item.get("render_data") or {}
        y_values.append(render_data.get("water_depth_y_span"))
        z_values.append(render_data.get("water_depth_z_span"))
        secondary_values.append(render_data.get("secondary_total"))
        frames.append({
            "frame": int(item.get("frame") or 0),
            "output_frame": item.get("output_frame"),
            "scene_frame": item.get("scene_frame"),
            "source_frame": item.get("source_frame"),
            "scene_time": item.get("scene_time"),
            "descriptor_path": descriptor_path,
            "anchor_path": anchor_path,
            "accepted_path": accepted_path,
            "positive_path": positive_path,
            "negative_path": negative_path,
            "render_data": render_data,
            "anchor_vs_accepted": item.get("anchor_vs_accepted") or {},
        })
    bounds = {
        "water_y": metric_bounds(y_values),
        "water_z": metric_bounds(z_values),
        "secondary": metric_bounds(secondary_values),
    }
    return frames, missing, bounds


def render_candidate(frames, missing, bounds, candidate, out_dir, root):
    label = candidate["label"]
    frames_dir = ensure_dir(os.path.join(out_dir, label, "frames"))
    rows = []
    for item in frames:
        anchor = Image.open(item["anchor_path"]).convert("RGB")
        accepted = Image.open(item["accepted_path"]).convert("RGB")
        positive = Image.open(item["positive_path"]).convert("RGB")
        negative = Image.open(item["negative_path"]).convert("RGB")
        render_data = item["render_data"]
        depth_factor = 0.5 * (
            normalized(render_data.get("water_depth_y_span"), bounds["water_y"])
            + normalized(render_data.get("water_depth_z_span"), bounds["water_z"])
        )
        secondary_factor = normalized(render_data.get("secondary_total"), bounds["secondary"])
        output, delta, response = apply_candidate(anchor, positive, negative, candidate, depth_factor, secondary_factor)
        frame_path = os.path.abspath(os.path.join(frames_dir, f"frame_{item['frame']:04d}.png"))
        output.save(frame_path)
        candidate_anchor = diff_metrics(output, anchor)
        candidate_accepted = diff_metrics(output, accepted)
        rows.append({
            "frame": item["frame"],
            "output_frame": item.get("output_frame"),
            "scene_frame": item.get("scene_frame"),
            "source_frame": item.get("source_frame"),
            "scene_time": item.get("scene_time"),
            "preview_repo_path": posix_rel(frame_path, root),
            "sha256": sha256_file(frame_path),
            "size": os.path.getsize(frame_path),
            "descriptor_repo_path": posix_rel(item["descriptor_path"], root),
            "anchor_repo_path": posix_rel(item["anchor_path"], root),
            "accepted_repo_path": posix_rel(item["accepted_path"], root),
            "candidate_vs_anchor": candidate_anchor,
            "candidate_vs_accepted": candidate_accepted,
            "anchor_vs_accepted": item.get("anchor_vs_accepted") or {},
            "native_delta": delta,
            "depth_factor": depth_factor,
            "secondary_factor": secondary_factor,
        })
        response.close()
    candidate_anchor_mean = [row["candidate_vs_anchor"]["mean_abs_diff"] for row in rows]
    candidate_accepted_mean = [row["candidate_vs_accepted"]["mean_abs_diff"] for row in rows]
    return {
        **candidate,
        "repo_path": posix_rel(os.path.join(out_dir, label), root),
        "frames": rows,
        "checks": {
            "frames": len(rows),
            "missing_references": len(missing),
            "max_candidate_anchor_abs_diff": max((row["candidate_vs_anchor"]["max_abs_diff"] for row in rows), default=999),
            "max_candidate_anchor_mean_diff": max(candidate_anchor_mean, default=999.0),
            "mean_candidate_anchor_mean_diff": sum(candidate_anchor_mean) / float(max(1, len(candidate_anchor_mean))),
            "max_candidate_accepted_abs_diff": max((row["candidate_vs_accepted"]["max_abs_diff"] for row in rows), default=999),
            "max_candidate_accepted_mean_diff": max(candidate_accepted_mean, default=999.0),
            "mean_candidate_accepted_mean_diff": sum(candidate_accepted_mean) / float(max(1, len(candidate_accepted_mean))),
            "max_anchor_accepted_abs_diff": max(((row.get("anchor_vs_accepted") or {}).get("max_abs_diff") or 0 for row in rows), default=999),
            "max_anchor_accepted_mean_diff": max(((row.get("anchor_vs_accepted") or {}).get("mean_abs_diff") or 0.0 for row in rows), default=999.0),
            "output_bytes": sum(row["size"] for row in rows),
        },
    }


def feasible(candidate, args):
    checks = candidate.get("checks") or {}
    return (
        checks.get("frames", 0) > 0
        and checks.get("missing_references", 1) == 0
        and checks.get("max_candidate_anchor_abs_diff", 999) <= args.anchor_abs_tolerance
        and checks.get("max_candidate_anchor_mean_diff", 999.0) <= args.anchor_mean_tolerance
        and checks.get("max_candidate_accepted_abs_diff", 999) <= args.accepted_abs_tolerance
        and checks.get("max_candidate_accepted_mean_diff", 999.0) <= args.accepted_mean_tolerance
    )


def select_candidate(candidates, args):
    feasible_candidates = [candidate for candidate in candidates if feasible(candidate, args)]
    if not feasible_candidates:
        return None
    return max(
        feasible_candidates,
        key=lambda candidate: (
            float((candidate.get("checks") or {}).get("mean_candidate_anchor_mean_diff") or 0.0),
            float((candidate.get("checks") or {}).get("max_candidate_anchor_mean_diff") or 0.0),
        ),
    )


def build_selected_gallery(selected, out_dir, root, fps, keyframes):
    if not selected:
        return [], {}
    label = selected["label"]
    strips_dir = ensure_dir(os.path.join(out_dir, label, "strips"))
    strip_paths = []
    for row in selected.get("frames") or []:
        output = Image.open(resolve_path(row["preview_repo_path"], root)).convert("RGB")
        anchor = Image.open(resolve_path(row["anchor_repo_path"], root)).convert("RGB")
        accepted = Image.open(resolve_path(row["accepted_repo_path"], root)).convert("RGB")
        strip_path = os.path.abspath(os.path.join(strips_dir, f"frame_{row['frame']:04d}_{label}.png"))
        labeled_strip(
            [accepted, anchor, output, diff_visual(output, anchor), diff_visual(output, accepted)],
            ["S577 accepted", "S585 anchor", label, "candidate-S585 x8", "candidate-S577 x8"],
            strip_path,
        )
        row["strip_repo_path"] = posix_rel(strip_path, root)
        strip_paths.append(strip_path)
    gif_path = os.path.join(out_dir, f"{label}_strips.gif")
    if strip_paths:
        write_gif(strip_paths, gif_path, fps)
    selected["strip_gif_repo_path"] = posix_rel(gif_path, root) if os.path.isfile(gif_path) else None
    selected["sample_strip_paths"] = []
    if strip_paths:
        key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes)))
        selected["sample_strip_paths"] = [strip_paths[index] for index in key_indices]
    selected["checks"] = dict(selected["checks"])
    selected["checks"]["strip_gif_bytes"] = os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0
    return strip_paths, selected


def html_page(summary):
    selected = summary.get("selected_candidate") or {}
    checks = selected.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "Selected S585 Anchor Native Candidate GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Selected S585 Anchor Native Candidate Strip ")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Selected", selected.get("label")),
            ("Candidates", (summary.get("checks") or {}).get("candidates")),
            ("S585 move", checks.get("max_candidate_anchor_abs_diff")),
            ("S585 MAD", f"{checks.get('max_candidate_anchor_mean_diff', 0.0):.4f}"),
            ("S577 MAD", f"{checks.get('max_candidate_accepted_mean_diff', 0.0):.4f}"),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="selected S585 anchor native candidate GIF"></section>' if gif else ""
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
  <p>Bounded response-AOV native candidate branched from the S632 S585 anchor, not from the stronger S617 response-scale family.</p>
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
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        f"Decision: `{summary['decision']}`",
        f"Selected candidate: `{selected.get('label')}`",
        "",
        "## Selected Checks",
        "",
        f"- Frames: `{selected_checks.get('frames')}`",
        f"- Max candidate-vs-S585 abs diff: `{selected_checks.get('max_candidate_anchor_abs_diff')}`",
        f"- Max candidate-vs-S585 mean diff: `{selected_checks.get('max_candidate_anchor_mean_diff')}`",
        f"- Mean candidate-vs-S585 mean diff: `{selected_checks.get('mean_candidate_anchor_mean_diff')}`",
        f"- Max candidate-vs-S577 abs diff: `{selected_checks.get('max_candidate_accepted_abs_diff')}`",
        f"- Max candidate-vs-S577 mean diff: `{selected_checks.get('max_candidate_accepted_mean_diff')}`",
        f"- Mean candidate-vs-S577 mean diff: `{selected_checks.get('mean_candidate_accepted_mean_diff')}`",
        f"- Baseline max S585-vs-S577 mean diff: `{selected_checks.get('max_anchor_accepted_mean_diff')}`",
        f"- Strip GIF bytes: `{format_bytes(selected_checks.get('strip_gif_bytes', 0))}`",
        "",
        "## Candidate Sweep",
        "",
        "| Candidate | Strength | S585 Max | S585 Max MAD | S585 Mean MAD | S577 Max | S577 Max MAD | S577 Mean MAD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in summary.get("candidates") or []:
        checks = candidate.get("checks") or {}
        lines.append(
            f"| `{candidate.get('label')}` | {candidate.get('strength')} | "
            f"{checks.get('max_candidate_anchor_abs_diff')} | {checks.get('max_candidate_anchor_mean_diff')} | "
            f"{checks.get('mean_candidate_anchor_mean_diff')} | {checks.get('max_candidate_accepted_abs_diff')} | "
            f"{checks.get('max_candidate_accepted_mean_diff')} | {checks.get('mean_candidate_accepted_mean_diff')} |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    anchor_path = require_file(resolve_path(args.anchor_summary, root), "S632 anchor summary")
    anchor = read_json(anchor_path)
    if anchor.get("schema") != ANCHOR_SCHEMA:
        raise SystemExit(f"{args.anchor_summary}: expected {ANCHOR_SCHEMA}")
    if anchor.get("status") != "ready":
        raise SystemExit(f"{args.anchor_summary}: anchor status is {anchor.get('status')!r}")
    out_dir = os.path.abspath(args.out_dir)
    ensure_dir(out_dir)
    frames, missing, bounds = load_inputs(anchor, root)
    candidates = [render_candidate(frames, missing, bounds, candidate, out_dir, root) for candidate in args.candidate]
    selected = select_candidate(candidates, args)
    strip_paths, selected = build_selected_gallery(selected, out_dir, root, args.fps, args.keyframes)

    gallery_dir = ensure_dir(os.path.join(out_dir, "gallery"))
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    assets = []
    if selected and selected.get("strip_gif_repo_path"):
        assets.append(copy_asset(resolve_path(selected["strip_gif_repo_path"], root), assets_dir, "selected_s585_anchor_native_candidate.gif", "Selected S585 Anchor Native Candidate GIF", root))
    for index, strip_path in enumerate((selected or {}).get("sample_strip_paths") or []):
        assets.append(copy_asset(strip_path, assets_dir, f"selected_s585_anchor_native_candidate_strip_{index:02d}.png", f"Selected S585 Anchor Native Candidate Strip {index + 1}", root))

    status = "ready" if selected and not missing else "review"
    decision = "s585_anchor_native_candidate_ready" if status == "ready" else "hold"
    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "decision": decision,
        "source_anchor": {
            "repo_path": posix_rel(anchor_path, root),
            "schema": anchor.get("schema"),
            "status": anchor.get("status"),
            "sha256": sha256_file(anchor_path),
            "size": os.path.getsize(anchor_path),
        },
        "settings": {
            "accepted_abs_tolerance": args.accepted_abs_tolerance,
            "accepted_mean_tolerance": args.accepted_mean_tolerance,
            "anchor_abs_tolerance": args.anchor_abs_tolerance,
            "anchor_mean_tolerance": args.anchor_mean_tolerance,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "candidates": len(candidates),
            "frames": len(frames),
            "missing_references": len(missing),
            "selected_label": selected.get("label") if selected else None,
        },
        "missing": missing,
        "selected_candidate": selected or {},
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
        "schema": "lsfs_mitsuba_response_aov_s585_anchor_native_candidate_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    checks = (selected or {}).get("checks") or {}
    print(
        "status={status} decision={decision} candidates={candidates} selected={selected} "
        "s585_move={s585_move} s577_mad={s577_mad} summary={summary}".format(
            status=status,
            decision=decision,
            candidates=len(candidates),
            selected=(selected or {}).get("label"),
            s585_move=checks.get("max_candidate_anchor_abs_diff"),
            s577_mad=checks.get("max_candidate_accepted_mean_diff"),
            summary=summary_path,
        )
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anchor_summary", help="S632 response-AOV S585 anchor handoff summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--candidate", action="append", type=parse_candidate, default=default_candidates())
    parser.add_argument("--accepted-abs-tolerance", type=int, default=6)
    parser.add_argument("--accepted-mean-tolerance", type=float, default=0.50)
    parser.add_argument("--anchor-abs-tolerance", type=int, default=2)
    parser.add_argument("--anchor-mean-tolerance", type=float, default=0.11)
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S633 Response AOV S585 Anchor Native Candidate")
    parser.add_argument(
        "--next",
        default="Promote this S585-anchored native candidate into the process backend path, then publish if visual review is needed.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.accepted_abs_tolerance < 0:
        parser.error("accepted-abs-tolerance must be non-negative")
    if args.accepted_mean_tolerance < 0.0:
        parser.error("accepted-mean-tolerance must be non-negative")
    if args.anchor_abs_tolerance < 0:
        parser.error("anchor-abs-tolerance must be non-negative")
    if args.anchor_mean_tolerance < 0.0:
        parser.error("anchor-mean-tolerance must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
