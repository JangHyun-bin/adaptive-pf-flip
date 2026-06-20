# S419 Mitsuba Water Mesh Response MMR5 Export

Generated UTC: `2026-06-20T10:39:19.291260+00:00`
Export JSON: `build/shots/s419_mitsuba_water_mesh_response_mmr5_reflect/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mesh Response

- Face limit: `0`
- Face stride: `1`
- Y lift: `0.025`
- Radiance: `[0.45, 0.6, 0.78]`
- Reflectance: `[0.55, 0.68, 0.82]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `1242`
- Mesh response faces: `1242`
- Mesh response vertices: `1433`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Selected Faces | Mesh Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 37 | 37 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s419_mitsuba_water_mesh_response_mmr5_reflect/scenes/frame_0000.xml` |
| 27 | 18576 | 28 | 28 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s419_mitsuba_water_mesh_response_mmr5_reflect/scenes/frame_0004.xml` |
| 47 | 22300 | 730 | 730 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s419_mitsuba_water_mesh_response_mmr5_reflect/scenes/frame_0007.xml` |

## Next

Validate, render, and compare MMR5 as reversed-face reflective water-mesh response.
