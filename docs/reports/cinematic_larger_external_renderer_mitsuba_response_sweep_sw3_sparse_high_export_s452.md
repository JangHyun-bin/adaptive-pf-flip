# S452 Mitsuba Response Sweep sw3_sparse_high Export

Generated UTC: `2026-06-20T14:16:53.563375+00:00`
Export JSON: `build/shots/s452_mitsuba_response_sweep/sw3_sparse_high/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s449_mitsuba_s401_per_face_material_pm3/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `10`
- Cluster screen radius: `34.0`
- Radius range: `0.055..0.34`
- Radiance: `[0.95, 1.18, 1.52]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `28`
- XML scene bytes: `1.38 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s452_mitsuba_response_sweep/sw3_sparse_high/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 2 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s452_mitsuba_response_sweep/sw3_sparse_high/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 10 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s452_mitsuba_response_sweep/sw3_sparse_high/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S452 sw3_sparse_high.
