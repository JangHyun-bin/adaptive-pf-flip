# S457 Mitsuba Residual Response lf40_mid Export

Generated UTC: `2026-06-20T14:47:42.287744+00:00`
Export JSON: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf40_mid/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s454_mitsuba_residual_response_rr4/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`

## Residual Response Patches

- Request limit: `16`
- Per-frame request limit: `1`
- Output frame filter: `[40]`
- Radius range: `0.025..0.24`
- Radius scale: `0.14`
- Radiance scale: `0.85`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Residual requests consumed: `1`
- Candidate vertices: `1065`
- Patches inserted: `1`
- Fallback patches: `0`
- XML scene bytes: `1.39 MB`

## Frame Samples

| Output | Vertices | Requests | Patches | Fallback | XML Scene |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 10000 | 0 | 0 | 0 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf40_mid/scenes/frame_0000.xml` |
| 27 | 9290 | 0 | 0 | 0 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf40_mid/scenes/frame_0004.xml` |
| 47 | 11152 | 0 | 0 | 0 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf40_mid/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S457 lf40_mid.
