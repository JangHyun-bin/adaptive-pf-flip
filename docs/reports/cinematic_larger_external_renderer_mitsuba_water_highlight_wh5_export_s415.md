# S415 Mitsuba Water Highlight WH5 Export

Generated UTC: `2026-06-20T09:58:03.353660+00:00`
Export JSON: `build/shots/s415_mitsuba_water_highlight_wh5_hotcore/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Highlight Emitters

- Emitter limit: `64`
- Radius: `0.075`
- Radiance: `[1.6, 1.85, 2.15]`
- Mask threshold: `8`
- Source luma gate: `155.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `9`
- Emitters inserted: `6`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Vertices | Candidates | Emitters | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 0 | 0 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s415_mitsuba_water_highlight_wh5_hotcore/scenes/frame_0000.xml` |
| 27 | 9290 | 0 | 0 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s415_mitsuba_water_highlight_wh5_hotcore/scenes/frame_0004.xml` |
| 47 | 11152 | 9 | 6 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s415_mitsuba_water_highlight_wh5_hotcore/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WH5 as a hot-core water-highlight candidate.
