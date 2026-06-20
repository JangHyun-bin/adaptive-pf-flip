# S558 Mitsuba S515 Full48 T4 Renderer Job Manifest Validation

Generated UTC: `2026-06-20T20:58:55.072059+00:00`
Validation JSON: `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/renderer_job_manifest_validation.json`
Status: `passed`
Job: `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/renderer_job_manifest.json`

## Summary

- Total checks: `606`
- Failed checks: `0`
- Skipped checks: `0`
- Public URL: `https://operating-intended-analyses-individually.trycloudflare.com`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `job:schema` | `ok` | schema |
| `job:version` | `ok` | version |
| `source:acceptance_package` | `ok` | build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/renderer_acceptance_package.json |
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
| `contract:shader:glsl` | `ok` | build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/shaders/low_frequency_parity_post_tonemap.glsl |
| `contract:shader:hlsl` | `ok` | build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/shaders/low_frequency_parity_post_tonemap.hlsl |
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
| `frame:0:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png |
| `frame:0:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:0:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:0:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0000.png |
| `frame:0:output_target:image` | `ok` | output target under output_root |
| `frame:0:output_target:metadata` | `ok` | output target under output_root |
| `frame:0:output_target:validation` | `ok` | output target under output_root |
| `frame:0:oracle_abs` | `ok` | oracle threshold |
| `frame:0:webgl_abs` | `ok` | WebGL threshold |
| `frame:1:input_present:base_rgb` | `ok` | required input in job |
| `frame:1:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0001.png |
| `frame:1:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:1:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:1:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0001.png |
| `frame:1:output_target:image` | `ok` | output target under output_root |
| `frame:1:output_target:metadata` | `ok` | output target under output_root |
| `frame:1:output_target:validation` | `ok` | output target under output_root |
| `frame:1:oracle_abs` | `ok` | oracle threshold |
| `frame:1:webgl_abs` | `ok` | WebGL threshold |
| `frame:2:input_present:base_rgb` | `ok` | required input in job |
| `frame:2:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0002.png |
| `frame:2:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:2:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:2:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0002.png |
| `frame:2:output_target:image` | `ok` | output target under output_root |
| `frame:2:output_target:metadata` | `ok` | output target under output_root |
| `frame:2:output_target:validation` | `ok` | output target under output_root |
| `frame:2:oracle_abs` | `ok` | oracle threshold |
| `frame:2:webgl_abs` | `ok` | WebGL threshold |
| `frame:3:input_present:base_rgb` | `ok` | required input in job |
| `frame:3:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0003.png |
| `frame:3:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:3:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:3:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0003.png |
| `frame:3:output_target:image` | `ok` | output target under output_root |
| `frame:3:output_target:metadata` | `ok` | output target under output_root |
| `frame:3:output_target:validation` | `ok` | output target under output_root |
| `frame:3:oracle_abs` | `ok` | oracle threshold |
| `frame:3:webgl_abs` | `ok` | WebGL threshold |
| `frame:4:input_present:base_rgb` | `ok` | required input in job |
| `frame:4:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0004.png |
| `frame:4:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:4:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:4:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0004.png |
| `frame:4:output_target:image` | `ok` | output target under output_root |
| `frame:4:output_target:metadata` | `ok` | output target under output_root |
| `frame:4:output_target:validation` | `ok` | output target under output_root |
| `frame:4:oracle_abs` | `ok` | oracle threshold |
| `frame:4:webgl_abs` | `ok` | WebGL threshold |
| `frame:5:input_present:base_rgb` | `ok` | required input in job |
| `frame:5:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0005.png |
| `frame:5:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:5:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:5:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0005.png |
| `frame:5:output_target:image` | `ok` | output target under output_root |
| `frame:5:output_target:metadata` | `ok` | output target under output_root |
| `frame:5:output_target:validation` | `ok` | output target under output_root |
| `frame:5:oracle_abs` | `ok` | oracle threshold |
| `frame:5:webgl_abs` | `ok` | WebGL threshold |
| `frame:6:input_present:base_rgb` | `ok` | required input in job |
| `frame:6:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0006.png |
| `frame:6:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:6:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:6:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0006.png |
| `frame:6:output_target:image` | `ok` | output target under output_root |
| `frame:6:output_target:metadata` | `ok` | output target under output_root |
| `frame:6:output_target:validation` | `ok` | output target under output_root |
| `frame:6:oracle_abs` | `ok` | oracle threshold |
| `frame:6:webgl_abs` | `ok` | WebGL threshold |
| `frame:7:input_present:base_rgb` | `ok` | required input in job |
| `frame:7:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0007.png |
| `frame:7:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:7:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:7:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0007.png |
| `frame:7:output_target:image` | `ok` | output target under output_root |
| `frame:7:output_target:metadata` | `ok` | output target under output_root |
| `frame:7:output_target:validation` | `ok` | output target under output_root |
| `frame:7:oracle_abs` | `ok` | oracle threshold |
| `frame:7:webgl_abs` | `ok` | WebGL threshold |
| `frame:8:input_present:base_rgb` | `ok` | required input in job |
| `frame:8:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0008.png |
| `frame:8:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:8:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0008_positive_delta_rgb.png |
| `frame:8:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:8:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0008_negative_delta_rgb.png |
| `frame:8:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0008.png |
| `frame:8:output_target:image` | `ok` | output target under output_root |
| `frame:8:output_target:metadata` | `ok` | output target under output_root |
| `frame:8:output_target:validation` | `ok` | output target under output_root |
| `frame:8:oracle_abs` | `ok` | oracle threshold |
| `frame:8:webgl_abs` | `ok` | WebGL threshold |
| `frame:9:input_present:base_rgb` | `ok` | required input in job |
| `frame:9:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0009.png |
| `frame:9:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:9:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0009_positive_delta_rgb.png |
| `frame:9:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:9:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0009_negative_delta_rgb.png |
| `frame:9:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0009.png |
| `frame:9:output_target:image` | `ok` | output target under output_root |
| `frame:9:output_target:metadata` | `ok` | output target under output_root |
| `frame:9:output_target:validation` | `ok` | output target under output_root |
| `frame:9:oracle_abs` | `ok` | oracle threshold |
| `frame:9:webgl_abs` | `ok` | WebGL threshold |
| `frame:10:input_present:base_rgb` | `ok` | required input in job |
| `frame:10:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0010.png |
| `frame:10:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:10:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0010_positive_delta_rgb.png |
| `frame:10:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:10:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0010_negative_delta_rgb.png |
| `frame:10:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0010.png |
| `frame:10:output_target:image` | `ok` | output target under output_root |
| `frame:10:output_target:metadata` | `ok` | output target under output_root |
| `frame:10:output_target:validation` | `ok` | output target under output_root |
| `frame:10:oracle_abs` | `ok` | oracle threshold |
| `frame:10:webgl_abs` | `ok` | WebGL threshold |
| `frame:11:input_present:base_rgb` | `ok` | required input in job |
| `frame:11:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0011.png |
| `frame:11:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:11:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0011_positive_delta_rgb.png |
| `frame:11:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:11:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0011_negative_delta_rgb.png |
| `frame:11:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0011.png |
| `frame:11:output_target:image` | `ok` | output target under output_root |
| `frame:11:output_target:metadata` | `ok` | output target under output_root |
| `frame:11:output_target:validation` | `ok` | output target under output_root |
| `frame:11:oracle_abs` | `ok` | oracle threshold |
| `frame:11:webgl_abs` | `ok` | WebGL threshold |
| `frame:12:input_present:base_rgb` | `ok` | required input in job |
| `frame:12:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0012.png |
| `frame:12:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:12:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0012_positive_delta_rgb.png |
| `frame:12:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:12:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0012_negative_delta_rgb.png |
| `frame:12:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0012.png |
| `frame:12:output_target:image` | `ok` | output target under output_root |
| `frame:12:output_target:metadata` | `ok` | output target under output_root |
| `frame:12:output_target:validation` | `ok` | output target under output_root |
| `frame:12:oracle_abs` | `ok` | oracle threshold |
| `frame:12:webgl_abs` | `ok` | WebGL threshold |
| `frame:13:input_present:base_rgb` | `ok` | required input in job |
| `frame:13:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0013.png |
| `frame:13:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:13:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0013_positive_delta_rgb.png |
| `frame:13:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:13:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0013_negative_delta_rgb.png |
| `frame:13:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0013.png |
| `frame:13:output_target:image` | `ok` | output target under output_root |
| `frame:13:output_target:metadata` | `ok` | output target under output_root |
| `frame:13:output_target:validation` | `ok` | output target under output_root |
| `frame:13:oracle_abs` | `ok` | oracle threshold |
| `frame:13:webgl_abs` | `ok` | WebGL threshold |
| `frame:14:input_present:base_rgb` | `ok` | required input in job |
| `frame:14:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0014.png |
| `frame:14:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:14:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0014_positive_delta_rgb.png |
| `frame:14:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:14:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0014_negative_delta_rgb.png |
| `frame:14:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0014.png |
| `frame:14:output_target:image` | `ok` | output target under output_root |
| `frame:14:output_target:metadata` | `ok` | output target under output_root |
| `frame:14:output_target:validation` | `ok` | output target under output_root |
| `frame:14:oracle_abs` | `ok` | oracle threshold |
| `frame:14:webgl_abs` | `ok` | WebGL threshold |
| `frame:15:input_present:base_rgb` | `ok` | required input in job |
| `frame:15:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0015.png |
| `frame:15:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:15:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0015_positive_delta_rgb.png |
| `frame:15:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:15:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0015_negative_delta_rgb.png |
| `frame:15:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0015.png |
| `frame:15:output_target:image` | `ok` | output target under output_root |
| `frame:15:output_target:metadata` | `ok` | output target under output_root |
| `frame:15:output_target:validation` | `ok` | output target under output_root |
| `frame:15:oracle_abs` | `ok` | oracle threshold |
| `frame:15:webgl_abs` | `ok` | WebGL threshold |
| `frame:16:input_present:base_rgb` | `ok` | required input in job |
| `frame:16:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0016.png |
| `frame:16:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:16:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0016_positive_delta_rgb.png |
| `frame:16:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:16:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0016_negative_delta_rgb.png |
| `frame:16:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0016.png |
| `frame:16:output_target:image` | `ok` | output target under output_root |
| `frame:16:output_target:metadata` | `ok` | output target under output_root |
| `frame:16:output_target:validation` | `ok` | output target under output_root |
| `frame:16:oracle_abs` | `ok` | oracle threshold |
| `frame:16:webgl_abs` | `ok` | WebGL threshold |
| `frame:17:input_present:base_rgb` | `ok` | required input in job |
| `frame:17:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0017.png |
| `frame:17:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:17:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0017_positive_delta_rgb.png |
| `frame:17:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:17:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0017_negative_delta_rgb.png |
| `frame:17:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0017.png |
| `frame:17:output_target:image` | `ok` | output target under output_root |
| `frame:17:output_target:metadata` | `ok` | output target under output_root |
| `frame:17:output_target:validation` | `ok` | output target under output_root |
| `frame:17:oracle_abs` | `ok` | oracle threshold |
| `frame:17:webgl_abs` | `ok` | WebGL threshold |
| `frame:18:input_present:base_rgb` | `ok` | required input in job |
| `frame:18:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0018.png |
| `frame:18:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:18:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0018_positive_delta_rgb.png |
| `frame:18:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:18:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0018_negative_delta_rgb.png |
| `frame:18:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0018.png |
| `frame:18:output_target:image` | `ok` | output target under output_root |
| `frame:18:output_target:metadata` | `ok` | output target under output_root |
| `frame:18:output_target:validation` | `ok` | output target under output_root |
| `frame:18:oracle_abs` | `ok` | oracle threshold |
| `frame:18:webgl_abs` | `ok` | WebGL threshold |
| `frame:19:input_present:base_rgb` | `ok` | required input in job |
| `frame:19:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0019.png |
| `frame:19:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:19:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0019_positive_delta_rgb.png |
| `frame:19:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:19:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0019_negative_delta_rgb.png |
| `frame:19:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0019.png |
| `frame:19:output_target:image` | `ok` | output target under output_root |
| `frame:19:output_target:metadata` | `ok` | output target under output_root |
| `frame:19:output_target:validation` | `ok` | output target under output_root |
| `frame:19:oracle_abs` | `ok` | oracle threshold |
| `frame:19:webgl_abs` | `ok` | WebGL threshold |
| `frame:20:input_present:base_rgb` | `ok` | required input in job |
| `frame:20:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0020.png |
| `frame:20:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:20:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0020_positive_delta_rgb.png |
| `frame:20:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:20:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0020_negative_delta_rgb.png |
| `frame:20:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0020.png |
| `frame:20:output_target:image` | `ok` | output target under output_root |
| `frame:20:output_target:metadata` | `ok` | output target under output_root |
| `frame:20:output_target:validation` | `ok` | output target under output_root |
| `frame:20:oracle_abs` | `ok` | oracle threshold |
| `frame:20:webgl_abs` | `ok` | WebGL threshold |
| `frame:21:input_present:base_rgb` | `ok` | required input in job |
| `frame:21:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0021.png |
| `frame:21:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:21:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0021_positive_delta_rgb.png |
| `frame:21:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:21:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0021_negative_delta_rgb.png |
| `frame:21:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0021.png |
| `frame:21:output_target:image` | `ok` | output target under output_root |
| `frame:21:output_target:metadata` | `ok` | output target under output_root |
| `frame:21:output_target:validation` | `ok` | output target under output_root |
| `frame:21:oracle_abs` | `ok` | oracle threshold |
| `frame:21:webgl_abs` | `ok` | WebGL threshold |
| `frame:22:input_present:base_rgb` | `ok` | required input in job |
| `frame:22:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0022.png |
| `frame:22:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:22:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0022_positive_delta_rgb.png |
| `frame:22:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:22:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0022_negative_delta_rgb.png |
| `frame:22:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0022.png |
| `frame:22:output_target:image` | `ok` | output target under output_root |
| `frame:22:output_target:metadata` | `ok` | output target under output_root |
| `frame:22:output_target:validation` | `ok` | output target under output_root |
| `frame:22:oracle_abs` | `ok` | oracle threshold |
| `frame:22:webgl_abs` | `ok` | WebGL threshold |
| `frame:23:input_present:base_rgb` | `ok` | required input in job |
| `frame:23:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0023.png |
| `frame:23:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:23:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0023_positive_delta_rgb.png |
| `frame:23:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:23:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0023_negative_delta_rgb.png |
| `frame:23:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0023.png |
| `frame:23:output_target:image` | `ok` | output target under output_root |
| `frame:23:output_target:metadata` | `ok` | output target under output_root |
| `frame:23:output_target:validation` | `ok` | output target under output_root |
| `frame:23:oracle_abs` | `ok` | oracle threshold |
| `frame:23:webgl_abs` | `ok` | WebGL threshold |
| `frame:24:input_present:base_rgb` | `ok` | required input in job |
| `frame:24:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png |
| `frame:24:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:24:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0024_positive_delta_rgb.png |
| `frame:24:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:24:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0024_negative_delta_rgb.png |
| `frame:24:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0024.png |
| `frame:24:output_target:image` | `ok` | output target under output_root |
| `frame:24:output_target:metadata` | `ok` | output target under output_root |
| `frame:24:output_target:validation` | `ok` | output target under output_root |
| `frame:24:oracle_abs` | `ok` | oracle threshold |
| `frame:24:webgl_abs` | `ok` | WebGL threshold |
| `frame:25:input_present:base_rgb` | `ok` | required input in job |
| `frame:25:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0025.png |
| `frame:25:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:25:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0025_positive_delta_rgb.png |
| `frame:25:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:25:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0025_negative_delta_rgb.png |
| `frame:25:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0025.png |
| `frame:25:output_target:image` | `ok` | output target under output_root |
| `frame:25:output_target:metadata` | `ok` | output target under output_root |
| `frame:25:output_target:validation` | `ok` | output target under output_root |
| `frame:25:oracle_abs` | `ok` | oracle threshold |
| `frame:25:webgl_abs` | `ok` | WebGL threshold |
| `frame:26:input_present:base_rgb` | `ok` | required input in job |
| `frame:26:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0026.png |
| `frame:26:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:26:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0026_positive_delta_rgb.png |
| `frame:26:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:26:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0026_negative_delta_rgb.png |
| `frame:26:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0026.png |
| `frame:26:output_target:image` | `ok` | output target under output_root |
| `frame:26:output_target:metadata` | `ok` | output target under output_root |
| `frame:26:output_target:validation` | `ok` | output target under output_root |
| `frame:26:oracle_abs` | `ok` | oracle threshold |
| `frame:26:webgl_abs` | `ok` | WebGL threshold |
| `frame:27:input_present:base_rgb` | `ok` | required input in job |
| `frame:27:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0027.png |
| `frame:27:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:27:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0027_positive_delta_rgb.png |
| `frame:27:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:27:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0027_negative_delta_rgb.png |
| `frame:27:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0027.png |
| `frame:27:output_target:image` | `ok` | output target under output_root |
| `frame:27:output_target:metadata` | `ok` | output target under output_root |
| `frame:27:output_target:validation` | `ok` | output target under output_root |
| `frame:27:oracle_abs` | `ok` | oracle threshold |
| `frame:27:webgl_abs` | `ok` | WebGL threshold |
| `frame:28:input_present:base_rgb` | `ok` | required input in job |
| `frame:28:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0028.png |
| `frame:28:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:28:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0028_positive_delta_rgb.png |
| `frame:28:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:28:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0028_negative_delta_rgb.png |
| `frame:28:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0028.png |
| `frame:28:output_target:image` | `ok` | output target under output_root |
| `frame:28:output_target:metadata` | `ok` | output target under output_root |
| `frame:28:output_target:validation` | `ok` | output target under output_root |
| `frame:28:oracle_abs` | `ok` | oracle threshold |
| `frame:28:webgl_abs` | `ok` | WebGL threshold |
| `frame:29:input_present:base_rgb` | `ok` | required input in job |
| `frame:29:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0029.png |
| `frame:29:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:29:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0029_positive_delta_rgb.png |
| `frame:29:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:29:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0029_negative_delta_rgb.png |
| `frame:29:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0029.png |
| `frame:29:output_target:image` | `ok` | output target under output_root |
| `frame:29:output_target:metadata` | `ok` | output target under output_root |
| `frame:29:output_target:validation` | `ok` | output target under output_root |
| `frame:29:oracle_abs` | `ok` | oracle threshold |
| `frame:29:webgl_abs` | `ok` | WebGL threshold |
| `frame:30:input_present:base_rgb` | `ok` | required input in job |
| `frame:30:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0030.png |
| `frame:30:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:30:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0030_positive_delta_rgb.png |
| `frame:30:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:30:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0030_negative_delta_rgb.png |
| `frame:30:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0030.png |
| `frame:30:output_target:image` | `ok` | output target under output_root |
| `frame:30:output_target:metadata` | `ok` | output target under output_root |
| `frame:30:output_target:validation` | `ok` | output target under output_root |
| `frame:30:oracle_abs` | `ok` | oracle threshold |
| `frame:30:webgl_abs` | `ok` | WebGL threshold |
| `frame:31:input_present:base_rgb` | `ok` | required input in job |
| `frame:31:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0031.png |
| `frame:31:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:31:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0031_positive_delta_rgb.png |
| `frame:31:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:31:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0031_negative_delta_rgb.png |
| `frame:31:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0031.png |
| `frame:31:output_target:image` | `ok` | output target under output_root |
| `frame:31:output_target:metadata` | `ok` | output target under output_root |
| `frame:31:output_target:validation` | `ok` | output target under output_root |
| `frame:31:oracle_abs` | `ok` | oracle threshold |
| `frame:31:webgl_abs` | `ok` | WebGL threshold |
| `frame:32:input_present:base_rgb` | `ok` | required input in job |
| `frame:32:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0032.png |
| `frame:32:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:32:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0032_positive_delta_rgb.png |
| `frame:32:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:32:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0032_negative_delta_rgb.png |
| `frame:32:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0032.png |
| `frame:32:output_target:image` | `ok` | output target under output_root |
| `frame:32:output_target:metadata` | `ok` | output target under output_root |
| `frame:32:output_target:validation` | `ok` | output target under output_root |
| `frame:32:oracle_abs` | `ok` | oracle threshold |
| `frame:32:webgl_abs` | `ok` | WebGL threshold |
| `frame:33:input_present:base_rgb` | `ok` | required input in job |
| `frame:33:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0033.png |
| `frame:33:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:33:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0033_positive_delta_rgb.png |
| `frame:33:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:33:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0033_negative_delta_rgb.png |
| `frame:33:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0033.png |
| `frame:33:output_target:image` | `ok` | output target under output_root |
| `frame:33:output_target:metadata` | `ok` | output target under output_root |
| `frame:33:output_target:validation` | `ok` | output target under output_root |
| `frame:33:oracle_abs` | `ok` | oracle threshold |
| `frame:33:webgl_abs` | `ok` | WebGL threshold |
| `frame:34:input_present:base_rgb` | `ok` | required input in job |
| `frame:34:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0034.png |
| `frame:34:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:34:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0034_positive_delta_rgb.png |
| `frame:34:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:34:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0034_negative_delta_rgb.png |
| `frame:34:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0034.png |
| `frame:34:output_target:image` | `ok` | output target under output_root |
| `frame:34:output_target:metadata` | `ok` | output target under output_root |
| `frame:34:output_target:validation` | `ok` | output target under output_root |
| `frame:34:oracle_abs` | `ok` | oracle threshold |
| `frame:34:webgl_abs` | `ok` | WebGL threshold |
| `frame:35:input_present:base_rgb` | `ok` | required input in job |
| `frame:35:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0035.png |
| `frame:35:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:35:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0035_positive_delta_rgb.png |
| `frame:35:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:35:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0035_negative_delta_rgb.png |
| `frame:35:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0035.png |
| `frame:35:output_target:image` | `ok` | output target under output_root |
| `frame:35:output_target:metadata` | `ok` | output target under output_root |
| `frame:35:output_target:validation` | `ok` | output target under output_root |
| `frame:35:oracle_abs` | `ok` | oracle threshold |
| `frame:35:webgl_abs` | `ok` | WebGL threshold |
| `frame:36:input_present:base_rgb` | `ok` | required input in job |
| `frame:36:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0036.png |
| `frame:36:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:36:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0036_positive_delta_rgb.png |
| `frame:36:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:36:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0036_negative_delta_rgb.png |
| `frame:36:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0036.png |
| `frame:36:output_target:image` | `ok` | output target under output_root |
| `frame:36:output_target:metadata` | `ok` | output target under output_root |
| `frame:36:output_target:validation` | `ok` | output target under output_root |
| `frame:36:oracle_abs` | `ok` | oracle threshold |
| `frame:36:webgl_abs` | `ok` | WebGL threshold |
| `frame:37:input_present:base_rgb` | `ok` | required input in job |
| `frame:37:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0037.png |
| `frame:37:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:37:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0037_positive_delta_rgb.png |
| `frame:37:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:37:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0037_negative_delta_rgb.png |
| `frame:37:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0037.png |
| `frame:37:output_target:image` | `ok` | output target under output_root |
| `frame:37:output_target:metadata` | `ok` | output target under output_root |
| `frame:37:output_target:validation` | `ok` | output target under output_root |
| `frame:37:oracle_abs` | `ok` | oracle threshold |
| `frame:37:webgl_abs` | `ok` | WebGL threshold |
| `frame:38:input_present:base_rgb` | `ok` | required input in job |
| `frame:38:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0038.png |
| `frame:38:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:38:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0038_positive_delta_rgb.png |
| `frame:38:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:38:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0038_negative_delta_rgb.png |
| `frame:38:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0038.png |
| `frame:38:output_target:image` | `ok` | output target under output_root |
| `frame:38:output_target:metadata` | `ok` | output target under output_root |
| `frame:38:output_target:validation` | `ok` | output target under output_root |
| `frame:38:oracle_abs` | `ok` | oracle threshold |
| `frame:38:webgl_abs` | `ok` | WebGL threshold |
| `frame:39:input_present:base_rgb` | `ok` | required input in job |
| `frame:39:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0039.png |
| `frame:39:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:39:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0039_positive_delta_rgb.png |
| `frame:39:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:39:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0039_negative_delta_rgb.png |
| `frame:39:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0039.png |
| `frame:39:output_target:image` | `ok` | output target under output_root |
| `frame:39:output_target:metadata` | `ok` | output target under output_root |
| `frame:39:output_target:validation` | `ok` | output target under output_root |
| `frame:39:oracle_abs` | `ok` | oracle threshold |
| `frame:39:webgl_abs` | `ok` | WebGL threshold |
| `frame:40:input_present:base_rgb` | `ok` | required input in job |
| `frame:40:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0040.png |
| `frame:40:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:40:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0040_positive_delta_rgb.png |
| `frame:40:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:40:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0040_negative_delta_rgb.png |
| `frame:40:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0040.png |
| `frame:40:output_target:image` | `ok` | output target under output_root |
| `frame:40:output_target:metadata` | `ok` | output target under output_root |
| `frame:40:output_target:validation` | `ok` | output target under output_root |
| `frame:40:oracle_abs` | `ok` | oracle threshold |
| `frame:40:webgl_abs` | `ok` | WebGL threshold |
| `frame:41:input_present:base_rgb` | `ok` | required input in job |
| `frame:41:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0041.png |
| `frame:41:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:41:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0041_positive_delta_rgb.png |
| `frame:41:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:41:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0041_negative_delta_rgb.png |
| `frame:41:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0041.png |
| `frame:41:output_target:image` | `ok` | output target under output_root |
| `frame:41:output_target:metadata` | `ok` | output target under output_root |
| `frame:41:output_target:validation` | `ok` | output target under output_root |
| `frame:41:oracle_abs` | `ok` | oracle threshold |
| `frame:41:webgl_abs` | `ok` | WebGL threshold |
| `frame:42:input_present:base_rgb` | `ok` | required input in job |
| `frame:42:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0042.png |
| `frame:42:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:42:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0042_positive_delta_rgb.png |
| `frame:42:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:42:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0042_negative_delta_rgb.png |
| `frame:42:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0042.png |
| `frame:42:output_target:image` | `ok` | output target under output_root |
| `frame:42:output_target:metadata` | `ok` | output target under output_root |
| `frame:42:output_target:validation` | `ok` | output target under output_root |
| `frame:42:oracle_abs` | `ok` | oracle threshold |
| `frame:42:webgl_abs` | `ok` | WebGL threshold |
| `frame:43:input_present:base_rgb` | `ok` | required input in job |
| `frame:43:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0043.png |
| `frame:43:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:43:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0043_positive_delta_rgb.png |
| `frame:43:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:43:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0043_negative_delta_rgb.png |
| `frame:43:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0043.png |
| `frame:43:output_target:image` | `ok` | output target under output_root |
| `frame:43:output_target:metadata` | `ok` | output target under output_root |
| `frame:43:output_target:validation` | `ok` | output target under output_root |
| `frame:43:oracle_abs` | `ok` | oracle threshold |
| `frame:43:webgl_abs` | `ok` | WebGL threshold |
| `frame:44:input_present:base_rgb` | `ok` | required input in job |
| `frame:44:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0044.png |
| `frame:44:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:44:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0044_positive_delta_rgb.png |
| `frame:44:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:44:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0044_negative_delta_rgb.png |
| `frame:44:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0044.png |
| `frame:44:output_target:image` | `ok` | output target under output_root |
| `frame:44:output_target:metadata` | `ok` | output target under output_root |
| `frame:44:output_target:validation` | `ok` | output target under output_root |
| `frame:44:oracle_abs` | `ok` | oracle threshold |
| `frame:44:webgl_abs` | `ok` | WebGL threshold |
| `frame:45:input_present:base_rgb` | `ok` | required input in job |
| `frame:45:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0045.png |
| `frame:45:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:45:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0045_positive_delta_rgb.png |
| `frame:45:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:45:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0045_negative_delta_rgb.png |
| `frame:45:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0045.png |
| `frame:45:output_target:image` | `ok` | output target under output_root |
| `frame:45:output_target:metadata` | `ok` | output target under output_root |
| `frame:45:output_target:validation` | `ok` | output target under output_root |
| `frame:45:oracle_abs` | `ok` | oracle threshold |
| `frame:45:webgl_abs` | `ok` | WebGL threshold |
| `frame:46:input_present:base_rgb` | `ok` | required input in job |
| `frame:46:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0046.png |
| `frame:46:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:46:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0046_positive_delta_rgb.png |
| `frame:46:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:46:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0046_negative_delta_rgb.png |
| `frame:46:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0046.png |
| `frame:46:output_target:image` | `ok` | output target under output_root |
| `frame:46:output_target:metadata` | `ok` | output target under output_root |
| `frame:46:output_target:validation` | `ok` | output target under output_root |
| `frame:46:oracle_abs` | `ok` | oracle threshold |
| `frame:46:webgl_abs` | `ok` | WebGL threshold |
| `frame:47:input_present:base_rgb` | `ok` | required input in job |
| `frame:47:input:base_rgb` | `ok` | build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png |
| `frame:47:input_present:positive_delta_rgb` | `ok` | required input in job |
| `frame:47:input:positive_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0047_positive_delta_rgb.png |
| `frame:47:input_present:negative_delta_rgb` | `ok` | required input in job |
| `frame:47:input:negative_delta_rgb` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/bindings/frame_0047_negative_delta_rgb.png |
| `frame:47:accepted_reference` | `ok` | build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0047.png |
| `frame:47:output_target:image` | `ok` | output target under output_root |
| `frame:47:output_target:metadata` | `ok` | output target under output_root |
| `frame:47:output_target:validation` | `ok` | output target under output_root |
| `frame:47:oracle_abs` | `ok` | oracle threshold |
| `frame:47:webgl_abs` | `ok` | WebGL threshold |
| `public:url` | `ok` | public URL present |
| `public:manifest_checks` | `ok` | manifest HTTP checks |
| `public:live_index` | `ok` | {'status': 200, 'content_length': 5068} |
