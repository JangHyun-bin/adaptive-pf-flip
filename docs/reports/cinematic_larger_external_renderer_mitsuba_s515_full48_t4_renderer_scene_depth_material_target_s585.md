# S585 Mitsuba Renderer Scene Depth Material Target

Generated UTC: `2026-06-20T22:23:41.839696+00:00`
Summary JSON: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`
Gallery: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/gallery/index.html`
Status: `ready`

## Selected Target

- Label: `strength_1_0`
- Base strength: `1.0`
- Max absolute delta: `5`
- Max mean absolute delta: `0.4139242541152263`
- Max changed coverage: `0.3287885802469136`

## Checks

- Frames: `48`
- Missing references: `0`
- Ready target previews: `48`

## Frame Samples

| Frame | Output | Effective Strength | Max Delta | Mean Delta | Target | Strip |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0.55 | 3 | 0.13618055555555555 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/frames/frame_0000.png` | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/strips/frame_0000_depth_material_sweep.png` |
| 24 | 24 | 0.575 | 4 | 0.10531057098765433 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/frames/frame_0024.png` | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/strips/frame_0024_depth_material_sweep.png` |
| 47 | 47 | 0.75 | 5 | 0.40434606481481483 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/frames/frame_0047.png` | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/strips/frame_0047_depth_material_sweep.png` |

## Next

Implement the S585 target in the native renderer path and compare the native result against the selected S584 preview references before promotion.
