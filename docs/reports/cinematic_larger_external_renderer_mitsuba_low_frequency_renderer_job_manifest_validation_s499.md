# S499 Mitsuba Low Frequency Renderer Job Manifest Validation

Generated UTC: `2026-06-20T18:45:47.596767+00:00`
Validation JSON: `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/renderer_job_manifest_validation.json`
Status: `passed`
Job: `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/renderer_job_manifest.json`

## Summary

- Total checks: `126`
- Failed checks: `0`
- Skipped checks: `0`
- Public URL: `https://thanks-pending-expired-enlargement.trycloudflare.com`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `job:schema` | `ok` | schema |
| `job:version` | `ok` | version |
| `source:acceptance_package` | `ok` | build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/renderer_acceptance_package.json |
| `source:schema` | `ok` | package schema |
| `source:status` | `ok` | package status |
| `policy:root_manifest_only` | `ok` | single root manifest policy |
| `policy:root_manifest_schema` | `ok` | root manifest schema |
| `contract:stage` | `ok` | stage |
| `contract:expression` | `ok` | expression |
| `contract:binding:base_rgb` | `ok` | required binding present |
| `contract:binding:positive_delta_rgb` | `ok` | required binding present |
| `contract:binding:negative_delta_rgb` | `ok` | required binding present |
| `contract:max_abs` | `ok` | max abs threshold |
| `contract:max_mean` | `ok` | max mean threshold |
| `contract:shader_count` | `ok` | shader refs present |
| `contract:shader:glsl` | `ok` | build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl |
| `contract:shader:hlsl` | `ok` | build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl |
| `job:status` | `ok` | status |
| `checks:package_status` | `ok` | package status |
| `checks:package_validation` | `ok` | package validation status |
| `checks:frames` | `ok` | frame count |
| `checks:bindings` | `ok` | all required bindings present |
| `checks:missing_inputs` | `ok` | missing inputs |
| `checks:missing_shaders` | `ok` | missing shaders |
| `checks:reference_hash` | `ok` | reference hash mismatches |
| `checks:public_http` | `ok` | public HTTP passed |
| `frames:nonempty` | `ok` | frame jobs nonempty |
| `frame:0:input_present:base_rgb` | `ok` | required input in job |
| `frame:0:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_base_rgb.png |
| `frame:0:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:0:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:0:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0000.png |
| `frame:0:output_target:image` | `ok` | output target under output_root |
| `frame:0:output_target:metadata` | `ok` | output target under output_root |
| `frame:0:output_target:validation` | `ok` | output target under output_root |
| `frame:0:oracle_abs` | `ok` | oracle threshold |
| `frame:0:webgl_abs` | `ok` | WebGL threshold |
| `frame:1:input_present:base_rgb` | `ok` | required input in job |
| `frame:1:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_base_rgb.png |
| `frame:1:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:1:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:1:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0001.png |
| `frame:1:output_target:image` | `ok` | output target under output_root |
| `frame:1:output_target:metadata` | `ok` | output target under output_root |
| `frame:1:output_target:validation` | `ok` | output target under output_root |
| `frame:1:oracle_abs` | `ok` | oracle threshold |
| `frame:1:webgl_abs` | `ok` | WebGL threshold |
| `frame:2:input_present:base_rgb` | `ok` | required input in job |
| `frame:2:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_base_rgb.png |
| `frame:2:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:2:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:2:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0002.png |
| `frame:2:output_target:image` | `ok` | output target under output_root |
| `frame:2:output_target:metadata` | `ok` | output target under output_root |
| `frame:2:output_target:validation` | `ok` | output target under output_root |
| `frame:2:oracle_abs` | `ok` | oracle threshold |
| `frame:2:webgl_abs` | `ok` | WebGL threshold |
| `frame:3:input_present:base_rgb` | `ok` | required input in job |
| `frame:3:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_base_rgb.png |
| `frame:3:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:3:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:3:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0003.png |
| `frame:3:output_target:image` | `ok` | output target under output_root |
| `frame:3:output_target:metadata` | `ok` | output target under output_root |
| `frame:3:output_target:validation` | `ok` | output target under output_root |
| `frame:3:oracle_abs` | `ok` | oracle threshold |
| `frame:3:webgl_abs` | `ok` | WebGL threshold |
| `frame:4:input_present:base_rgb` | `ok` | required input in job |
| `frame:4:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_base_rgb.png |
| `frame:4:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:4:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:4:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0004.png |
| `frame:4:output_target:image` | `ok` | output target under output_root |
| `frame:4:output_target:metadata` | `ok` | output target under output_root |
| `frame:4:output_target:validation` | `ok` | output target under output_root |
| `frame:4:oracle_abs` | `ok` | oracle threshold |
| `frame:4:webgl_abs` | `ok` | WebGL threshold |
| `frame:5:input_present:base_rgb` | `ok` | required input in job |
| `frame:5:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_base_rgb.png |
| `frame:5:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:5:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:5:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0005.png |
| `frame:5:output_target:image` | `ok` | output target under output_root |
| `frame:5:output_target:metadata` | `ok` | output target under output_root |
| `frame:5:output_target:validation` | `ok` | output target under output_root |
| `frame:5:oracle_abs` | `ok` | oracle threshold |
| `frame:5:webgl_abs` | `ok` | WebGL threshold |
| `frame:6:input_present:base_rgb` | `ok` | required input in job |
| `frame:6:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_base_rgb.png |
| `frame:6:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:6:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:6:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0006.png |
| `frame:6:output_target:image` | `ok` | output target under output_root |
| `frame:6:output_target:metadata` | `ok` | output target under output_root |
| `frame:6:output_target:validation` | `ok` | output target under output_root |
| `frame:6:oracle_abs` | `ok` | oracle threshold |
| `frame:6:webgl_abs` | `ok` | WebGL threshold |
| `frame:7:input_present:base_rgb` | `ok` | required input in job |
| `frame:7:input:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_base_rgb.png |
| `frame:7:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:7:input:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:7:input:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:accepted_reference` | `ok` | build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0007.png |
| `frame:7:output_target:image` | `ok` | output target under output_root |
| `frame:7:output_target:metadata` | `ok` | output target under output_root |
| `frame:7:output_target:validation` | `ok` | output target under output_root |
| `frame:7:oracle_abs` | `ok` | oracle threshold |
| `frame:7:webgl_abs` | `ok` | WebGL threshold |
| `public:url` | `ok` | public URL present |
| `public:manifest_checks` | `ok` | manifest HTTP checks |
| `public:live_index` | `ok` | {'status': 200, 'content_length': 10349} |
