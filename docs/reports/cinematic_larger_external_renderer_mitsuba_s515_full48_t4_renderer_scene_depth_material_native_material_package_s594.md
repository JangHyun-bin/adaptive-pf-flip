# S594 Mitsuba Renderer Scene Depth Material Native Material Package

Generated UTC: `2026-06-20T23:02:46.836596+00:00`
Summary JSON: `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/native_material_package_summary.json`
Gallery: `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/gallery/index.html`
Status: `ready`

## Inputs

- Backend summary: `build/shots/s591_mitsuba_renderer_scene_depth_material_scene_cache_backend_full48/scene_cache_backend_full48_summary.json`
- Backend compare summary: `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/backend_output_compare_summary.json`
- Target summary: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Material snippets: `48`
- Texture bindings: `48`
- Max backend-vs-target abs diff: `0`
- Max backend-vs-target mean diff: `0.0`
- Max backend-vs-accepted abs diff: `5`
- Max backend-vs-accepted mean diff: `0.4139242541152263`
- Snippet bytes: `45.77 KB`
- Intent GIF bytes: `6.42 MB`

## Material Ranges

- Alpha: `0.008699999999999998` .. `0.011999999999999999`
- Mask weight: `0.625` .. `0.74875`
- Strength: `0.5` .. `0.775`

## Frame Samples

| Frame | Output | Strength | Alpha | Mask Weight | Backend/Target Max | Snippet | Strip |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0.55 | 0.011399999999999997 | 0.6475000000000001 | 0 | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/snippets/frame_0000_scene_depth_material.xml` | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/strips/frame_0000_native_material_intent.png` |
| 24 | 24 | 0.575 | 0.011099999999999999 | 0.65875 | 0 | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/snippets/frame_0024_scene_depth_material.xml` | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/strips/frame_0024_native_material_intent.png` |
| 47 | 47 | 0.75 | 0.008999999999999998 | 0.7375 | 0 | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/snippets/frame_0047_scene_depth_material.xml` | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/strips/frame_0047_native_material_intent.png` |

## Next

Bind this package to a Mitsuba XML water-material sample and render it through the native renderer path.
