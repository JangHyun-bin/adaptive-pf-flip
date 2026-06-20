# S518 Mitsuba Material Tone mt10_dim_secondary_strong_key Export

Generated UTC: `2026-06-20T19:45:38.272351+00:00`
Export JSON: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt10_dim_secondary_strong_key/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.18`
- Secondary opacity drop: `0.12`
- Water alpha drop: `0.25`
- Water alpha min: `0.0035`
- Highlight key light max radiance: `[0.16, 0.2, 0.28]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `322.37 KB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `16`
- Secondary opacity replacements: `16`
- Key lights inserted: `8`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.011321373456790124 | 0.0016859567901234569 | 0.024293976993666797 | 0.8461374890766094 | 0.8974249927177396 | `[0.022592736202662535, 0.028240920253328167, 0.03953728835465944]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt10_dim_secondary_strong_key/scenes/frame_0000.xml` |
| 27 | 0.005208333333333333 | 0.0010686728395061728 | 0.024552475119555384 | 0.9292164287794932 | 0.9528109525196621 | `[0.014320796174227738, 0.01790099521778467, 0.02506139330489854]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt10_dim_secondary_strong_key/scenes/frame_0004.xml` |
| 47 | 0.0132445987654321 | 0.014924768518518518 | 0.018750000000000003 | 0.8200000000000001 | 0.88 | `[0.2, 0.25, 0.35000000000000003]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt10_dim_secondary_strong_key/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S518 mt10_dim_secondary_strong_key.
