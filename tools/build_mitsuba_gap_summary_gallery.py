#!/usr/bin/env python
"""Build a compact gallery from Mitsuba target-gap summaries."""

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


def parse_candidate(value):
    if "=" not in value:
        path = value
        label = os.path.splitext(os.path.basename(os.path.dirname(path)))[0]
        return label, path
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("candidate label cannot be empty")
    return label, path.strip()


def resolve_path(path):
    if os.path.isabs(path):
        return os.path.abspath(path)
    return os.path.abspath(str(path).replace("/", os.sep))


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
    entry = {
        "label": label,
        "path": dest,
        "repo_path": posix_rel(dest, root),
        "href": "assets/" + name.replace(os.sep, "/"),
        "source": os.path.abspath(src),
        "source_repo_path": posix_rel(src, root),
        "size": os.path.getsize(dest),
        "sha256": sha256_file(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def summary_gallery_assets(summary):
    gallery = summary.get("gallery") or {}
    for item in gallery.get("assets") or []:
        yield item


def asset_source_path(item):
    return item.get("source") or item.get("source_repo_path") or item.get("asset") or item.get("repo_path")


def metric_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def html_page(title, items, summary):
    rows = []
    cards = []
    for rank, item in enumerate(items, start=1):
        checks = item["checks"]
        gallery = item["gallery"]
        gif = gallery.get("gif")
        strip_links = " ".join(
            f'<a href="{html.escape(strip["href"])}">{html.escape(strip["label"])}</a>'
            for strip in gallery.get("strips", [])
        )
        rows.append(
            "<tr>"
            f"<td>{rank}</td>"
            f"<td><code>{html.escape(item['label'])}</code></td>"
            f"<td>{html.escape(item['status'])}</td>"
            f"<td>{checks.get('frames')}</td>"
            f"<td>{checks.get('mean_gap_mean_abs_diff'):.6f}</td>"
            f"<td>{checks.get('max_gap_mean_abs_diff'):.6f}</td>"
            f"<td>{checks.get('max_gap_max_abs_diff')}</td>"
            f"<td>{html.escape(format_bytes(checks.get('gif_bytes', 0)))}</td>"
            "</tr>"
        )
        media = f'<img src="{html.escape(gif["href"])}" alt="{html.escape(item["label"])} gap GIF">' if gif else ""
        cards.append(
            "<section class=\"candidate\">"
            f"<h2>{rank}. {html.escape(item['label'])}</h2>"
            "<div class=\"metrics\">"
            f"<span>Mean MAD <strong>{checks.get('mean_gap_mean_abs_diff'):.3f}</strong></span>"
            f"<span>Max MAD <strong>{checks.get('max_gap_mean_abs_diff'):.3f}</strong></span>"
            f"<span>Max Diff <strong>{checks.get('max_gap_max_abs_diff')}</strong></span>"
            "</div>"
            f"{media}"
            f"<p class=\"links\">{strip_links}</p>"
            "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #070b0f; --panel: #101820; --ink: #edf7fb; --muted: #9eb2bc; --line: #2b3a44; --accent: #93d5ff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 18px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    .meta {{ color: var(--muted); font-size: 13px; text-align: right; }}
    table {{ width: 100%; border-collapse: collapse; margin: 0 0 22px; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; font-size: 13px; }}
    th {{ color: var(--muted); font-weight: 600; }}
    code {{ color: var(--accent); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; }}
    .candidate {{ background: var(--panel); border: 1px solid var(--line); padding: 14px; }}
    .candidate h2 {{ margin: 0 0 10px; font-size: 17px; font-weight: 650; letter-spacing: 0; }}
    .metrics {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; color: var(--muted); }}
    .metrics span {{ border: 1px solid var(--line); padding: 6px 8px; font-size: 12px; }}
    .metrics strong {{ color: var(--ink); font-weight: 650; }}
    img {{ width: 100%; height: auto; display: block; border: 1px solid var(--line); background: #020406; }}
    .links {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0 0; font-size: 13px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{html.escape(title)}</h1>
    <div class="meta">Generated {html.escape(summary["generated_utc"])}<br>Best {html.escape(summary["best_candidate"])}</div>
  </header>
  <table>
    <thead><tr><th>Rank</th><th>Candidate</th><th>Status</th><th>Frames</th><th>Mean MAD</th><th>Max MAD</th><th>Max Diff</th><th>GIF</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  <div class="grid">
    {''.join(cards)}
  </div>
</main>
</body>
</html>
"""


def markdown_report(summary, summary_path, root, next_text):
    lines = [
        f"# {summary['title']}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Summary JSON: `{posix_rel(summary_path, root)}`",
        f"Gallery: `{summary['gallery']['index_repo_path']}`",
        f"Best candidate: `{summary['best_candidate']}`",
        f"Best max gap MAD: `{summary['best_max_gap_mean_abs_diff']}`",
        "",
        "## Ranking",
        "",
        "| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | GIF |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for rank, item in enumerate(summary.get("candidates") or [], start=1):
        checks = item.get("checks") or {}
        gif = ((item.get("gallery") or {}).get("gif") or {}).get("repo_path")
        lines.append(
            f"| {rank} | `{item.get('label')}` | `{item.get('status')}` | "
            f"{checks.get('frames')} | {checks.get('mean_gap_mean_abs_diff')} | "
            f"{checks.get('max_gap_mean_abs_diff')} | {checks.get('max_gap_max_abs_diff')} | `{gif}` |"
        )
    lines.extend(["", "## Next", "", next_text, ""])
    return "\n".join(lines)


def build(args):
    root = os.getcwd()
    out_dir = os.path.abspath(args.out_dir)
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    candidates = []
    copied_assets = []
    for raw in args.candidate:
        label, path = parse_candidate(raw)
        summary_path = require_file(path, f"{label} target-gap summary")
        summary = read_json(summary_path)
        if summary.get("schema") != "lsfs_mitsuba_renderer_target_gap":
            raise SystemExit(f"{path}: expected lsfs_mitsuba_renderer_target_gap schema")
        checks = summary.get("checks") or {}
        label_dir = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label)
        gallery_assets = {"strips": []}
        for asset in summary_gallery_assets(summary):
            source = resolve_path(asset_source_path(asset))
            if not source or not os.path.isfile(source):
                continue
            asset_label = asset.get("label") or ""
            if asset_label == "Gap GIF":
                copied = copy_asset(source, assets_dir, f"{label_dir}/shot.gif", f"{label} Gap GIF", root)
                gallery_assets["gif"] = copied
                copied_assets.append(copied)
            elif asset_label.startswith("Gap Strip"):
                name = os.path.basename(asset.get("href") or asset.get("repo_path") or source)
                copied = copy_asset(source, assets_dir, f"{label_dir}/{name}", f"{label} {asset_label}", root)
                gallery_assets["strips"].append(copied)
                copied_assets.append(copied)
        candidates.append({
            "label": label,
            "status": summary.get("status"),
            "summary": {
                "path": summary_path,
                "repo_path": posix_rel(summary_path, root),
                "sha256": sha256_file(summary_path),
                "size": os.path.getsize(summary_path),
            },
            "checks": {
                "frames": int(checks.get("frames") or 0),
                "mean_gap_mean_abs_diff": float(checks.get("mean_gap_mean_abs_diff") or 0.0),
                "max_gap_mean_abs_diff": float(checks.get("max_gap_mean_abs_diff") or 0.0),
                "max_gap_max_abs_diff": int(checks.get("max_gap_max_abs_diff") or 0),
                "gif_bytes": int(checks.get("gif_bytes") or 0),
            },
            "gallery": gallery_assets,
        })

    candidates.sort(key=lambda item: metric_float((item.get("checks") or {}).get("max_gap_mean_abs_diff")))
    if not candidates:
        raise SystemExit("no candidates were loaded")
    best = candidates[0]
    generated = datetime.now(timezone.utc).isoformat()
    summary_path = os.path.join(out_dir, "gap_summary_gallery.json")
    index_path = os.path.join(gallery_dir, "index.html")
    gallery_manifest_path = os.path.join(gallery_dir, "gallery_manifest.json")
    summary = {
        "schema": "lsfs_mitsuba_gap_summary_gallery",
        "version": 1,
        "generated_utc": generated,
        "title": args.title,
        "status": "ready",
        "best_candidate": best["label"],
        "best_max_gap_mean_abs_diff": best["checks"]["max_gap_mean_abs_diff"],
        "candidates": candidates,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": index_path,
            "index_repo_path": posix_rel(index_path, root),
            "assets": copied_assets,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    write_text(index_path, html_page(args.title, candidates, summary))
    write_json(gallery_manifest_path, {
        "schema": "lsfs_mitsuba_gap_summary_gallery_manifest",
        "version": 1,
        "generated_utc": generated,
        "title": args.title,
        "index": index_path,
        "index_repo_path": posix_rel(index_path, root),
        "summary": summary_path,
        "summary_repo_path": posix_rel(summary_path, root),
        "assets": copied_assets,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root, args.next))
    print(
        f"status=ready candidates={len(candidates)} best={best['label']} "
        f"max_gap={best['checks']['max_gap_mean_abs_diff']} gallery={index_path}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a visual gallery from Mitsuba target-gap summaries")
    parser.add_argument("out_dir")
    parser.add_argument("--candidate", action="append", required=True, help="LABEL=renderer_target_gap_summary.json")
    parser.add_argument("--title", default="Mitsuba Gap Summary Gallery")
    parser.add_argument("--report")
    parser.add_argument("--next", default="Use this visual comparison to choose the next renderer-native response direction.")
    args = parser.parse_args(argv)
    build(args)


if __name__ == "__main__":
    main()
