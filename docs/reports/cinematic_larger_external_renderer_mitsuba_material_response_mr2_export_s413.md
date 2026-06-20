# S413 Mitsuba Material Response MR2 Export

Generated UTC: `2026-06-20T09:35:26.089301+00:00`
Export JSON: `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Channel mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.35`
- Secondary opacity drop: `0.2`
- Water alpha drop: `0.0`
- Water alpha min: `0.006`
- Highlight key light max radiance: `[0.1, 0.13, 0.17]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `1.36 MB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `32`
- Secondary opacity replacements: `32`
- Key lights inserted: `0`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.011321373456790124 | 0.0016859567901234569 | 0.014 | 0.7008228954267405 | 0.829041654529566 | `[0.0, 0.0, 0.0]` | `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/scenes/frame_0000.xml` |
| 27 | 0.005208333333333333 | 0.0010686728395061728 | 0.014 | 0.8623652781823479 | 0.9213515875327701 | `[0.0, 0.0, 0.0]` | `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/scenes/frame_0004.xml` |
| 47 | 0.0132445987654321 | 0.014924768518518518 | 0.014 | 0.65 | 0.8 | `[0.0, 0.0, 0.0]` | `build/shots/s413_mitsuba_material_response_mr2_secondary_attenuation/scenes/frame_0007.xml` |

## Next

Render and compare MR2 to see whether secondary material attenuation alone improves over SS1.
