# S457 Mitsuba Residual Response lf47_low Export

Generated UTC: `2026-06-20T14:47:53.270830+00:00`
Export JSON: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_low/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s454_mitsuba_residual_response_rr4/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`

## Residual Response Patches

- Request limit: `16`
- Per-frame request limit: `1`
- Output frame filter: `[47]`
- Radius range: `0.02..0.16`
- Radius scale: `0.08`
- Radiance scale: `0.45`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Residual requests consumed: `1`
- Candidate vertices: `1000`
- Patches inserted: `1`
- Fallback patches: `0`
- XML scene bytes: `1.39 MB`

## Frame Samples

| Output | Vertices | Requests | Patches | Fallback | XML Scene |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 10000 | 0 | 0 | 0 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_low/scenes/frame_0000.xml` |
| 27 | 9290 | 0 | 0 | 0 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_low/scenes/frame_0004.xml` |
| 47 | 11152 | 1 | 1 | 0 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_low/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S457 lf47_low.
