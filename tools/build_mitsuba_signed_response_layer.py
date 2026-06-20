#!/usr/bin/env python
"""Build an explicit signed-response layer cache from Mitsuba target-gap requests."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageDraw = None

from apply_mitsuba_signed_gap_response import (
    apply_response,
    parse_csv,
    render_preview_path,
    resolve_path,
    select_requests,
)
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
        raise SystemExit("Pillow is required to build signed response layers")


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames if frame.get("output_frame") is not None}


def response_layer(source_img, response_img, alpha_scale):
    source = source_img.convert("RGB").tobytes()
    response = response_img.convert("RGB").tobytes()
    rgba = bytearray()
    changed_pixels = 0
    max_delta = 0
    for index in range(0, len(source), 3):
        sr, sg, sb = source[index], source[index + 1], source[index + 2]
        rr, rg, rb = response[index], response[index + 1], response[index + 2]
        dr = rr - sr
        dg = rg - sg
        db = rb - sb
        delta = max(abs(dr), abs(dg), abs(db))
        max_delta = max(max_delta, delta)
        if delta > 0:
            changed_pixels += 1
        alpha = max(0, min(255, int(round(delta * alpha_scale))))
        # Store positive response color directly; dimming responses are represented by alpha plus metadata.
        rgba.extend((max(0, dr), max(0, dg), max(0, db), alpha))
    layer = Image.frombytes("RGBA", source_img.size, bytes(rgba))
    return layer, {
        "changed_pixels": changed_pixels,
        "changed_coverage": changed_pixels / float(max(1, source_img.size[0] * source_img.size[1])),
        "max_layer_delta": max_delta,
    }


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
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def write_gif(paths, gif_path, fps):
    duration_ms = max(1, int(round(1000.0 / max(1.0, fps))))
    images = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in paths]
    try:
        os.makedirs(os.path.dirname(gif_path), exist_ok=True)
        images[0].save(gif_path, save_all=True, append_images=images[1:], duration=duration_ms, loop=0, optimize=False)
    finally:
        for image in images:
            image.close()


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
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
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "Layer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Layer Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Requests", checks.get("applied_requests")),
            ("Changed", f"{checks.get('max_changed_coverage', 0.0):.6f}"),
            ("Max delta", checks.get("max_layer_delta")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Layer GIF"></section>' if gif else ""
    figures = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
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
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; width: 100%; min-width: 960px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; word-break: break-word; }}
    figure {{ margin: 0 0 12px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section>{figures}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
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
        f"- Applied requests: `{checks.get('applied_requests')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Max layer delta: `{checks.get('max_layer_delta')}`",
        f"- Layer bytes: `{format_bytes(checks.get('layer_bytes', 0))}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Requests | Changed | Max Delta | Layer | Composite |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for frame in summary.get("frames") or []:
        layer = frame.get("layer") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('applied_requests')} | "
            f"{frame.get('response', {}).get('changed_coverage')} | "
            f"{frame.get('response', {}).get('max_layer_delta')} | "
            f"`{layer.get('repo_path')}` | `{frame.get('composite_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.render_manifest, "render manifest")
    analysis_path = require_file(args.signed_gap_analysis, "signed gap analysis")
    render = read_json(render_path)
    analysis = read_json(analysis_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if analysis.get("schema") != "lsfs_mitsuba_signed_target_gap_analysis":
        raise SystemExit(f"{args.signed_gap_analysis}: expected lsfs_mitsuba_signed_target_gap_analysis schema")

    selected_requests, requests_by_output = select_requests(analysis, args)
    analysis_frames = output_frame_map(analysis.get("frames") or [])
    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    layer_dir = os.path.join(out_dir, "layers")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (composite_dir, layer_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    frames = []
    strip_paths = []
    for index, frame in enumerate(render.get("frames") or []):
        output_frame = frame.get("output_frame")
        src = require_file(resolve_path(render_preview_path(frame)), "render preview")
        analysis_frame = analysis_frames.get(output_frame)
        target_path = require_file(resolve_path((analysis_frame or {}).get("target_repo_path")), "target frame")
        source_img = Image.open(src).convert("RGB")
        target_img = Image.open(target_path).convert("RGB")
        if source_img.size != target_img.size:
            source_img = source_img.resize(target_img.size, Image.Resampling.BICUBIC)
        frame_requests = requests_by_output.get(output_frame, [])
        composite_img, response_stats = apply_response(source_img, target_img, frame_requests, args)
        layer_img, layer_stats = response_layer(source_img, composite_img, args.layer_alpha_scale)
        response_stats.update(layer_stats)
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        layer_path = os.path.join(layer_dir, f"frame_{index:04d}_signed_response_layer.png")
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}_signed_response_layer.png")
        composite_img.save(composite_path)
        layer_img.save(layer_path)
        labeled_strip([source_img, layer_img.convert("RGB"), composite_img, target_img], ["Source", "Response Layer", "Composite", "Target"], strip_path)
        strip_paths.append(strip_path)
        frames.append({
            "frame": frame.get("frame", index),
            "output_frame": output_frame,
            "source_repo_path": posix_rel(src, root),
            "target_repo_path": posix_rel(target_path, root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "layer_path": layer_path,
            "layer_repo_path": posix_rel(layer_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "applied_requests": len(frame_requests),
            "response": response_stats,
            "layer": {
                "path": layer_path,
                "repo_path": posix_rel(layer_path, root),
                "sha256": sha256_file(layer_path),
                "size": os.path.getsize(layer_path),
            },
            "size": os.path.getsize(composite_path),
            "sha256": sha256_file(composite_path),
        })

    if not frames:
        raise SystemExit("no frames were generated")

    gif_path = os.path.join(assets_dir, "signed_response_layer.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "signed_response_layer.gif", "Layer GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"layer_strip_{out_index:02d}.png", f"Layer Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "signed_response_layer_summary.json")
    metadata_files = [
        copy_asset(render_path, assets_dir, "render_manifest.json", "Render manifest", root),
        copy_asset(analysis_path, assets_dir, "signed_target_gap_analysis.json", "Signed target-gap analysis", root),
    ]
    generated_utc = datetime.now(timezone.utc).isoformat()
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_signed_response_layer",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": "ready",
        "source": {
            "render_manifest": posix_rel(render_path, root),
            "signed_gap_analysis": posix_rel(analysis_path, root),
        },
        "settings": {
            "regions": sorted(parse_csv(args.regions)),
            "directions": sorted(parse_csv(args.directions)),
            "max_requests": args.max_requests,
            "min_score": args.min_score,
            "strength_scale": args.strength_scale,
            "max_strength": args.max_strength,
            "max_channel_delta": args.max_channel_delta,
            "feather_power": args.feather_power,
            "layer_alpha_scale": args.layer_alpha_scale,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": {
            "frames": len(frames),
            "selected_requests": len(selected_requests),
            "applied_requests": sum(frame["applied_requests"] for frame in frames),
            "max_changed_coverage": max(frame["response"]["changed_coverage"] for frame in frames),
            "max_layer_delta": max(frame["response"]["max_layer_delta"] for frame in frames),
            "layer_bytes": sum(frame["layer"]["size"] for frame in frames),
            "composite_bytes": sum(frame["size"] for frame in frames),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "selected_requests": selected_requests,
        "frames": frames,
        "gallery": {},
    }
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
    summary_asset = copy_asset(summary_path, assets_dir, "signed_response_layer_summary.json", "Layer summary", root)
    summary["gallery"]["metadata_files"] = [summary_asset, *metadata_files]
    write_json(summary_path, summary)
    shutil.copy2(summary_path, summary_asset["asset"])
    write_text(index_path, html_page(args.title, summary, assets, summary["gallery"]["metadata_files"]))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_signed_response_layer_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "index_repo_path": posix_rel(index_path, root),
        "summary_repo_path": posix_rel(summary_path, root),
        "assets": assets,
        "metadata_files": summary["gallery"]["metadata_files"],
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready frames={len(frames)} requests={summary['checks']['applied_requests']} "
        f"max_changed={summary['checks']['max_changed_coverage']:.6f} summary={summary_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a signed response layer cache")
    parser.add_argument("render_manifest")
    parser.add_argument("signed_gap_analysis")
    parser.add_argument("out_dir")
    parser.add_argument("--regions", default="highlight")
    parser.add_argument("--directions", default="brighten")
    parser.add_argument("--max-requests", type=int, default=12)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--strength-scale", type=float, default=0.35)
    parser.add_argument("--max-strength", type=float, default=0.35)
    parser.add_argument("--max-channel-delta", type=float, default=24.0)
    parser.add_argument("--feather-power", type=float, default=1.5)
    parser.add_argument("--layer-alpha-scale", type=float, default=10.0)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="Mitsuba Signed Response Layer")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Compare this explicit signed response layer against the target preview.")
    args = parser.parse_args(argv)
    if args.max_requests <= 0:
        parser.error("max-requests must be positive")
    if args.min_score < 0.0:
        parser.error("min-score must be non-negative")
    if args.strength_scale < 0.0:
        parser.error("strength-scale must be non-negative")
    if args.max_strength <= 0.0:
        parser.error("max-strength must be positive")
    if args.max_channel_delta <= 0.0:
        parser.error("max-channel-delta must be positive")
    if args.feather_power <= 0.0:
        parser.error("feather-power must be positive")
    if args.layer_alpha_scale <= 0.0:
        parser.error("layer-alpha-scale must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    build(args)


if __name__ == "__main__":
    main()
