#!/usr/bin/env python
"""Summarize a cinematic gallery into a visual review triage report."""

import argparse
import json
import os
from datetime import datetime, timezone


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def posix_rel(path, root):
    if not path:
        return "n/a"
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def resolve_path(path, root):
    if not path:
        return None
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(root, path))


def format_value(value, digits=3):
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def nested(data, path, default=None):
    cur = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def gate_passed(metrics, key):
    gate = metrics.get(key)
    if isinstance(gate, dict):
        return gate.get("passed")
    return None


def endpoint_label(url):
    if not url:
        return "n/a"
    label = "public" if url.startswith("https://") else "local"
    for suffix in ("/index.html", "/assets/shot.gif"):
        if url.endswith(suffix):
            return f"{label} {suffix.lstrip('/')}"
    return label


def publish_checks(publish):
    if not publish:
        return []
    return publish.get("checks", [])


def find_optional_file(gallery, label):
    for item in gallery.get("optional_files", []):
        if item.get("label") == label:
            return item.get("asset") or item.get("source")
    return None


def load_shot_summary(gallery, root):
    path = find_optional_file(gallery, "shot_summary.json")
    if path:
        resolved = resolve_path(path, root)
        if os.path.isfile(resolved):
            return read_json(resolved), resolved
    return {}, None


def metric_rows(shot):
    metrics = shot.get("metrics", {})
    rows = [
        ("visual gate", gate_passed(metrics, "visual_qa_gate"), "pass/fail"),
        ("focus gate", gate_passed(metrics, "focus_review_gate"), "pass/fail"),
        ("secondary depth gate", gate_passed(metrics, "secondary_depth_review_gate"), "pass/fail"),
        ("ripple readability gate", gate_passed(metrics, "ripple_readability_gate"), "pass/fail"),
        ("temporal highlight gate", gate_passed(metrics, "temporal_highlight_gate"), "pass/fail"),
        ("mean luminance", nested(metrics, ["visual_qa", "mean_luminance", "mean"]), "visual balance"),
        ("mean contrast", nested(metrics, ["visual_qa", "contrast", "mean"]), "visual balance"),
        ("mean bright ratio", nested(metrics, ["visual_qa", "bright_ratio", "mean"]), "highlight presence"),
        ("secondary min inside ratio", nested(metrics, ["secondary_framing", "min_inside_ratio"]), "composition risk"),
        ("secondary mean screen y", nested(metrics, ["secondary_framing", "mean_screen_y"]), "composition"),
        ("secondary mean crop ratio", nested(metrics, ["secondary_depth_review", "summary", "crop_ratio", "mean"]), "secondary visibility"),
        ("secondary mean depth span", nested(metrics, ["secondary_depth_review", "summary", "depth_span", "mean"]), "depth layering"),
        (
            "secondary channel depth delta",
            nested(metrics, ["secondary_depth_review", "summary", "channel_depth_delta", "mean"]),
            "channel separation",
        ),
        ("ripple edge mean", nested(metrics, ["ripple_readability", "summary", "edge_mean", "mean"]), "surface detail"),
        (
            "ripple highlight ratio",
            nested(metrics, ["ripple_readability", "summary", "highlight_ratio", "mean"]),
            "surface highlight control",
        ),
    ]
    return rows


def automatic_findings(shot):
    metrics = shot.get("metrics", {})
    findings = []
    min_inside = nested(metrics, ["secondary_framing", "min_inside_ratio"])
    if isinstance(min_inside, (int, float)) and min_inside < 0.45:
        findings.append(
            f"Secondary framing is still marginal early in the shot: min inside ratio is {min_inside:.3f}."
        )
    bright = nested(metrics, ["focus_review", "summary", "bright_ratio", "mean"])
    if isinstance(bright, (int, float)) and bright < 0.001:
        findings.append(
            f"Water-body focus highlights are subdued: focus bright-ratio mean is {bright:.6f}."
        )
    channel_delta = nested(metrics, ["secondary_depth_review", "summary", "channel_depth_delta", "mean"])
    if isinstance(channel_delta, (int, float)) and channel_delta < 2.0:
        findings.append(
            f"Secondary channel depth separation is modest: mean channel depth delta is {channel_delta:.3f}."
        )
    droplets = nested(metrics, ["secondary_channels", "last", "droplet_count"])
    if droplets == 0:
        findings.append("Rendered secondary channels end with no droplet channel contribution.")
    if not findings:
        findings.append("Numeric gates pass; remaining issues should be judged from the visual sheets.")
    return findings


