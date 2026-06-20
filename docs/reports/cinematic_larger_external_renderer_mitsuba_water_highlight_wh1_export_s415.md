# S415 Mitsuba Water Highlight WH1 Export

Generated UTC: `2026-06-20T09:55:33.931328+00:00`
Export JSON: `build/shots/s415_mitsuba_water_highlight_wh1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Highlight Emitters

- Emitter limit: `48`
- Radius: `0.035`
- Radiance: `[0.35, 0.45, 0.6]`
- Mask threshold: `8`
- Source luma gate: `120.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `1105`
- Emitters inserted: `150`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Vertices | Candidates | Emitters | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 34 | 15 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s415_mitsuba_water_highlight_wh1/scenes/frame_0000.xml` |
| 27 | 9290 | 26 | 9 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s415_mitsuba_water_highlight_wh1/scenes/frame_0004.xml` |
| 47 | 11152 | 658 | 48 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s415_mitsuba_water_highlight_wh1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WH1 against SS1, S409 SF12_H18, and S401 CR21.
