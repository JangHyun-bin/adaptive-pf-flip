# S342 Mitsuba Depth-Aware Composite Validation

Generated UTC: `2026-06-20T01:09:53.500125+00:00`
Validation JSON: `build/shots/s342_mitsuba_depth_aware_composite_validation/validation.json`
Status: `passed`
Composite: `build/shots/s341_mitsuba_depth_aware_composite_c3/depth_aware_secondary_composite_summary.json`

## Summary

- Total checks: `129`
- Failed checks: `0`
- Skipped checks: `0`
- Max target MAD threshold: `18.0`
- Max contract MAD threshold: `9.0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `summary:schema` | `ok` | schema |
| `summary:version` | `ok` | version |
| `summary:status` | `ok` | status |
| `source:native_render_manifest` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/mitsuba_render.json |
| `source_schema:native_render_manifest` | `ok` | schema matches |
| `source:secondary_pass_contract` | `ok` | build/shots/s335_mitsuba_secondary_pass_contract/secondary_pass_contract.json |
| `source_schema:secondary_pass_contract` | `ok` | schema matches |
| `gallery:index` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/index.html |
| `gallery_asset:Composite GIF` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/shot.gif |
| `gallery_asset:Composite Strip 1` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/composite_strip_00.png |
| `gallery_asset:Composite Strip 2` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/composite_strip_01.png |
| `gallery_asset:Composite Strip 3` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/composite_strip_02.png |
| `gallery_asset:Composite Strip 4` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/composite_strip_03.png |
| `gallery_metadata:Composite summary` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/depth_aware_secondary_composite_summary.json |
| `gallery_metadata:Native render manifest` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/native_mitsuba_render.json |
| `gallery_metadata:Secondary pass contract` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/assets/secondary_pass_contract.json |
| `checks:frames` | `ok` | frame count |
| `checks:missing_references` | `ok` | missing references must stay zero |
| `checks:max_target_mad` | `ok` | max target MAD threshold |
| `checks:mean_target_mad` | `ok` | mean target MAD threshold |
| `checks:beats_contract_max` | `ok` | composite max target MAD must beat S335 contract |
| `checks:max_contract_mad` | `ok` | max contract drift threshold |
| `checks:mean_native_weight` | `ok` | mean native weight range |
| `frame:0:frame_id` | `ok` | integer frame id |
| `frame:0:output_frame` | `ok` | integer output frame |
| `frame:0:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0000.png |
| `frame:0:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0000.png |
| `frame:0:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0000.png |
| `frame:0:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0000.png |
| `frame:0:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0000.png |
| `frame:0:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0000.png |
| `frame:0:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0000.png |
| `frame:0:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0000.png |
| `frame:0:target_mad` | `ok` | frame target MAD |
| `frame:0:contract_mad` | `ok` | frame contract MAD |
| `frame:0:native_weight` | `ok` | frame native weight |
| `frame:1:frame_id` | `ok` | integer frame id |
| `frame:1:output_frame` | `ok` | integer output frame |
| `frame:1:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0001.png |
| `frame:1:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0001.png |
| `frame:1:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0001.png |
| `frame:1:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0001.png |
| `frame:1:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0001.png |
| `frame:1:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0001.png |
| `frame:1:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0001.png |
| `frame:1:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0001.png |
| `frame:1:target_mad` | `ok` | frame target MAD |
| `frame:1:contract_mad` | `ok` | frame contract MAD |
| `frame:1:native_weight` | `ok` | frame native weight |
| `frame:2:frame_id` | `ok` | integer frame id |
| `frame:2:output_frame` | `ok` | integer output frame |
| `frame:2:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0002.png |
| `frame:2:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0002.png |
| `frame:2:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0002.png |
| `frame:2:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0002.png |
| `frame:2:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0002.png |
| `frame:2:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0002.png |
| `frame:2:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0002.png |
| `frame:2:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0002.png |
| `frame:2:target_mad` | `ok` | frame target MAD |
| `frame:2:contract_mad` | `ok` | frame contract MAD |
| `frame:2:native_weight` | `ok` | frame native weight |
| `frame:3:frame_id` | `ok` | integer frame id |
| `frame:3:output_frame` | `ok` | integer output frame |
| `frame:3:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0003.png |
| `frame:3:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0003.png |
| `frame:3:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0003.png |
| `frame:3:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0003.png |
| `frame:3:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0003.png |
| `frame:3:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0003.png |
| `frame:3:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0003.png |
| `frame:3:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0003.png |
| `frame:3:target_mad` | `ok` | frame target MAD |
| `frame:3:contract_mad` | `ok` | frame contract MAD |
| `frame:3:native_weight` | `ok` | frame native weight |
| `frame:4:frame_id` | `ok` | integer frame id |
| `frame:4:output_frame` | `ok` | integer output frame |
| `frame:4:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0004.png |
| `frame:4:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0004.png |
| `frame:4:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0004.png |
| `frame:4:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0004.png |
| `frame:4:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0004.png |
| `frame:4:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0004.png |
| `frame:4:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0004.png |
| `frame:4:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0004.png |
| `frame:4:target_mad` | `ok` | frame target MAD |
| `frame:4:contract_mad` | `ok` | frame contract MAD |
| `frame:4:native_weight` | `ok` | frame native weight |
| `frame:5:frame_id` | `ok` | integer frame id |
| `frame:5:output_frame` | `ok` | integer output frame |
| `frame:5:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0005.png |
| `frame:5:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0005.png |
| `frame:5:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0005.png |
| `frame:5:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0005.png |
| `frame:5:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0005.png |
| `frame:5:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0005.png |
| `frame:5:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0005.png |
| `frame:5:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0005.png |
| `frame:5:target_mad` | `ok` | frame target MAD |
| `frame:5:contract_mad` | `ok` | frame contract MAD |
| `frame:5:native_weight` | `ok` | frame native weight |
| `frame:6:frame_id` | `ok` | integer frame id |
| `frame:6:output_frame` | `ok` | integer output frame |
| `frame:6:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0006.png |
| `frame:6:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0006.png |
| `frame:6:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0006.png |
| `frame:6:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0006.png |
| `frame:6:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0006.png |
| `frame:6:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0006.png |
| `frame:6:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0006.png |
| `frame:6:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0006.png |
| `frame:6:target_mad` | `ok` | frame target MAD |
| `frame:6:contract_mad` | `ok` | frame contract MAD |
| `frame:6:native_weight` | `ok` | frame native weight |
| `frame:7:frame_id` | `ok` | integer frame id |
| `frame:7:output_frame` | `ok` | integer output frame |
| `frame:7:native_repo_path` | `ok` | build/shots/s338_mitsuba_secondary_mist_m1/actual_render/previews/frame_0007.png |
| `frame:7:contract_repo_path` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0007.png |
| `frame:7:secondary_layer_repo_path` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0007.png |
| `frame:7:target_repo_path` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0007.png |
| `frame:7:composite_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/composites/frame_0007.png |
| `frame:7:native_weight_mask_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/native_weight_masks/frame_0007.png |
| `frame:7:diff_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/diffs/frame_0007.png |
| `frame:7:strip_repo_path` | `ok` | build/shots/s341_mitsuba_depth_aware_composite_c3/strips/frame_0007.png |
| `frame:7:target_mad` | `ok` | frame target MAD |
| `frame:7:contract_mad` | `ok` | frame contract MAD |
| `frame:7:native_weight` | `ok` | frame native weight |
| `frames:unique_output_frames` | `ok` | unique output frames |
| `frames:ascending_output_frames` | `ok` | ascending output frames |
