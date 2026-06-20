# S494 Mitsuba Low Frequency Runtime Handoff Bundle Validation

Generated UTC: `2026-06-20T18:16:42.007627+00:00`
Validation JSON: `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle_validation.json`
Status: `passed`
Bundle: `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle.json`

## Summary

- Total checks: `161`
- Failed checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `bundle:schema` | `ok` | schema |
| `bundle:version` | `ok` | version |
| `source:compositor_contract` | `ok` | build/shots/s492_mitsuba_low_frequency_compositor_contract/low_frequency_compositor_contract.json |
| `source_schema:compositor_contract` | `ok` | schema matches |
| `source:webgl_proof_summary` | `ok` | build/shots/s493_mitsuba_low_frequency_webgl_compositor_proof/webgl_compositor_proof_summary.json |
| `source_schema:webgl_proof_summary` | `ok` | schema matches |
| `runtime_contract:stage` | `ok` | stage |
| `runtime_contract:expression` | `ok` | delta expression |
| `runtime_contract:binding:base_rgb` | `ok` | required binding present |
| `runtime_contract:binding:positive_delta_rgb` | `ok` | required binding present |
| `runtime_contract:binding:negative_delta_rgb` | `ok` | required binding present |
| `bundle:status` | `ok` | status |
| `checks:contract_status` | `ok` | contract status |
| `checks:proof_status` | `ok` | proof status |
| `checks:proof_abs_diff` | `ok` | WebGL proof max abs diff |
| `checks:proof_mean_diff` | `ok` | WebGL proof max mean diff |
| `checks:proof_missing` | `ok` | WebGL proof missing refs |
| `totals:frames` | `ok` | frame count |
| `totals:missing` | `ok` | missing references |
| `totals:copied_files` | `ok` | copied file count |
| `checks:target_gap_mean_mad` | `ok` | non-negative target gap metric |
| `checks:target_gap_max_mad` | `ok` | non-negative target gap metric |
| `checks:target_gap_max_abs_diff` | `ok` | non-negative target gap metric |
| `copied:metadata:webgl_proof_summary` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/metadata/webgl_compositor_proof_summary.json |
| `copied:metadata:compositor_contract` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/metadata/low_frequency_compositor_contract.json |
| `copied:source_metadata:texture_package_summary` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/metadata/texture_package_summary.json |
| `copied:source_metadata:post_tonemap_stage_summary` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/metadata/post_tonemap_stage_summary.json |
| `copied:source_metadata:target_gap_summary` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/metadata/target_gap_summary.json |
| `copied:runtime:runtime_webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime/runtime_webgl.html |
| `copied:proof_gallery:webgl_proof_gif` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/gallery/webgl_proof.gif |
| `copied:glsl_reference:low_frequency_parity_post_tonemap.glsl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.glsl |
| `copied:hlsl_reference:low_frequency_parity_post_tonemap.hlsl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.hlsl |
| `copied:pseudocode_reference:low_frequency_parity_post_tonemap.txt` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.txt |
| `copied:base_rgb:frame_0000_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_base_rgb.png |
| `copied:positive_delta_rgb:frame_0000_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0000_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0000_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_dark_damping_weight_luma.png |
| `copied:oracle:frame_0000_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/oracle/frame_0000_oracle.png |
| `copied:webgl_frame:frame_0000_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_webgl_frame.png |
| `copied:proof_strip:frame_0000_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_proof_strip.png |
| `copied:base_rgb:frame_0001_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_base_rgb.png |
| `copied:positive_delta_rgb:frame_0001_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0001_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0001_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_dark_damping_weight_luma.png |
| `copied:oracle:frame_0001_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/oracle/frame_0001_oracle.png |
| `copied:webgl_frame:frame_0001_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_webgl_frame.png |
| `copied:proof_strip:frame_0001_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_proof_strip.png |
| `copied:base_rgb:frame_0002_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_base_rgb.png |
| `copied:positive_delta_rgb:frame_0002_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0002_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0002_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_dark_damping_weight_luma.png |
| `copied:oracle:frame_0002_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/oracle/frame_0002_oracle.png |
| `copied:webgl_frame:frame_0002_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_webgl_frame.png |
| `copied:proof_strip:frame_0002_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_proof_strip.png |
| `copied:base_rgb:frame_0003_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_base_rgb.png |
| `copied:positive_delta_rgb:frame_0003_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0003_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0003_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_dark_damping_weight_luma.png |
| `copied:oracle:frame_0003_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/oracle/frame_0003_oracle.png |
| `copied:webgl_frame:frame_0003_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_webgl_frame.png |
| `copied:proof_strip:frame_0003_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_proof_strip.png |
| `copied:base_rgb:frame_0004_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_base_rgb.png |
| `copied:positive_delta_rgb:frame_0004_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0004_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0004_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_dark_damping_weight_luma.png |
| `copied:oracle:frame_0004_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/oracle/frame_0004_oracle.png |
| `copied:webgl_frame:frame_0004_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_webgl_frame.png |
| `copied:proof_strip:frame_0004_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_proof_strip.png |
| `copied:base_rgb:frame_0005_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_base_rgb.png |
| `copied:positive_delta_rgb:frame_0005_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0005_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0005_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_dark_damping_weight_luma.png |
| `copied:oracle:frame_0005_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/oracle/frame_0005_oracle.png |
| `copied:webgl_frame:frame_0005_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_webgl_frame.png |
| `copied:proof_strip:frame_0005_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_proof_strip.png |
| `copied:base_rgb:frame_0006_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_base_rgb.png |
| `copied:positive_delta_rgb:frame_0006_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0006_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0006_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_dark_damping_weight_luma.png |
| `copied:oracle:frame_0006_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/oracle/frame_0006_oracle.png |
| `copied:webgl_frame:frame_0006_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_webgl_frame.png |
| `copied:proof_strip:frame_0006_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_proof_strip.png |
| `copied:base_rgb:frame_0007_base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_base_rgb.png |
| `copied:positive_delta_rgb:frame_0007_positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_positive_delta_rgb.png |
| `copied:negative_delta_rgb:frame_0007_negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_negative_delta_rgb.png |
| `copied:dark_damping_weight_luma:frame_0007_dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_dark_damping_weight_luma.png |
| `copied:oracle:frame_0007_oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/oracle/frame_0007_oracle.png |
| `copied:webgl_frame:frame_0007_webgl_frame` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_webgl_frame.png |
| `copied:proof_strip:frame_0007_proof_strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_proof_strip.png |
| `frame:0:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_base_rgb.png |
| `frame:0:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_positive_delta_rgb.png |
| `frame:0:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_negative_delta_rgb.png |
| `frame:0:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/bindings/frame_0000_dark_damping_weight_luma.png |
| `frame:0:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/oracle/frame_0000_oracle.png |
| `frame:0:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_webgl_frame.png |
| `frame:0:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_proof_strip.png |
| `frame:0:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:0:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:1:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_base_rgb.png |
| `frame:1:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_positive_delta_rgb.png |
| `frame:1:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_negative_delta_rgb.png |
| `frame:1:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/bindings/frame_0001_dark_damping_weight_luma.png |
| `frame:1:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/oracle/frame_0001_oracle.png |
| `frame:1:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_webgl_frame.png |
| `frame:1:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_proof_strip.png |
| `frame:1:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:1:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:2:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_base_rgb.png |
| `frame:2:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_positive_delta_rgb.png |
| `frame:2:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_negative_delta_rgb.png |
| `frame:2:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/bindings/frame_0002_dark_damping_weight_luma.png |
| `frame:2:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/oracle/frame_0002_oracle.png |
| `frame:2:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_webgl_frame.png |
| `frame:2:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_proof_strip.png |
| `frame:2:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:2:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:3:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_base_rgb.png |
| `frame:3:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_positive_delta_rgb.png |
| `frame:3:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_negative_delta_rgb.png |
| `frame:3:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/bindings/frame_0003_dark_damping_weight_luma.png |
| `frame:3:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/oracle/frame_0003_oracle.png |
| `frame:3:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_webgl_frame.png |
| `frame:3:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_proof_strip.png |
| `frame:3:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:3:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:4:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_base_rgb.png |
| `frame:4:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_positive_delta_rgb.png |
| `frame:4:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_negative_delta_rgb.png |
| `frame:4:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/bindings/frame_0004_dark_damping_weight_luma.png |
| `frame:4:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/oracle/frame_0004_oracle.png |
| `frame:4:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_webgl_frame.png |
| `frame:4:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_proof_strip.png |
| `frame:4:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:4:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:5:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_base_rgb.png |
| `frame:5:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_positive_delta_rgb.png |
| `frame:5:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_negative_delta_rgb.png |
| `frame:5:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/bindings/frame_0005_dark_damping_weight_luma.png |
| `frame:5:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/oracle/frame_0005_oracle.png |
| `frame:5:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_webgl_frame.png |
| `frame:5:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_proof_strip.png |
| `frame:5:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:5:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:6:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_base_rgb.png |
| `frame:6:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_positive_delta_rgb.png |
| `frame:6:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_negative_delta_rgb.png |
| `frame:6:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/bindings/frame_0006_dark_damping_weight_luma.png |
| `frame:6:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/oracle/frame_0006_oracle.png |
| `frame:6:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_webgl_frame.png |
| `frame:6:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_proof_strip.png |
| `frame:6:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:6:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
| `frame:7:binding:base_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_base_rgb.png |
| `frame:7:binding:positive_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_positive_delta_rgb.png |
| `frame:7:binding:negative_delta_rgb` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_negative_delta_rgb.png |
| `frame:7:binding:dark_damping_weight_luma` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/bindings/frame_0007_dark_damping_weight_luma.png |
| `frame:7:oracle` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/oracle/frame_0007_oracle.png |
| `frame:7:proof:webgl` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_webgl_frame.png |
| `frame:7:proof:strip` | `ok` | build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_proof_strip.png |
| `frame:7:proof_abs_diff` | `ok` | frame WebGL proof diff |
| `frame:7:proof_mean_diff` | `ok` | frame WebGL proof mean diff |
