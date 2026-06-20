# S414 Mitsuba Localized Secondary LR3 Export

Generated UTC: `2026-06-20T09:46:43.835301+00:00`
Export JSON: `build/shots/s414_mitsuba_localized_secondary_lr3_luma95/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`

## Localized Response

- Channels: `['foam', 'spray']`
- Mask threshold: `8`
- Mask sample radius: `4`
- Source luma gate: `0.0..95.0`
- Localized reflectance scale: `0.45`
- Localized opacity scale: `0.7`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Localized shapes: `980`
- Localized disks: `490`
- Localized spheres: `490`
- Localized BSDFs: `30`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Mask | Localized Shapes | Disks | Spheres | Localized BSDFs | XML Scene |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 0 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0000.png` | 188 | 94 | 94 | 4 | `build/shots/s414_mitsuba_localized_secondary_lr3_luma95/scenes/frame_0000.xml` |
| 27 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0004.png` | 46 | 23 | 23 | 2 | `build/shots/s414_mitsuba_localized_secondary_lr3_luma95/scenes/frame_0004.xml` |
| 47 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0007.png` | 332 | 166 | 166 | 4 | `build/shots/s414_mitsuba_localized_secondary_lr3_luma95/scenes/frame_0007.xml` |

## Next

Validate, render, and compare LR3 against LR1, MR2, and previous native candidates.
