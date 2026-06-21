#!/usr/bin/env python
"""Run a narrow vectorized sweep around the S624 scene-aware native probe."""

import argparse
import os
from datetime import datetime, timezone

try:
    import numpy as np
except ImportError:  # pragma: no cover - reported at runtime.
    np = None

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageFilter = None
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
from build_mitsuba_low_frequency_parity_texture_package import diff_stats, write_gif
from run_mitsuba_response_aov_scene_native_probe import (
    BACKEND_SCHEMA,
    file_path,
    load_backend_summary,
    metric_bounds,
    normalized,
    resolve_path,
)


SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_probe_sweep"


def require_runtime():
    if Image is None:
        raise SystemExit("Pillow is required to run native probe sweeps")
    if np is None:
        raise SystemExit("NumPy is required to run native probe sweeps")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


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
        parse_candidate("S624_REF=0.45,9,4.0,0.68,1.00,1.00"),
        parse_candidate("SOFT_WIDE=0.58,13,6.0,0.60,0.95,0.80"),
        parse_candidate("DEEP_BAL=0.66,11,4.5,0.62,1.10,0.90"),
        parse_candidate("HILITE=0.52,9,3.5,0.58,0.82,1.55"),
        parse_candidate("BOLD_SAFE=0.74,15,6.5,0.62,1.02,0.85"),
    ]


def copy_asset(src, assets_dir, name, label, root):
    source = require_file(resolve_path(src, root), label)
    dest = os.path.join(assets_dir, name)
    ensure_dir(os.path.dirname(dest))
    if os.path.abspath(source) != os.path.abspath(dest):
        with open(source, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
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


def luma_array(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def max_mask(image, mask_size, blur):
    mask = image.convert("L")
    if mask_size > 1:
        mask = mask.filter(ImageFilter.MaxFilter(size=mask_size))
    if blur > 0.0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur))
    return np.asarray(mask, dtype=np.float32) / 255.0


def response_masks(positive, negative, candidate):
    pos_arr = np.asarray(positive.convert("RGB"), dtype=np.uint8)
    neg_arr = np.asarray(negative.convert("RGB"), dtype=np.uint8)
    response_raw = np.maximum(pos_arr.max(axis=2), neg_arr.max(axis=2)).astype(np.uint8)
    positive_raw = pos_arr.max(axis=2).astype(np.uint8)
    response = max_mask(Image.fromarray(response_raw, mode="L"), candidate["mask_size"], candidate["mask_blur"])
    positive_mask = max_mask(Image.fromarray(positive_raw, mode="L"), 5, 2.0)
    return response, positive_mask


def apply_candidate(base, positive, negative, candidate, depth_factor, secondary_factor):
    base_arr = np.asarray(base.convert("RGB"), dtype=np.float32)
    response, positive_mask = response_masks(positive, negative, candidate)
    lum = luma_array(base_arr) / 255.0
    mask_weight = np.power(response, candidate["mask_power"])
    shadow_weight = 0.40 + 0.60 * (1.0 - lum)
    depth_gain = 0.45 + 0.45 * depth_factor + 0.10 * secondary_factor
    sparkle_gain = 0.20 + 0.80 * secondary_factor
    volume = candidate["strength"] * candidate["volume_scale"] * depth_gain * mask_weight * shadow_weight
    sparkle = (
        candidate["strength"]
        * candidate["sparkle_scale"]
        * sparkle_gain
        * np.power(positive_mask, 1.45)
    )
    out = np.empty_like(base_arr)
    out[..., 0] = base_arr[..., 0] * (1.0 - 0.10 * volume) + 4.0 * sparkle
    out[..., 1] = base_arr[..., 1] * (1.0 - 0.04 * volume) + 6.0 * volume + 7.0 * sparkle
    out[..., 2] = base_arr[..., 2] * (1.0 + 0.09 * volume) + 16.0 * volume + 10.0 * sparkle
    out_u8 = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    delta = np.abs(out_u8.astype(np.int16) - base_arr.astype(np.int16))
    pixel_delta = delta.max(axis=2)
    return Image.fromarray(out_u8, mode="RGB"), {
        "max_abs_delta": int(pixel_delta.max(initial=0)),
        "mean_abs_delta": float(delta.mean()),
        "changed_coverage": float((pixel_delta > 0).mean()),
        "depth_factor": depth_factor,
        "secondary_factor": secondary_factor,
    }, Image.fromarray(np.clip(response * 255.0, 0, 255).astype(np.uint8), mode="L")


