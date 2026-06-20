#!/usr/bin/env python
"""Build a renderer-native material intent package from scene-depth backend gates."""

import argparse
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
from apply_mitsuba_renderer_scene_depth_material_preview import (
    Image,
    ImageOps,
    copy_asset,
    labeled_strip,
    resolve_path,
    write_gif,
)


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def fmt(value):
    return f"{float(value):.8g}"


def csv3(values):
    return ", ".join(fmt(item) for item in values)


def by_frame(rows):
    return {int(row.get("frame") or 0): row for row in rows or []}


def ref_path(ref, root):
    if isinstance(ref, dict):
        return resolve_path(ref.get("path") or ref.get("repo_path"), root)
    return resolve_path(ref, root)


def file_entry(path, root, label=None):
    entry = {
        "repo_path": posix_rel(path, root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    if label:
        entry["label"] = label
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def selected_indices(length, count):
    if length <= 0:
        return []
    if count <= 0 or count >= length:
        return list(range(length))
    if count == 1:
        return [length // 2]
    return sorted(set(round(i * (length - 1) / float(count - 1)) for i in range(count)))


def material_params(strength):
    s = clamp(float(strength), 0.0, 1.0)
    alpha = clamp(0.018 - 0.012 * s, 0.0055, 0.018)
    specular_reflectance = [
        clamp(0.34 + 0.18 * s, 0.0, 1.0),
        clamp(0.42 + 0.17 * s, 0.0, 1.0),
        clamp(0.56 + 0.14 * s, 0.0, 1.0),
    ]
    specular_transmittance = [
        clamp(0.88 - 0.10 * s, 0.0, 1.0),
        clamp(0.94 - 0.06 * s, 0.0, 1.0),
        clamp(1.00, 0.0, 1.0),
    ]
    absorption_tint = [
        clamp(0.012 + 0.035 * s, 0.0, 1.0),
        clamp(0.035 + 0.055 * s, 0.0, 1.0),
        clamp(0.075 + 0.080 * s, 0.0, 1.0),
    ]
    mask_weight = clamp(0.40 + 0.45 * s, 0.0, 1.0)
    return {
        "roughdielectric_alpha": alpha,
        "distribution": "ggx",
        "int_ior": 1.333,
        "ext_ior": 1.0,
        "specular_reflectance": specular_reflectance,
        "specular_transmittance": specular_transmittance,
        "absorption_tint": absorption_tint,
        "mask_weight": mask_weight,
        "mask_falloff_power": 0.7,
    }


def xml_path(path):
    return resolve_path(path, os.getcwd()).replace(os.sep, "/")


def xml_snippet(frame_id, params, mask_repo_path):
    bsdf_id = f"lsfs_scene_depth_material_water_{frame_id:04d}"
    texture_id = f"lsfs_scene_depth_material_mask_{frame_id:04d}"
    return "\n".join([
        f'<texture type="bitmap" id="{texture_id}">',
        f'  <string name="filename" value="{xml_path(mask_repo_path)}"/>',
        '  <string name="filter_type" value="bilinear"/>',
        '</texture>',
        f'<bsdf type="roughdielectric" id="{bsdf_id}">',
        f'  <string name="distribution" value="{params["distribution"]}"/>',
        f'  <float name="alpha" value="{fmt(params["roughdielectric_alpha"])}"/>',
        f'  <float name="int_ior" value="{fmt(params["int_ior"])}"/>',
        f'  <float name="ext_ior" value="{fmt(params["ext_ior"])}"/>',
        f'  <rgb name="specular_reflectance" value="{csv3(params["specular_reflectance"])}"/>',
        f'  <rgb name="specular_transmittance" value="{csv3(params["specular_transmittance"])}"/>',
        '</bsdf>',
        '<!-- Material consumer note:',
        f'     Use {texture_id} as the localized scene-depth material mask.',
        f'     Blend toward {bsdf_id} with mask_weight={fmt(params["mask_weight"])}',
        f'     and mask_falloff_power={fmt(params["mask_falloff_power"])}.',
        f'     Absorption tint target: {csv3(params["absorption_tint"])}.',
        '-->',
        '',
    ])


def parameter_visual(source, mask, params):
    mask_rgb = ImageOps.colorize(mask.convert("L"), black=(5, 10, 16), white=(120, 205, 255))
    source_rgb = source.convert("RGB")
    blended = Image.blend(source_rgb, mask_rgb, 0.32)
    return blended


def markdown_report(summary, summary_path, root):
    checks = summary.get("checks") or {}
    ranges = summary.get("material_parameter_ranges") or {}
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Backend summary: `{summary['inputs']['backend_summary']}`",
        f"- Backend compare summary: `{summary['inputs']['backend_compare_summary']}`",
        f"- Target summary: `{summary['inputs']['target_summary']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Material snippets: `{checks.get('material_snippets')}`",
        f"- Texture bindings: `{checks.get('texture_bindings')}`",
        f"- Max backend-vs-target abs diff: `{checks.get('max_backend_target_abs_diff')}`",
        f"- Max backend-vs-target mean diff: `{checks.get('max_backend_target_mean_diff')}`",
        f"- Max backend-vs-accepted abs diff: `{checks.get('max_backend_accepted_abs_diff')}`",
        f"- Max backend-vs-accepted mean diff: `{checks.get('max_backend_accepted_mean_diff')}`",
        f"- Snippet bytes: `{format_bytes(checks.get('snippet_bytes', 0))}`",
        f"- Intent GIF bytes: `{format_bytes(checks.get('intent_gif_bytes', 0))}`",
        "",
        "## Material Ranges",
        "",
        f"- Alpha: `{ranges.get('alpha_min')}` .. `{ranges.get('alpha_max')}`",
        f"- Mask weight: `{ranges.get('mask_weight_min')}` .. `{ranges.get('mask_weight_max')}`",
        f"- Strength: `{ranges.get('strength_min')}` .. `{ranges.get('strength_max')}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Strength | Alpha | Mask Weight | Backend/Target Max | Snippet | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in selected_indices(len(frames), 3):
        frame = frames[index]
        params = frame.get("material_parameters") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('effective_strength')} | {params.get('roughdielectric_alpha')} | "
            f"{params.get('mask_weight')} | {frame.get('gate', {}).get('backend_vs_target', {}).get('max_abs_diff')} | "
            f"`{frame.get('snippet', {}).get('repo_path')}` | `{frame.get('strip', {}).get('repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def html_page(summary):
    checks = summary.get("checks") or {}
    assets = (summary.get("gallery") or {}).get("assets") or []
    gif = next((item for item in assets if item.get("label") == "Native Material Intent GIF"), None)
    strips = [item for item in assets if item.get("label", "").startswith("Native Material Intent Strip")]
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Snippets", checks.get("material_snippets")),
            ("Textures", checks.get("texture_bindings")),
            ("Target Diff", checks.get("max_backend_target_abs_diff")),
            ("Accepted Diff", checks.get("max_backend_accepted_abs_diff")),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="native material intent gif"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{summary['title']}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #edf7fb; --muted: #9fb4c1; --line: #30414c; --accent: #95ddff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1680px; margin: 0 auto; padding: 24px 18px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 650; letter-spacing: 0; }}
    p {{ margin: 0 0 16px; color: var(--muted); line-height: 1.5; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 16px 0 24px; }}
    .tiles div {{ border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 10px 12px; }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 16px; word-break: break-word; }}
    .hero, figure {{ border: 1px solid var(--line); background: #0d1820; overflow-x: auto; margin: 0 0 12px; }}
    img {{ display: block; max-width: none; }}
    figcaption {{ padding: 8px 10px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); }}
  </style>
</head>
<body>
<main>
  <h1>{summary['title']}</h1>
  <p>Renderer-native material parameter package derived from the full48 scene-cache backend gate.</p>
  <section class="tiles">{tiles}</section>
  {hero}
  <section>{figures}</section>
</main>
</body>
</html>
"""


def run(args):
    root = os.getcwd()
    backend_path = require_file(resolve_path(args.backend_summary, root), "scene-depth backend summary")
    compare_path = require_file(resolve_path(args.backend_compare_summary, root), "scene-depth backend compare summary")
    target_path = require_file(resolve_path(args.target_summary, root), "scene-depth target summary")
    backend = read_json(backend_path)
    compare = read_json(compare_path)
    target = read_json(target_path)
    if backend.get("status") != "passed":
        raise SystemExit(f"{args.backend_summary}: backend status is {backend.get('status')!r}")
    if compare.get("status") != "ready":
        raise SystemExit(f"{args.backend_compare_summary}: compare status is {compare.get('status')!r}")
    if target.get("status") != "ready":
        raise SystemExit(f"{args.target_summary}: target status is {target.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    snippet_dir = os.path.join(out_dir, "snippets")
    strip_dir = os.path.join(out_dir, "strips")
    intent_dir = os.path.join(out_dir, "intent_frames")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for directory in (snippet_dir, strip_dir, intent_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)

    compare_by_frame = by_frame(compare.get("frames"))
    target_by_frame = by_frame(target.get("frames"))
    frames = []
    missing = []
    intent_paths = []
    strip_paths = []
    snippet_bytes = 0
    for backend_frame in sorted(backend.get("frames") or [], key=lambda item: int(item.get("frame") or 0)):
        frame_id = int(backend_frame.get("frame") or 0)
        compare_frame = compare_by_frame.get(frame_id, {})
        target_frame = target_by_frame.get(frame_id, {})
        refs = target_frame.get("references") or {}
        source_path = ref_path(refs.get("source_composite"), root)
        mask_path = ref_path(refs.get("magnitude_mask"), root)
        backend_image_path = resolve_path(backend_frame.get("output_image_repo_path"), root)
        absent = [
            name for name, path in (
                ("source_composite", source_path),
                ("magnitude_mask", mask_path),
                ("backend_output", backend_image_path),
            )
            if not path or not os.path.isfile(path)
        ]
        if absent:
            missing.append({"frame": frame_id, "missing": absent})
            continue
        strength = float(backend_frame.get("effective_strength") or (target_frame.get("control") or {}).get("effective_strength") or 0.0)
        params = material_params(strength)
        snippet_path = os.path.join(snippet_dir, f"frame_{frame_id:04d}_scene_depth_material.xml")
        write_text(snippet_path, xml_snippet(frame_id, params, posix_rel(mask_path, root)))
        snippet_bytes += os.path.getsize(snippet_path)

        source = Image.open(source_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")
        backend_image = Image.open(backend_image_path).convert("RGB")
        intent = parameter_visual(source, mask, params)
        intent_path = os.path.join(intent_dir, f"frame_{frame_id:04d}_native_material_intent.png")
        intent.save(intent_path)
        mask_rgb = ImageOps.colorize(mask, black=(5, 10, 16), white=(120, 205, 255))
        strip_path = os.path.join(strip_dir, f"frame_{frame_id:04d}_native_material_intent.png")
        labeled_strip(
            [source, mask_rgb, intent, backend_image],
            ["S577 accepted", "material mask", "native material intent", "S591 backend target"],
            strip_path,
        )
        intent_paths.append(intent_path)
        strip_paths.append(strip_path)
        gate = {
            "backend_vs_target": compare_frame.get("backend_vs_target") or {},
            "backend_vs_accepted": compare_frame.get("backend_vs_accepted") or {},
        }
        frames.append({
            "frame": frame_id,
            "output_frame": backend_frame.get("output_frame"),
            "effective_strength": strength,
            "material_parameters": params,
            "texture_bindings": {
                "localized_material_mask": file_entry(mask_path, root, "localized material mask"),
            },
            "references": {
                "source_composite": posix_rel(source_path, root),
                "backend_output": posix_rel(backend_image_path, root),
            },
            "snippet": file_entry(snippet_path, root, "Mitsuba material snippet"),
            "intent_frame": file_entry(intent_path, root, "native material intent frame"),
            "strip": file_entry(strip_path, root, "native material intent strip"),
            "gate": gate,
        })

    if not frames:
        raise SystemExit("no native material frames produced")

    intent_gif = os.path.join(out_dir, "native_material_intent.gif")
    strip_gif = os.path.join(out_dir, "native_material_intent_strips.gif")
    write_gif(intent_paths, intent_gif, args.fps)
    write_gif(strip_paths, strip_gif, args.fps)
    sample_indices = selected_indices(len(strip_paths), args.keyframes)
    assets = [
        copy_asset(intent_gif, assets_dir, "native_material_intent.gif", "Native Material Intent GIF", root),
        copy_asset(strip_gif, assets_dir, "native_material_intent_strips.gif", "Native Material Intent Strip GIF", root),
    ]
    for out_index, frame_index in enumerate(sample_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"native_material_intent_strip_{out_index:02d}.png", f"Native Material Intent Strip {out_index + 1}", root))

    alpha_values = [frame["material_parameters"]["roughdielectric_alpha"] for frame in frames]
    weight_values = [frame["material_parameters"]["mask_weight"] for frame in frames]
    strength_values = [frame["effective_strength"] for frame in frames]
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "material_snippets": len(frames),
        "texture_bindings": len(frames),
        "max_backend_target_abs_diff": max((frame["gate"]["backend_vs_target"].get("max_abs_diff", 999) for frame in frames), default=999),
        "max_backend_target_mean_diff": max((frame["gate"]["backend_vs_target"].get("mean_abs_diff", 999.0) for frame in frames), default=999.0),
        "max_backend_accepted_abs_diff": max((frame["gate"]["backend_vs_accepted"].get("max_abs_diff", 999) for frame in frames), default=999),
        "max_backend_accepted_mean_diff": max((frame["gate"]["backend_vs_accepted"].get("mean_abs_diff", 999.0) for frame in frames), default=999.0),
        "snippet_bytes": snippet_bytes,
        "intent_gif_bytes": os.path.getsize(intent_gif),
        "strip_gif_bytes": os.path.getsize(strip_gif),
    }
    status = "ready" if (
        checks["frames"] > 0
        and checks["missing_references"] == 0
        and checks["material_snippets"] == checks["frames"]
        and checks["texture_bindings"] == checks["frames"]
        and checks["max_backend_target_abs_diff"] == 0
        and checks["max_backend_target_mean_diff"] == 0.0
    ) else "failed"
    summary_path = os.path.abspath(args.summary)
    index_path = os.path.join(gallery_dir, "index.html")
    metadata_files = [
        copy_asset(backend_path, assets_dir, "scene_cache_backend_full48_summary.json", "Scene-Cache Backend Full48 Summary", root),
        copy_asset(compare_path, assets_dir, "backend_output_compare_summary.json", "Backend Output Compare Summary", root),
        copy_asset(target_path, assets_dir, "depth_material_target_summary.json", "Depth Material Target Summary", root),
    ]
    summary = {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_native_material_package",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "inputs": {
            "backend_summary": posix_rel(backend_path, root),
            "backend_compare_summary": posix_rel(compare_path, root),
            "target_summary": posix_rel(target_path, root),
        },
        "renderer_native_material_contract": {
            "consumer": "Mitsuba XML roughdielectric water material or renderer-native equivalent",
            "control_texture": "localized_material_mask",
            "control_parameter": "effective_strength",
            "validated_against": "S592 full48 backend promotion gate",
            "notes": [
                "Use snippets as frame-local material intent, not as a standalone complete scene.",
                "Next pass should bind these parameters to the water surface material and render a sample.",
            ],
        },
        "checks": checks,
        "material_parameter_ranges": {
            "alpha_min": min(alpha_values),
            "alpha_max": max(alpha_values),
            "mask_weight_min": min(weight_values),
            "mask_weight_max": max(weight_values),
            "strength_min": min(strength_values),
            "strength_max": max(strength_values),
        },
        "missing_references": missing,
        "frames": frames,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": index_path,
            "index_repo_path": posix_rel(index_path, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "native_material_package_summary.json", "Native Material Package Summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    summary_asset = resolve_path(metadata_files[0]["repo_path"], root)
    write_json(summary_asset, summary)
    write_text(index_path, html_page(summary))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_renderer_scene_depth_material_native_material_package_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} snippets={checks['material_snippets']} "
        f"textures={checks['texture_bindings']} max_diff={checks['max_backend_target_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a renderer-native scene-depth material package")
    parser.add_argument("backend_summary")
    parser.add_argument("backend_compare_summary")
    parser.add_argument("target_summary")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=12.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--title", default="S594 Mitsuba Renderer Scene Depth Material Native Material Package")
    parser.add_argument(
        "--next",
        default="Bind this package to a Mitsuba XML water-material sample and render it through the native renderer path.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
