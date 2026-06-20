# S405 CR21 Native Highlight Sprites Export

Generated UTC: `2026-06-20T08:34:35.929045+00:00`
Export JSON: `build/shots/s405_mitsuba_cr21_native_highlight_sprites/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s405_mitsuba_cr21_highlight_mask_source/source_response_mask_source_summary.json`
- Mask source schema: `lsfs_mitsuba_secondary_composite`

## Screen Card

- Card distance: `18.0`
- Card mode: `sprites`
- Card scale: `1.0`
- Mask gain: `1.0`
- Mask blur radius: `0.0`
- Flip Y: `False`
- Reflectance: `0.70,0.84,0.96`
- Sprite limit: `96`
- Sprite threshold: `16`
- Sprite radius pixels: `4.5`
- Sprite radiance: `5.5,6.8,8.2`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `768`
- Screen card mask bytes: `101.67 KB`
- XML scene bytes: `1.60 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s405_mitsuba_cr21_native_highlight_sprites/scenes/frame_0000.xml` | `build/shots/s405_mitsuba_cr21_native_highlight_sprites/secondary_screen_masks/frame_0000.png` | 13883 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 96 |
| 27 | `build/shots/s405_mitsuba_cr21_native_highlight_sprites/scenes/frame_0004.xml` | `build/shots/s405_mitsuba_cr21_native_highlight_sprites/secondary_screen_masks/frame_0004.png` | 9466 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 96 |
| 47 | `build/shots/s405_mitsuba_cr21_native_highlight_sprites/scenes/frame_0007.xml` | `build/shots/s405_mitsuba_cr21_native_highlight_sprites/secondary_screen_masks/frame_0007.png` | 22767 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 96 |

## Next

Render and compare NH1 against SS1 and the CR21 profile.
