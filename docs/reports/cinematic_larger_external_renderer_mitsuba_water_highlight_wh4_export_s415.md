# S415 Mitsuba Water Highlight WH4 Export

Generated UTC: `2026-06-20T09:58:03.367467+00:00`
Export JSON: `build/shots/s415_mitsuba_water_highlight_wh4_strong/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Highlight Emitters

- Emitter limit: `96`
- Radius: `0.065`
- Radiance: `[1.2, 1.45, 1.75]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Emitters inserted: `145`
- XML scene bytes: `1.39 MB`

## Frame Samples

| Output | Vertices | Candidates | Emitters | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 7 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s415_mitsuba_water_highlight_wh4_strong/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 5 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s415_mitsuba_water_highlight_wh4_strong/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 81 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s415_mitsuba_water_highlight_wh4_strong/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WH4 as a stronger high-luma water-highlight candidate.
