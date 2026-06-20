#!/usr/bin/env python
"""Build a depth-aware post-render secondary composite from a Mitsuba render."""

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
from build_mitsuba_renderer_target_preview import (
    Image,
    ImageChops,
    ImageFilter,
    ImageOps,
    copy_asset,
    diff_image,
    grade_image,
    labeled_strip,
    layer_panel,
    max_abs_diff,
    mean_abs_diff,
    require_pillow,
    resolve_path,
    write_gif,
)
from compare_mitsuba_renderer_target_gap import output_frame_map, render_preview_path


def frame_asset_path(frame, role):
    asset = ((frame.get("assets") or {}).get(role) or {})
    return asset.get("path") or asset.get("repo_path")


def normalized_alpha(layer, blur_radius, gain):
    alpha = layer.convert("RGBA").getchannel("A")
    if blur_radius > 0.0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur_radius))
    if gain != 1.0:
        alpha = alpha.point(lambda value: max(0, min(255, int(value * gain))))
    return alpha


def luminance_weight(native, gamma):
    if gamma <= 0.0:
        return Image.new("L", native.size, 255)
    gray = ImageOps.grayscale(native)
    return gray.point(lambda value: max(0, min(255, int(255.0 * ((value / 255.0) ** gamma)))))


def native_weight_mask(layer_alpha, native, args):
    secondary = normalized_alpha(layer_alpha, args.mask_blur_radius, args.mask_gain)
    inverse = ImageOps.invert(secondary)
    base = inverse.point(
        lambda value: int(args.secondary_native_strength * 255.0 +
                          (args.native_base_strength - args.secondary_native_strength) * value)
    )
    lum = luminance_weight(native, args.luminance_gamma)
    if args.luminance_gamma > 0.0:
        base = ImageChops.multiply(base, lum)
    return base


def blend_with_mask(contract_img, native_img, mask):
    return Image.composite(native_img.convert("RGB"), contract_img.convert("RGB"), mask)


