#!/usr/bin/env python
"""Build a self-contained static gallery for cinematic review artifacts."""

import argparse
import html
import json
import os
import shutil
from datetime import datetime, timezone

from package_cinematic_artifacts import collect_artifacts, format_bytes, posix_rel, read_json, summary_lines


def slug_name(row):
    fixed = {
        "gif": "shot.gif",
    }
    if row["key"] in fixed:
        return fixed[row["key"]]
    _, ext = os.path.splitext(row["path"])
    base = row["key"].replace("_sheet", "").replace("_comparison", "_compare")
    return f"{base}{ext.lower()}"


def copy_artifacts(rows, out_dir):
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    copied = []
    for row in rows:
        if not row["exists"]:
            continue
        asset_name = slug_name(row)
        dest = os.path.join(assets_dir, asset_name)
        shutil.copy2(row["path"], dest)
        copied.append({
            **row,
            "asset_name": asset_name,
            "asset_path": dest,
            "asset_href": f"assets/{asset_name}",
        })
    return copied


def copy_optional_file(src, out_dir, asset_name):
    if not src or not os.path.isfile(src):
        return None
    dest = os.path.join(out_dir, "assets", asset_name)
    shutil.copy2(src, dest)
    return {
        "label": asset_name,
        "source": os.path.abspath(src),
        "asset": dest,
        "href": f"assets/{asset_name}",
        "size": os.path.getsize(dest),
    }


def compact_summary(summary):
    config = summary.get("config", {})
    metrics = summary.get("metrics", {})
    export_metrics = summary.get("export_metrics", {})
    validation = summary.get("validation_metrics", {})
    return {
        "status": summary.get("status", "n/a"),
        "renderer": summary.get("selected_renderer", summary.get("requested_renderer", "n/a")),
        "preset": summary.get("shot_preset", config.get("preset", "n/a")),
        "grid": [config.get("nx"), config.get("ny"), config.get("nz")],
        "frames": config.get("frames", metrics.get("cache_frame_count")),
        "samples": config.get("samples"),
        "export_particles": export_metrics.get("particles"),
        "validated_particles": validation.get("particles"),
        "gif_bytes": metrics.get("shot_gif_bytes"),
        "comparison_sources": metrics.get("comparison_source_count"),
        "visual_gate": metrics.get("visual_qa_gate", {}).get("passed"),
        "focus_gate": metrics.get("focus_review_gate", {}).get("passed"),
        "secondary_depth_gate": metrics.get("secondary_depth_review_gate", {}).get("passed"),
        "ripple_gate": metrics.get("ripple_readability_gate", {}).get("passed"),
    }


def metric_tiles(summary):
    data = compact_summary(summary)
    grid = data["grid"]
    grid_text = " x ".join(str(v) for v in grid if v is not None) or "n/a"
    return [
        ("Status", data["status"]),
        ("Renderer", data["renderer"]),
        ("Grid", grid_text),
        ("Frames", data["frames"]),
        ("Samples", data["samples"]),
        ("Export Particles", data["export_particles"]),
        ("Validated Particles", data["validated_particles"]),
        ("Comparison Sources", data["comparison_sources"]),
        ("Visual Gate", data["visual_gate"]),
        ("Focus Gate", data["focus_gate"]),
        ("Secondary Depth", data["secondary_depth_gate"]),
        ("Ripple Gate", data["ripple_gate"]),
    ]


def image_block(row):
    dims = row.get("dimensions")
    dim_text = "n/a"
    if dims:
        dim_text = f"{dims[0]} x {dims[1]}"
    return f"""
      <figure class=\"artifact\">
        <a href=\"{html.escape(row['asset_href'])}\"><img src=\"{html.escape(row['asset_href'])}\" alt=\"{html.escape(row['label'])}\"></a>
        <figcaption>
          <strong>{html.escape(row['label'])}</strong>
          <span>{html.escape(dim_text)} · {html.escape(format_bytes(row.get('size')))}</span>
        </figcaption>
      </figure>"""


