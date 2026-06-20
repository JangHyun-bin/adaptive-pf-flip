# S569 Mitsuba S515 Full48 T4 Low Frequency Light Response Sample Export

Generated UTC: `2026-06-20T21:27:02.011319+00:00`
Export JSON: `build/shots/s569_mitsuba_s515_full48_t4_low_frequency_light_response_sample/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Light contract: `build/shots/s568_mitsuba_s515_full48_t4_low_frequency_light_response_contract/light_response_contract.json`

## Light Response

- Anchor limit: `8`
- Radius range: `0.018..0.13`
- Base radiance: `[0.45, 0.62, 0.9]`
- Radiance scale: `0.7`
- Vertex stride: `8`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Contract frames matched: `8`
- Contract frames missing ignored: `0`
- Anchors consumed: `64`
- Lights inserted: `64`
- Localized anchors: `64`
- XML scene bytes: `337.91 KB`

## Frame Samples

| Output | Anchors | Lights | Vertices | XML Scene |
| ---: | ---: | ---: | ---: | --- |
| 0 | 8 | 8 | 1250 | `build/shots/s569_mitsuba_s515_full48_t4_low_frequency_light_response_sample/scenes/frame_0000.xml` |
| 27 | 8 | 8 | 1162 | `build/shots/s569_mitsuba_s515_full48_t4_low_frequency_light_response_sample/scenes/frame_0004.xml` |
| 47 | 8 | 8 | 1394 | `build/shots/s569_mitsuba_s515_full48_t4_low_frequency_light_response_sample/scenes/frame_0007.xml` |

## Next

Validate this XML export, then render a short sample against the S564/S515 post-tonemap proof.
