# S518 Mitsuba Material Tone mt9_sharp_key Export

Generated UTC: `2026-06-20T19:45:29.197969+00:00`
Export JSON: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt9_sharp_key/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.04`
- Secondary opacity drop: `0.02`
- Water alpha drop: `0.35`
- Water alpha min: `0.003`
- Highlight key light max radiance: `[0.12, 0.16, 0.22]`

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
| 0 | 0.011321373456790124 | 0.0016859567901234569 | 0.024011567791133517 | 0.9658083309059132 | 0.9829041654529566 | `[0.014911205893757273, 0.01988160785834303, 0.027337210805221668]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt9_sharp_key/scenes/frame_0000.xml` |
| 27 | 0.005208333333333333 | 0.0010686728395061728 | 0.02437346516737754 | 0.984270317506554 | 0.9921351587532771 | `[0.009451725474990307, 0.01260230063332041, 0.017328163370815563]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt9_sharp_key/scenes/frame_0004.xml` |
| 47 | 0.0132445987654321 | 0.014924768518518518 | 0.01625 | 0.96 | 0.98 | `[0.132, 0.17600000000000002, 0.24200000000000002]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt9_sharp_key/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S518 mt9_sharp_key.
