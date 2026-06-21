# S617 Response Scale S075 vs S577 Gap

Generated UTC: `2026-06-21T02:09:57.680581+00:00`
Status: `ready`

## Inputs

- Actual: `build/shots/s617_mitsuba_response_scale_composite_s075/response_scale_composite_summary.json`
- Reference: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Mean gap MAD: `2.9732022274734224`
- Max gap MAD: `5.5108699845679014`
- Max gap abs: `151`
- GIF bytes: `27.61 MB`

## Frame Samples

| Output | MAD | Max Abs | Strip |
| ---: | ---: | ---: | --- |
| 0 | 2.7513734567901236 | 134 | `build/shots/s617_mitsuba_response_scale_composite_s075/gap_vs_s577/strips/frame_0000.png` |
| 24 | 2.33774241255144 | 112 | `build/shots/s617_mitsuba_response_scale_composite_s075/gap_vs_s577/strips/frame_0024.png` |
| 47 | 5.384697788065844 | 129 | `build/shots/s617_mitsuba_response_scale_composite_s075/gap_vs_s577/strips/frame_0047.png` |

## Next

Use this accepted-gate gap with the S585 gap to decide whether the response-scale composite is a stronger promotion baseline.
