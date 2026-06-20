# S446 Mitsuba S401 Smooth Glint SG1 Export

Generated UTC: `2026-06-20T13:34:57.221424+00:00`
Export JSON: `build/shots/s446_mitsuba_s401_smooth_glint_sg1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `16`
- Cluster screen radius: `42.0`
- Radius range: `0.05..0.4`
- Radiance: `[0.95, 1.15, 1.45]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `31`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s446_mitsuba_s401_smooth_glint_sg1/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 2 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s446_mitsuba_s401_smooth_glint_sg1/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 10 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s446_mitsuba_s401_smooth_glint_sg1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare SG1 against GL3 for artifact reduction.
