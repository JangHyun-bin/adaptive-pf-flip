# S592 Mitsuba Renderer Scene Depth Material Backend Output Compare

Generated UTC: `2026-06-20T22:54:10.482062+00:00`
Summary JSON: `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/backend_output_compare_summary.json`
Gallery: `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/index.html`
Status: `ready`
Decision: `renderer_native_material_ready`

## Checks

- Frames: `48`
- Missing references: `0`
- Max backend-vs-target abs diff: `0`
- Max backend-vs-target mean diff: `0.0`
- Max backend-vs-accepted abs diff: `5`
- Max backend-vs-accepted mean diff: `0.4139242541152263`
- Max target-vs-accepted abs diff: `5`
- Max target-vs-accepted mean diff: `0.4139242541152263`
- Strip GIF bytes: `29.16 MB`

## Frame Samples

| Frame | Output | Backend/Target Max | Backend/Accepted Max | Backend/Accepted Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 3 | 0.13618055555555555 | `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/strips/frame_0000_backend_compare.png` |
| 24 | 24 | 0 | 4 | 0.10531057098765433 | `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/strips/frame_0024_backend_compare.png` |
| 47 | 47 | 0 | 5 | 0.40434606481481483 | `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/strips/frame_0047_backend_compare.png` |

## Next

Use this full48 backend gate before attempting a renderer-native material implementation.
