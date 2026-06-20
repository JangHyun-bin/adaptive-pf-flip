# S445 Mitsuba S401 Dark Primary Mesh DP1 Export

Generated UTC: `2026-06-20T13:29:02.348354+00:00`
Export JSON: `build/shots/s445_mitsuba_s401_dark_primary_mesh_dp1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_dark_secondary_mask_source/source_response_mask_source_summary.json`

## Water Mesh Response

- Face limit: `0`
- Face stride: `1`
- Y lift: `0.018`
- BSDF mode: `diffuse`
- Rough alpha: `0.006`
- IOR: `1.0 -> 1.333`
- Radiance: `[0.0, 0.0, 0.0]`
- Reflectance: `[0.015, 0.025, 0.04]`
- Mask threshold: `8`
- Source luma gate: `0.0..90.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `142649`
- Mesh response faces: `142649`
- Mesh response vertices: `75955`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Selected Faces | Mesh Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 18822 | 18822 | `build/shots/s423_mitsuba_s401_cr21_dark_secondary_mask_source/masks/frame_0000.png` | `build/shots/s445_mitsuba_s401_dark_primary_mesh_dp1/scenes/frame_0000.xml` |
| 27 | 18576 | 17188 | 17188 | `build/shots/s423_mitsuba_s401_cr21_dark_secondary_mask_source/masks/frame_0004.png` | `build/shots/s445_mitsuba_s401_dark_primary_mesh_dp1/scenes/frame_0004.xml` |
| 47 | 22300 | 19034 | 19034 | `build/shots/s423_mitsuba_s401_cr21_dark_secondary_mask_source/masks/frame_0007.png` | `build/shots/s445_mitsuba_s401_dark_primary_mesh_dp1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare DP1 as a direct water-surface dark-primary response.
