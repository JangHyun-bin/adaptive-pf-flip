# S457 Mitsuba Residual Response Late-Frame Decision

Generated UTC: `2026-06-20T14:50:00+00:00`

## Decision

Promote `lf47_mid` as the new best safe target-driven residual response candidate. It preserves the RR4 output-13 gain, adds one low-energy residual patch on output frame `47`, and improves mean gap MAD without increasing max gap MAD or max absolute gap.

Do not promote `lf40_low`, `lf40_mid`, or `lf47_low`. The output-40 candidates regress mean gap, and `lf47_low` improves the mean less than `lf47_mid`.

## Evidence

- Sweep runner: `tools/run_mitsuba_residual_response_energy_sweep.py`
- Sweep report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_late_frame_sweep_s457.md`
- Fit report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_late_frame_sweep_fit_s457.md`
- Best candidate target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_late_frame_sweep_lf47_mid_target_gap_s457.md`
- Representative output-47 strip: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid_target_gap/strips/frame_0007.png`

## Ranking Against RR4

| Candidate | Target | Energy | Safe | Mean Gap MAD | Max Gap MAD | Max Gap | Delta Mean MAD |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `lf47_mid` | output `47` | `0.0715` | `true` | `19.139147215792182` | `23.95382973251029` | `177` | `-0.0004321791409473974` |
| `lf47_low` | output `47` | `0.036` | `true` | `19.139517907664608` | `23.95382973251029` | `177` | `-0.00006148726852117647` |
| `RR4` | output `13` | `0.616` | `true` | `19.13957939493313` | `23.95382973251029` | `177` | `0` |
| `lf40_low` | output `40` | `0.06` | `true` | `19.139640801826133` | `23.95382973251029` | `177` | `0.00006140689300337954` |
| `lf40_mid` | output `40` | `0.119` | `true` | `19.14035453639403` | `23.95382973251029` | `177` | `0.0007751414609025176` |

## Interpretation

The late-frame residual should be handled asymmetrically. Output `47` accepts a very low-energy patch and improves the global mean while preserving the existing safety bounds. Output `40` currently moves in the wrong direction for this patch family, so it should not be tuned further until the response fitter can reason about local signed residuals instead of positive residual alone.

The current best safe chain is now:

1. `RR4`: output `13`, radius scale `0.28`, radiance scale `2.2`.
2. `lf47_mid`: added on top of RR4, output `47`, radius scale `0.11`, radiance scale `0.65`.

## Next

S458 should package this chain as a named preset/export and compare it directly against S452 sw2, RR4, SS1, and GL3 in one decision gallery.
