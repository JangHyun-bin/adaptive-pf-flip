# S346 Mitsuba Secondary Screen Card SC1 Export

Generated UTC: `2026-06-20T01:32:24.781254+00:00`
Export JSON: `build/shots/s346_mitsuba_secondary_screen_card_sc1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s345_mitsuba_secondary_mist_billboard_mb2/mitsuba_export.json`
- Depth-aware composite: `build/shots/s341_mitsuba_depth_aware_composite_c3/depth_aware_secondary_composite_summary.json`

## Screen Card

- Card distance: `18.0`
- Card scale: `1.0`
- Mask gain: `0.6`
- Mask blur radius: `1.5`
- Flip Y: `False`
- Reflectance: `0.7,0.84,0.96`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen card mask bytes: `61.53 KB`
- XML scene bytes: `1.99 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents |
| ---: | --- | --- | ---: | --- | --- |
| 0 | `build/shots/s346_mitsuba_secondary_screen_card_sc1/scenes/frame_0000.xml` | `build/shots/s346_mitsuba_secondary_screen_card_sc1/secondary_screen_masks/frame_0000.png` | 8792 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` |
| 27 | `build/shots/s346_mitsuba_secondary_screen_card_sc1/scenes/frame_0004.xml` | `build/shots/s346_mitsuba_secondary_screen_card_sc1/secondary_screen_masks/frame_0004.png` | 5846 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` |
| 47 | `build/shots/s346_mitsuba_secondary_screen_card_sc1/scenes/frame_0007.xml` | `build/shots/s346_mitsuba_secondary_screen_card_sc1/secondary_screen_masks/frame_0007.png` | 13285 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` |

## Next

Render this first secondary mask card candidate and compare against the S344 C3 bridge gate.
