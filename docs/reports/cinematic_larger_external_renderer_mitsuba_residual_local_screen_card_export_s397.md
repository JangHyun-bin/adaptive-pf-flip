# S397 Mitsuba Residual Local Screen Card Export

Generated UTC: `2026-06-20T07:57:10.376757+00:00`
Export JSON: `build/shots/s397_mitsuba_residual_local_screen_card/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s397_mitsuba_residual_mask_source_best/residual_mask_source_summary.json`
- Mask source schema: `lsfs_mitsuba_secondary_composite`

## Screen Card

- Card distance: `18.0`
- Card mode: `rectangle`
- Card scale: `1.0`
- Mask gain: `1.0`
- Mask blur radius: `0.0`
- Flip Y: `False`
- Reflectance: `0.06,0.08,0.12`
- Sprite limit: `0`
- Sprite threshold: `16`
- Sprite radius pixels: `5.0`
- Sprite radiance: `4.0,5.5,7.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `0`
- Screen card mask bytes: `43.64 KB`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s397_mitsuba_residual_local_screen_card/scenes/frame_0000.xml` | `build/shots/s397_mitsuba_residual_local_screen_card/secondary_screen_masks/frame_0000.png` | 7219 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 27 | `build/shots/s397_mitsuba_residual_local_screen_card/scenes/frame_0004.xml` | `build/shots/s397_mitsuba_residual_local_screen_card/secondary_screen_masks/frame_0004.png` | 1801 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 47 | `build/shots/s397_mitsuba_residual_local_screen_card/scenes/frame_0007.xml` | `build/shots/s397_mitsuba_residual_local_screen_card/secondary_screen_masks/frame_0007.png` | 14200 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |

## Next

Render and compare this residual-local native screen-card candidate.
