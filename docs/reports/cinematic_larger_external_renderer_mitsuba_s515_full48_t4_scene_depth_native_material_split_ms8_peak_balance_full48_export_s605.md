# S605 Scene Depth Native Material Split MS8 Peak Balance Full48 Export

Generated UTC: `2026-06-21T00:06:42.721121+00:00`
Export JSON: `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48_base/mitsuba_export.json`
- Mask source: `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `1300`
- Face stride: `1`
- Response alpha: `0.17`
- Response bins: `2`
- Distribution: `ggx`
- IOR: `1.0 -> 1.333`
- Specular reflectance: `None`
- Specular transmittance: `None`
- Mask threshold: `128`
- Source luma gate: `0.0..255.0`
- Use current water shape: `False`
- Response shape ID prefix: `lsfs_s421_water_mask_material`
- Response BSDF ID prefix: `lsfs_water_surface_masked_response`

## Checks

- Frames exported: `48`
- Missing references: `0`
- Empty mask frames ignored: `0`
- Candidate faces: `62400`
- Response faces: `62400`
- Remainder faces: `863964`
- Water shape replacements: `48`
- Response BSDF insertions: `48`
- XML scene bytes: `1.95 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 1300 | 18700 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0000_low_frequency_response_mask.png` | `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/scenes/frame_0000.xml` |
| 24 | 17912 | 1300 | 16612 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0024_low_frequency_response_mask.png` | `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/scenes/frame_0024.xml` |
| 47 | 22300 | 1300 | 21000 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0047_low_frequency_response_mask.png` | `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/scenes/frame_0047.xml` |

## Next

Validate and render this peak-balanced full48 localized material split, then compare full48 metrics against S602 and S604.
