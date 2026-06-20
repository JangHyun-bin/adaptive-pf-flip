# S460 Mitsuba Material Tone mt6_trim_key Export

Generated UTC: `2026-06-20T15:02:27.804000+00:00`
Export JSON: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt6_trim_key/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask source: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.1`
- Secondary opacity drop: `0.06`
- Water alpha drop: `0.12`
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
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.013810221015897635 | 0.9 | 0.94 | `[0.001988160785834303, 0.002609461031407523, 0.0034792813752100304]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt6_trim_key/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013879705312136488 | 0.9973262032085561 | 0.9983957219251337 | `[0.001260230063332041, 0.001654051958123304, 0.002205402610831072]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt6_trim_key/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.012320000000000001 | 0.9314171122994652 | 0.9588502673796792 | `[0.0176, 0.023100000000000002, 0.030800000000000004]` | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt6_trim_key/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S460 mt6_trim_key.
