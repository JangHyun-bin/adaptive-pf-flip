# S518 Mitsuba Material Tone mt11_soft_water_bright Export

Generated UTC: `2026-06-20T19:45:46.939789+00:00`
Export JSON: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt11_soft_water_bright/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.0`
- Secondary opacity drop: `0.0`
- Water alpha drop: `0.45`
- Water alpha min: `0.0025`
- Highlight key light max radiance: `[0.08, 0.11, 0.16]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `322.08 KB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `16`
- Secondary opacity replacements: `16`
- Key lights inserted: `8`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.011321373456790124 | 0.0016859567901234569 | 0.023729158588600235 | 1.0 | 1.0 | `[0.007229675584852011, 0.009940803929171516, 0.014459351169704022]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt11_soft_water_bright/scenes/frame_0000.xml` |
| 27 | 0.005208333333333333 | 0.0010686728395061728 | 0.02419445521519969 | 1.0 | 1.0 | `[0.004582654775752876, 0.006301150316660205, 0.009165309551505752]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt11_soft_water_bright/scenes/frame_0004.xml` |
| 47 | 0.0132445987654321 | 0.014924768518518518 | 0.013750000000000002 | 1.0 | 1.0 | `[0.064, 0.08800000000000001, 0.128]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt11_soft_water_bright/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S518 mt11_soft_water_bright.
