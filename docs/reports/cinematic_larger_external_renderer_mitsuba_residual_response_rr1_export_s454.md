# S454 Mitsuba Residual Response RR1 Export

Generated UTC: `2026-06-20T14:30:11.817412+00:00`
Export JSON: `build/shots/s454_mitsuba_residual_response_rr1/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s452_mitsuba_response_sweep/sw2_compact_high/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`

## Residual Response Patches

- Request limit: `16`
- Per-frame request limit: `4`
- Radius range: `0.035..0.34`
- Radius scale: `0.16`
- Radiance scale: `1.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Residual requests consumed: `16`
- Candidate vertices: `4201`
- Patches inserted: `16`
- Fallback patches: `0`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Vertices | Requests | Patches | Fallback | XML Scene |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 10000 | 3 | 3 | 0 | `build/shots/s454_mitsuba_residual_response_rr1/scenes/frame_0000.xml` |
| 27 | 9290 | 1 | 1 | 0 | `build/shots/s454_mitsuba_residual_response_rr1/scenes/frame_0004.xml` |
| 47 | 11152 | 3 | 3 | 0 | `build/shots/s454_mitsuba_residual_response_rr1/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S454 RR1 against S452 sw2, SS1, and GL3.
