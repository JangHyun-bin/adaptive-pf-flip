# S450 Mitsuba PM3 Soft Patch HY3 Export

Generated UTC: `2026-06-20T14:06:12.268311+00:00`
Export JSON: `build/shots/s450_mitsuba_pm3_soft_patch_hy3/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s449_mitsuba_s401_per_face_material_pm3/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `24`
- Cluster screen radius: `30.0`
- Radius range: `0.04..0.3`
- Radiance: `[0.45, 0.6, 0.82]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `41`
- XML scene bytes: `1.39 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s450_mitsuba_pm3_soft_patch_hy3/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s450_mitsuba_pm3_soft_patch_hy3/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 16 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s450_mitsuba_pm3_soft_patch_hy3/scenes/frame_0007.xml` |

## Next

Validate, render, and compare HY3 as a sharper PM3 material plus patch hybrid.
