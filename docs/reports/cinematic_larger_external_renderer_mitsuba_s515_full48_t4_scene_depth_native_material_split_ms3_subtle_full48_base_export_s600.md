# S600 Scene Depth Native Material Split MS3 Subtle Full48 Base Export

Generated UTC: `2026-06-20T23:44:36.729027+00:00`
Export JSON: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48_base/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask source: `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s567_mitsuba_s515_full48_t4_low_frequency_response_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['bubble', 'droplet', 'foam', 'spray']`
- Secondary reflectance drop: `0.35`
- Secondary opacity drop: `0.18`
- Water alpha drop: `0.55`
- Water alpha min: `0.006`
- Highlight key light max radiance: `[0.0, 0.0, 0.0]`

## Checks

- Frames exported: `48`
- Missing references: `0`
- XML scene bytes: `1.88 MB`
- Water alpha replacements: `48`
- Secondary reflectance replacements: `192`
- Secondary opacity replacements: `192`
- Key lights inserted: `0`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.10051890432098766 | 0.10051890432098766 | 0.017560572001121367 | 0.8106327418467257 | 0.9026111243783161 | `[0.0, 0.0, 0.0]` | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48_base/scenes/frame_0000.xml` |
| 24 | 0.08406635802469135 | 0.08406635802469135 | 0.01877822886274673 | 0.8416276437790076 | 0.9185513596577753 | `[0.0, 0.0, 0.0]` | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48_base/scenes/frame_0024.xml` |
| 47 | 0.18329089506172838 | 0.18329089506172838 | 0.01143459729418239 | 0.6546988402155518 | 0.8224165463965695 | `[0.0, 0.0, 0.0]` | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48_base/scenes/frame_0047.xml` |

## Next

Apply the S599 subtle localized material split settings across this full48 material/tone base export.
