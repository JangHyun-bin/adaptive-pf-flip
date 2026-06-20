# S454 Mitsuba Residual Response RR2 Export

Generated UTC: `2026-06-20T14:32:41.055726+00:00`
Export JSON: `build/shots/s454_mitsuba_residual_response_rr2/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s452_mitsuba_response_sweep/sw2_compact_high/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`

## Residual Response Patches

- Request limit: `16`
- Per-frame request limit: `4`
- Radius range: `0.045..0.65`
- Radius scale: `0.28`
- Radiance scale: `2.2`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Residual requests consumed: `16`
- Candidate vertices: `5078`
- Patches inserted: `16`
- Fallback patches: `0`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Vertices | Requests | Patches | Fallback | XML Scene |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 10000 | 3 | 3 | 0 | `build/shots/s454_mitsuba_residual_response_rr2/scenes/frame_0000.xml` |
| 27 | 9290 | 1 | 1 | 0 | `build/shots/s454_mitsuba_residual_response_rr2/scenes/frame_0004.xml` |
| 47 | 11152 | 3 | 3 | 0 | `build/shots/s454_mitsuba_residual_response_rr2/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S454 RR2 against RR1 and S452 sw2.
