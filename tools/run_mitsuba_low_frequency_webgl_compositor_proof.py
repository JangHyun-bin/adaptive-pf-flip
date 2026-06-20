#!/usr/bin/env python
"""Run the low-frequency compositor contract in Chromium/WebGL and compare parity."""

import argparse
import base64
import os
from datetime import datetime, timezone

try:
    from PIL import Image, ImageChops, ImageDraw, ImageOps
except ImportError:  # pragma: no cover - reported at runtime.
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageOps = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - reported at runtime.
    sync_playwright = None

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
from build_mitsuba_low_frequency_parity_texture_package import diff_stats, write_gif


WEBGL_PAGE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>LSFS WebGL Compositor Proof</title>
  <style>
    html, body { margin: 0; background: #071016; color: #eaf5fb; font-family: sans-serif; }
    canvas { display: block; width: 960px; height: 540px; image-rendering: pixelated; }
  </style>
</head>
<body>
<canvas id="stage" width="960" height="540"></canvas>
<script>
const vertexSource = `
precision mediump float;
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_uv;
void main() {
  gl_Position = vec4(a_position, 0.0, 1.0);
  v_uv = a_texcoord;
}`;
const fragmentSource = `
precision mediump float;
uniform sampler2D u_base_rgb;
uniform sampler2D u_positive_delta_rgb;
uniform sampler2D u_negative_delta_rgb;
uniform float u_texture_gain;
uniform float u_shader_flip_y;
varying vec2 v_uv;
void main() {
  vec2 uv = v_uv;
  uv.y = mix(uv.y, 1.0 - uv.y, u_shader_flip_y);
  vec3 base_rgb = texture2D(u_base_rgb, uv).rgb;
  vec3 positive_delta = texture2D(u_positive_delta_rgb, uv).rgb;
  vec3 negative_delta = texture2D(u_negative_delta_rgb, uv).rgb;
  vec3 corrected = clamp(base_rgb + (positive_delta - negative_delta) * u_texture_gain, 0.0, 1.0);
  gl_FragColor = vec4(corrected, 1.0);
}`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    throw new Error("compile failed type=" + type + " log=" + gl.getShaderInfoLog(shader) + " source=" + source);
  }
  return shader;
}

function program(gl) {
  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, vertexSource));
  gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, fragmentSource));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    throw new Error(gl.getProgramInfoLog(prog));
  }
  return prog;
}

let state = null;

function initState(width, height) {
  const canvas = document.getElementById("stage");
  canvas.width = width;
  canvas.height = height;
  const gl = canvas.getContext("webgl", { preserveDrawingBuffer: true });
  if (!gl) {
    throw new Error("WebGL unavailable");
  }
  const vs = "attribute vec2 a_position; attribute vec2 a_texcoord; varying vec2 v_uv; void main(){gl_Position=vec4(a_position,0.0,1.0); v_uv=a_texcoord;}";
  const fs = "precision mediump float; uniform sampler2D u_base_rgb; uniform sampler2D u_positive_delta_rgb; uniform sampler2D u_negative_delta_rgb; uniform float u_texture_gain; uniform float u_shader_flip_y; varying vec2 v_uv; void main(){vec2 uv=v_uv; uv.y=mix(uv.y,1.0-uv.y,u_shader_flip_y); vec3 base_rgb=texture2D(u_base_rgb,uv).rgb; vec3 positive_delta=texture2D(u_positive_delta_rgb,uv).rgb; vec3 negative_delta=texture2D(u_negative_delta_rgb,uv).rgb; vec3 corrected=clamp(base_rgb+(positive_delta-negative_delta)*u_texture_gain,0.0,1.0); gl_FragColor=vec4(corrected,1.0);}";
  function sh(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      throw new Error("compile failed type=" + type + " log=" + gl.getShaderInfoLog(shader));
    }
    return shader;
  }
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs));
  gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    throw new Error("link failed log=" + gl.getProgramInfoLog(prog));
  }
  gl.useProgram(prog);
  const position = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, position);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    -1, -1, 0, 0,
     1, -1, 1, 0,
    -1,  1, 0, 1,
     1,  1, 1, 1,
  ]), gl.STATIC_DRAW);
  const stride = 4 * 4;
  const aPosition = gl.getAttribLocation(prog, "a_position");
  const aTexcoord = gl.getAttribLocation(prog, "a_texcoord");
  gl.enableVertexAttribArray(aPosition);
  gl.enableVertexAttribArray(aTexcoord);
  gl.vertexAttribPointer(aPosition, 2, gl.FLOAT, false, stride, 0);
  gl.vertexAttribPointer(aTexcoord, 2, gl.FLOAT, false, stride, 2 * 4);
  state = { canvas, gl, prog, width, height };
  return state;
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error("failed to load image"));
    img.src = src;
  });
}

