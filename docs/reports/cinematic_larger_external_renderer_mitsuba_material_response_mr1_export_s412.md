# S412 Mitsuba Material Response MR1 Export

Generated UTC: `2026-06-20T09:30:45.764221+00:00`
Export JSON: `build/shots/s412_mitsuba_material_response_mr1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Channel mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.45`
- Secondary opacity drop: `0.3`
- Water alpha drop: `0.45`
- Water alpha min: `0.006`
- Highlight key light max radiance: `[0.1, 0.13, 0.17]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `1.36 MB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `32`
- Secondary opacity replacements: `32`
- Key lights inserted: `8`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.011321373456790124 | 0.0016859567901234569 | 0.013288328809616131 | 0.6153437226915235 | 0.7435624817943489 | `[0.011296368101331267, 0.014685278531730647, 0.019203825772263153]` | `build/shots/s412_mitsuba_material_response_mr1/scenes/frame_0000.xml` |
| 27 | 0.005208333333333333 | 0.0010686728395061728 | 0.013548894920511827 | 0.8230410719487329 | 0.8820273812991553 | `[0.007160398087113869, 0.00930851751324803, 0.012172676748093577]` | `build/shots/s412_mitsuba_material_response_mr1/scenes/frame_0004.xml` |
| 47 | 0.0132445987654321 | 0.014924768518518518 | 0.007700000000000001 | 0.55 | 0.7 | `[0.1, 0.13, 0.17]` | `build/shots/s412_mitsuba_material_response_mr1/scenes/frame_0007.xml` |

## Next

Render and compare MR1 against SS1, S409 SF12_H18, and S401 CR21 before promotion.
