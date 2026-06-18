#!/usr/bin/env python
"""Summarize command timings and reuse flags from a cinematic shot_summary.json."""

import argparse
import json
import os
from datetime import datetime, timezone


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_reuse_flag(command):
    if command.get("reused") is True:
        return True
    stdout_log = command.get("stdout_log")
    if not stdout_log or not os.path.isfile(stdout_log):
        return False
    try:
        with open(stdout_log, encoding="utf-8") as f:
            for line in f:
                if line.strip() == "reused=true":
                    return True
    except OSError:
        return False
    return False


def rel(path, root):
    if not path:
        return "n/a"
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path


def fmt_ms(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if value >= 1000.0:
        return f"{value / 1000.0:.2f}s"
    return f"{value:.2f}ms"


def markdown(summary, summary_path, root):
    commands = summary.get("commands", [])
    metrics = summary.get("metrics", {})
    total_ms = sum(float(item.get("elapsed_ms", 0.0) or 0.0) for item in commands)
    reused_ms = sum(float(item.get("elapsed_ms", 0.0) or 0.0) for item in commands if read_reuse_flag(item))

    lines = [
        "# Cinematic Warm Cache Command Summary",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Source summary: `{rel(summary_path, root)}`",
        "",
        "## Reuse Flags",
        "",
        f"- Export cache reused: `{metrics.get('export_cache_reused', 'n/a')}`",
        f"- Validation reused: `{metrics.get('validation_reused', 'n/a')}`",
        f"- Water reconstruction reused: `{metrics.get('water_reconstruction_reused', 'n/a')}`",
        f"- Converted sequence reused: `{metrics.get('converted_sequence_reused', 'n/a')}`",
        f"- Render frames reused: `{metrics.get('render_frames_reused', 'n/a')}`",
        f"- GIF reused: `{metrics.get('gif_reused', 'n/a')}`",
        "",
        "## Command Timings",
        "",
        "| Stage | Exit | Reused | Elapsed | Stdout log |",
        "| --- | ---: | --- | ---: | --- |",
    ]
    for item in commands:
        reused = read_reuse_flag(item)
        lines.append(
            "| "
            + " | ".join([
                f"`{item.get('label', 'unknown')}`",
                str(item.get("returncode", "n/a")),
                "`true`" if reused else "`false`",
                fmt_ms(item.get("elapsed_ms")),
                f"`{rel(item.get('stdout_log'), root)}`",
            ])
            + " |"
        )

    lines.extend([
        "",
        "## Totals",
        "",
        f"- Total command time: `{fmt_ms(total_ms)}`",
        f"- Reused command time: `{fmt_ms(reused_ms)}`",
        "",
        "## Next",
        "",
        "S121 should turn the current artifact package into a browser-ready static gallery for review or cftunnel sharing.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", help="shot_summary.json")
    parser.add_argument("--out", required=True, help="Markdown output path")
    args = parser.parse_args(argv)

    root = os.getcwd()
    summary_path = os.path.abspath(args.summary)
    summary = read_json(summary_path)
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown(summary, summary_path, root))
    print(out)


if __name__ == "__main__":
    main()
