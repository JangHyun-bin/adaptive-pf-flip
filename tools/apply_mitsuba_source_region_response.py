#!/usr/bin/env python
"""Apply a target-free source-region response to Mitsuba composite frames."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from analyze_mitsuba_contact_particle_masks import particle_rows
from build_mitsuba_secondary_channel_aov_package import draw_channel_density
from apply_mitsuba_target_region_response import (
    clamp,
    composite_path,
    copy_asset,
    html_page,
    labeled_strip,
    layer_path,
    luminance_from_rgb,
    output_frame_map,
    resolve_path,
    write_gif,
)
from build_bridge_review_package import (
    image_dimensions,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to apply source-region response")


def lighten(value, strength, max_delta):
    delta = (255.0 - value) * strength
    if max_delta > 0.0:
        delta = min(max_delta, delta)
    return value + delta


def darken(value, strength, max_delta):
    delta = value * strength
    if max_delta > 0.0:
        delta = min(max_delta, delta)
    return value - delta


def dilated_ring_mask(mask, size, radius):
    if radius <= 0:
        return None
    filter_size = radius * 2 + 1
    mask_bytes = bytes(255 if value else 0 for value in mask)
    mask_img = Image.frombytes("L", size, mask_bytes)
    dilated = mask_img.filter(ImageFilter.MaxFilter(filter_size)).tobytes()
    return [value > 0 and not mask[index] for index, value in enumerate(dilated)]


def dilate_bool_mask(mask, size, radius):
    if radius <= 0:
        return mask
    filter_size = radius * 2 + 1
    mask_bytes = bytes(255 if value else 0 for value in mask)
    mask_img = Image.frombytes("L", size, mask_bytes)
    dilated = mask_img.filter(ImageFilter.MaxFilter(filter_size)).tobytes()
    return [value > 0 for value in dilated]


def export_frame_map(summary):
    return {
        int(frame.get("output_frame")): frame
        for frame in summary.get("frames") or []
        if frame.get("output_frame") is not None
    }


def particle_path(frame):
    return (frame.get("sidecar_assets") or {}).get("particles")


def xml_path(frame):
    return (frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path")


class ChannelDensityArgs:
    def __init__(self, radius_scale, density_blur_radius):
        self.radius_scale = radius_scale
        self.density_blur_radius = density_blur_radius


SOURCE_RESPONSE_PROFILES = {
    "cr21": {
        "secondary_alpha_threshold": 4,
        "highlight_source_luma_threshold": 120.0,
        "highlight_alpha_max": 3,
        "highlight_strength": 1.0,
        "highlight_max_delta": 255.0,
        "dark_secondary_source_luma_min": 0.0,
        "dark_secondary_source_luma_max": 75.0,
        "dark_secondary_strength": 1.0,
        "dark_secondary_max_delta": 255.0,
        "dark_secondary_ring_radius": 0,
        "dark_secondary_ring_source_luma_min": 0.0,
        "dark_secondary_ring_source_luma_max": 95.0,
        "dark_secondary_ring_strength": 0.0,
        "dark_secondary_ring_max_delta": 35.0,
        "channel_band_source_luma_min": 75.0,
        "channel_band_source_luma_max": 82.0,
        "channel_band_strength": 0.6,
        "channel_band_max_delta": 56.0,
        "channel_band_dilate_radius": 0,
        "channel_radius_scale": 1.0,
        "channel_density_blur_radius": 2.0,
        "dark_secondary_soft_source_luma_min": 75.0,
        "dark_secondary_soft_source_luma_max": 95.0,
        "dark_secondary_soft_strength": 0.0,
        "dark_secondary_soft_max_delta": 35.0,
        "nonsecondary_lift": 0.0,
    },
}


def apply_profile(args):
    if args.profile == "default":
        return
    profile = SOURCE_RESPONSE_PROFILES[args.profile]
    for key, value in profile.items():
        setattr(args, key, value)


def channel_union_mask(export_frame, size, args):
    if export_frame is None:
        return None, None
    particles_path = require_file(particle_path(export_frame), "particle stream")
    scene_path = require_file(xml_path(export_frame), "xml scene")
    particles = particle_rows(particles_path)
    draw_args = ChannelDensityArgs(args.channel_radius_scale, args.channel_density_blur_radius)
    _masks, _density, union, _density_union, projected_counts = draw_channel_density(
        particles, scene_path, size, draw_args
    )
    flat = [bool(value) for value in union.ravel()]
    flat = dilate_bool_mask(flat, size, args.channel_band_dilate_radius)
    return flat, {
        "particles_repo_path": posix_rel(particles_path, os.getcwd()),
        "xml_scene_repo_path": posix_rel(scene_path, os.getcwd()),
        "projected_counts": projected_counts,
    }


def classify_response_pixels(actual_img, layer_img, args, channel_mask=None):
    actual_bytes = actual_img.convert("RGB").tobytes()
    alpha_bytes = layer_img.convert("RGBA").split()[3].tobytes()
    source_luma_values = [
        luminance_from_rgb(actual_bytes[index], actual_bytes[index + 1], actual_bytes[index + 2])
        for index in range(0, len(actual_bytes), 3)
    ]
    primary_dark_mask = [
        alpha >= args.secondary_alpha_threshold
        and args.dark_secondary_source_luma_min <= source_luma <= args.dark_secondary_source_luma_max
        for alpha, source_luma in zip(alpha_bytes, source_luma_values)
    ]
    ring_mask = dilated_ring_mask(primary_dark_mask, actual_img.size, args.dark_secondary_ring_radius)
    false_mask = [False] * len(alpha_bytes)
    masks = {
        "secondary": [],
        "highlight": [],
        "dark_secondary_primary": primary_dark_mask,
        "dark_secondary_ring": ring_mask or false_mask,
        "dark_secondary_channel_band": [],
        "dark_secondary_soft": [],
    }
    for pixel_index, alpha in enumerate(alpha_bytes):
        source_luma = source_luma_values[pixel_index]
        is_secondary = alpha >= args.secondary_alpha_threshold
        is_dark_secondary = primary_dark_mask[pixel_index]
        is_ring_dark_secondary = (
            ring_mask is not None
            and ring_mask[pixel_index]
            and is_secondary
            and args.dark_secondary_ring_strength > 0.0
            and source_luma >= args.dark_secondary_ring_source_luma_min
            and source_luma <= args.dark_secondary_ring_source_luma_max
        )
        is_channel_band_dark_secondary = (
            channel_mask is not None
            and channel_mask[pixel_index]
            and is_secondary
            and args.channel_band_strength > 0.0
            and source_luma > args.channel_band_source_luma_min
            and source_luma <= args.channel_band_source_luma_max
        )
        is_soft_dark_secondary = (
            is_secondary
            and not is_dark_secondary
            and not is_ring_dark_secondary
            and not is_channel_band_dark_secondary
            and args.dark_secondary_soft_strength > 0.0
            and source_luma >= args.dark_secondary_soft_source_luma_min
            and source_luma <= args.dark_secondary_soft_source_luma_max
        )
        masks["secondary"].append(is_secondary)
        masks["highlight"].append(
            source_luma >= args.highlight_source_luma_threshold
            and alpha <= args.highlight_alpha_max
        )
        masks["dark_secondary_channel_band"].append(is_channel_band_dark_secondary)
        masks["dark_secondary_soft"].append(is_soft_dark_secondary)
    return actual_bytes, alpha_bytes, source_luma_values, masks


def apply_response(actual_img, layer_img, args, channel_mask=None):
    actual_bytes, alpha_bytes, source_luma_values, masks = classify_response_pixels(
        actual_img,
        layer_img,
        args,
        channel_mask=channel_mask,
    )
    out = bytearray(len(actual_bytes))
    stats = {
        "pixels": len(alpha_bytes),
        "highlight_pixels": 0,
        "dark_secondary_pixels": 0,
        "dark_secondary_primary_pixels": 0,
        "dark_secondary_soft_pixels": 0,
        "dark_secondary_ring_pixels": 0,
        "dark_secondary_channel_band_pixels": 0,
        "nonsecondary_pixels": 0,
        "changed_pixels": 0,
    }
    for pixel_index, alpha in enumerate(alpha_bytes):
        base = pixel_index * 3
        ar, ag, ab = actual_bytes[base], actual_bytes[base + 1], actual_bytes[base + 2]
        nr, ng, nb = float(ar), float(ag), float(ab)
        is_secondary = alpha >= args.secondary_alpha_threshold
        is_highlight = masks["highlight"][pixel_index]
        is_dark_secondary = masks["dark_secondary_primary"][pixel_index]
        is_ring_dark_secondary = masks["dark_secondary_ring"][pixel_index]
        is_channel_band_dark_secondary = masks["dark_secondary_channel_band"][pixel_index]
        is_soft_dark_secondary = masks["dark_secondary_soft"][pixel_index]
        if not is_secondary and args.nonsecondary_lift != 0.0:
            nr += args.nonsecondary_lift
            ng += args.nonsecondary_lift
            nb += args.nonsecondary_lift
            stats["nonsecondary_pixels"] += 1
        if is_highlight and args.highlight_strength > 0.0:
            nr = lighten(nr, args.highlight_strength, args.highlight_max_delta)
            ng = lighten(ng, args.highlight_strength, args.highlight_max_delta)
            nb = lighten(nb, args.highlight_strength, args.highlight_max_delta)
            stats["highlight_pixels"] += 1
        if is_dark_secondary and args.dark_secondary_strength > 0.0:
            nr = darken(nr, args.dark_secondary_strength, args.dark_secondary_max_delta)
            ng = darken(ng, args.dark_secondary_strength, args.dark_secondary_max_delta)
            nb = darken(nb, args.dark_secondary_strength, args.dark_secondary_max_delta)
            stats["dark_secondary_pixels"] += 1
            stats["dark_secondary_primary_pixels"] += 1
        if is_ring_dark_secondary:
            nr = darken(nr, args.dark_secondary_ring_strength, args.dark_secondary_ring_max_delta)
            ng = darken(ng, args.dark_secondary_ring_strength, args.dark_secondary_ring_max_delta)
            nb = darken(nb, args.dark_secondary_ring_strength, args.dark_secondary_ring_max_delta)
            stats["dark_secondary_pixels"] += 1
            stats["dark_secondary_ring_pixels"] += 1
        if is_channel_band_dark_secondary:
            nr = darken(nr, args.channel_band_strength, args.channel_band_max_delta)
            ng = darken(ng, args.channel_band_strength, args.channel_band_max_delta)
            nb = darken(nb, args.channel_band_strength, args.channel_band_max_delta)
            stats["dark_secondary_pixels"] += 1
            stats["dark_secondary_channel_band_pixels"] += 1
        if is_soft_dark_secondary:
            nr = darken(nr, args.dark_secondary_soft_strength, args.dark_secondary_soft_max_delta)
            ng = darken(ng, args.dark_secondary_soft_strength, args.dark_secondary_soft_max_delta)
            nb = darken(nb, args.dark_secondary_soft_strength, args.dark_secondary_soft_max_delta)
            stats["dark_secondary_pixels"] += 1
            stats["dark_secondary_soft_pixels"] += 1
        rr, gg, bb = clamp(nr), clamp(ng), clamp(nb)
        out[base], out[base + 1], out[base + 2] = rr, gg, bb
        if rr != ar or gg != ag or bb != ab:
            stats["changed_pixels"] += 1
    image = Image.frombytes("RGB", actual_img.size, bytes(out))
    stats["highlight_coverage"] = stats["highlight_pixels"] / float(max(1, stats["pixels"]))
    stats["dark_secondary_coverage"] = stats["dark_secondary_pixels"] / float(max(1, stats["pixels"]))
    stats["dark_secondary_primary_coverage"] = stats["dark_secondary_primary_pixels"] / float(max(1, stats["pixels"]))
    stats["dark_secondary_soft_coverage"] = stats["dark_secondary_soft_pixels"] / float(max(1, stats["pixels"]))
    stats["dark_secondary_ring_coverage"] = stats["dark_secondary_ring_pixels"] / float(max(1, stats["pixels"]))
    stats["dark_secondary_channel_band_coverage"] = stats["dark_secondary_channel_band_pixels"] / float(max(1, stats["pixels"]))
    stats["nonsecondary_coverage"] = stats["nonsecondary_pixels"] / float(max(1, stats["pixels"]))
    stats["changed_coverage"] = stats["changed_pixels"] / float(max(1, stats["pixels"]))
    return image, stats


def copy_json_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    return {
        "label": label,
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary.get('gallery', {}).get('index_repo_path')}`",
        f"Status: `{summary['status']}`",
        "",
        "## Settings",
        "",
    ]
    for key, value in summary.get("settings", {}).items():
        lines.append(f"- {key}: `{value}`")
    checks = summary.get("checks", {})
    lines.extend([
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Max highlight coverage: `{checks.get('max_highlight_coverage')}`",
        f"- Max dark secondary coverage: `{checks.get('max_dark_secondary_coverage')}`",
        f"- GIF bytes: `{checks.get('gif_bytes')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Changed | Highlight | Dark Secondary | Graded |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        response = frame.get("response", {})
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {response.get('changed_coverage')} | "
            f"{response.get('highlight_coverage')} | {response.get('dark_secondary_coverage')} | "
            f"`{frame.get('graded_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def apply_source_response(args):
    require_pillow()
    root = os.getcwd()
    composite_summary_path = require_file(args.composite_summary, "composite summary")
    composite_summary = read_json(composite_summary_path)
    if composite_summary.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.composite_summary}: expected lsfs_mitsuba_secondary_composite schema")
    composite_frames = output_frame_map(composite_summary.get("frames") or [])
    export_frames = {}
    export_summary_path = None
    if args.mitsuba_export:
        export_summary_path = require_file(args.mitsuba_export, "Mitsuba export")
        export_summary = read_json(export_summary_path)
        if export_summary.get("schema") != "lsfs_mitsuba_xml_export":
            raise SystemExit(f"{args.mitsuba_export}: expected lsfs_mitsuba_xml_export schema")
        export_frames = export_frame_map(export_summary)
    out_dir = os.path.abspath(args.out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    results = []
    frame_paths = []
    strip_paths = []
    for index, output_frame in enumerate(sorted(composite_frames)):
        composite_frame = composite_frames[output_frame]
        actual_img_path = require_file(composite_path(composite_frame), "composite frame")
        layer_img_path = require_file(layer_path(composite_frame), "secondary layer")
        actual_img = Image.open(actual_img_path).convert("RGB")
        layer_img = Image.open(layer_img_path).convert("RGBA")
        if actual_img.size != layer_img.size:
            raise SystemExit(f"image size mismatch for output_frame={output_frame}")
        channel_mask = None
        channel_metadata = None
        if args.channel_band_strength > 0.0:
            if output_frame not in export_frames:
                raise SystemExit(f"missing Mitsuba export frame for output_frame={output_frame}")
            channel_mask, channel_metadata = channel_union_mask(export_frames[output_frame], actual_img.size, args)
        graded_img, response = apply_response(actual_img, layer_img, args, channel_mask=channel_mask)
        out_path = os.path.join(frames_dir, f"frame_{index:04d}.png")
        graded_img.save(out_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_source_response.png")
        labeled_strip(
            [actual_img, graded_img, layer_img.convert("RGB")],
            ["Source", "Response", "Layer"],
            strip_path,
        )
        frame_paths.append(out_path)
        strip_paths.append(strip_path)
        results.append({
            "frame": index,
            "output_frame": output_frame,
            "source_repo_path": posix_rel(actual_img_path, root),
            "layer_repo_path": posix_rel(layer_img_path, root),
            "graded_repo_path": posix_rel(out_path, root),
            "graded_sha256": sha256_file(out_path),
            "size": os.path.getsize(out_path),
            "dimensions": image_dimensions(out_path),
            "response": response,
        })
        if channel_metadata:
            results[-1]["channel_band"] = channel_metadata

    if not results:
        raise SystemExit("no composite frames to process")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(frame_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Shot GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"strip_{out_index:02d}.png", f"Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "source_region_response_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_composite_grade",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "composite_summary": posix_rel(composite_summary_path, root),
        },
        "settings": {
            "profile": args.profile,
            "secondary_alpha_threshold": args.secondary_alpha_threshold,
            "highlight_source_luma_threshold": args.highlight_source_luma_threshold,
            "highlight_alpha_max": args.highlight_alpha_max,
            "highlight_strength": args.highlight_strength,
            "highlight_max_delta": args.highlight_max_delta,
            "dark_secondary_source_luma_min": args.dark_secondary_source_luma_min,
            "dark_secondary_source_luma_max": args.dark_secondary_source_luma_max,
            "dark_secondary_strength": args.dark_secondary_strength,
            "dark_secondary_max_delta": args.dark_secondary_max_delta,
            "dark_secondary_ring_radius": args.dark_secondary_ring_radius,
            "dark_secondary_ring_source_luma_min": args.dark_secondary_ring_source_luma_min,
            "dark_secondary_ring_source_luma_max": args.dark_secondary_ring_source_luma_max,
            "dark_secondary_ring_strength": args.dark_secondary_ring_strength,
            "dark_secondary_ring_max_delta": args.dark_secondary_ring_max_delta,
            "mitsuba_export": posix_rel(export_summary_path, root) if export_summary_path else None,
            "channel_band_source_luma_min": args.channel_band_source_luma_min,
            "channel_band_source_luma_max": args.channel_band_source_luma_max,
            "channel_band_strength": args.channel_band_strength,
            "channel_band_max_delta": args.channel_band_max_delta,
            "channel_band_dilate_radius": args.channel_band_dilate_radius,
            "channel_radius_scale": args.channel_radius_scale,
            "channel_density_blur_radius": args.channel_density_blur_radius,
            "dark_secondary_soft_source_luma_min": args.dark_secondary_soft_source_luma_min,
            "dark_secondary_soft_source_luma_max": args.dark_secondary_soft_source_luma_max,
            "dark_secondary_soft_strength": args.dark_secondary_soft_strength,
            "dark_secondary_soft_max_delta": args.dark_secondary_soft_max_delta,
            "nonsecondary_lift": args.nonsecondary_lift,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(results),
            "gif_bytes": os.path.getsize(gif_path),
            "max_changed_coverage": max((item["response"].get("changed_coverage") or 0.0 for item in results), default=0.0),
            "max_highlight_coverage": max((item["response"].get("highlight_coverage") or 0.0 for item in results), default=0.0),
            "max_dark_secondary_coverage": max((item["response"].get("dark_secondary_coverage") or 0.0 for item in results), default=0.0),
            "max_dark_secondary_channel_band_coverage": max((item["response"].get("dark_secondary_channel_band_coverage") or 0.0 for item in results), default=0.0),
        },
        "frames": results,
        "gallery": {},
        "next": args.next,
    }
    metadata_files = [
        copy_json_asset(composite_summary_path, assets_dir, "composite_summary.json", "Composite summary", root),
    ]
    if export_summary_path:
        metadata_files.append(copy_json_asset(export_summary_path, assets_dir, "mitsuba_export.json", "Mitsuba export", root))
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
    summary_asset = copy_json_asset(summary_path, assets_dir, "source_region_response_summary.json", "Response summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, assets, summary["gallery"]["metadata_files"], summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_source_region_response_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": summary["gallery"]["metadata_files"],
        "summary_repo_path": posix_rel(summary_path, root),
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(results)} changed={summary['checks']['max_changed_coverage']:.6f} "
        f"summary={summary_path}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Apply source-evidence Mitsuba region response")
    parser.add_argument("composite_summary", help="lsfs_mitsuba_secondary_composite summary")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--profile", choices=("default", *sorted(SOURCE_RESPONSE_PROFILES)), default="default",
                        help="apply a named target-free source-response profile")
    parser.add_argument("--secondary-alpha-threshold", type=int, default=4)
    parser.add_argument("--highlight-source-luma-threshold", type=float, default=145.0)
    parser.add_argument("--highlight-alpha-max", type=int, default=255)
    parser.add_argument("--highlight-strength", type=float, default=0.35)
    parser.add_argument("--highlight-max-delta", type=float, default=55.0)
    parser.add_argument("--dark-secondary-source-luma-min", type=float, default=20.0)
    parser.add_argument("--dark-secondary-source-luma-max", type=float, default=105.0)
    parser.add_argument("--dark-secondary-strength", type=float, default=0.35)
    parser.add_argument("--dark-secondary-max-delta", type=float, default=55.0)
    parser.add_argument("--dark-secondary-ring-radius", type=int, default=0)
    parser.add_argument("--dark-secondary-ring-source-luma-min", type=float, default=0.0)
    parser.add_argument("--dark-secondary-ring-source-luma-max", type=float, default=95.0)
    parser.add_argument("--dark-secondary-ring-strength", type=float, default=0.0)
    parser.add_argument("--dark-secondary-ring-max-delta", type=float, default=35.0)
    parser.add_argument("--mitsuba-export")
    parser.add_argument("--channel-band-source-luma-min", type=float, default=75.0)
    parser.add_argument("--channel-band-source-luma-max", type=float, default=85.0)
    parser.add_argument("--channel-band-strength", type=float, default=0.0)
    parser.add_argument("--channel-band-max-delta", type=float, default=24.0)
    parser.add_argument("--channel-band-dilate-radius", type=int, default=0)
    parser.add_argument("--channel-radius-scale", type=float, default=1.0)
    parser.add_argument("--channel-density-blur-radius", type=float, default=2.0)
    parser.add_argument("--dark-secondary-soft-source-luma-min", type=float, default=75.0)
    parser.add_argument("--dark-secondary-soft-source-luma-max", type=float, default=95.0)
    parser.add_argument("--dark-secondary-soft-strength", type=float, default=0.0)
    parser.add_argument("--dark-secondary-soft-max-delta", type=float, default=35.0)
    parser.add_argument("--nonsecondary-lift", type=float, default=0.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Source Region Response")
    parser.add_argument("--next", default="Compare this target-free source response against the target-gap baseline.")
    args = parser.parse_args()
    apply_profile(args)
    if args.secondary_alpha_threshold < 0 or args.secondary_alpha_threshold > 255:
        parser.error("secondary-alpha-threshold must be in [0, 255]")
    if args.highlight_alpha_max < 0 or args.highlight_alpha_max > 255:
        parser.error("highlight-alpha-max must be in [0, 255]")
    if (
        args.highlight_strength < 0.0
        or args.dark_secondary_strength < 0.0
        or args.dark_secondary_ring_strength < 0.0
        or args.channel_band_strength < 0.0
        or args.dark_secondary_soft_strength < 0.0
    ):
        parser.error("strength values must be non-negative")
    if (
        args.highlight_max_delta < 0.0
        or args.dark_secondary_max_delta < 0.0
        or args.dark_secondary_ring_max_delta < 0.0
        or args.channel_band_max_delta < 0.0
        or args.dark_secondary_soft_max_delta < 0.0
    ):
        parser.error("max delta values must be non-negative")
    if args.dark_secondary_source_luma_min > args.dark_secondary_source_luma_max:
        parser.error("dark secondary luma min cannot exceed max")
    if args.dark_secondary_ring_radius < 0:
        parser.error("dark secondary ring radius must be non-negative")
    if args.dark_secondary_ring_source_luma_min > args.dark_secondary_ring_source_luma_max:
        parser.error("dark secondary ring luma min cannot exceed max")
    if args.channel_band_source_luma_min > args.channel_band_source_luma_max:
        parser.error("channel band luma min cannot exceed max")
    if args.channel_band_dilate_radius < 0:
        parser.error("channel band dilate radius must be non-negative")
    if args.channel_radius_scale <= 0.0:
        parser.error("channel radius scale must be positive")
    if args.channel_density_blur_radius < 0.0:
        parser.error("channel density blur radius must be non-negative")
    if args.channel_band_strength > 0.0 and not args.mitsuba_export:
        parser.error("mitsuba-export is required when channel band strength is positive")
    if args.dark_secondary_soft_source_luma_min > args.dark_secondary_soft_source_luma_max:
        parser.error("dark secondary soft luma min cannot exceed max")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    return args


if __name__ == "__main__":
    apply_source_response(parse_args())
