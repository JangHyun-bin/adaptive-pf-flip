#!/usr/bin/env python
"""Build a shader/compositor contract for low-frequency parity textures."""

import argparse
import os
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None

from build_bridge_review_package import (
    format_bytes,
    posix_rel,
    read_json,
    require_file,
    sha256_file,
    write_json,
    write_text,
)
from build_mitsuba_low_frequency_parity_texture_package import diff_stats, reconstruct


GLSL_SOURCE = """#version 330 core
// LSFS low-frequency parity post-tonemap compositor.
// Inputs are tonemapped RGB textures in the same display color space.

uniform sampler2D u_base_rgb;
uniform sampler2D u_positive_delta_rgb;
uniform sampler2D u_negative_delta_rgb;
uniform sampler2D u_dark_damping_weight_luma;
uniform float u_texture_gain;
in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec3 base_rgb = texture(u_base_rgb, v_uv).rgb;
    vec3 positive_delta = texture(u_positive_delta_rgb, v_uv).rgb;
    vec3 negative_delta = texture(u_negative_delta_rgb, v_uv).rgb;
    vec3 corrected = clamp(base_rgb + (positive_delta - negative_delta) * u_texture_gain, 0.0, 1.0);
    fragColor = vec4(corrected, 1.0);
}
"""


HLSL_SOURCE = """// LSFS low-frequency parity post-tonemap compositor.
// Inputs are tonemapped RGB textures in the same display color space.

Texture2D<float4> BaseRgb : register(t0);
Texture2D<float4> PositiveDeltaRgb : register(t1);
Texture2D<float4> NegativeDeltaRgb : register(t2);
Texture2D<float4> DarkDampingWeightLuma : register(t3);
SamplerState LinearSampler : register(s0);
cbuffer LowFrequencyParityParams : register(b0) {
    float TextureGain;
    float3 _Padding;
};

float4 main(float2 uv : TEXCOORD0) : SV_Target {
    float3 base_rgb = BaseRgb.Sample(LinearSampler, uv).rgb;
    float3 positive_delta = PositiveDeltaRgb.Sample(LinearSampler, uv).rgb;
    float3 negative_delta = NegativeDeltaRgb.Sample(LinearSampler, uv).rgb;
    float3 corrected = saturate(base_rgb + (positive_delta - negative_delta) * TextureGain);
    return float4(corrected, 1.0);
}
"""


PSEUDOCODE_SOURCE = """LSFS low-frequency parity compositor contract

stage: post_tonemap
color_space: tonemapped RGB, normalized [0, 1]
operation:
  corrected_rgb = clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)

required bindings:
  u_base_rgb
  u_positive_delta_rgb
  u_negative_delta_rgb

optional binding:
  u_dark_damping_weight_luma

promotion gate:
  CPU reference must match the S491 parity oracle with max_abs_diff == 0 at texture_gain == 1.0.
"""


def require_pillow():
    if Image is None:
        raise SystemExit("Pillow is required to build compositor contracts")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def texture_path(frame, name):
    entry = ((frame.get("textures") or {}).get(name) or {})
    return entry.get("path") or entry.get("repo_path")


def output_frame_map(frames):
    return {frame.get("output_frame"): frame for frame in frames or [] if frame.get("output_frame") is not None}


def file_entry(path, root, label, role):
    resolved = require_file(path, label)
    return {
        "label": label,
        "role": role,
        "path": resolved,
        "repo_path": posix_rel(resolved, root),
        "sha256": sha256_file(resolved),
        "size": os.path.getsize(resolved),
    }


def json_entry(path, root, label):
    resolved = require_file(path, label)
    payload = read_json(resolved)
    entry = file_entry(resolved, root, label, "metadata")
    entry["schema"] = payload.get("schema")
    entry["subschema"] = payload.get("subschema")
    entry["status"] = payload.get("status")
    return entry, payload


def write_shader_files(out_dir, root):
    shader_dir = os.path.join(out_dir, "shaders")
    os.makedirs(shader_dir, exist_ok=True)
    files = [
        ("low_frequency_parity_post_tonemap.glsl", GLSL_SOURCE, "glsl_reference"),
        ("low_frequency_parity_post_tonemap.hlsl", HLSL_SOURCE, "hlsl_reference"),
        ("low_frequency_parity_post_tonemap.txt", PSEUDOCODE_SOURCE, "pseudocode_reference"),
    ]
    entries = []
    for name, source, role in files:
        path = os.path.join(shader_dir, name)
        write_text(path, source)
        entries.append(file_entry(path, root, name, role))
    return entries


