#!/usr/bin/env python
"""Profile stage timings from a cinematic benchmark summary Markdown table."""

import argparse
import os
import re
from datetime import datetime, timezone


STAGES = ["Export", "Validate", "Reconstruct", "Convert", "Render"]
NON_RENDER_STAGES = ["Export", "Validate", "Reconstruct", "Convert"]


def parse_seconds(value):
    match = re.search(r"([-+]?\d+(?:\.\d+)?)s\b", value)
    if not match:
        return 0.0
    return float(match.group(1))


def parse_markdown_table(path):
    rows = []
    header = None
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line.startswith("|"):
                if header and rows:
                    break
                continue
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            if not header:
                if "Gate" in cells and "Total" in cells:
                    header = cells
                continue
            if all(set(cell) <= {"-", ":"} for cell in cells):
                continue
            if len(cells) != len(header):
                continue
            rows.append(dict(zip(header, cells)))
    if not header or not rows:
        raise ValueError(f"No cinematic benchmark table found in {path}")
    return rows


def enrich(row):
    enriched = dict(row)
    for stage in STAGES + ["Total"]:
        enriched[f"{stage}_s"] = parse_seconds(row.get(stage, "0s"))
    enriched["Non-render_s"] = sum(enriched[f"{stage}_s"] for stage in NON_RENDER_STAGES)
    total = enriched["Total_s"]
    enriched["Render_pct"] = 100.0 * enriched["Render_s"] / total if total > 0 else 0.0
    enriched["Non-render_pct"] = 100.0 * enriched["Non-render_s"] / total if total > 0 else 0.0
    top_non_render = max(NON_RENDER_STAGES, key=lambda stage: enriched[f"{stage}_s"])
    enriched["Top_non_render"] = top_non_render
    return enriched


def average(rows, label):
    out = {"label": label, "count": len(rows)}
    for stage in STAGES + ["Total", "Non-render"]:
        out[f"{stage}_s"] = sum(row[f"{stage}_s"] for row in rows) / len(rows) if rows else 0.0
    total = out["Total_s"]
    out["Render_pct"] = 100.0 * out["Render_s"] / total if total > 0 else 0.0
    out["Non-render_pct"] = 100.0 * out["Non-render_s"] / total if total > 0 else 0.0
    return out


def fmt_seconds(value):
    return f"{value:.2f}s"


def fmt_pct(value):
    return f"{value:.1f}%"


def stage_ranking(rows):
    if not rows:
        return []
    totals = []
    total_s = sum(row["Total_s"] for row in rows) / len(rows)
    for stage in STAGES:
        avg_s = sum(row[f"{stage}_s"] for row in rows) / len(rows)
        totals.append((stage, avg_s, 100.0 * avg_s / total_s if total_s > 0 else 0.0))
    return sorted(totals, key=lambda item: item[1], reverse=True)


def markdown(rows, source_path):
    large_grid_rows = [row for row in rows if row.get("Grid") == "32x40x26"]
    groups = [average(rows, "all gates")]
    if large_grid_rows:
        groups.append(average(large_grid_rows, "large grid"))

    lines = [
        "# Cinematic Stage Profile",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Source summary: `{source_path}`",
        "",
        "## Gate Cost Split",
        "",
        "| Gate | Grid | Total | Non-render | Non-render % | Render | Render % | Top non-render |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join([
                f"`{row['Gate']}`",
                f"`{row['Grid']}`",
                fmt_seconds(row["Total_s"]),
                fmt_seconds(row["Non-render_s"]),
                fmt_pct(row["Non-render_pct"]),
                fmt_seconds(row["Render_s"]),
                fmt_pct(row["Render_pct"]),
                f"`{row['Top_non_render']}`",
            ])
            + " |"
        )

    lines.extend([
        "",
        "## Average Stage Breakdown",
        "",
        "| Group | Count | Export | Validate | Reconstruct | Convert | Render | Total | Non-render % |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for group in groups:
        lines.append(
            "| "
            + " | ".join([
                group["label"],
                str(group["count"]),
                fmt_seconds(group["Export_s"]),
                fmt_seconds(group["Validate_s"]),
                fmt_seconds(group["Reconstruct_s"]),
                fmt_seconds(group["Convert_s"]),
                fmt_seconds(group["Render_s"]),
                fmt_seconds(group["Total_s"]),
                fmt_pct(group["Non-render_pct"]),
            ])
            + " |"
        )

    ranking_rows = large_grid_rows or rows
    lines.extend([
        "",
        "## Bottleneck Ranking",
        "",
        "| Stage | Average | Share of total |",
        "| --- | ---: | ---: |",
    ])
    for stage, avg_s, pct in stage_ranking(ranking_rows):
        lines.append(f"| `{stage}` | {fmt_seconds(avg_s)} | {fmt_pct(pct)} |")

    if large_grid_rows:
        latest = large_grid_rows[-1]
        lines.extend([
            "",
            "## S108 Recommendation",
            "",
            f"- Large-grid non-render work is `{fmt_seconds(latest['Non-render_s'])}` ({fmt_pct(latest['Non-render_pct'])}) versus render `{fmt_seconds(latest['Render_s'])}` ({fmt_pct(latest['Render_pct'])}).",
            f"- The largest large-grid non-render stage is `{latest['Top_non_render']}`.",
            "- Target cache conversion and cache validation before running another larger-grid cinematic gate.",
            "- Preserve the S106 render preset as the current quality baseline while optimizing the cache path.",
        ])
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", help="Cinematic benchmark summary Markdown file")
    parser.add_argument("--out", required=True, help="Markdown output path")
    args = parser.parse_args(argv)

    rows = [enrich(row) for row in parse_markdown_table(args.summary)]
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    source = os.path.relpath(os.path.abspath(args.summary), os.getcwd()).replace("\\", "/")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown(rows, source))
    print(out)


if __name__ == "__main__":
    main()
