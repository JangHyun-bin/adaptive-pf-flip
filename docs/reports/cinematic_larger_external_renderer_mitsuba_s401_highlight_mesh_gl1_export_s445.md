# S445 Mitsuba S401 Highlight Mesh GL1 Export

Generated UTC: `2026-06-20T13:29:01.472326+00:00`
Export JSON: `build/shots/s445_mitsuba_s401_highlight_mesh_gl1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mesh Response

- Face limit: `0`
- Face stride: `1`
- Y lift: `0.025`
- BSDF mode: `diffuse`
- Rough alpha: `0.006`
- IOR: `1.0 -> 1.333`
- Radiance: `[0.55, 0.72, 0.95]`
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
| 0 | 20000 | 63 | 63 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s445_mitsuba_s401_highlight_mesh_gl1/scenes/frame_0000.xml` |
| 27 | 18576 | 55 | 55 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s445_mitsuba_s401_highlight_mesh_gl1/scenes/frame_0004.xml` |
| 47 | 22300 | 1298 | 1298 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s445_mitsuba_s401_highlight_mesh_gl1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare GL1 as a direct water-surface highlight response.
