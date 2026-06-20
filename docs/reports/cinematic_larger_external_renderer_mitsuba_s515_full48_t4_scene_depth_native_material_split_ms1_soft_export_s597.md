# S597 Scene Depth Native Material Split MS1 Soft Export

Generated UTC: `2026-06-20T23:27:25.307145+00:00`
Export JSON: `build/shots/s597_mitsuba_scene_depth_native_material_split_ms1_soft/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/mitsuba_export.json`
- Mask source: `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `0`
- Face stride: `1`
- Response alpha: `0.03`
- Response bins: `3`
- Distribution: `ggx`
- IOR: `1.0 -> 1.333`
- Specular reflectance: `None`
- Specular transmittance: `None`
- Mask threshold: `16`
- Source luma gate: `0.0..255.0`
- Use current water shape: `False`
- Response shape ID prefix: `lsfs_s421_water_mask_material`
- Response BSDF ID prefix: `lsfs_water_surface_masked_response`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Empty mask frames ignored: `0`
- Candidate faces: `103565`
- Response faces: `103565`
- Remainder faces: `53199`
- Water shape replacements: `8`
- Response BSDF insertions: `8`
- XML scene bytes: `338.43 KB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 12796 | 7204 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0000_low_frequency_response_mask.png` | `build/shots/s597_mitsuba_scene_depth_native_material_split_ms1_soft/scenes/frame_0000.xml` |
| 27 | 18576 | 11738 | 6838 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0027_low_frequency_response_mask.png` | `build/shots/s597_mitsuba_scene_depth_native_material_split_ms1_soft/scenes/frame_0004.xml` |
| 47 | 22300 | 18821 | 3479 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0047_low_frequency_response_mask.png` | `build/shots/s597_mitsuba_scene_depth_native_material_split_ms1_soft/scenes/frame_0007.xml` |

## Next

Validate, render, and compare this localized face-split material response against S596 and the S573/S577/S585 references.
