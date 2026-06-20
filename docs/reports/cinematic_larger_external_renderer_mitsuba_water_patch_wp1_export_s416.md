# S416 Mitsuba Water Patch WP1 Export

Generated UTC: `2026-06-20T10:03:23.491018+00:00`
Export JSON: `build/shots/s416_mitsuba_water_patch_wp1_broad/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Highlight Emitters

- Emitter limit: `48`
- Radius: `0.14`
- Radiance: `[0.8, 1.0, 1.25]`
- Mask threshold: `8`
- Source luma gate: `120.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `1105`
- Emitters inserted: `101`
- XML scene bytes: `1.38 MB`

## Frame Samples

| Output | Vertices | Candidates | Emitters | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 34 | 11 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s416_mitsuba_water_patch_wp1_broad/scenes/frame_0000.xml` |
| 27 | 9290 | 26 | 6 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s416_mitsuba_water_patch_wp1_broad/scenes/frame_0004.xml` |
| 47 | 11152 | 658 | 36 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s416_mitsuba_water_patch_wp1_broad/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WP1 as a broader water-highlight patch candidate.
