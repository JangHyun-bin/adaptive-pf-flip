# S619 Response AOV Consumer S075 vs S585 Gap

Generated UTC: `2026-06-21T02:21:38.731181+00:00`
Status: `ready`

## Inputs

- Actual: `build/shots/s619_mitsuba_response_aov_consumer_s075/response_aov_consumer_summary.json`
- Reference: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Mean gap MAD: `2.982389550647291`
- Max gap MAD: `5.524723508230453`
- Max gap abs: `148`
- GIF bytes: `28.46 MB`

## Frame Samples

| Output | MAD | Max Abs | Strip |
| ---: | ---: | ---: | --- |
| 0 | 2.7625295781893002 | 132 | `build/shots/s619_mitsuba_response_aov_consumer_s075/gap_vs_s585/strips/frame_0000.png` |
| 24 | 2.346917438271605 | 113 | `build/shots/s619_mitsuba_response_aov_consumer_s075/gap_vs_s585/strips/frame_0024.png` |
| 47 | 5.414034850823045 | 124 | `build/shots/s619_mitsuba_response_aov_consumer_s075/gap_vs_s585/strips/frame_0047.png` |

## Next

Use this consumed AOV target-gate result as the import proof for renderer/cache handoff integration.
