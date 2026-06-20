# S413 Mitsuba Material Response MR2 Validation

Generated UTC: `2026-06-20T09:35:36.509528+00:00`
Validation JSON: `build/shots/s413_mitsuba_material_response_mr2_validation`
Status: `ready`

## Mitsuba

- Command: `mitsuba`
- Found: `True`
- Required: `False`
- Path: `C:\Users\user\AppData\Local\Programs\Python\Python311\Scripts\mitsuba.EXE`

## Export

- Export manifest: `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/mitsuba_export.json`

## Checks

- Frames: `8`
- XML parsed: `8`
- Command count: `8`
- OBJ shapes: `8`
- Sphere shapes: `2877`
- BSDFs: `144`
- Failures: `0`
- Warnings: `0`

## Frame Samples

| Output | XML Scene | OBJ Shapes | Sphere Shapes | BSDFs |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/scenes/frame_0000.xml` | 1 | 256 | 18 |
| 27 | `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/scenes/frame_0004.xml` | 1 | 256 | 18 |
| 47 | `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/scenes/frame_0007.xml` | 1 | 964 | 18 |

## Next

Render MR2 with the project Mitsuba runtime and compare target gap.