def summary_table(gallery, shot):
    summary = gallery.get("summary", {})
    config = shot.get("config", {})
    return [
        ("status", summary.get("status", shot.get("status"))),
        ("renderer", summary.get("renderer", shot.get("selected_renderer"))),
        ("preset", summary.get("preset", shot.get("shot_preset"))),
        ("grid", " x ".join(str(v) for v in summary.get("grid", []) if v is not None)),
        ("frames", summary.get("frames", config.get("frames"))),
        ("samples", summary.get("samples", config.get("samples"))),
        ("comparison sources", summary.get("comparison_sources")),
        ("export particles", summary.get("export_particles")),
        ("validated particles", summary.get("validated_particles")),
    ]


def required_artifact_status(gallery):
    required = [item for item in gallery.get("artifacts", []) if item.get("required")]
    present = [item for item in required if os.path.isfile(resolve_path(item.get("asset"), os.getcwd()))]
    return len(required), len(present)


def markdown(gallery, gallery_path, publish, publish_path, shot, shot_path, findings, decision, root):
    required_count, present_count = required_artifact_status(gallery)
    lines = [
        "# Cinematic Visual Review Triage",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Gallery manifest: `{posix_rel(gallery_path, root)}`",
    ]
    if publish_path:
        lines.append(f"Publish manifest: `{posix_rel(publish_path, root)}`")
    if shot_path:
        lines.append(f"Shot summary: `{posix_rel(shot_path, root)}`")
    lines.extend([
        "",
        "## Current Shot",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ])
    for name, value in summary_table(gallery, shot):
        lines.append(f"| {name} | `{format_value(value)}` |")

    lines.extend([
        "",
        "## Publish Checks",
        "",
        "| Endpoint | Method | Status | Bytes |",
        "| --- | --- | ---: | ---: |",
    ])
    for check in publish_checks(publish):
        lines.append(
            f"| {endpoint_label(check.get('url'))} | `{check.get('method', 'n/a')}` | {check.get('status', 'n/a')} | {check.get('content_length', 'n/a')} |"
        )

    lines.extend([
        "",
        "## Artifact Coverage",
        "",
        f"- Required visual artifacts present: `{present_count} / {required_count}`",
        f"- Total gallery artifacts: `{len(gallery.get('artifacts', []))}`",
        "",
        "| Artifact | Required | Size | Dimensions |",
        "| --- | --- | ---: | --- |",
    ])
    for item in gallery.get("artifacts", []):
        dims = item.get("dimensions")
        dims_text = "n/a"
        if dims:
            dims_text = f"{dims[0]} x {dims[1]}"
        required = "yes" if item.get("required") else "no"
        lines.append(f"| {item.get('label', item.get('key'))} | `{required}` | {item.get('size', 'n/a')} | `{dims_text}` |")

    lines.extend([
        "",
        "## Numeric Triage",
        "",
        "| Metric | Value | Notes |",
        "| --- | ---: | --- |",
    ])
    for name, value, notes in metric_rows(shot):
        lines.append(f"| {name} | `{format_value(value)}` | {notes} |")

    all_findings = automatic_findings(shot) + list(findings)
    lines.extend([
        "",
        "## Visual Findings",
        "",
    ])
    for item in all_findings:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Decision",
        "",
        decision,
        "",
        "## Next",
        "",
        "S124 should implement the selected composition/look-dev adjustment and run a warm-cache Blender gate against the current S119 baseline.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("gallery_manifest", help="gallery_manifest.json from build_cinematic_gallery.py")
    parser.add_argument("--publish", help="publish manifest from publish_cinematic_gallery.py")
    parser.add_argument("--out", required=True, help="Markdown output path")
    parser.add_argument("--finding", action="append", default=[], help="Additional visual finding to include")
    parser.add_argument(
        "--decision",
        default=(
            "Select S124 composition/look-dev pass: move the camera toward the contact band, reduce the tank/back-wall read, "
            "and tune secondary integration without weakening existing visual gates."
        ),
        help="Decision text for the next milestone",
    )
    args = parser.parse_args(argv)

    root = os.getcwd()
    gallery_path = os.path.abspath(args.gallery_manifest)
    gallery = read_json(gallery_path)
    publish = None
    publish_path = None
    if args.publish:
        publish_path = os.path.abspath(args.publish)
        publish = read_json(publish_path)
    shot, shot_path = load_shot_summary(gallery, root)

    required_count, present_count = required_artifact_status(gallery)
    if required_count != present_count:
        raise SystemExit(f"Required visual artifacts missing: {present_count}/{required_count}")

    if publish:
        bad = [check for check in publish_checks(publish) if check.get("status") != 200]
        if bad:
            raise SystemExit(f"Publish checks contain non-200 statuses: {bad}")

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown(gallery, gallery_path, publish, publish_path, shot, shot_path, args.finding, args.decision, root))
    print(out)


if __name__ == "__main__":
    main()
