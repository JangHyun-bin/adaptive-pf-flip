# S456 Mitsuba Residual Response Energy Sweep Decision

Generated UTC: `2026-06-20T14:46:00+00:00`

## Decision

Keep `tools/run_mitsuba_residual_response_energy_sweep.py` and keep `RR4` as the current best safe target-driven residual response. The S456 narrow output-13 energy sweep did not beat RR4, but it usefully bounded the search: output frame `13` is already near the safe local optimum for this patch family.

Do not promote `rr5_hint_low`, `rr6_mid`, `rr7_rr4_soft`, or `rr8_rr4_plus`. The first three are safe but slightly weaker than RR4. `rr8_rr4_plus` preserves max absolute gap but regresses both max and mean MAD, so it is rejected by the fitter.

## Evidence

- Runner: `tools/run_mitsuba_residual_response_energy_sweep.py`
- Sweep report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_energy_sweep_s456.md`
- Fit report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_energy_sweep_fit_s456.md`
- Fit summary: `build/shots/s456_mitsuba_residual_response_energy_sweep/fit/residual_response_fit_summary.json`
- Representative strip: `build/shots/s456_mitsuba_residual_response_energy_sweep/rr7_rr4_soft_target_gap/strips/frame_0002.png`

## Ranking

| Candidate | Energy | Safe | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `RR4` | `0.616` | `true` | `19.13957939493313` | `23.95382973251029` | `177` | Current best safe candidate. |
| `rr7_rr4_soft` | `0.56` | `true` | `19.13958132394547` | `23.953845164609053` | `177` | Very close but weaker than RR4. |
| `rr5_hint_low` | `0.322` | `true` | `19.139584137088477` | `23.953867669753087` | `177` | Safe, weaker than RR4. |
| `rr6_mid` | `0.45` | `true` | `19.13959514853395` | `23.953955761316873` | `177` | Safe, weaker than RR4. |
| `rr8_rr4_plus` | `0.66` | `false` | `19.139707674254115` | `23.95485596707819` | `177` | Regresses objective. |

## Interpretation

S456 confirms that the output-13 residual patch family has a narrow useful window. More energy does not monotonically improve the render; after RR4 the objective worsens. The next visual improvement should preserve RR4 and move to a separate residual group rather than keep tuning the same output-13 patch.

The strongest remaining unresolved residuals in S453 were late-frame upper water bands. S454 RR2 proved that touching all late-frame requests can reduce max MAD but risks high max-gap artifacts. The next step should handle late-frame requests with a stricter cap and one frame/group at a time.

## Next

S457 should add a late-frame residual group sweep that preserves RR4, targets output frames `40` and `47` separately, and rejects any candidate that raises max absolute gap above `177`.
