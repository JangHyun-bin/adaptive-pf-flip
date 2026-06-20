# S485 Mitsuba Light Response lrs4_sparse_spec Export

Generated UTC: `2026-06-20T17:16:25.680246+00:00`
Export JSON: `build/shots/s485_mitsuba_light_response_sweep/lrs4_sparse_spec/light_export/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr4_focus_worst/mitsuba_export.json`
- Light contract: `build/shots/s479_mitsuba_response_control_handoff/light_response_contract.json`

## Light Response

- Anchor limit: `4`
- Radius range: `0.01..0.072`
- Base radiance: `[0.82, 0.98, 1.32]`
- Radiance scale: `1.6`
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
| 0 | 2 | 2 | 10000 | `build/shots/s485_mitsuba_light_response_sweep/lrs4_sparse_spec/light_export/scenes/frame_0000.xml` |
| 27 | 1 | 1 | 9290 | `build/shots/s485_mitsuba_light_response_sweep/lrs4_sparse_spec/light_export/scenes/frame_0004.xml` |
| 47 | 0 | 0 | 0 | `build/shots/s485_mitsuba_light_response_sweep/lrs4_sparse_spec/light_export/scenes/frame_0007.xml` |

## Next

Validate, render, and compare lrs4_sparse_spec.
