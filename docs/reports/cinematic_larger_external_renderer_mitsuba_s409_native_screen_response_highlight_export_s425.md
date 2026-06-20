# S425 Mitsuba S409 Native Screen Response Highlight Export

Generated UTC: `2026-06-20T11:43:12.707097+00:00`
Export JSON: `build/shots/s425_mitsuba_s409_native_screen_response_highlight/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s423_mitsuba_s409_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`
- Mask source schema: `lsfs_mitsuba_source_response_mask_source`

## Screen Card

- Card distance: `18.0`
- Card mode: `both`
- Card scale: `1.0`
- ID prefix: `lsfs_s425_highlight_screen_card`
- Mask gain: `1.2`
- Mask blur radius: `0.6`
- Flip Y: `False`
- Reflectance: `0.55,0.70,0.88`
- Sprite limit: `96`
- Sprite threshold: `12`
- Sprite radius pixels: `5.5`
- Sprite radiance: `5.0,6.5,8.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Screen cards emitted: `8`
- Screen sprites emitted: `768`
- Screen card mask bytes: `113.51 KB`
- XML scene bytes: `1.61 MB`

## Frame Samples

| Output | XML Scene | Mask | Mask Bytes | Center | Half Extents | Sprites |
| ---: | --- | --- | ---: | --- | --- | ---: |
| 0 | `build/shots/s425_mitsuba_s409_native_screen_response_highlight/scenes/frame_0000.xml` | `build/shots/s425_mitsuba_s409_native_screen_response_highlight/secondary_screen_masks/frame_0000.png` | 15243 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 96 |
| 27 | `build/shots/s425_mitsuba_s409_native_screen_response_highlight/scenes/frame_0004.xml` | `build/shots/s425_mitsuba_s409_native_screen_response_highlight/secondary_screen_masks/frame_0004.png` | 10681 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 96 |
| 47 | `build/shots/s425_mitsuba_s409_native_screen_response_highlight/scenes/frame_0007.xml` | `build/shots/s425_mitsuba_s409_native_screen_response_highlight/secondary_screen_masks/frame_0007.png` | 25429 | `[18.0, 15.263887, 40.634251]` | `[9.783382, 5.503152]` | 96 |

## Next

Layer the S409 response-union dark screen card onto this highlight response, then render and compare the combined native response.
