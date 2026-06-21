# S618 Mitsuba Response AOV Contract S075

Generated UTC: `2026-06-21T02:15:58.523477+00:00`
Contract JSON: `build/shots/s618_mitsuba_response_aov_contract_s075/response_aov_contract.json`
Gallery: `build/shots/s618_mitsuba_response_aov_contract_s075/gallery/index.html`
Status: `ready`

## Inputs

- Response buffer: `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/response_delta_buffer_summary.json`
- Response composite: `build/shots/s617_mitsuba_response_scale_composite_s075/response_scale_composite_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Response scale: `0.75`
- Reconstruction max abs diff: `0`
- Reconstruction max mean abs diff: `0.0`
- Mean abs signed delta: `2.092316449116941`
- Max abs signed delta: `138`
- Composite bytes: `14.77 MB`
- AOV bytes: `40.45 MB`
- GIF bytes: `35.43 MB`

## Gate Metrics

- s577: mean/max/maxabs `2.9732022274734224` / `5.5108699845679014` / `151`
- s585: mean/max/maxabs `2.982389550647291` / `5.524723508230453` / `148`

## Frame Samples

| Output | Mean Delta | Max Delta | Recon Max | Strip |
| ---: | ---: | ---: | ---: | --- |
| 0 | 2.054025848765432 | 114 | 0 | `build/shots/s618_mitsuba_response_aov_contract_s075/strips/frame_0000.png` |
| 24 | 2.002457561728395 | 113 | 0 | `build/shots/s618_mitsuba_response_aov_contract_s075/strips/frame_0024.png` |
| 47 | 1.859156378600823 | 119 | 0 | `build/shots/s618_mitsuba_response_aov_contract_s075/strips/frame_0047.png` |

## Next

Consume this signed response-AOV contract in a renderer/cache handoff and keep S617 as the visual gate.
