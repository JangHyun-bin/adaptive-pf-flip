# S468 Mitsuba Visual Cache Bundle

Generated UTC: `2026-06-20T15:51:44.926589+00:00`
Bundle JSON: `build/shots/s468_mitsuba_visual_cache_bundle/visual_cache_bundle_manifest.json`
Gallery: `build/shots/s468_mitsuba_visual_cache_bundle/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Copied files: `77`
- Copied bytes: `54.21 MB`
- Missing references: `0`
- Hash failures: `0`
- Mean target-gap MAD: `19.10240579989712`
- Max target-gap MAD: `23.950307355967077`
- Max target-gap absolute diff: `176`
- Max changed coverage: `0.019110725308641975`
- Max layer delta: `30`

## Sources

| Source | Schema | Status | Path |
| --- | --- | --- | --- |
| base_handoff | `lsfs_mitsuba_renderer_handoff_bundle` | `ready` | `build/shots/s327_mitsuba_renderer_handoff_bundle/handoff_manifest.json` |
| signed_response_layer | `lsfs_mitsuba_secondary_composite` | `ready` | `build/shots/s467_mitsuba_signed_response_layer/signed_response_layer_summary.json` |
| target_gap | `lsfs_mitsuba_renderer_target_gap` | `ready` | `build/shots/s467_mitsuba_signed_response_layer_target_gap/renderer_target_gap_summary.json` |

## Frame Samples

| Frame | Output | Requests | Gap MAD | Layer | Composite | Strip |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 2 | 22.43327739197531 | `build/shots/s468_mitsuba_visual_cache_bundle/frames/signed_response_layer/frame_0000.png` | `build/shots/s468_mitsuba_visual_cache_bundle/frames/signed_composite/frame_0000.png` | `build/shots/s468_mitsuba_visual_cache_bundle/frames/target_gap_strip/frame_0000.png` |
| 4 | 27 | 1 | 19.087934670781895 | `build/shots/s468_mitsuba_visual_cache_bundle/frames/signed_response_layer/frame_0004.png` | `build/shots/s468_mitsuba_visual_cache_bundle/frames/signed_composite/frame_0004.png` | `build/shots/s468_mitsuba_visual_cache_bundle/frames/target_gap_strip/frame_0004.png` |
| 7 | 47 | 3 | 20.837453060699588 | `build/shots/s468_mitsuba_visual_cache_bundle/frames/signed_response_layer/frame_0007.png` | `build/shots/s468_mitsuba_visual_cache_bundle/frames/signed_composite/frame_0007.png` | `build/shots/s468_mitsuba_visual_cache_bundle/frames/target_gap_strip/frame_0007.png` |

## Next

Use this promoted visual-cache bundle as the renderer handoff input, then continue by either publishing it for review or moving the same layer contract into renderer-native response/AOV work.
