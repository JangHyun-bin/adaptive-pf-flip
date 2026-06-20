# S495 Mitsuba Low Frequency Runtime Import Preview Validation

Generated UTC: `2026-06-20T18:24:34.746820+00:00`
Validation JSON: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview_validation.json`
Status: `passed`
Preview: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`

## Summary

- Total checks: `230`
- Failed checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `preview:schema` | `ok` | schema |
| `preview:version` | `ok` | version |
| `source_bundle:file` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle.json |
| `source_bundle:schema` | `ok` | source bundle schema |
| `source_bundle:status` | `ok` | source bundle status |
| `preview:status` | `ok` | status |
| `checks:missing_required_bindings` | `ok` | missing_required_bindings |
| `checks:hash_mismatches` | `ok` | hash_mismatches |
| `checks:size_mismatches` | `ok` | size_mismatches |
| `checks:dimension_mismatches` | `ok` | dimension_mismatches |
| `checks:inside_bundle_violations` | `ok` | inside_bundle_violations |
| `checks:source_dependency_leaks` | `ok` | source_dependency_leaks |
| `checks:proof_failures` | `ok` | proof_failures |
| `checks:ready_frames` | `ok` | all frames ready |
| `checks:runtime_html_resolved` | `ok` | runtime HTML resolved |
| `checks:shader_refs_resolved` | `ok` | shader refs resolved |
| `runtime:runtime_webgl:inside_bundle` | `ok` | bundle-local asset |
| `runtime:runtime_webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime/runtime_webgl.html |
| `runtime:webgl_proof_gif:inside_bundle` | `ok` | bundle-local asset |
| `runtime:webgl_proof_gif` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/gallery/webgl_proof.gif |
| `runtime:shader_count` | `ok` | shader entrypoints resolved |
| `runtime:shader:glsl:inside_bundle` | `ok` | bundle-local asset |
| `runtime:shader:glsl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.glsl |
| `runtime:shader:hlsl:inside_bundle` | `ok` | bundle-local asset |
| `runtime:shader:hlsl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.hlsl |
| `frames:count` | `ok` | frame count |
| `frame:0:binding_present:base_rgb` | `ok` | required binding present |
| `frame:0:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_base_rgb.png |
| `frame:0:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:0:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:0:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_dark_damping_weight_luma.png |
| `frame:0:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/oracle/frame_0000_oracle.png |
| `frame:0:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_webgl_frame.png |
| `frame:0:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:0:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_proof_strip.png |
| `frame:0:proof_abs_diff` | `ok` | proof max diff |
| `frame:0:proof_mean_diff` | `ok` | proof mean diff |
| `frame:0:ready` | `ok` | frame ready |
| `frame:0:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:0:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:0:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:0:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:0:source_frame_match` | `ok` | output frame matches bundle |
| `frame:1:binding_present:base_rgb` | `ok` | required binding present |
| `frame:1:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_base_rgb.png |
| `frame:1:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:1:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:1:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_dark_damping_weight_luma.png |
| `frame:1:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/oracle/frame_0001_oracle.png |
| `frame:1:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_webgl_frame.png |
| `frame:1:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:1:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_proof_strip.png |
| `frame:1:proof_abs_diff` | `ok` | proof max diff |
| `frame:1:proof_mean_diff` | `ok` | proof mean diff |
| `frame:1:ready` | `ok` | frame ready |
| `frame:1:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:1:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:1:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:1:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:1:source_frame_match` | `ok` | output frame matches bundle |
| `frame:2:binding_present:base_rgb` | `ok` | required binding present |
| `frame:2:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_base_rgb.png |
| `frame:2:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:2:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:2:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_dark_damping_weight_luma.png |
| `frame:2:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/oracle/frame_0002_oracle.png |
| `frame:2:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_webgl_frame.png |
| `frame:2:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:2:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_proof_strip.png |
| `frame:2:proof_abs_diff` | `ok` | proof max diff |
| `frame:2:proof_mean_diff` | `ok` | proof mean diff |
| `frame:2:ready` | `ok` | frame ready |
| `frame:2:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:2:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:2:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:2:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:2:source_frame_match` | `ok` | output frame matches bundle |
| `frame:3:binding_present:base_rgb` | `ok` | required binding present |
| `frame:3:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_base_rgb.png |
| `frame:3:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:3:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:3:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_dark_damping_weight_luma.png |
| `frame:3:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/oracle/frame_0003_oracle.png |
| `frame:3:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_webgl_frame.png |
| `frame:3:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:3:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_proof_strip.png |
| `frame:3:proof_abs_diff` | `ok` | proof max diff |
| `frame:3:proof_mean_diff` | `ok` | proof mean diff |
| `frame:3:ready` | `ok` | frame ready |
| `frame:3:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:3:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:3:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:3:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:3:source_frame_match` | `ok` | output frame matches bundle |
| `frame:4:binding_present:base_rgb` | `ok` | required binding present |
| `frame:4:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_base_rgb.png |
| `frame:4:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:4:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:4:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_dark_damping_weight_luma.png |
| `frame:4:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/oracle/frame_0004_oracle.png |
| `frame:4:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_webgl_frame.png |
| `frame:4:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:4:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_proof_strip.png |
| `frame:4:proof_abs_diff` | `ok` | proof max diff |
| `frame:4:proof_mean_diff` | `ok` | proof mean diff |
| `frame:4:ready` | `ok` | frame ready |
| `frame:4:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:4:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:4:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:4:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:4:source_frame_match` | `ok` | output frame matches bundle |
| `frame:5:binding_present:base_rgb` | `ok` | required binding present |
| `frame:5:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_base_rgb.png |
| `frame:5:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:5:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:5:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_dark_damping_weight_luma.png |
| `frame:5:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/oracle/frame_0005_oracle.png |
| `frame:5:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_webgl_frame.png |
| `frame:5:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:5:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_proof_strip.png |
| `frame:5:proof_abs_diff` | `ok` | proof max diff |
| `frame:5:proof_mean_diff` | `ok` | proof mean diff |
| `frame:5:ready` | `ok` | frame ready |
| `frame:5:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:5:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:5:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:5:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:5:source_frame_match` | `ok` | output frame matches bundle |
| `frame:6:binding_present:base_rgb` | `ok` | required binding present |
| `frame:6:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_base_rgb.png |
| `frame:6:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:6:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:6:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_dark_damping_weight_luma.png |
| `frame:6:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/oracle/frame_0006_oracle.png |
| `frame:6:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_webgl_frame.png |
| `frame:6:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:6:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_proof_strip.png |
| `frame:6:proof_abs_diff` | `ok` | proof max diff |
| `frame:6:proof_mean_diff` | `ok` | proof mean diff |
| `frame:6:ready` | `ok` | frame ready |
| `frame:6:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:6:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:6:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:6:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:6:source_frame_match` | `ok` | output frame matches bundle |
| `frame:7:binding_present:base_rgb` | `ok` | required binding present |
| `frame:7:binding:base_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_base_rgb.png |
| `frame:7:binding_present:positive_delta_rgb` | `ok` | required binding present |
| `frame:7:binding:positive_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:binding_present:negative_delta_rgb` | `ok` | required binding present |
| `frame:7:binding:negative_delta_rgb:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:optional:dark_damping_weight_luma:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:optional:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_dark_damping_weight_luma.png |
| `frame:7:oracle:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/oracle/frame_0007_oracle.png |
| `frame:7:proof:webgl:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_webgl_frame.png |
| `frame:7:proof:strip:inside_bundle` | `ok` | bundle-local asset |
| `frame:7:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_proof_strip.png |
| `frame:7:proof_abs_diff` | `ok` | proof max diff |
| `frame:7:proof_mean_diff` | `ok` | proof mean diff |
| `frame:7:ready` | `ok` | frame ready |
| `frame:7:ui_input:base_rgb` | `ok` | UI input semantic present |
| `frame:7:ui_input:positive_delta_rgb` | `ok` | UI input semantic present |
| `frame:7:ui_input:negative_delta_rgb` | `ok` | UI input semantic present |
| `frame:7:ui_no_source_keys` | `ok` | no source-path keys in UI inputs |
| `frame:7:source_frame_match` | `ok` | output frame matches bundle |
| `output:index_html` | `ok` | build/shots/s495_mitsuba_low_frequency_runtime_import_preview/index.html |
| `output:index_mentions_bundle` | `ok` | bundle link in HTML |
| `output:index_mentions_frames` | `ok` | frame sections in HTML |
| `preview:no_source_keys_in_frames` | `ok` | no source-path keys in frame import data |
