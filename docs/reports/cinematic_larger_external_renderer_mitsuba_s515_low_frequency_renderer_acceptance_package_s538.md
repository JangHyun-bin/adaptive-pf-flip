# S538 Mitsuba S515 Low Frequency Renderer Acceptance Package

Generated UTC: `2026-06-20T20:15:20.095278+00:00`
Package JSON: `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/renderer_acceptance_package.json`
Status: `ready`
Public URL: `https://famous-premium-notes-kept.trycloudflare.com`

## Checks

- Runtime summary status: `ready`
- Runtime validation status: `passed`
- Runtime import status: `ready`
- Source frames: `8`
- Accepted frames: `8`
- Max oracle abs diff: `0`
- Max WebGL abs diff: `0`
- Public HTTP checks passed: `True`
- Missing references: `0`

## Copied Files

| Label | Role | Size | Path |
| --- | --- | ---: | --- |
| renderer_runtime_preview_summary | `metadata` | 24.75 KB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/renderer_runtime_preview_summary.json` |
| renderer_runtime_preview_validation | `metadata` | 18.14 KB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/renderer_runtime_preview_validation.json` |
| runtime_import_preview | `metadata` | 65.39 KB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/runtime_import_preview.json` |
| runtime_handoff_bundle | `metadata` | 80.67 KB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/runtime_handoff_bundle.json` |
| publish_manifest | `metadata` | 2.23 KB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/publish_manifest.json` |
| low_frequency_parity_post_tonemap.glsl | `glsl_shader` | 705 B | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl` |
| low_frequency_parity_post_tonemap.hlsl | `hlsl_shader` | 859 B | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl` |
| Renderer Runtime GIF | `runtime_gif` | 1.34 MB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/gallery/shot.gif` |
| Runtime Strip GIF | `strip_gif` | 6.58 MB | `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/gallery/runtime_consumer_strips.gif` |

## Acceptance Contract

- Stage: `renderer_post_tonemap_low_frequency_runtime_consumer`
- Required bindings: `base_rgb, positive_delta_rgb, negative_delta_rgb`
- Max abs threshold: `0`
- Max mean threshold: `0.0`

## Next

Build a production-style renderer job manifest from this S515-calibrated acceptance package.
