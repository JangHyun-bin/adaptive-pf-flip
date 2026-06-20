# S456 Mitsuba Residual Response rr8_rr4_plus Export

Generated UTC: `2026-06-20T14:43:59.506292+00:00`
Export JSON: `build/shots/s456_mitsuba_residual_response_energy_sweep/rr8_rr4_plus/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s452_mitsuba_response_sweep/sw2_compact_high/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`

## Residual Response Patches

- Request limit: `16`
- Per-frame request limit: `4`
- Output frame filter: `[13]`
- Radius range: `0.045..0.65`
- Radius scale: `0.3`
- Radiance scale: `2.2`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Residual requests consumed: `2`
- Candidate vertices: `155`
- Patches inserted: `2`
- Fallback patches: `0`
- XML scene bytes: `1.39 MB`

## Frame Samples

| Output | Vertices | Requests | Patches | Fallback | XML Scene |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 10000 | 0 | 0 | 0 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr8_rr4_plus/scenes/frame_0000.xml` |
| 27 | 9290 | 0 | 0 | 0 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr8_rr4_plus/scenes/frame_0004.xml` |
| 47 | 11152 | 0 | 0 | 0 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr8_rr4_plus/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S456 rr8_rr4_plus.
