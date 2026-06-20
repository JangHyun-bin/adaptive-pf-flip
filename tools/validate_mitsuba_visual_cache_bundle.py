#!/usr/bin/env python
"""Validate that a Mitsuba visual-cache bundle can reconstruct composites."""

import argparse
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


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to validate visual cache bundles")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def reference_path(frame, role):
    ref = ((frame.get("references") or {}).get(role) or {})
    return ref.get("path") or ref.get("repo_path") or ref.get("source_repo_path")


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


def reconstruct(base_img, layer_img):
    base = base_img.convert("RGB").tobytes()
    layer = layer_img.convert("RGBA").tobytes()
    out = bytearray()
    for index in range(0, len(base), 3):
        layer_index = (index // 3) * 4
        br, bg, bb = base[index], base[index + 1], base[index + 2]
        lr, lg, lb = layer[layer_index], layer[layer_index + 1], layer[layer_index + 2]
        out.extend((min(255, br + lr), min(255, bg + lg), min(255, bb + lb)))
    return Image.frombytes("RGB", base_img.size, bytes(out))


def diff_stats(actual_img, expected_img):
    actual = actual_img.convert("RGB").tobytes()
    expected = expected_img.convert("RGB").tobytes()
    if len(actual) != len(expected):
        raise ValueError("image byte sizes differ")
    total_abs = 0
    max_abs = 0
    mismatched_pixels = 0
    diff_bytes = bytearray()
    for index in range(0, len(actual), 3):
        dr = abs(actual[index] - expected[index])
        dg = abs(actual[index + 1] - expected[index + 1])
        db = abs(actual[index + 2] - expected[index + 2])
        pixel_max = max(dr, dg, db)
        if pixel_max:
            mismatched_pixels += 1
        total_abs += dr + dg + db
        max_abs = max(max_abs, pixel_max)
        diff_bytes.extend((min(255, dr * 8), min(255, dg * 8), min(255, db * 8)))
    pixels = max(1, len(actual) // 3)
    return {
        "mean_abs_diff": total_abs / float(max(1, len(actual))),
        "max_abs_diff": max_abs,
        "mismatched_pixels": mismatched_pixels,
        "mismatched_coverage": mismatched_pixels / float(pixels),
        "diff_image": Image.frombytes("RGB", actual_img.size, bytes(diff_bytes)),
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
    return strip


def html_page(title, summary, assets):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Validation GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Validation Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Max diff", checks.get("max_abs_diff")),
            ("Mean diff", f"{checks.get('max_mean_abs_diff', 0.0):.6f}"),
            ("Mismatch", f"{checks.get('max_mismatched_coverage', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Validation GIF"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #101b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
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
  <p>Reconstructs each composite from base render plus signed response layer, then compares against the bundled composite.</p>
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
        f"- Max absolute diff: `{checks.get('max_abs_diff')}`",
        f"- Max mean absolute diff: `{checks.get('max_mean_abs_diff')}`",
        f"- Max mismatched coverage: `{checks.get('max_mismatched_coverage')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Mean Diff | Max Diff | Mismatch | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('mean_abs_diff')} | "
            f"{frame.get('max_abs_diff')} | {frame.get('mismatched_coverage')} | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def validate(args):
    require_pillow()
    root = os.getcwd()
    bundle_path = require_file(args.bundle_manifest, "visual cache bundle manifest")
    bundle = read_json(bundle_path)
    if bundle.get("schema") != "lsfs_mitsuba_visual_cache_bundle":
        raise SystemExit(f"{args.bundle_manifest}: expected lsfs_mitsuba_visual_cache_bundle schema")

    out_dir = os.path.abspath(args.out_dir)
    reconstructed_dir = os.path.join(out_dir, "reconstructed")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    frames = []
    missing = []
    strips = []
    for index, frame in enumerate(bundle.get("frames") or []):
        paths = {
            role: resolve_path(reference_path(frame, role), root)
            for role in ("base_render", "signed_response_layer", "signed_composite")
        }
        absent = [role for role, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        base = Image.open(paths["base_render"]).convert("RGB")
        layer = Image.open(paths["signed_response_layer"]).convert("RGBA")
        expected = Image.open(paths["signed_composite"]).convert("RGB")
        if base.size != layer.size or base.size != expected.size:
            raise SystemExit(f"frame {index}: base/layer/composite dimensions differ")
        actual = reconstruct(base, layer)
        stats = diff_stats(actual, expected)
        reconstructed_path = os.path.join(reconstructed_dir, f"frame_{index:04d}.png")
        os.makedirs(os.path.dirname(reconstructed_path), exist_ok=True)
        actual.save(reconstructed_path)
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        layer_visual = Image.new("RGB", layer.size, (0, 0, 0))
        layer_visual.paste(layer.convert("RGB"), mask=layer.getchannel("A"))
        labeled_strip(
            [base, layer_visual, actual, expected, stats["diff_image"]],
            ["base", "layer", "reconstructed", "expected", "diff x8"],
            strip_path,
        )
        strips.append(strip_path)
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "mean_abs_diff": stats["mean_abs_diff"],
            "max_abs_diff": stats["max_abs_diff"],
            "mismatched_pixels": stats["mismatched_pixels"],
            "mismatched_coverage": stats["mismatched_coverage"],
            "reconstructed_repo_path": posix_rel(reconstructed_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
        })

    gif_path = os.path.join(out_dir, "visual_cache_validation.gif")
    if strips:
        strip_images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in strips]
        strip_images[0].save(gif_path, save_all=True, append_images=strip_images[1:], duration=int(1000 / args.fps), loop=0)
    else:
        raise SystemExit("no frames were validated")

    status = "passed"
    if missing:
        status = "failed"
    if max(frame["max_abs_diff"] for frame in frames) > args.max_abs_tolerance:
        status = "failed"
    if max(frame["mean_abs_diff"] for frame in frames) > args.mean_abs_tolerance:
        status = "failed"

    key_indices = sorted(set([0, len(strips) // 2, len(strips) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "visual_cache_validation.gif", "Validation GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"validation_strip_{out_index:02d}.png", f"Validation Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_visual_cache_bundle_validation",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "sha256": sha256_file(bundle_path),
            "schema": bundle.get("schema"),
            "status": bundle.get("status"),
        },
        "checks": {
            "frames": len(frames),
            "missing_references": len(missing),
            "max_abs_diff": max(frame["max_abs_diff"] for frame in frames),
            "max_mean_abs_diff": max(frame["mean_abs_diff"] for frame in frames),
            "max_mismatched_coverage": max(frame["mismatched_coverage"] for frame in frames),
            "gif_bytes": os.path.getsize(gif_path),
            "max_abs_tolerance": args.max_abs_tolerance,
            "mean_abs_tolerance": args.mean_abs_tolerance,
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
        "schema": "lsfs_mitsuba_visual_cache_bundle_validation_gallery",
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
        f"status={status} frames={len(frames)} max_abs={summary['checks']['max_abs_diff']} "
        f"max_mean={summary['checks']['max_mean_abs_diff']:.8f} summary={summary_path}"
    )
    if status != "passed":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a Mitsuba visual-cache bundle")
    parser.add_argument("bundle_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="Mitsuba Visual Cache Bundle Validation")
    parser.add_argument(
        "--next",
        default="Use this consumer validation as the gate before moving signed response layers into renderer-native AOV or compositor tooling.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    validate(args)


if __name__ == "__main__":
    main()
