# S455 Mitsuba Residual Response Fit

Generated UTC: `2026-06-20T14:38:56.512221+00:00`
Summary JSON: `build/shots/s455_mitsuba_residual_response_fit/residual_response_fit_summary.json`
Status: `ready`

## Baseline

- Gap summary: `build/shots/s452_mitsuba_response_sweep/sw2_compact_high_target_gap/renderer_target_gap_summary.json`
- Mean gap MAD: `19.139631156764402`
- Max gap MAD: `23.954243827160493`
- Max absolute gap: `177.0`

## Candidate Ranking

| Rank | Candidate | Safe | Mean Gap MAD | Max Gap MAD | Max Gap | Delta Max MAD | Delta Mean MAD |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `RR4` | `True` | 19.13957939493313 | 23.95382973251029 | 177.0 | -0.0004140946502033671 | -5.1761831272756353e-05 |
| 2 | `RR2` | `False` | 19.175778517232512 | 23.95382973251029 | 206.0 | -0.0004140946502033671 | 0.03614736046811018 |
| 3 | `RR1` | `False` | 19.151900479038066 | 23.95425925925926 | 177.0 | 1.5432098766865465e-05 | 0.012269322273663619 |
| 4 | `RR3` | `False` | 19.143790991512347 | 23.98752250514403 | 188.0 | 0.033278677983538785 | 0.004159834747945013 |

## Best Safe Candidate

- Label: `RR4`
- Max gap MAD: `23.95382973251029`
- Mean gap MAD: `19.13957939493313`
- Max absolute gap: `177.0`

## Fit Hint

- Kind: `output13_energy_scan`
- Best sampled energy: `0.6160000000000001`
- Quadratic energy center: `0.31938300266158576`

## Next

Use RR4 as the current safe target-driven response and search a narrow output-13 energy band before touching late-frame residuals again.
