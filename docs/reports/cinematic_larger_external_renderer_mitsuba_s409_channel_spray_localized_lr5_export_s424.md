# S424 Mitsuba S409 Channel Spray Localized LR5 Export

Generated UTC: `2026-06-20T11:31:45.207434+00:00`
Export JSON: `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/source_response_mask_source_summary.json`

## Localized Response

- Channels: `['spray']`
- Mask threshold: `8`
- Mask sample radius: `4`
- Source luma gate: `0.0..95.0`
- Localized reflectance scale: `0.35`
- Localized opacity scale: `0.6`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Localized shapes: `916`
- Localized disks: `458`
- Localized spheres: `458`
- Localized BSDFs: `16`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Mask | Localized Shapes | Disks | Spheres | Localized BSDFs | XML Scene |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 0 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0000.png` | 152 | 76 | 76 | 2 | `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5/scenes/frame_0000.xml` |
| 27 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0004.png` | 46 | 23 | 23 | 2 | `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5/scenes/frame_0004.xml` |
| 47 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0007.png` | 328 | 164 | 164 | 2 | `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5/scenes/frame_0007.xml` |

## Next

Render and compare this spray-only localized response against SS1, S409, and S401 before deciding whether secondary attenuation remains a viable native target.
