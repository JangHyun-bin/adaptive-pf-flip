# S541 Mitsuba S515 Low Frequency Backend Adapter Validation

Generated UTC: `2026-06-20T20:17:21.569228+00:00`
Validation JSON: `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/backend_adapter_validation.json`
Status: `passed`
Manifest: `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/backend_adapter_manifest.json`

## Summary

- Total checks: `185`
- Failed checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest:schema` | `ok` | schema |
| `manifest:version` | `ok` | version |
| `source:job` | `ok` | build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/renderer_job_manifest.json |
| `source:schema` | `ok` | source schema |
| `source:status` | `ok` | source status |
| `policy:root_manifest_only` | `ok` | root manifest only |
| `policy:root_manifest_schema` | `ok` | root schema |
| `contract:stage` | `ok` | stage |
| `contract:expression` | `ok` | expression |
| `contract:binding:base_rgb` | `ok` | required binding present |
| `contract:binding:positive_delta_rgb` | `ok` | required binding present |
| `contract:binding:negative_delta_rgb` | `ok` | required binding present |
| `shader:glsl` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl |
| `shader:hlsl` | `ok` | build/shots/s538_mitsuba_s515_low_frequency_renderer_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl |
| `manifest:status` | `ok` | status |
| `checks:source_status` | `ok` | source job status |
| `checks:frames` | `ok` | scene count |
| `checks:inputs` | `ok` | required inputs |
| `checks:missing_inputs` | `ok` | missing inputs |
| `checks:missing_shaders` | `ok` | missing shaders |
| `checks:reference_hash` | `ok` | reference hashes |
| `checks:output_targets` | `ok` | output targets |
| `checks:scene_bytes` | `ok` | scene descriptor bytes |
| `command_list` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/backend_commands.txt |
| `frames:nonempty` | `ok` | frames nonempty |
| `frame:0:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_base_rgb.png |
| `frame:0:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0000.png |
| `frame:0:output:image` | `ok` | output path |
| `frame:0:output:metadata` | `ok` | output path |
| `frame:0:output:validation` | `ok` | output path |
| `frame:0:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0000_backend_scene.json |
| `frame:0:scene_schema` | `ok` | scene schema |
| `frame:0:scene_stage` | `ok` | scene stage |
| `frame:0:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:0:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_base_rgb.png |
| `frame:0:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:0:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:0:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0000.png |
| `frame:0:scene_output:image` | `ok` | scene output path |
| `frame:0:scene_output:metadata` | `ok` | scene output path |
| `frame:0:scene_output:validation` | `ok` | scene output path |
| `frame:1:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_base_rgb.png |
| `frame:1:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0001.png |
| `frame:1:output:image` | `ok` | output path |
| `frame:1:output:metadata` | `ok` | output path |
| `frame:1:output:validation` | `ok` | output path |
| `frame:1:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0001_backend_scene.json |
| `frame:1:scene_schema` | `ok` | scene schema |
| `frame:1:scene_stage` | `ok` | scene stage |
| `frame:1:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:1:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_base_rgb.png |
| `frame:1:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:1:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:1:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0001.png |
| `frame:1:scene_output:image` | `ok` | scene output path |
| `frame:1:scene_output:metadata` | `ok` | scene output path |
| `frame:1:scene_output:validation` | `ok` | scene output path |
| `frame:2:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_base_rgb.png |
| `frame:2:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0002.png |
| `frame:2:output:image` | `ok` | output path |
| `frame:2:output:metadata` | `ok` | output path |
| `frame:2:output:validation` | `ok` | output path |
| `frame:2:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0002_backend_scene.json |
| `frame:2:scene_schema` | `ok` | scene schema |
| `frame:2:scene_stage` | `ok` | scene stage |
| `frame:2:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:2:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_base_rgb.png |
| `frame:2:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:2:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:2:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0002.png |
| `frame:2:scene_output:image` | `ok` | scene output path |
| `frame:2:scene_output:metadata` | `ok` | scene output path |
| `frame:2:scene_output:validation` | `ok` | scene output path |
| `frame:3:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_base_rgb.png |
| `frame:3:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0003.png |
| `frame:3:output:image` | `ok` | output path |
| `frame:3:output:metadata` | `ok` | output path |
| `frame:3:output:validation` | `ok` | output path |
| `frame:3:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0003_backend_scene.json |
| `frame:3:scene_schema` | `ok` | scene schema |
| `frame:3:scene_stage` | `ok` | scene stage |
| `frame:3:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:3:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_base_rgb.png |
| `frame:3:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:3:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:3:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0003.png |
| `frame:3:scene_output:image` | `ok` | scene output path |
| `frame:3:scene_output:metadata` | `ok` | scene output path |
| `frame:3:scene_output:validation` | `ok` | scene output path |
| `frame:4:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_base_rgb.png |
| `frame:4:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0004.png |
| `frame:4:output:image` | `ok` | output path |
| `frame:4:output:metadata` | `ok` | output path |
| `frame:4:output:validation` | `ok` | output path |
| `frame:4:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0004_backend_scene.json |
| `frame:4:scene_schema` | `ok` | scene schema |
| `frame:4:scene_stage` | `ok` | scene stage |
| `frame:4:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:4:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_base_rgb.png |
| `frame:4:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:4:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:4:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0004.png |
| `frame:4:scene_output:image` | `ok` | scene output path |
| `frame:4:scene_output:metadata` | `ok` | scene output path |
| `frame:4:scene_output:validation` | `ok` | scene output path |
| `frame:5:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_base_rgb.png |
| `frame:5:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0005.png |
| `frame:5:output:image` | `ok` | output path |
| `frame:5:output:metadata` | `ok` | output path |
| `frame:5:output:validation` | `ok` | output path |
| `frame:5:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0005_backend_scene.json |
| `frame:5:scene_schema` | `ok` | scene schema |
| `frame:5:scene_stage` | `ok` | scene stage |
| `frame:5:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:5:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_base_rgb.png |
| `frame:5:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:5:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:5:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0005.png |
| `frame:5:scene_output:image` | `ok` | scene output path |
| `frame:5:scene_output:metadata` | `ok` | scene output path |
| `frame:5:scene_output:validation` | `ok` | scene output path |
| `frame:6:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_base_rgb.png |
| `frame:6:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0006.png |
| `frame:6:output:image` | `ok` | output path |
| `frame:6:output:metadata` | `ok` | output path |
| `frame:6:output:validation` | `ok` | output path |
| `frame:6:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0006_backend_scene.json |
| `frame:6:scene_schema` | `ok` | scene schema |
| `frame:6:scene_stage` | `ok` | scene stage |
| `frame:6:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:6:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_base_rgb.png |
| `frame:6:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:6:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:6:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0006.png |
| `frame:6:scene_output:image` | `ok` | scene output path |
| `frame:6:scene_output:metadata` | `ok` | scene output path |
| `frame:6:scene_output:validation` | `ok` | scene output path |
| `frame:7:input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_base_rgb.png |
| `frame:7:input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0007.png |
| `frame:7:output:image` | `ok` | output path |
| `frame:7:output:metadata` | `ok` | output path |
| `frame:7:output:validation` | `ok` | output path |
| `frame:7:scene` | `ok` | build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0007_backend_scene.json |
| `frame:7:scene_schema` | `ok` | scene schema |
| `frame:7:scene_stage` | `ok` | scene stage |
| `frame:7:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:7:scene_input:base_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_base_rgb.png |
| `frame:7:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:7:scene_input:positive_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:7:scene_input:negative_delta_rgb` | `ok` | build/shots/s534_mitsuba_s515_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:scene_reference` | `ok` | build/shots/s536_mitsuba_s515_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0007.png |
| `frame:7:scene_output:image` | `ok` | scene output path |
| `frame:7:scene_output:metadata` | `ok` | scene output path |
| `frame:7:scene_output:validation` | `ok` | scene output path |
