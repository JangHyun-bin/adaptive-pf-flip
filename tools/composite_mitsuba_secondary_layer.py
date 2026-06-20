#!/usr/bin/env python
"""Composite a soft screen-space secondary layer over Mitsuba preview frames."""

import argparse
import csv
import math
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None

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


CHANNEL_STYLE = {
    "spray": {"color": (220, 238, 250), "alpha": 26, "radius": 4.2},
    "foam": {"color": (246, 250, 252), "alpha": 42, "radius": 6.8},
    "bubble": {"color": (160, 205, 232), "alpha": 22, "radius": 5.2},
    "droplet": {"color": (210, 235, 250), "alpha": 30, "radius": 3.5},
}


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to composite secondary layers")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(path.replace("/", os.sep))


def key_path(path, root):
    resolved = resolve_path(path)
    try:
        return os.path.relpath(resolved, root).replace(os.sep, "/").lower()
    except ValueError:
        return resolved.replace(os.sep, "/").lower()


def parse_vec(value):
    return [float(part.strip()) for part in value.split(",")]


def parse_rgb(value, label):
    items = [int(part.strip()) for part in value.split(",")] if value else []
    if len(items) != 3:
        raise ValueError(f"{label} must contain three comma-separated RGB values")
    for item in items:
        if item < 0 or item > 255:
            raise ValueError(f"{label} values must be in [0, 255]")
    return tuple(items)


def vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def vec_dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def vec_cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def vec_norm(a):
    length = math.sqrt(max(1.0e-12, vec_dot(a, a)))
    return [item / length for item in a]


def parse_camera(xml_path):
    root = ET.parse(xml_path).getroot()
    lookat = root.find(".//lookat")
    if lookat is None:
        raise ValueError(f"{xml_path}: missing lookat camera")
    fov_item = root.find(".//sensor/float[@name='fov']")
    width_item = root.find(".//film/integer[@name='width']")
    height_item = root.find(".//film/integer[@name='height']")
    origin = parse_vec(lookat.attrib["origin"])
    target = parse_vec(lookat.attrib["target"])
    up = parse_vec(lookat.attrib.get("up", "0, 1, 0"))
    return {
        "origin": origin,
        "target": target,
        "up": up,
        "fov": float(fov_item.attrib["value"]) if fov_item is not None else 45.0,
        "width": int(width_item.attrib["value"]) if width_item is not None else 960,
        "height": int(height_item.attrib["value"]) if height_item is not None else 540,
    }


def projection_basis(camera):
    forward = vec_norm(vec_sub(camera["target"], camera["origin"]))
    right = vec_norm(vec_cross(forward, camera["up"]))
    up = vec_norm(vec_cross(right, forward))
    return forward, right, up


def project(point, camera, width, height):
    forward, right, up = projection_basis(camera)
    rel = vec_sub(point, camera["origin"])
    z = vec_dot(rel, forward)
    if z <= 0.1:
        return None
    x = vec_dot(rel, right)
    y = vec_dot(rel, up)
    aspect = width / float(max(1, height))
    tan_y = math.tan(math.radians(camera["fov"]) * 0.5)
    ndc_x = x / (z * tan_y * aspect)
    ndc_y = y / (z * tan_y)
    px = (ndc_x * 0.5 + 0.5) * width
    py = (0.5 - ndc_y * 0.5) * height
    if px < -64 or px > width + 64 or py < -64 or py > height + 64:
        return None
    return px, py, z