def validate_frame(package_frame, stage_frame, root, texture_gain):
    paths = {
        "base_rgb": resolve_path(texture_path(package_frame, "base_rgb"), root),
        "positive_delta_rgb": resolve_path(texture_path(package_frame, "applied_positive_delta_rgb"), root),
        "negative_delta_rgb": resolve_path(texture_path(package_frame, "applied_negative_delta_rgb"), root),
        "dark_damping_weight_luma": resolve_path(texture_path(package_frame, "dark_damping_weight_luma"), root),
        "oracle": resolve_path(stage_frame.get("graded_repo_path"), root),
    }
    missing = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
    if missing:
        return None, {"missing": missing, "paths": paths}
    base = Image.open(paths["base_rgb"]).convert("RGB")
    positive = Image.open(paths["positive_delta_rgb"]).convert("RGB")
    negative = Image.open(paths["negative_delta_rgb"]).convert("RGB")
    if texture_gain != 1.0:
        raise SystemExit("S492 contract validation currently requires texture_gain == 1.0")
    actual = reconstruct(base, positive, negative)
    oracle = Image.open(paths["oracle"]).convert("RGB")
    stats = diff_stats(actual, oracle)
    return {
        "frame": package_frame.get("frame"),
        "output_frame": package_frame.get("output_frame"),
        "bindings": {
            name: posix_rel(path, root)
            for name, path in paths.items()
            if name != "oracle"
        },
        "oracle_repo_path": posix_rel(paths["oracle"], root),
        "oracle_sha256": sha256_file(paths["oracle"]),
        "max_abs_diff": stats["max_abs_diff"],
        "mean_abs_diff": stats["mean_abs_diff"],
        "mismatched_coverage": stats["mismatched_coverage"],
        "changed_coverage": (package_frame.get("stats") or {}).get("changed_coverage"),
        "max_layer_delta": (package_frame.get("stats") or {}).get("max_abs_delta"),
    }, None


def markdown_report(contract, contract_path, root):
    checks = contract.get("checks") or {}
    lines = [
        f"# {contract['title']}",
        "",
        f"Generated UTC: `{contract['generated_utc']}`",
        f"Contract JSON: `{posix_rel(contract_path, root)}`",
        f"Status: `{contract['status']}`",
        "",
        "## Operation",
        "",
        f"- Stage: `{contract['compositor_contract']['stage']}`",
        f"- Color space: `{contract['compositor_contract']['color_space']}`",
        f"- Expression: `{contract['compositor_contract']['expression']}`",
        f"- Texture gain: `{contract['compositor_contract']['parameters']['texture_gain']}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max oracle abs diff: `{checks.get('max_oracle_abs_diff')}`",
        f"- Max oracle mean diff: `{checks.get('max_oracle_mean_abs_diff')}`",
        f"- Max mismatched coverage: `{checks.get('max_oracle_mismatched_coverage')}`",
        f"- Max changed coverage: `{checks.get('max_changed_coverage')}`",
        f"- Target-gap mean MAD: `{checks.get('target_gap_mean_mad')}`",
        f"- Target-gap max MAD: `{checks.get('target_gap_max_mad')}`",
        f"- Shader bytes: `{format_bytes(checks.get('shader_bytes', 0))}`",
        "",
        "## Shader Artifacts",
        "",
        "| Role | Path | Size |",
        "| --- | --- | ---: |",
    ]
    for artifact in contract.get("artifacts") or []:
        if artifact.get("role", "").endswith("reference"):
            lines.append(f"| `{artifact['role']}` | `{artifact['repo_path']}` | {format_bytes(artifact['size'])} |")
    lines.extend([
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Max Diff | Changed Coverage | Base |",
        "| ---: | ---: | ---: | ---: | --- |",
    ])
    frames = contract.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        bindings = frame.get("bindings") or {}
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('max_abs_diff')} | "
            f"{frame.get('changed_coverage')} | `{bindings.get('base_rgb')}` |"
        )
    lines.extend(["", "## Next", "", contract.get("next", ""), ""])
    return "\n".join(lines)


