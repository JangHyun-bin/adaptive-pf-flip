# S456 Mitsuba Residual Response Energy Sweep

Generated UTC: `2026-06-20T14:44:12.342958+00:00`
Summary JSON: `build/shots/s456_mitsuba_residual_response_energy_sweep/residual_response_energy_sweep_summary.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s452_mitsuba_response_sweep/sw2_compact_high/mitsuba_export.json`
- Residual analysis: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`
- Baseline gap: `build/shots/s452_mitsuba_response_sweep/sw2_compact_high_target_gap/renderer_target_gap_summary.json`

## Variants

| Candidate | Energy | Mean Gap MAD | Max Gap MAD | Max Gap | Export Patches | Target Gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `rr5_hint_low` | 0.322 | 19.139584137088477 | 23.953867669753087 | 177 | 2 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr5_hint_low_target_gap/renderer_target_gap_summary.json` |
| `rr6_mid` | 0.45 | 19.13959514853395 | 23.953955761316873 | 177 | 2 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr6_mid_target_gap/renderer_target_gap_summary.json` |
| `rr7_rr4_soft` | 0.56 | 19.13958132394547 | 23.953845164609053 | 177 | 2 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr7_rr4_soft_target_gap/renderer_target_gap_summary.json` |
| `rr8_rr4_plus` | 0.66 | 19.139707674254115 | 23.95485596707819 | 177 | 2 | `build/shots/s456_mitsuba_residual_response_energy_sweep/rr8_rr4_plus_target_gap/renderer_target_gap_summary.json` |

## Fit

- Fit summary: `build/shots/s456_mitsuba_residual_response_energy_sweep/fit/residual_response_fit_summary.json`
- Fit report: `docs\reports\cinematic_larger_external_renderer_mitsuba_residual_response_energy_sweep_fit_s456.md`
- Best safe candidate: `RR4`

## Next

Use the best safe S456 candidate as the current target-driven response preset and move to late-frame residuals only after preserving the output-13 gain.