function makeTexture(gl, unit, image, uploadFlipY) {
  const texture = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0 + unit);
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
  return texture;
}

window.renderLsfsFrame = async function(frame, options) {
  const current = (!state || state.width !== frame.width || state.height !== frame.height)
    ? initState(frame.width, frame.height)
    : state;
  const canvas = current.canvas;
  const gl = current.gl;
  const prog = current.prog;
  gl.useProgram(prog);

  const base = await loadImage(frame.base);
  const positive = await loadImage(frame.positive);
  const negative = await loadImage(frame.negative);
  makeTexture(gl, 0, base, options.uploadFlipY);
  makeTexture(gl, 1, positive, options.uploadFlipY);
  makeTexture(gl, 2, negative, options.uploadFlipY);
  gl.uniform1i(gl.getUniformLocation(prog, "u_base_rgb"), 0);
  gl.uniform1i(gl.getUniformLocation(prog, "u_positive_delta_rgb"), 1);
  gl.uniform1i(gl.getUniformLocation(prog, "u_negative_delta_rgb"), 2);
  gl.uniform1f(gl.getUniformLocation(prog, "u_texture_gain"), options.textureGain);
  gl.uniform1f(gl.getUniformLocation(prog, "u_shader_flip_y"), options.shaderFlipY ? 1.0 : 0.0);
  gl.viewport(0, 0, frame.width, frame.height);
  gl.clearColor(0, 0, 0, 1);
  gl.clear(gl.COLOR_BUFFER_BIT);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  gl.finish();
  const sample = new Uint8Array(4);
  gl.readPixels(Math.floor(frame.width * 0.5), Math.floor(frame.height * 0.5), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, sample);
  return {
    dataUrl: canvas.toDataURL("image/png"),
    renderer: gl.getParameter(gl.RENDERER),
    vendor: gl.getParameter(gl.VENDOR),
    error: gl.getError(),
    sample: Array.from(sample),
  };
}

