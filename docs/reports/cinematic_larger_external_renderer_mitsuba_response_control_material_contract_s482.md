# S482 Mitsuba Response Control Material Contract

Generated UTC: `2026-06-20T16:48:37.005303+00:00`
Export JSON: `build/shots/s482_mitsuba_response_control_material_contract/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
- Material response contract: `build/shots/s479_mitsuba_response_control_handoff/material_response_contract.json`

## Material Response Contract

- Face limit: `700`
- Face grow steps: `1`
- Face grow max faces: `900`
- Face stride: `1`
- BBox pad: `4.0`
- Blur pad scale: `1.0`
- BSDF mode: `diffuse`
- Reflectance base: `[0.55, 0.72, 1.0]`
- Radiance base: `[0.35, 0.48, 0.7]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Contract frames matched: `2`
- Contract frames missing ignored: `6`
- Controls consumed: `2`
- Candidate faces: `1400`
- Mesh response faces: `1800`
- Mesh response vertices: `1083`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Controls | Mesh Faces | Ignored | XML Scene |
| ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0 | `True` | `build/shots/s482_mitsuba_response_control_material_contract/scenes/frame_0000.xml` |
| 27 | 0 | 0 | `True` | `build/shots/s482_mitsuba_response_control_material_contract/scenes/frame_0004.xml` |
| 47 | 1 | 900 | `False` | `build/shots/s482_mitsuba_response_control_material_contract/scenes/frame_0007.xml` |

## Next

Validate, render, and compare this light-plus-material native candidate against S481 light-only and the S478 p4 proxy gate.
