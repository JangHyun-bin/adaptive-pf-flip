#!/usr/bin/env python
"""Compare a native Mitsuba render against a depth-aware composite bridge."""

import argparse
import os
import shutil
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
from compare_mitsuba_renderer_target_gap import (
    Image,
    copy_asset,
    diff_image,
    labeled_strip,
    max_abs_diff,
    mean_abs_diff,
    output_frame_map,
    render_preview_path,
    require_pillow,
    resolve_path,
    write_gif,
)


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Replacement Gap GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Replacement Gap Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    verdict = summary.get("verdict", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Decision", verdict.get("decision")),
        ("Frames", checks.get("frames")),
        ("Native Max Target MAD", f"{checks.get('max_candidate_target_mean_abs_diff', 0.0):.3f}"),
        ("Bridge Max Target MAD", f"{checks.get('bridge_max_target_mean_abs_diff', 0.0):.3f}"),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Replacement Gap GIF"></section>' if gif else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #111a21; --ink: #edf7fb; --muted: #a2b5bf; --line: #2e3d47; --accent: #9fd9ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111820; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); background: var(--panel); }}
    figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section class="grid">{frame_html}</section>
  </main>
</body>
</html>
"""


def source_entry(path, root, label, payload=None):
    entry = {
        "label": label,
        "path": path,
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
    return entry


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks", {})
    verdict = summary.get("verdict", {})
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        f"Decision: `{verdict.get('decision')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Mean native->bridge MAD: `{checks.get('mean_candidate_bridge_mean_abs_diff')}`",
        f"- Max native->bridge MAD: `{checks.get('max_candidate_bridge_mean_abs_diff')}`",
        f"- Mean native->target MAD: `{checks.get('mean_candidate_target_mean_abs_diff')}`",
        f"- Max native->target MAD: `{checks.get('max_candidate_target_mean_abs_diff')}`",
        f"- Bridge mean target MAD: `{checks.get('bridge_mean_target_mean_abs_diff')}`",
        f"- Bridge max target MAD: `{checks.get('bridge_max_target_mean_abs_diff')}`",
        f"- Native beats bridge mean: `{verdict.get('beats_bridge_mean')}`",
        f"- Native beats bridge max: `{verdict.get('beats_bridge_max')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('candidate_bridge_mean_abs_diff'):.4f} | "
            f"{frame.get('candidate_target_mean_abs_diff'):.4f} | "
            f"{frame.get('bridge_target_mean_abs_diff'):.4f} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    if summary.get("missing_references"):
        lines.extend(["", "## Missing References", ""])
        for item in summary["missing_references"]:
            lines.append(f"- frame `{item.get('frame')}`: `{item}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def compare(args):
    require_pillow()
    root = os.getcwd()
    bridge_path = require_file(args.depth_aware_composite, "depth-aware composite summary")
    render_path = require_file(args.actual_render_manifest, "actual render manifest")
    bridge = read_json(bridge_path)
    render = read_json(render_path)
    if bridge.get("schema") != "lsfs_mitsuba_depth_aware_secondary_composite":
        raise SystemExit(f"{args.depth_aware_composite}: expected lsfs_mitsuba_depth_aware_secondary_composite schema")
    if bridge.get("status") != "ready":
        raise SystemExit(f"{args.depth_aware_composite}: bridge status is {bridge.get('status')!r}")
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.actual_render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.actual_render_manifest}: render status is {render.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    bridge_diff_dir = os.path.join(out_dir, "candidate_bridge_diffs")
    target_diff_dir = os.path.join(out_dir, "candidate_target_diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (bridge_diff_dir, target_diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    render_frames = output_frame_map(render.get("frames") or [])
    results = []
    missing = []
    strip_paths = []
    for index, bridge_frame in enumerate(bridge.get("frames") or []):
        frame_id = bridge_frame.get("frame")
        output_frame = bridge_frame.get("output_frame")
        render_frame = render_frames.get(output_frame)
        candidate_path = resolve_path(render_preview_path(render_frame))
        composite_path = resolve_path(bridge_frame.get("composite_repo_path"))
        target_path = resolve_path(bridge_frame.get("target_repo_path"))
        absent = []
        for role, path in (
            ("candidate", candidate_path),
            ("bridge_composite", composite_path),
            ("target", target_path),
        ):
            if not path or not os.path.isfile(path):
                absent.append({"role": role, "path": path})
        if absent:
            missing.append({"frame": frame_id, "output_frame": output_frame, "missing": absent})
            continue

        candidate = Image.open(candidate_path).convert("RGB")
        bridge_img = Image.open(composite_path).convert("RGB")
        target = Image.open(target_path).convert("RGB")
        if candidate.size != bridge_img.size:
            candidate = candidate.resize(bridge_img.size, Image.Resampling.BICUBIC)
        if target.size != bridge_img.size:
            target = target.resize(bridge_img.size, Image.Resampling.BICUBIC)
        candidate_bridge_diff = diff_image(candidate, bridge_img)
        candidate_target_diff = diff_image(candidate, target)

        base_name = f"frame_{index:04d}.png"
        bridge_diff_path = os.path.join(bridge_diff_dir, base_name)
        target_diff_path = os.path.join(target_diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        candidate_bridge_diff.save(bridge_diff_path)
        candidate_target_diff.save(target_diff_path)
        labeled_strip(
            [candidate, bridge_img, target, candidate_bridge_diff, candidate_target_diff],
            ["native candidate", "S341 C3 bridge", "accepted target", "candidate-bridge diff", "candidate-target diff"],
            strip_path,
        )
        strip_paths.append(strip_path)
        results.append({
            "frame": frame_id,
            "output_frame": output_frame,
            "candidate_repo_path": posix_rel(candidate_path, root),
            "bridge_composite_repo_path": posix_rel(composite_path, root),
            "target_repo_path": posix_rel(target_path, root),
            "candidate_bridge_diff_repo_path": posix_rel(bridge_diff_path, root),
            "candidate_target_diff_repo_path": posix_rel(target_diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "candidate_sha256": sha256_file(candidate_path),
            "bridge_composite_sha256": sha256_file(composite_path),
            "target_sha256": sha256_file(target_path),
            "candidate_bridge_mean_abs_diff": mean_abs_diff(candidate, bridge_img),
            "candidate_bridge_max_abs_diff": max_abs_diff(candidate, bridge_img),
            "candidate_target_mean_abs_diff": mean_abs_diff(candidate, target),
            "candidate_target_max_abs_diff": max_abs_diff(candidate, target),
            "bridge_target_mean_abs_diff": bridge_frame.get("target_mean_abs_diff"),
            "bridge_target_max_abs_diff": bridge_frame.get("target_max_abs_diff"),
        })

    if not results:
        raise SystemExit("no comparable frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Replacement Gap GIF", root)]
    key_indices = sorted(set(round(i * (len(results) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(
            strip_paths[frame_index],
            assets_dir,
            f"replacement_gap_strip_{out_index:02d}.png",
            f"Replacement Gap Strip {out_index + 1}",
            root,
        ))

    bridge_checks = bridge.get("checks") or {}
    checks = {
        "frames": len(results),
        "missing_references": len(missing),
        "mean_candidate_bridge_mean_abs_diff": sum(item["candidate_bridge_mean_abs_diff"] for item in results) / len(results),
        "max_candidate_bridge_mean_abs_diff": max(item["candidate_bridge_mean_abs_diff"] for item in results),
        "max_candidate_bridge_max_abs_diff": max(item["candidate_bridge_max_abs_diff"] for item in results),
        "mean_candidate_target_mean_abs_diff": sum(item["candidate_target_mean_abs_diff"] for item in results) / len(results),
        "max_candidate_target_mean_abs_diff": max(item["candidate_target_mean_abs_diff"] for item in results),
        "max_candidate_target_max_abs_diff": max(item["candidate_target_max_abs_diff"] for item in results),
        "bridge_mean_target_mean_abs_diff": bridge_checks.get("mean_target_mean_abs_diff"),
        "bridge_max_target_mean_abs_diff": bridge_checks.get("max_target_mean_abs_diff"),
        "bridge_max_target_max_abs_diff": bridge_checks.get("max_target_max_abs_diff"),
        "gif_bytes": os.path.getsize(gif_path),
    }
    beats_mean = checks["mean_candidate_target_mean_abs_diff"] <= checks["bridge_mean_target_mean_abs_diff"]
    beats_max = checks["max_candidate_target_mean_abs_diff"] <= checks["bridge_max_target_mean_abs_diff"]
    verdict = {
        "candidate_label": args.candidate_label,
        "beats_bridge_mean": beats_mean,
        "beats_bridge_max": beats_max,
        "decision": "native_candidate_can_replace_bridge" if beats_mean and beats_max else "native_candidate_needs_work",
        "target": "replace the S341 C3 bridge only when native render beats both mean and max target MAD",
    }
    status = "ready" if not missing else "review"
    summary_path = os.path.join(out_dir, "depth_aware_native_replacement_gap_summary.json")
    summary = {
        "schema": "lsfs_mitsuba_depth_aware_native_replacement_gap",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "verdict": verdict,
        "sources": {
            "depth_aware_composite": source_entry(bridge_path, root, "depth-aware composite summary", bridge),
            "actual_render_manifest": source_entry(render_path, root, "actual render manifest", render),
        },
        "settings": {
            "candidate_label": args.candidate_label,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": results,
        "gallery": {},
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "depth_aware_native_replacement_gap_summary.json", "Replacement gap summary", root)
    summary_asset.pop("sha256", None)
    summary_asset["hash_policy"] = "self_referential_json"
    bridge_asset = copy_asset(bridge_path, assets_dir, "depth_aware_secondary_composite_summary.json", "Depth-aware composite summary", root)
    render_asset = copy_asset(render_path, assets_dir, "mitsuba_render.json", "Actual render manifest", root)
    metadata_files = [summary_asset, bridge_asset, render_asset]
    index_path = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_depth_aware_native_replacement_gap_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={summary['status']} decision={verdict['decision']} frames={checks['frames']} "
        f"native_max_target_mad={checks['max_candidate_target_mean_abs_diff']:.6f} "
        f"bridge_max_target_mad={checks['bridge_max_target_mean_abs_diff']} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare a native Mitsuba render against a depth-aware composite bridge")
    parser.add_argument("depth_aware_composite")
    parser.add_argument("actual_render_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate-label", default="native_candidate")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Depth-Aware Native Replacement Gap")
    parser.add_argument("--report")
    parser.add_argument(
        "--next",
        default="Use this native replacement gap before claiming a renderer-native secondary pass can replace the bridge.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    compare(args)


if __name__ == "__main__":
    main()
