#!/usr/bin/env python
"""Build a signed response-AOV contract from a promoted response-scale composite."""

import argparse
import os
import shutil
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageOps = None

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
from compare_mitsuba_renderer_target_gap import max_abs_diff, mean_abs_diff, write_gif


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build a response-AOV contract")


def resolve_path(path, root):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(root, str(path).replace("/", os.sep)))


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def copy_asset(src, assets_dir, name, label, root):
    dst = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)
    entry = {
        "label": label,
        "asset": dst,
        "repo_path": posix_rel(dst, root),
        "href": f"assets/{name}",
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "sha256": sha256_file(dst),
        "size": os.path.getsize(dst),
    }
    dims = image_dimensions(dst)
    if dims:
        entry["dimensions"] = dims
    return entry


def file_ref(path, label, role, root):
    entry = {
        "label": label,
        "role": role,
        "path": os.path.abspath(path),
        "repo_path": posix_rel(os.path.abspath(path), root),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }
    dims = image_dimensions(path)
    if dims:
        entry["dimensions"] = dims
    return entry


def selected_signed_layers(base_img, composite_img):
    base = base_img.convert("RGB")
    composite = composite_img.convert("RGB")
    positive = Image.new("RGB", base.size)
    negative = Image.new("RGB", base.size)
    bp = base.load()
    cp = composite.load()
    pp = positive.load()
    np = negative.load()
    changed = 0
    total_abs = 0
    max_abs = 0
    count = base.size[0] * base.size[1] * 3
    for y in range(base.size[1]):
        for x in range(base.size[0]):
            bv = bp[x, y]
            cv = cp[x, y]
            pos = []
            neg = []
            for channel in range(3):
                delta = int(cv[channel]) - int(bv[channel])
                abs_delta = abs(delta)
                total_abs += abs_delta
                max_abs = max(max_abs, abs_delta)
                if abs_delta:
                    changed += 1
                pos.append(max(0, delta))
                neg.append(max(0, -delta))
            pp[x, y] = tuple(pos)
            np[x, y] = tuple(neg)
    return positive, negative, {
        "mean_abs_signed_delta": total_abs / float(max(1, count)),
        "max_abs_signed_delta": max_abs,
        "changed_channel_fraction": changed / float(max(1, count)),
    }


def reconstruct(base_img, positive_img, negative_img):
    base = base_img.convert("RGB")
    positive = positive_img.convert("RGB")
    negative = negative_img.convert("RGB")
    out = Image.new("RGB", base.size)
    bp = base.load()
    pp = positive.load()
    np = negative.load()
    op = out.load()
    for y in range(base.size[1]):
        for x in range(base.size[0]):
            bv = bp[x, y]
            pv = pp[x, y]
            nv = np[x, y]
            op[x, y] = tuple(max(0, min(255, int(bv[c]) + int(pv[c]) - int(nv[c]))) for c in range(3))
    return out


def delta_visual(layer, gain):
    if gain <= 1.0:
        return layer.convert("RGB")
    return Image.eval(layer.convert("RGB"), lambda value: max(0, min(255, int(round(value * gain)))))


def diff_image(a, b):
    return ImageOps.autocontrast(ImageChops.difference(a.convert("RGB"), b.convert("RGB")))


def labeled_strip(panels, labels, out_path):
    width, height = panels[0].size
    label_h = 28
    strip = Image.new("RGB", (width * len(panels), height + label_h), (8, 13, 18))
    draw = ImageDraw.Draw(strip)
    for index, panel in enumerate(panels):
        x = index * width
        draw.rectangle((x, 0, x + width, label_h), fill=(18, 28, 36))
        draw.text((x + 8, 8), labels[index], fill=(230, 242, 248))
        strip.paste(panel.convert("RGB"), (x, label_h))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path)


def json_source(path, root, payload):
    return {
        "path": path,
        "repo_path": posix_rel(path, root),
        "schema": payload.get("schema"),
        "subschema": payload.get("subschema"),
        "status": payload.get("status"),
        "sha256": sha256_file(path),
        "size": os.path.getsize(path),
    }


def gap_source(path, root):
    if not path:
        return None, None
    resolved = require_file(path, "gap summary")
    payload = read_json(resolved)
    return json_source(resolved, root, payload), payload


