#!/usr/bin/env python
"""Build a renderer-neutral light-response contract from source-highlight masks."""

import argparse
import html
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a light-response contract")


def resolve_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def layer_path(frame):
    return frame.get("layer_path") or frame.get("layer_repo_path")


def source_path(frame):
    return frame.get("source_path") or frame.get("source_repo_path") or frame.get("composite_repo_path")


def luma(pixel):
    r, g, b = pixel[:3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def connected_components(mask, min_pixels):
    width, height = mask.size
    pix = mask.load()
    visited = bytearray(width * height)
    components = []
    for y in range(height):
        row = y * width
        for x in range(width):
            index = row + x
            if visited[index] or pix[x, y] == 0:
                continue
            visited[index] = 1
            queue = deque([(x, y)])
            pixels = []
            min_x = max_x = x
            min_y = max_y = y
            while queue:
                cx, cy = queue.popleft()
                value = int(pix[cx, cy])
                pixels.append((cx, cy, value))
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    ni = ny * width + nx
                    if visited[ni] or pix[nx, ny] == 0:
                        continue
                    visited[ni] = 1
                    queue.append((nx, ny))
            if len(pixels) >= min_pixels:
                components.append({
                    "pixels": pixels,
                    "bbox": [min_x, min_y, max_x, max_y],
                })
    components.sort(key=lambda item: len(item["pixels"]), reverse=True)
    return components


def threshold_alpha(alpha, threshold):
    return alpha.point(lambda value: value if value >= threshold else 0)


def component_anchor(component, source, width, height):
    pixels = component["pixels"]
    weight_sum = sum(max(1, value) for _x, _y, value in pixels)
    cx = sum(x * max(1, value) for x, _y, value in pixels) / float(weight_sum)
    cy = sum(y * max(1, value) for _x, y, value in pixels) / float(weight_sum)
    lumas = []
    max_luma = 0.0
    for x, y, _value in pixels:
        lum = luma(source.getpixel((x, y)))
        lumas.append(lum)
        max_luma = max(max_luma, lum)
    bbox = component["bbox"]
    pixel_count = len(pixels)
    return {
        "pixel_count": pixel_count,
        "coverage": pixel_count / float(max(1, width * height)),
        "centroid_px": [cx, cy],
        "centroid_uv": [cx / float(max(1, width - 1)), cy / float(max(1, height - 1))],
        "bbox_px": bbox,
        "bbox_uv": [
            bbox[0] / float(max(1, width - 1)),
            bbox[1] / float(max(1, height - 1)),
            bbox[2] / float(max(1, width - 1)),
            bbox[3] / float(max(1, height - 1)),
        ],
        "alpha_mean": sum(value for _x, _y, value in pixels) / float(pixel_count),
        "alpha_max": max(value for _x, _y, value in pixels),
        "source_luma_mean": sum(lumas) / float(max(1, len(lumas))),
        "source_luma_max": max_luma,
        "suggested_response": {
            "kind": "bounded_light_response",
            "weight": min(1.0, pixel_count / 2200.0),
            "luma_scale": max_luma / 255.0,
        },
    }


def draw_overlay(source, mask, anchors, out_path):
    overlay = source.convert("RGBA")
    tint = Image.new("RGBA", overlay.size, (92, 182, 255, 0))
    tint.putalpha(mask.point(lambda value: min(180, int(value * 0.7))))
    overlay = Image.alpha_composite(overlay, tint)
    draw = ImageDraw.Draw(overlay)
    for index, anchor in enumerate(anchors, start=1):
        x0, y0, x1, y1 = anchor["bbox_px"]
        cx, cy = anchor["centroid_px"]
        color = (255, 215, 92, 255)
        draw.rectangle([x0, y0, x1, y1], outline=color, width=2)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(255, 96, 72, 255), width=2)
        draw.text((x0 + 4, max(0, y0 - 14)), f"L{index}", fill=color)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    overlay.convert("RGB").save(out_path)


