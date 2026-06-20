#!/usr/bin/env python
"""Build a self-contained publish gallery from a runtime import preview."""

import argparse
import html
import os
import shutil
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


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def copy_asset(src, dest, label, role, root):
    source = require_file(src, label)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(source) != os.path.abspath(dest):
        shutil.copy2(source, dest)
    entry = {
        "label": label,
        "role": role,
        "source_repo_path": posix_rel(source, root),
        "repo_path": posix_rel(dest, root),
        "href": os.path.relpath(dest, os.path.dirname(os.path.dirname(dest))).replace(os.sep, "/"),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def asset_path(item, root):
    return resolve_path((item or {}).get("repo_path") or (item or {}).get("path"), root)


def select_frames(frames, limit):
    if limit <= 0 or len(frames) <= limit:
        return list(enumerate(frames))
    return [
        (round(index * (len(frames) - 1) / float(max(1, limit - 1))), frames[round(index * (len(frames) - 1) / float(max(1, limit - 1)))])
        for index in range(limit)
    ]


def image_tile(label, item):
    href = item.get("href")
    dims = item.get("dimensions")
    dims_text = f"{dims[0]} x {dims[1]}" if dims else "n/a"
    if not href:
        return f"<figure><figcaption>{html.escape(label)} missing</figcaption></figure>"
    return (
        f'<figure><a href="{html.escape(href)}"><img src="{html.escape(href)}" '
        f'alt="{html.escape(label)}"></a><figcaption>{html.escape(label)} - {html.escape(dims_text)}</figcaption></figure>'
    )


def html_page(title, gallery):
    checks = gallery.get("checks") or {}
    shot = next((item for item in gallery.get("assets") or [] if item.get("label") == "Shot GIF"), {})
    metrics = [
        ("Status", gallery.get("status")),
        ("Frames", checks.get("source_frames")),
        ("Published", checks.get("published_frames")),
        ("Assets", checks.get("assets")),
        ("Missing", checks.get("missing_assets")),
        ("Source leaks", checks.get("external_href_violations")),
    ]
    metric_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metrics
    )
    hero = ""
    if shot.get("href"):
        hero = f'<section class="hero"><img src="{html.escape(shot["href"])}" alt="Low-frequency WebGL proof GIF"></section>'
    frame_sections = []
    for frame in gallery.get("frames") or []:
        assets = frame.get("assets") or {}
        frame_sections.append(f"""
        <section class="frame">
          <header>
            <h2>Frame {html.escape(str(frame.get('frame')))} / output {html.escape(str(frame.get('output_frame')))}</h2>
            <span>proof diff {html.escape(str(frame.get('proof_max_abs_diff')))}</span>
          </header>
          <div class="grid">
            {image_tile('Base', assets.get('base_rgb') or {})}
            {image_tile('Oracle', assets.get('oracle') or {})}
            {image_tile('WebGL', assets.get('webgl_frame') or {})}
            {image_tile('Proof Strip', assets.get('proof_strip') or {})}
          </div>
        </section>""")
    metadata_links = "\n".join(
        f'<a href="{html.escape(item["href"])}">{html.escape(item["label"])}</a>'
        for item in gallery.get("metadata_files") or []
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #070b0f; --panel: #111920; --line: #2b3740; --ink: #edf7fb; --muted: #9cabb4; --accent: #82d9ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 22px 18px 44px; }}
    header.top {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; font-size: 13px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #0b1115; margin-bottom: 14px; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div, .frame {{ border: 1px solid var(--line); background: var(--panel); }}
    .metrics div {{ padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
    .frame {{ margin-top: 14px; }}
    .frame header {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 12px; border-bottom: 1px solid var(--line); }}
    h2 {{ margin: 0; font-size: 16px; font-weight: 650; letter-spacing: 0; }}
    .frame header span {{ color: var(--accent); font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1px; background: var(--line); }}
    figure {{ margin: 0; background: #0d1318; min-width: 0; }}
    figure img {{ width: 100%; aspect-ratio: 16 / 9; object-fit: contain; display: block; background: #020304; }}
    figcaption {{ padding: 7px 9px; color: var(--muted); font-size: 12px; }}
  </style>
</head>
<body>
  <main>
    <header class="top">
      <h1>{html.escape(title)}</h1>
      <nav>{metadata_links}</nav>
    </header>
    {hero}
    <section class="metrics">{metric_html}</section>
    {''.join(frame_sections)}
  </main>
</body>
</html>
"""


def markdown_report(gallery, manifest_path, root):
    checks = gallery.get("checks") or {}
    lines = [
        f"# {gallery['title']}",
        "",
        f"Generated UTC: `{gallery['generated_utc']}`",
        f"Gallery directory: `{gallery['gallery_repo_path']}`",
        f"Manifest: `{posix_rel(manifest_path, root)}`",
        f"Index HTML: `{gallery['index']['repo_path']}`",
        f"Status: `{gallery['status']}`",
        "",
        "## Checks",
        "",
        f"- Source frames: `{checks.get('source_frames')}`",
        f"- Published frames: `{checks.get('published_frames')}`",
        f"- Assets: `{checks.get('assets')}`",
        f"- Missing assets: `{checks.get('missing_assets')}`",
        f"- External href violations: `{checks.get('external_href_violations')}`",
        "",
        "## Assets",
        "",
        "| Asset | Role | Size | Dimensions | Path |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for item in gallery.get("assets") or []:
        dims = item.get("dimensions")
        dims_text = f"{dims[0]} x {dims[1]}" if dims else "n/a"
        lines.append(f"| {item.get('label')} | `{item.get('role')}` | {format_bytes(item.get('size', 0))} | `{dims_text}` | `{item.get('repo_path')}` |")
    lines.extend(["", "## Metadata Files", ""])
    for item in gallery.get("metadata_files") or []:
        lines.append(f"- `{item.get('repo_path')}` ({format_bytes(item.get('size', 0))})")
    lines.extend(["", "## Next", "", gallery.get("next") or "Publish this gallery through the static preview tunnel.", ""])
    return "\n".join(lines)


def build_gallery(args):
    root = os.getcwd()
    preview_path = require_file(resolve_path(args.preview, root), "runtime import preview")
    preview = read_json(preview_path)
    if preview.get("schema") != "lsfs_mitsuba_low_frequency_runtime_import_preview":
        raise SystemExit(f"{args.preview}: expected lsfs_mitsuba_low_frequency_runtime_import_preview schema")
    if preview.get("status") != "ready":
        raise SystemExit(f"{args.preview}: preview status is {preview.get('status')!r}")
    out_dir = os.path.abspath(args.out_dir)
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    assets = []
    metadata_files = []
    missing = []
    runtime = preview.get("runtime_assets") or {}
    shot_source = asset_path(runtime.get("webgl_proof_gif") or {}, root)
    if shot_source and os.path.isfile(shot_source):
        assets.append(copy_asset(shot_source, os.path.join(assets_dir, "shot.gif"), "Shot GIF", "proof_gif", root))
    else:
        missing.append({"role": "shot_gif", "path": shot_source})
    metadata_files.append(copy_asset(preview_path, os.path.join(assets_dir, "runtime_import_preview.json"), "Runtime Import Preview", "metadata", root))
    source_bundle = preview.get("source_bundle") or {}
    bundle_path = asset_path(source_bundle, root)
    if bundle_path and os.path.isfile(bundle_path):
        metadata_files.append(copy_asset(bundle_path, os.path.join(assets_dir, "runtime_handoff_bundle.json"), "Runtime Handoff Bundle", "metadata", root))
    else:
        missing.append({"role": "runtime_handoff_bundle", "path": bundle_path})
    frames = []
    selected = select_frames(preview.get("frames") or [], args.max_frames)
    for selected_index, frame in selected:
        frame_assets = {}
        copy_plan = [
            ("base_rgb", ((frame.get("runtime_bindings") or {}).get("base_rgb") or {}), "base_rgb"),
            ("oracle", frame.get("oracle") or {}, "oracle"),
            ("webgl_frame", ((frame.get("proof") or {}).get("webgl_frame") or {}), "webgl_frame"),
            ("proof_strip", ((frame.get("proof") or {}).get("proof_strip") or {}), "proof_strip"),
        ]
        for key, item, role in copy_plan:
            source = asset_path(item, root)
            if not source or not os.path.isfile(source):
                missing.append({"frame": frame.get("frame"), "role": role, "path": source})
                continue
            ext = os.path.splitext(source)[1] or ".png"
            dest = os.path.join(assets_dir, f"frame_{selected_index:04d}_{key}{ext}")
            entry = copy_asset(source, dest, f"Frame {selected_index:04d} {key}", role, root)
            assets.append(entry)
            frame_assets[key] = entry
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "proof_max_abs_diff": (frame.get("proof") or {}).get("max_abs_diff"),
            "assets": frame_assets,
        })
    index_path = os.path.join(out_dir, "index.html")
    manifest_path = os.path.abspath(args.manifest)
    external_href_violations = 0
    for item in assets + metadata_files:
        href = item.get("href") or ""
        if href.startswith("../") or "://" in href:
            external_href_violations += 1
    gallery = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_publish_gallery",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": "ready" if not missing and external_href_violations == 0 else "review",
        "gallery_path": out_dir,
        "gallery_repo_path": posix_rel(out_dir, root),
        "index": {
            "path": index_path,
            "repo_path": posix_rel(index_path, root),
            "href": "index.html",
        },
        "source_preview": {
            "path": preview_path,
            "repo_path": posix_rel(preview_path, root),
            "schema": preview.get("schema"),
            "status": preview.get("status"),
            "sha256": sha256_file(preview_path),
            "size": os.path.getsize(preview_path),
        },
        "assets": assets,
        "metadata_files": metadata_files,
        "frames": frames,
        "checks": {
            "source_frames": len(preview.get("frames") or []),
            "published_frames": len(frames),
            "assets": len(assets),
            "metadata_files": len(metadata_files),
            "missing_assets": len(missing),
            "external_href_violations": external_href_violations,
        },
        "missing_assets": missing,
        "next": args.next,
    }
    write_text(index_path, html_page(args.title, gallery))
    gallery["index"]["sha256"] = sha256_file(index_path)
    gallery["index"]["size"] = os.path.getsize(index_path)
    write_json(manifest_path, gallery)
    if args.report:
        write_text(args.report, markdown_report(gallery, manifest_path, root))
    print(
        f"status={gallery['status']} frames={len(frames)} assets={len(assets)} "
        f"missing={len(missing)} gallery={out_dir}"
    )
    if gallery["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a self-contained runtime publish gallery")
    parser.add_argument("preview")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S496 Mitsuba Low Frequency Runtime Publish Gallery")
    parser.add_argument("--max-frames", type=int, default=8)
    parser.add_argument("--next", default="Publish this gallery through a verified static preview tunnel.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    build_gallery(args)


if __name__ == "__main__":
    main()
