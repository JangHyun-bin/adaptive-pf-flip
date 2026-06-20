# S560 Mitsuba S515 Full48 T4 Backend Adapter Validation

Generated UTC: `2026-06-20T21:00:42.313023+00:00`
Validation JSON: `build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/backend_adapter_validation.json`
Status: `passed`
Manifest: `build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/backend_adapter_manifest.json`

## Summary

- Total checks: `985`
- Failed checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest:schema` | `ok` | schema |
| `manifest:version` | `ok` | version |
| `source:job` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/renderer_job_manifest.json |
| `source:schema` | `ok` | source schema |
| `source:status` | `ok` | source status |
| `policy:root_manifest_only` | `ok` | root manifest only |
| `policy:root_manifest_schema` | `ok` | root schema |
| `contract:stage` | `ok` | stage |
| `contract:expression` | `ok` | expression |
| `contract:binding:base_rgb` | `ok` | required binding present |
| `contract:binding:positive_delta_rgb` | `ok` | required binding present |
| `contract:binding:negative_delta_rgb` | `ok` | required binding present |
| `shader:glsl` | `ok` | build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl |
| `shader:hlsl` | `ok` | build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl |
| `manifest:status` | `ok` | status |
| `checks:source_status` | `ok` | source job status |
| `checks:frames` | `ok` | scene count |
| `checks:inputs` | `ok` | required inputs |
| `checks:missing_inputs` | `ok` | missing inputs |
| `checks:missing_shaders` | `ok` | missing shaders |
| `checks:reference_hash` | `ok` | reference hashes |
| `checks:output_targets` | `ok` | output targets |
| `checks:scene_bytes` | `ok` | scene descriptor bytes |
| `command_list` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/backend_commands.txt |
| `frames:nonempty` | `ok` | frames nonempty |
| `frame:0:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png |
| `frame:0:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0000.png |
| `frame:0:output:image` | `ok` | output path |
| `frame:0:output:metadata` | `ok` | output path |
| `frame:0:output:validation` | `ok` | output path |
| `frame:0:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0000_backend_scene.json |
| `frame:0:scene_schema` | `ok` | scene schema |
| `frame:0:scene_stage` | `ok` | scene stage |
| `frame:0:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:0:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png |
| `frame:0:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:0:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:0:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0000.png |
| `frame:0:scene_output:image` | `ok` | scene output path |
| `frame:0:scene_output:metadata` | `ok` | scene output path |
| `frame:0:scene_output:validation` | `ok` | scene output path |
| `frame:1:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0001.png |
| `frame:1:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0001.png |
| `frame:1:output:image` | `ok` | output path |
| `frame:1:output:metadata` | `ok` | output path |
| `frame:1:output:validation` | `ok` | output path |
| `frame:1:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0001_backend_scene.json |
| `frame:1:scene_schema` | `ok` | scene schema |
| `frame:1:scene_stage` | `ok` | scene stage |
| `frame:1:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:1:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0001.png |
| `frame:1:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:1:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:1:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0001.png |
| `frame:1:scene_output:image` | `ok` | scene output path |
| `frame:1:scene_output:metadata` | `ok` | scene output path |
| `frame:1:scene_output:validation` | `ok` | scene output path |
| `frame:2:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0002.png |
| `frame:2:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0002.png |
| `frame:2:output:image` | `ok` | output path |
| `frame:2:output:metadata` | `ok` | output path |
| `frame:2:output:validation` | `ok` | output path |
| `frame:2:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0002_backend_scene.json |
| `frame:2:scene_schema` | `ok` | scene schema |
| `frame:2:scene_stage` | `ok` | scene stage |
| `frame:2:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:2:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0002.png |
| `frame:2:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:2:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:2:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0002.png |
| `frame:2:scene_output:image` | `ok` | scene output path |
| `frame:2:scene_output:metadata` | `ok` | scene output path |
| `frame:2:scene_output:validation` | `ok` | scene output path |
| `frame:3:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0003.png |
| `frame:3:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0003.png |
| `frame:3:output:image` | `ok` | output path |
| `frame:3:output:metadata` | `ok` | output path |
| `frame:3:output:validation` | `ok` | output path |
| `frame:3:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0003_backend_scene.json |
| `frame:3:scene_schema` | `ok` | scene schema |
| `frame:3:scene_stage` | `ok` | scene stage |
| `frame:3:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:3:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0003.png |
| `frame:3:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:3:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:3:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0003.png |
| `frame:3:scene_output:image` | `ok` | scene output path |
| `frame:3:scene_output:metadata` | `ok` | scene output path |
| `frame:3:scene_output:validation` | `ok` | scene output path |
| `frame:4:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0004.png |
| `frame:4:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0004.png |
| `frame:4:output:image` | `ok` | output path |
| `frame:4:output:metadata` | `ok` | output path |
| `frame:4:output:validation` | `ok` | output path |
| `frame:4:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0004_backend_scene.json |
| `frame:4:scene_schema` | `ok` | scene schema |
| `frame:4:scene_stage` | `ok` | scene stage |
| `frame:4:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:4:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0004.png |
| `frame:4:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:4:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:4:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0004.png |
| `frame:4:scene_output:image` | `ok` | scene output path |
| `frame:4:scene_output:metadata` | `ok` | scene output path |
| `frame:4:scene_output:validation` | `ok` | scene output path |
| `frame:5:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0005.png |
| `frame:5:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0005.png |
| `frame:5:output:image` | `ok` | output path |
| `frame:5:output:metadata` | `ok` | output path |
| `frame:5:output:validation` | `ok` | output path |
| `frame:5:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0005_backend_scene.json |
| `frame:5:scene_schema` | `ok` | scene schema |
| `frame:5:scene_stage` | `ok` | scene stage |
| `frame:5:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:5:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0005.png |
| `frame:5:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:5:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:5:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0005.png |
| `frame:5:scene_output:image` | `ok` | scene output path |
| `frame:5:scene_output:metadata` | `ok` | scene output path |
| `frame:5:scene_output:validation` | `ok` | scene output path |
| `frame:6:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0006.png |
| `frame:6:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0006.png |
| `frame:6:output:image` | `ok` | output path |
| `frame:6:output:metadata` | `ok` | output path |
| `frame:6:output:validation` | `ok` | output path |
| `frame:6:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0006_backend_scene.json |
| `frame:6:scene_schema` | `ok` | scene schema |
| `frame:6:scene_stage` | `ok` | scene stage |
| `frame:6:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:6:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0006.png |
| `frame:6:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:6:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:6:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0006.png |
| `frame:6:scene_output:image` | `ok` | scene output path |
| `frame:6:scene_output:metadata` | `ok` | scene output path |
| `frame:6:scene_output:validation` | `ok` | scene output path |
| `frame:7:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0007.png |
| `frame:7:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0007.png |
| `frame:7:output:image` | `ok` | output path |
| `frame:7:output:metadata` | `ok` | output path |
| `frame:7:output:validation` | `ok` | output path |
| `frame:7:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0007_backend_scene.json |
| `frame:7:scene_schema` | `ok` | scene schema |
| `frame:7:scene_stage` | `ok` | scene stage |
| `frame:7:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:7:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0007.png |
| `frame:7:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:7:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:7:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0007.png |
| `frame:7:scene_output:image` | `ok` | scene output path |
| `frame:7:scene_output:metadata` | `ok` | scene output path |
| `frame:7:scene_output:validation` | `ok` | scene output path |
| `frame:8:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0008.png |
| `frame:8:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0008_negative_delta_rgb.png |
| `frame:8:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0008_positive_delta_rgb.png |
| `frame:8:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0008.png |
| `frame:8:output:image` | `ok` | output path |
| `frame:8:output:metadata` | `ok` | output path |
| `frame:8:output:validation` | `ok` | output path |
| `frame:8:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0008_backend_scene.json |
| `frame:8:scene_schema` | `ok` | scene schema |
| `frame:8:scene_stage` | `ok` | scene stage |
| `frame:8:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:8:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0008.png |
| `frame:8:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:8:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0008_positive_delta_rgb.png |
| `frame:8:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:8:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0008_negative_delta_rgb.png |
| `frame:8:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0008.png |
| `frame:8:scene_output:image` | `ok` | scene output path |
| `frame:8:scene_output:metadata` | `ok` | scene output path |
| `frame:8:scene_output:validation` | `ok` | scene output path |
| `frame:9:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0009.png |
| `frame:9:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0009_negative_delta_rgb.png |
| `frame:9:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0009_positive_delta_rgb.png |
| `frame:9:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0009.png |
| `frame:9:output:image` | `ok` | output path |
| `frame:9:output:metadata` | `ok` | output path |
| `frame:9:output:validation` | `ok` | output path |
| `frame:9:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0009_backend_scene.json |
| `frame:9:scene_schema` | `ok` | scene schema |
| `frame:9:scene_stage` | `ok` | scene stage |
| `frame:9:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:9:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0009.png |
| `frame:9:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:9:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0009_positive_delta_rgb.png |
| `frame:9:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:9:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0009_negative_delta_rgb.png |
| `frame:9:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0009.png |
| `frame:9:scene_output:image` | `ok` | scene output path |
| `frame:9:scene_output:metadata` | `ok` | scene output path |
| `frame:9:scene_output:validation` | `ok` | scene output path |
| `frame:10:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0010.png |
| `frame:10:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0010_negative_delta_rgb.png |
| `frame:10:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0010_positive_delta_rgb.png |
| `frame:10:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0010.png |
| `frame:10:output:image` | `ok` | output path |
| `frame:10:output:metadata` | `ok` | output path |
| `frame:10:output:validation` | `ok` | output path |
| `frame:10:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0010_backend_scene.json |
| `frame:10:scene_schema` | `ok` | scene schema |
| `frame:10:scene_stage` | `ok` | scene stage |
| `frame:10:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:10:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0010.png |
| `frame:10:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:10:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0010_positive_delta_rgb.png |
| `frame:10:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:10:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0010_negative_delta_rgb.png |
| `frame:10:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0010.png |
| `frame:10:scene_output:image` | `ok` | scene output path |
| `frame:10:scene_output:metadata` | `ok` | scene output path |
| `frame:10:scene_output:validation` | `ok` | scene output path |
| `frame:11:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0011.png |
| `frame:11:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0011_negative_delta_rgb.png |
| `frame:11:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0011_positive_delta_rgb.png |
| `frame:11:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0011.png |
| `frame:11:output:image` | `ok` | output path |
| `frame:11:output:metadata` | `ok` | output path |
| `frame:11:output:validation` | `ok` | output path |
| `frame:11:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0011_backend_scene.json |
| `frame:11:scene_schema` | `ok` | scene schema |
| `frame:11:scene_stage` | `ok` | scene stage |
| `frame:11:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:11:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0011.png |
| `frame:11:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:11:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0011_positive_delta_rgb.png |
| `frame:11:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:11:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0011_negative_delta_rgb.png |
| `frame:11:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0011.png |
| `frame:11:scene_output:image` | `ok` | scene output path |
| `frame:11:scene_output:metadata` | `ok` | scene output path |
| `frame:11:scene_output:validation` | `ok` | scene output path |
| `frame:12:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0012.png |
| `frame:12:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0012_negative_delta_rgb.png |
| `frame:12:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0012_positive_delta_rgb.png |
| `frame:12:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0012.png |
| `frame:12:output:image` | `ok` | output path |
| `frame:12:output:metadata` | `ok` | output path |
| `frame:12:output:validation` | `ok` | output path |
| `frame:12:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0012_backend_scene.json |
| `frame:12:scene_schema` | `ok` | scene schema |
| `frame:12:scene_stage` | `ok` | scene stage |
| `frame:12:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:12:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0012.png |
| `frame:12:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:12:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0012_positive_delta_rgb.png |
| `frame:12:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:12:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0012_negative_delta_rgb.png |
| `frame:12:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0012.png |
| `frame:12:scene_output:image` | `ok` | scene output path |
| `frame:12:scene_output:metadata` | `ok` | scene output path |
| `frame:12:scene_output:validation` | `ok` | scene output path |
| `frame:13:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0013.png |
| `frame:13:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0013_negative_delta_rgb.png |
| `frame:13:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0013_positive_delta_rgb.png |
| `frame:13:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0013.png |
| `frame:13:output:image` | `ok` | output path |
| `frame:13:output:metadata` | `ok` | output path |
| `frame:13:output:validation` | `ok` | output path |
| `frame:13:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0013_backend_scene.json |
| `frame:13:scene_schema` | `ok` | scene schema |
| `frame:13:scene_stage` | `ok` | scene stage |
| `frame:13:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:13:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0013.png |
| `frame:13:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:13:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0013_positive_delta_rgb.png |
| `frame:13:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:13:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0013_negative_delta_rgb.png |
| `frame:13:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0013.png |
| `frame:13:scene_output:image` | `ok` | scene output path |
| `frame:13:scene_output:metadata` | `ok` | scene output path |
| `frame:13:scene_output:validation` | `ok` | scene output path |
| `frame:14:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0014.png |
| `frame:14:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0014_negative_delta_rgb.png |
| `frame:14:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0014_positive_delta_rgb.png |
| `frame:14:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0014.png |
| `frame:14:output:image` | `ok` | output path |
| `frame:14:output:metadata` | `ok` | output path |
| `frame:14:output:validation` | `ok` | output path |
| `frame:14:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0014_backend_scene.json |
| `frame:14:scene_schema` | `ok` | scene schema |
| `frame:14:scene_stage` | `ok` | scene stage |
| `frame:14:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:14:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0014.png |
| `frame:14:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:14:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0014_positive_delta_rgb.png |
| `frame:14:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:14:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0014_negative_delta_rgb.png |
| `frame:14:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0014.png |
| `frame:14:scene_output:image` | `ok` | scene output path |
| `frame:14:scene_output:metadata` | `ok` | scene output path |
| `frame:14:scene_output:validation` | `ok` | scene output path |
| `frame:15:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0015.png |
| `frame:15:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0015_negative_delta_rgb.png |
| `frame:15:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0015_positive_delta_rgb.png |
| `frame:15:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0015.png |
| `frame:15:output:image` | `ok` | output path |
| `frame:15:output:metadata` | `ok` | output path |
| `frame:15:output:validation` | `ok` | output path |
| `frame:15:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0015_backend_scene.json |
| `frame:15:scene_schema` | `ok` | scene schema |
| `frame:15:scene_stage` | `ok` | scene stage |
| `frame:15:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:15:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0015.png |
| `frame:15:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:15:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0015_positive_delta_rgb.png |
| `frame:15:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:15:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0015_negative_delta_rgb.png |
| `frame:15:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0015.png |
| `frame:15:scene_output:image` | `ok` | scene output path |
| `frame:15:scene_output:metadata` | `ok` | scene output path |
| `frame:15:scene_output:validation` | `ok` | scene output path |
| `frame:16:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0016.png |
| `frame:16:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0016_negative_delta_rgb.png |
| `frame:16:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0016_positive_delta_rgb.png |
| `frame:16:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0016.png |
| `frame:16:output:image` | `ok` | output path |
| `frame:16:output:metadata` | `ok` | output path |
| `frame:16:output:validation` | `ok` | output path |
| `frame:16:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0016_backend_scene.json |
| `frame:16:scene_schema` | `ok` | scene schema |
| `frame:16:scene_stage` | `ok` | scene stage |
| `frame:16:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:16:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0016.png |
| `frame:16:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:16:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0016_positive_delta_rgb.png |
| `frame:16:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:16:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0016_negative_delta_rgb.png |
| `frame:16:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0016.png |
| `frame:16:scene_output:image` | `ok` | scene output path |
| `frame:16:scene_output:metadata` | `ok` | scene output path |
| `frame:16:scene_output:validation` | `ok` | scene output path |
| `frame:17:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0017.png |
| `frame:17:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0017_negative_delta_rgb.png |
| `frame:17:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0017_positive_delta_rgb.png |
| `frame:17:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0017.png |
| `frame:17:output:image` | `ok` | output path |
| `frame:17:output:metadata` | `ok` | output path |
| `frame:17:output:validation` | `ok` | output path |
| `frame:17:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0017_backend_scene.json |
| `frame:17:scene_schema` | `ok` | scene schema |
| `frame:17:scene_stage` | `ok` | scene stage |
| `frame:17:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:17:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0017.png |
| `frame:17:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:17:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0017_positive_delta_rgb.png |
| `frame:17:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:17:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0017_negative_delta_rgb.png |
| `frame:17:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0017.png |
| `frame:17:scene_output:image` | `ok` | scene output path |
| `frame:17:scene_output:metadata` | `ok` | scene output path |
| `frame:17:scene_output:validation` | `ok` | scene output path |
| `frame:18:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0018.png |
| `frame:18:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0018_negative_delta_rgb.png |
| `frame:18:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0018_positive_delta_rgb.png |
| `frame:18:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0018.png |
| `frame:18:output:image` | `ok` | output path |
| `frame:18:output:metadata` | `ok` | output path |
| `frame:18:output:validation` | `ok` | output path |
| `frame:18:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0018_backend_scene.json |
| `frame:18:scene_schema` | `ok` | scene schema |
| `frame:18:scene_stage` | `ok` | scene stage |
| `frame:18:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:18:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0018.png |
| `frame:18:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:18:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0018_positive_delta_rgb.png |
| `frame:18:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:18:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0018_negative_delta_rgb.png |
| `frame:18:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0018.png |
| `frame:18:scene_output:image` | `ok` | scene output path |
| `frame:18:scene_output:metadata` | `ok` | scene output path |
| `frame:18:scene_output:validation` | `ok` | scene output path |
| `frame:19:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0019.png |
| `frame:19:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0019_negative_delta_rgb.png |
| `frame:19:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0019_positive_delta_rgb.png |
| `frame:19:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0019.png |
| `frame:19:output:image` | `ok` | output path |
| `frame:19:output:metadata` | `ok` | output path |
| `frame:19:output:validation` | `ok` | output path |
| `frame:19:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0019_backend_scene.json |
| `frame:19:scene_schema` | `ok` | scene schema |
| `frame:19:scene_stage` | `ok` | scene stage |
| `frame:19:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:19:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0019.png |
| `frame:19:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:19:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0019_positive_delta_rgb.png |
| `frame:19:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:19:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0019_negative_delta_rgb.png |
| `frame:19:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0019.png |
| `frame:19:scene_output:image` | `ok` | scene output path |
| `frame:19:scene_output:metadata` | `ok` | scene output path |
| `frame:19:scene_output:validation` | `ok` | scene output path |
| `frame:20:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0020.png |
| `frame:20:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0020_negative_delta_rgb.png |
| `frame:20:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0020_positive_delta_rgb.png |
| `frame:20:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0020.png |
| `frame:20:output:image` | `ok` | output path |
| `frame:20:output:metadata` | `ok` | output path |
| `frame:20:output:validation` | `ok` | output path |
| `frame:20:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0020_backend_scene.json |
| `frame:20:scene_schema` | `ok` | scene schema |
| `frame:20:scene_stage` | `ok` | scene stage |
| `frame:20:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:20:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0020.png |
| `frame:20:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:20:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0020_positive_delta_rgb.png |
| `frame:20:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:20:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0020_negative_delta_rgb.png |
| `frame:20:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0020.png |
| `frame:20:scene_output:image` | `ok` | scene output path |
| `frame:20:scene_output:metadata` | `ok` | scene output path |
| `frame:20:scene_output:validation` | `ok` | scene output path |
| `frame:21:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0021.png |
| `frame:21:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0021_negative_delta_rgb.png |
| `frame:21:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0021_positive_delta_rgb.png |
| `frame:21:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0021.png |
| `frame:21:output:image` | `ok` | output path |
| `frame:21:output:metadata` | `ok` | output path |
| `frame:21:output:validation` | `ok` | output path |
| `frame:21:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0021_backend_scene.json |
| `frame:21:scene_schema` | `ok` | scene schema |
| `frame:21:scene_stage` | `ok` | scene stage |
| `frame:21:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:21:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0021.png |
| `frame:21:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:21:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0021_positive_delta_rgb.png |
| `frame:21:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:21:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0021_negative_delta_rgb.png |
| `frame:21:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0021.png |
| `frame:21:scene_output:image` | `ok` | scene output path |
| `frame:21:scene_output:metadata` | `ok` | scene output path |
| `frame:21:scene_output:validation` | `ok` | scene output path |
| `frame:22:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0022.png |
| `frame:22:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0022_negative_delta_rgb.png |
| `frame:22:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0022_positive_delta_rgb.png |
| `frame:22:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0022.png |
| `frame:22:output:image` | `ok` | output path |
| `frame:22:output:metadata` | `ok` | output path |
| `frame:22:output:validation` | `ok` | output path |
| `frame:22:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0022_backend_scene.json |
| `frame:22:scene_schema` | `ok` | scene schema |
| `frame:22:scene_stage` | `ok` | scene stage |
| `frame:22:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:22:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0022.png |
| `frame:22:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:22:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0022_positive_delta_rgb.png |
| `frame:22:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:22:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0022_negative_delta_rgb.png |
| `frame:22:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0022.png |
| `frame:22:scene_output:image` | `ok` | scene output path |
| `frame:22:scene_output:metadata` | `ok` | scene output path |
| `frame:22:scene_output:validation` | `ok` | scene output path |
| `frame:23:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0023.png |
| `frame:23:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0023_negative_delta_rgb.png |
| `frame:23:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0023_positive_delta_rgb.png |
| `frame:23:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0023.png |
| `frame:23:output:image` | `ok` | output path |
| `frame:23:output:metadata` | `ok` | output path |
| `frame:23:output:validation` | `ok` | output path |
| `frame:23:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0023_backend_scene.json |
| `frame:23:scene_schema` | `ok` | scene schema |
| `frame:23:scene_stage` | `ok` | scene stage |
| `frame:23:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:23:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0023.png |
| `frame:23:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:23:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0023_positive_delta_rgb.png |
| `frame:23:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:23:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0023_negative_delta_rgb.png |
| `frame:23:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0023.png |
| `frame:23:scene_output:image` | `ok` | scene output path |
| `frame:23:scene_output:metadata` | `ok` | scene output path |
| `frame:23:scene_output:validation` | `ok` | scene output path |
| `frame:24:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png |
| `frame:24:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0024_negative_delta_rgb.png |
| `frame:24:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0024_positive_delta_rgb.png |
| `frame:24:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0024.png |
| `frame:24:output:image` | `ok` | output path |
| `frame:24:output:metadata` | `ok` | output path |
| `frame:24:output:validation` | `ok` | output path |
| `frame:24:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0024_backend_scene.json |
| `frame:24:scene_schema` | `ok` | scene schema |
| `frame:24:scene_stage` | `ok` | scene stage |
| `frame:24:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:24:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png |
| `frame:24:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:24:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0024_positive_delta_rgb.png |
| `frame:24:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:24:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0024_negative_delta_rgb.png |
| `frame:24:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0024.png |
| `frame:24:scene_output:image` | `ok` | scene output path |
| `frame:24:scene_output:metadata` | `ok` | scene output path |
| `frame:24:scene_output:validation` | `ok` | scene output path |
| `frame:25:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0025.png |
| `frame:25:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0025_negative_delta_rgb.png |
| `frame:25:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0025_positive_delta_rgb.png |
| `frame:25:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0025.png |
| `frame:25:output:image` | `ok` | output path |
| `frame:25:output:metadata` | `ok` | output path |
| `frame:25:output:validation` | `ok` | output path |
| `frame:25:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0025_backend_scene.json |
| `frame:25:scene_schema` | `ok` | scene schema |
| `frame:25:scene_stage` | `ok` | scene stage |
| `frame:25:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:25:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0025.png |
| `frame:25:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:25:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0025_positive_delta_rgb.png |
| `frame:25:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:25:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0025_negative_delta_rgb.png |
| `frame:25:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0025.png |
| `frame:25:scene_output:image` | `ok` | scene output path |
| `frame:25:scene_output:metadata` | `ok` | scene output path |
| `frame:25:scene_output:validation` | `ok` | scene output path |
| `frame:26:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0026.png |
| `frame:26:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0026_negative_delta_rgb.png |
| `frame:26:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0026_positive_delta_rgb.png |
| `frame:26:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0026.png |
| `frame:26:output:image` | `ok` | output path |
| `frame:26:output:metadata` | `ok` | output path |
| `frame:26:output:validation` | `ok` | output path |
| `frame:26:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0026_backend_scene.json |
| `frame:26:scene_schema` | `ok` | scene schema |
| `frame:26:scene_stage` | `ok` | scene stage |
| `frame:26:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:26:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0026.png |
| `frame:26:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:26:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0026_positive_delta_rgb.png |
| `frame:26:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:26:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0026_negative_delta_rgb.png |
| `frame:26:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0026.png |
| `frame:26:scene_output:image` | `ok` | scene output path |
| `frame:26:scene_output:metadata` | `ok` | scene output path |
| `frame:26:scene_output:validation` | `ok` | scene output path |
| `frame:27:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0027.png |
| `frame:27:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0027_negative_delta_rgb.png |
| `frame:27:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0027_positive_delta_rgb.png |
| `frame:27:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0027.png |
| `frame:27:output:image` | `ok` | output path |
| `frame:27:output:metadata` | `ok` | output path |
| `frame:27:output:validation` | `ok` | output path |
| `frame:27:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0027_backend_scene.json |
| `frame:27:scene_schema` | `ok` | scene schema |
| `frame:27:scene_stage` | `ok` | scene stage |
| `frame:27:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:27:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0027.png |
| `frame:27:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:27:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0027_positive_delta_rgb.png |
| `frame:27:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:27:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0027_negative_delta_rgb.png |
| `frame:27:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0027.png |
| `frame:27:scene_output:image` | `ok` | scene output path |
| `frame:27:scene_output:metadata` | `ok` | scene output path |
| `frame:27:scene_output:validation` | `ok` | scene output path |
| `frame:28:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0028.png |
| `frame:28:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0028_negative_delta_rgb.png |
| `frame:28:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0028_positive_delta_rgb.png |
| `frame:28:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0028.png |
| `frame:28:output:image` | `ok` | output path |
| `frame:28:output:metadata` | `ok` | output path |
| `frame:28:output:validation` | `ok` | output path |
| `frame:28:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0028_backend_scene.json |
| `frame:28:scene_schema` | `ok` | scene schema |
| `frame:28:scene_stage` | `ok` | scene stage |
| `frame:28:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:28:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0028.png |
| `frame:28:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:28:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0028_positive_delta_rgb.png |
| `frame:28:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:28:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0028_negative_delta_rgb.png |
| `frame:28:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0028.png |
| `frame:28:scene_output:image` | `ok` | scene output path |
| `frame:28:scene_output:metadata` | `ok` | scene output path |
| `frame:28:scene_output:validation` | `ok` | scene output path |
| `frame:29:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0029.png |
| `frame:29:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0029_negative_delta_rgb.png |
| `frame:29:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0029_positive_delta_rgb.png |
| `frame:29:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0029.png |
| `frame:29:output:image` | `ok` | output path |
| `frame:29:output:metadata` | `ok` | output path |
| `frame:29:output:validation` | `ok` | output path |
| `frame:29:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0029_backend_scene.json |
| `frame:29:scene_schema` | `ok` | scene schema |
| `frame:29:scene_stage` | `ok` | scene stage |
| `frame:29:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:29:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0029.png |
| `frame:29:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:29:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0029_positive_delta_rgb.png |
| `frame:29:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:29:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0029_negative_delta_rgb.png |
| `frame:29:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0029.png |
| `frame:29:scene_output:image` | `ok` | scene output path |
| `frame:29:scene_output:metadata` | `ok` | scene output path |
| `frame:29:scene_output:validation` | `ok` | scene output path |
| `frame:30:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0030.png |
| `frame:30:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0030_negative_delta_rgb.png |
| `frame:30:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0030_positive_delta_rgb.png |
| `frame:30:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0030.png |
| `frame:30:output:image` | `ok` | output path |
| `frame:30:output:metadata` | `ok` | output path |
| `frame:30:output:validation` | `ok` | output path |
| `frame:30:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0030_backend_scene.json |
| `frame:30:scene_schema` | `ok` | scene schema |
| `frame:30:scene_stage` | `ok` | scene stage |
| `frame:30:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:30:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0030.png |
| `frame:30:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:30:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0030_positive_delta_rgb.png |
| `frame:30:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:30:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0030_negative_delta_rgb.png |
| `frame:30:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0030.png |
| `frame:30:scene_output:image` | `ok` | scene output path |
| `frame:30:scene_output:metadata` | `ok` | scene output path |
| `frame:30:scene_output:validation` | `ok` | scene output path |
| `frame:31:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0031.png |
| `frame:31:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0031_negative_delta_rgb.png |
| `frame:31:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0031_positive_delta_rgb.png |
| `frame:31:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0031.png |
| `frame:31:output:image` | `ok` | output path |
| `frame:31:output:metadata` | `ok` | output path |
| `frame:31:output:validation` | `ok` | output path |
| `frame:31:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0031_backend_scene.json |
| `frame:31:scene_schema` | `ok` | scene schema |
| `frame:31:scene_stage` | `ok` | scene stage |
| `frame:31:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:31:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0031.png |
| `frame:31:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:31:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0031_positive_delta_rgb.png |
| `frame:31:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:31:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0031_negative_delta_rgb.png |
| `frame:31:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0031.png |
| `frame:31:scene_output:image` | `ok` | scene output path |
| `frame:31:scene_output:metadata` | `ok` | scene output path |
| `frame:31:scene_output:validation` | `ok` | scene output path |
| `frame:32:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0032.png |
| `frame:32:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0032_negative_delta_rgb.png |
| `frame:32:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0032_positive_delta_rgb.png |
| `frame:32:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0032.png |
| `frame:32:output:image` | `ok` | output path |
| `frame:32:output:metadata` | `ok` | output path |
| `frame:32:output:validation` | `ok` | output path |
| `frame:32:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0032_backend_scene.json |
| `frame:32:scene_schema` | `ok` | scene schema |
| `frame:32:scene_stage` | `ok` | scene stage |
| `frame:32:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:32:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0032.png |
| `frame:32:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:32:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0032_positive_delta_rgb.png |
| `frame:32:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:32:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0032_negative_delta_rgb.png |
| `frame:32:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0032.png |
| `frame:32:scene_output:image` | `ok` | scene output path |
| `frame:32:scene_output:metadata` | `ok` | scene output path |
| `frame:32:scene_output:validation` | `ok` | scene output path |
| `frame:33:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0033.png |
| `frame:33:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0033_negative_delta_rgb.png |
| `frame:33:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0033_positive_delta_rgb.png |
| `frame:33:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0033.png |
| `frame:33:output:image` | `ok` | output path |
| `frame:33:output:metadata` | `ok` | output path |
| `frame:33:output:validation` | `ok` | output path |
| `frame:33:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0033_backend_scene.json |
| `frame:33:scene_schema` | `ok` | scene schema |
| `frame:33:scene_stage` | `ok` | scene stage |
| `frame:33:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:33:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0033.png |
| `frame:33:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:33:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0033_positive_delta_rgb.png |
| `frame:33:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:33:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0033_negative_delta_rgb.png |
| `frame:33:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0033.png |
| `frame:33:scene_output:image` | `ok` | scene output path |
| `frame:33:scene_output:metadata` | `ok` | scene output path |
| `frame:33:scene_output:validation` | `ok` | scene output path |
| `frame:34:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0034.png |
| `frame:34:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0034_negative_delta_rgb.png |
| `frame:34:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0034_positive_delta_rgb.png |
| `frame:34:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0034.png |
| `frame:34:output:image` | `ok` | output path |
| `frame:34:output:metadata` | `ok` | output path |
| `frame:34:output:validation` | `ok` | output path |
| `frame:34:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0034_backend_scene.json |
| `frame:34:scene_schema` | `ok` | scene schema |
| `frame:34:scene_stage` | `ok` | scene stage |
| `frame:34:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:34:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0034.png |
| `frame:34:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:34:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0034_positive_delta_rgb.png |
| `frame:34:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:34:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0034_negative_delta_rgb.png |
| `frame:34:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0034.png |
| `frame:34:scene_output:image` | `ok` | scene output path |
| `frame:34:scene_output:metadata` | `ok` | scene output path |
| `frame:34:scene_output:validation` | `ok` | scene output path |
| `frame:35:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0035.png |
| `frame:35:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0035_negative_delta_rgb.png |
| `frame:35:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0035_positive_delta_rgb.png |
| `frame:35:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0035.png |
| `frame:35:output:image` | `ok` | output path |
| `frame:35:output:metadata` | `ok` | output path |
| `frame:35:output:validation` | `ok` | output path |
| `frame:35:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0035_backend_scene.json |
| `frame:35:scene_schema` | `ok` | scene schema |
| `frame:35:scene_stage` | `ok` | scene stage |
| `frame:35:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:35:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0035.png |
| `frame:35:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:35:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0035_positive_delta_rgb.png |
| `frame:35:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:35:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0035_negative_delta_rgb.png |
| `frame:35:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0035.png |
| `frame:35:scene_output:image` | `ok` | scene output path |
| `frame:35:scene_output:metadata` | `ok` | scene output path |
| `frame:35:scene_output:validation` | `ok` | scene output path |
| `frame:36:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0036.png |
| `frame:36:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0036_negative_delta_rgb.png |
| `frame:36:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0036_positive_delta_rgb.png |
| `frame:36:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0036.png |
| `frame:36:output:image` | `ok` | output path |
| `frame:36:output:metadata` | `ok` | output path |
| `frame:36:output:validation` | `ok` | output path |
| `frame:36:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0036_backend_scene.json |
| `frame:36:scene_schema` | `ok` | scene schema |
| `frame:36:scene_stage` | `ok` | scene stage |
| `frame:36:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:36:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0036.png |
| `frame:36:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:36:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0036_positive_delta_rgb.png |
| `frame:36:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:36:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0036_negative_delta_rgb.png |
| `frame:36:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0036.png |
| `frame:36:scene_output:image` | `ok` | scene output path |
| `frame:36:scene_output:metadata` | `ok` | scene output path |
| `frame:36:scene_output:validation` | `ok` | scene output path |
| `frame:37:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0037.png |
| `frame:37:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0037_negative_delta_rgb.png |
| `frame:37:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0037_positive_delta_rgb.png |
| `frame:37:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0037.png |
| `frame:37:output:image` | `ok` | output path |
| `frame:37:output:metadata` | `ok` | output path |
| `frame:37:output:validation` | `ok` | output path |
| `frame:37:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0037_backend_scene.json |
| `frame:37:scene_schema` | `ok` | scene schema |
| `frame:37:scene_stage` | `ok` | scene stage |
| `frame:37:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:37:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0037.png |
| `frame:37:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:37:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0037_positive_delta_rgb.png |
| `frame:37:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:37:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0037_negative_delta_rgb.png |
| `frame:37:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0037.png |
| `frame:37:scene_output:image` | `ok` | scene output path |
| `frame:37:scene_output:metadata` | `ok` | scene output path |
| `frame:37:scene_output:validation` | `ok` | scene output path |
| `frame:38:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0038.png |
| `frame:38:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0038_negative_delta_rgb.png |
| `frame:38:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0038_positive_delta_rgb.png |
| `frame:38:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0038.png |
| `frame:38:output:image` | `ok` | output path |
| `frame:38:output:metadata` | `ok` | output path |
| `frame:38:output:validation` | `ok` | output path |
| `frame:38:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0038_backend_scene.json |
| `frame:38:scene_schema` | `ok` | scene schema |
| `frame:38:scene_stage` | `ok` | scene stage |
| `frame:38:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:38:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0038.png |
| `frame:38:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:38:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0038_positive_delta_rgb.png |
| `frame:38:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:38:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0038_negative_delta_rgb.png |
| `frame:38:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0038.png |
| `frame:38:scene_output:image` | `ok` | scene output path |
| `frame:38:scene_output:metadata` | `ok` | scene output path |
| `frame:38:scene_output:validation` | `ok` | scene output path |
| `frame:39:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0039.png |
| `frame:39:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0039_negative_delta_rgb.png |
| `frame:39:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0039_positive_delta_rgb.png |
| `frame:39:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0039.png |
| `frame:39:output:image` | `ok` | output path |
| `frame:39:output:metadata` | `ok` | output path |
| `frame:39:output:validation` | `ok` | output path |
| `frame:39:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0039_backend_scene.json |
| `frame:39:scene_schema` | `ok` | scene schema |
| `frame:39:scene_stage` | `ok` | scene stage |
| `frame:39:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:39:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0039.png |
| `frame:39:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:39:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0039_positive_delta_rgb.png |
| `frame:39:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:39:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0039_negative_delta_rgb.png |
| `frame:39:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0039.png |
| `frame:39:scene_output:image` | `ok` | scene output path |
| `frame:39:scene_output:metadata` | `ok` | scene output path |
| `frame:39:scene_output:validation` | `ok` | scene output path |
| `frame:40:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0040.png |
| `frame:40:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0040_negative_delta_rgb.png |
| `frame:40:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0040_positive_delta_rgb.png |
| `frame:40:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0040.png |
| `frame:40:output:image` | `ok` | output path |
| `frame:40:output:metadata` | `ok` | output path |
| `frame:40:output:validation` | `ok` | output path |
| `frame:40:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0040_backend_scene.json |
| `frame:40:scene_schema` | `ok` | scene schema |
| `frame:40:scene_stage` | `ok` | scene stage |
| `frame:40:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:40:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0040.png |
| `frame:40:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:40:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0040_positive_delta_rgb.png |
| `frame:40:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:40:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0040_negative_delta_rgb.png |
| `frame:40:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0040.png |
| `frame:40:scene_output:image` | `ok` | scene output path |
| `frame:40:scene_output:metadata` | `ok` | scene output path |
| `frame:40:scene_output:validation` | `ok` | scene output path |
| `frame:41:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0041.png |
| `frame:41:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0041_negative_delta_rgb.png |
| `frame:41:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0041_positive_delta_rgb.png |
| `frame:41:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0041.png |
| `frame:41:output:image` | `ok` | output path |
| `frame:41:output:metadata` | `ok` | output path |
| `frame:41:output:validation` | `ok` | output path |
| `frame:41:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0041_backend_scene.json |
| `frame:41:scene_schema` | `ok` | scene schema |
| `frame:41:scene_stage` | `ok` | scene stage |
| `frame:41:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:41:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0041.png |
| `frame:41:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:41:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0041_positive_delta_rgb.png |
| `frame:41:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:41:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0041_negative_delta_rgb.png |
| `frame:41:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0041.png |
| `frame:41:scene_output:image` | `ok` | scene output path |
| `frame:41:scene_output:metadata` | `ok` | scene output path |
| `frame:41:scene_output:validation` | `ok` | scene output path |
| `frame:42:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0042.png |
| `frame:42:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0042_negative_delta_rgb.png |
| `frame:42:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0042_positive_delta_rgb.png |
| `frame:42:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0042.png |
| `frame:42:output:image` | `ok` | output path |
| `frame:42:output:metadata` | `ok` | output path |
| `frame:42:output:validation` | `ok` | output path |
| `frame:42:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0042_backend_scene.json |
| `frame:42:scene_schema` | `ok` | scene schema |
| `frame:42:scene_stage` | `ok` | scene stage |
| `frame:42:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:42:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0042.png |
| `frame:42:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:42:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0042_positive_delta_rgb.png |
| `frame:42:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:42:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0042_negative_delta_rgb.png |
| `frame:42:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0042.png |
| `frame:42:scene_output:image` | `ok` | scene output path |
| `frame:42:scene_output:metadata` | `ok` | scene output path |
| `frame:42:scene_output:validation` | `ok` | scene output path |
| `frame:43:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0043.png |
| `frame:43:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0043_negative_delta_rgb.png |
| `frame:43:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0043_positive_delta_rgb.png |
| `frame:43:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0043.png |
| `frame:43:output:image` | `ok` | output path |
| `frame:43:output:metadata` | `ok` | output path |
| `frame:43:output:validation` | `ok` | output path |
| `frame:43:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0043_backend_scene.json |
| `frame:43:scene_schema` | `ok` | scene schema |
| `frame:43:scene_stage` | `ok` | scene stage |
| `frame:43:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:43:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0043.png |
| `frame:43:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:43:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0043_positive_delta_rgb.png |
| `frame:43:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:43:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0043_negative_delta_rgb.png |
| `frame:43:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0043.png |
| `frame:43:scene_output:image` | `ok` | scene output path |
| `frame:43:scene_output:metadata` | `ok` | scene output path |
| `frame:43:scene_output:validation` | `ok` | scene output path |
| `frame:44:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0044.png |
| `frame:44:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0044_negative_delta_rgb.png |
| `frame:44:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0044_positive_delta_rgb.png |
| `frame:44:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0044.png |
| `frame:44:output:image` | `ok` | output path |
| `frame:44:output:metadata` | `ok` | output path |
| `frame:44:output:validation` | `ok` | output path |
| `frame:44:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0044_backend_scene.json |
| `frame:44:scene_schema` | `ok` | scene schema |
| `frame:44:scene_stage` | `ok` | scene stage |
| `frame:44:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:44:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0044.png |
| `frame:44:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:44:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0044_positive_delta_rgb.png |
| `frame:44:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:44:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0044_negative_delta_rgb.png |
| `frame:44:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0044.png |
| `frame:44:scene_output:image` | `ok` | scene output path |
| `frame:44:scene_output:metadata` | `ok` | scene output path |
| `frame:44:scene_output:validation` | `ok` | scene output path |
| `frame:45:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0045.png |
| `frame:45:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0045_negative_delta_rgb.png |
| `frame:45:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0045_positive_delta_rgb.png |
| `frame:45:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0045.png |
| `frame:45:output:image` | `ok` | output path |
| `frame:45:output:metadata` | `ok` | output path |
| `frame:45:output:validation` | `ok` | output path |
| `frame:45:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0045_backend_scene.json |
| `frame:45:scene_schema` | `ok` | scene schema |
| `frame:45:scene_stage` | `ok` | scene stage |
| `frame:45:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:45:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0045.png |
| `frame:45:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:45:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0045_positive_delta_rgb.png |
| `frame:45:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:45:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0045_negative_delta_rgb.png |
| `frame:45:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0045.png |
| `frame:45:scene_output:image` | `ok` | scene output path |
| `frame:45:scene_output:metadata` | `ok` | scene output path |
| `frame:45:scene_output:validation` | `ok` | scene output path |
| `frame:46:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0046.png |
| `frame:46:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0046_negative_delta_rgb.png |
| `frame:46:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0046_positive_delta_rgb.png |
| `frame:46:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0046.png |
| `frame:46:output:image` | `ok` | output path |
| `frame:46:output:metadata` | `ok` | output path |
| `frame:46:output:validation` | `ok` | output path |
| `frame:46:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0046_backend_scene.json |
| `frame:46:scene_schema` | `ok` | scene schema |
| `frame:46:scene_stage` | `ok` | scene stage |
| `frame:46:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:46:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0046.png |
| `frame:46:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:46:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0046_positive_delta_rgb.png |
| `frame:46:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:46:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0046_negative_delta_rgb.png |
| `frame:46:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0046.png |
| `frame:46:scene_output:image` | `ok` | scene output path |
| `frame:46:scene_output:metadata` | `ok` | scene output path |
| `frame:46:scene_output:validation` | `ok` | scene output path |
| `frame:47:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png |
| `frame:47:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0047_negative_delta_rgb.png |
| `frame:47:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0047_positive_delta_rgb.png |
| `frame:47:reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0047.png |
| `frame:47:output:image` | `ok` | output path |
| `frame:47:output:metadata` | `ok` | output path |
| `frame:47:output:validation` | `ok` | output path |
| `frame:47:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0047_backend_scene.json |
| `frame:47:scene_schema` | `ok` | scene schema |
| `frame:47:scene_stage` | `ok` | scene stage |
| `frame:47:scene_input_present:base_rgb` | `ok` | scene input present |
| `frame:47:scene_input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png |
| `frame:47:scene_input_present:positive_delta_rgb` | `ok` | scene input present |
| `frame:47:scene_input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0047_positive_delta_rgb.png |
| `frame:47:scene_input_present:negative_delta_rgb` | `ok` | scene input present |
| `frame:47:scene_input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0047_negative_delta_rgb.png |
| `frame:47:scene_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0047.png |
| `frame:47:scene_output:image` | `ok` | scene output path |
| `frame:47:scene_output:metadata` | `ok` | scene output path |
| `frame:47:scene_output:validation` | `ok` | scene output path |
