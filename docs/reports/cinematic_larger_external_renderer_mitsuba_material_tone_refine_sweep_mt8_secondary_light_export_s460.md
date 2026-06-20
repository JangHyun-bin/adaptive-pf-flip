# S460 Mitsuba Material Tone mt8_secondary_light Export

Generated UTC: `2026-06-20T15:02:50.935224+00:00`
Export JSON: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask source: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.08`
- Secondary opacity drop: `0.04`
- Water alpha drop: `0.12`
- Water alpha min: `0.004`
- Highlight key light max radiance: `[0.03, 0.04, 0.054]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `1.40 MB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `32`
- Secondary opacity replacements: `32`
- Key lights inserted: `8`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.013810221015897635 | 0.92 | 0.96 | `[0.0020333462582396277, 0.002711128344319504, 0.00366002326483133]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013879705312136488 | 0.9978609625668449 | 0.9989304812834224 | `[0.0012888716556804963, 0.0017184955409073285, 0.0023199689802248934]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.012320000000000001 | 0.9451336898395721 | 0.9725668449197861 | `[0.018, 0.024, 0.0324]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S460 mt8_secondary_light.
