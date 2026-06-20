# S446 Mitsuba S401 Smooth Glint SG2 Export

Generated UTC: `2026-06-20T13:34:57.357014+00:00`
Export JSON: `build/shots/s446_mitsuba_s401_smooth_glint_sg2/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `24`
- Cluster screen radius: `30.0`
- Radius range: `0.04..0.3`
- Radiance: `[0.65, 0.85, 1.1]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `41`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s446_mitsuba_s401_smooth_glint_sg2/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s446_mitsuba_s401_smooth_glint_sg2/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 16 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s446_mitsuba_s401_smooth_glint_sg2/scenes/frame_0007.xml` |

## Next

Validate, render, and compare SG2 against GL3 for artifact reduction.
