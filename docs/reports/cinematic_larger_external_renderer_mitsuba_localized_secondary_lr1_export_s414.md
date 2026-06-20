# S414 Mitsuba Localized Secondary LR1 Export

Generated UTC: `2026-06-20T09:43:46.215817+00:00`
Export JSON: `build/shots/s414_mitsuba_localized_secondary_lr1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`

## Localized Response

- Channels: `['foam', 'spray']`
- Mask threshold: `8`
- Mask sample radius: `4`
- Localized reflectance scale: `0.45`
- Localized opacity scale: `0.7`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Localized shapes: `5200`
- Localized disks: `2600`
- Localized spheres: `2600`
- Localized BSDFs: `32`
- XML scene bytes: `1.41 MB`

## Frame Samples

| Output | Mask | Localized Shapes | Disks | Spheres | Localized BSDFs | XML Scene |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 0 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0000.png` | 460 | 230 | 230 | 4 | `build/shots/s414_mitsuba_localized_secondary_lr1/scenes/frame_0000.xml` |
| 27 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0004.png` | 460 | 230 | 230 | 4 | `build/shots/s414_mitsuba_localized_secondary_lr1/scenes/frame_0004.xml` |
| 47 | `build/shots/s410_mitsuba_sf12_channel_band_mask_source/masks/frame_0007.png` | 1760 | 880 | 880 | 4 | `build/shots/s414_mitsuba_localized_secondary_lr1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare LR1 against SS1, MR2, S409 SF12_H18, and S401 CR21.
