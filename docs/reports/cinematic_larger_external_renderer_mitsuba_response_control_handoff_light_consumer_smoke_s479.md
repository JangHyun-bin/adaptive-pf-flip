# S479 Mitsuba Response Control Handoff Light Consumer Smoke

Generated UTC: `2026-06-20T16:38:42.019204+00:00`
Export JSON: `build/shots/s479_mitsuba_response_control_handoff/light_contract_consumer_smoke/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr4_focus_worst/mitsuba_export.json`
- Light contract: `build/shots/s479_mitsuba_response_control_handoff/light_response_contract.json`

## Light Response

- Anchor limit: `2`
- Radius range: `0.018..0.13`
- Base radiance: `[0.55, 0.7, 0.95]`
- Radiance scale: `1.0`
- Vertex stride: `1`

## Checks

- Frames exported: `1`
- Missing references: `0`
- Contract frames matched: `1`
- Anchors consumed: `2`
- Lights inserted: `2`
- Localized anchors: `2`
- XML scene bytes: `128.85 KB`

## Frame Samples

| Output | Anchors | Lights | Vertices | XML Scene |
| ---: | ---: | ---: | ---: | --- |
| 0 | 2 | 2 | 10000 | `build/shots/s479_mitsuba_response_control_handoff/light_contract_consumer_smoke/scenes/frame_0000.xml` |

## Next

Use the generated XML scene as the first renderer-native light-control candidate, then compare target gap against the S478 p4 proxy gate.
