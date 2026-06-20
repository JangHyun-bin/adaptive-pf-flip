# S459 Mitsuba Material Tone mt3_secondary_dim Export

Generated UTC: `2026-06-20T14:58:39.276206+00:00`
Export JSON: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt3_secondary_dim/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask source: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.14`
- Secondary opacity drop: `0.09`
- Water alpha drop: `0.04`
- Water alpha min: `0.004`
- Highlight key light max radiance: `[0.012, 0.016, 0.022]`

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
| 0 | 0.0014429012345679012 | 0.0016859567901234569 | 0.013936740338632545 | 0.86 | 0.91 | `[0.0005422256688639008, 0.0007229675584852012, 0.0009940803929171516]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt3_secondary_dim/scenes/frame_0000.xml` |
| 27 | 3.8580246913580246e-05 | 0.0010686728395061728 | 0.013959901770712163 | 0.9962566844919786 | 0.9975935828877005 | `[0.00034369910818146573, 0.0004582654775752876, 0.0006301150316660205]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt3_secondary_dim/scenes/frame_0004.xml` |
| 47 | 0.0009895833333333334 | 0.014924768518518518 | 0.01344 | 0.9039839572192513 | 0.9382754010695187 | `[0.0048000000000000004, 0.0064, 0.0088]` | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt3_secondary_dim/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S459 mt3_secondary_dim.
