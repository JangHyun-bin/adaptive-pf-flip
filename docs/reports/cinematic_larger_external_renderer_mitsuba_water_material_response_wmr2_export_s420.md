# S420 Mitsuba Water Material Response WMR2 Export

Generated UTC: `2026-06-20T10:52:29.721968+00:00`
Export JSON: `build/shots/s420_mitsuba_water_material_response_wmr2_limited/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mesh Response

- Face limit: `700`
- Face stride: `1`
- Y lift: `0.025`
- Radiance: `[0.0, 0.0, 0.0]`
- Reflectance: `[0.85, 0.93, 1.0]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `1212`
- Mesh response faces: `1212`
- Mesh response vertices: `1419`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Selected Faces | Mesh Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 37 | 37 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s420_mitsuba_water_material_response_wmr2_limited/scenes/frame_0000.xml` |
| 27 | 18576 | 28 | 28 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s420_mitsuba_water_material_response_wmr2_limited/scenes/frame_0004.xml` |
| 47 | 22300 | 700 | 700 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s420_mitsuba_water_material_response_wmr2_limited/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WMR2 as a stronger reflectance-only water mesh material response.
