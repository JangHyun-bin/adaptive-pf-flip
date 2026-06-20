# S498 Mitsuba Low Frequency Renderer Acceptance Package

Generated UTC: `2026-06-20T18:40:31.554521+00:00`
Package JSON: `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/renderer_acceptance_package.json`
Status: `ready`
Public URL: `https://thanks-pending-expired-enlargement.trycloudflare.com`

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
| renderer_runtime_preview_summary | `metadata` | 24.14 KB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/metadata/renderer_runtime_preview_summary.json` |
| renderer_runtime_preview_validation | `metadata` | 17.90 KB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/metadata/renderer_runtime_preview_validation.json` |
| runtime_import_preview | `metadata` | 64.57 KB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/metadata/runtime_import_preview.json` |
| runtime_handoff_bundle | `metadata` | 79.73 KB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/metadata/runtime_handoff_bundle.json` |
| publish_manifest | `metadata` | 2.21 KB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/metadata/publish_manifest.json` |
| low_frequency_parity_post_tonemap.glsl | `glsl_shader` | 705 B | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl` |
| low_frequency_parity_post_tonemap.hlsl | `hlsl_shader` | 859 B | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl` |
| Renderer Runtime GIF | `runtime_gif` | 1.14 MB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/gallery/shot.gif` |
| Runtime Strip GIF | `strip_gif` | 5.37 MB | `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/gallery/runtime_consumer_strips.gif` |

## Acceptance Contract

- Stage: `renderer_post_tonemap_low_frequency_runtime_consumer`
- Required bindings: `base_rgb, positive_delta_rgb, negative_delta_rgb`
- Max abs threshold: `0`
- Max mean threshold: `0.0`

## Next

Use this acceptance package as the handoff gate before implementing the production renderer/export runner.
