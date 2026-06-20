# S415 Mitsuba Water Highlight WH3 Export

Generated UTC: `2026-06-20T09:56:46.762073+00:00`
Export JSON: `build/shots/s415_mitsuba_water_highlight_wh3_compact/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Highlight Emitters

- Emitter limit: `48`
- Radius: `0.045`
- Radiance: `[0.75, 0.9, 1.1]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Emitters inserted: `98`
- XML scene bytes: `1.38 MB`

## Frame Samples

| Output | Vertices | Candidates | Emitters | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 6 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s415_mitsuba_water_highlight_wh3_compact/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 3 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s415_mitsuba_water_highlight_wh3_compact/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 48 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s415_mitsuba_water_highlight_wh3_compact/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WH3 as a compact high-luma water-highlight candidate.
