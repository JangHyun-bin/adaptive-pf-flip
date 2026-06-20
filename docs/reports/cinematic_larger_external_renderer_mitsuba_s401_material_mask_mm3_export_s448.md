# S448 Mitsuba S401 Material Mask MM3 Export

Generated UTC: `2026-06-20T13:48:38.702413+00:00`
Export JSON: `build/shots/s448_mitsuba_s401_material_mask_mm3/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `300`
- Face stride: `1`
- Response alpha: `0.0015`
- Distribution: `ggx`
- IOR: `1.0 -> 1.333`
- Specular reflectance: `[1.0, 1.0, 1.0]`
- Specular transmittance: `[0.88, 0.96, 1.0]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `736`
- Response faces: `736`
- Remainder faces: `156028`
- Water shape replacements: `8`
- Response BSDF insertions: `8`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 37 | 19963 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s448_mitsuba_s401_material_mask_mm3/scenes/frame_0000.xml` |
| 27 | 18576 | 28 | 18548 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s448_mitsuba_s401_material_mask_mm3/scenes/frame_0004.xml` |
| 47 | 22300 | 300 | 22000 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s448_mitsuba_s401_material_mask_mm3/scenes/frame_0007.xml` |

## Next

Validate, render, and compare MM3 as a valid non-emissive masked water specular response.
