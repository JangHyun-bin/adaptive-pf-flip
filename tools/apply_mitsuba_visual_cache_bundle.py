#!/usr/bin/env python
"""Apply a Mitsuba visual-cache bundle into a composite summary."""

import argparse
import os
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
from validate_mitsuba_visual_cache_bundle import (
    labeled_strip,
    reconstruct,
    reference_path,
    require_pillow,
    resolve_path,
)


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


def html_page(title, summary, assets):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Consumer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Consumer Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Applied", checks.get("applied_frames")),
            ("Requests", checks.get("applied_requests")),
            ("Coverage", f"{checks.get('max_changed_coverage', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Consumer GIF"></section>' if gif else ""
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
  <p>Consumes the promoted visual-cache bundle and emits a standard secondary composite summary.</p>
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
        f"- Applied frames: `{checks.get('applied_frames')}`",
        f"- Applied requests: `{checks.get('applied_requests')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Max layer delta: `{checks.get('max_layer_delta')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Requests | Composite | Strip |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('applied_requests')} | "
            f"`{frame.get('composite_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def apply_bundle(args):
    require_pillow()
    root = os.getcwd()
    bundle_path = require_file(args.bundle_manifest, "visual cache bundle manifest")
    bundle = read_json(bundle_path)
    if bundle.get("schema") != "lsfs_mitsuba_visual_cache_bundle":
        raise SystemExit(f"{args.bundle_manifest}: expected lsfs_mitsuba_visual_cache_bundle schema")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    strip_dir = os.path.join(out_dir, "strips")
    frames = []
    missing = []
    strips = []
    for index, frame in enumerate(bundle.get("frames") or []):
        base_path = resolve_path(reference_path(frame, "base_render"), root)
        layer_path = resolve_path(reference_path(frame, "signed_response_layer"), root)
        target_path = resolve_path(reference_path(frame, "accepted_target"), root)
        absent = [
            role
            for role, path in (
                ("base_render", base_path),
                ("signed_response_layer", layer_path),
                ("accepted_target", target_path),
            )
            if not path or not os.path.isfile(path)
        ]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        base = Image.open(base_path).convert("RGB")
        layer = Image.open(layer_path).convert("RGBA")
        target = Image.open(target_path).convert("RGB")
        if base.size != layer.size:
            raise SystemExit(f"frame {index}: base and signed response layer dimensions differ")
        composite = reconstruct(base, layer)
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        os.makedirs(os.path.dirname(composite_path), exist_ok=True)
        composite.save(composite_path)
        layer_visual = Image.new("RGB", layer.size, (0, 0, 0))
        layer_visual.paste(layer.convert("RGB"), mask=layer.getchannel("A"))
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        labeled_strip([base, layer_visual, composite, target], ["base", "layer", "composite", "target"], strip_path)
        strips.append(strip_path)
        response = frame.get("response") or {}
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "source_repo_path": posix_rel(base_path, root),
            "layer_repo_path": posix_rel(layer_path, root),
            "target_repo_path": posix_rel(target_path, root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "applied_requests": frame.get("applied_requests"),
            "response": response,
        })

    if not frames:
        raise SystemExit("no frames were consumed")
    gif_path = os.path.join(out_dir, "visual_cache_consumer.gif")
    strip_images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in strips]
    strip_images[0].save(gif_path, save_all=True, append_images=strip_images[1:], duration=int(1000 / args.fps), loop=0)

    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    key_indices = sorted(set([0, len(strips) // 2, len(strips) - 1]))
    assets = [copy_asset(gif_path, assets_dir, "visual_cache_consumer.gif", "Consumer GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"consumer_strip_{out_index:02d}.png", f"Consumer Strip {out_index + 1}", root))

    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    status = "ready" if not missing else "failed"
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_visual_cache_bundle_consumer",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "visual_cache_bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "sha256": sha256_file(bundle_path),
            "schema": bundle.get("schema"),
            "status": bundle.get("status"),
            "profile": bundle.get("profile"),
        },
        "checks": {
            "frames": len(frames),
            "applied_frames": sum(1 for frame in frames if frame.get("applied_requests")),
            "applied_requests": sum(int(frame.get("applied_requests") or 0) for frame in frames),
            "missing_references": len(missing),
            "composite_bytes": sum(frame["size"] for frame in frames),
            "gif_bytes": os.path.getsize(gif_path),
            "max_changed_coverage": max((frame.get("response") or {}).get("changed_coverage", 0.0) for frame in frames),
            "max_layer_delta": max((frame.get("response") or {}).get("max_layer_delta", 0) for frame in frames),
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
        "schema": "lsfs_mitsuba_visual_cache_bundle_consumer_gallery",
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
        f"status={status} frames={len(frames)} requests={summary['checks']['applied_requests']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply a Mitsuba visual-cache bundle")
    parser.add_argument("bundle_manifest")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--title", default="Mitsuba Visual Cache Bundle Consumer")
    parser.add_argument(
        "--next",
        default="Run the target-gap harness against this consumer summary before promoting it as the command-line composite path.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    apply_bundle(args)


if __name__ == "__main__":
    main()