def make_gallery(out_dir, title, overlays, root):
    gallery_dir = os.path.join(out_dir, "gallery")
    asset_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(asset_dir, exist_ok=True)
    assets = []
    for index, src in enumerate(overlays):
        dest = os.path.join(asset_dir, f"frame_{index:04d}_light_response_overlay.png")
        if os.path.abspath(src) != os.path.abspath(dest):
            Image.open(src).save(dest)
        entry = {
            "label": f"Frame {index + 1} Overlay",
            "path": dest,
            "repo_path": posix_rel(dest, root),
            "href": "assets/" + os.path.basename(dest),
            "size": os.path.getsize(dest),
            "sha256": sha256_file(dest),
        }
        dims = image_dimensions(dest)
        if dims:
            entry["dimensions"] = dims
        assets.append(entry)
    figures = "\n".join(
        f'<figure><a href="{html.escape(item["href"])}"><img src="{html.escape(item["href"])}"></a>'
        f'<figcaption>{html.escape(item["label"])}</figcaption></figure>'
        for item in assets
    )
    index_path = os.path.join(gallery_dir, "index.html")
    write_text(index_path, f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071014; --panel: #101b22; --ink: #edf7fb; --muted: #9fb2bc; --line: #2c3a44; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ font-size: 26px; margin: 0 0 18px; letter-spacing: 0; }}
    figure {{ margin: 0 0 14px; border: 1px solid var(--line); background: var(--panel); }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body><main><h1>{html.escape(title)}</h1>{figures}</main></body>
</html>
""")
    manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    manifest = {
        "schema": "lsfs_mitsuba_light_response_contract_gallery",
        "version": 1,
        "title": title,
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
    }
    write_json(manifest_path, manifest)
    return {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "manifest_path": manifest_path,
        "manifest_repo_path": posix_rel(manifest_path, root),
        "assets": assets,
    }


def source_entry(path, root, label, payload=None):
    entry = {
        "label": label,
        "path": os.path.abspath(path),
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if payload:
        entry["schema"] = payload.get("schema")
        entry["version"] = payload.get("version")
    return entry


def markdown_report(contract, contract_path, root, next_text):
    checks = contract.get("checks") or {}
    lines = [
        f"# {contract['title']}",
        "",
        f"Generated UTC: `{contract['generated_utc']}`",
        f"Contract JSON: `{posix_rel(contract_path, root)}`",
        f"Gallery: `{contract['gallery']['index_repo_path']}`",
        f"Status: `{contract['status']}`",
        "",
        "## Inputs",
        "",
        f"- Mask source: `{contract['sources']['mask_source']['repo_path']}`",
        f"- Mask kind: `{contract.get('mask_kind')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Anchors: `{checks.get('anchors')}`",
        f"- Max anchors per frame: `{checks.get('max_anchors_per_frame')}`",
        f"- Mean mask coverage: `{checks.get('mean_mask_coverage')}`",
        f"- Max mask coverage: `{checks.get('max_mask_coverage')}`",
        f"- Overlay bytes: `{format_bytes(checks.get('overlay_bytes', 0))}`",
        "",
        "## Frame Anchors",
        "",
        "| Output | Coverage | Anchors | Largest Anchor | Mean Luma | Overlay |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for frame in contract.get("frames") or []:
        anchors = frame.get("anchors") or []
        largest = anchors[0] if anchors else {}
        mean_luma = (
            sum(anchor.get("source_luma_mean", 0.0) for anchor in anchors) / float(len(anchors))
            if anchors else 0.0
        )
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('mask_coverage')} | {len(anchors)} | "
            f"{largest.get('coverage', 0.0)} | {mean_luma:.6f} | `{frame.get('overlay_repo_path')}` |"
        )
    lines.extend(["", "## Decision Use", ""])
    lines.extend([
        "This contract is renderer-neutral. It does not apply a post-composite grade,",
        "does not add a screen card, and does not mutate the water mesh. It packages",
        "the nonsecondary highlight evidence as bounded per-frame light-response",
        "anchors that a renderer backend can consume as area lights, caustic/glint",
        "controls, or volume-light metadata.",
    ])
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    mask_source_path = require_file(args.mask_source, "mask source")
    mask_source = read_json(mask_source_path)
    if mask_source.get("schema") != "lsfs_mitsuba_source_response_mask_source":
        raise SystemExit(f"{args.mask_source}: expected lsfs_mitsuba_source_response_mask_source schema")
    if mask_source.get("status") != "ready":
        raise SystemExit(f"{args.mask_source}: mask source status is {mask_source.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    overlay_dir = os.path.join(out_dir, "overlays")
    os.makedirs(overlay_dir, exist_ok=True)
    frames = []
    overlays = []
    total_anchors = 0
    total_coverage = 0.0
    max_coverage = 0.0
    for index, frame in enumerate(mask_source.get("frames") or []):
        mask_path = require_file(resolve_path(layer_path(frame)), "mask layer")
        src_path = require_file(resolve_path(source_path(frame)), "source image")
        mask_rgba = Image.open(mask_path).convert("RGBA")
        alpha = threshold_alpha(mask_rgba.getchannel("A"), args.alpha_threshold)
        source = Image.open(src_path).convert("RGB")
        if alpha.size != source.size:
            raise SystemExit(f"{mask_path}: mask/source image size mismatch")
        width, height = alpha.size
        components = connected_components(alpha, args.min_component_pixels)
        anchors = [
            component_anchor(component, source, width, height)
            for component in components[:args.max_anchors]
        ]
        histogram = alpha.histogram()
        coverage = (width * height - histogram[0]) / float(max(1, width * height))
        overlay_path = os.path.join(overlay_dir, f"frame_{index:04d}_light_response_overlay.png")
        draw_overlay(source, alpha, anchors, overlay_path)
        overlays.append(overlay_path)
        total_anchors += len(anchors)
        total_coverage += coverage
        max_coverage = max(max_coverage, coverage)
        frames.append({
            "frame": index,
            "output_frame": frame.get("output_frame"),
            "mask_layer_repo_path": posix_rel(mask_path, root),
            "source_repo_path": posix_rel(src_path, root),
            "overlay_path": overlay_path,
            "overlay_repo_path": posix_rel(overlay_path, root),
            "overlay_sha256": sha256_file(overlay_path),
            "overlay_size": os.path.getsize(overlay_path),
            "mask_coverage": coverage,
            "anchors": anchors,
        })

    gallery = make_gallery(out_dir, args.title, overlays, root)
    status = "ready" if frames and total_anchors > 0 else "review"
    contract = {
        "schema": "lsfs_mitsuba_light_response_contract",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "sources": {
            "mask_source": source_entry(mask_source_path, root, "source highlight mask source", mask_source),
        },
        "mask_kind": mask_source.get("mask_kind"),
        "settings": {
            "alpha_threshold": args.alpha_threshold,
            "min_component_pixels": args.min_component_pixels,
            "max_anchors": args.max_anchors,
        },
        "checks": {
            "frames": len(frames),
            "anchors": total_anchors,
            "max_anchors_per_frame": max((len(frame.get("anchors") or []) for frame in frames), default=0),
            "mean_mask_coverage": total_coverage / float(max(1, len(frames))),
            "max_mask_coverage": max_coverage,
            "overlay_bytes": sum(frame.get("overlay_size", 0) for frame in frames),
        },
        "frames": frames,
        "gallery": gallery,
        "next": args.next,
    }
    contract_path = os.path.join(out_dir, "light_response_contract.json")
    write_json(contract_path, contract)
    if args.report:
        write_text(args.report, markdown_report(contract, contract_path, root, args.next))
    print(
        f"status={status} frames={len(frames)} anchors={total_anchors} "
        f"contract={contract_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a renderer-neutral light-response contract from source-highlight masks")
    parser.add_argument("mask_source")
    parser.add_argument("out_dir")
    parser.add_argument("--alpha-threshold", type=int, default=8)
    parser.add_argument("--min-component-pixels", type=int, default=12)
    parser.add_argument("--max-anchors", type=int, default=8)
    parser.add_argument("--report")
    parser.add_argument("--title", default="Mitsuba Light Response Contract")
    parser.add_argument("--next", default="Use this contract as renderer-native light/volume response input before another post-composite grade.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    if args.alpha_threshold < 0 or args.alpha_threshold > 255:
        parser.error("alpha-threshold must be in [0, 255]")
    if args.min_component_pixels <= 0:
        parser.error("min-component-pixels must be positive")
    if args.max_anchors <= 0:
        parser.error("max-anchors must be positive")
    build(args)


if __name__ == "__main__":
    main()