def diff_visual(a, b):
    return ImageOps.autocontrast(ImageChops.difference(a.convert("RGB"), b.convert("RGB")))


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


def load_frame_inputs(backend_summary, root):
    frames = []
    missing = []
    for frame in backend_summary.get("frames") or []:
        output_path = resolve_path(frame.get("output_image_repo_path"), root)
        descriptor_path = resolve_path(((frame.get("scene_descriptor") or {}).get("repo_path")), root)
        if not output_path or not os.path.isfile(output_path):
            missing.append({"frame": frame.get("frame"), "missing": "backend_output"})
            continue
        if not descriptor_path or not os.path.isfile(descriptor_path):
            missing.append({"frame": frame.get("frame"), "missing": "descriptor"})
            continue
        descriptor = read_json(descriptor_path)
        aovs = ((descriptor.get("inputs") or {}).get("aov_layers") or {})
        positive_path = file_path(aovs.get("response_positive_rgb"), root)
        negative_path = file_path(aovs.get("response_negative_rgb"), root)
        selected_path = file_path(aovs.get("selected_composite_rgb"), root)
        absent = [
            name for name, path in (
                ("response_positive_rgb", positive_path),
                ("response_negative_rgb", negative_path),
                ("selected_composite_rgb", selected_path),
            )
            if not path or not os.path.isfile(path)
        ]
        if absent:
            missing.append({"frame": frame.get("frame"), "missing": absent})
            continue
        render_data = descriptor.get("render_data") or {}
        frames.append({
            "frame": int(frame.get("frame") or 0),
            "output_frame": frame.get("output_frame"),
            "scene_frame": frame.get("scene_frame"),
            "source_frame": frame.get("source_frame"),
            "output_path": output_path,
            "descriptor_path": descriptor_path,
            "positive_path": positive_path,
            "negative_path": negative_path,
            "selected_path": selected_path,
            "water_depth_y_span": render_data.get("water_depth_y_span"),
            "water_depth_z_span": render_data.get("water_depth_z_span"),
            "secondary_total": ((render_data.get("secondary_counts") or {}).get("total") or 0),
            "visual_gate": descriptor.get("visual_gate") or {},
        })
    return frames, missing


