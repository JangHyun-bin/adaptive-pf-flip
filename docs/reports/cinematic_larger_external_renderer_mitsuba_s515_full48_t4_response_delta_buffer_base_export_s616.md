# S616 Mitsuba Response Buffer Base-Only Export

Generated UTC: `2026-06-21T01:54:04.987337+00:00`
Export JSON: `build/shots/s616_mitsuba_response_delta_buffer_probe/base_only/mitsuba_base_export.json`
Status: `ready`

## Inputs

- Split export: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/mitsuba_export.json`

## Base-Only Export

- Remove response shapes: `True`
- Remove response BSDFs: `True`

## Checks

- Frames exported: `48`
- Missing references: `0`
- Response shapes removed: `96`
- Response BSDFs removed: `96`
- Response faces removed: `55526`
- XML bytes: `1.88 MB`
- Failures: `0`

## Frame Samples

| Output | Removed Shapes | Removed BSDFs | Response Faces | XML |
| ---: | ---: | ---: | ---: | --- |
| 0 | 2 | 2 | 1200 | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_only/scenes/frame_0000.xml` |
| 24 | 2 | 2 | 1200 | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_only/scenes/frame_0024.xml` |
| 47 | 2 | 2 | 841 | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_only/scenes/frame_0047.xml` |

## Next

Render this base-only export and subtract it from the split full render to inspect response contribution.