def build(args):
    require_pillow()
    root = os.getcwd()
    package_source, package = json_entry(args.texture_package_summary, root, "texture package summary")
    stage_source, stage = json_entry(args.post_tonemap_stage_summary, root, "post-tonemap stage summary")
    target_gap_source, target_gap = json_entry(args.target_gap_summary, root, "target-gap summary")
    if package.get("schema") != "lsfs_mitsuba_low_frequency_parity_texture_package":
        raise SystemExit(f"{args.texture_package_summary}: expected lsfs_mitsuba_low_frequency_parity_texture_package")
    if stage.get("schema") != "lsfs_mitsuba_composite_grade":
        raise SystemExit(f"{args.post_tonemap_stage_summary}: expected lsfs_mitsuba_composite_grade")
    if stage.get("subschema") != "lsfs_mitsuba_low_frequency_post_tonemap_texture_stage":
        raise SystemExit(f"{args.post_tonemap_stage_summary}: expected low-frequency post-tonemap subschema")
    if target_gap.get("schema") != "lsfs_mitsuba_renderer_target_gap":
        raise SystemExit(f"{args.target_gap_summary}: expected lsfs_mitsuba_renderer_target_gap")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    shader_artifacts = write_shader_files(out_dir, root)
    stage_frames = output_frame_map(stage.get("frames") or [])
    frames = []
    missing = []
    for package_frame in package.get("frames") or []:
        stage_frame = stage_frames.get(package_frame.get("output_frame"))
        if not stage_frame:
            missing.append({"frame": package_frame.get("frame"), "output_frame": package_frame.get("output_frame"), "missing": ["stage_frame"]})
            continue
        frame_record, failure = validate_frame(package_frame, stage_frame, root, args.texture_gain)
        if failure:
            failure.update({"frame": package_frame.get("frame"), "output_frame": package_frame.get("output_frame")})
            missing.append(failure)
            continue
        frames.append(frame_record)

    checks = {
        "frames": len(frames),
        "missing_references": len(missing),
        "max_oracle_abs_diff": max((frame["max_abs_diff"] for frame in frames), default=0),
        "max_oracle_mean_abs_diff": max((frame["mean_abs_diff"] for frame in frames), default=0.0),
        "max_oracle_mismatched_coverage": max((frame["mismatched_coverage"] for frame in frames), default=0.0),
        "max_changed_coverage": max((frame.get("changed_coverage") or 0.0 for frame in frames), default=0.0),
        "max_layer_delta": max((frame.get("max_layer_delta") or 0 for frame in frames), default=0),
        "target_gap_mean_mad": (target_gap.get("checks") or {}).get("mean_gap_mean_abs_diff"),
        "target_gap_max_mad": (target_gap.get("checks") or {}).get("max_gap_mean_abs_diff"),
        "target_gap_max_abs_diff": (target_gap.get("checks") or {}).get("max_gap_max_abs_diff"),
        "shader_bytes": sum(item.get("size", 0) for item in shader_artifacts),
        "max_abs_tolerance": args.max_abs_tolerance,
        "mean_abs_tolerance": args.mean_abs_tolerance,
    }
    status = "ready"
    if missing:
        status = "failed"
    if checks["max_oracle_abs_diff"] > args.max_abs_tolerance:
        status = "failed"
    if checks["max_oracle_mean_abs_diff"] > args.mean_abs_tolerance:
        status = "failed"

    generated = datetime.now(timezone.utc).isoformat()
    contract_path = os.path.abspath(args.out)
    contract = {
        "schema": "lsfs_mitsuba_low_frequency_compositor_contract",
        "version": 1,
        "generated_utc": generated,
        "title": args.title,
        "status": status,
        "sources": {
            "texture_package_summary": package_source,
            "post_tonemap_stage_summary": stage_source,
            "target_gap_summary": target_gap_source,
        },
        "compositor_contract": {
            "stage": "post_tonemap",
            "color_space": "tonemapped_rgb_normalized",
            "expression": "clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)",
            "parameters": {
                "texture_gain": args.texture_gain,
            },
            "required_bindings": [
                "base_rgb",
                "positive_delta_rgb",
                "negative_delta_rgb",
            ],
            "optional_bindings": [
                "dark_damping_weight_luma",
            ],
            "shader_entrypoints": {
                "glsl": "low_frequency_parity_post_tonemap.glsl",
                "hlsl": "low_frequency_parity_post_tonemap.hlsl",
            },
            "parity_oracle": {
                "summary_repo_path": stage_source["repo_path"],
                "required_max_abs_diff": args.max_abs_tolerance,
                "required_mean_abs_diff": args.mean_abs_tolerance,
            },
        },
        "checks": checks,
        "artifacts": shader_artifacts,
        "frames": frames,
        "missing_references": missing,
        "next": args.next,
    }
    write_json(contract_path, contract)
    if args.report:
        write_text(args.report, markdown_report(contract, contract_path, root))
    print(
        f"status={status} frames={checks['frames']} max_oracle={checks['max_oracle_abs_diff']} "
        f"contract={contract_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a low-frequency parity compositor contract")
    parser.add_argument("texture_package_summary")
    parser.add_argument("post_tonemap_stage_summary")
    parser.add_argument("target_gap_summary")
    parser.add_argument("out_dir")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report")
    parser.add_argument("--texture-gain", type=float, default=1.0)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="S492 Mitsuba Low Frequency Compositor Contract")
    parser.add_argument(
        "--next",
        default="Use this shader contract to implement the low-frequency correction in an engine-native compositor and check parity against S491.",
    )
    args = parser.parse_args(argv)
    if args.texture_gain < 0.0:
        parser.error("texture-gain must be non-negative")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    build(args)


if __name__ == "__main__":
    main()
