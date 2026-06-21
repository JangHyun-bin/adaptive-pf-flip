#!/usr/bin/env python
"""Consume a signed Mitsuba response-AOV contract into a composite summary."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
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
from compare_mitsuba_renderer_target_gap import max_abs_diff, mean_abs_diff, write_gif


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to consume a response-AOV contract")


def resolve_path(path, root):
    if not path:
        return None
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(root, str(path).replace("/", os.sep)))


def ref_path(frame, role):
    return (((frame.get("references") or {}).get(role) or {}).get("path")
            or ((frame.get("references") or {}).get(role) or {}).get("repo_path"))


def copy_asset(src, assets_dir, name, label, root):
    dst = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dst):
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())
    entry = {
        "label": label,
        "asset": os.path.abspath(dst),
        "repo_path": posix_rel(os.path.abspath(dst), root),
        "href": f"assets/{name}",
        "sha256": sha256_file(dst),
        "size": os.path.getsize(dst),
    }
    dims = image_dimensions(dst)
    if dims:
        entry["dimensions"] = dims
    return entry


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


def layer_visual(layer, gain):
    if gain <= 1.0:
        return layer.convert("RGB")
    return Image.eval(layer.convert("RGB"), lambda value: max(0, min(255, int(round(value * gain)))))


def diff_image(a, b):
    return ImageChops.multiply(ImageChops.difference(a.convert("RGB"), b.convert("RGB")), Image.new("RGB", a.size, (8, 8, 8)))


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


def html_page(title, summary, assets, metadata_files):
    checks = summary.get("checks") or {}
    gif = next((item for item in assets if item["label"] == "Response AOV Consumer GIF"), None)
    strips = [item for item in assets if item["label"].startswith("Response AOV Consumer Strip")]
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Scale", summary.get("settings", {}).get("response_scale")),
            ("Max Diff", checks.get("max_import_abs_diff")),
            ("Mean Diff", f"{checks.get('max_import_mean_abs_diff', 0.0):.6f}"),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="response AOV consumer GIF"></section>' if gif else ""
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
        "## Inputs",
        "",
        f"- Response AOV contract: `{summary['response_aov_contract']['repo_path']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Response scale: `{summary['settings']['response_scale']}`",
        f"- Max import absolute diff: `{checks.get('max_import_abs_diff')}`",
        f"- Max import mean absolute diff: `{checks.get('max_import_mean_abs_diff')}`",
        f"- Max import mismatched coverage: `{checks.get('max_import_mismatched_coverage')}`",
        f"- Composite bytes: `{format_bytes(checks.get('composite_bytes', 0))}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Output | Import Mean Diff | Import Max Diff | Composite | Strip |",
        "| ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    sample_indices = sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []
    for index in sample_indices:
        frame = frames[index]
        lines.append(
            f"| {frame.get('output_frame')} | {frame.get('import_mean_abs_diff')} | "
            f"{frame.get('import_max_abs_diff')} | `{frame.get('composite_repo_path')}` | "
            f"`{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next") or "", ""])
    return "\n".join(lines)


def consume(args):
    require_pillow()
    root = os.getcwd()
    contract_path = require_file(args.contract, "response AOV contract")
    contract = read_json(contract_path)
    if contract.get("schema") != "lsfs_mitsuba_response_aov_contract":
        raise SystemExit(f"{args.contract}: expected lsfs_mitsuba_response_aov_contract schema")
    if contract.get("status") != "ready":
        raise SystemExit(f"{args.contract}: contract status is {contract.get('status')!r}")

    out_dir = os.path.abspath(args.out_dir)
    composite_dir = os.path.join(out_dir, "composites")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(composite_dir, exist_ok=True)
    os.makedirs(strip_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    frames = []
    strips = []
    missing = []
    for index, frame in enumerate(contract.get("frames") or []):
        paths = {
            role: resolve_path(ref_path(frame, role), root)
            for role in ("base_rgb", "response_positive_rgb", "response_negative_rgb", "selected_composite_rgb")
        }
        absent = [role for role, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"output_frame": frame.get("output_frame"), "missing": absent})
            continue
        base = Image.open(paths["base_rgb"]).convert("RGB")
        positive = Image.open(paths["response_positive_rgb"]).convert("RGB")
        negative = Image.open(paths["response_negative_rgb"]).convert("RGB")
        expected = Image.open(paths["selected_composite_rgb"]).convert("RGB")
        if any(img.size != base.size for img in (positive, negative, expected)):
            raise SystemExit(f"frame {index}: response AOV dimensions differ")
        composite = reconstruct(base, positive, negative)
        import_mean = mean_abs_diff(composite, expected)
        import_max = max_abs_diff(composite, expected)
        diff = ImageChops.difference(composite, expected).convert("RGB")
        diff_bytes = diff.tobytes()
        mismatched = 0
        for offset in range(0, len(diff_bytes), 3):
            if max(diff_bytes[offset], diff_bytes[offset + 1], diff_bytes[offset + 2]) != 0:
                mismatched += 1
        mismatch_coverage = mismatched / float(max(1, base.size[0] * base.size[1]))
        composite_path = os.path.join(composite_dir, f"frame_{index:04d}.png")
        strip_path = os.path.join(strip_dir, f"frame_{index:04d}.png")
        composite.save(composite_path)
        labeled_strip(
            [base, layer_visual(positive, args.preview_gain), layer_visual(negative, args.preview_gain), composite, expected, diff_image(composite, expected)],
            ["base", "+response", "-response", "consumer", "expected", "diff"],
            strip_path,
        )
        strips.append(strip_path)
        frames.append({
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            "source_repo_path": posix_rel(paths["base_rgb"], root),
            "target_repo_path": posix_rel(paths["selected_composite_rgb"], root),
            "composite_path": composite_path,
            "composite_repo_path": posix_rel(composite_path, root),
            "strip_repo_path": posix_rel(strip_path, root),
            "sha256": sha256_file(composite_path),
            "size": os.path.getsize(composite_path),
            "response": (frame.get("stats") or {}),
            "import_mean_abs_diff": import_mean,
            "import_max_abs_diff": import_max,
            "import_mismatched_coverage": mismatch_coverage,
        })

    if not frames:
        raise SystemExit("no response-AOV frames were consumed")
    gif_path = os.path.join(out_dir, "response_aov_consumer.gif")
    write_gif(strips, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strips) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "response_aov_consumer.gif", "Response AOV Consumer GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strips[frame_index], assets_dir, f"response_aov_consumer_strip_{out_index:02d}.png", f"Response AOV Consumer Strip {out_index + 1}", root))

    status = "ready"
    if missing:
        status = "failed"
    if max(frame["import_max_abs_diff"] for frame in frames) > args.max_abs_tolerance:
        status = "failed"
    if max(frame["import_mean_abs_diff"] for frame in frames) > args.mean_abs_tolerance:
        status = "failed"

    summary_path = os.path.join(out_dir, args.summary_name)
    generated_utc = datetime.now(timezone.utc).isoformat()
    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "response_scale": (contract.get("settings") or {}).get("response_scale"),
        "max_import_abs_diff": max(frame["import_max_abs_diff"] for frame in frames),
        "max_import_mean_abs_diff": max(frame["import_mean_abs_diff"] for frame in frames),
        "max_import_mismatched_coverage": max(frame["import_mismatched_coverage"] for frame in frames),
        "composite_bytes": sum(frame["size"] for frame in frames),
        "gif_bytes": os.path.getsize(gif_path),
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
    summary = {
        "schema": "lsfs_mitsuba_secondary_composite",
        "subschema": "lsfs_mitsuba_response_aov_consumer",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "status": status,
        "response_aov_contract": {
            "path": contract_path,
            "repo_path": posix_rel(contract_path, root),
            "sha256": sha256_file(contract_path),
            "schema": contract.get("schema"),
            "status": contract.get("status"),
        },
        "settings": {
            "response_scale": (contract.get("settings") or {}).get("response_scale"),
            "composition": "base_rgb + response_positive_rgb - response_negative_rgb",
            "preview_gain": args.preview_gain,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "frames": frames,
        "missing_references": missing,
        "gallery": {},
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files = [
        copy_asset(summary_path, assets_dir, "response_aov_consumer_summary.json", "Response AOV consumer summary", root),
        copy_asset(contract_path, assets_dir, "response_aov_contract.json", "Response AOV contract", root),
    ]
    gallery_index = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary["gallery"] = {
        "path": gallery_dir,
        "repo_path": posix_rel(gallery_dir, root),
        "index_path": gallery_index,
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    }
    write_json(summary_path, summary)
    with open(summary_path, "rb") as f_in, open(metadata_files[0]["asset"], "wb") as f_out:
        f_out.write(f_in.read())
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_response_aov_consumer_gallery",
        "version": 1,
        "generated_utc": generated_utc,
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} max_abs={checks['max_import_abs_diff']} "
        f"summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consume a signed response-AOV contract")
    parser.add_argument("contract")
    parser.add_argument("out_dir")
    parser.add_argument("--summary-name", default="response_aov_consumer_summary.json")
    parser.add_argument("--report")
    parser.add_argument("--preview-gain", type=float, default=4.0)
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--keyframes", type=int, default=6)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="Mitsuba Response AOV Consumer")
    parser.add_argument(
        "--next",
        default="Use this consumer as the import gate for renderer/cache handoff integration.",
    )
    args = parser.parse_args(argv)
    if args.preview_gain < 0.0:
        parser.error("preview-gain must be non-negative")
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    consume(args)


if __name__ == "__main__":
    main()
