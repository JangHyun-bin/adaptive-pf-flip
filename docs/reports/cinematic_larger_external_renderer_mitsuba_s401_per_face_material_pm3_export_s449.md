# S449 Mitsuba S401 Per-Face Material PM3 Export

Generated UTC: `2026-06-20T14:00:44.237138+00:00`
Export JSON: `build/shots/s449_mitsuba_s401_per_face_material_pm3/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `260`
- Face stride: `1`
- Response alpha: `0.002`
- Response bins: `3`
- Distribution: `ggx`
- IOR: `1.0 -> 1.55`
- Specular reflectance: `None`
- Specular transmittance: `None`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `656`
- Response faces: `656`
- Remainder faces: `156108`
- Water shape replacements: `8`
- Response BSDF insertions: `8`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 37 | 19963 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s449_mitsuba_s401_per_face_material_pm3/scenes/frame_0000.xml` |
| 27 | 18576 | 28 | 18548 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s449_mitsuba_s401_per_face_material_pm3/scenes/frame_0004.xml` |
| 47 | 22300 | 260 | 22040 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s449_mitsuba_s401_per_face_material_pm3/scenes/frame_0007.xml` |

## Next

Validate, render, and compare PM3 as a sharper lifted per-face material response map.
