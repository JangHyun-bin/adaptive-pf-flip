#!/usr/bin/env python
"""Generate scene-aware native-style probes from response-AOV backend output."""

import argparse
import os
from datetime import datetime, timezone

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


BACKEND_SCHEMA = "lsfs_mitsuba_response_aov_scene_backend_adapter"
SUMMARY_SCHEMA = "lsfs_mitsuba_response_aov_scene_native_probe"


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to run response-AOV scene native probes")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def clamp_byte(value):
    return max(0, min(255, int(round(value))))


def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def finite(value):
    return isinstance(value, (int, float))


def metric_bounds(values):
    finite_values = [float(v) for v in values if finite(v)]
    if not finite_values:
        return (0.0, 1.0)
    lo = min(finite_values)
    hi = max(finite_values)
    if hi <= lo:
        hi = lo + 1.0
    return (lo, hi)


def normalized(value, bounds):
    if not finite(value):
        return 0.0
    lo, hi = bounds
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (float(value) - lo) / (hi - lo)))


def parse_strengths(text):
    strengths = []
    for item in str(text).split(","):
        item = item.strip()
        if not item:
            continue
        value = float(item)
        if value <= 0.0 or value > 1.0:
            raise argparse.ArgumentTypeError("strengths must be in (0, 1.0]")
        strengths.append(value)
    if not strengths:
        raise argparse.ArgumentTypeError("at least one strength is required")
    return strengths


def file_path(ref, root):
    if not isinstance(ref, dict):
        return None
    return resolve_path(ref.get("path") or ref.get("repo_path"), root)


