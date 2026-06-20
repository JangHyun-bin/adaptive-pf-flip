#!/usr/bin/env python
"""Fit renderer-control specs from visual-cache response intent regions."""

import argparse
import csv
import math
import os
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
from validate_mitsuba_visual_cache_bundle import resolve_path


CONTROL_KIND = {
    "surface_highlight_response": {
        "control_type": "localized_light_or_glint",
        "renderer_native_hint": "surface glint texture or small area light fitted to water surface",
        "priority": "high",
    },
    "crest_band_response": {
        "control_type": "anisotropic_surface_texture",
        "renderer_native_hint": "thin water-surface roughness or emission texture band",
        "priority": "medium",
    },
    "water_body_response": {
        "control_type": "volume_or_material_response",
        "renderer_native_hint": "water material/volume response texture carried by projected mask",
        "priority": "medium",
    },
}


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to fit response controls")


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        with open(src, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def fit_strength(component, args):
    control = component.get("suggested_control") or {}
    hint = float(control.get("strength_hint") or 0.0)
    response = float(component.get("mean_response_luma") or 0.0) / 255.0
    peak = float(component.get("max_response_luma") or 0.0) / 255.0
    value = max(hint, response * args.mean_gain, peak * args.peak_gain)
    return max(args.min_strength, min(args.max_strength, value))


def component_radius(component):
    x0, y0, x1, y1 = component.get("bbox") or [0, 0, 0, 0]
    return max(1.0, math.sqrt(max(1, (x1 - x0 + 1) * (y1 - y0 + 1))) * 0.5)


def fit_control(frame, component, args):
    kind = component.get("kind") or "unknown"
    meta = CONTROL_KIND.get(kind, {
        "control_type": "generic_response_texture",
        "renderer_native_hint": "generic projected response texture",
        "priority": "low",
    })
    strength = fit_strength(component, args)
    radius = component_radius(component)
    control_type = meta["control_type"]
    if control_type == "localized_light_or_glint":
        response_payload = {
            "emission_scale": round(strength * args.light_scale, 6),
            "roughness_delta": round(-0.15 * strength, 6),
            "glint_radius_px": round(radius * args.radius_scale, 3),
        }
    elif control_type == "volume_or_material_response":
        response_payload = {
            "scattering_scale": round(strength * args.volume_scale, 6),
            "albedo_lift": round(strength * args.material_scale, 6),
            "mask_blur_px": round(max(2.0, radius * 0.12), 3),
        }
    else:
        response_payload = {
            "texture_strength": round(strength * args.material_scale, 6),
            "mask_blur_px": round(max(1.0, radius * 0.08), 3),
        }
    return {
        "control_id": f"s476_f{int(frame.get('frame') or 0):04d}_c{int(component.get('rank') or 0):02d}",
        "frame": frame.get("frame"),
        "output_frame": frame.get("output_frame"),
        "rank": component.get("rank"),
        "source_kind": kind,
        "control_type": control_type,
        "priority": meta["priority"],
        "renderer_native_hint": meta["renderer_native_hint"],
        "bbox": component.get("bbox"),
        "bbox_normalized": component.get("bbox_normalized"),
        "centroid": component.get("centroid"),
        "centroid_normalized": component.get("centroid_normalized"),
        "pixels": component.get("pixels"),
        "coverage": component.get("coverage"),
        "mean_response_luma": component.get("mean_response_luma"),
        "max_response_luma": component.get("max_response_luma"),
        "mean_target_gap_luma": component.get("mean_target_gap_luma"),
        "fit_strength": round(strength, 6),
        "response": response_payload,
        "native_gate": {
            "must_compare_against": "S473 AOV import target-gap",
            "max_pixel_import_diff_required": 0,
            "target_gap_max_mad_ceiling": 23.950307355967077,
        },
    }


def draw_control_overlay(source_path, controls, out_path):
    base = Image.open(source_path).convert("RGB")
    draw = ImageDraw.Draw(base)
    colors = {
        "localized_light_or_glint": (255, 230, 80),
        "anisotropic_surface_texture": (120, 230, 255),
        "volume_or_material_response": (255, 110, 150),
        "generic_response_texture": (230, 230, 230),
    }
    for control in controls:
        color = colors.get(control.get("control_type"), (230, 230, 230))
        x0, y0, x1, y1 = control.get("bbox") or [0, 0, 0, 0]
        draw.rectangle((x0, y0, x1, y1), outline=color, width=2)
        label = f"{control.get('control_id')} {control.get('control_type')} {control.get('fit_strength')}"
        draw.text((x0 + 4, max(0, y0 - 14)), label, fill=color)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base.save(out_path)
    return out_path


def write_csv_file(path, controls):
    fields = [
        "control_id",
        "frame",
        "output_frame",
        "rank",
        "source_kind",
        "control_type",
        "priority",
        "fit_strength",
        "pixels",
        "coverage",
        "mean_response_luma",
        "max_response_luma",
        "mean_target_gap_luma",
        "bbox",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for control in controls:
            row = dict(control)
            row["bbox"] = " ".join(str(item) for item in (control.get("bbox") or []))
            writer.writerow({field: row.get(field) for field in fields})


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Control GIF"), None)
    overlays = [item for item in assets if item["label"].startswith("Control Overlay")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Controls", checks.get("controls")),
            ("Frames", checks.get("frames_with_controls")),
            ("Light", checks.get("localized_light_or_glint_controls")),
            ("Material", checks.get("volume_or_material_response_controls")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Control GIF"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in overlays
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #eaf5fb; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 26px; font-weight: 650; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 18px; }}
    .hero {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; margin-bottom: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 6px; background: #0d1820; overflow: hidden; }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <header><h1>{title}</h1><nav>{links}</nav></header>
  <section class="tiles">{tiles}</section>
  {hero}
  <section class="grid">{figures}</section>
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
        f"CSV: `{summary.get('csv_repo_path')}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Controls: `{checks.get('controls')}`",
        f"- Frames with controls: `{checks.get('frames_with_controls')}`",
        f"- Localized light/glint controls: `{checks.get('localized_light_or_glint_controls')}`",
        f"- Volume/material controls: `{checks.get('volume_or_material_response_controls')}`",
        f"- Max fit strength: `{checks.get('max_fit_strength')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Top Controls",
        "",
        "| Control | Frame | Output | Type | Strength | Pixels | BBox | Native Hint |",
        "| --- | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for control in (summary.get("controls") or [])[:16]:
        lines.append(
            f"| `{control.get('control_id')}` | {control.get('frame')} | {control.get('output_frame')} | "
            f"`{control.get('control_type')}` | {control.get('fit_strength')} | {control.get('pixels')} | "
            f"`{control.get('bbox')}` | {control.get('renderer_native_hint')} |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def fit(args):
    require_pillow()
    root = os.getcwd()
    intent_path = require_file(args.response_intent, "response intent summary")
    intent = read_json(intent_path)
    if intent.get("schema") != "lsfs_mitsuba_visual_cache_response_intent":
        raise SystemExit(f"{args.response_intent}: expected lsfs_mitsuba_visual_cache_response_intent schema")

    out_dir = os.path.abspath(args.out_dir)
    overlay_dir = os.path.join(out_dir, "overlays")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(overlay_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    controls = []
    frame_records = []
    overlay_paths = []
    for frame in intent.get("frames") or []:
        frame_controls = [fit_control(frame, component, args) for component in frame.get("components") or []]
        frame_controls = [control for control in frame_controls if control["pixels"] >= args.min_pixels]
        frame_controls.sort(key=lambda item: (item["priority"] != "high", -item["fit_strength"], -item["pixels"]))
        if args.max_controls_per_frame > 0:
            frame_controls = frame_controls[:args.max_controls_per_frame]
        controls.extend(frame_controls)
        overlay_source = resolve_path(frame.get("overlay_repo_path"), root)
        overlay_path = None
        if overlay_source and os.path.isfile(overlay_source):
            overlay_path = os.path.join(overlay_dir, f"frame_{int(frame.get('frame') or 0):04d}_response_controls.png")
            draw_control_overlay(overlay_source, frame_controls, overlay_path)
            overlay_paths.append(overlay_path)
        frame_records.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "control_count": len(frame_controls),
            "overlay_repo_path": posix_rel(overlay_path, root) if overlay_path else None,
            "controls": [control["control_id"] for control in frame_controls],
        })
    controls.sort(key=lambda item: (item["priority"] != "high", -item["fit_strength"], -item["pixels"]))
    csv_path = os.path.abspath(args.csv or os.path.join(out_dir, "response_controls.csv"))
    write_csv_file(csv_path, controls)
    gif_path = os.path.join(out_dir, "response_controls.gif")
    if overlay_paths:
        images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in overlay_paths]
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=int(1000 / args.fps), loop=0)
    else:
        raise SystemExit("no overlays were built for response controls")

    key_indices = sorted(set([0, len(overlay_paths) // 2, len(overlay_paths) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "response_controls.gif", "Control GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(overlay_paths[frame_index], assets_dir, f"control_overlay_{out_index:02d}.png", f"Control Overlay {out_index + 1}", root))
    metadata_files = [
        copy_asset(intent_path, assets_dir, "response_intent_summary.json", "Response intent", root),
        copy_asset(csv_path, assets_dir, "response_controls.csv", "Response control CSV", root),
    ]
    checks = {
        "controls": len(controls),
        "frames_with_controls": sum(1 for frame in frame_records if frame.get("control_count", 0) > 0),
        "localized_light_or_glint_controls": sum(1 for control in controls if control.get("control_type") == "localized_light_or_glint"),
        "volume_or_material_response_controls": sum(1 for control in controls if control.get("control_type") == "volume_or_material_response"),
        "anisotropic_surface_texture_controls": sum(1 for control in controls if control.get("control_type") == "anisotropic_surface_texture"),
        "max_fit_strength": max((control.get("fit_strength", 0.0) for control in controls), default=0.0),
        "gif_bytes": os.path.getsize(gif_path),
    }
    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_response_control_spec",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if controls else "empty",
        "response_intent": {
            "path": intent_path,
            "repo_path": posix_rel(intent_path, root),
            "sha256": sha256_file(intent_path),
            "schema": intent.get("schema"),
            "status": intent.get("status"),
        },
        "fit_settings": {
            "min_pixels": args.min_pixels,
            "max_controls_per_frame": args.max_controls_per_frame,
            "mean_gain": args.mean_gain,
            "peak_gain": args.peak_gain,
            "min_strength": args.min_strength,
            "max_strength": args.max_strength,
            "light_scale": args.light_scale,
            "material_scale": args.material_scale,
            "volume_scale": args.volume_scale,
        },
        "checks": checks,
        "csv_path": csv_path,
        "csv_repo_path": posix_rel(csv_path, root),
        "frames": frame_records,
        "controls": controls,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "response_control_spec.json", "Response control spec", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_control_spec_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={summary['status']} controls={len(controls)} "
        f"light={checks['localized_light_or_glint_controls']} material={checks['volume_or_material_response_controls']} "
        f"summary={summary_path}"
    )
    if summary["status"] != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fit Mitsuba response controls from visual-cache intent")
    parser.add_argument("response_intent")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--csv")
    parser.add_argument("--report")
    parser.add_argument("--min-pixels", type=int, default=32)
    parser.add_argument("--max-controls-per-frame", type=int, default=8)
    parser.add_argument("--mean-gain", type=float, default=1.5)
    parser.add_argument("--peak-gain", type=float, default=1.0)
    parser.add_argument("--min-strength", type=float, default=0.01)
    parser.add_argument("--max-strength", type=float, default=0.35)
    parser.add_argument("--light-scale", type=float, default=1.0)
    parser.add_argument("--material-scale", type=float, default=0.75)
    parser.add_argument("--volume-scale", type=float, default=0.55)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--title", default="Mitsuba Visual Cache Response Controls")
    parser.add_argument(
        "--next",
        default="Use this response-control spec to drive a renderer-native material/light/volume candidate and compare it against the S473 AOV import gate.",
    )
    args = parser.parse_args(argv)
    if args.min_pixels <= 0:
        parser.error("min-pixels must be positive")
    if args.max_controls_per_frame < 0:
        parser.error("max-controls-per-frame must be non-negative")
    for name in ("mean_gain", "peak_gain", "light_scale", "material_scale", "volume_scale", "radius_scale", "fps"):
        if getattr(args, name) <= 0.0:
            parser.error(f"{name.replace('_', '-')} must be positive")
    if args.min_strength < 0.0 or args.max_strength <= 0.0 or args.min_strength > args.max_strength:
        parser.error("strength bounds must be valid")
    fit(args)


if __name__ == "__main__":
    main()
