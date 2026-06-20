# S467 Mitsuba Signed Response Layer Decision

## Decision

Promote the signed response layer path as the current compositor-compatible visual cache for the cinematic Mitsuba bridge.

This does not replace the renderer-native patch work. It gives the pipeline a reproducible layer artifact, with per-frame RGBA response layers and composite frames, while the renderer-native emitter path remains experimental.

## Evidence

- Layer cache status: `ready`
- Frames: `8`
- Selected requests: `12`
- Applied requests: `12`
- Max changed coverage: `0.019110725308641975`
- Max layer delta: `30`
- Layer bytes: `44.10 KB`
- Composite bytes: `1.79 MB`
- Target-gap mean MAD: `19.10240579989712`
- Target-gap max MAD: `23.950307355967077`
- Target-gap max absolute gap: `176`

The target-gap score matches the previous best S463 image-space signed response path, but S467 stores the correction as an explicit cache:

- `build/shots/s467_mitsuba_signed_response_layer/signed_response_layer_summary.json`
- `build/shots/s467_mitsuba_signed_response_layer/layers/frame_####_signed_response_layer.png`
- `build/shots/s467_mitsuba_signed_response_layer/composites/frame_####.png`
- `build/shots/s467_mitsuba_signed_response_layer/gallery/index.html`

## Interpretation

S466 showed that the native Mitsuba residual-patch footprint lands inside the requested screen regions. That means placement is not the main problem. The remaining problem is weak visible energy transfer through the renderer/material/visibility path.

S467 therefore creates the next practical bridge: keep Mitsuba as the physical base render, then export a deterministic signed response layer that a compositor or cache consumer can apply explicitly. This is more inspectable and reproducible than treating the adjusted PNG as an opaque final image.

## Next

Use the S467 summary schema as the promoted visual-cache input for the next renderer handoff step, then package it with the cinematic cache metadata so downstream preview/render tools can consume base render, response layer, composite frame, and target-gap evidence together.
