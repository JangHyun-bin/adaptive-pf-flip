# S480 Mitsuba Response Control Light Full Candidate

Generated UTC: `2026-06-20T16:41:06.408826+00:00`
Export JSON: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr4_focus_worst/mitsuba_export.json`
- Light contract: `build/shots/s479_mitsuba_response_control_handoff/light_response_contract.json`

## Light Response

- Anchor limit: `8`
- Radius range: `0.018..0.13`
- Base radiance: `[0.55, 0.7, 0.95]`
- Radiance scale: `1.0`
- Vertex stride: `1`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Contract frames matched: `5`
- Contract frames missing ignored: `3`
- Anchors consumed: `8`
- Lights inserted: `8`
- Localized anchors: `8`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Anchors | Lights | Vertices | XML Scene |
| ---: | ---: | ---: | ---: | --- |
| 0 | 2 | 2 | 10000 | `build/shots/s480_mitsuba_response_control_light_full/scenes/frame_0000.xml` |
| 27 | 1 | 1 | 9290 | `build/shots/s480_mitsuba_response_control_light_full/scenes/frame_0004.xml` |
| 47 | 0 | 0 | 0 | `build/shots/s480_mitsuba_response_control_light_full/scenes/frame_0007.xml` |

## Next

Render this full-frame XML candidate and compare target gap against the S478 p4 proxy before adding the material contract consumer.
