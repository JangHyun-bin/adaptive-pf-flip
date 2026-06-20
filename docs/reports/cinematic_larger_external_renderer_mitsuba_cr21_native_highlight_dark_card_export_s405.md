# S405 CR21 Native Highlight Dark Card Export

Generated UTC: `2026-06-20T08:34:47.407569+00:00`
Export JSON: `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s405_mitsuba_cr21_native_highlight_sprites/mitsuba_export.json`
- Mask source: `build/shots/s405_mitsuba_cr21_dark_secondary_mask_source/source_response_mask_source_summary.json`
- Mask source schema: `lsfs_mitsuba_secondary_composite`

## Screen Card

- Card distance: `18.0`
- Card mode: `rectangle`
- Card scale: `1.0`
- Mask gain: `0.42`
- Mask blur radius: `1.2`
- Flip Y: `False`
- Reflectance: `0.02,0.025,0.03`
- Sprite limit: `0`
- Sprite threshold: `16`
- Sprite radius pixels: `5.0`
- Sprite radiance: `4.0,5.5,7.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `0`
- Screen card mask bytes: `74.39 KB`
- XML scene bytes: `1.60 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/scenes/frame_0000.xml` | `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/secondary_screen_masks/frame_0000.png` | 10287 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 27 | `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/scenes/frame_0004.xml` | `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/secondary_screen_masks/frame_0004.png` | 7135 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 47 | `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/scenes/frame_0007.xml` | `build/shots/s405_mitsuba_cr21_native_highlight_dark_card/secondary_screen_masks/frame_0007.png` | 16022 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |

## Next

Render and compare NHD1 against SS1 and the CR21 profile.
