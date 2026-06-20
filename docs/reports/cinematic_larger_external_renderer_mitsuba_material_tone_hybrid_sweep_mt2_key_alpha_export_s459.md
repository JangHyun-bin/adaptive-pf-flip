# S459 Mitsuba Material Tone mt2_key_alpha Export

Generated UTC: `2026-06-20T14:58:27.550244+00:00`
Export JSON: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt2_key_alpha/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask source: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.0`
- Secondary opacity drop: `0.0`
- Water alpha drop: `0.1`
- Water alpha min: `0.004`
- Highlight key light max radiance: `[0.035, 0.045, 0.06]`

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
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.013841850846581362 | 1.0 | 1.0 | `[0.0029652966265994577, 0.0038125242341993026, 0.00508336564559907]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt2_key_alpha/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013899754426780406 | 1.0 | 1.0 | `[0.0018796044978673908, 0.002416634354400931, 0.0032221791392012407]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt2_key_alpha/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.0126 | 1.0 | 1.0 | `[0.026250000000000002, 0.03375, 0.045]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt2_key_alpha/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S459 mt2_key_alpha.
