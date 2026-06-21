#!/usr/bin/env python
"""Dry-run response-AOV scene frame descriptors into renderer/cache outputs."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
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


JOB_SCHEMA = "lsfs_mitsuba_response_aov_scene_job_manifest"
DESCRIPTOR_SCHEMA = "lsfs_mitsuba_response_aov_scene_frame_job"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_scene_job_dry_run"
STAGE = "renderer_cache_scene_response_aov_consumer"


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to dry-run response-AOV scene jobs")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def ensure_parent(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def clamp(value):
    return max(0, min(255, int(value)))


def reconstruct(base_img, positive_img, negative_img):
    base = base_img.convert("RGB").tobytes()
    positive = positive_img.convert("RGB").tobytes()
    negative = negative_img.convert("RGB").tobytes()
    out = bytearray(len(base))
    for index in range(len(base)):
        out[index] = clamp(int(base[index]) + int(positive[index]) - int(negative[index]))
    return Image.frombytes("RGB", base_img.size, bytes(out))


def layer_visual(image, gain):
    rgb = image.convert("RGB")
    if gain <= 1.0:
        return rgb
    return Image.eval(rgb, lambda value: clamp(round(value * gain)))


def diff_visual(diff_image):
    return ImageChops.multiply(diff_image.convert("RGB"), Image.new("RGB", diff_image.size, (8, 8, 8)))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        draw.rectangle((x, 0, x + width, label_h), fill=(17, 27, 35))
        draw.text((x + 8, 8), labels[index], fill=(229, 242, 248))
        strip.paste(panel.convert("RGB"), (x, label_h))
    ensure_parent(out_path)
    strip.save(out_path)


def ref_path(ref, root):
    path = resolve_path((ref or {}).get("repo_path") or (ref or {}).get("path"), root)
    return path if path and os.path.isfile(path) else None


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


def metadata_entry(path, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    return {
        "label": label,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source_repo_path": posix_rel(path, root),
    }


def load_descriptor(frame_job, root):
    descriptor_path = require_file(ref_path(frame_job.get("descriptor"), root), "frame descriptor")
    descriptor = read_json(descriptor_path)
    if descriptor.get("schema") != DESCRIPTOR_SCHEMA:
        raise SystemExit(f"{descriptor_path}: expected {DESCRIPTOR_SCHEMA} schema")
    if descriptor.get("stage") != STAGE:
        raise SystemExit(f"{descriptor_path}: expected stage {STAGE}")
    return descriptor_path, descriptor


def run_frame(frame_job, root, out_dir, strip_dir, preview_gain):
    descriptor_path, descriptor = load_descriptor(frame_job, root)
    inputs = descriptor.get("inputs") or {}
    layers = inputs.get("aov_layers") or {}
    required = {
        "base_rgb": ref_path(layers.get("base_rgb"), root),
        "response_positive_rgb": ref_path(layers.get("response_positive_rgb"), root),
        "response_negative_rgb": ref_path(layers.get("response_negative_rgb"), root),
        "selected_composite_rgb": ref_path(layers.get("selected_composite_rgb"), root),
        "imported_composite": ref_path(inputs.get("imported_composite"), root),
    }
    missing = [name for name, path in required.items() if not path]
    if missing:
        return {
            "status": "failed",
            "job_index": frame_job.get("job_index"),
            "frame": frame_job.get("frame"),
            "missing": missing,
            "descriptor_repo_path": posix_rel(descriptor_path, root),
        }

    base = Image.open(required["base_rgb"]).convert("RGB")
    positive = Image.open(required["response_positive_rgb"]).convert("RGB")
    negative = Image.open(required["response_negative_rgb"]).convert("RGB")
    selected = Image.open(required["selected_composite_rgb"]).convert("RGB")
    imported = Image.open(required["imported_composite"]).convert("RGB")
    if any(image.size != base.size for image in (positive, negative, selected, imported)):
        return {
            "status": "failed",
            "job_index": frame_job.get("job_index"),
            "frame": frame_job.get("frame"),
            "dimension_mismatch": True,
            "descriptor_repo_path": posix_rel(descriptor_path, root),
        }

    rendered = reconstruct(base, positive, negative)
    selected_diff = diff_stats(rendered, selected)
    imported_diff = diff_stats(rendered, imported)
    outputs = descriptor.get("outputs") or {}
    output_image = resolve_path(((outputs.get("renderer_candidate") or {}).get("repo_path")), root)
    output_metadata = resolve_path(((outputs.get("metadata") or {}).get("repo_path")), root)
    output_validation = resolve_path(((outputs.get("validation") or {}).get("repo_path")), root)
    if not output_image:
        output_image = os.path.join(out_dir, "renderer_frames", f"frame_{frame_job.get('job_index', 0):04d}.png")
    if not output_metadata:
        output_metadata = os.path.join(out_dir, "renderer_metadata", f"frame_{frame_job.get('job_index', 0):04d}_metadata.json")
    if not output_validation:
        output_validation = os.path.join(out_dir, "renderer_validation", f"frame_{frame_job.get('job_index', 0):04d}_validation.json")

    ensure_parent(output_image)
    rendered.save(output_image)
    strip_path = os.path.join(strip_dir, f"frame_{frame_job.get('job_index', 0):04d}_scene_aov_dry_run.png")
    labeled_strip(
        [
            base,
            layer_visual(positive, preview_gain),
            layer_visual(negative, preview_gain),
            rendered,
            selected,
            diff_visual(selected_diff["diff_image"]),
        ],
        ["base", "+response", "-response", "dry-run", "selected", "diff"],
        strip_path,
    )

    status = "passed" if (
        selected_diff["max_abs_diff"] == 0
        and selected_diff["mean_abs_diff"] == 0.0
        and imported_diff["max_abs_diff"] == 0
        and imported_diff["mean_abs_diff"] == 0.0
    ) else "failed"
    metadata = {
        "schema": "lsfs_mitsuba_response_aov_scene_frame_metadata",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "job_index": frame_job.get("job_index"),
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "descriptor": {
            "repo_path": posix_rel(descriptor_path, root),
            "sha256": sha256_file(descriptor_path),
            "size": os.path.getsize(descriptor_path),
        },
        "scene_frame": descriptor.get("scene_frame"),
        "source_frame": descriptor.get("source_frame"),
        "render_data": descriptor.get("render_data") or {},
        "visual_gate": descriptor.get("visual_gate") or {},
        "inputs": {name: image_entry(path, root) for name, path in required.items()},
        "output": image_entry(output_image, root),
    }
    validation = {
        "schema": "lsfs_mitsuba_response_aov_scene_frame_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "job_index": frame_job.get("job_index"),
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "selected_diff": {
            "mean_abs_diff": selected_diff["mean_abs_diff"],
            "max_abs_diff": selected_diff["max_abs_diff"],
            "mismatched_coverage": selected_diff["mismatched_coverage"],
        },
        "imported_diff": {
            "mean_abs_diff": imported_diff["mean_abs_diff"],
            "max_abs_diff": imported_diff["max_abs_diff"],
            "mismatched_coverage": imported_diff["mismatched_coverage"],
        },
        "expectations": descriptor.get("validation_expectations") or {},
        "output": image_entry(output_image, root),
    }
    write_json(output_metadata, metadata)
    write_json(output_validation, validation)
    return {
        "status": status,
        "job_index": frame_job.get("job_index"),
        "frame": frame_job.get("frame"),
        "output_frame": frame_job.get("output_frame"),
        "scene_frame": descriptor.get("scene_frame"),
        "source_frame": descriptor.get("source_frame"),
        "descriptor_repo_path": posix_rel(descriptor_path, root),
        "output_image_repo_path": posix_rel(output_image, root),
        "metadata_repo_path": posix_rel(output_metadata, root),
        "validation_repo_path": posix_rel(output_validation, root),
        "strip_repo_path": posix_rel(strip_path, root),
        "selected_mean_abs_diff": selected_diff["mean_abs_diff"],
        "selected_max_abs_diff": selected_diff["max_abs_diff"],
        "selected_mismatched_coverage": selected_diff["mismatched_coverage"],
        "imported_mean_abs_diff": imported_diff["mean_abs_diff"],
        "imported_max_abs_diff": imported_diff["max_abs_diff"],
        "imported_mismatched_coverage": imported_diff["mismatched_coverage"],
        "output_sha256": sha256_file(output_image),
        "visual_gate": descriptor.get("visual_gate") or {},
    }


def html_page(summary, assets, metadata_files):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item.get("label") == "Scene AOV Dry Run GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Scene AOV Dry Run Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Passed", checks.get("passed_frames")),
            ("Missing", checks.get("missing_frames")),
            ("Selected Max", checks.get("max_selected_abs_diff")),
            ("Imported Max", checks.get("max_imported_abs_diff")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="scene AOV dry run GIF"></section>' if gif else ""
    frame_html = "\n".join(
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
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --line: #30414c; --ink: #edf7fb; --muted: #9fb4c1; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 42px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 27px; font-weight: 670; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; margin: 0 0 12px; }}
    .hero img, figure img {{ width: 100%; display: block; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; min-height: 58px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    strong {{ display: block; font-size: 15px; word-break: break-word; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <header><h1>{summary['title']}</h1><nav>{links}</nav></header>
  {hero}
  <section class="tiles">{tiles}</section>
  <section>{frame_html}</section>
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
        "## Input",
        "",
        f"- Job manifest: `{summary['source_job']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Passed frames: `{checks.get('passed_frames')}`",
        f"- Failed frames: `{checks.get('failed_frames')}`",
        f"- Missing frames: `{checks.get('missing_frames')}`",
        f"- Max selected abs diff: `{checks.get('max_selected_abs_diff')}`",
        f"- Max selected mean abs diff: `{checks.get('max_selected_mean_abs_diff')}`",
        f"- Max imported abs diff: `{checks.get('max_imported_abs_diff')}`",
        f"- Max imported mean abs diff: `{checks.get('max_imported_mean_abs_diff')}`",
        f"- Output bytes: `{format_bytes(checks.get('output_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Job | Frame | Scene | Source | Status | Selected Max | Imported Max | Output |",
        "| ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('job_index')} | {frame.get('frame')} | {frame.get('scene_frame')} | "
            f"{frame.get('source_frame')} | `{frame.get('status')}` | "
            f"{frame.get('selected_max_abs_diff')} | {frame.get('imported_max_abs_diff')} | "
            f"`{frame.get('output_image_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run_job(args):
    require_pillow()
    root = os.getcwd()
    job_path = require_file(resolve_path(args.job_manifest, root), "response-AOV scene job manifest")
    job = read_json(job_path)
    if job.get("schema") != JOB_SCHEMA:
        raise SystemExit(f"{args.job_manifest}: expected {JOB_SCHEMA} schema")
    if job.get("status") != "ready":
        raise SystemExit(f"{args.job_manifest}: job status is {job.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (strip_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    frame_results = [
        run_frame(frame_job, root, out_dir, strip_dir, args.preview_gain)
        for frame_job in job.get("frames") or []
    ]
    passed = [item for item in frame_results if item.get("status") == "passed"]
    failed = [item for item in frame_results if item.get("status") != "passed"]
    output_paths = [resolve_path(item.get("output_image_repo_path"), root) for item in passed]
    strip_paths = [resolve_path(item.get("strip_repo_path"), root) for item in passed]
    gif_path = os.path.join(assets_dir, "scene_aov_dry_run.gif")
    strip_gif_path = os.path.join(assets_dir, "scene_aov_dry_run_strips.gif")
    if output_paths:
        write_gif(output_paths, gif_path, args.fps)
    if strip_paths:
        write_gif(strip_paths, strip_gif_path, args.fps)

    assets = []
    if os.path.isfile(gif_path):
        assets.append(copy_asset(gif_path, assets_dir, "scene_aov_dry_run.gif", "Scene AOV Dry Run GIF", root))
    if os.path.isfile(strip_gif_path):
        assets.append(copy_asset(strip_gif_path, assets_dir, "scene_aov_dry_run_strips.gif", "Scene AOV Dry Run Strip GIF", root))
    keyframes = max(1, min(args.keyframes, len(passed)))
    key_indices = sorted(set(round(i * (len(passed) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes))) if passed else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(passed[frame_index]["strip_repo_path"], assets_dir, f"scene_aov_dry_run_strip_{out_index:02d}.png", f"Scene AOV Dry Run Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary) if args.summary else os.path.join(out_dir, "response_aov_scene_job_dry_run_summary.json")
    checks = {
        "frames": len(frame_results),
        "passed_frames": len(passed),
        "failed_frames": len(failed),
        "missing_frames": sum(1 for item in frame_results if item.get("missing")),
        "max_selected_abs_diff": max((item.get("selected_max_abs_diff", 999) for item in frame_results), default=999),
        "max_selected_mean_abs_diff": max((item.get("selected_mean_abs_diff", 999.0) for item in frame_results), default=999.0),
        "max_imported_abs_diff": max((item.get("imported_max_abs_diff", 999) for item in frame_results), default=999),
        "max_imported_mean_abs_diff": max((item.get("imported_mean_abs_diff", 999.0) for item in frame_results), default=999.0),
        "max_selected_mismatched_coverage": max((item.get("selected_mismatched_coverage", 1.0) for item in frame_results), default=1.0),
        "max_imported_mismatched_coverage": max((item.get("imported_mismatched_coverage", 1.0) for item in frame_results), default=1.0),
        "output_bytes": sum(os.path.getsize(path) for path in output_paths if path and os.path.isfile(path)),
        "gif_bytes": os.path.getsize(gif_path) if os.path.isfile(gif_path) else 0,
        "strip_gif_bytes": os.path.getsize(strip_gif_path) if os.path.isfile(strip_gif_path) else 0,
    }
    status = "passed" if (
        checks["frames"] > 0
        and checks["passed_frames"] == checks["frames"]
        and checks["failed_frames"] == 0
        and checks["max_selected_abs_diff"] == 0
        and checks["max_selected_mean_abs_diff"] == 0.0
        and checks["max_imported_abs_diff"] == 0
        and checks["max_imported_mean_abs_diff"] == 0.0
    ) else "failed"
    summary = {
        "schema": SUMMARY_SCHEMA,
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
            "preview_gain": args.preview_gain,
            "stage": STAGE,
        },
        "checks": checks,
        "frames": frame_results,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        metadata_entry(summary_path, assets_dir, "response_aov_scene_job_dry_run_summary.json", "Dry Run Summary", root),
        copy_asset(job_path, assets_dir, "response_aov_scene_job_manifest.json", "Response AOV Scene Job Manifest", root),
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
    write_text(index_path, html_page(summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_aov_scene_job_dry_run_gallery",
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
        "status={status} frames={frames} passed={passed} selected_max={selected} imported_max={imported} summary={summary}".format(
            status=status,
            frames=checks["frames"],
            passed=checks["passed_frames"],
            selected=checks["max_selected_abs_diff"],
            imported=checks["max_imported_abs_diff"],
            summary=summary_path,
        )
    )
    if status != "passed" and args.fail_on_review:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_manifest", help="S621 response-AOV scene job manifest")
    parser.add_argument("out_dir", help="Output directory for dry-run report/gallery assets")
    parser.add_argument("--summary", help="Output dry-run summary JSON")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--preview-gain", type=float, default=4.0)
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Job Dry Run")
    parser.add_argument(
        "--next",
        default="Replace this dry-run compositor with the external renderer/cache backend while preserving descriptor IO and gate checks.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.preview_gain <= 0.0:
        parser.error("preview-gain must be positive")
    run_job(args)


if __name__ == "__main__":
    main()
