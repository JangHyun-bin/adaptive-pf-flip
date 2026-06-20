#!/usr/bin/env python
"""Build a UI/import preview from a low-frequency runtime handoff bundle."""

import argparse
import html
import os
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


def is_inside(path, parent):
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(parent)]) == os.path.abspath(parent)
    except ValueError:
        return False


def href_from(out_dir, path):
    return os.path.relpath(path, out_dir).replace(os.sep, "/")


def source_file(bundle_item, root, label):
    path = resolve_path((bundle_item or {}).get("repo_path") or (bundle_item or {}).get("path"), root)
    if not path:
        raise SystemExit(f"Missing path for {label}")
    return require_file(path, label)


def public_asset(bundle_item, root, out_dir, bundle_root, label, role):
    path = source_file(bundle_item, root, label)
    actual_size = os.path.getsize(path)
    actual_sha = sha256_file(path)
    expected_size = bundle_item.get("size")
    expected_sha = bundle_item.get("sha256")
    entry = {
        "label": label,
        "role": role,
        "repo_path": posix_rel(path, root),
        "uri": href_from(out_dir, path),
        "size": actual_size,
        "sha256": actual_sha,
        "declared_size": expected_size,
        "declared_sha256": expected_sha,
        "size_match": expected_size is None or expected_size == actual_size,
        "sha256_match": not expected_sha or expected_sha == actual_sha,
        "inside_bundle": is_inside(path, bundle_root),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def copied_file_by_role(bundle, role):
    for entry in bundle.get("copied_files") or []:
        if entry.get("role") == role:
            return entry
    return None


def copied_file_by_basename(bundle, basename):
    for entry in bundle.get("copied_files") or []:
        path = entry.get("repo_path") or entry.get("path") or ""
        if os.path.basename(str(path).replace("/", os.sep)) == basename:
            return entry
    return None


def frame_ready(frame, required_bindings):
    bindings = frame.get("runtime_bindings") or {}
    for binding in required_bindings:
        item = bindings.get(binding)
        if not item or not item.get("sha256_match") or not item.get("size_match") or not item.get("inside_bundle"):
            return False
    proof = frame.get("proof") or {}
    return proof.get("max_abs_diff") == 0 and proof.get("mean_abs_diff") == 0.0


def collect_frame(bundle_frame, index, contract, root, out_dir, bundle_root):
    required = contract.get("required_bindings") or []
    optional = contract.get("optional_bindings") or []
    runtime_bindings = {}
    optional_bindings = {}
    ui_inputs = []
    missing = []
    for binding in required:
        item = (bundle_frame.get("bindings") or {}).get(binding)
        if not item:
            missing.append(binding)
            continue
        asset = public_asset(item, root, out_dir, bundle_root, f"frame_{index:04d}_{binding}", binding)
        runtime_bindings[binding] = asset
        ui_inputs.append({
            "semantic": binding,
            "uri": asset["uri"],
            "repo_path": asset["repo_path"],
            "sha256": asset["sha256"],
            "size": asset["size"],
            "dimensions": asset.get("dimensions"),
        })
    for binding in optional:
        item = (bundle_frame.get("bindings") or {}).get(binding)
        if item:
            optional_bindings[binding] = public_asset(item, root, out_dir, bundle_root, f"frame_{index:04d}_{binding}", binding)
    oracle = public_asset(bundle_frame.get("oracle") or {}, root, out_dir, bundle_root, f"frame_{index:04d}_oracle", "oracle")
    proof_block = bundle_frame.get("proof") or {}
    proof = {
        "max_abs_diff": proof_block.get("max_abs_diff"),
        "mean_abs_diff": proof_block.get("mean_abs_diff"),
        "mismatched_coverage": proof_block.get("mismatched_coverage"),
        "webgl_frame": public_asset(proof_block.get("webgl_frame") or {}, root, out_dir, bundle_root, f"frame_{index:04d}_webgl_frame", "webgl_frame"),
        "proof_strip": public_asset(proof_block.get("proof_strip") or {}, root, out_dir, bundle_root, f"frame_{index:04d}_proof_strip", "proof_strip"),
    }
    dims = [tuple(item.get("dimensions") or []) for item in runtime_bindings.values() if item.get("dimensions")]
    dimension_mismatch = len(set(dims)) > 1
    frame = {
        "frame": bundle_frame.get("frame"),
        "output_frame": bundle_frame.get("output_frame"),
        "runtime_bindings": runtime_bindings,
        "optional_bindings": optional_bindings,
        "ui_runtime_inputs": ui_inputs,
        "oracle": oracle,
        "proof": proof,
        "missing_required_bindings": missing,
        "dimension_mismatch": dimension_mismatch,
    }
    frame["ready"] = not missing and not dimension_mismatch and frame_ready(frame, required)
    return frame


def count_source_keys(value):
    if isinstance(value, dict):
        total = sum(1 for key in value if "source" in str(key).lower())
        return total + sum(count_source_keys(item) for item in value.values())
    if isinstance(value, list):
        return sum(count_source_keys(item) for item in value)
    return 0


def runtime_assets(bundle, contract, root, out_dir, bundle_root):
    assets = {}
    runtime_html = copied_file_by_role(bundle, "runtime")
    if runtime_html:
        assets["runtime_webgl"] = public_asset(runtime_html, root, out_dir, bundle_root, "runtime_webgl", "runtime")
    proof_gif = copied_file_by_role(bundle, "proof_gallery")
    if proof_gif:
        assets["webgl_proof_gif"] = public_asset(proof_gif, root, out_dir, bundle_root, "webgl_proof_gif", "proof_gallery")
    shaders = {}
    for api, basename in (contract.get("shader_entrypoints") or {}).items():
        entry = copied_file_by_basename(bundle, basename)
        if entry:
            shaders[api] = public_asset(entry, root, out_dir, bundle_root, basename, f"{api}_shader")
    assets["shaders"] = shaders
    return assets


def html_page(title, preview):
    checks = preview.get("checks") or {}
    runtime = preview.get("runtime_assets") or {}
    frames = preview.get("frames") or []
    proof_gif = runtime.get("webgl_proof_gif") or {}
    bundle = preview.get("source_bundle") or {}
    metrics = [
        ("Status", preview.get("status")),
        ("Frames", checks.get("frames")),
        ("Ready", checks.get("ready_frames")),
        ("Missing", checks.get("missing_required_bindings")),
        ("Hash mismatches", checks.get("hash_mismatches")),
        ("Source leaks", checks.get("source_dependency_leaks")),
        ("Proof failures", checks.get("proof_failures")),
    ]
    metrics_html = "\n".join(
        f"<div><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        for label, value in metrics
    )
    hero = ""
    if proof_gif.get("uri"):
        hero = f'<section class="hero"><img src="{html.escape(proof_gif["uri"])}" alt="WebGL proof GIF"></section>'
    frame_html = []
    for frame in frames:
        bindings = frame.get("runtime_bindings") or {}
        proof = frame.get("proof") or {}
        base = bindings.get("base_rgb") or {}
        positive = bindings.get("positive_delta_rgb") or {}
        negative = bindings.get("negative_delta_rgb") or {}
        oracle = frame.get("oracle") or {}
        webgl = proof.get("webgl_frame") or {}
        strip = proof.get("proof_strip") or {}
        frame_html.append(f"""
        <section class="frame">
          <header>
            <h2>Frame {html.escape(str(frame.get('frame')))} / output {html.escape(str(frame.get('output_frame')))}</h2>
            <span>diff {html.escape(str(proof.get('max_abs_diff')))}</span>
          </header>
          <div class="grid">
            {image_tile('Base', base)}
            {image_tile('+Delta', positive)}
            {image_tile('-Delta', negative)}
            {image_tile('Oracle', oracle)}
            {image_tile('WebGL', webgl)}
            {image_tile('Proof Strip', strip)}
          </div>
        </section>""")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d10; --panel: #121a20; --line: #2c3942; --ink: #edf7fb; --muted: #9aacb6; --accent: #77d8bd; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 22px 18px 42px; }}
    h1 {{ margin: 0 0 6px; font-size: 27px; font-weight: 680; letter-spacing: 0; }}
    .source {{ margin: 0 0 18px; color: var(--muted); font-size: 13px; word-break: break-all; }}
    .hero {{ border: 1px solid var(--line); margin-bottom: 14px; background: #111; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div, .frame {{ border: 1px solid var(--line); background: var(--panel); }}
    .metrics div {{ padding: 10px 12px; min-height: 58px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 640; }}
    .frame {{ margin-top: 14px; }}
    .frame header {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 12px; border-bottom: 1px solid var(--line); }}
    h2 {{ margin: 0; font-size: 16px; font-weight: 650; letter-spacing: 0; }}
    .frame header span {{ color: var(--accent); font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1px; background: var(--line); }}
    figure {{ margin: 0; background: #0d1419; min-width: 0; }}
    figure img {{ display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: contain; background: #030506; }}
    figcaption {{ padding: 7px 9px; color: var(--muted); font-size: 12px; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(title)}</h1>
    <p class="source">Bundle: <a href="{html.escape(bundle.get('uri', '#'))}">{html.escape(bundle.get('repo_path', 'n/a'))}</a></p>
    {hero}
    <section class="metrics">{metrics_html}</section>
    {''.join(frame_html)}
  </main>
</body>
</html>
"""


def image_tile(label, item):
    uri = item.get("uri")
    dims = item.get("dimensions")
    detail = f"{dims[0]} x {dims[1]}" if dims else "n/a"
    if not uri:
        return f"<figure><figcaption>{html.escape(label)} missing</figcaption></figure>"
    return (
        f'<figure><a href="{html.escape(uri)}"><img src="{html.escape(uri)}" '
        f'alt="{html.escape(label)}"></a><figcaption>{html.escape(label)} - {html.escape(detail)}</figcaption></figure>'
    )


def markdown_report(preview, manifest_path, root):
    checks = preview.get("checks") or {}
    lines = [
        f"# {preview['title']}",
        "",
        f"Generated UTC: `{preview['generated_utc']}`",
        f"Preview JSON: `{posix_rel(manifest_path, root)}`",
        f"Index HTML: `{preview['output']['index_html']['repo_path']}`",
        f"Status: `{preview['status']}`",
        f"Source bundle: `{preview['source_bundle']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Ready frames: `{checks.get('ready_frames')}`",
        f"- Missing required bindings: `{checks.get('missing_required_bindings')}`",
        f"- Hash mismatches: `{checks.get('hash_mismatches')}`",
        f"- Size mismatches: `{checks.get('size_mismatches')}`",
        f"- Dimension mismatches: `{checks.get('dimension_mismatches')}`",
        f"- Bundle-local violations: `{checks.get('inside_bundle_violations')}`",
        f"- Source dependency leaks: `{checks.get('source_dependency_leaks')}`",
        f"- Proof failures: `{checks.get('proof_failures')}`",
        "",
        "## Runtime Assets",
        "",
        "| Asset | Role | Size | Path |",
        "| --- | --- | ---: | --- |",
    ]
    runtime_assets_flat = []
    for key, item in (preview.get("runtime_assets") or {}).items():
        if key == "shaders":
            for shader in item.values():
                runtime_assets_flat.append(shader)
        elif isinstance(item, dict):
            runtime_assets_flat.append(item)
    for item in runtime_assets_flat:
        lines.append(f"| {item.get('label')} | `{item.get('role')}` | {format_bytes(item.get('size', 0))} | `{item.get('repo_path')}` |")
    lines.extend([
        "",
        "## Frame Imports",
        "",
        "| Frame | Ready | Inputs | Oracle | WebGL |",
        "| ---: | --- | ---: | --- | --- |",
    ])
    for frame in preview.get("frames") or []:
        oracle = frame.get("oracle") or {}
        webgl = (frame.get("proof") or {}).get("webgl_frame") or {}
        lines.append(
            f"| {frame.get('frame')} | `{frame.get('ready')}` | {len(frame.get('ui_runtime_inputs') or [])} | "
            f"`{oracle.get('repo_path')}` | `{webgl.get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", preview.get("next") or "Use this import preview as the renderer UI integration gate.", ""])
    return "\n".join(lines)


def build_preview(args):
    root = os.getcwd()
    bundle_path = require_file(resolve_path(args.bundle, root), "runtime handoff bundle")
    bundle = read_json(bundle_path)
    if bundle.get("schema") != "lsfs_mitsuba_low_frequency_runtime_handoff_bundle":
        raise SystemExit(f"{args.bundle}: expected lsfs_mitsuba_low_frequency_runtime_handoff_bundle schema")
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    bundle_root = resolve_path((bundle.get("bundle_root") or {}).get("repo_path") or os.path.dirname(bundle_path), root)
    contract = bundle.get("runtime_contract") or {}
    frames = [collect_frame(frame, index, contract, root, out_dir, bundle_root) for index, frame in enumerate(bundle.get("frames") or [])]
    assets = runtime_assets(bundle, contract, root, out_dir, bundle_root)
    hash_mismatches = 0
    size_mismatches = 0
    inside_bundle_violations = 0
    for frame in frames:
        items = list((frame.get("runtime_bindings") or {}).values())
        items += list((frame.get("optional_bindings") or {}).values())
        items.append(frame.get("oracle") or {})
        proof = frame.get("proof") or {}
        items += [proof.get("webgl_frame") or {}, proof.get("proof_strip") or {}]
        for item in items:
            hash_mismatches += 0 if item.get("sha256_match") else 1
            size_mismatches += 0 if item.get("size_match") else 1
            inside_bundle_violations += 0 if item.get("inside_bundle") else 1
    runtime_items = []
    for key, item in assets.items():
        if key == "shaders":
            runtime_items.extend(item.values())
        elif isinstance(item, dict):
            runtime_items.append(item)
    for item in runtime_items:
        hash_mismatches += 0 if item.get("sha256_match") else 1
        size_mismatches += 0 if item.get("size_match") else 1
        inside_bundle_violations += 0 if item.get("inside_bundle") else 1
    required_total = len(frames) * len(contract.get("required_bindings") or [])
    required_found = sum(len(frame.get("runtime_bindings") or {}) for frame in frames)
    checks = {
        "bundle_status": bundle.get("status"),
        "frames": len(frames),
        "ready_frames": sum(1 for frame in frames if frame.get("ready")),
        "required_bindings_per_frame": len(contract.get("required_bindings") or []),
        "required_bindings_total": required_total,
        "required_bindings_found": required_found,
        "missing_required_bindings": sum(len(frame.get("missing_required_bindings") or []) for frame in frames),
        "hash_mismatches": hash_mismatches,
        "size_mismatches": size_mismatches,
        "dimension_mismatches": sum(1 for frame in frames if frame.get("dimension_mismatch")),
        "inside_bundle_violations": inside_bundle_violations,
        "source_dependency_leaks": count_source_keys(frames),
        "proof_failures": sum(
            1
            for frame in frames
            if (frame.get("proof") or {}).get("max_abs_diff") != 0
            or (frame.get("proof") or {}).get("mean_abs_diff") != 0.0
        ),
        "runtime_html_resolved": bool((assets.get("runtime_webgl") or {}).get("repo_path")),
        "shader_refs_resolved": len((assets.get("shaders") or {})) == len(contract.get("shader_entrypoints") or {}),
    }
    status = "ready" if (
        bundle.get("status") == "ready"
        and checks["ready_frames"] == checks["frames"]
        and checks["missing_required_bindings"] == 0
        and checks["hash_mismatches"] == 0
        and checks["size_mismatches"] == 0
        and checks["dimension_mismatches"] == 0
        and checks["inside_bundle_violations"] == 0
        and checks["source_dependency_leaks"] == 0
        and checks["proof_failures"] == 0
        and checks["runtime_html_resolved"]
        and checks["shader_refs_resolved"]
    ) else "review"
    manifest_path = os.path.abspath(args.manifest)
    index_path = os.path.join(out_dir, "index.html")
    preview = {
        "schema": "lsfs_mitsuba_low_frequency_runtime_import_preview",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "source_bundle": {
            "path": bundle_path,
            "repo_path": posix_rel(bundle_path, root),
            "uri": href_from(out_dir, bundle_path),
            "schema": bundle.get("schema"),
            "status": bundle.get("status"),
            "sha256": sha256_file(bundle_path),
            "size": os.path.getsize(bundle_path),
        },
        "output": {
            "root": {"path": out_dir, "repo_path": posix_rel(out_dir, root)},
            "index_html": {"path": index_path, "repo_path": posix_rel(index_path, root), "uri": "index.html"},
            "manifest": {"path": manifest_path, "repo_path": posix_rel(manifest_path, root)},
        },
        "runtime_contract": contract,
        "runtime_assets": assets,
        "frames": frames,
        "checks": checks,
        "next": args.next,
    }
    write_text(index_path, html_page(args.title, preview))
    preview["output"]["index_html"]["sha256"] = sha256_file(index_path)
    preview["output"]["index_html"]["size"] = os.path.getsize(index_path)
    write_json(manifest_path, preview)
    if args.report:
        write_text(args.report, markdown_report(preview, manifest_path, root))
    print(
        f"status={preview['status']} frames={checks['frames']} ready={checks['ready_frames']} "
        f"source_leaks={checks['source_dependency_leaks']} manifest={manifest_path}"
    )
    if preview["status"] != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a runtime-bundle import preview")
    parser.add_argument("bundle")
    parser.add_argument("out_dir")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    parser.add_argument("--title", default="S495 Mitsuba Low Frequency Runtime Import Preview")
    parser.add_argument("--next", default="Use this bundle-only import preview as the production renderer UI/export gate.")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args(argv)
    build_preview(args)


if __name__ == "__main__":
    main()
