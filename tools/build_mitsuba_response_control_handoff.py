#!/usr/bin/env python
"""Package fitted Mitsuba response controls for renderer-native follow-up."""

import argparse
import os
from datetime import datetime, timezone

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


def source_entry(path, root, label, payload=None):
    resolved = require_file(path, label)
    entry = {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
    }
    if payload is not None:
        entry["schema"] = payload.get("schema")
        entry["status"] = payload.get("status")
    return entry


def clamp01(value):
    return max(0.0, min(1.0, float(value or 0.0)))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def controls_by_output(controls):
    grouped = {}
    for control in controls or []:
        grouped.setdefault(control.get("output_frame"), []).append(control)
    for values in grouped.values():
        values.sort(key=lambda item: (str(item.get("control_type")), int(item.get("rank") or 0), item.get("control_id") or ""))
    return grouped


def control_bbox_center(control):
    centroid = control.get("centroid")
    if centroid and len(centroid) >= 2:
        return [float(centroid[0]), float(centroid[1])]
    x0, y0, x1, y1 = control.get("bbox") or [0, 0, 0, 0]
    return [(float(x0) + float(x1)) * 0.5, (float(y0) + float(y1)) * 0.5]


def light_anchor(control, args):
    response = control.get("response") or {}
    fit_strength = clamp01(control.get("fit_strength"))
    emission = clamp01(response.get("emission_scale"))
    max_luma_scale = clamp01(float(control.get("max_response_luma") or 0.0) / 255.0)
    luma_scale = clamp01(max(max_luma_scale, emission * args.proxy_gain))
    weight = clamp01(max(fit_strength, emission))
    return {
        "pixel_count": int(control.get("pixels") or 0),
        "coverage": float(control.get("coverage") or 0.0),
        "centroid_px": control_bbox_center(control),
        "centroid_uv": control.get("centroid_normalized"),
        "bbox_px": control.get("bbox"),
        "bbox_uv": control.get("bbox_normalized"),
        "source_luma_mean": float(control.get("mean_response_luma") or 0.0),
        "source_luma_max": float(control.get("max_response_luma") or 0.0),
        "response_control_id": control.get("control_id"),
        "priority": control.get("priority"),
        "renderer_native_hint": control.get("renderer_native_hint"),
        "suggested_response": {
            "kind": "visual_cache_control_light_response",
            "weight": round(weight, 6),
            "luma_scale": round(luma_scale, 6),
            "emission_scale": response.get("emission_scale"),
            "roughness_delta": response.get("roughness_delta"),
            "glint_radius_px": response.get("glint_radius_px"),
            "proxy_setting": args.proxy_label,
        },
    }


def material_control(control, args, gap_checks):
    response = control.get("response") or {}
    return {
        "control_id": control.get("control_id"),
        "frame": control.get("frame"),
        "output_frame": control.get("output_frame"),
        "rank": control.get("rank"),
        "source_kind": control.get("source_kind"),
        "control_type": control.get("control_type"),
        "priority": control.get("priority"),
        "renderer_native_hint": control.get("renderer_native_hint"),
        "bbox_px": control.get("bbox"),
        "bbox_uv": control.get("bbox_normalized"),
        "centroid_px": control_bbox_center(control),
        "centroid_uv": control.get("centroid_normalized"),
        "pixel_count": int(control.get("pixels") or 0),
        "coverage": float(control.get("coverage") or 0.0),
        "fit_strength": float(control.get("fit_strength") or 0.0),
        "source_luma_mean": float(control.get("mean_response_luma") or 0.0),
        "source_luma_max": float(control.get("max_response_luma") or 0.0),
        "source_target_gap_luma_mean": control.get("mean_target_gap_luma"),
        "native_response": {
            "scattering_scale": response.get("scattering_scale"),
            "albedo_lift": response.get("albedo_lift"),
            "mask_blur_px": response.get("mask_blur_px"),
            "proxy_material_weight": args.proxy_material_weight,
            "proxy_falloff_power": args.proxy_falloff_power,
        },
        "native_gate": {
            "compare_against": args.proxy_label,
            "target_gap_mean_abs_diff": gap_checks.get("mean_gap_mean_abs_diff"),
            "target_gap_max_mean_abs_diff": gap_checks.get("max_gap_mean_abs_diff"),
            "target_gap_max_abs_diff": gap_checks.get("max_gap_max_abs_diff"),
            "must_not_exceed_proxy_max_mad": True,
        },
    }


