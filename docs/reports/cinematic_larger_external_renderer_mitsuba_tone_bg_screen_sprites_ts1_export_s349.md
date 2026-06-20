# S349 Mitsuba Tone Background Screen Sprites TS1 Export

Generated UTC: `2026-06-20T02:01:55.881281+00:00`
Export JSON: `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s348_mitsuba_tone_bg_tb6/mitsuba_export.json`
- Depth-aware composite: `build/shots/s341_mitsuba_depth_aware_composite_c3/depth_aware_secondary_composite_summary.json`

## Screen Card

- Card distance: `18.0`
- Card mode: `sprites`
- Card scale: `1.0`
- Mask gain: `8.0`
- Mask blur radius: `2.0`
- Flip Y: `False`
- Reflectance: `0.70,0.84,0.96`
- Sprite limit: `1024`
- Sprite threshold: `18`
- Sprite radius pixels: `11.0`
- Sprite radiance: `42,52,64`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `8192`
- Screen card mask bytes: `73.76 KB`
- XML scene bytes: `4.56 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/scenes/frame_0000.xml` | `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/secondary_screen_masks/frame_0000.png` | 10564 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 1024 |
| 27 | `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/scenes/frame_0004.xml` | `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/secondary_screen_masks/frame_0004.png` | 6750 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 1024 |
| 47 | `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/scenes/frame_0007.xml` | `build/shots/s349_mitsuba_tone_bg_screen_sprites_ts1/secondary_screen_masks/frame_0007.png` | 16622 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 1024 |

## Next

Render TB6 with SC4-style screen sprites and compare against the S344 C3 bridge gate.
