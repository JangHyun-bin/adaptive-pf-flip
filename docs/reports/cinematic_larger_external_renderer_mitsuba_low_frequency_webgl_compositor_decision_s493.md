# S493 Mitsuba Low Frequency WebGL Compositor Decision

Generated UTC: `2026-06-20T18:12:05+00:00`

## Decision

Promote S493 as the runtime parity proof for the low-frequency compositor contract.

S493 runs the S492 contract through Chromium/WebGL, emits compositor frames, and compares them against the S491 post-tonemap oracle. The runtime output is pixel-identical to S491 across all sampled frames.

## Evidence

- S493 WebGL proof report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_webgl_compositor_proof_s493.md`
- S493 summary JSON: `build/shots/s493_mitsuba_low_frequency_webgl_compositor_proof/webgl_compositor_proof_summary.json`
- S493 gallery: `build/shots/s493_mitsuba_low_frequency_webgl_compositor_proof/gallery/index.html`
- S492 contract: `build/shots/s492_mitsuba_low_frequency_compositor_contract/low_frequency_compositor_contract.json`
- S491 oracle: `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/grade_summary.json`

## Checks

- Browser: `chromium`.
- WebGL renderer: `WebKit WebGL`.
- WebGL vendor: `WebKit`.
- Orientation: `upload0_shader1`.
- Frames: `8`.
- Missing references: `0`.
- Max oracle abs diff: `0`.
- Max oracle mean diff: `0.0`.
- Max mismatched coverage: `0.0`.
- WebGL frame bytes: `5.18 MB`.
- GIF bytes: `4.21 MB`.

## Interpretation

S493 closes the main representation risk left by S492. The low-frequency correction has now passed through:

- S489 texture package;
- S490 texture consumer;
- S491 post-tonemap stage;
- S492 shader/compositor contract;
- S493 actual Chromium/WebGL runtime proof.

The result still does not beat the S478 proxy target-gap gate, but it gives us a reliable renderer-facing path for preserving the S487 low-frequency visual improvement without relying on an opaque Python-only preview.

## Next

Implement S494 as a packaged runtime handoff:

- include the S492 contract, S493 WebGL runtime page, S489 texture bindings, and S493 proof summary in one portable bundle;
- add a validator that checks shader artifacts, runtime proof, and target-gap references;
- use that bundle as the integration artifact for production renderer UI/export work.
