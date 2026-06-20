#!/usr/bin/env python
"""Dry-run a low-frequency renderer job manifest."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

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
from build_mitsuba_low_frequency_parity_texture_package import diff_stats, write_gif


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to dry-run low-frequency renderer jobs")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def clamp_int(value):
    return max(0, min(255, int(round(value))))


def blend_delta(base, positive, negative, gain):
    base_bytes = base.convert("RGB").tobytes()
    pos_bytes = positive.convert("RGB").tobytes()
    neg_bytes = negative.convert("RGB").tobytes()
    out = bytearray(len(base_bytes))
    for index in range(len(base_bytes)):
        out[index] = clamp_int(int(base_bytes[index]) + (int(pos_bytes[index]) - int(neg_bytes[index])) * gain)
    return Image.frombytes("RGB", base.size, bytes(out))


def file_path(item, root):
    return resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)


def ensure_parent(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def image_entry(path, root):
    return {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
        "dimensions": image_dimensions(path),
    }


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (9, 14, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        strip.paste(panel.convert("RGB"), (x, label_h))
        draw.text((x + 8, 8), labels[index], fill=(233, 244, 248))
    ensure_parent(out_path)
    strip.save(out_path)


def copy_asset(src, assets_dir, name, label, root):
    source = require_file(resolve_path(src, root), label)
    dest = os.path.join(assets_dir, name)
    ensure_parent(dest)
    if os.path.abspath(source) != os.path.abspath(dest):
        shutil.copy2(source, dest)
    entry = {
        "label": label,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source_repo_path": posix_rel(source, root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def summary_metadata_entry(summary_path, assets_dir, root):
    dest = os.path.join(assets_dir, "renderer_job_dry_run_summary.json")
    return {
        "label": "Dry Run Summary",
        "repo_path": posix_rel(dest, root),
        "href": "assets/renderer_job_dry_run_summary.json",
        "source_repo_path": posix_rel(summary_path, root),
    }


def run_frame(job, frame_job, root, strip_dir):
    inputs = frame_job.get("inputs") or {}
    paths = {
        "base_rgb": file_path(inputs.get("base_rgb"), root),
        "positive_delta_rgb": file_path(inputs.get("positive_delta_rgb"), root),
        "negative_delta_rgb": file_path(inputs.get("negative_delta_rgb"), root),
        "accepted_reference": file_path(frame_job.get("accepted_reference"), root),
    }
    missing = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
    if missing:
        return {"status": "failed", "frame": frame_job.get("frame"), "missing": missing}
    base = Image.open(paths["base_rgb"]).convert("RGB")
    positive = Image.open(paths["positive_delta_rgb"]).convert("RGB")
    negative = Image.open(paths["negative_delta_rgb"]).convert("RGB")
    reference = Image.open(paths["accepted_reference"]).convert("RGB")
    if any(image.size != base.size for image in (positive, negative, reference)):
        return {"status": "failed", "frame": frame_job.get("frame"), "dimension_mismatch": True}
    gain = float(((job.get("render_settings") or {}).get("texture_gain") or 1.0))
    rendered = blend_delta(base, positive, negative, gain)
    stats = diff_stats(rendered, reference)
    output_image = resolve_path(((frame_job.get("outputs") or {}).get("image") or {}).get("repo_path"), root)
    output_metadata = resolve_path(((frame_job.get("outputs") or {}).get("metadata") or {}).get("repo_path"), root)
    output_validation = resolve_path(((frame_job.get("outputs") or {}).get("validation") or {}).get("repo_path"), root)
    ensure_parent(output_image)
    rendered.save(output_image)
    metadata = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_frame_metadata",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "job_index": frame_job.get("job_index"),
        "stage": frame_job.get("stage"),
        "inputs": {
            name: {
                "repo_path": posix_rel(path, root),
                "sha256": sha256_file(path),
                "size": os.path.getsize(path),
            }
            for name, path in paths.items()
        },
        "output": image_entry(output_image, root),
    }
    validation = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_frame_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "status": "passed" if stats["max_abs_diff"] == 0 and stats["mean_abs_diff"] == 0.0 else "failed",
        "reference": {
            "repo_path": posix_rel(paths["accepted_reference"], root),
            "expected_sha256": (frame_job.get("accepted_reference") or {}).get("expected_sha256"),
            "sha256": sha256_file(paths["accepted_reference"]),
        },
        "output": image_entry(output_image, root),
        "diff": {
            "mean_abs_diff": stats["mean_abs_diff"],
            "max_abs_diff": stats["max_abs_diff"],
            "mismatched_coverage": stats["mismatched_coverage"],
        },
    }
    write_json(output_metadata, metadata)
    write_json(output_validation, validation)
    strip_path = os.path.join(strip_dir, f"frame_{frame_job.get('job_index', 0):04d}_dry_run.png")
    labeled_strip(
        [base, positive, negative, rendered, reference, stats["diff_image"]],
        ["base", "positive", "negative", "dry-run output", "accepted reference", "diff x8"],
        strip_path,
    )
    return {
        "status": validation["status"],
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "job_index": frame_job.get("job_index"),
        "output_image_repo_path": posix_rel(output_image, root),
        "metadata_repo_path": posix_rel(output_metadata, root),
        "validation_repo_path": posix_rel(output_validation, root),
        "strip_repo_path": posix_rel(strip_path, root),
        "output_sha256": sha256_file(output_image),
        "reference_sha256": sha256_file(paths["accepted_reference"]),
        "expected_reference_sha256": (frame_job.get("accepted_reference") or {}).get("expected_sha256"),
        "mean_abs_diff": stats["mean_abs_diff"],
        "max_abs_diff": stats["max_abs_diff"],
        "mismatched_coverage": stats["mismatched_coverage"],
    }


def html_page(title, summary, assets, metadata_files):
    shot = next((item for item in assets if item.get("label") == "Dry Run GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Dry Run Strip")]
    checks = summary.get("checks") or {}
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Passed", checks.get("passed_frames")),
        ("Failed", checks.get("failed_frames")),
        ("Max Diff", checks.get("max_abs_diff")),
        ("Mean Diff", checks.get("max_mean_abs_diff")),
    ]
    metrics = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in tiles)
    hero = f'<section class="hero"><img src="{shot["href"]}" alt="Dry-run GIF"></section>' if shot else ""
    frame_html = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #070c10; --panel: #101820; --line: #2b3942; --ink: #edf7fb; --muted: #9cadb7; --accent: #8bdcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 42px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111; margin-bottom: 14px; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
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
    <section class="metrics">{metrics}</section>
    <section class="grid">{frame_html}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Passed frames: `{checks.get('passed_frames')}`",
        f"- Failed frames: `{checks.get('failed_frames')}`",
        f"- Missing frames: `{checks.get('missing_frames')}`",
        f"- Max abs diff: `{checks.get('max_abs_diff')}`",
        f"- Max mean abs diff: `{checks.get('max_mean_abs_diff')}`",
        f"- Output bytes: `{format_bytes(checks.get('output_bytes', 0))}`",
        "",
        "## Frame Results",
        "",
        "| Job | Frame | Output | Status | Max Diff | Output | Validation |",
        "| ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('output_frame')} | `{frame.get('status')}` | "
            f"{frame.get('max_abs_diff')} | `{frame.get('output_image_repo_path')}` | `{frame.get('validation_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "Use this dry run as the production renderer/export execution smoke gate.", ""])
    return "\n".join(lines)


def run_job(args):
    require_pillow()
    root = os.getcwd()
    job_path = require_file(resolve_path(args.job, root), "renderer job manifest")
    job = read_json(job_path)
    if job.get("schema") != "lsfs_mitsuba_low_frequency_renderer_job_manifest":
        raise SystemExit(f"{args.job}: expected lsfs_mitsuba_low_frequency_renderer_job_manifest schema")
    if job.get("status") != "ready":
        raise SystemExit(f"{args.job}: job status is {job.get('status')!r}")
    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (strip_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)
    frame_results = [run_frame(job, frame, root, strip_dir) for frame in job.get("frame_jobs") or []]
    passed = [item for item in frame_results if item.get("status") == "passed"]
    failed = [item for item in frame_results if item.get("status") != "passed"]
    output_paths = [resolve_path(item.get("output_image_repo_path"), root) for item in passed]
    strip_paths = [resolve_path(item.get("strip_repo_path"), root) for item in passed]
    gif_path = os.path.join(assets_dir, "shot.gif")
    strip_gif_path = os.path.join(assets_dir, "dry_run_strips.gif")
    if output_paths:
        write_gif(output_paths, gif_path, args.fps)
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)
    assets = []
    if os.path.isfile(gif_path):
        assets.append(copy_asset(gif_path, assets_dir, "shot.gif", "Dry Run GIF", root))
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "dry_run_strips.gif", "Dry Run Strip GIF", root))
    keyframes = max(1, min(args.keyframes, len(passed)))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["output_image_repo_path"], assets_dir, f"keyframe_{out_index:02d}.png", f"Dry Run Keyframe {out_index + 1}", root))
        assets.append(copy_asset(passed[frame_index]["strip_repo_path"], assets_dir, f"dry_run_strip_{out_index:02d}.png", f"Dry Run Strip {out_index + 1}", root))
    summary_path = os.path.abspath(args.summary)
    checks = {
        "frames": len(frame_results),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "missing_frames": sum(1 for item in frame_results if item.get("missing")),
        "max_abs_diff": max((item.get("max_abs_diff", 999) for item in frame_results), default=999),
        "max_mean_abs_diff": max((item.get("mean_abs_diff", 999.0) for item in frame_results), default=999.0),
        "output_bytes": sum(os.path.getsize(path) for path in output_paths if path and os.path.isfile(path)),
        "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
    }
    status = "passed" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["max_abs_diff"] == 0
        and checks["max_mean_abs_diff"] == 0.0
    ) else "failed"
    summary = {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_dry_run",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source_job": {
            "repo_path": posix_rel(job_path, root),
            "schema": job.get("schema"),
            "status": job.get("status"),
            "sha256": sha256_file(job_path),
            "size": os.path.getsize(job_path),
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
            "stage": "renderer_post_tonemap_low_frequency_runtime_consumer",
        },
        "checks": checks,
        "frames": frame_results,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        summary_metadata_entry(summary_path, assets_dir, root),
        copy_asset(job_path, assets_dir, "renderer_job_manifest.json", "Renderer Job Manifest", root),
    ]
    index_path = os.path.join(gallery_dir, "index.html")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    shutil.copy2(summary_path, resolve_path(metadata_files[0]["repo_path"], root))
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_renderer_job_dry_run_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} passed={checks['passed_frames']} "
        f"max_diff={checks['max_abs_diff']} summary={summary_path}"
    )
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Dry-run a low-frequency renderer job manifest")
    parser.add_argument("job")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S500 Mitsuba Low Frequency Renderer Job Dry Run")
    parser.add_argument("--next", default="Use this dry run as the execution smoke gate before connecting a real renderer backend.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run_job(args)


if __name__ == "__main__":
    main()
