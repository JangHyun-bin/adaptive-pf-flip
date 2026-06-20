# S442 Mitsuba Light Response Contract LR1 Export

Generated UTC: `2026-06-20T12:59:45.496273+00:00`
Export JSON: `build/shots/s442_mitsuba_light_response_contract_lr1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Light contract: `build/reports/s441_mitsuba_s401_light_response_contract/light_response_contract.json`

## Light Response

- Anchor limit: `8`
- Radius range: `0.018..0.13`
- Base radiance: `[0.55, 0.7, 0.95]`
- Radiance scale: `1.0`
- Vertex stride: `1`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Contract frames matched: `8`
- Anchors consumed: `49`
- Lights inserted: `49`
- Localized anchors: `49`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Anchors | Lights | Vertices | XML Scene |
| ---: | ---: | ---: | ---: | --- |
| 0 | 7 | 7 | 10000 | `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0000.xml` |
| 27 | 2 | 2 | 9290 | `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0004.xml` |
| 47 | 8 | 8 | 11152 | `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0007.xml` |

## Next

Validate and render this contract-driven world-space light response candidate, then compare target gap against SS1_Native and S417_WP4_H18_D90.