def html_page(title, contract, assets, metadata_files):
    checks = contract.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Response AOV GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Response AOV Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", contract.get("status")),
            ("Scale", contract.get("settings", {}).get("response_scale")),
            ("Frames", checks.get("frames")),
            ("Max Diff", checks.get("reconstruction_max_abs_diff")),
            ("Mean Delta", f"{checks.get('mean_abs_signed_delta', 0.0):.3f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="response AOV GIF"></section>' if gif else ""
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
    :root {{ color-scheme: dark; --bg: #080d11; --panel: #111a21; --ink: #edf7fb; --muted: #a2b5bf; --line: #2e3d47; --accent: #9fd9ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero {{ border: 1px solid var(--line); background: #111820; }}
    .hero img {{ display: block; width: 100%; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
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
    <section class="grid">{figures}</section>
  </main>
</body>
</html>
"""


def markdown_report(contract, contract_path, root):
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
        f"- Response buffer: `{contract['sources']['response_delta_buffer']['repo_path']}`",
        f"- Response composite: `{contract['sources']['response_scale_composite']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Response scale: `{contract['settings']['response_scale']}`",
        f"- Reconstruction max abs diff: `{checks.get('reconstruction_max_abs_diff')}`",
        f"- Reconstruction max mean abs diff: `{checks.get('reconstruction_max_mean_abs_diff')}`",
        f"- Mean abs signed delta: `{checks.get('mean_abs_signed_delta')}`",
        f"- Max abs signed delta: `{checks.get('max_abs_signed_delta')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- AOV bytes: `{format_bytes(checks.get('aov_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Gate Metrics",
        "",
    ]
    gates = contract.get("gate_metrics") or {}
    for key in ("s577", "s585"):
        gate = gates.get(key) or {}
        if gate:
            lines.append(
                f"- {key}: mean/max/maxabs `{gate.get('mean_gap_mean_abs_diff')}` / "
                f"`{gate.get('max_gap_mean_abs_diff')}` / `{gate.get('max_gap_max_abs_diff')}`"
            )
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Output | Mean Delta | Max Delta | Recon Max | Strip |",
        "| ---: | ---: | ---: | ---: | --- |",
    ])
    frames = contract.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        stats = frame.get("stats") or {}
        lines.append(
            f"| {frame.get('output_frame')} | {stats.get('mean_abs_signed_delta')} | "
            f"{stats.get('max_abs_signed_delta')} | {stats.get('reconstruction_max_abs_diff')} | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", contract.get("next") or "", ""])
    return "\n".join(lines)


def run(args):
    require_pillow()
    root = os.getcwd()
    response_path = require_file(args.response_summary, "response delta buffer summary")
    composite_summary_path = require_file(args.composite_summary, "response scale composite summary")
    response = read_json(response_path)
    composite = read_json(composite_summary_path)
    if response.get("schema") != "lsfs_mitsuba_response_delta_buffer":
        raise SystemExit(f"{args.response_summary}: expected lsfs_mitsuba_response_delta_buffer schema")
    if composite.get("schema") != "lsfs_mitsuba_secondary_composite":
        raise SystemExit(f"{args.composite_summary}: expected lsfs_mitsuba_secondary_composite schema")
    if composite.get("status") != "ready":
        raise SystemExit(f"{args.composite_summary}: composite status is {composite.get('status')!r}")

    scale = float((composite.get("settings") or {}).get("response_scale"))
    composite_by_output = output_frame_map(composite.get("frames") or [])
    out_dir = os.path.abspath(args.out_dir)
    base_dir = os.path.join(out_dir, "aovs", "base_rgb")
    pos_dir = os.path.join(out_dir, "aovs", "response_positive_rgb")
    neg_dir = os.path.join(out_dir, "aovs", "response_negative_rgb")
    composite_dir = os.path.join(out_dir, "aovs", "selected_composite_rgb")
    full_dir = os.path.join(out_dir, "aovs", "full_render_rgb")
    strip_dir = os.path.join(out_dir, "strips")
    recon_dir = os.path.join(out_dir, "reconstructed")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    for path in (base_dir, pos_dir, neg_dir, composite_dir, full_dir, strip_dir, recon_dir, assets_dir):
        os.makedirs(path, exist_ok=True)

    frames = []
    strips = []
    missing = []
    for index, response_frame in enumerate(response.get("frames") or []):
        output = response_frame.get("output_frame")
        composite_frame = composite_by_output.get(output)
        if not composite_frame:
            missing.append({"output_frame": output, "missing": ["composite_frame"]})
            continue
        paths = {
            "base": resolve_path(response_frame.get("base_repo_path"), root),
            "full": resolve_path(response_frame.get("full_repo_path"), root),
            "composite": resolve_path(composite_frame.get("composite_repo_path"), root),
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"output_frame": output, "missing": absent})
            continue
        base = Image.open(paths["base"]).convert("RGB")
        full = Image.open(paths["full"]).convert("RGB")
        selected = Image.open(paths["composite"]).convert("RGB")
        if full.size != base.size:
            full = full.resize(base.size, Image.Resampling.BICUBIC)
        if selected.size != base.size:
            selected = selected.resize(base.size, Image.Resampling.BICUBIC)
        positive, negative, delta_stats = selected_signed_layers(base, selected)
        reconstructed = reconstruct(base, positive, negative)
        recon_mean = mean_abs_diff(reconstructed, selected)
        recon_max = max_abs_diff(reconstructed, selected)
        full_mean = mean_abs_diff(selected, full)
        full_max = max_abs_diff(selected, full)

        base_path = os.path.join(base_dir, f"frame_{index:04d}.png")
        pos_path = os.path.join(pos_dir, f"frame_{index:04d}.png")
        neg_path = os.path.join(neg_dir, f"frame_{index:04d}.png")
        selected_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        full_path = os.path.join(full_dir, f"frame_{index:04d}.png")
        recon_path = os.path.join(recon_dir, f"frame_{index:04d}.png")
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        shutil.copy2(paths["base"], base_path)
        shutil.copy2(paths["full"], full_path)
        shutil.copy2(paths["composite"], selected_path)
        positive.save(pos_path)
        negative.save(neg_path)
        reconstructed.save(recon_path)
        labeled_strip(
            [
                base,
                delta_visual(positive, args.preview_gain),
                delta_visual(negative, args.preview_gain),
                reconstructed,
                selected,
                diff_image(reconstructed, selected),
            ],
            ["base", "+response", "-response", "reconstructed", "selected", "diff"],
            strip_path,
        )
        strips.append(strip_path)
        stats = {
            **delta_stats,
            "reconstruction_mean_abs_diff": recon_mean,
            "reconstruction_max_abs_diff": recon_max,
            "selected_full_mean_abs_diff": full_mean,
            "selected_full_max_abs_diff": full_max,
        }
        frames.append({
            "frame": response_frame.get("sequence_frame"),
            "output_frame": output,
            "response_scale": scale,
            "references": {
                "base_rgb": file_ref(base_path, "base_rgb", "aov", root),
                "response_positive_rgb": file_ref(pos_path, "response_positive_rgb", "aov", root),
                "response_negative_rgb": file_ref(neg_path, "response_negative_rgb", "aov", root),
                "selected_composite_rgb": file_ref(selected_path, "selected_composite_rgb", "aov", root),
                "full_render_rgb": file_ref(full_path, "full_render_rgb", "reference", root),
                "reconstructed_rgb": file_ref(recon_path, "reconstructed_rgb", "validation", root),
            },
            "strip_repo_path": posix_rel(strip_path, root),
            "stats": stats,
        })

    if not frames:
        raise SystemExit("no response-AOV frames were built")

    gif_path = os.path.join(out_dir, "response_aov_contract.gif")
    write_gif(strips, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strips) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "response_aov_contract.gif", "Response AOV GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"response_aov_strip_{out_index:02d}.png", f"Response AOV Strip {out_index + 1}", root))

    s577_source, s577_gap = gap_source(args.s577_gap_summary, root) if args.s577_gap_summary else (None, None)
    s585_source, s585_gap = gap_source(args.s585_gap_summary, root) if args.s585_gap_summary else (None, None)
    gate_metrics = {}
    for key, gap in (("s577", s577_gap), ("s585", s585_gap)):
        if gap:
            checks = gap.get("checks") or {}
            gate_metrics[key] = {
                "mean_gap_mean_abs_diff": checks.get("mean_gap_mean_abs_diff"),
                "max_gap_mean_abs_diff": checks.get("max_gap_mean_abs_diff"),
                "max_gap_max_abs_diff": checks.get("max_gap_max_abs_diff"),
                "frames": checks.get("frames"),
            }

    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "response_scale": scale,
        "mean_abs_signed_delta": sum((frame.get("stats") or {}).get("mean_abs_signed_delta") or 0.0 for frame in frames) / len(frames),
        "max_abs_signed_delta": max((frame.get("stats") or {}).get("max_abs_signed_delta") or 0 for frame in frames),
        "changed_channel_fraction": sum((frame.get("stats") or {}).get("changed_channel_fraction") or 0.0 for frame in frames) / len(frames),
        "reconstruction_max_abs_diff": max((frame.get("stats") or {}).get("reconstruction_max_abs_diff") or 0 for frame in frames),
        "reconstruction_max_mean_abs_diff": max((frame.get("stats") or {}).get("reconstruction_mean_abs_diff") or 0.0 for frame in frames),
        "selected_full_max_mean_abs_diff": max((frame.get("stats") or {}).get("selected_full_mean_abs_diff") or 0.0 for frame in frames),
        "selected_full_max_abs_diff": max((frame.get("stats") or {}).get("selected_full_max_abs_diff") or 0 for frame in frames),
        "aov_bytes": sum(
            (frame["references"][role]["size"])
            for frame in frames
            for role in ("base_rgb", "response_positive_rgb", "response_negative_rgb", "selected_composite_rgb")
        ),
        "composite_bytes": sum(frame["references"]["selected_composite_rgb"]["size"] for frame in frames),
        "gif_bytes": os.path.getsize(gif_path),
    }
    status = "ready"
    if missing or checks["reconstruction_max_abs_diff"] != 0:
        status = "failed"

    contract_path = os.path.join(out_dir, args.contract_name)
    generated_utc = datetime.now(timezone.utc).isoformat()
    contract = {
        "schema": "lsfs_mitsuba_response_aov_contract",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "sources": {
            "response_delta_buffer": json_source(response_path, root, response),
            "response_scale_composite": json_source(composite_summary_path, root, composite),
            "s577_gap": s577_source,
            "s585_gap": s585_source,
        },
        "settings": {
            "response_scale": scale,
            "composition": "selected_composite_rgb = base_rgb + response_positive_rgb - response_negative_rgb",
            "preview_gain": args.preview_gain,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "gate_metrics": gate_metrics,
        "missing_references": missing,
        "frames": frames,
        "gallery": {},
        "next": args.next,
    }
    write_json(contract_path, contract)
    metadata_files = [copy_asset(contract_path, assets_dir, "response_aov_contract.json", "Response AOV contract", root)]
    metadata_files.append(copy_asset(response_path, assets_dir, "response_delta_buffer_summary.json", "Response delta buffer", root))
    metadata_files.append(copy_asset(composite_summary_path, assets_dir, "response_scale_composite_summary.json", "Response scale composite", root))
    for source, name, label in (
        (args.s577_gap_summary, "s577_gap_summary.json", "S577 gap summary"),
        (args.s585_gap_summary, "s585_gap_summary.json", "S585 gap summary"),
    ):
        if source:
            metadata_files.append(copy_asset(require_file(source, label), assets_dir, name, label, root))
    gallery_index = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    contract["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": gallery_index,
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(contract_path, contract)
    shutil.copy2(contract_path, metadata_files[0]["asset"])
    write_text(gallery_index, html_page(args.title, contract, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_response_aov_contract_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "summary_repo_path": posix_rel(contract_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(contract, contract_path, root))
    print(
        f"status={status} frames={checks['frames']} scale={scale:g} "
        f"recon_max={checks['reconstruction_max_abs_diff']} out={contract_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a signed response-AOV contract")
    parser.add_argument("response_summary")
    parser.add_argument("composite_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--s577-gap-summary")
    parser.add_argument("--s585-gap-summary")
    parser.add_argument("--contract-name", default="response_aov_contract.json")
    parser.add_argument("--report")
    parser.add_argument("--preview-gain", type=float, default=4.0)
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--title", default="Mitsuba Response AOV Contract")
    parser.add_argument(
        "--next",
        default="Use this signed response-AOV contract as the portable input for renderer-native pass export and cache handoff.",
    )
    args = parser.parse_args(argv)
    if args.preview_gain < 0.0:
        parser.error("preview-gain must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    run(args)


if __name__ == "__main__":
    main()
