#!/usr/bin/env python
"""Derive renderer-response intent regions from visual-cache AOVs."""

import argparse
import os
from collections import deque
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to derive response intent")


def aov_path(frame, name):
    entry = ((frame.get("aovs") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


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


def luma(pixel):
    if isinstance(pixel, int):
        return pixel
    return int(round(0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]))


def component_kind(cx, cy, bbox, width, height):
    _x0, y0, _x1, y1 = bbox
    if cy < height * 0.42:
        return "surface_highlight_response"
    if y1 - y0 <= height * 0.08 and cy < height * 0.62:
        return "crest_band_response"
    return "water_body_response"


def suggested_control(kind, mean_response_luma, max_response_luma):
    if kind == "surface_highlight_response":
        return {
            "type": "localized_light_or_glint",
            "strength_hint": round(max_response_luma / 255.0, 6),
            "priority": "high",
        }
    if kind == "crest_band_response":
        return {
            "type": "anisotropic_surface_texture",
            "strength_hint": round(max(mean_response_luma, max_response_luma * 0.5) / 255.0, 6),
            "priority": "medium",
        }
    return {
        "type": "volume_or_material_response",
        "strength_hint": round(mean_response_luma / 255.0, 6),
        "priority": "medium",
    }


def connected_components(mask_img, response_img, diff_img, args):
    width, height = mask_img.size
    mask = mask_img.convert("L").load()
    response = response_img.convert("L").load()
    diff = diff_img.convert("RGB").load()
    visited = bytearray(width * height)
    components = []
    for y in range(height):
        row_offset = y * width
        for x in range(width):
            offset = row_offset + x
            if visited[offset] or mask[x, y] <= 0:
                continue
            visited[offset] = 1
            queue = deque([(x, y)])
            pixels = []
            while queue:
                px, py = queue.popleft()
                pixels.append((px, py))
                for ny in (py - 1, py, py + 1):
                    if ny < 0 or ny >= height:
                        continue
                    for nx in (px - 1, px, px + 1):
                        if nx < 0 or nx >= width or (nx == px and ny == py):
                            continue
                        n_offset = ny * width + nx
                        if visited[n_offset] or mask[nx, ny] <= 0:
                            continue
                        visited[n_offset] = 1
                        queue.append((nx, ny))
            if len(pixels) < args.min_pixels:
                continue
            xs = [p[0] for p in pixels]
            ys = [p[1] for p in pixels]
            x0, x1 = min(xs), max(xs)
            y0, y1 = min(ys), max(ys)
            response_values = [response[px, py] for px, py in pixels]
            diff_values = [luma(diff[px, py]) for px, py in pixels]
            cx = sum(xs) / float(len(xs))
            cy = sum(ys) / float(len(ys))
            mean_response = sum(response_values) / float(len(response_values))
            max_response = max(response_values)
            mean_diff = sum(diff_values) / float(len(diff_values))
            kind = component_kind(cx, cy, (x0, y0, x1, y1), width, height)
            components.append({
                "component": len(components),
                "kind": kind,
                "bbox": [x0, y0, x1, y1],
                "bbox_normalized": [
                    round(x0 / float(width), 6),
                    round(y0 / float(height), 6),
                    round((x1 + 1) / float(width), 6),
                    round((y1 + 1) / float(height), 6),
                ],
                "centroid": [round(cx, 3), round(cy, 3)],
                "centroid_normalized": [round(cx / float(width), 6), round(cy / float(height), 6)],
                "pixels": len(pixels),
                "coverage": len(pixels) / float(width * height),
                "mean_response_luma": mean_response,
                "max_response_luma": max_response,
                "mean_target_gap_luma": mean_diff,
                "suggested_control": suggested_control(kind, mean_response, max_response),
            })
    components.sort(key=lambda item: (item["pixels"], item["max_response_luma"]), reverse=True)
    for index, component in enumerate(components):
        component["rank"] = index + 1
    return components


def draw_overlay(base_img, components, out_path):
    image = base_img.convert("RGB").copy()
    draw = ImageDraw.Draw(image)
    colors = {
        "surface_highlight_response": (255, 230, 80),
        "crest_band_response": (120, 230, 255),
        "water_body_response": (255, 110, 150),
    }
    for component in components:
        color = colors.get(component["kind"], (220, 220, 220))
        x0, y0, x1, y1 = component["bbox"]
        draw.rectangle((x0, y0, x1, y1), outline=color, width=2)
        draw.text((x0 + 4, max(0, y0 - 14)), f"#{component['rank']} {component['kind']}", fill=color)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    image.save(out_path)
    return image


def html_page(title, summary, assets):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Intent GIF"), None)
    overlays = [item for item in assets if item["label"].startswith("Intent Overlay")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Components", checks.get("components")),
            ("Max/frame", checks.get("max_components_per_frame")),
            ("Coverage", f"{checks.get('max_component_coverage', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Intent GIF"></section>' if gif else ""
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
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; }}
    p {{ margin: 0 0 16px; color: var(--muted); }}
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
  <h1>{title}</h1>
  <p>Connected response-mask regions converted into renderer-control intent records.</p>
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
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Components: `{checks.get('components')}`",
        f"- Max components per frame: `{checks.get('max_components_per_frame')}`",
        f"- Max component coverage: `{checks.get('max_component_coverage')}`",
        f"- Min pixels: `{checks.get('min_pixels')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Top Components",
        "",
        "| Frame | Output | Rank | Kind | Pixels | Coverage | Control | BBox |",
        "| ---: | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    rows = []
    for frame in summary.get("frames") or []:
        for component in (frame.get("components") or [])[:3]:
            rows.append((frame, component))
    rows.sort(key=lambda item: item[1].get("pixels", 0), reverse=True)
    for frame, component in rows[:12]:
        control = (component.get("suggested_control") or {}).get("type")
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {component.get('rank')} | "
            f"`{component.get('kind')}` | {component.get('pixels')} | {component.get('coverage')} | "
            f"`{control}` | `{component.get('bbox')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def derive(args):
    require_pillow()
    root = os.getcwd()
    package_path = require_file(args.aov_summary, "visual-cache AOV summary")
    package = read_json(package_path)
    if package.get("schema") != "lsfs_mitsuba_visual_cache_aov_package":
        raise SystemExit(f"{args.aov_summary}: expected lsfs_mitsuba_visual_cache_aov_package schema")

    out_dir = os.path.abspath(args.out_dir)
    overlay_dir = os.path.join(out_dir, "overlays")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(overlay_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    frames = []
    overlay_paths = []
    missing = []
    for index, frame in enumerate(package.get("frames") or []):
        paths = {
            name: resolve_path(aov_path(frame, name), root)
            for name in ("base_rgb", "response_mask", "response_luma", "target_gap_diff")
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        base = Image.open(paths["base_rgb"]).convert("RGB")
        mask = Image.open(paths["response_mask"]).convert("L")
        response = Image.open(paths["response_luma"]).convert("L")
        diff = Image.open(paths["target_gap_diff"]).convert("RGB")
        components = connected_components(mask, response, diff, args)
        overlay_path = os.path.join(overlay_dir, f"frame_{index:04d}_response_intent.png")
        draw_overlay(base, components, overlay_path)
        overlay_paths.append(overlay_path)
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "applied_requests": frame.get("applied_requests"),
            "component_count": len(components),
            "components": components[:args.max_components_per_frame],
            "overlay_repo_path": posix_rel(overlay_path, root),
        })

    if not frames:
        raise SystemExit("no response intent frames were derived")
    gif_path = os.path.join(out_dir, "response_intent.gif")
    gif_images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in overlay_paths]
    gif_images[0].save(gif_path, save_all=True, append_images=gif_images[1:], duration=int(1000 / args.fps), loop=0)

    key_indices = sorted(set([0, len(overlay_paths) // 2, len(overlay_paths) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "response_intent.gif", "Intent GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(overlay_paths[frame_index], assets_dir, f"intent_overlay_{out_index:02d}.png", f"Intent Overlay {out_index + 1}", root))
    status = "ready" if not missing else "failed"
    all_components = [component for frame in frames for component in frame.get("components") or []]
    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_visual_cache_response_intent",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "visual_cache_aov_package": {
            "path": package_path,
            "repo_path": posix_rel(package_path, root),
            "sha256": sha256_file(package_path),
            "schema": package.get("schema"),
            "status": package.get("status"),
        },
        "checks": {
            "frames": len(frames),
            "components": len(all_components),
            "max_components_per_frame": max((frame.get("component_count", 0) for frame in frames), default=0),
            "max_component_coverage": max((component.get("coverage", 0.0) for component in all_components), default=0.0),
            "min_pixels": args.min_pixels,
            "missing_references": len(missing),
            "gif_bytes": os.path.getsize(gif_path),
        },
        "frames": frames,
        "missing_references": missing,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_visual_cache_response_intent_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={len(frames)} components={len(all_components)} "
        f"max_components={summary['checks']['max_components_per_frame']} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Derive visual-cache response intent")
    parser.add_argument("aov_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--min-pixels", type=int, default=32)
    parser.add_argument("--max-components-per-frame", type=int, default=16)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--title", default="Mitsuba Visual Cache Response Intent")
    parser.add_argument(
        "--next",
        default="Use these intent regions to fit renderer-native material, light, or volume controls against the S473 AOV import gate.",
    )
    args = parser.parse_args(argv)
    if args.min_pixels <= 0:
        parser.error("min-pixels must be positive")
    if args.max_components_per_frame <= 0:
        parser.error("max-components-per-frame must be positive")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    derive(args)


if __name__ == "__main__":
    main()
