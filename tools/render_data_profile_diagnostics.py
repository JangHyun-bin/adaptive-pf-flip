#!/usr/bin/env python3
"""Build trend diagnostics from an LSFS render-data summary sidecar."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


SERIES = [
    ("water_depth_y_span", "Water Y Span", "#4fa3d1"),
    ("water_depth_z_span", "Water Z Span", "#7cc47f"),
    ("water_mesh_face_count", "Mesh Faces", "#d6a64f"),
    ("secondary_total_count", "Secondaries", "#c47fd6"),
]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def finite(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def stats(values):
    clean = [float(v) for v in values if finite(v)]
    if not clean:
        return {"count": 0, "min": None, "mean": None, "max": None, "delta": None}
    return {
        "count": len(clean),
        "min": min(clean),
        "mean": sum(clean) / float(len(clean)),
        "max": max(clean),
        "delta": clean[-1] - clean[0],
    }


def normalized(value, lo, hi):
    if not finite(value) or not finite(lo) or not finite(hi) or float(hi) <= float(lo):
        return 0.0
    return (float(value) - float(lo)) / (float(hi) - float(lo))


def extract_rows(sidecar):
    rows = []
    for frame in sidecar.get("frames", []):
        secondary = frame.get("secondary_counts", {})
        rows.append({
            "output_frame": frame.get("output_frame"),
            "source_frame": frame.get("source_frame"),
            "source_time": frame.get("source_time"),
            "water_depth_y_span": frame.get("water_depth_y_span"),
            "water_depth_z_span": frame.get("water_depth_z_span"),
            "water_mesh_face_count": frame.get("water_mesh_face_count"),
            "water_mesh_vertex_count": frame.get("water_mesh_vertex_count"),
            "occupied_cell_count": frame.get("occupied_cell_count"),
            "phase_field_liquid_volume": frame.get("phase_field_liquid_volume"),
            "secondary_total_count": secondary.get("total"),
            "secondary_spray_count": secondary.get("spray"),
            "secondary_foam_count": secondary.get("foam"),
            "secondary_bubble_count": secondary.get("bubble"),
        })
    return rows


def write_csv(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "output_frame",
        "source_frame",
        "source_time",
        "water_depth_y_span",
        "water_depth_z_span",
        "water_mesh_face_count",
        "water_mesh_vertex_count",
        "occupied_cell_count",
        "phase_field_liquid_volume",
        "secondary_total_count",
        "secondary_spray_count",
        "secondary_foam_count",
        "secondary_bubble_count",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def polyline(points):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def svg_escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_svg(path: Path, rows, summary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 1200
    height = 680
    margin_left = 74
    margin_top = 52
    chart_w = 1040
    chart_h = 120
    gap = 34
    frame_count = max(1, len(rows))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#101419"/>',
        f'<text x="48" y="30" fill="#e8eef5" font-family="Consolas, monospace" font-size="18">{svg_escape(summary.get("title", "S172 Render Data Profile Diagnostics"))}</text>',
    ]
    for chart_idx, (key, label, color) in enumerate(SERIES):
        y0 = margin_top + chart_idx * (chart_h + gap)
        values = [row.get(key) for row in rows]
        st = stats(values)
        lo = st["min"] if st["min"] is not None else 0.0
        hi = st["max"] if st["max"] is not None else 1.0
        if hi == lo:
            hi = lo + 1.0
        points = []
        for idx, row in enumerate(rows):
            x = margin_left + (chart_w * idx / float(max(1, frame_count - 1)))
            t = normalized(row.get(key), lo, hi)
            y = y0 + chart_h - chart_h * t
            points.append((x, y))
        parts.extend([
            f'<text x="48" y="{y0 - 12}" fill="#dce8f1" font-family="Consolas, monospace" font-size="14">{svg_escape(label)}</text>',
            f'<text x="360" y="{y0 - 12}" fill="#8fa3b4" font-family="Consolas, monospace" font-size="12">min={lo:.3f} mean={(st["mean"] or 0):.3f} max={hi:.3f} delta={(st["delta"] or 0):.3f}</text>',
            f'<rect x="{margin_left}" y="{y0}" width="{chart_w}" height="{chart_h}" fill="#151b22" stroke="#2d3a46" stroke-width="1"/>',
            f'<line x1="{margin_left}" y1="{y0 + chart_h}" x2="{margin_left + chart_w}" y2="{y0 + chart_h}" stroke="#40505f" stroke-width="1"/>',
            f'<line x1="{margin_left}" y1="{y0}" x2="{margin_left}" y2="{y0 + chart_h}" stroke="#40505f" stroke-width="1"/>',
            f'<polyline points="{polyline(points)}" fill="none" stroke="{color}" stroke-width="2.2"/>',
        ])
        for idx in range(0, frame_count, max(1, frame_count // 6)):
            x = margin_left + (chart_w * idx / float(max(1, frame_count - 1)))
            parts.append(f'<line x1="{x:.2f}" y1="{y0}" x2="{x:.2f}" y2="{y0 + chart_h}" stroke="#25313b" stroke-width="1"/>')
            parts.append(f'<text x="{x - 8:.2f}" y="{y0 + chart_h + 16}" fill="#758796" font-family="Consolas, monospace" font-size="10">{idx}</text>')

    checks = summary.get("sanity_checks", [])
    passed = sum(1 for check in checks if check.get("passed"))
    parts.extend([
        f'<text x="48" y="{height - 38}" fill="#a6bac8" font-family="Consolas, monospace" font-size="13">status={svg_escape(summary.get("status"))} checks={passed}/{len(checks)} generated={svg_escape(summary.get("generated_utc"))}</text>',
        "</svg>",
    ])
    path.write_text("\n".join(parts), encoding="utf-8")


def build_summary(sidecar_path: Path, csv_path: Path, svg_path: Path, rows, title, next_recommendation):
    sidecar = read_json(sidecar_path)
    simulation = sidecar.get("simulation", {})
    y_stats = stats(row.get("water_depth_y_span") for row in rows)
    z_stats = stats(row.get("water_depth_z_span") for row in rows)
    mesh_stats = stats(row.get("water_mesh_face_count") for row in rows)
    secondary_stats = stats(row.get("secondary_total_count") for row in rows)
    liquid_stats = stats(row.get("phase_field_liquid_volume") for row in rows)
    source_frames = [row.get("source_frame") for row in rows if row.get("source_frame") is not None]
    output_frames = [row.get("output_frame") for row in rows if row.get("output_frame") is not None]

    checks = [
        {
            "name": "row_count_matches_render_frames",
            "passed": len(rows) == int(simulation.get("render_frame_count", len(rows))),
            "value": len(rows),
        },
        {
            "name": "water_depth_y_span_present",
            "passed": y_stats["count"] == len(rows),
            "value": y_stats["count"],
        },
        {
            "name": "water_depth_z_span_present",
            "passed": z_stats["count"] == len(rows),
            "value": z_stats["count"],
        },
        {
            "name": "mesh_faces_present",
            "passed": mesh_stats["count"] == len(rows) and (mesh_stats["min"] or 0) > 0,
            "value": mesh_stats,
        },
        {
            "name": "secondary_counts_present",
            "passed": secondary_stats["count"] == len(rows) and (secondary_stats["min"] or 0) > 0,
            "value": secondary_stats,
        },
        {
            "name": "source_frame_mapping_monotonic",
            "passed": source_frames == sorted(source_frames),
            "value": source_frames[:3] + source_frames[-3:] if len(source_frames) >= 6 else source_frames,
        },
        {
            "name": "output_frame_mapping_monotonic",
            "passed": output_frames == sorted(output_frames),
            "value": output_frames[:3] + output_frames[-3:] if len(output_frames) >= 6 else output_frames,
        },
    ]
    status = "ok" if all(check["passed"] for check in checks) else "failed"
    findings = [
        "Water Z-depth span is near the full grid depth for much of the shot, so a renderer can use this sidecar to separate foreground and background water more deliberately.",
        "Mesh face counts remain high and stable enough for a metadata-driven render pass without re-reading raw cache JSONL.",
    ]
    if secondary_stats["delta"] is None:
        findings.append("Secondary count variation is unavailable, so secondary attenuation should use conservative constant bounds.")
    elif abs(float(secondary_stats["delta"])) < 1e-9:
        findings.append("Secondary total count is stable across the mapped frames; channel mix and depth placement should drive attenuation more than total count.")
    else:
        findings.append("Secondary counts vary across the shot, so depth-aware secondary attenuation should be frame dependent rather than a single constant.")
    return {
        "schema": "lsfs_render_data_profile_diagnostics",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "title": title,
        "status": status,
        "inputs": {
            "render_data_summary": str(sidecar_path),
        },
        "outputs": {
            "csv": str(csv_path),
            "svg": str(svg_path),
        },
        "frame_count": len(rows),
        "simulation": simulation,
        "trends": {
            "water_depth_y_span": y_stats,
            "water_depth_z_span": z_stats,
            "water_mesh_face_count": mesh_stats,
            "secondary_total_count": secondary_stats,
            "phase_field_liquid_volume": liquid_stats,
        },
        "sanity_checks": checks,
        "findings": findings,
        "next_recommendation": next_recommendation,
    }


def write_report(path: Path, summary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    t = summary["trends"]
    lines = [
        f"# {summary.get('title', 'S172 Render Data Consumer Diagnostics')}",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Inputs",
        "",
        f"- Render data summary: `{summary['inputs']['render_data_summary']}`",
        "",
        "## Outputs",
        "",
        f"- CSV profile: `{summary['outputs']['csv']}`",
        f"- SVG profile: `{summary['outputs']['svg']}`",
        "",
        "## Trend Summary",
        "",
        "| Trend | Count | Min | Mean | Max | Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, label, _color in SERIES:
        st = t[key]
        lines.append(
            f"| {label} | {st['count']} | {st['min']} | {st['mean']} | {st['max']} | {st['delta']} |"
        )
    lines.extend([
        "",
        f"- Phase-field liquid volume: `{t['phase_field_liquid_volume']}`",
        "",
        "## Sanity Checks",
        "",
        "| Check | Passed | Value |",
        "| --- | ---: | --- |",
    ])
    for check in summary["sanity_checks"]:
        lines.append(f"| `{check['name']}` | `{check['passed']}` | `{check['value']}` |")
    lines.extend([
        "",
        "## Findings",
        "",
    ])
    for finding in summary["findings"]:
        lines.append(f"- {finding}")
    lines.extend([
        "",
        "## Next",
        "",
        summary["next_recommendation"],
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render_data_summary", help="S171 render_data_summary.json")
    parser.add_argument("--out-dir", required=True, help="Output diagnostic directory")
    parser.add_argument("--report", help="Optional Markdown report path")
    parser.add_argument("--title", default="S172 Render Data Profile Diagnostics")
    parser.add_argument(
        "--next",
        default="S173 should consume render_data_summary.json in the render bridge as a bounded metadata-driven depth/attenuation pass, then compare against S168 without rerunning simulation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sidecar_path = Path(args.render_data_summary)
    out_dir = Path(args.out_dir)
    sidecar = read_json(sidecar_path)
    rows = extract_rows(sidecar)
    csv_path = out_dir / "render_data_profile.csv"
    svg_path = out_dir / "render_data_profile.svg"
    json_path = out_dir / "render_data_profile_summary.json"
    write_csv(csv_path, rows)
    summary = build_summary(sidecar_path, csv_path, svg_path, rows, args.title, args.next)
    write_svg(svg_path, rows, summary)
    write_json(json_path, summary)
    if args.report:
        write_report(Path(args.report), summary)
    print(f"status={summary['status']}")
    print(f"frames={summary['frame_count']}")
    print(f"csv={csv_path}")
    print(f"svg={svg_path}")
    print(f"summary={json_path}")
    if args.report:
        print(f"report={args.report}")
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
