#!/usr/bin/env python
"""Rough volumetric-ish renderer for two-phase particle dumps.

Reads render_###.csv (produced by apps/dump_render.cpp): a header line
"nx ny dx", then one "x,y,type" line per particle (type 0=liquid, 1=gas).
Splats liquid particles into a smooth density field and shades it as a
volumetric water body with a surface highlight -- a big step up from raw
point dots. NOT the paper's ray tracer (that's SPEC-4); this is the "rough"
rendering goal.

Usage:  python tools/rough_render.py <dir-with-csvs> [out_dir] [supersample]
Outputs shaded PNGs and an animated GIF.
"""
import sys, glob, os
import numpy as np
from PIL import Image

try:
    from scipy.ndimage import gaussian_filter
    def blur2d(a, sigma):
        return gaussian_filter(a, sigma)
except Exception:
    def blur2d(a, sigma):
        r = max(1, int(3 * sigma))
        x = np.arange(-r, r + 1)
        k = np.exp(-(x * x) / (2.0 * sigma * sigma)); k /= k.sum()
        a = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, a)
        a = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
        return a

def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)

def lerp(a, b, t):
    return a + (b - a) * t[..., None]

# palette (RGB)
DEEP    = np.array([12, 38, 86],   float)   # thick interior water
SHALLOW = np.array([70, 150, 220], float)   # thin / near surface
RIM     = np.array([170, 225, 250], float)  # surface highlight
BG_TOP  = np.array([8, 10, 15],    float)
BG_BOT  = np.array([18, 22, 30],   float)

def render_frame(path, S):
    with open(path) as f:
        nx, ny, dx = f.readline().split()
        nx, ny, dx = int(nx), int(ny), float(dx)
        data = np.loadtxt(f, delimiter=",") if os.path.getsize(path) > 40 else np.empty((0, 3))
    if data.ndim == 1:
        data = data.reshape(1, -1)
    W, H = nx * S, ny * S
    liq = np.zeros((H, W), float)
    if len(data):
        xs = data[:, 0] / dx * S
        ys = data[:, 1] / dx * S
        t  = data[:, 2].astype(int)
        pj = (H - 1 - ys).astype(int)
        pi = xs.astype(int)
        ok = (pi >= 0) & (pi < W) & (pj >= 0) & (pj < H) & (t == 0)
        np.add.at(liq, (pj[ok], pi[ok]), 1.0)

    # smooth the splat into a continuous density field
    liq = blur2d(liq, S * 0.9)

    # opacity, normalized to a robust per-frame reference
    nz = liq[liq > 1e-6]
    ref = np.percentile(nz, 80) if nz.size else 1.0
    op = smoothstep(liq / (ref + 1e-9))

    # vertical background gradient
    gy = np.linspace(0, 1, H)[:, None]
    bg = BG_TOP[None, None, :] * (1 - gy[..., None]) + BG_BOT[None, None, :] * gy[..., None]
    bg = np.broadcast_to(bg, (H, W, 3)).copy()

    # water body colour: thicker -> deeper/darker, thinner -> brighter
    water = lerp(SHALLOW, DEEP, smoothstep(op))

    # surface highlight from the density gradient (interface catches light),
    # biased toward up-facing surfaces (a soft top light)
    gradj, gradi = np.gradient(op)
    grad = np.sqrt(gradi * gradi + gradj * gradj)
    rim = smoothstep(grad / (grad.max() + 1e-9) * 3.0)
    topface = np.clip(gradj, 0, None)          # op increases downward at a top surface
    topface = topface / (topface.max() + 1e-9)
    spec = rim * (0.4 + 0.6 * smoothstep(topface * 2.0))

    out = bg * (1 - op[..., None]) + water * op[..., None]
    out = out + RIM[None, None, :] * spec[..., None] * 0.9
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else src
    S   = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "render_*.csv")))
    if not files:
        print("no render_*.csv found in", src); return
    frames = []
    for i, p in enumerate(files):
        img = render_frame(p, S)
        png = os.path.join(out, f"shaded_{i:03d}.png")
        img.save(png)
        frames.append(img)
    gif = os.path.join(out, "rough_render.gif")
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=110, loop=0)
    print(f"rendered {len(frames)} frames -> {gif}")

if __name__ == "__main__":
    main()
