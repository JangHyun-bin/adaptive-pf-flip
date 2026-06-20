#!/usr/bin/env python
"""Compare a native Mitsuba secondary candidate against the S335 contract."""

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


def asset_path(frame, role):
    asset = ((frame.get("assets") or {}).get(role) or {})
    return asset.get("path") or asset.get("repo_path")


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Candidate GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Candidate Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    verdict = summary.get("verdict", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Decision", verdict.get("decision")),
        ("Frames", checks.get("frames")),
        ("Candidate Max MAD", f"{checks.get('max_candidate_target_mean_abs_diff', 0.0):.3f}"),
        ("Contract Max MAD", f"{checks.get('contract_max_overlay_mean_abs_diff', 0.0):.3f}"),
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
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Candidate GIF"></section>' if gif else ""
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
        f"- Mean candidate->contract MAD: `{checks.get('mean_candidate_contract_mean_abs_diff')}`",
        f"- Max candidate->contract MAD: `{checks.get('max_candidate_contract_mean_abs_diff')}`",
        f"- Mean candidate->target MAD: `{checks.get('mean_candidate_target_mean_abs_diff')}`",
        f"- Max candidate->target MAD: `{checks.get('max_candidate_target_mean_abs_diff')}`",
        f"- Contract mean overlay MAD: `{checks.get('contract_mean_overlay_mean_abs_diff')}`",
        f"- Contract max overlay MAD: `{checks.get('contract_max_overlay_mean_abs_diff')}`",
        f"- Candidate beats contract mean: `{verdict.get('beats_contract_mean')}`",
        f"- Candidate beats contract max: `{verdict.get('beats_contract_max')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Candidate->Contract MAD | Candidate->Target MAD | Contract->Target MAD | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('candidate_contract_mean_abs_diff'):.4f} | "
            f"{frame.get('candidate_target_mean_abs_diff'):.4f} | "
            f"{frame.get('contract_target_mean_abs_diff'):.4f} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    if summary.get("missing_references"):
        lines.extend(["", "## Missing References", ""])
        for item in summary["missing_references"]:
            lines.append(f"- frame `{item.get('frame')}`: `{item}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def source_entry(path, root, label):
    return {
        "label": label,
        "path": path,
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def compare(args):
    require_pillow()
    root = os.getcwd()
    contract_path = require_file(args.contract, "secondary pass contract")
    render_path = require_file(args.actual_render_manifest, "actual render manifest")
    contract = read_json(contract_path)
    render = read_json(render_path)
    if contract.get("schema") != "lsfs_mitsuba_secondary_pass_contract":
        raise SystemExit(f"{args.contract}: expected lsfs_mitsuba_secondary_pass_contract schema")
    if contract.get("status") != "ready":
        raise SystemExit(f"{args.contract}: contract status is {contract.get('status')!r}")
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.actual_render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.actual_render_manifest}: render status is {render.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    contract_diff_dir = os.path.join(out_dir, "candidate_contract_diffs")
    target_diff_dir = os.path.join(out_dir, "candidate_target_diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (contract_diff_dir, target_diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    render_frames = output_frame_map(render.get("frames") or [])
    results = []
    missing = []
    strip_paths = []
    for index, contract_frame in enumerate(contract.get("frames") or []):
        frame_id = contract_frame.get("frame")
        output_frame = contract_frame.get("output_frame")
        render_frame = render_frames.get(output_frame)
        candidate_path = resolve_path(render_preview_path(render_frame))
        contract_overlay_path = resolve_path(asset_path(contract_frame, "overlay_graded"))
        target_path = resolve_path(asset_path(contract_frame, "target"))
        absent = []
        for role, path in (
            ("candidate", candidate_path),
            ("contract_overlay", contract_overlay_path),
            ("target", target_path),
        ):
            if not path or not os.path.isfile(path):
                absent.append({"role": role, "path": path})
        if absent:
            missing.append({"frame": frame_id, "output_frame": output_frame, "missing": absent})
            continue

        candidate = Image.open(candidate_path).convert("RGB")
        contract_overlay = Image.open(contract_overlay_path).convert("RGB")
        target = Image.open(target_path).convert("RGB")
        if candidate.size != contract_overlay.size:
            candidate = candidate.resize(contract_overlay.size, Image.Resampling.BICUBIC)
        if target.size != contract_overlay.size:
            target = target.resize(contract_overlay.size, Image.Resampling.BICUBIC)
        candidate_contract_diff = diff_image(candidate, contract_overlay)
        candidate_target_diff = diff_image(candidate, target)

        base_name = f"frame_{index:04d}.png"
        contract_diff_path = os.path.join(contract_diff_dir, base_name)
        target_diff_path = os.path.join(target_diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        candidate_contract_diff.save(contract_diff_path)
        candidate_target_diff.save(target_diff_path)
        labeled_strip(
            [candidate, contract_overlay, target, candidate_contract_diff, candidate_target_diff],
            ["native candidate", "S335 contract", "accepted target", "candidate-contract diff", "candidate-target diff"],
            strip_path,
        )
        strip_paths.append(strip_path)
        contract_metrics = contract_frame.get("metrics") or {}
        results.append({
            "frame": frame_id,
            "output_frame": output_frame,
            "candidate_repo_path": posix_rel(candidate_path, root),
            "contract_overlay_repo_path": posix_rel(contract_overlay_path, root),
            "target_repo_path": posix_rel(target_path, root),
            "candidate_contract_diff_repo_path": posix_rel(contract_diff_path, root),
            "candidate_target_diff_repo_path": posix_rel(target_diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "candidate_sha256": sha256_file(candidate_path),
            "contract_overlay_sha256": sha256_file(contract_overlay_path),
            "target_sha256": sha256_file(target_path),
            "candidate_contract_mean_abs_diff": mean_abs_diff(candidate, contract_overlay),
            "candidate_contract_max_abs_diff": max_abs_diff(candidate, contract_overlay),
            "candidate_target_mean_abs_diff": mean_abs_diff(candidate, target),
            "candidate_target_max_abs_diff": max_abs_diff(candidate, target),
            "contract_target_mean_abs_diff": contract_metrics.get("overlay_mean_abs_diff"),
            "contract_target_max_abs_diff": contract_metrics.get("overlay_max_abs_diff"),
        })

    if not results:
        raise SystemExit("no comparable frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(strip_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Candidate GIF", root)]
    key_indices = sorted(set(round(i * (len(results) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"candidate_strip_{out_index:02d}.png", f"Candidate Strip {out_index + 1}", root))

    checks = {
        "frames": len(results),
        "missing_references": len(missing),
        "mean_candidate_contract_mean_abs_diff": sum(item["candidate_contract_mean_abs_diff"] for item in results) / len(results),
        "max_candidate_contract_mean_abs_diff": max(item["candidate_contract_mean_abs_diff"] for item in results),
        "max_candidate_contract_max_abs_diff": max(item["candidate_contract_max_abs_diff"] for item in results),
        "mean_candidate_target_mean_abs_diff": sum(item["candidate_target_mean_abs_diff"] for item in results) / len(results),
        "max_candidate_target_mean_abs_diff": max(item["candidate_target_mean_abs_diff"] for item in results),
        "max_candidate_target_max_abs_diff": max(item["candidate_target_max_abs_diff"] for item in results),
        "contract_mean_overlay_mean_abs_diff": (contract.get("checks") or {}).get("mean_overlay_mean_abs_diff"),
        "contract_max_overlay_mean_abs_diff": (contract.get("checks") or {}).get("max_overlay_mean_abs_diff"),
        "contract_max_overlay_max_abs_diff": (contract.get("checks") or {}).get("max_overlay_max_abs_diff"),
        "gif_bytes": os.path.getsize(gif_path),
    }
    beats_mean = checks["mean_candidate_target_mean_abs_diff"] <= checks["contract_mean_overlay_mean_abs_diff"]
    beats_max = checks["max_candidate_target_mean_abs_diff"] <= checks["contract_max_overlay_mean_abs_diff"]
    verdict = {
        "candidate_label": args.candidate_label,
        "beats_contract_mean": beats_mean,
        "beats_contract_max": beats_max,
        "decision": "candidate_beats_contract" if beats_mean and beats_max else "candidate_needs_work",
        "target": "replace the S335 overlay only when both mean and max target MAD beat the contract",
    }
    status = "ready" if not missing else "review"
    summary_path = os.path.join(out_dir, "secondary_native_candidate_gap_summary.json")
    summary = {
        "schema": "lsfs_mitsuba_secondary_native_candidate_gap",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "verdict": verdict,
        "sources": {
            "contract": source_entry(contract_path, root, "secondary pass contract"),
            "actual_render_manifest": source_entry(render_path, root, "actual render manifest"),
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
    summary_asset = copy_asset(summary_path, assets_dir, "secondary_native_candidate_gap_summary.json", "Candidate gap summary", root)
    contract_asset = copy_asset(contract_path, assets_dir, "secondary_pass_contract.json", "Secondary pass contract", root)
    render_asset = copy_asset(render_path, assets_dir, "mitsuba_render.json", "Actual render manifest", root)
    metadata_files = [summary_asset, contract_asset, render_asset]
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
        "schema": "lsfs_mitsuba_secondary_native_candidate_gap_gallery",
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
        f"candidate_max_target_mad={checks['max_candidate_target_mean_abs_diff']:.6f} "
        f"contract_max_mad={checks['contract_max_overlay_mean_abs_diff']} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare a native Mitsuba secondary candidate against a secondary pass contract")
    parser.add_argument("contract")
    parser.add_argument("actual_render_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate-label", default="native_candidate")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Secondary Native Candidate Gap")
    parser.add_argument("--report")
    parser.add_argument(
        "--next",
        default="Use this candidate gap to decide the next renderer-native secondary tuning pass.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    compare(args)


if __name__ == "__main__":
    main()
