# S411 SF12 H18 Split Native Candidate Export

Generated UTC: `2026-06-20T09:18:22.443597+00:00`
Export JSON: `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s411_mitsuba_sf12_channel_dark_card/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`
- Mask source schema: `lsfs_mitsuba_secondary_composite`

## Screen Card

- Card distance: `18.0`
- Card mode: `sprites`
- Card scale: `1.0`
- Mask gain: `0.85`
- Mask blur radius: `0.0`
- Flip Y: `False`
- Reflectance: `0.70,0.84,0.96`
- Sprite limit: `64`
- Sprite threshold: `16`
- Sprite radius pixels: `3.8`
- Sprite radiance: `2.6,3.2,3.8`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `512`
- Screen card mask bytes: `97.65 KB`
- XML scene bytes: `1.53 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/scenes/frame_0000.xml` | `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/secondary_screen_masks/frame_0000.png` | 13291 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 64 |
| 27 | `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/scenes/frame_0004.xml` | `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/secondary_screen_masks/frame_0004.png` | 9220 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 64 |
| 47 | `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/scenes/frame_0007.xml` | `build/shots/s411_mitsuba_sf12_h18_split_native_candidate/secondary_screen_masks/frame_0007.png` | 21546 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 64 |

## Next

Render and compare this split native candidate against S409 SF12_H18, SS1, and S401 CR21.
