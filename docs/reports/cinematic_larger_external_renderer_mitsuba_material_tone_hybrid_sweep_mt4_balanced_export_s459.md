# S459 Mitsuba Material Tone mt4_balanced Export

Generated UTC: `2026-06-20T14:58:51.110029+00:00`
Export JSON: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced/mitsuba_export.json`
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
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.013810221015897635 | 0.9 | 0.94 | `[0.002349644565076904, 0.003083908491663436, 0.004111877988884581]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013879705312136488 | 0.9973262032085561 | 0.9983957219251337 | `[0.0014893628021196848, 0.0019547886777820864, 0.002606384903709448]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.012320000000000001 | 0.9314171122994652 | 0.9588502673796792 | `[0.020800000000000003, 0.0273, 0.0364]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S459 mt4_balanced.
