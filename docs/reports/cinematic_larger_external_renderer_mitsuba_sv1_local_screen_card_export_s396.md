# S396 Mitsuba SV1 Local Screen Card Export

Generated UTC: `2026-06-20T07:49:21.651786+00:00`
Export JSON: `build/shots/s396_mitsuba_sv1_local_screen_card/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Mask source schema: `lsfs_mitsuba_secondary_composite`

## Screen Card

- Card distance: `18.0`
- Card mode: `rectangle`
- Card scale: `1.0`
- Mask gain: `0.35`
- Mask blur radius: `0.8`
- Flip Y: `False`
- Reflectance: `0.32,0.42,0.54`
- Sprite limit: `0`
- Sprite threshold: `16`
- Sprite radius pixels: `5.0`
- Sprite radiance: `4.0,5.5,7.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `0`
- Screen card mask bytes: `69.71 KB`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s396_mitsuba_sv1_local_screen_card/scenes/frame_0000.xml` | `build/shots/s396_mitsuba_sv1_local_screen_card/secondary_screen_masks/frame_0000.png` | 9674 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 27 | `build/shots/s396_mitsuba_sv1_local_screen_card/scenes/frame_0004.xml` | `build/shots/s396_mitsuba_sv1_local_screen_card/secondary_screen_masks/frame_0004.png` | 6554 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 47 | `build/shots/s396_mitsuba_sv1_local_screen_card/scenes/frame_0007.xml` | `build/shots/s396_mitsuba_sv1_local_screen_card/secondary_screen_masks/frame_0007.png` | 15149 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |

## Next

Render the SV1-localized screen-card candidate and compare target/native gaps.
