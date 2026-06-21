# S605 Scene Depth Native Material Split MS8 Peak Balance Full48 Validation

Generated UTC: `2026-06-21T00:06:54.308758+00:00`
Validation JSON: `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48_validation/validation.json`
Status: `ready`

## Mitsuba

- Command: `mitsuba`
- Found: `True`
- Required: `False`
- Path: `C:\Users\user\AppData\Local\Programs\Python\Python311\Scripts\mitsuba.EXE`

## Export

- Export manifest: `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/mitsuba_export.json`

## Checks

- Frames: `48`
- XML parsed: `48`
- Command count: `48`
- OBJ shapes: `144`
- Sphere shapes: `9216`
- BSDFs: `576`
- Failures: `0`
- Warnings: `0`

## Frame Samples

| Output | XML Scene | OBJ Shapes | Sphere Shapes | BSDFs |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/scenes/frame_0000.xml` | 3 | 192 | 12 |
| 24 | `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/scenes/frame_0024.xml` | 3 | 192 | 12 |
| 47 | `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/scenes/frame_0047.xml` | 3 | 192 | 12 |

## Next

Render this validated peak-balanced full48 localized material split through Mitsuba SPP4 and compare against S602/S604.
