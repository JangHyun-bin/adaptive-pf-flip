# S419 Mitsuba Water Mesh Response MMR3 Export

Generated UTC: `2026-06-20T10:37:23.552386+00:00`
Export JSON: `build/shots/s419_mitsuba_water_mesh_response_mmr3_broad/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mesh Response

- Face limit: `0`
- Face stride: `1`
- Y lift: `0.025`
- Radiance: `[1.1, 1.4, 1.8]`
- Reflectance: `[0.0, 0.0, 0.0]`
- Mask threshold: `8`
- Source luma gate: `120.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `2247`
- Mesh response faces: `2247`
- Mesh response vertices: `1983`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Selected Faces | Mesh Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 63 | 63 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s419_mitsuba_water_mesh_response_mmr3_broad/scenes/frame_0000.xml` |
| 27 | 18576 | 55 | 55 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s419_mitsuba_water_mesh_response_mmr3_broad/scenes/frame_0004.xml` |
| 47 | 22300 | 1298 | 1298 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s419_mitsuba_water_mesh_response_mmr3_broad/scenes/frame_0007.xml` |

## Next

Validate, render, and compare MMR3 as a broader masked water-mesh response.
