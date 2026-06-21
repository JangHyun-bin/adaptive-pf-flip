# S619 Response AOV Consumer S075 Direct Metrics

Generated UTC: `2026-06-21T02:22:00Z`
Status: `ready`

## Inputs

- Response AOV contract: `build/shots/s618_mitsuba_response_aov_contract_s075/response_aov_contract.json`
- Response AOV consumer: `build/shots/s619_mitsuba_response_aov_consumer_s075/response_aov_consumer_summary.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene depth/material target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Import Parity

| Check | Value |
| --- | ---: |
| Frames | `48` |
| Missing references | `0` |
| Response scale | `0.75` |
| Max import absolute diff | `0` |
| Max import mean absolute diff | `0.0` |
| Max import mismatched coverage | `0.0` |

## Gate Metrics

| Candidate | Reference | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S619 consumed response AOV | S577 | `2.9732022274734224` | `5.5108699845679014` | `151` |
| S619 consumed response AOV | S585 | `2.982389550647291` | `5.524723508230453` | `148` |

## Decision

Promote S619 as the response-AOV import proof. It consumes the S618 signed AOV
contract with exact parity against the S617 selected composite and preserves
the same S577/S585 visual gate metrics. The next step can wire the same
contract/consumer boundary into the renderer scene-cache handoff instead of
recomputing response layers from full/base preview images.