def read_secondary_particles(path, max_particles):
    particles = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            channel = (row.get("render_channel") or "").strip()
            if channel not in CHANNEL_STYLE:
                continue
            kind = (row.get("kind") or "").strip()
            if not kind.startswith("secondary"):
                continue
            particles.append({
                "channel": channel,
                "x": float(row.get("x") or 0.0),
                "y": float(row.get("y") or 0.0),
                "z": float(row.get("z") or 0.0),
                "volume": float(row.get("volume") or 1.0),
            })
    if max_particles and len(particles) > max_particles:
        if max_particles == 1:
            return [particles[len(particles) // 2]]
        indices = sorted(set(round(i * (len(particles) - 1) / float(max_particles - 1)) for i in range(max_particles)))
        return [particles[index] for index in indices]
    return particles


def draw_layer(particles, camera, width, height, args):
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    projected = 0
    counts = {channel: 0 for channel in CHANNEL_STYLE}
    for particle in particles:
        projected_point = project([particle["x"], particle["y"], particle["z"]], camera, width, height)
        if projected_point is None:
            continue
        px, py, depth = projected_point
        style = CHANNEL_STYLE[particle["channel"]]
        depth_scale = max(0.55, min(2.4, args.reference_depth / max(1.0, depth)))
        volume_scale = max(0.65, min(1.8, particle["volume"] ** (1.0 / 3.0) if particle["volume"] > 0.0 else 1.0))
        radius = style["radius"] * args.radius_scale * depth_scale * volume_scale
        alpha_scale = args.opacity_scale * (args.shadow_alpha_scale if args.blend_mode == "shadow" else 1.0)
        alpha = int(max(1, min(255, style["alpha"] * alpha_scale)))
        rgb = args.shadow_color_rgb if args.blend_mode == "shadow" else style["color"]
        color = (*rgb, alpha)
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=color)
        projected += 1
        counts[particle["channel"]] += 1
    if args.blur_radius > 0.0:
        layer = layer.filter(ImageFilter.GaussianBlur(args.blur_radius))
    return layer, projected, counts


def alpha_coverage(layer):
    alpha = layer.split()[3]
    hist = alpha.histogram()
    nonzero = sum(hist[1:])
    return nonzero / float(max(1, layer.size[0] * layer.size[1]))


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    dims = image_dimensions(dest)
    entry = {
        "label": label,
        "asset": dest,
        "repo_path": posix_rel(dest, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    if dims:
        entry["dimensions"] = dims
    return entry


def write_gif(frame_paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    try:
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def html_page(title, assets, metadata_files, summary):
    gif = next((item for item in assets if item["label"] == "Shot GIF"), None)
    keyframes = [item for item in assets if item["label"].startswith("Keyframe")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    metrics = [
        ("Frames", summary["checks"].get("frames")),
        ("Particles", summary["checks"].get("particles_total")),
        ("Projected", summary["checks"].get("particles_projected")),
        ("Max Coverage", summary["checks"].get("max_layer_coverage")),
        ("Blur", summary["settings"].get("blur_radius")),
        ("Radius Scale", summary["settings"].get("radius_scale")),
    ]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in metrics
    )
    frames = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in keyframes
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Composite GIF"></section>' if gif else ""
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
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #aab7c4; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
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
    <section class="grid">{frames}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, manifest_path, root, next_text):
    checks = summary["checks"]
    visibility_cache = summary.get("secondary_visibility_cache") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(manifest_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Visibility cache: `{visibility_cache.get('repo_path')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Particles total: `{checks.get('particles_total')}`",
        f"- Particles projected: `{checks.get('particles_projected')}`",
        f"- Max layer coverage: `{checks.get('max_layer_coverage')}`",
        f"- Layer bytes: `{format_bytes(checks.get('layer_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Particles | Projected | Coverage | Composite |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('particles_total')} | "
            f"{frame.get('particles_projected')} | {frame.get('layer_coverage')} | `{frame.get('composite_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build_export_frame_map(export, root):
    mapping = {}
    for frame in export.get("frames") or []:
        xml = frame.get("xml_scene") or {}
        for value in (xml.get("path"), xml.get("repo_path")):
            if value:
                mapping[key_path(value, root)] = frame
    return mapping


def build_visibility_cache(summary, cache_path, root):
    frames = []
    layer_bytes = 0
    for frame in summary.get("frames") or []:
        layer_path = resolve_path(frame.get("layer_repo_path"))
        layer_size = os.path.getsize(layer_path)
        layer_bytes += layer_size
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "sequence_frame": frame.get("sequence_frame"),
            "layer_repo_path": posix_rel(layer_path, root),
            "layer_sha256": sha256_file(layer_path),
            "layer_size": layer_size,
            "layer_coverage": frame.get("layer_coverage"),
            "particles_projected": frame.get("particles_projected"),
            "projected_counts": frame.get("projected_counts"),
        })
    return {
        "schema": "lsfs_mitsuba_secondary_visibility_cache",
        "version": 1,
        "generated_utc": summary.get("generated_utc"),
        "title": f"{summary.get('title')} Visibility Cache",
        "profile_name": (summary.get("settings") or {}).get("profile_name"),
        "source": summary.get("source"),
        "settings": summary.get("settings"),
        "usage": {
            "kind": "renderer_facing_secondary_visibility_layer",
            "composition": "alpha_composite_visibility_layer_over_render_preview",
            "blend_mode": (summary.get("settings") or {}).get("blend_mode"),
            "layer_color_space": "rgba_png",
        },
        "checks": {
            "frames": len(frames),
            "particles_projected": sum(item.get("particles_projected") or 0 for item in frames),
            "max_layer_coverage": max((item.get("layer_coverage") or 0.0 for item in frames), default=0.0),
            "layer_bytes": layer_bytes,
            "failures": 0,
        },
        "path": cache_path,
        "repo_path": posix_rel(cache_path, root),
        "frames": frames,
    }


def composite(args):
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.render_manifest, "render manifest")
    render = read_json(render_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.render_manifest}: render status is {render.get('status')!r}")
    export_path = require_file((render.get("mitsuba_export") or {}).get("path") or (render.get("mitsuba_export") or {}).get("repo_path"), "mitsuba export")
    export = read_json(export_path)
    export_frames = build_export_frame_map(export, root)

    out_dir = os.path.abspath(args.out_dir)
    layer_dir = os.path.join(out_dir, "layers")
    composite_dir = os.path.join(out_dir, "composites")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(layer_dir, exist_ok=True)
    os.makedirs(composite_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frame_results = []
    composite_paths = []
    total_particles = 0
    total_projected = 0
    max_coverage = 0.0
    layer_bytes = 0
    for index, frame in enumerate(render.get("frames") or []):
        preview_path = require_file((frame.get("preview") or {}).get("path") or (frame.get("preview") or {}).get("repo_path"), "render preview")
        xml_path = require_file((frame.get("xml_scene") or {}).get("path") or (frame.get("xml_scene") or {}).get("repo_path"), "xml scene")
        export_frame = export_frames.get(key_path(xml_path, root))
        if not export_frame:
            raise SystemExit(f"missing export frame for {xml_path}")
        particles_path = require_file((export_frame.get("sidecar_assets") or {}).get("particles"), "particle stream")
        base = Image.open(preview_path).convert("RGBA")
        width, height = base.size
        camera = parse_camera(xml_path)
        particles = read_secondary_particles(particles_path, args.max_particles)
        layer, projected, counts = draw_layer(particles, camera, width, height, args)
        layer_path = os.path.join(layer_dir, f"frame_{index:04d}_secondary_layer.png")
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        layer.save(layer_path)
        Image.alpha_composite(base, layer).convert("RGB").save(composite_path)
        coverage = alpha_coverage(layer)
        layer_size = os.path.getsize(layer_path)
        composite_size = os.path.getsize(composite_path)
        total_particles += len(particles)
        total_projected += projected
        max_coverage = max(max_coverage, coverage)
        layer_bytes += layer_size
        composite_paths.append(composite_path)
        frame_results.append({
            "frame": index,
            "output_frame": frame.get("output_frame"),
            "sequence_frame": frame.get("sequence_frame"),
            "preview_repo_path": posix_rel(preview_path, root),
            "layer_repo_path": posix_rel(layer_path, root),
            "layer_sha256": sha256_file(layer_path),
            "layer_size": layer_size,
            "composite_repo_path": posix_rel(composite_path, root),
            "composite_sha256": sha256_file(composite_path),
            "composite_size": composite_size,
            "particles_total": len(particles),
            "particles_projected": projected,
            "projected_counts": counts,
            "layer_coverage": coverage,
        })

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(composite_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Shot GIF", root)]
    key_indices = sorted(set(round(i * (len(composite_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes))) if composite_paths else []
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(composite_paths[frame_index], assets_dir, f"keyframe_{out_index:02d}.png", f"Keyframe {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "secondary_composite_summary.json")
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "source": {
            "render_manifest": posix_rel(render_path, root),
            "mitsuba_export": posix_rel(export_path, root),
        },
        "settings": {
            "profile_name": args.profile_name,
            "max_particles": args.max_particles,
            "radius_scale": args.radius_scale,
            "opacity_scale": args.opacity_scale,
            "blend_mode": args.blend_mode,
            "shadow_alpha_scale": args.shadow_alpha_scale if args.blend_mode == "shadow" else None,
            "shadow_color": list(args.shadow_color_rgb) if args.blend_mode == "shadow" else None,
            "blur_radius": args.blur_radius,
            "reference_depth": args.reference_depth,
            "fps": args.fps,
        },
        "checks": {
            "frames": len(frame_results),
            "particles_total": total_particles,
            "particles_projected": total_projected,
            "max_layer_coverage": max_coverage,
            "layer_bytes": layer_bytes,
            "gif_bytes": os.path.getsize(gif_path),
        },
        "secondary_visibility_cache": {},
        "gallery": {},
        "frames": frame_results,
    }
    cache_path = os.path.join(out_dir, "secondary_visibility_cache.json")
    cache = build_visibility_cache(summary, cache_path, root)
    write_json(cache_path, cache)
    summary["secondary_visibility_cache"] = {
        "path": cache_path,
        "repo_path": posix_rel(cache_path, root),
        "sha256": sha256_file(cache_path),
        "size": os.path.getsize(cache_path),
        "schema": cache["schema"],
        "profile_name": cache["profile_name"],
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "secondary_composite_summary.json", "Composite summary", root)
    cache_asset = copy_asset(cache_path, assets_dir, "secondary_visibility_cache.json", "Visibility cache", root)
    render_asset = copy_asset(render_path, assets_dir, "mitsuba_render.json", "Mitsuba render manifest", root)
    export_asset = copy_asset(export_path, assets_dir, "mitsuba_export.json", "Mitsuba export manifest", root)
    metadata_files = [summary_asset, cache_asset, render_asset, export_asset]
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
    write_text(index_path, html_page(args.title, assets, metadata_files, summary))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_secondary_composite_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
        "summary": {
            "frames": len(frame_results),
            "particles_projected": total_projected,
            "max_layer_coverage": max_coverage,
            "layer_bytes": layer_bytes,
            "secondary_visibility_cache": summary["secondary_visibility_cache"].get("repo_path"),
        },
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ok frames={len(frame_results)} projected={total_projected} "
        f"coverage={max_coverage} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Composite soft secondary layers over Mitsuba previews")
    parser.add_argument("render_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--max-particles", type=int, default=1400)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument("--opacity-scale", type=float, default=1.0)
    parser.add_argument("--blend-mode", choices=("alpha", "shadow"), default="alpha")
    parser.add_argument("--shadow-alpha-scale", type=float, default=1.0)
    parser.add_argument("--shadow-color", default="12,16,18",
                        help="RGB tint used by --blend-mode=shadow")
    parser.add_argument("--blur-radius", type=float, default=2.4)
    parser.add_argument("--reference-depth", type=float, default=52.0)
    parser.add_argument("--profile-name", default="custom")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Secondary Composite")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this composite as a screen-space secondary layer proof.")
    args = parser.parse_args(argv)
    if args.max_particles <= 0:
        parser.error("max-particles must be positive")
    if args.radius_scale <= 0.0:
        parser.error("radius-scale must be positive")
    if args.opacity_scale <= 0.0:
        parser.error("opacity-scale must be positive")
    if args.shadow_alpha_scale <= 0.0:
        parser.error("shadow-alpha-scale must be positive")
    if args.blur_radius < 0.0:
        parser.error("blur-radius must be non-negative")
    if args.reference_depth <= 0.0:
        parser.error("reference-depth must be positive")
    if not args.profile_name.strip():
        parser.error("profile-name must not be empty")
    args.profile_name = args.profile_name.strip()
    try:
        args.shadow_color_rgb = parse_rgb(args.shadow_color, "shadow-color")
    except ValueError as exc:
        parser.error(str(exc))
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    composite(args)


if __name__ == "__main__":
    main()