def copy_asset(src, assets_dir, name, label, root):
    resolved = require_file(src, label)
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(resolved) != os.path.abspath(dest):
        with open(resolved, "rb") as f_in, open(dest, "wb") as f_out:
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


def maybe_copy_asset(src, assets_dir, name, label, root):
    if not src:
        return None
    resolved = resolve_path(src, root)
    if not resolved or not os.path.isfile(resolved):
        return None
    return copy_asset(resolved, assets_dir, name, label, root)


def make_gallery(out_dir, title, assets, root):
    gallery_dir = os.path.join(out_dir, "gallery")
    gallery_index = os.path.join(gallery_dir, "index.html")
    gallery = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": gallery_index,
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
    }
    write_text(gallery_index, html_page(title, assets))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_response_control_handoff_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "index_repo_path": gallery["index_repo_path"],
        "assets": assets,
    })
    return gallery


def html_page(title, assets):
    hero = next((item for item in assets if item["label"] == "Promoted Proxy GIF"), None)
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a>'
        f'<figcaption>{item["label"]}</figcaption></figure>'
        for item in assets
        if item is not hero
    )
    hero_html = f'<section class="hero"><img src="{hero["href"]}" alt="{hero["label"]}"></section>' if hero else ""
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
    .hero {{ border: 1px solid var(--line); border-radius: 6px; overflow: hidden; margin-bottom: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); overflow: hidden; }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{title}</h1>
    <nav>
      <a href="../response_control_handoff.json">handoff</a>
      <a href="../light_response_contract.json">light contract</a>
      <a href="../material_response_contract.json">material contract</a>
    </nav>
  </header>
  {hero_html}
  <section class="grid">{figures}</section>
