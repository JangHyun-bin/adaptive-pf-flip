# S457 Mitsuba Residual Response Late-Frame Sweep

Generated UTC: `2026-06-20T14:48:17.267025+00:00`
Summary JSON: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/residual_response_energy_sweep_summary.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s454_mitsuba_residual_response_rr4/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`
- Baseline gap: `build/shots/s454_mitsuba_residual_response_rr4_target_gap/renderer_target_gap_summary.json`

## Variants

| Candidate | Energy | Mean Gap MAD | Max Gap MAD | Max Gap | Export Patches | Target Gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lf40_low` | 0.06 | 19.139640801826133 | 23.95382973251029 | 177 | 1 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf40_low_target_gap/renderer_target_gap_summary.json` |
| `lf40_mid` | 0.11900000000000001 | 19.14035453639403 | 23.95382973251029 | 177 | 1 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf40_mid_target_gap/renderer_target_gap_summary.json` |
| `lf47_low` | 0.036000000000000004 | 19.139517907664608 | 23.95382973251029 | 177 | 1 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_low_target_gap/renderer_target_gap_summary.json` |
| `lf47_mid` | 0.07150000000000001 | 19.139147215792182 | 23.95382973251029 | 177 | 1 | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid_target_gap/renderer_target_gap_summary.json` |

## Fit

- Fit summary: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/fit/residual_response_fit_summary.json`
- Fit report: `docs\reports\cinematic_larger_external_renderer_mitsuba_residual_response_late_frame_sweep_fit_s457.md`
- Best safe candidate: `lf47_mid`

## Next

Keep RR4 unless a late-frame candidate improves max or mean gap without raising max absolute gap above 177.
