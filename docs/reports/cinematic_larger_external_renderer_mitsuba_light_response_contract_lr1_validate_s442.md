# S442 Mitsuba Light Response Contract LR1 Validation

Generated UTC: `2026-06-20T12:59:57.783272+00:00`
Validation JSON: `build/shots/s442_mitsuba_light_response_contract_lr1_validation/mitsuba_export_validation.json`
Status: `ready`

## Mitsuba

- Command: `mitsuba`
- Found: `True`
- Required: `False`
- Path: `C:\Users\user\AppData\Local\Programs\Python\Python311\Scripts\mitsuba.EXE`

## Export

- Export manifest: `build/shots/s442_mitsuba_light_response_contract_lr1/mitsuba_export.json`

## Checks

- Frames: `8`
- XML parsed: `8`
- Command count: `8`
- OBJ shapes: `8`
- Sphere shapes: `2926`
- BSDFs: `144`
- Failures: `0`
- Warnings: `0`

## Frame Samples

| Output | XML Scene | OBJ Shapes | Sphere Shapes | BSDFs |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0000.xml` | 1 | 263 | 18 |
| 27 | `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0004.xml` | 1 | 258 | 18 |
| 47 | `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0007.xml` | 1 | 972 | 18 |

## Next

Render LR1 and compare target gap; if it regresses badly, lower radiance scale before trying volume/glint metadata.
