# S336 Mitsuba Secondary Pass Contract Validation

Generated UTC: `2026-06-20T00:21:46.370283+00:00`
Validation JSON: `build/shots/s336_mitsuba_secondary_pass_contract_validation/validation.json`
Status: `passed`
Contract: `build/shots/s335_mitsuba_secondary_pass_contract/secondary_pass_contract.json`
Public URL: `https://laundry-tanks-prot-until.trycloudflare.com`
Public check: `False`

## Summary

- Total checks: `187`
- Failed checks: `0`
- Skipped checks: `2`
- Max overlay MAD threshold: `20.0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `contract:schema` | `ok` | schema |
| `contract:version` | `ok` | version |
| `contract:status` | `ok` | status |
| `source:actual_render_manifest` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/mitsuba_render.json |
| `source_schema:actual_render_manifest` | `ok` | schema matches |
| `source:handoff_manifest` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/handoff_manifest.json |
| `source_schema:handoff_manifest` | `ok` | schema matches |
| `source:overlay_summary` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/secondary_overlay_summary.json |
| `source_schema:overlay_summary` | `ok` | schema matches |
| `source:publish_manifest` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid_publish/publish_manifest.json |
| `source:target_summary` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json |
| `source_schema:target_summary` | `ok` | schema matches |
| `artifact:gallery index` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/index.html |
| `artifact:overlay gif` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/shot.gif |
| `artifact:Overlay Strip 1` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_00.png |
| `artifact:Overlay Strip 2` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_01.png |
| `artifact:Overlay Strip 3` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_02.png |
| `artifact:Overlay Strip 4` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_03.png |
| `checks:frames` | `ok` | frame count |
| `checks:overlay_frames` | `ok` | overlay frame count |
| `checks:missing_frame_assets` | `ok` | missing frame assets must stay zero |
| `checks:overlay_missing_references` | `ok` | overlay missing references must stay zero |
| `checks:max_overlay_mean_abs_diff` | `ok` | contract max overlay MAD |
| `checks:mean_overlay_mean_abs_diff` | `ok` | contract mean overlay MAD |
| `checks:max_overlay_max_abs_diff` | `ok` | contract max absolute channel diff |
| `checks:public_url_present` | `ok` | public review URL is recorded |
| `pass:base_renderer` | `ok` | base renderer |
| `pass:implementation_stage` | `ok` | implementation stage |
| `pass:composition` | `ok` | composition contract |
| `pass:future_expectations` | `ok` | renderer-native follow-up expectations recorded |
| `frame:0:frame_id` | `ok` | integer frame id |
| `frame:0:output_frame` | `ok` | integer output frame |
| `frame:0:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:0:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:0:actual:status` | `ok` | asset status |
| `frame:0:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0000.png |
| `frame:0:secondary_layer:status` | `ok` | asset status |
| `frame:0:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0000.png |
| `frame:0:overlay:status` | `ok` | asset status |
| `frame:0:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0000.png |
| `frame:0:overlay_graded:status` | `ok` | asset status |
| `frame:0:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0000.png |
| `frame:0:target:status` | `ok` | asset status |
| `frame:0:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0000.png |
| `frame:0:diff:status` | `ok` | asset status |
| `frame:0:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0000.png |
| `frame:0:strip:status` | `ok` | asset status |
| `frame:0:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0000.png |
| `frame:0:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:1:frame_id` | `ok` | integer frame id |
| `frame:1:output_frame` | `ok` | integer output frame |
| `frame:1:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:1:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:1:actual:status` | `ok` | asset status |
| `frame:1:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0001.png |
| `frame:1:secondary_layer:status` | `ok` | asset status |
| `frame:1:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0001.png |
| `frame:1:overlay:status` | `ok` | asset status |
| `frame:1:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0001.png |
| `frame:1:overlay_graded:status` | `ok` | asset status |
| `frame:1:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0001.png |
| `frame:1:target:status` | `ok` | asset status |
| `frame:1:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0001.png |
| `frame:1:diff:status` | `ok` | asset status |
| `frame:1:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0001.png |
| `frame:1:strip:status` | `ok` | asset status |
| `frame:1:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0001.png |
| `frame:1:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:2:frame_id` | `ok` | integer frame id |
| `frame:2:output_frame` | `ok` | integer output frame |
| `frame:2:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:2:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:2:actual:status` | `ok` | asset status |
| `frame:2:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0002.png |
| `frame:2:secondary_layer:status` | `ok` | asset status |
| `frame:2:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0002.png |
| `frame:2:overlay:status` | `ok` | asset status |
| `frame:2:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0002.png |
| `frame:2:overlay_graded:status` | `ok` | asset status |
| `frame:2:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0002.png |
| `frame:2:target:status` | `ok` | asset status |
| `frame:2:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0002.png |
| `frame:2:diff:status` | `ok` | asset status |
| `frame:2:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0002.png |
| `frame:2:strip:status` | `ok` | asset status |
| `frame:2:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0002.png |
| `frame:2:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:3:frame_id` | `ok` | integer frame id |
| `frame:3:output_frame` | `ok` | integer output frame |
| `frame:3:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:3:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:3:actual:status` | `ok` | asset status |
| `frame:3:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0003.png |
| `frame:3:secondary_layer:status` | `ok` | asset status |
| `frame:3:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0003.png |
| `frame:3:overlay:status` | `ok` | asset status |
| `frame:3:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0003.png |
| `frame:3:overlay_graded:status` | `ok` | asset status |
| `frame:3:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0003.png |
| `frame:3:target:status` | `ok` | asset status |
| `frame:3:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0003.png |
| `frame:3:diff:status` | `ok` | asset status |
| `frame:3:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0003.png |
| `frame:3:strip:status` | `ok` | asset status |
| `frame:3:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0003.png |
| `frame:3:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:4:frame_id` | `ok` | integer frame id |
| `frame:4:output_frame` | `ok` | integer output frame |
| `frame:4:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:4:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:4:actual:status` | `ok` | asset status |
| `frame:4:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0004.png |
| `frame:4:secondary_layer:status` | `ok` | asset status |
| `frame:4:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0004.png |
| `frame:4:overlay:status` | `ok` | asset status |
| `frame:4:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0004.png |
| `frame:4:overlay_graded:status` | `ok` | asset status |
| `frame:4:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0004.png |
| `frame:4:target:status` | `ok` | asset status |
| `frame:4:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0004.png |
| `frame:4:diff:status` | `ok` | asset status |
| `frame:4:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0004.png |
| `frame:4:strip:status` | `ok` | asset status |
| `frame:4:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0004.png |
| `frame:4:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:5:frame_id` | `ok` | integer frame id |
| `frame:5:output_frame` | `ok` | integer output frame |
| `frame:5:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:5:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:5:actual:status` | `ok` | asset status |
| `frame:5:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0005.png |
| `frame:5:secondary_layer:status` | `ok` | asset status |
| `frame:5:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0005.png |
| `frame:5:overlay:status` | `ok` | asset status |
| `frame:5:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0005.png |
| `frame:5:overlay_graded:status` | `ok` | asset status |
| `frame:5:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0005.png |
| `frame:5:target:status` | `ok` | asset status |
| `frame:5:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0005.png |
| `frame:5:diff:status` | `ok` | asset status |
| `frame:5:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0005.png |
| `frame:5:strip:status` | `ok` | asset status |
| `frame:5:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0005.png |
| `frame:5:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:6:frame_id` | `ok` | integer frame id |
| `frame:6:output_frame` | `ok` | integer output frame |
| `frame:6:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:6:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:6:actual:status` | `ok` | asset status |
| `frame:6:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0006.png |
| `frame:6:secondary_layer:status` | `ok` | asset status |
| `frame:6:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0006.png |
| `frame:6:overlay:status` | `ok` | asset status |
| `frame:6:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0006.png |
| `frame:6:overlay_graded:status` | `ok` | asset status |
| `frame:6:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0006.png |
| `frame:6:target:status` | `ok` | asset status |
| `frame:6:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0006.png |
| `frame:6:diff:status` | `ok` | asset status |
| `frame:6:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0006.png |
| `frame:6:strip:status` | `ok` | asset status |
| `frame:6:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0006.png |
| `frame:6:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frame:7:frame_id` | `ok` | integer frame id |
| `frame:7:output_frame` | `ok` | integer output frame |
| `frame:7:overlay_mean_abs_diff` | `ok` | per-frame overlay MAD |
| `frame:7:overlay_max_abs_diff` | `ok` | per-frame max absolute channel diff |
| `frame:7:actual:status` | `ok` | asset status |
| `frame:7:actual:file` | `ok` | build/shots/s333_mitsuba_secondary_halo_h2/actual_render/previews/frame_0007.png |
| `frame:7:secondary_layer:status` | `ok` | asset status |
| `frame:7:secondary_layer:file` | `ok` | build/shots/s327_mitsuba_renderer_handoff_bundle/reference_frames/secondary_layer/frame_0007.png |
| `frame:7:overlay:status` | `ok` | asset status |
| `frame:7:overlay:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_secondary/frame_0007.png |
| `frame:7:overlay_graded:status` | `ok` | asset status |
| `frame:7:overlay_graded:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0007.png |
| `frame:7:target:status` | `ok` | asset status |
| `frame:7:target:file` | `ok` | build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0007.png |
| `frame:7:diff:status` | `ok` | asset status |
| `frame:7:diff:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/diffs/frame_0007.png |
| `frame:7:strip:status` | `ok` | asset status |
| `frame:7:strip:file` | `ok` | build/shots/s334_mitsuba_secondary_overlay_hybrid/strips/frame_0007.png |
| `frame:7:overlay_graded_sha` | `ok` | overlay graded hash matches expected frame hash |
| `frames:unique_frame_ids` | `ok` | unique frame ids |
| `frames:unique_output_frames` | `ok` | unique output frames |
| `frames:ascending_output_frames` | `ok` | ascending output frame mapping |
| `public:index` | `skipped` | not requested |
| `public:shot_gif` | `skipped` | not requested |