</main>
</body>
</html>
"""


def frame_source_paths(output_frame, spec_frames, proxy_frames):
    spec_frame = spec_frames.get(output_frame) or {}
    proxy_frame = proxy_frames.get(output_frame) or {}
    return {
        "source_repo_path": proxy_frame.get("composite_repo_path") or spec_frame.get("overlay_repo_path"),
        "proxy_strip_repo_path": proxy_frame.get("strip_repo_path"),
        "control_overlay_repo_path": spec_frame.get("overlay_repo_path"),
    }


def build_contracts(args):
    root = os.getcwd()
    control_spec_path = require_file(args.control_spec, "response control spec")
    proxy_summary_path = require_file(args.proxy_summary, "promoted proxy summary")
    target_gap_path = require_file(args.target_gap_summary, "promoted target-gap summary")
    baseline_gap_path = require_file(args.baseline_gap_summary, "baseline target-gap summary") if args.baseline_gap_summary else None

    control_spec = read_json(control_spec_path)
    proxy_summary = read_json(proxy_summary_path)
    target_gap = read_json(target_gap_path)
    baseline_gap = read_json(baseline_gap_path) if baseline_gap_path else None

    if control_spec.get("schema") != "lsfs_mitsuba_response_control_spec":
        raise SystemExit(f"{args.control_spec}: expected lsfs_mitsuba_response_control_spec schema")
    if proxy_summary.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.proxy_summary}: expected lsfs_mitsuba_secondary_composite schema")
    if target_gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{args.target_gap_summary}: expected lsfs_mitsuba_renderer_target_gap schema")
    if baseline_gap and baseline_gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{args.baseline_gap_summary}: expected lsfs_mitsuba_renderer_target_gap schema")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    controls = control_spec.get("controls") or []
    light_controls = [control for control in controls if control.get("control_type") == "localized_light_or_glint"]
    material_controls = [control for control in controls if control.get("control_type") == "volume_or_material_response"]
    grouped_controls = controls_by_output(controls)
    spec_frames = output_frame_map(control_spec.get("frames") or [])
    proxy_frames = output_frame_map(proxy_summary.get("frames") or [])
    gap_checks = target_gap.get("checks") or {}
    baseline_checks = (baseline_gap or {}).get("checks") or {}

    light_frames = []
    material_frames = []
    material_entries = []
    total_light_coverage = 0.0
    max_light_coverage = 0.0
    total_material_coverage = 0.0
    max_material_coverage = 0.0

    for output_frame in sorted(grouped_controls):
        controls_for_frame = grouped_controls[output_frame]
        paths = frame_source_paths(output_frame, spec_frames, proxy_frames)
        frame_light_controls = [item for item in controls_for_frame if item in light_controls]
        frame_material_controls = [item for item in controls_for_frame if item in material_controls]
        if frame_light_controls:
            anchors = [light_anchor(control, args) for control in frame_light_controls]
            frame_coverage = sum(float(anchor.get("coverage") or 0.0) for anchor in anchors)
            total_light_coverage += frame_coverage
            max_light_coverage = max(max_light_coverage, frame_coverage)
            light_frames.append({
                "frame": frame_light_controls[0].get("frame"),
                "output_frame": output_frame,
                "source_repo_path": paths["source_repo_path"],
                "proxy_strip_repo_path": paths["proxy_strip_repo_path"],
                "control_overlay_repo_path": paths["control_overlay_repo_path"],
                "mask_coverage": frame_coverage,
                "anchors": anchors,
            })
        if frame_material_controls:
            frame_entries = [material_control(control, args, gap_checks) for control in frame_material_controls]
            frame_coverage = sum(float(entry.get("coverage") or 0.0) for entry in frame_entries)
            total_material_coverage += frame_coverage
            max_material_coverage = max(max_material_coverage, frame_coverage)
            material_entries.extend(frame_entries)
            material_frames.append({
                "frame": frame_material_controls[0].get("frame"),
                "output_frame": output_frame,
                "source_repo_path": paths["source_repo_path"],
                "proxy_strip_repo_path": paths["proxy_strip_repo_path"],
                "control_overlay_repo_path": paths["control_overlay_repo_path"],
                "coverage": frame_coverage,
                "controls": [entry.get("control_id") for entry in frame_entries],
            })

    assets_dir = os.path.join(out_dir, "gallery", "assets")
    assets = []
    control_gif = os.path.join(os.path.dirname(control_spec_path), "response_controls.gif")
    proxy_gif = os.path.join(os.path.dirname(proxy_summary_path), "response_control_proxy.gif")
    gap_gif = os.path.join(os.path.dirname(target_gap_path), "gallery", "assets", "shot.gif")
    gap_strip = os.path.join(os.path.dirname(target_gap_path), "gallery", "assets", "gap_strip_03.png")
    for entry in (
        maybe_copy_asset(proxy_gif, assets_dir, "promoted_proxy.gif", "Promoted Proxy GIF", root),
        maybe_copy_asset(control_gif, assets_dir, "response_controls.gif", "Response Control Overlay GIF", root),
        maybe_copy_asset(gap_gif, assets_dir, "promoted_proxy_target_gap.gif", "Promoted Proxy Target Gap GIF", root),
        maybe_copy_asset(gap_strip, assets_dir, "promoted_proxy_gap_strip_03.png", "Promoted Proxy Gap Strip", root),
    ):
        if entry:
            assets.append(entry)

    generated_utc = datetime.now(timezone.utc).isoformat()
    gallery = make_gallery(out_dir, args.title, assets, root)
    light_contract_path = os.path.join(out_dir, "light_response_contract.json")
    material_contract_path = os.path.join(out_dir, "material_response_contract.json")
    handoff_path = os.path.join(out_dir, "response_control_handoff.json")

    common_sources = {
        "response_control_spec": source_entry(control_spec_path, root, "response control spec", control_spec),
        "promoted_proxy_summary": source_entry(proxy_summary_path, root, "promoted proxy summary", proxy_summary),
        "promoted_target_gap_summary": source_entry(target_gap_path, root, "promoted target-gap summary", target_gap),
    }
    if baseline_gap_path:
        common_sources["baseline_target_gap_summary"] = source_entry(baseline_gap_path, root, "baseline target-gap summary", baseline_gap)

    light_status = "ready" if light_frames else "review"
    material_status = "ready" if material_entries else "review"
    status = "ready" if light_status == "ready" and material_status == "ready" and target_gap.get("status") == "ready" else "review"

    light_contract = {
        "schema": "lsfs_mitsuba_light_response_contract",
        "version": 2,
        "generated_utc": generated_utc,
        "title": f"{args.title} Light Contract",
        "status": light_status,
        "sources": common_sources,
        "mask_kind": "visual_cache_response_control_light",
        "settings": {
            "source_control_type": "localized_light_or_glint",
            "proxy_label": args.proxy_label,
            "proxy_gain": args.proxy_gain,
            "proxy_light_weight": args.proxy_light_weight,
        },
        "checks": {
            "frames": len(light_frames),
            "anchors": sum(len(frame.get("anchors") or []) for frame in light_frames),
            "max_anchors_per_frame": max((len(frame.get("anchors") or []) for frame in light_frames), default=0),
            "mean_mask_coverage": total_light_coverage / float(max(1, len(light_frames))),
            "max_mask_coverage": max_light_coverage,
        },
        "frames": light_frames,
        "gallery": gallery,
        "next": "Consume this with add_mitsuba_light_response_contract.py, then compare renderer-native output against the promoted proxy gap.",
    }

    material_contract = {
        "schema": "lsfs_mitsuba_material_response_contract",
        "version": 1,
        "generated_utc": generated_utc,
        "title": f"{args.title} Material Contract",
        "status": material_status,
        "sources": common_sources,
        "settings": {
            "source_control_type": "volume_or_material_response",
            "proxy_label": args.proxy_label,
            "proxy_gain": args.proxy_gain,
            "proxy_material_weight": args.proxy_material_weight,
            "proxy_falloff_power": args.proxy_falloff_power,
        },
        "checks": {
            "frames": len(material_frames),
            "controls": len(material_entries),
            "mean_coverage": total_material_coverage / float(max(1, len(material_frames))),
            "max_coverage": max_material_coverage,
        },
        "frames": material_frames,
        "controls": material_entries,
        "gallery": gallery,
        "next": "Use these projected material/volume controls to drive a renderer-native water material response pass.",
    }

    baseline_mean = baseline_checks.get("mean_gap_mean_abs_diff")
    baseline_max = baseline_checks.get("max_gap_mean_abs_diff")
    promoted_mean = gap_checks.get("mean_gap_mean_abs_diff")
    promoted_max = gap_checks.get("max_gap_mean_abs_diff")
    improvement = {}
    if baseline_mean is not None and promoted_mean is not None:
        improvement["mean_gap_mad_delta_vs_baseline"] = float(baseline_mean) - float(promoted_mean)
    if baseline_max is not None and promoted_max is not None:
        improvement["max_gap_mad_delta_vs_baseline"] = float(baseline_max) - float(promoted_max)

    handoff = {
        "schema": "lsfs_mitsuba_response_control_handoff",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "sources": common_sources,
        "promoted_proxy": {
            "label": args.proxy_label,
            "settings": {
                "gain": args.proxy_gain,
                "light_weight": args.proxy_light_weight,
                "material_weight": args.proxy_material_weight,
                "texture_weight": args.proxy_texture_weight,
                "falloff_power": args.proxy_falloff_power,
            },
            "target_gap_checks": gap_checks,
            "baseline_gap_checks": baseline_checks,
            "improvement": improvement,
        },
        "outputs": {
            "light_response_contract": {
                "repo_path": posix_rel(light_contract_path, root),
                "schema": light_contract["schema"],
                "status": light_contract["status"],
            },
            "material_response_contract": {
                "repo_path": posix_rel(material_contract_path, root),
                "schema": material_contract["schema"],
                "status": material_contract["status"],
            },
            "gallery": gallery,
        },
        "checks": {
            "controls": len(controls),
            "light_controls": len(light_controls),
            "material_controls": len(material_controls),
            "light_frames": len(light_frames),
            "material_frames": len(material_frames),
            "promoted_proxy_frames": (proxy_summary.get("checks") or {}).get("frames"),
            "promoted_proxy_controls_applied": (proxy_summary.get("checks") or {}).get("controls_applied"),
            "promoted_gap_mean_abs_diff": promoted_mean,
            "promoted_gap_max_mean_abs_diff": promoted_max,
            "promoted_gap_max_abs_diff": gap_checks.get("max_gap_max_abs_diff"),
            "baseline_gap_mean_abs_diff": baseline_mean,
            "baseline_gap_max_mean_abs_diff": baseline_max,
        },
        "renderer_next_steps": [
            "Feed light_response_contract.json into add_mitsuba_light_response_contract.py.",
            "Add a native water-material consumer for material_response_contract.json.",
            "Render the native candidate and compare against the promoted p4_soft_wide proxy target-gap.",
        ],
        "gallery": gallery,
        "next": args.next,
    }

    write_json(light_contract_path, light_contract)
    write_json(material_contract_path, material_contract)
    write_json(handoff_path, handoff)
    if args.report:
        write_text(args.report, markdown_report(handoff, handoff_path, light_contract_path, material_contract_path, root))

    print(
        f"status={status} controls={len(controls)} light={len(light_controls)} material={len(material_controls)} "
        f"promoted_max_gap={promoted_max} handoff={handoff_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def markdown_report(handoff, handoff_path, light_contract_path, material_contract_path, root):
    checks = handoff.get("checks") or {}
    promoted = handoff.get("promoted_proxy") or {}
    improvement = promoted.get("improvement") or {}
    outputs = handoff.get("outputs") or {}
    gallery = outputs.get("gallery") or {}
    lines = [
        f"# {handoff['title']}",
        "",
        f"Generated UTC: `{handoff['generated_utc']}`",
        f"Status: `{handoff['status']}`",
        f"Handoff JSON: `{posix_rel(handoff_path, root)}`",
        f"Light contract: `{posix_rel(light_contract_path, root)}`",
        f"Material contract: `{posix_rel(material_contract_path, root)}`",
        f"Gallery: `{gallery.get('index_repo_path')}`",
        "",
        "## Scope",
        "",
        "S479 packages the promoted S478 `p4_soft_wide` response-control proxy into renderer-facing contracts.",
        "The light contract is schema-compatible with the existing Mitsuba XML light consumer; the material contract carries the remaining water material/volume controls for the next native pass.",
        "",
        "## Checks",
        "",
        f"- Controls: `{checks.get('controls')}`",
        f"- Light controls: `{checks.get('light_controls')}`",
        f"- Material controls: `{checks.get('material_controls')}`",
        f"- Light frames: `{checks.get('light_frames')}`",
        f"- Material frames: `{checks.get('material_frames')}`",
        f"- Promoted proxy frames: `{checks.get('promoted_proxy_frames')}`",
        f"- Promoted proxy controls applied: `{checks.get('promoted_proxy_controls_applied')}`",
        f"- Promoted mean target-gap MAD: `{checks.get('promoted_gap_mean_abs_diff')}`",
        f"- Promoted max target-gap MAD: `{checks.get('promoted_gap_max_mean_abs_diff')}`",
        f"- Promoted max abs gap: `{checks.get('promoted_gap_max_abs_diff')}`",
        f"- Baseline mean target-gap MAD: `{checks.get('baseline_gap_mean_abs_diff')}`",
        f"- Baseline max target-gap MAD: `{checks.get('baseline_gap_max_mean_abs_diff')}`",
        f"- Mean MAD improvement vs baseline: `{improvement.get('mean_gap_mad_delta_vs_baseline')}`",
        f"- Max MAD improvement vs baseline: `{improvement.get('max_gap_mad_delta_vs_baseline')}`",
        "",
        "## Outputs",
        "",
        "| Artifact | Schema | Status | Path |",
        "| --- | --- | --- | --- |",
        f"| Handoff | `{handoff.get('schema')}` | `{handoff.get('status')}` | `{posix_rel(handoff_path, root)}` |",
        f"| Light contract | `{(outputs.get('light_response_contract') or {}).get('schema')}` | `{(outputs.get('light_response_contract') or {}).get('status')}` | `{posix_rel(light_contract_path, root)}` |",
        f"| Material contract | `{(outputs.get('material_response_contract') or {}).get('schema')}` | `{(outputs.get('material_response_contract') or {}).get('status')}` | `{posix_rel(material_contract_path, root)}` |",
        "",
        "## Gallery Assets",
        "",
    ]
    assets = gallery.get("assets") or []
    if assets:
        lines.extend([
            "| Asset | Size | Path |",
            "| --- | ---: | --- |",
        ])
        for asset in assets:
            lines.append(f"| {asset.get('label')} | {format_bytes(asset.get('size') or 0)} | `{asset.get('repo_path')}` |")
    else:
        lines.append("No gallery assets were copied.")
    lines.extend(["", "## Next", "", handoff.get("next", ""), ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Mitsuba response-control handoff package")
    parser.add_argument("control_spec")
    parser.add_argument("proxy_summary")
    parser.add_argument("target_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--baseline-gap-summary", default="build/shots/s473_mitsuba_visual_cache_aov_import_consumer_target_gap/renderer_target_gap_summary.json")
    parser.add_argument("--proxy-label", default="p4_soft_wide")
    parser.add_argument("--proxy-gain", type=float, default=1.05)
    parser.add_argument("--proxy-light-weight", type=float, default=1.0)
    parser.add_argument("--proxy-material-weight", type=float, default=0.85)
    parser.add_argument("--proxy-texture-weight", type=float, default=0.8)
    parser.add_argument("--proxy-falloff-power", type=float, default=1.0)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S479 Mitsuba Response Control Handoff")
    parser.add_argument("--next", default="Consume the light contract in the Mitsuba XML path, then add the material contract consumer and compare the native render against the promoted proxy gate.")
    args = parser.parse_args(argv)
    build_contracts(args)


if __name__ == "__main__":
    main()
