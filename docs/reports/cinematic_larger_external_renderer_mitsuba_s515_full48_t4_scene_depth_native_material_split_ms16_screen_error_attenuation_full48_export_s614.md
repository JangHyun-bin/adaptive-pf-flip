# S614 Mitsuba Scene-Depth Native Material Split MS16 Screen Error Attenuation Full48

Generated UTC: `2026-06-21T01:30:45.371448+00:00`
Export JSON: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48_base/mitsuba_export.json`
- Mask source: `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `1200`
- Face stride: `1`
- Response alpha: `0.18`
- Response bins: `2`
- Distribution: `ggx`
- IOR: `1.0 -> 1.333`
- Specular reflectance: `None`
- Specular transmittance: `None`
- Mask threshold: `128`
- Source luma gate: `0.0..255.0`
- Coverage attenuation: strength=`0.28`, pivot=`0.12`, width=`0.08`, max=`0.28`
- Coverage material scale: alpha_boost=`0.25`, reflectance_attenuation=`0.5`, transmittance_attenuation=`0.0`
- Low-coverage rescue: strength=`0.2`, pivot=`0.07`, width=`0.006`
- Coverage-band rescue: strength=`0.12`, center=`0.1133`, width=`0.0035`
- Screen-region attenuation: strength=`0.0`, x=`0.0..1.0`, y=`0.0..1.0`, coverage=`0.0..1.0`, output=`-1..-1`
- Screen-error attenuation: strength=`0.3`, threshold=`8.0`, width=`48.0`, coverage=`0.15..0.2`, output=`42..47`, gap=`build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/renderer_target_gap_summary.json`
- Low-coverage rescue scale: face_limit_boost=`0.15`, alpha_tighten=`0.15`, reflectance_boost=`0.45`, transmittance_boost=`0.0`
- Use current water shape: `False`
- Response shape ID prefix: `lsfs_s421_water_mask_material`
- Response BSDF ID prefix: `lsfs_water_surface_masked_response`

## Checks

- Frames exported: `48`
- Missing references: `0`
- Empty mask frames ignored: `0`
- Candidate faces: `55526`
- Response faces: `55526`
- Remainder faces: `870838`
- Water shape replacements: `48`
- Response BSDF insertions: `48`
- Coverage-control attenuated frames: `11`
- Coverage-control max attenuation: `0.2302478780864198`
- Low-coverage rescue frames: `11`
- Low-coverage max rescue: `0.2`
- Coverage-band rescue frames: `4`
- Coverage-band max rescue: `0.1189232804232805`
- Screen-region attenuated frames: `0`
- Screen-region candidate faces: `0`
- Screen-region dropped faces: `0`
- Screen-region max drop fraction: `0.0`
- Screen-error attenuated frames: `6`
- Screen-error sampled faces: `5806`
- Screen-error candidate faces: `3301`
- Screen-error dropped faces: `532`
- Screen-error max drop fraction: `0.10032362459546926`
- XML scene bytes: `1.95 MB`

## Frame Samples

| Output | Coverage | Atten | Low Rescue | Band Rescue | Region Drop | Error Drop | Limit | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.10051890432098766 | 0.0 | 0.0 | 0.0 | 0 | 0 | 1200 | 20000 | 1200 | 18800 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0000_low_frequency_response_mask.png` | `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/scenes/frame_0000.xml` |
| 24 | 0.08406635802469135 | 0.0 | 0.0 | 0.0 | 0 | 0 | 1200 | 17912 | 1200 | 16712 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0024_low_frequency_response_mask.png` | `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/scenes/frame_0024.xml` |
| 47 | 0.18329089506172838 | 0.22151813271604937 | 0.0 | 0.0 | 0 | 93 | 934 | 22300 | 841 | 21459 | `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/masks/frame_0047_low_frequency_response_mask.png` | `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/scenes/frame_0047.xml` |

## Next

Validate, render, and compare this tuned automatic screen-error attenuation against S612 and S613.
