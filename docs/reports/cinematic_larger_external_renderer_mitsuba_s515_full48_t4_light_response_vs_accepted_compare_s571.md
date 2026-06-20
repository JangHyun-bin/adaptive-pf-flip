# S571 Mitsuba S515 Full48 T4 Light Response vs Accepted Compare

Generated UTC: `2026-06-20T21:28:56.060362+00:00`
Summary JSON: `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/sequence_compare_summary.json`
Gallery: `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/gallery/index.html`
Status: `ready`

## Checks

- Candidates: `3`
- Common frames: `8`
- Selected frames: `8`
- Missing frame references: `0`
- GIF bytes: `4.34 MB`

## Candidates

| Label | Schema | Frames | Source |
| --- | --- | ---: | --- |
| `S515 Raw SPP4` | `lsfs_mitsuba_xml_render` | 48 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json` |
| `S555 Accepted T4` | `lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter` | 48 | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/runtime_render_sequence_adapter_summary.json` |
| `S570 Native Light` | `lsfs_mitsuba_xml_render` | 8 | `build/shots/s570_mitsuba_s515_full48_t4_low_frequency_light_response_sample_spp4/render/mitsuba_render.json` |

## Selected Frames

| Output | Strip |
| ---: | --- |
| 0 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0000_sequence_compare.png` |
| 7 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0007_sequence_compare.png` |
| 13 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0013_sequence_compare.png` |
| 20 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0020_sequence_compare.png` |
| 27 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0027_sequence_compare.png` |
| 34 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0034_sequence_compare.png` |
| 40 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0040_sequence_compare.png` |
| 47 | `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/strips/frame_0047_sequence_compare.png` |

## Next

Inspect whether the renderer-native S570 light anchors move toward the accepted S555 tone without over-brightening; if not, tune radiance/anchor filtering before full48.
