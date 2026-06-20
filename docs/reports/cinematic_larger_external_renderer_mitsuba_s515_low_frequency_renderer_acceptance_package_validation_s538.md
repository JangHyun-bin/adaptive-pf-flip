# S538 Mitsuba S515 Low Frequency Renderer Acceptance Package Validation

Generated UTC: `2026-06-20T20:15:21.390048+00:00`
Validation JSON: `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/renderer_acceptance_package_validation.json`
Status: `passed`
Package: `build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/renderer_acceptance_package.json`

## Summary

- Total checks: `106`
- Failed checks: `0`
- Skipped checks: `0`
- Public URL: `https://famous-premium-notes-kept.trycloudflare.com`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `package:schema` | `ok` | schema |
| `package:version` | `ok` | version |
| `source:runtime_summary` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime_preview_summary.json |
| `source:runtime_summary:schema` | `ok` | source schema |
| `source:runtime_summary:status` | `ok` | source status |
| `source:runtime_validation` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/renderer_runtime_preview_validation.json |
| `source:runtime_validation:schema` | `ok` | source schema |
| `source:runtime_validation:status` | `ok` | source status |
| `source:runtime_import_preview` | `ok` | build/shots/s535_mitsuba_s515_low_frequency_runtime_import_preview/runtime_import_preview.json |
| `source:runtime_import_preview:schema` | `ok` | source schema |
| `source:runtime_import_preview:status` | `ok` | source status |
| `source:runtime_handoff_bundle` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle.json |
| `source:runtime_handoff_bundle:schema` | `ok` | source schema |
| `source:runtime_handoff_bundle:status` | `ok` | source status |
| `source:publish_manifest` | `ok` | build/shots/s537_mitsuba_s515_low_frequency_renderer_runtime_preview_publish/publish_manifest.json |
| `contract:stage` | `ok` | stage |
| `contract:expression` | `ok` | low-frequency expression |
| `contract:binding:base_rgb` | `ok` | required binding present |
| `contract:binding:positive_delta_rgb` | `ok` | required binding present |
| `contract:binding:negative_delta_rgb` | `ok` | required binding present |
| `contract:shader:glsl` | `ok` | GLSL shader present |
| `contract:shader:hlsl` | `ok` | HLSL shader present |
| `contract:threshold:max_abs` | `ok` | max abs threshold |
| `contract:threshold:max_mean` | `ok` | max mean threshold |
| `package:status` | `ok` | status |
| `checks:runtime_summary_status` | `ok` | runtime summary status |
| `checks:runtime_validation_status` | `ok` | runtime validation status |
| `checks:runtime_validation_failed` | `ok` | runtime validation failures |
| `checks:runtime_import_status` | `ok` | runtime import status |
| `checks:runtime_handoff_status` | `ok` | runtime handoff status |
| `checks:frames` | `ok` | accepted all frames |
| `checks:missing` | `ok` | missing references |
| `checks:dimensions` | `ok` | dimension mismatches |
| `checks:oracle_abs` | `ok` | oracle max diff |
| `checks:webgl_abs` | `ok` | WebGL max diff |
| `checks:public_http` | `ok` | public HTTP checks |
| `checks:copied_files` | `ok` | copied file count |
| `frames:nonempty` | `ok` | frame list nonempty |
| `frame:0:oracle_abs` | `ok` | oracle max diff |
| `frame:0:oracle_mean` | `ok` | oracle mean diff |
| `frame:0:webgl_abs` | `ok` | WebGL max diff |
| `frame:0:webgl_mean` | `ok` | WebGL mean diff |
| `frame:0:binding:base_rgb` | `ok` | binding path present |
| `frame:0:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:0:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:1:oracle_abs` | `ok` | oracle max diff |
| `frame:1:oracle_mean` | `ok` | oracle mean diff |
| `frame:1:webgl_abs` | `ok` | WebGL max diff |
| `frame:1:webgl_mean` | `ok` | WebGL mean diff |
| `frame:1:binding:base_rgb` | `ok` | binding path present |
| `frame:1:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:1:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:2:oracle_abs` | `ok` | oracle max diff |
| `frame:2:oracle_mean` | `ok` | oracle mean diff |
| `frame:2:webgl_abs` | `ok` | WebGL max diff |
| `frame:2:webgl_mean` | `ok` | WebGL mean diff |
| `frame:2:binding:base_rgb` | `ok` | binding path present |
| `frame:2:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:2:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:3:oracle_abs` | `ok` | oracle max diff |
| `frame:3:oracle_mean` | `ok` | oracle mean diff |
| `frame:3:webgl_abs` | `ok` | WebGL max diff |
| `frame:3:webgl_mean` | `ok` | WebGL mean diff |
| `frame:3:binding:base_rgb` | `ok` | binding path present |
| `frame:3:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:3:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:4:oracle_abs` | `ok` | oracle max diff |
| `frame:4:oracle_mean` | `ok` | oracle mean diff |
| `frame:4:webgl_abs` | `ok` | WebGL max diff |
| `frame:4:webgl_mean` | `ok` | WebGL mean diff |
| `frame:4:binding:base_rgb` | `ok` | binding path present |
| `frame:4:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:4:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:5:oracle_abs` | `ok` | oracle max diff |
| `frame:5:oracle_mean` | `ok` | oracle mean diff |
| `frame:5:webgl_abs` | `ok` | WebGL max diff |
| `frame:5:webgl_mean` | `ok` | WebGL mean diff |
| `frame:5:binding:base_rgb` | `ok` | binding path present |
| `frame:5:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:5:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:6:oracle_abs` | `ok` | oracle max diff |
| `frame:6:oracle_mean` | `ok` | oracle mean diff |
| `frame:6:webgl_abs` | `ok` | WebGL max diff |
| `frame:6:webgl_mean` | `ok` | WebGL mean diff |
| `frame:6:binding:base_rgb` | `ok` | binding path present |
| `frame:6:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:6:binding:negative_delta_rgb` | `ok` | binding path present |
| `frame:7:oracle_abs` | `ok` | oracle max diff |
| `frame:7:oracle_mean` | `ok` | oracle mean diff |
| `frame:7:webgl_abs` | `ok` | WebGL max diff |
| `frame:7:webgl_mean` | `ok` | WebGL mean diff |
| `frame:7:binding:base_rgb` | `ok` | binding path present |
| `frame:7:binding:positive_delta_rgb` | `ok` | binding path present |
| `frame:7:binding:negative_delta_rgb` | `ok` | binding path present |
| `public:url` | `ok` | public URL present |
| `public:manifest_checks` | `ok` | manifest HTTP checks |
| `public:live_index` | `ok` | {'status': 200, 'content_length': 3574} |
| `copied:metadata:renderer_runtime_preview_summary` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/renderer_runtime_preview_summary.json |
| `copied:metadata:renderer_runtime_preview_validation` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/renderer_runtime_preview_validation.json |
| `copied:metadata:runtime_import_preview` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/runtime_import_preview.json |
| `copied:metadata:runtime_handoff_bundle` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/runtime_handoff_bundle.json |
| `copied:metadata:publish_manifest` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/metadata/publish_manifest.json |
| `copied:glsl_shader:low_frequency_parity_post_tonemap.glsl` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl |
| `copied:hlsl_shader:low_frequency_parity_post_tonemap.hlsl` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl |
| `copied:runtime_gif:Renderer Runtime GIF` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/gallery/shot.gif |
| `copied:strip_gif:Runtime Strip GIF` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/gallery/runtime_consumer_strips.gif |
