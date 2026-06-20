# S452 Mitsuba Response Sweep sw1_compact_mid Export

Generated UTC: `2026-06-20T14:16:29.560306+00:00`
Export JSON: `build/shots/s452_mitsuba_response_sweep/sw1_compact_mid/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s449_mitsuba_s401_per_face_material_pm3/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `18`
- Cluster screen radius: `26.0`
- Radius range: `0.04..0.28`
- Radiance: `[0.62, 0.8, 1.08]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `46`
- XML scene bytes: `1.39 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0000.png` | `build/shots/s452_mitsuba_response_sweep/sw1_compact_mid/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 3 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0004.png` | `build/shots/s452_mitsuba_response_sweep/sw1_compact_mid/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 18 | `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/masks/frame_0007.png` | `build/shots/s452_mitsuba_response_sweep/sw1_compact_mid/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S452 sw1_compact_mid.