def render_candidate(frames, missing, candidate, out_dir, root, fps, keyframes):
    label = candidate["label"]
    candidate_dir = ensure_dir(os.path.join(out_dir, label))
    frames_dir = ensure_dir(os.path.join(candidate_dir, "frames"))
    strips_dir = ensure_dir(os.path.join(candidate_dir, "strips"))
    y_bounds = metric_bounds([frame.get("water_depth_y_span") for frame in frames])
    z_bounds = metric_bounds([frame.get("water_depth_z_span") for frame in frames])
    secondary_bounds = metric_bounds([frame.get("secondary_total") for frame in frames])
    rows = []
    frame_paths = []
    strip_paths = []
    for item in frames:
        base = Image.open(item["output_path"]).convert("RGB")
        positive = Image.open(item["positive_path"]).convert("RGB")
        negative = Image.open(item["negative_path"]).convert("RGB")
        selected = Image.open(item["selected_path"]).convert("RGB")
        depth_factor = 0.5 * normalized(item.get("water_depth_y_span"), y_bounds) + 0.5 * normalized(item.get("water_depth_z_span"), z_bounds)
        secondary_factor = normalized(item.get("secondary_total"), secondary_bounds)
        probe, delta_stats, response = apply_candidate(base, positive, negative, candidate, depth_factor, secondary_factor)
        selected_stats = diff_stats(probe, selected)
        frame_path = os.path.join(frames_dir, f"frame_{item['frame']:04d}.png")
        strip_path = os.path.join(strips_dir, f"frame_{item['frame']:04d}_{label}.png")
        probe.save(frame_path)
        response_visual = ImageOps.colorize(response, black=(7, 12, 18), white=(120, 220, 255))
        labeled_strip(
            [base, response_visual, probe, selected, diff_visual(probe, selected)],
            ["S623 backend", "response mask", label, "selected", "selected diff"],
            strip_path,
        )
        frame_paths.append(frame_path)
        strip_paths.append(strip_path)
        rows.append({
            "frame": item["frame"],
            "output_frame": item["output_frame"],
            "scene_frame": item["scene_frame"],
            "source_frame": item["source_frame"],
            "preview_repo_path": posix_rel(frame_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "source_backend_repo_path": posix_rel(item["output_path"], root),
            "descriptor_repo_path": posix_rel(item["descriptor_path"], root),
            "depth_factor": depth_factor,
            "secondary_factor": secondary_factor,
            "max_abs_delta_from_s623": delta_stats["max_abs_delta"],
            "mean_abs_delta_from_s623": delta_stats["mean_abs_delta"],
            "changed_coverage_from_s623": delta_stats["changed_coverage"],
            "selected_mean_abs_diff": selected_stats["mean_abs_diff"],
            "selected_max_abs_diff": selected_stats["max_abs_diff"],
            "selected_mismatched_coverage": selected_stats["mismatched_coverage"],
            "sha256": sha256_file(frame_path),
            "size": os.path.getsize(frame_path),
            "visual_gate": item.get("visual_gate") or {},
        })
    gif_path = os.path.join(candidate_dir, "native_probe.gif")
    strip_gif_path = os.path.join(candidate_dir, "native_probe_strips.gif")
    write_gif(frame_paths, gif_path, fps)
    write_gif(strip_paths, strip_gif_path, fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, keyframes - 1))) for i in range(keyframes))) if strip_paths else []
    return {
        **candidate,
        "repo_path": posix_rel(candidate_dir, root),
        "gif_repo_path": posix_rel(gif_path, root),
        "strip_gif_repo_path": posix_rel(strip_gif_path, root),
        "frames": rows,
        "sample_strip_paths": [strip_paths[index] for index in key_indices],
        "checks": {
            "frames": len(rows),
            "missing_references": len(missing),
            "max_abs_delta_from_s623": max((row["max_abs_delta_from_s623"] for row in rows), default=999),
            "max_mean_abs_delta_from_s623": max((row["mean_abs_delta_from_s623"] for row in rows), default=999.0),
            "mean_mean_abs_delta_from_s623": sum((row["mean_abs_delta_from_s623"] for row in rows), 0.0) / float(max(1, len(rows))),
            "max_changed_coverage_from_s623": max((row["changed_coverage_from_s623"] for row in rows), default=1.0),
            "max_selected_abs_diff": max((row["selected_max_abs_diff"] for row in rows), default=999),
            "max_selected_mean_abs_diff": max((row["selected_mean_abs_diff"] for row in rows), default=999.0),
            "mean_selected_mean_abs_diff": sum((row["selected_mean_abs_diff"] for row in rows), 0.0) / float(max(1, len(rows))),
            "gif_bytes": os.path.getsize(gif_path),
            "strip_gif_bytes": os.path.getsize(strip_gif_path),
            "output_bytes": sum(row["size"] for row in rows),
        },
    }


def select_candidate(candidates, max_abs_tolerance, mean_abs_tolerance):
    feasible = [
        candidate for candidate in candidates
        if (candidate.get("checks") or {}).get("max_abs_delta_from_s623", 999) <= max_abs_tolerance
        and (candidate.get("checks") or {}).get("max_mean_abs_delta_from_s623", 999.0) <= mean_abs_tolerance
        and (candidate.get("checks") or {}).get("missing_references", 1) == 0
    ]
    if not feasible:
        return None
    return max(
        feasible,
        key=lambda candidate: (
            float((candidate.get("checks") or {}).get("mean_mean_abs_delta_from_s623") or 0.0),
            float((candidate.get("checks") or {}).get("max_changed_coverage_from_s623") or 0.0),
        ),
    )


