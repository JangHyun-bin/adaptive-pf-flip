# S572 Mitsuba S515 Full48 T4 LFMask Material Tone Dark Water Export

Generated UTC: `2026-06-20T21:33:32.445547+00:00`
Export JSON: `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/mitsuba_export.json`
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

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `320.17 KB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `32`
- Secondary opacity replacements: `32`
- Key lights inserted: `0`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.10051890432098766 | 0.10051890432098766 | 0.017560572001121367 | 0.8106327418467257 | 0.9026111243783161 | `[0.0, 0.0, 0.0]` | `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/scenes/frame_0000.xml` |
| 27 | 0.09749228395061728 | 0.09749228395061728 | 0.017784572894061944 | 0.8163345827579405 | 0.9055434997040837 | `[0.0, 0.0, 0.0]` | `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/scenes/frame_0004.xml` |
| 47 | 0.18329089506172838 | 0.18329089506172838 | 0.01143459729418239 | 0.6546988402155518 | 0.8224165463965695 | `[0.0, 0.0, 0.0]` | `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/scenes/frame_0007.xml` |

## Next

Validate and render this S567-driven material/tone sample, then compare against S555 accepted correction.
