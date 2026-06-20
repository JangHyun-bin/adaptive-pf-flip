#!/usr/bin/env python
"""Package a Mitsuba visual-cache handoff bundle from signed response layers."""

import argparse
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


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".html"}


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def json_source(path, label, root):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    return {
        "label": label,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "schema": payload.get("schema"),
        "subschema": payload.get("subschema"),
        "version": payload.get("version"),
        "status": payload.get("status"),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }, payload


def copy_entry(source, dest, label, role, root):
    resolved = resolve_path(source, root)
    if not resolved or not os.path.isfile(resolved):
        raise FileNotFoundError(source)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(resolved, dest)
    entry = {
        "label": label,
        "role": role,
        "source_path": resolved,
        "source_repo_path": posix_rel(resolved, root),
        "path": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def copy_optional(source, dest, label, role, root, missing, copied):
    resolved = resolve_path(source, root)
    if not resolved or not os.path.isfile(resolved):
        missing.append({"label": label, "role": role, "path": source})
        return {
            "label": label,
            "role": role,
            "status": "missing",
            "source_repo_path": source,
        }
    entry = copy_entry(resolved, dest, label, role, root)
    entry["status"] = "copied"
    copied.append(entry)
    return entry


def output_frame_map(frames):
    result = {}
    for frame in frames or []:
        output = frame.get("output_frame")
        if output is not None:
            result[output] = frame
    return result


def reference_path(reference):
    if not isinstance(reference, dict):
        return None
    return reference.get("repo_path") or reference.get("source_repo_path") or reference.get("path")


def frame_source(base_frame, role):
    if not base_frame:
        return None
    refs = base_frame.get("references") or {}
    return reference_path(refs.get(role))


def copy_metadata_files(sources, root, out_dir):
    copied = []
    metadata_dir = os.path.join(out_dir, "metadata")
    for key, entry in sources.items():
        copied.append(copy_entry(entry["path"], os.path.join(metadata_dir, f"{key}.json"), key, "source_metadata", root))
    return copied


def gallery_source(item):
    return item.get("asset") or item.get("source") or item.get("repo_path") or item.get("path")


def copy_gallery_assets(summary, prefix, root, out_dir):
    assets = []
    gallery_dir = os.path.join(out_dir, "gallery", "assets")
    for index, item in enumerate((summary.get("gallery") or {}).get("assets") or []):
        source = gallery_source(item)
        if not source:
            continue
        ext = os.path.splitext(str(source))[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            continue
        name = f"{prefix}_{index:02d}{ext}"
        label = f"{prefix}:{item.get('label') or os.path.basename(str(source))}"
        entry = copy_entry(source, os.path.join(gallery_dir, name), label, "gallery_asset", root)
        entry["href"] = f"assets/{name}"
        assets.append(entry)
    return assets


def check_expected_hash(checks, root, label, source, expected):
    resolved = resolve_path(source, root)
    if not resolved or not os.path.isfile(resolved):
        checks.append({"name": label, "status": "failed", "detail": "missing source", "path": source})
        return
    actual = sha256_file(resolved)
    checks.append({
        "name": label,
        "status": "passed" if not expected or actual == expected else "failed",
        "detail": "sha256 matched" if not expected or actual == expected else "sha256 mismatch",
        "path": posix_rel(resolved, root),
        "expected": expected,
        "actual": actual,
    })


def build_frames(base_handoff, layer_summary, gap_summary, root, out_dir):
    base_by_output = output_frame_map(base_handoff.get("frames") or [])
    gap_by_output = output_frame_map(gap_summary.get("frames") or [])
    frames = []
    copied = []
    missing = []
    checks = []
    for index, layer_frame in enumerate(layer_summary.get("frames") or []):
        output = layer_frame.get("output_frame")
        base_frame = base_by_output.get(output)
        gap_frame = gap_by_output.get(output)
        references = {}
        frame_dir = os.path.join(out_dir, "frames")
        sources = {
            "base_render": layer_frame.get("source_repo_path"),
            "signed_response_layer": layer_frame.get("layer_repo_path"),
            "signed_composite": layer_frame.get("composite_repo_path"),
            "accepted_target": layer_frame.get("target_repo_path"),
            "target_gap_diff": (gap_frame or {}).get("diff_repo_path"),
            "target_gap_strip": (gap_frame or {}).get("strip_repo_path"),
            "handoff_graded_reference": frame_source(base_frame, "graded"),
            "handoff_secondary_layer": frame_source(base_frame, "secondary_layer"),
        }
        for role, source in sources.items():
            ext = os.path.splitext(str(source or ""))[1] or ".png"
            dest = os.path.join(frame_dir, role, f"frame_{index:04d}{ext}")
            references[role] = copy_optional(source, dest, f"frame_{index:04d}_{role}", role, root, missing, copied)
        if gap_frame:
            check_expected_hash(checks, root, f"frame_{index:04d}:composite", layer_frame.get("composite_repo_path"), gap_frame.get("actual_sha256"))
            check_expected_hash(checks, root, f"frame_{index:04d}:target", layer_frame.get("target_repo_path"), gap_frame.get("target_sha256"))
        else:
            checks.append({
                "name": f"frame_{index:04d}:target_gap",
                "status": "failed",
                "detail": "missing target-gap frame for output frame",
                "actual": output,
            })
        frames.append({
            "frame": layer_frame.get("frame"),
            "output_frame": output,
            "applied_requests": layer_frame.get("applied_requests"),
            "response": layer_frame.get("response") or {},
            "gap": {
                "gap_mean_abs_diff": (gap_frame or {}).get("gap_mean_abs_diff"),
                "gap_max_abs_diff": (gap_frame or {}).get("gap_max_abs_diff"),
            },
            "references": references,
        })
    return frames, copied, missing, checks


def html_page(bundle):
    checks = bundle.get("checks") or {}
    gallery = bundle.get("gallery") or {}
    assets = gallery.get("assets") or []
    gif_cards = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in assets
        if str(item.get("href", "")).lower().endswith(".gif")
    )
    strip_cards = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in assets
        if str(item.get("href", "")).lower().endswith(".png")
    )
    frame_cards = []
    gallery_dir = gallery.get("path") or ""
    frames = bundle.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        strip = ((frame.get("references") or {}).get("target_gap_strip") or {})
        path = strip.get("path")
        if not path:
            continue
        href = os.path.relpath(path, gallery_dir).replace(os.sep, "/")
        frame_cards.append(
            f'<figure><a href="{href}"><img src="{href}" alt="frame {frame.get("frame")} strip"></a>'
            f'<figcaption>frame {frame.get("frame")} / output {frame.get("output_frame")}</figcaption></figure>'
        )
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", bundle.get("status")),
            ("Frames", checks.get("frames")),
            ("Copied", checks.get("copied_files")),
            ("Missing", checks.get("missing_references")),
            ("Mean MAD", f"{checks.get('mean_gap_mean_abs_diff', 0.0):.4f}"),
            ("Max MAD", f"{checks.get('max_gap_mean_abs_diff', 0.0):.4f}"),
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{bundle['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; }}
    h2 {{ margin: 28px 0 12px; font-size: 17px; }}
    p {{ margin: 0 0 16px; color: var(--muted); }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 6px; background: #0d1820; overflow: hidden; }}
    img {{ display: block; width: 100%; height: auto; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
<main>
  <h1>{bundle['title']}</h1>
  <p>Promoted Mitsuba visual-cache bundle: base render, signed response layer, composite frame, accepted target, and target-gap evidence.</p>
  <section class="tiles">{tiles}</section>
  <h2>Gallery Assets</h2>
  <section class="grid">{gif_cards}{strip_cards}</section>
  <h2>Frame Samples</h2>
  <section class="grid">{''.join(frame_cards)}</section>
</main>
</body>
</html>
"""


def markdown_report(bundle, manifest_path, root):
    checks = bundle.get("checks") or {}
    lines = [
        f"# {bundle['title']}",
        "",
        f"Generated UTC: `{bundle['generated_utc']}`",
        f"Bundle JSON: `{posix_rel(manifest_path, root)}`",
        f"Gallery: `{bundle['gallery']['index_repo_path']}`",
        f"Status: `{bundle['status']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Copied files: `{checks.get('copied_files')}`",
        f"- Copied bytes: `{format_bytes(checks.get('copied_bytes', 0))}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Hash failures: `{checks.get('hash_failures')}`",
        f"- Mean target-gap MAD: `{checks.get('mean_gap_mean_abs_diff')}`",
        f"- Max target-gap MAD: `{checks.get('max_gap_mean_abs_diff')}`",
        f"- Max target-gap absolute diff: `{checks.get('max_gap_max_abs_diff')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Max layer delta: `{checks.get('max_layer_delta')}`",
        "",
        "## Sources",
        "",
        "| Source | Schema | Status | Path |",
        "| --- | --- | --- | --- |",
    ]
    for key, source in bundle.get("sources", {}).items():
        lines.append(
            f"| {key} | `{source.get('schema')}` | `{source.get('status')}` | `{source.get('repo_path')}` |"
        )
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Requests | Gap MAD | Layer | Composite | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- | --- |",
    ])
    frames = bundle.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        refs = frame.get("references") or {}
        layer = refs.get("signed_response_layer") or {}
        composite = refs.get("signed_composite") or {}
        strip = refs.get("target_gap_strip") or {}
        gap = frame.get("gap") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('applied_requests')} | "
            f"{gap.get('gap_mean_abs_diff')} | `{layer.get('repo_path')}` | "
            f"`{composite.get('repo_path')}` | `{strip.get('repo_path')}` |"
        )
    if bundle.get("missing_references"):
        lines.extend(["", "## Missing References", ""])
        for item in bundle["missing_references"]:
            lines.append(f"- `{item.get('role')}` {item.get('label')}: `{item.get('path')}`")
    lines.extend(["", "## Next", "", bundle.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    handoff_source, handoff = json_source(args.handoff_manifest, "Mitsuba renderer handoff bundle", root)
    layer_source, layer = json_source(args.signed_response_layer, "signed response layer summary", root)
    gap_source, gap = json_source(args.target_gap_summary, "target-gap summary", root)

    schema_errors = []
    if handoff.get("schema") != "lsfs_mitsuba_renderer_handoff_bundle":
        schema_errors.append("handoff schema")
    if layer.get("schema") != "lsfs_mitsuba_secondary_composite":
        schema_errors.append("signed response layer schema")
    if layer.get("subschema") != "lsfs_mitsuba_signed_response_layer":
        schema_errors.append("signed response layer subschema")
    if gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        schema_errors.append("target-gap schema")

    sources = {
        "base_handoff": handoff_source,
        "signed_response_layer": layer_source,
        "target_gap": gap_source,
    }
    metadata_files = copy_metadata_files(sources, root, out_dir)
    gallery_assets = []
    gallery_assets.extend(copy_gallery_assets(layer, "layer", root, out_dir))
    gallery_assets.extend(copy_gallery_assets(gap, "gap", root, out_dir))
    frames, frame_copies, missing, hash_checks = build_frames(handoff, layer, gap, root, out_dir)
    copied_files = metadata_files + gallery_assets + frame_copies
    hash_failures = sum(1 for item in hash_checks if item.get("status") == "failed")

    layer_checks = layer.get("checks") or {}
    gap_checks = gap.get("checks") or {}
    source_ready = handoff.get("status") == "ready" and layer.get("status") == "ready" and gap.get("status") == "ready"
    status = "ready" if source_ready and not schema_errors and not missing and not hash_failures else "failed"
    gallery_dir = os.path.join(out_dir, "gallery")
    gallery_index = os.path.join(gallery_dir, "index.html")
    manifest_path = os.path.abspath(args.manifest)
    bundle = {
        "schema": "lsfs_mitsuba_visual_cache_bundle",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "profile": args.profile,
        "bundle_root": {
            "path": out_dir,
            "repo_path": posix_rel(out_dir, root),
        },
        "sources": sources,
        "promoted_visual_cache": {
            "base_renderer": "mitsuba",
            "layer_contract": "signed_response_layer",
            "composite_schema": layer.get("schema"),
            "composite_subschema": layer.get("subschema"),
            "target_gap_schema": gap.get("schema"),
        },
        "checks": {
            "frames": len(frames),
            "copied_files": len(copied_files),
            "copied_bytes": sum(item.get("size", 0) for item in copied_files),
            "missing_references": len(missing),
            "hash_checks": len(hash_checks),
            "hash_failures": hash_failures,
            "schema_errors": schema_errors,
            "source_ready": source_ready,
            "selected_requests": layer_checks.get("selected_requests"),
            "applied_requests": layer_checks.get("applied_requests"),
            "max_changed_coverage": layer_checks.get("max_changed_coverage"),
            "max_layer_delta": layer_checks.get("max_layer_delta"),
            "mean_gap_mean_abs_diff": gap_checks.get("mean_gap_mean_abs_diff"),
            "max_gap_mean_abs_diff": gap_checks.get("max_gap_mean_abs_diff"),
            "max_gap_max_abs_diff": gap_checks.get("max_gap_max_abs_diff"),
        },
        "metadata_files": metadata_files,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": gallery_assets,
        },
        "frames": frames,
        "hash_checks": hash_checks,
        "missing_references": missing,
        "next": args.next,
    }
    write_json(manifest_path, bundle)
    write_text(gallery_index, html_page(bundle))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_visual_cache_bundle_gallery",
        "version": 1,
        "generated_utc": bundle["generated_utc"],
        "title": args.title,
        "bundle_repo_path": posix_rel(manifest_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": gallery_assets,
    })
    if args.report:
        write_text(args.report, markdown_report(bundle, manifest_path, root))
    print(
        f"status={status} frames={len(frames)} copied={len(copied_files)} "
        f"missing={len(missing)} hash_failures={hash_failures} manifest={manifest_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a Mitsuba visual-cache bundle")
    parser.add_argument("handoff_manifest")
    parser.add_argument("signed_response_layer")
    parser.add_argument("target_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--profile", default="s467_signed_response_layer")
    parser.add_argument("--title", default="Mitsuba Visual Cache Bundle")
    parser.add_argument(
        "--next",
        default="Use this bundle as the promoted visual-cache handoff before renderer-native response work continues.",
    )
    args = parser.parse_args(argv)
    build(args)


if __name__ == "__main__":
    main()