def html_page(summary):
    selected = summary.get("selected_candidate") or {}
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    hero = next((item for item in assets if item.get("label") == "Selected Native Probe Sweep GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Selected Native Probe Sweep Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Candidates", checks.get("candidates")),
            ("Selected", selected.get("label")),
            ("S623 Max Delta", (selected.get("checks") or {}).get("max_abs_delta_from_s623")),
            ("S623 Mean", f"{(selected.get('checks') or {}).get('max_mean_abs_delta_from_s623', 0.0):.4f}"),
            ("Selected Max", (selected.get("checks") or {}).get("max_selected_abs_diff")),
        )
    )
    hero_html = f'<section class="hero"><img src="{hero["href"]}" alt="selected native probe sweep GIF"></section>' if hero else ""
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
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 27px; font-weight: 670; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; min-height: 58px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    strong {{ display: block; font-size: 15px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; margin: 0 0 12px; }}
    .hero img, figure img {{ width: 100%; display: block; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Narrow vectorized sweep around S624 using response masks, water-depth metadata, and secondary-density metadata.</p>
  <section class="tiles">{tiles}</section>
  {hero_html}
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
        f"Selected candidate: `{selected.get('label')}`",
        "",
        "## Selected Checks",
        "",
        f"- Frames: `{selected_checks.get('frames')}`",
        f"- Missing references: `{selected_checks.get('missing_references')}`",
        f"- Max abs delta from S623: `{selected_checks.get('max_abs_delta_from_s623')}`",
        f"- Max mean abs delta from S623: `{selected_checks.get('max_mean_abs_delta_from_s623')}`",
        f"- Mean mean abs delta from S623: `{selected_checks.get('mean_mean_abs_delta_from_s623')}`",
        f"- Max selected abs diff: `{selected_checks.get('max_selected_abs_diff')}`",
        f"- Max selected mean abs diff: `{selected_checks.get('max_selected_mean_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(selected_checks.get('gif_bytes', 0))}`",
        "",
        "## Candidate Sweep",
        "",
        "| Candidate | Strength | Mask | Blur | Power | Volume | Sparkle | Max S623 Delta | Max S623 MAD | Mean S623 MAD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in summary.get("candidates") or []:
        checks = candidate.get("checks") or {}
        lines.append(
            f"| `{candidate.get('label')}` | {candidate.get('strength')} | {candidate.get('mask_size')} | "
            f"{candidate.get('mask_blur')} | {candidate.get('mask_power')} | {candidate.get('volume_scale')} | "
            f"{candidate.get('sparkle_scale')} | {checks.get('max_abs_delta_from_s623')} | "
            f"{checks.get('max_mean_abs_delta_from_s623')} | {checks.get('mean_mean_abs_delta_from_s623')} |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    require_runtime()
    root = os.getcwd()
    backend_path, backend_summary = load_backend_summary(args.backend_summary, root)
    out_dir = os.path.abspath(args.out_dir)
    ensure_dir(out_dir)
    frames, missing = load_frame_inputs(backend_summary, root)
    candidates = [
        render_candidate(frames, missing, candidate, out_dir, root, args.fps, args.keyframes)
        for candidate in args.candidate
    ]
    selected = select_candidate(candidates, args.max_abs_tolerance, args.mean_abs_tolerance)
    status = "ready" if selected and frames and not missing else "review"
    gallery_dir = ensure_dir(os.path.join(out_dir, "gallery"))
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    assets = []
    if selected:
        assets.append(copy_asset(
            resolve_path(selected.get("gif_repo_path"), root),
            assets_dir,
            "selected_native_probe_sweep.gif",
            "Selected Native Probe Sweep GIF",
            root,
        ))
        for index, strip_path in enumerate(selected.get("sample_strip_paths") or []):
            assets.append(copy_asset(
                strip_path,
                assets_dir,
                f"selected_native_probe_sweep_strip_{index:02d}.png",
                f"Selected Native Probe Sweep Strip {index + 1}",
                root,
            ))
    summary_path = os.path.abspath(args.summary) if args.summary else os.path.join(out_dir, "response_aov_scene_native_probe_sweep_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": SUMMARY_SCHEMA,
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source_backend": {
            "repo_path": posix_rel(backend_path, root),
            "schema": backend_summary.get("schema"),
            "status": backend_summary.get("status"),
            "sha256": sha256_file(backend_path),
            "size": os.path.getsize(backend_path),
        },
        "settings": {
            "max_abs_tolerance": args.max_abs_tolerance,
            "mean_abs_tolerance": args.mean_abs_tolerance,
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
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        "status={status} candidates={candidates} selected={selected} frames={frames} missing={missing} summary={summary}".format(
            status=status,
            candidates=len(candidates),
            selected=(selected or {}).get("label"),
            frames=len(frames),
            missing=len(missing),
            summary=summary_path,
        )
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend_summary", help="S623 response-AOV scene backend adapter summary")
    parser.add_argument("out_dir", help="Output directory for the S626 sweep")
    parser.add_argument("--summary", help="Output summary JSON")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--candidate", action="append", type=parse_candidate, default=default_candidates())
    parser.add_argument("--max-abs-tolerance", type=int, default=10)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.75)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Native Probe Sweep")
    parser.add_argument(
        "--next",
        default="Review the selected sweep candidate, then promote it into the backend adapter or publish it for direct comparison.",
    )
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
