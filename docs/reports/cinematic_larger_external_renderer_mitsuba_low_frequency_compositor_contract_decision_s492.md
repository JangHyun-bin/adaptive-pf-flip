# S492 Mitsuba Low Frequency Compositor Contract Decision

Generated UTC: `2026-06-20T17:57:20+00:00`

## Decision

Promote S492 as the engine/compositor handoff contract for the low-frequency parity correction.

S492 does not claim that Mitsuba XML itself now owns the correction. The correction is a post-tonemap operation, so the correct handoff target is a renderer output compositor or shader pass. The contract now states the exact operation, required texture bindings, GLSL/HLSL reference snippets, and a parity oracle against S491.

## Evidence

- S492 contract report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_compositor_contract_s492.md`
- S492 contract JSON: `build/shots/s492_mitsuba_low_frequency_compositor_contract/low_frequency_compositor_contract.json`
- GLSL reference: `build/shots/s492_mitsuba_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.glsl`
- HLSL reference: `build/shots/s492_mitsuba_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.hlsl`
- S491 parity oracle: `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/grade_summary.json`

## Contract

- Stage: `post_tonemap`.
- Color space: `tonemapped_rgb_normalized`.
- Expression: `clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)`.
- Texture gain: `1.0`.
- Required bindings: `base_rgb`, `positive_delta_rgb`, `negative_delta_rgb`.
- Optional binding: `dark_damping_weight_luma`.
- Promotion oracle: S491 with max absolute diff `0`.

## Checks

- Frames: `8`.
- Missing references: `0`.
- Max oracle abs diff: `0`.
- Max oracle mean diff: `0.0`.
- Max mismatched coverage: `0.0`.
- Max changed coverage: `0.18508873456790123`.
- Max layer delta: `23`.
- Target-gap mean MAD: `19.144350646219134`.
- Target-gap max MAD: `23.95285943930041`.
- Target-gap max gap: `214`.
- Shader bytes: `2029`.

## Interpretation

S492 is the first point where the low-frequency correction is no longer just a Python preview or texture consumer. It is now an explicit renderer-facing shader contract. The next implementation should run this contract in an actual compositor runtime and compare that runtime output against S491.

## Next

Implement S493 as a runtime compositor proof:

- use the S492 GLSL contract or a WebGL/DirectX-equivalent implementation;
- bind the S489 textures frame-by-frame;
- emit rendered compositor frames;
- compare against S491 with max abs diff `0` or document any sampling/color-space differences explicitly.
