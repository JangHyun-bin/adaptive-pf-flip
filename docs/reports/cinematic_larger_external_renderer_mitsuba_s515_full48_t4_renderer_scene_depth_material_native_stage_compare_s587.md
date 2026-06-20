# S587 Mitsuba Renderer Scene Depth Material Native Stage Compare

Generated UTC: `2026-06-20T22:32:54.564663+00:00`
Summary JSON: `build/shots/s587_mitsuba_renderer_scene_depth_material_native_stage_compare/native_stage_compare_summary.json`
Gallery: `build/shots/s587_mitsuba_renderer_scene_depth_material_native_stage_compare/gallery/index.html`
Status: `ready`
Decision: `backend_sample_ready`

## Checks

- Frames: `48`
- Missing references: `0`
- Max native-vs-target abs diff: `0`
- Max native-vs-target mean diff: `0.0`
- Max native-vs-accepted abs diff: `5`
- Max native-vs-accepted mean diff: `0.4139242541152263`
- Max target-vs-accepted abs diff: `5`
- Max target-vs-accepted mean diff: `0.4139242541152263`
- Strip GIF bytes: `29.15 MB`

## Frame Samples

| Frame | Output | Native/Target Max | Native/Accepted Max | Native/Accepted Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 3 | 0.13618055555555555 | `build/shots/s587_mitsuba_renderer_scene_depth_material_native_stage_compare/strips/frame_0000_native_compare.png` |
| 24 | 24 | 0 | 4 | 0.10531057098765433 | `build/shots/s587_mitsuba_renderer_scene_depth_material_native_stage_compare/strips/frame_0024_native_compare.png` |
| 47 | 47 | 0 | 5 | 0.40434606481481483 | `build/shots/s587_mitsuba_renderer_scene_depth_material_native_stage_compare/strips/frame_0047_native_compare.png` |

## Next

Use this gate before replacing the process-proof stage with a real renderer material or tonemap backend sample.
