# S405 CR21 Native Union Soft Card Export

Generated UTC: `2026-06-20T08:34:35.849360+00:00`
Export JSON: `build/shots/s405_mitsuba_cr21_native_union_soft_card/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s405_mitsuba_cr21_response_union_mask_source/source_response_mask_source_summary.json`
- Mask source schema: `lsfs_mitsuba_secondary_composite`

## Screen Card

- Card distance: `18.0`
- Card mode: `rectangle`
- Card scale: `1.0`
- Mask gain: `0.28`
- Mask blur radius: `1.0`
- Flip Y: `False`
- Reflectance: `0.18,0.24,0.30`
- Sprite limit: `0`
- Sprite threshold: `16`
- Sprite radius pixels: `5.0`
- Sprite radiance: `4.0,5.5,7.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `0`
- Screen card mask bytes: `63.30 KB`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s405_mitsuba_cr21_native_union_soft_card/scenes/frame_0000.xml` | `build/shots/s405_mitsuba_cr21_native_union_soft_card/secondary_screen_masks/frame_0000.png` | 8834 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 27 | `build/shots/s405_mitsuba_cr21_native_union_soft_card/scenes/frame_0004.xml` | `build/shots/s405_mitsuba_cr21_native_union_soft_card/secondary_screen_masks/frame_0004.png` | 6017 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |
| 47 | `build/shots/s405_mitsuba_cr21_native_union_soft_card/scenes/frame_0007.xml` | `build/shots/s405_mitsuba_cr21_native_union_soft_card/secondary_screen_masks/frame_0007.png` | 13770 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 0 |

## Next

Render and compare NU1 against SS1 and the CR21 profile.
