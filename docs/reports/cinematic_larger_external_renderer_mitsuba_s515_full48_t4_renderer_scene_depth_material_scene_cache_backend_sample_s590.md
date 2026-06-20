# S590 Mitsuba Renderer Scene Depth Material Scene-Cache Backend Sample

Generated UTC: `2026-06-20T22:46:13.388809+00:00`
Summary JSON: `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/scene_cache_backend_sample_summary.json`
Gallery: `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/gallery/index.html`
Status: `passed`

## Inputs

- Handoff manifest: `build/shots/s578_mitsuba_renderer_scene_cache_handoff/renderer_scene_cache_handoff_summary.json`
- Render-data summary: `build/shots/s580_mitsuba_renderer_scene_render_data/render_data_summary.json`
- Target summary: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

- Frames: `8`
- Passed frames: `8`
- Failed frames: `0`
- Process failures: `0`
- Max abs diff vs S585 target: `0`
- Max mean diff vs S585 target: `0.0`
- Max backend delta from source: `5`
- Output bytes: `2.61 MB`
- GIF bytes: `1.33 MB`

## Frame Results

| Job | Frame | Output | Status | Return | Strength | Max Diff | Output | Strip |
| ---: | ---: | ---: | --- | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0 | `passed` | 0 | 0.55 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0000.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0000_backend_sample.png` |
| 1 | 7 | 7 | `passed` | 0 | 0.525 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0007.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0007_backend_sample.png` |
| 2 | 13 | 13 | `passed` | 0 | 0.6499999999999999 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0013.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0013_backend_sample.png` |
| 3 | 20 | 20 | `passed` | 0 | 0.6 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0020.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0020_backend_sample.png` |
| 4 | 27 | 27 | `passed` | 0 | 0.575 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0027.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0027_backend_sample.png` |
| 5 | 34 | 34 | `passed` | 0 | 0.6749999999999999 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0034.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0034_backend_sample.png` |
| 6 | 40 | 40 | `passed` | 0 | 0.65 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0040.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0040_backend_sample.png` |
| 7 | 47 | 47 | `passed` | 0 | 0.75 | 0 | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/backend_frames/frame_0047.png` | `build/shots/s590_mitsuba_renderer_scene_depth_material_scene_cache_backend_sample/strips/frame_0047_backend_sample.png` |

## Next

Use this scene-cache direct backend sample as the input contract for a renderer-native material or tonemap implementation, then rerun the S587 promotion gate.
