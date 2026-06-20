# S557 Mitsuba S515 Full48 T4 Sequence Acceptance Package

Generated UTC: `2026-06-20T20:58:36.430450+00:00`
Package JSON: `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/renderer_acceptance_package.json`
Status: `ready`
Public URL: `https://operating-intended-analyses-individually.trycloudflare.com`

## Checks

- Sequence status: `ready`
- Runtime import status: `ready`
- Source frames: `48`
- Accepted frames: `48`
- Required bindings present: `144/144`
- Missing references: `0`
- Reference hash mismatches: `0`
- Max oracle abs diff: `0`
- Max WebGL abs diff: `0`
- Public HTTP checks passed: `True`

## Copied Files

| Label | Role | Size | Path |
| --- | --- | ---: | --- |
| sequence_adapter_summary | `metadata` | 112.75 KB | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/metadata/sequence_adapter_summary.json` |
| runtime_import_preview | `metadata` | 65.39 KB | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/metadata/runtime_import_preview.json` |
| mitsuba_render_manifest | `metadata` | 55.99 KB | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/metadata/mitsuba_render_manifest.json` |
| publish_manifest | `metadata` | 2.30 KB | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/metadata/publish_manifest.json` |
| low_frequency_parity_post_tonemap.glsl | `glsl_shader` | 705 B | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl` |
| low_frequency_parity_post_tonemap.hlsl | `hlsl_shader` | 859 B | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl` |
| Corrected Sequence GIF | `corrected_sequence_gif` | 6.78 MB | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/gallery/shot.gif` |
| Sequence Strip GIF | `sequence_strip_gif` | 28.77 MB | `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/gallery/sequence_strips.gif` |

## Acceptance Contract

- Stage: `renderer_post_tonemap_low_frequency_runtime_consumer`
- Expression: `clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)`
- Required bindings: `base_rgb, positive_delta_rgb, negative_delta_rgb`
- Optional bindings: `dark_damping_weight_luma, correction_mask`

## Next

Build the full-sequence renderer job manifest and dry-run it against the accepted references.
