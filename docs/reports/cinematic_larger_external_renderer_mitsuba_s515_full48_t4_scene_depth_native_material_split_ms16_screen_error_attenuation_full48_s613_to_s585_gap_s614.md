# S614 Input Gap: S613 Native Split vs S585 Scene-Depth Target

Generated UTC: `2026-06-21T01:27:26.509768+00:00`
Status: `ready`

## Inputs

- Actual: `build/shots/s613_mitsuba_scene_depth_native_material_split_ms15_screen_region_attenuation_full48/render_vs18/mitsuba_render.json`
- Reference: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Mean gap MAD: `3.050184823495371`
- Max gap MAD: `5.5998945473251025`
- Max gap abs: `172`
- GIF bytes: `28.18 MB`

## Frame Samples

| Output | MAD | Max Abs | Strip |
| ---: | ---: | ---: | --- |
| 0 | 2.8101202417695474 | 142 | `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/strips/frame_0000.png` |
| 24 | 2.481033950617284 | 137 | `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/strips/frame_0024.png` |
| 47 | 5.543927469135802 | 148 | `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/strips/frame_0047.png` |

## Next

Use this signed gap as screen-error input for S614 face-level material attenuation.