def html_page(summary, copied, optional_files, package_href, manifest_href):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = "Cinematic Review Gallery"
    preset = compact_summary(summary)["preset"]
    hero = next((row for row in copied if row["key"] == "gif"), None)
    primary = [row for row in copied if row["key"] in {
        "contact_sheet",
        "comparison_sheet",
        "focus_comparison_sheet",
        "secondary_depth_comparison_sheet",
        "ripple_readability_comparison_sheet",
    }]
    diagnostics = [row for row in copied if row["preview"] and row not in primary and row["key"] != "gif"]
    meta_rows = []
    for label, value in metric_tiles(summary):
        meta_rows.append(
            f"<div class=\"metric\"><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>"
        )
    links = [
        ("Gallery manifest", manifest_href),
    ]
    if package_href:
        links.append(("Markdown package", package_href))
    for item in optional_files:
        links.append((item["label"], item["href"]))
    link_items = "\n".join(
        f"<li><a href=\"{html.escape(href)}\">{html.escape(label)}</a></li>" for label, href in links if href
    )

    hero_markup = ""
    if hero:
        hero_markup = f"""
    <section class=\"hero\">
      <img src=\"{html.escape(hero['asset_href'])}\" alt=\"{html.escape(hero['label'])}\">
    </section>"""

    primary_markup = "\n".join(image_block(row) for row in primary)
    diagnostic_markup = "\n".join(image_block(row) for row in diagnostics)

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8f5;
      --ink: #18201b;
      --muted: #5c665f;
      --line: #d7ded4;
      --panel: #ffffff;
      --accent: #196c5b;
      --accent-soft: #d8eee8;
      --shadow: 0 10px 28px rgba(24, 32, 27, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    header {{
      padding: 28px min(5vw, 56px) 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0;
      font-size: 34px;
      line-height: 1.1;
      font-weight: 760;
      letter-spacing: 0;
    }}
    .subhead {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.45;
      overflow-wrap: anywhere;
    }}
    main {{
      width: min(1520px, 100%);
      margin: 0 auto;
      padding: 22px min(5vw, 56px) 48px;
    }}
    .hero {{
      margin: 0 0 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: #101512;
      box-shadow: var(--shadow);
    }}
    .hero img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 0 0 22px;
    }}
    .metric {{
      min-height: 72px;
      padding: 13px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }}
    .metric strong {{
      display: block;
      margin-top: 8px;
      font-size: 17px;
      line-height: 1.15;
      overflow-wrap: anywhere;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 22px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 430px), 1fr));
      gap: 16px;
    }}
    figure.artifact {{
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: hidden;
      box-shadow: var(--shadow);
    }}
    figure.artifact img {{
      display: block;
      width: 100%;
      height: auto;
      background: #101512;
    }}
    figcaption {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }}
    figcaption strong {{
      color: var(--ink);
      font-size: 14px;
      overflow-wrap: anywhere;
    }}
    .links {{
      margin: 0;
      padding: 14px 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      columns: 2 280px;
    }}
    .links li {{
      margin: 5px 0;
      break-inside: avoid;
    }}
    a {{
      color: var(--accent);
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }}
    footer {{
      padding: 0 min(5vw, 56px) 28px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 720px) {{
      header {{ padding-top: 22px; }}
      h1 {{ font-size: 28px; }}
      main {{ padding-top: 16px; }}
      figcaption {{ display: block; }}
      figcaption span {{ display: block; margin-top: 4px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <div class=\"subhead\">{html.escape(str(preset))} · generated {html.escape(now)}</div>
  </header>
  <main>
    {hero_markup}
    <section class=\"metrics\">
      {''.join(meta_rows)}
    </section>
    <h2>Comparison Review</h2>
    <section class=\"grid\">
      {primary_markup}
    </section>
    <h2>Diagnostics</h2>
    <section class=\"grid\">
      {diagnostic_markup}
    </section>
    <h2>Files</h2>
    <ul class=\"links\">
      {link_items}
    </ul>
  </main>
  <footer>Generated by tools/build_cinematic_gallery.py.</footer>
</body>
</html>
"""


def write_manifest(path, summary, rows, optional_files, root, package_path):
    data = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary": compact_summary(summary),
        "package": posix_rel(package_path, root) if package_path else None,
        "artifacts": [
            {
                "key": row["key"],
                "label": row["label"],
                "description": row["description"],
                "required": row["required"],
                "preview": row["preview"],
                "source": posix_rel(row["path"], root),
                "asset": posix_rel(row["asset_path"], root),
                "size": row["size"],
                "dimensions": row["dimensions"],
            }
            for row in rows
        ],
        "optional_files": [
            {
                "label": item["label"],
                "source": posix_rel(item["source"], root),
                "asset": posix_rel(item["asset"], root),
                "size": item["size"],
            }
            for item in optional_files
        ],
    }
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def markdown_report(summary, shot_dir, out_dir, index_path, manifest_path, rows, optional_files, package_path, root):
    copied_count = len(rows)
    required_count = sum(1 for row in rows if row["required"])
    lines = [
        "# Cinematic Static Gallery",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Shot directory: `{posix_rel(shot_dir, root)}`",
        f"Gallery index: `{posix_rel(index_path, root)}`",
        f"Gallery manifest: `{posix_rel(manifest_path, root)}`",
    ]
    if package_path:
        lines.append(f"Source package: `{posix_rel(package_path, root)}`")
    lines.extend([
        "",
        "## Shot Summary",
        "",
        *summary_lines(summary),
        "",
        "## Gallery Contents",
        "",
        f"- Copied artifacts: `{copied_count}`",
        f"- Required visual artifacts: `{required_count}`",
        f"- Output directory: `{posix_rel(out_dir, root)}`",
        "",
        "| Asset | Size | Dimensions | Gallery path |",
        "| --- | ---: | --- | --- |",
    ])
    for row in rows:
        dims = row.get("dimensions")
        dims_text = "n/a"
        if dims:
            dims_text = f"{dims[0]} x {dims[1]}"
        lines.append(
            f"| {row['label']} | {format_bytes(row.get('size'))} | `{dims_text}` | `{posix_rel(row['asset_path'], root)}` |"
        )
    if optional_files:
        lines.extend(["", "## Metadata Files", ""])
        for item in optional_files:
            lines.append(f"- `{posix_rel(item['asset'], root)}` ({format_bytes(item['size'])})")
    lines.extend([
        "",
        "## Next",
        "",
        "S125 should add a contact-volume integration preset that softens the remaining boxed/tank read.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("shot_dir", help="Cinematic shot directory")
    parser.add_argument("--package", dest="package_path", help="Optional Markdown artifact package to copy into the gallery")
    parser.add_argument("--out", required=True, help="Output gallery directory")
    parser.add_argument("--report", help="Optional Markdown report path")
    args = parser.parse_args(argv)

    root = os.getcwd()
    shot_dir = os.path.abspath(args.shot_dir)
    summary_path = os.path.join(shot_dir, "shot_summary.json")
    if not os.path.isfile(summary_path):
        raise SystemExit(f"Missing shot summary: {summary_path}")
    summary = read_json(summary_path)

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    rows = collect_artifacts(summary, shot_dir, strict=True)
    copied = copy_artifacts(rows, out_dir)

    package_path = os.path.abspath(args.package_path) if args.package_path else None
    optional_files = []
    optional_files.append(copy_optional_file(summary_path, out_dir, "shot_summary.json"))
    if package_path:
        optional_files.append(copy_optional_file(package_path, out_dir, "artifact_package.md"))
    optional_files = [item for item in optional_files if item]

    manifest_path = os.path.join(out_dir, "gallery_manifest.json")
    write_manifest(manifest_path, summary, copied, optional_files, root, package_path)
    manifest_href = "gallery_manifest.json"
    package_href = "assets/artifact_package.md" if package_path and os.path.isfile(package_path) else None
    index_path = os.path.join(out_dir, "index.html")
    with open(index_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html_page(summary, copied, optional_files, package_href, manifest_href))

    if args.report:
        report_path = os.path.abspath(args.report)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(markdown_report(summary, shot_dir, out_dir, index_path, manifest_path, copied, optional_files, package_path, root))
        print(report_path)
    print(index_path)


if __name__ == "__main__":
    main()
