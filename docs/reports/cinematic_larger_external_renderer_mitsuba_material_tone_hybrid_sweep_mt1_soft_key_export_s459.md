# S459 Mitsuba Material Tone mt1_soft_key Export

Generated UTC: `2026-06-20T14:58:15.296796+00:00`
Export JSON: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask source: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.08`
- Secondary opacity drop: `0.05`
- Water alpha drop: `0.08`
- Water alpha min: `0.004`
- Highlight key light max radiance: `[0.025, 0.032, 0.042]`

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
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.01387348067726509 | 0.92 | 0.95 | `[0.0014120460126664084, 0.0018074188962130028, 0.002372237301279566]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013919803541424325 | 0.9978609625668449 | 0.9986631016042781 | `[0.0008950497608892336, 0.001145663693938219, 0.0015036835982939125]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.01288 | 0.9451336898395721 | 0.9657085561497326 | `[0.0125, 0.016, 0.021]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S459 mt1_soft_key.
