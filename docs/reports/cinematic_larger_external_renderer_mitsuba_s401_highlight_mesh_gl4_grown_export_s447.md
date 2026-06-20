# S447 Mitsuba S401 Highlight Mesh GL4 Grown Export

Generated UTC: `2026-06-20T13:40:45.810731+00:00`
Export JSON: `build/shots/s447_mitsuba_s401_highlight_mesh_gl4_grown/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mesh Response

- Face limit: `300`
- Face grow steps: `1`
- Face grow max faces: `1600`
- Face stride: `1`
- Y lift: `0.025`
- BSDF mode: `diffuse`
- Rough alpha: `0.006`
- IOR: `1.0 -> 1.333`
- Radiance: `[0.75, 0.95, 1.2]`
- Reflectance: `[0.0, 0.0, 0.0]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `736`
- Grown response faces: `3046`
- Mesh response faces: `3046`
- Mesh response vertices: `2110`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Selected Faces | Mesh Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 219 | 219 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s447_mitsuba_s401_highlight_mesh_gl4_grown/scenes/frame_0000.xml` |
| 27 | 18576 | 126 | 126 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s447_mitsuba_s401_highlight_mesh_gl4_grown/scenes/frame_0004.xml` |
| 47 | 22300 | 1110 | 1110 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s447_mitsuba_s401_highlight_mesh_gl4_grown/scenes/frame_0007.xml` |

## Next

Validate, render, and compare GL4 grown response against GL3 and smooth disk emitters.
