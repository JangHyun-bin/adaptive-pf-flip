# S450 Mitsuba PM3 Soft Patch HY1 Export

Generated UTC: `2026-06-20T14:04:26.193426+00:00`
Export JSON: `build/shots/s450_mitsuba_pm3_soft_patch_hy1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s449_mitsuba_s401_per_face_material_pm3/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `12`
- Cluster screen radius: `58.0`
- Radius range: `0.12..0.52`
- Radiance: `[0.08, 0.11, 0.16]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `21`
- XML scene bytes: `1.38 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s450_mitsuba_pm3_soft_patch_hy1/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 2 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s450_mitsuba_pm3_soft_patch_hy1/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 7 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s450_mitsuba_pm3_soft_patch_hy1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare HY1 as a low-energy PM3 material plus softened patch hybrid.
