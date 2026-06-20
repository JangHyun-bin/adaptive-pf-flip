#!/usr/bin/env python
"""Apply a Mitsuba secondary visibility cache over rendered preview frames."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to apply secondary visibility caches")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def render_preview_path(frame):
    preview = (frame or {}).get("preview") or {}
    return preview.get("path") or preview.get("repo_path")


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
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def html_page(title, assets, metadata_files, summary):
    gif = next((item for item in assets if item["label"] == "Shot GIF"), None)
    keyframes = [item for item in assets if item["label"].startswith("Keyframe")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks") or {}
    metrics = [
        ("Frames", checks.get("frames")),
        ("Projected", checks.get("particles_projected")),
        ("Max Coverage", checks.get("max_layer_coverage")),
        ("Layer Bytes", format_bytes(checks.get("layer_bytes", 0))),
        ("Profile", (summary.get("settings") or {}).get("profile_name")),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    frames = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in keyframes
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Visibility cache composite GIF"></section>' if gif else ""
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


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks") or {}
    cache = summary.get("secondary_visibility_cache") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Visibility cache: `{cache.get('repo_path')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Projected particles: `{checks.get('particles_projected')}`",
        f"- Max layer coverage: `{checks.get('max_layer_coverage')}`",
        f"- Layer bytes: `{format_bytes(checks.get('layer_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Coverage | Composite |",
        "| ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('layer_coverage')} | `{frame.get('composite_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def apply_cache(args):
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.render_manifest, "render manifest")
    cache_path = require_file(args.visibility_cache, "visibility cache")
    render = read_json(render_path)
    cache = read_json(cache_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.render_manifest}: render status is {render.get('status')!r}")
    if cache.get("schema") != "lsfs_mitsuba_secondary_visibility_cache":
        raise SystemExit(f"{args.visibility_cache}: expected lsfs_mitsuba_secondary_visibility_cache schema")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(composite_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    cache_frames = output_frame_map(cache.get("frames") or [])
    frame_results = []
    composite_paths = []
    layer_bytes = 0
    total_projected = 0
    max_coverage = 0.0
    for index, render_frame in enumerate(render.get("frames") or []):
        output_frame = render_frame.get("output_frame")
        cache_frame = cache_frames.get(output_frame)
        if not cache_frame:
            raise SystemExit(f"missing visibility cache frame for output_frame={output_frame}")
        preview_path = require_file(render_preview_path(render_frame), "render preview")
        layer_path = require_file(cache_frame.get("layer_path") or cache_frame.get("layer_repo_path"), "visibility layer")
        base = Image.open(preview_path).convert("RGBA")
        layer = Image.open(layer_path).convert("RGBA")
        if base.size != layer.size:
            raise SystemExit(f"layer size mismatch for output_frame={output_frame}: {layer.size} != {base.size}")
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        Image.alpha_composite(base, layer).convert("RGB").save(composite_path)
        coverage = alpha_coverage(layer)
        layer_size = os.path.getsize(layer_path)
        layer_bytes += layer_size
        total_projected += int(cache_frame.get("particles_projected") or 0)
        max_coverage = max(max_coverage, coverage)
        composite_paths.append(composite_path)
        frame_results.append({
            "frame": index,
            "output_frame": output_frame,
            "sequence_frame": render_frame.get("sequence_frame"),
            "preview_repo_path": posix_rel(preview_path, root),
            "layer_repo_path": posix_rel(layer_path, root),
            "layer_sha256": sha256_file(layer_path),
            "layer_size": layer_size,
            "layer_coverage": coverage,
            "composite_repo_path": posix_rel(composite_path, root),
            "composite_sha256": sha256_file(composite_path),
            "composite_size": os.path.getsize(composite_path),
            "particles_projected": int(cache_frame.get("particles_projected") or 0),
            "projected_counts": cache_frame.get("projected_counts") or {},
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
            "visibility_cache": posix_rel(cache_path, root),
        },
        "settings": {
            "profile_name": cache.get("profile_name"),
            "source": "secondary_visibility_cache",
            "fps": args.fps,
        },
        "checks": {
            "frames": len(frame_results),
            "particles_total": total_projected,
            "particles_projected": total_projected,
            "max_layer_coverage": max_coverage,
            "layer_bytes": layer_bytes,
            "gif_bytes": os.path.getsize(gif_path),
        },
        "secondary_visibility_cache": {
            "path": cache_path,
            "repo_path": posix_rel(cache_path, root),
            "sha256": sha256_file(cache_path),
            "size": os.path.getsize(cache_path),
            "schema": cache.get("schema"),
            "profile_name": cache.get("profile_name"),
        },
        "gallery": {},
        "frames": frame_results,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "secondary_composite_summary.json", "Composite summary", root)
    cache_asset = copy_asset(cache_path, assets_dir, "secondary_visibility_cache.json", "Visibility cache", root)
    render_asset = copy_asset(render_path, assets_dir, "mitsuba_render.json", "Mitsuba render manifest", root)
    metadata_files = [summary_asset, cache_asset, render_asset]
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
        "schema": "lsfs_mitsuba_secondary_visibility_cache_apply_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(resolve_path(args.report), markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ok frames={len(frame_results)} projected={total_projected} "
        f"coverage={max_coverage} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render_manifest")
    parser.add_argument("visibility_cache")
    parser.add_argument("out_dir")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Secondary Visibility Cache Apply")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this cache-consumed composite for renderer-facing review.")
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    apply_cache(args)


if __name__ == "__main__":
    main()