// Stable headless Chromium path. This intentionally creates a fresh WebGL
// context per frame to avoid context-loss behavior seen with reused contexts
// in some SwiftShader/ANGLE combinations.
window.renderLsfsFrame = async function(frame, options) {
  const canvas = document.getElementById("stage");
  canvas.width = frame.width;
  canvas.height = frame.height;
  const images = await Promise.all([loadImage(frame.base), loadImage(frame.positive), loadImage(frame.negative)]);
  const gl = canvas.getContext("webgl", { preserveDrawingBuffer: true });
  if (!gl) {
    throw new Error("WebGL unavailable");
  }
  const prog = program(gl);
  gl.useProgram(prog);
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    -1, -1, 0, 0,
     1, -1, 1, 0,
    -1,  1, 0, 1,
     1,  1, 1, 1,
  ]), gl.STATIC_DRAW);
  const stride = 4 * 4;
  let loc = gl.getAttribLocation(prog, "a_position");
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, stride, 0);
  loc = gl.getAttribLocation(prog, "a_texcoord");
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, stride, 2 * 4);
  function tex(unit, image) {
    const texture = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
  }
  tex(0, images[0]);
  tex(1, images[1]);
  tex(2, images[2]);
  gl.uniform1i(gl.getUniformLocation(prog, "u_base_rgb"), 0);
  gl.uniform1i(gl.getUniformLocation(prog, "u_positive_delta_rgb"), 1);
  gl.uniform1i(gl.getUniformLocation(prog, "u_negative_delta_rgb"), 2);
  gl.uniform1f(gl.getUniformLocation(prog, "u_texture_gain"), options.textureGain);
  gl.uniform1f(gl.getUniformLocation(prog, "u_shader_flip_y"), options.shaderFlipY ? 1.0 : 0.0);
  gl.viewport(0, 0, frame.width, frame.height);
  gl.clearColor(0, 0, 0, 1);
  gl.clear(gl.COLOR_BUFFER_BIT);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  gl.finish();
  const sample = new Uint8Array(4);
  gl.readPixels(Math.floor(frame.width * 0.5), Math.floor(frame.height * 0.5), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, sample);
  return {
    dataUrl: canvas.toDataURL("image/png"),
    renderer: gl.getParameter(gl.RENDERER),
    vendor: gl.getParameter(gl.VENDOR),
    error: gl.getError(),
    sample: Array.from(sample),
  };
}
</script>
</body>
</html>
"""


def require_runtime():
    if Image is None:
        raise SystemExit("Pillow is required to run WebGL compositor proof")
    if sync_playwright is None:
        raise SystemExit("Playwright is required to run WebGL compositor proof")


def resolve_path(value, root):
    if not value:
        return None
    text = str(value).replace("/", os.sep)
    if os.path.isabs(text):
        return os.path.abspath(text)
    return os.path.abspath(os.path.join(root, text))


def data_url(path):
    with open(path, "rb") as f:
        payload = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def save_data_url(value, path):
    prefix = "data:image/png;base64,"
    if not value.startswith(prefix):
        raise ValueError("expected PNG data URL")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(base64.b64decode(value[len(prefix):]))


def frame_dimensions(path):
    with Image.open(path) as img:
        return img.size


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


def copy_asset(src, assets_dir, name, label, root):
    dest = os.path.join(assets_dir, name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dest):
        with open(src, "rb") as f_in, open(dest, "wb") as f_out:
            f_out.write(f_in.read())
    entry = {
        "label": label,
        "asset": os.path.abspath(dest),
        "repo_path": posix_rel(os.path.abspath(dest), root),
        "href": "assets/" + name.replace(os.sep, "/"),
        "sha256": sha256_file(dest),
        "size": os.path.getsize(dest),
    }
    dims = image_dimensions(dest)
    if dims:
        entry["dimensions"] = dims
    return entry


def html_page(title, summary, assets, metadata_files):
    links = "\n".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in metadata_files)
    gif = next((item for item in assets if item["label"] == "WebGL Proof GIF"), None)
    strips = [item for item in assets if item["label"].startswith("WebGL Proof Strip")]
    checks = summary.get("checks") or {}
    tiles = "\n".join(
        f"<div><span>{label}</span><strong>{value}</strong></div>"
        for label, value in (
            ("Status", summary.get("status")),
            ("Frames", checks.get("frames")),
            ("Max diff", checks.get("max_oracle_abs_diff")),
            ("Mean diff", f"{checks.get('max_oracle_mean_abs_diff', 0.0):.6f}"),
            ("Orientation", summary.get("orientation")),
            ("GIF", format_bytes(checks.get("gif_bytes", 0))),
        )
    )
    hero = f'<section class="hero"><img src="{gif["href"]}" alt="WebGL proof GIF"></section>' if gif else ""
    figures = "\n".join(
        f'<figure><a href="{item["href"]}"><img src="{item["href"]}" alt="{item["label"]}"></a><figcaption>{item["label"]}</figcaption></figure>'
        for item in strips
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; --bg: #071016; --panel: #111b23; --ink: #eaf5fb; --muted: #9fb4c1; --line: #2c3c47; --accent: #9ddcff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1500px; margin: 0 auto; padding: 24px 18px 40px; }}
    header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 16px; }}
    h1 {{ margin: 0; font-size: 28px; font-weight: 680; letter-spacing: 0; }}
    nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .hero, figure {{ border: 1px solid var(--line); background: var(--panel); overflow-x: auto; }}
    .hero img, figure img {{ display: block; max-width: none; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .metrics div {{ border: 1px solid var(--line); background: var(--panel); padding: 10px 12px; min-height: 60px; }}
    .metrics span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .metrics strong {{ display: block; font-size: 15px; font-weight: 620; word-break: break-word; }}
    figure {{ margin: 0 0 12px; }}
    figcaption {{ color: var(--muted); font-size: 13px; padding: 8px 10px; }}
  </style>
</head>
<body>
  <main>
    <header><h1>{title}</h1><nav>{links}</nav></header>
    {hero}
    <section class="metrics">{tiles}</section>
    <section>{figures}</section>
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
        "## Runtime",
        "",
        f"- Browser: `{summary.get('browser')}`",
        f"- WebGL renderer: `{summary.get('webgl_renderer')}`",
        f"- WebGL vendor: `{summary.get('webgl_vendor')}`",
        f"- Orientation: `{summary.get('orientation')}`",
        "",
        "## Checks",
        "",
        f"- Frames: `{checks.get('frames')}`",
        f"- Missing references: `{checks.get('missing_references')}`",
        f"- Max oracle abs diff: `{checks.get('max_oracle_abs_diff')}`",
        f"- Max oracle mean diff: `{checks.get('max_oracle_mean_abs_diff')}`",
        f"- Max mismatched coverage: `{checks.get('max_oracle_mismatched_coverage')}`",
        f"- GIF bytes: `{format_bytes(checks.get('gif_bytes', 0))}`",
        "",
        "## Frame Samples",
        "",
        "| Frame | Output | Max Diff | Mean Diff | WebGL | Strip |",
        "| ---: | ---: | ---: | ---: | --- | --- |",
    ]
    frames = summary.get("frames") or []
    for index in sorted(set([0, len(frames) // 2, len(frames) - 1])) if frames else []:
        frame = frames[index]
        lines.append(
            f"| {frame.get('frame')} | {frame.get('output_frame')} | {frame.get('max_abs_diff')} | "
            f"{frame.get('mean_abs_diff')} | `{frame.get('webgl_repo_path')}` | `{frame.get('strip_repo_path')}` |"
        )
    lines.extend(["", "## Next", "", summary.get("next", ""), ""])
    return "\n".join(lines)


def contract_sources(contract):
    for source in (contract.get("sources") or {}).values():
        if source:
            yield source


def image_from_path(path):
    return Image.open(path).convert("RGB")


def render_frame(page, frame, orientation, texture_gain):
    width, height = frame_dimensions(frame["base"])
    payload = {
        "width": width,
        "height": height,
        "base": data_url(frame["base"]),
        "positive": data_url(frame["positive"]),
        "negative": data_url(frame["negative"]),
    }
    return page.evaluate(
        "(args) => window.renderLsfsFrame(args.frame, args.options)",
        {
            "frame": payload,
            "options": {
                "uploadFlipY": orientation["upload_flip_y"],
                "shaderFlipY": orientation["shader_flip_y"],
                "textureGain": texture_gain,
            },
        },
    )


def choose_orientation(page, first_frame, texture_gain, temp_dir):
    candidates = [
        {"name": "upload0_shader0", "upload_flip_y": False, "shader_flip_y": False},
        {"name": "upload0_shader1", "upload_flip_y": False, "shader_flip_y": True},
    ]
    best = None
    oracle = image_from_path(first_frame["oracle"])
    os.makedirs(temp_dir, exist_ok=True)
    for candidate in candidates:
        result = render_frame(page, first_frame, candidate, texture_gain)
        out_path = os.path.join(temp_dir, candidate["name"] + ".png")
        save_data_url(result["dataUrl"], out_path)
        stats = diff_stats(image_from_path(out_path), oracle)
        record = dict(candidate)
        record.update({
            "max_abs_diff": stats["max_abs_diff"],
            "mean_abs_diff": stats["mean_abs_diff"],
            "renderer": result.get("renderer"),
            "vendor": result.get("vendor"),
        })
        if best is None or (record["max_abs_diff"], record["mean_abs_diff"]) < (best["max_abs_diff"], best["mean_abs_diff"]):
            best = record
    return best


def build(args):
    require_runtime()
    root = os.getcwd()
    contract_path = require_file(args.contract, "compositor contract")
    contract = read_json(contract_path)
    if contract.get("schema") != "lsfs_mitsuba_low_frequency_compositor_contract":
        raise SystemExit(f"{args.contract}: expected lsfs_mitsuba_low_frequency_compositor_contract")

    out_dir = os.path.abspath(args.out_dir)
    webgl_dir = os.path.join(out_dir, "webgl_frames")
    strip_dir = os.path.join(out_dir, "strips")
    gallery_dir = os.path.join(out_dir, "gallery")
    assets_dir = os.path.join(gallery_dir, "assets")
    temp_dir = os.path.join(out_dir, "_orientation")
    for directory in (webgl_dir, strip_dir, assets_dir):
        os.makedirs(directory, exist_ok=True)
    html_runtime_path = os.path.join(out_dir, "runtime_webgl.html")
    write_text(html_runtime_path, WEBGL_PAGE)

    frame_inputs = []
    missing = []
    for frame in contract.get("frames") or []:
        bindings = frame.get("bindings") or {}
        paths = {
            "base": resolve_path(bindings.get("base_rgb"), root),
            "positive": resolve_path(bindings.get("positive_delta_rgb"), root),
            "negative": resolve_path(bindings.get("negative_delta_rgb"), root),
            "oracle": resolve_path(frame.get("oracle_repo_path"), root),
        }
        absent = [name for name, path in paths.items() if not path or not os.path.isfile(path)]
        if absent:
            missing.append({"frame": frame.get("frame"), "output_frame": frame.get("output_frame"), "missing": absent})
            continue
        payload = {
            "frame": frame.get("frame"),
            "output_frame": frame.get("output_frame"),
            **paths,
        }
        frame_inputs.append(payload)
    if not frame_inputs:
        raise SystemExit("no WebGL compositor frames to render")

    texture_gain = ((contract.get("compositor_contract") or {}).get("parameters") or {}).get("texture_gain", 1.0)
    generated_frames = []
    strip_paths = []
    webgl_renderer = None
    webgl_vendor = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-gpu-sandbox"])
        try:
            page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=1)
            page.set_content(WEBGL_PAGE, wait_until="load")
            orientation = choose_orientation(page, frame_inputs[0], texture_gain, temp_dir)
            for index, frame in enumerate(frame_inputs):
                result = render_frame(page, frame, orientation, texture_gain)
                webgl_renderer = result.get("renderer")
                webgl_vendor = result.get("vendor")
                webgl_path = os.path.join(webgl_dir, f"frame_{index:04d}.png")
                save_data_url(result["dataUrl"], webgl_path)
                webgl_image = image_from_path(webgl_path)
                oracle_image = image_from_path(frame["oracle"])
                stats = diff_stats(webgl_image, oracle_image)
                strip_path = os.path.join(strip_dir, f"frame_{index:04d}_webgl_proof.png")
                diff_visual = ImageOps.autocontrast(ImageChops.difference(webgl_image, oracle_image))
                labeled_strip(
                    [
                        image_from_path(frame["base"]),
                        image_from_path(frame["positive"]),
                        image_from_path(frame["negative"]),
                        webgl_image,
                        oracle_image,
                        diff_visual,
                    ],
                    ["base", "positive", "negative", "WebGL", "S491 oracle", "diff"],
                    strip_path,
                )
                strip_paths.append(strip_path)
                generated_frames.append({
                    "frame": frame["frame"],
                    "output_frame": frame["output_frame"],
                    "webgl_path": webgl_path,
                    "webgl_repo_path": posix_rel(webgl_path, root),
                    "webgl_sha256": sha256_file(webgl_path),
                    "webgl_size": os.path.getsize(webgl_path),
                    "webgl_sample_rgba": result.get("sample"),
                    "webgl_error": result.get("error"),
                    "oracle_repo_path": posix_rel(frame["oracle"], root),
                    "strip_repo_path": posix_rel(strip_path, root),
                    "max_abs_diff": stats["max_abs_diff"],
                    "mean_abs_diff": stats["mean_abs_diff"],
                    "mismatched_coverage": stats["mismatched_coverage"],
                })
        finally:
            browser.close()

    gif_path = os.path.join(assets_dir, "webgl_proof.gif")
    write_gif(strip_paths, gif_path, args.fps)
    key_indices = sorted(set(round(i * (len(strip_paths) - 1) / float(max(1, args.keyframes - 1))) for i in range(args.keyframes)))
    assets = [copy_asset(gif_path, assets_dir, "webgl_proof.gif", "WebGL Proof GIF", root)]
    for out_index, frame_index in enumerate(key_indices):
        assets.append(copy_asset(strip_paths[frame_index], assets_dir, f"webgl_proof_strip_{out_index:02d}.png", f"WebGL Proof Strip {out_index + 1}", root))
    metadata_files = [
        copy_asset(contract_path, assets_dir, "low_frequency_compositor_contract.json", "Compositor contract", root),
        copy_asset(html_runtime_path, assets_dir, "runtime_webgl.html", "Runtime HTML", root),
    ]
    checks = {
        "frames": len(generated_frames),
        "missing_references": len(missing),
        "max_oracle_abs_diff": max((frame["max_abs_diff"] for frame in generated_frames), default=0),
        "max_oracle_mean_abs_diff": max((frame["mean_abs_diff"] for frame in generated_frames), default=0.0),
        "max_oracle_mismatched_coverage": max((frame["mismatched_coverage"] for frame in generated_frames), default=0.0),
        "webgl_frame_bytes": sum(frame["webgl_size"] for frame in generated_frames),
        "gif_bytes": os.path.getsize(gif_path),
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
    summary_path = os.path.abspath(args.summary)
    gallery_index = os.path.join(gallery_dir, "index.html")
    summary = {
        "schema": "lsfs_mitsuba_low_frequency_webgl_compositor_proof",
        "version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "status": status,
        "browser": "chromium",
        "webgl_renderer": webgl_renderer,
        "webgl_vendor": webgl_vendor,
        "orientation": orientation["name"],
        "contract": {
            "path": contract_path,
            "repo_path": posix_rel(contract_path, root),
            "sha256": sha256_file(contract_path),
            "schema": contract.get("schema"),
            "status": contract.get("status"),
        },
        "settings": {
            "texture_gain": texture_gain,
            "fps": args.fps,
            "keyframes": args.keyframes,
        },
        "checks": checks,
        "frames": generated_frames,
        "missing_references": missing,
        "gallery": {
            "path": gallery_dir,
            "repo_path": posix_rel(gallery_dir, root),
            "index_path": gallery_index,
            "index_repo_path": posix_rel(gallery_index, root),
            "assets": assets,
            "metadata_files": metadata_files,
        },
        "next": args.next,
    }
    write_json(summary_path, summary)
    metadata_files.insert(0, copy_asset(summary_path, assets_dir, "webgl_compositor_proof_summary.json", "WebGL proof summary", root))
    summary["gallery"]["metadata_files"] = metadata_files
    write_json(summary_path, summary)
    write_text(gallery_index, html_page(args.title, summary, assets, metadata_files))
    write_json(os.path.join(gallery_dir, "gallery_manifest.json"), {
        "schema": "lsfs_mitsuba_low_frequency_webgl_compositor_proof_gallery",
        "version": 1,
        "generated_utc": summary["generated_utc"],
        "title": args.title,
        "summary_repo_path": posix_rel(summary_path, root),
        "index_repo_path": posix_rel(gallery_index, root),
        "assets": assets,
        "metadata_files": metadata_files,
    })
    if args.report:
        write_text(args.report, markdown_report(summary, summary_path, root))
    print(
        f"status={status} frames={checks['frames']} max_oracle={checks['max_oracle_abs_diff']} "
        f"renderer={webgl_renderer} summary={summary_path}"
    )
    if status != "ready":
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a WebGL compositor proof for the low-frequency contract")
    parser.add_argument("contract")
    parser.add_argument("out_dir")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--report")
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--keyframes", type=int, default=4)
    parser.add_argument("--max-abs-tolerance", type=int, default=0)
    parser.add_argument("--mean-abs-tolerance", type=float, default=0.0)
    parser.add_argument("--title", default="S493 Mitsuba Low Frequency WebGL Compositor Proof")
    parser.add_argument(
        "--next",
        default="Use this WebGL proof as the runtime parity gate before wiring the compositor contract into the production renderer UI or export package.",
    )
    args = parser.parse_args(argv)
    if args.fps <= 0.0:
        parser.error("fps must be positive")
    if args.keyframes <= 0:
        parser.error("keyframes must be positive")
    if args.max_abs_tolerance < 0:
        parser.error("max-abs-tolerance must be non-negative")
    if args.mean_abs_tolerance < 0.0:
        parser.error("mean-abs-tolerance must be non-negative")
    build(args)


if __name__ == "__main__":
    main()
