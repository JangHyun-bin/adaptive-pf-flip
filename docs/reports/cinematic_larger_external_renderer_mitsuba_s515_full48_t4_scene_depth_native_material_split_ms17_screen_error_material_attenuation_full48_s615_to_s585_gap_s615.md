# S615 Output Gap: S615 Native Split vs S585 Scene-Depth Target

Generated UTC: `2026-06-21T01:44:58.007690+00:00`
Status: `ready`

## Inputs

- Actual: `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/render_vs18/mitsuba_render.json`
- Reference: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Mean gap MAD: `3.0605547785922496`
- Max gap MAD: `5.672728909465021`
- Max gap abs: `172`
- GIF bytes: `28.20 MB`

## Frame Samples

| Output | MAD | Max Abs | Strip |
| ---: | ---: | ---: | --- |
| 0 | 2.8101202417695474 | 142 | `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/s615_to_s585_gap/strips/frame_0000.png` |
| 24 | 2.481033950617284 | 137 | `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/s615_to_s585_gap/strips/frame_0024.png` |
| 47 | 5.617730195473251 | 160 | `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/s615_to_s585_gap/strips/frame_0047.png` |

## Next

Use this gap as evidence that material-only attenuation regresses and should be replaced by separated response buffers.
