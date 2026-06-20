# S414 Mitsuba Localized Secondary LR4 Export

Generated UTC: `2026-06-20T09:47:56.224871+00:00`
Export JSON: `build/shots/s414_mitsuba_localized_secondary_lr4_luma85/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`

## Localized Response

- Channels: `['foam', 'spray']`
- Mask threshold: `8`
- Mask sample radius: `4`
- Source luma gate: `0.0..85.0`
- Localized reflectance scale: `0.4`
- Localized opacity scale: `0.65`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Localized shapes: `202`
- Localized disks: `101`
- Localized spheres: `101`
- Localized BSDFs: `20`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Mask | Localized Shapes | Disks | Spheres | Localized BSDFs | XML Scene |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 0 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0000.png` | 110 | 55 | 55 | 4 | `build/shots/s414_mitsuba_localized_secondary_lr4_luma85/scenes/frame_0000.xml` |
| 27 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0004.png` | 2 | 1 | 1 | 2 | `build/shots/s414_mitsuba_localized_secondary_lr4_luma85/scenes/frame_0004.xml` |
| 47 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0007.png` | 38 | 19 | 19 | 2 | `build/shots/s414_mitsuba_localized_secondary_lr4_luma85/scenes/frame_0007.xml` |

## Next

Validate, render, and compare LR4 against LR3 and previous native candidates.