def response_mask(positive, negative):
    pos = positive.convert("RGB").tobytes()
    neg = negative.convert("RGB").tobytes()
    mask = bytearray(len(pos) // 3)
    for pixel, index in enumerate(range(0, len(pos), 3)):
        mask[pixel] = max(
            pos[index],
            pos[index + 1],
            pos[index + 2],
            neg[index],
            neg[index + 1],
            neg[index + 2],
        )
    return (
        Image.frombytes("L", positive.size, bytes(mask))
        .filter(ImageFilter.MaxFilter(size=9))
        .filter(ImageFilter.GaussianBlur(radius=4.0))
    )


def max_channel_image(image):
    data = image.convert("RGB").tobytes()
    out = bytearray(len(data) // 3)
    for pixel, index in enumerate(range(0, len(data), 3)):
        out[pixel] = max(data[index], data[index + 1], data[index + 2])
    return (
        Image.frombytes("L", image.size, bytes(out))
        .filter(ImageFilter.MaxFilter(size=5))
        .filter(ImageFilter.GaussianBlur(radius=2.0))
    )


def apply_probe(base, positive, negative, strength, depth_factor, secondary_factor):
    mask = response_mask(positive, negative)
    positive_mask = max_channel_image(positive)
    base_bytes = base.convert("RGB").tobytes()
    mask_bytes = mask.tobytes()
    pos_bytes = positive_mask.tobytes()
    out = bytearray(len(base_bytes))
    max_delta = 0
    total_delta = 0
    changed = 0
    depth_gain = 0.45 + 0.45 * depth_factor + 0.10 * secondary_factor
    sparkle_gain = 0.20 + 0.80 * secondary_factor
    for pixel, idx in enumerate(range(0, len(base_bytes), 3)):
        r = base_bytes[idx]
        g = base_bytes[idx + 1]
        b = base_bytes[idx + 2]
        lum = luma(r, g, b) / 255.0
        mask_weight = (mask_bytes[pixel] / 255.0) ** 0.68
        shadow_weight = 0.40 + 0.60 * (1.0 - lum)
        volume = strength * depth_gain * mask_weight * shadow_weight
        sparkle = strength * sparkle_gain * ((pos_bytes[pixel] / 255.0) ** 1.45)
        nr = clamp_byte(r * (1.0 - 0.10 * volume) + 4.0 * sparkle)
        ng = clamp_byte(g * (1.0 - 0.04 * volume) + 6.0 * volume + 7.0 * sparkle)
        nb = clamp_byte(b * (1.0 + 0.09 * volume) + 16.0 * volume + 10.0 * sparkle)
        out[idx] = nr
        out[idx + 1] = ng
        out[idx + 2] = nb
        delta = max(abs(nr - r), abs(ng - g), abs(nb - b))
        if delta:
            changed += 1
        max_delta = max(max_delta, delta)
        total_delta += abs(nr - r) + abs(ng - g) + abs(nb - b)
    pixels = max(1, len(mask_bytes))
    return Image.frombytes("RGB", base.size, bytes(out)), {
        "max_abs_delta": max_delta,
        "mean_abs_delta": total_delta / float(max(1, len(base_bytes))),
        "changed_coverage": changed / float(pixels),
        "depth_factor": depth_factor,
        "secondary_factor": secondary_factor,
    }


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


def image_asset(path, root, label=None):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if label:
        entry["label"] = label
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def copy_asset(src, assets_dir, name, label, root):
    source = require_file(resolve_path(src, root), label)
    dest = os.path.join(assets_dir, name)
    ensure_dir(os.path.dirname(dest))
    if os.path.abspath(source) != os.path.abspath(dest):
        with open(source, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
    entry = image_asset(dest, root, label)
    entry["href"] = f"assets/{name}"
    entry["source_repo_path"] = posix_rel(source, root)
    return entry


def load_backend_summary(path, root):
    resolved = require_file(resolve_path(path, root), "response-AOV scene backend summary")
    summary = read_json(resolved)
    if summary.get("schema") != BACKEND_SCHEMA:
        raise SystemExit(f"{path}: expected {BACKEND_SCHEMA} schema")
    if summary.get("status") != "passed":
        raise SystemExit(f"{path}: backend summary status is {summary.get('status')!r}")
    return resolved, summary


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
        secondary_total = ((render_data.get("secondary_counts") or {}).get("total") or 0)
        frames.append({
            "frame": frame.get("frame"),
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
            "secondary_total": secondary_total,
            "visual_gate": descriptor.get("visual_gate") or {},
        })
    return frames, missing


def render_candidate(frames, missing, strength, out_dir, root, fps, keyframes):
    label = f"strength_{str(strength).replace('.', '_')}"
    candidate_dir = os.path.join(out_dir, label)
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
        if any(image.size != base.size for image in (positive, negative, selected)):
            raise SystemExit(f"frame {item['frame']}: image dimensions differ")
        depth_factor = 0.5 * normalized(item.get("water_depth_y_span"), y_bounds) + 0.5 * normalized(item.get("water_depth_z_span"), z_bounds)
        secondary_factor = normalized(item.get("secondary_total"), secondary_bounds)
        probe, delta_stats = apply_probe(base, positive, negative, strength, depth_factor, secondary_factor)
        selected_stats = diff_stats(probe, selected)
        frame_path = os.path.join(frames_dir, f"frame_{int(item['frame']):04d}.png")
        strip_path = os.path.join(strips_dir, f"frame_{int(item['frame']):04d}_{label}.png")
        probe.save(frame_path)
        mask = response_mask(positive, negative)
        mask_visual = ImageOps.colorize(mask, black=(7, 12, 18), white=(120, 220, 255))
        labeled_strip(
            [base, mask_visual, probe, selected, diff_visual(probe, selected)],
            ["S623 backend", "response mask", "native probe", "selected", "selected diff"],
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
            "strength": strength,
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
        "label": label,
        "strength": strength,
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


def candidate_score(candidate):
    checks = candidate.get("checks") or {}
    return (
        float(checks.get("max_mean_abs_delta_from_s623") or 0.0),
        float(checks.get("max_changed_coverage_from_s623") or 0.0),
        float(checks.get("max_abs_delta_from_s623") or 0.0),
    )


def select_candidate(candidates, max_abs_tolerance, mean_abs_tolerance):
    feasible = [
        candidate for candidate in candidates
        if (candidate.get("checks") or {}).get("max_abs_delta_from_s623", 999) <= max_abs_tolerance
        and (candidate.get("checks") or {}).get("max_mean_abs_delta_from_s623", 999.0) <= mean_abs_tolerance
        and (candidate.get("checks") or {}).get("missing_references", 1) == 0
    ]
    if not feasible:
        return None
    return max(feasible, key=candidate_score)


def html_page(summary):
    selected = summary.get("selected_candidate") or {}
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    hero = next((item for item in assets if item.get("label") == "Selected Native Probe GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Selected Native Probe Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Candidates", checks.get("candidates")),
            ("Selected", selected.get("label")),
            ("S623 Max Delta", (selected.get("checks") or {}).get("max_abs_delta_from_s623")),
            ("S623 Mean Delta", f"{(selected.get('checks') or {}).get('max_mean_abs_delta_from_s623', 0.0):.4f}"),
            ("Selected Max", (selected.get("checks") or {}).get("max_selected_abs_diff")),
        )
    )
    hero_html = f'<section class="hero"><img src="{hero["href"]}" alt="selected native probe GIF"></section>' if hero else ""
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
  <p>Scene-aware native-style probe driven by response AOV masks, water depth, and secondary particle density.</p>
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
        "| Candidate | Max S623 Delta | Max S623 MAD | Mean S623 MAD | Max Selected Delta | Max Selected MAD |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in summary.get("candidates") or []:
        checks = candidate.get("checks") or {}
        lines.append(
            f"| `{candidate.get('label')}` | {checks.get('max_abs_delta_from_s623')} | "
            f"{checks.get('max_mean_abs_delta_from_s623')} | {checks.get('mean_mean_abs_delta_from_s623')} | "
            f"{checks.get('max_selected_abs_diff')} | {checks.get('max_selected_mean_abs_diff')} |"
        )
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Scene | Source | Depth | Secondary | S623 Delta | Selected Delta | Output |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    frames = selected.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('scene_frame')} | {frame.get('source_frame')} | "
            f"{frame.get('depth_factor'):.4f} | {frame.get('secondary_factor'):.4f} | "
            f"{frame.get('max_abs_delta_from_s623')} | {frame.get('selected_max_abs_diff')} | "
            f"`{frame.get('preview_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    backend_path, backend_summary = load_backend_summary(args.backend_summary, root)
    out_dir = os.path.abspath(args.out_dir)
    ensure_dir(out_dir)
    frames, missing = load_frame_inputs(backend_summary, root)
    candidates = [
        render_candidate(frames, missing, strength, out_dir, root, args.fps, args.keyframes)
        for strength in args.strengths
    ]
    selected = select_candidate(candidates, args.max_abs_tolerance, args.mean_abs_tolerance)
    status = "ready" if selected and frames and not missing else "review"
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = ensure_dir(os.path.join(gallery_dir, "assets"))
    assets = []
    if selected:
        assets.append(copy_asset(
            resolve_path(selected.get("gif_repo_path"), root),
            assets_dir,
            "selected_native_probe.gif",
            "Selected Native Probe GIF",
            root,
        ))
        for index, strip_path in enumerate(selected.get("sample_strip_paths") or []):
            assets.append(copy_asset(
                strip_path,
                assets_dir,
                f"selected_native_probe_strip_{index:02d}.png",
                f"Selected Native Probe Strip {index + 1}",
                root,
            ))
    summary_path = os.path.abspath(args.summary) if args.summary else os.path.join(out_dir, "response_aov_scene_native_probe_summary.json")
    index_path = os.path.join(gallery_dir, "index.html")
    checks = {
        "candidates": len(candidates),
        "frames": len(frames),
        "missing_references": len(missing),
        "selected_label": selected.get("label") if selected else None,
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
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
            "strengths": args.strengths,
            "fps": args.fps,
            "keyframes": args.keyframes,
            "max_abs_tolerance": args.max_abs_tolerance,
            "mean_abs_tolerance": args.mean_abs_tolerance,
        },
        "checks": checks,
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
    parser.add_argument("out_dir", help="Output directory for native-style probes")
    parser.add_argument("--summary", help="Output summary JSON")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--strengths", type=parse_strengths, default=parse_strengths("0.45"))
    parser.add_argument("--max-abs-tolerance", type=int, default=24)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.85)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Response AOV Scene Native Probe")
    parser.add_argument(
        "--next",
        default="Review the selected native-style probe visually, then either promote it or run a narrower parameter sweep.",
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
