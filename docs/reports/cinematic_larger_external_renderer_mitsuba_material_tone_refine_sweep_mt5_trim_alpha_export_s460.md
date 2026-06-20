# S460 Mitsuba Material Tone mt5_trim_alpha Export

Generated UTC: `2026-06-20T15:02:16.247437+00:00`
Export JSON: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt5_trim_alpha/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask source: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.1`
- Secondary opacity drop: `0.06`
- Water alpha drop: `0.1`
- Water alpha min: `0.004`
- Highlight key light max radiance: `[0.032, 0.042, 0.056]`

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
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.013841850846581362 | 0.9 | 0.94 | `[0.002168902675455603, 0.002846684761535479, 0.0037955796820473052]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt5_trim_alpha/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013899754426780406 | 0.9973262032085561 | 0.9983957219251337 | `[0.0013747964327258627, 0.001804420317952695, 0.0024058937572702596]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt5_trim_alpha/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.0126 | 0.9314171122994652 | 0.9588502673796792 | `[0.0192, 0.0252, 0.0336]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt5_trim_alpha/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S460 mt5_trim_alpha.