def html_page(title, summary, assets, metadata_files):
    gif = next((item for item in assets if item["label"] == "Composite GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Composite Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    checks = summary.get("checks", {})
    metrics = [
        ("Status", summary.get("status")),
        ("Frames", checks.get("frames")),
        ("Max Target MAD", f"{checks.get('max_target_mean_abs_diff', 0.0):.3f}"),
        ("Mean Target MAD", f"{checks.get('mean_target_mean_abs_diff', 0.0):.3f}"),
        ("Max Contract MAD", f"{checks.get('max_contract_mean_abs_diff', 0.0):.3f}"),
        ("GIF", format_bytes(checks.get("gif_bytes", 0))),
    ]
    tiles = "\n".join(f"<div><span>{label}</span><strong>{value}</strong></div>" for label, value in metrics)
    frame_html = "\n".join(
        f"""
        <figure>
          <a href="{item['href']}"><img src="{item['href']}" alt="{item['label']}"></a>
          <figcaption>{item['label']}</figcaption>
        </figure>"""
        for item in strips
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="Composite GIF"></section>' if gif else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #111a21; --ink: #edf7fb; --muted: #a2b5bf; --line: #2e3d47; --accent: #9fd9ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111820; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
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
    <section class="grid">{frame_html}</section>
  </main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
    checks = summary.get("checks", {})
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
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Mean target MAD: `{checks.get('mean_target_mean_abs_diff')}`",
        f"- Max target MAD: `{checks.get('max_target_mean_abs_diff')}`",
        f"- Max target diff: `{checks.get('max_target_max_abs_diff')}`",
        f"- Mean contract MAD: `{checks.get('mean_contract_mean_abs_diff')}`",
        f"- Max contract MAD: `{checks.get('max_contract_mean_abs_diff')}`",
        f"- Contract max target MAD: `{checks.get('contract_max_overlay_mean_abs_diff')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Settings",
        "",
    ]
    for key, value in (summary.get("settings") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Target MAD | Contract MAD | Native Weight Mean | Strip |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    frames = summary.get("frames", [])
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | "
            f"{frame.get('target_mean_abs_diff'):.4f} | {frame.get('contract_mean_abs_diff'):.4f} | "
            f"{frame.get('native_weight_mean'):.4f} | `{frame.get('strip_repo_path')}` |"
        )
    if summary.get("missing_references"):
        lines.extend(["", "## Missing References", ""])
        for item in summary["missing_references"]:
            lines.append(f"- frame `{item.get('frame')}`: `{item}`")
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build_composite(args):
    require_pillow()
    root = os.getcwd()
    render_path = require_file(args.native_render_manifest, "native render manifest")
    contract_path = require_file(args.contract, "secondary pass contract")
    render = read_json(render_path)
    contract = read_json(contract_path)
    if render.get("schema") != "lsfs_mitsuba_xml_render":
        raise SystemExit(f"{args.native_render_manifest}: expected lsfs_mitsuba_xml_render schema")
    if render.get("status") != "ready":
        raise SystemExit(f"{args.native_render_manifest}: render status is {render.get('status')!r}")
    if contract.get("schema") != "lsfs_mitsuba_secondary_pass_contract":
        raise SystemExit(f"{args.contract}: expected lsfs_mitsuba_secondary_pass_contract schema")
    if contract.get("status") != "ready":
        raise SystemExit(f"{args.contract}: contract status is {contract.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    mask_dir = os.path.join(out_dir, "native_weight_masks")
    diff_dir = os.path.join(out_dir, "diffs")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (composite_dir, mask_dir, diff_dir, strip_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    render_frames = output_frame_map(render.get("frames") or [])
    grade_settings = ((contract.get("secondary_pass_contract") or {}).get("grade_settings") or {})
    results = []
    missing = []
    composite_paths = []
    for index, contract_frame in enumerate(contract.get("frames") or []):
        frame_id = contract_frame.get("frame")
        output_frame = contract_frame.get("output_frame")
        render_frame = render_frames.get(output_frame)
        paths = {
            "native": render_preview_path(render_frame),
            "contract": frame_asset_path(contract_frame, "overlay_graded"),
            "secondary_layer": frame_asset_path(contract_frame, "secondary_layer"),
            "target": frame_asset_path(contract_frame, "target"),
        }
        resolved = {role: resolve_path(path) for role, path in paths.items()}
        absent = [
            {"role": role, "path": path}
            for role, path in resolved.items()
            if not path or not os.path.isfile(path)
        ]
        if absent:
            missing.append({"frame": frame_id, "output_frame": output_frame, "missing": absent})
            continue

        native = Image.open(resolved["native"]).convert("RGB")
        contract_img = Image.open(resolved["contract"]).convert("RGB")
        layer = Image.open(resolved["secondary_layer"]).convert("RGBA")
        target = Image.open(resolved["target"]).convert("RGB")
        if native.size != contract_img.size:
            native = native.resize(contract_img.size, Image.Resampling.BICUBIC)
        if layer.size != contract_img.size:
            layer = layer.resize(contract_img.size, Image.Resampling.BICUBIC)
        if target.size != contract_img.size:
            target = target.resize(contract_img.size, Image.Resampling.BICUBIC)
        native_graded = grade_image(native, grade_settings)
        mask = native_weight_mask(layer, native_graded, args)
        composite = blend_with_mask(contract_img, native_graded, mask)
        target_diff = diff_image(composite, target)
        contract_diff = diff_image(composite, contract_img)

        base_name = f"frame_{index:04d}.png"
        composite_path = os.path.join(composite_dir, base_name)
        mask_path = os.path.join(mask_dir, base_name)
        diff_path = os.path.join(diff_dir, base_name)
        strip_path = os.path.join(strip_dir, base_name)
        composite.save(composite_path)
        mask.save(mask_path)
        target_diff.save(diff_path)
        labeled_strip(
            [
                native_graded,
                layer_panel(layer, (20, 30, 38, 255)),
                mask.convert("RGB"),
                contract_img,
                composite,
                target,
                target_diff,
            ],
            ["native graded", "secondary layer", "native weight", "S335 contract", "depth composite", "target", "target diff"],
            strip_path,
        )
        composite_paths.append(composite_path)
        hist = mask.histogram()
        mask_mean = sum(value * count for value, count in enumerate(hist)) / float(max(1, sum(hist))) / 255.0
        results.append({
            "frame": frame_id,
            "output_frame": output_frame,
            "native_repo_path": posix_rel(resolved["native"], root),
            "contract_repo_path": posix_rel(resolved["contract"], root),
            "secondary_layer_repo_path": posix_rel(resolved["secondary_layer"], root),
            "target_repo_path": posix_rel(resolved["target"], root),
            "composite_repo_path": posix_rel(composite_path, root),
            "native_weight_mask_repo_path": posix_rel(mask_path, root),
            "diff_repo_path": posix_rel(diff_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "composite_sha256": sha256_file(composite_path),
            "native_weight_mean": mask_mean,
            "target_mean_abs_diff": mean_abs_diff(composite, target),
            "target_max_abs_diff": max_abs_diff(composite, target),
            "contract_mean_abs_diff": mean_abs_diff(composite, contract_img),
            "contract_max_abs_diff": max_abs_diff(composite, contract_img),
            "contract_target_mean_abs_diff": (contract_frame.get("metrics") or {}).get("overlay_mean_abs_diff"),
            "contract_target_max_abs_diff": (contract_frame.get("metrics") or {}).get("overlay_max_abs_diff"),
        })

    if not results:
        raise SystemExit("no composite frames were generated")

    gif_path = os.path.join(assets_dir, "shot.gif")
    write_gif(composite_paths, gif_path, args.fps)
    assets = [copy_asset(gif_path, assets_dir, "shot.gif", "Composite GIF", root)]
    key_indices = sorted(set(round(i * (len(results) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(results[frame_index]["strip_repo_path"], assets_dir, f"composite_strip_{out_index:02d}.png", f"Composite Strip {out_index + 1}", root))

    summary_path = os.path.join(out_dir, "depth_aware_secondary_composite_summary.json")
    checks = {
        "frames": len(results),
        "missing_references": len(missing),
        "mean_target_mean_abs_diff": sum(item["target_mean_abs_diff"] for item in results) / len(results),
        "max_target_mean_abs_diff": max(item["target_mean_abs_diff"] for item in results),
        "max_target_max_abs_diff": max(item["target_max_abs_diff"] for item in results),
        "mean_contract_mean_abs_diff": sum(item["contract_mean_abs_diff"] for item in results) / len(results),
        "max_contract_mean_abs_diff": max(item["contract_mean_abs_diff"] for item in results),
        "max_contract_max_abs_diff": max(item["contract_max_abs_diff"] for item in results),
        "mean_native_weight": sum(item["native_weight_mean"] for item in results) / len(results),
        "contract_mean_overlay_mean_abs_diff": (contract.get("checks") or {}).get("mean_overlay_mean_abs_diff"),
        "contract_max_overlay_mean_abs_diff": (contract.get("checks") or {}).get("max_overlay_mean_abs_diff"),
        "gif_bytes": os.path.getsize(gif_path),
    }
    status = "ready" if not missing and checks["max_target_mean_abs_diff"] <= args.max_target_mean_abs_diff else "review"
    summary = {
        "schema": "lsfs_mitsuba_depth_aware_secondary_composite",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "sources": {
            "native_render_manifest": {
                "path": render_path,
                "repo_path": posix_rel(render_path, root),
                "sha256": sha256_file(render_path),
                "schema": render.get("schema"),
            },
            "secondary_pass_contract": {
                "path": contract_path,
                "repo_path": posix_rel(contract_path, root),
                "sha256": sha256_file(contract_path),
                "schema": contract.get("schema"),
            },
        },
        "settings": {
            "fps": args.fps,
            "keyframes": args.keyframes,
            "native_base_strength": args.native_base_strength,
            "secondary_native_strength": args.secondary_native_strength,
            "mask_blur_radius": args.mask_blur_radius,
            "mask_gain": args.mask_gain,
            "luminance_gamma": args.luminance_gamma,
            "max_target_mean_abs_diff": args.max_target_mean_abs_diff,
            "grade": grade_settings,
        },
        "checks": checks,
        "missing_references": missing,
        "frames": results,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    summary_asset = copy_asset(summary_path, assets_dir, "depth_aware_secondary_composite_summary.json", "Composite summary", root)
    render_asset = copy_asset(render_path, assets_dir, "native_mitsuba_render.json", "Native render manifest", root)
    contract_asset = copy_asset(contract_path, assets_dir, "secondary_pass_contract.json", "Secondary pass contract", root)
    metadata_files = [summary_asset, render_asset, contract_asset]
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
    write_text(index_path, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_depth_aware_secondary_composite_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status={status} frames={checks['frames']} max_target_mad={checks['max_target_mean_abs_diff']:.6f} "
        f"max_contract_mad={checks['max_contract_mean_abs_diff']:.6f} summary={summary_path}"
    )
    if status != "ready" and args.fail_on_review:
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a depth-aware Mitsuba secondary composite")
    parser.add_argument("native_render_manifest")
    parser.add_argument("contract")
    parser.add_argument("out_dir")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--native-base-strength", type=float, default=0.045)
    parser.add_argument("--secondary-native-strength", type=float, default=0.006)
    parser.add_argument("--mask-blur-radius", type=float, default=2.5)
    parser.add_argument("--mask-gain", type=float, default=1.35)
    parser.add_argument("--luminance-gamma", type=float, default=0.0)
    parser.add_argument("--max-target-mean-abs-diff", type=float, default=24.0)
    parser.add_argument("--fail-on-review", action="store_true")
    parser.add_argument("--title", default="Mitsuba Depth-Aware Secondary Composite")
    parser.add_argument("--report")
    parser.add_argument(
        "--next",
        default="Use this composite as a post-render bridge while replacing screen-space secondary with depth-aware data.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    for name in ("native_base_strength", "secondary_native_strength"):
        value = getattr(args, name)
        if not (0.0 <= value <= 1.0):
            parser.error(f"{name.replace('_', '-')} must be in [0, 1]")
    if args.secondary_native_strength > args.native_base_strength:
        parser.error("secondary-native-strength must be <= native-base-strength")
    if args.mask_blur_radius < 0.0:
        parser.error("mask-blur-radius must be non-negative")
    if args.mask_gain <= 0.0:
        parser.error("mask-gain must be positive")
    if args.luminance_gamma < 0.0:
        parser.error("luminance-gamma must be non-negative")
    if args.max_target_mean_abs_diff < 0.0:
        parser.error("max-target-mean-abs-diff must be non-negative")
    build_composite(args)


if __name__ == "__main__":
    main()
