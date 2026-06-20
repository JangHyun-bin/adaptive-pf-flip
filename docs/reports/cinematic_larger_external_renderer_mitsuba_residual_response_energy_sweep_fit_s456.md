# S456 Mitsuba Residual Response Energy Fit

Generated UTC: `2026-06-20T14:44:12.326263+00:00`
Summary JSON: `build/shots/s456_mitsuba_residual_response_energy_sweep/fit/residual_response_fit_summary.json`
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
| 2 | `rr7_rr4_soft` | `True` | 19.13958132394547 | 23.953845164609053 | 177.0 | -0.00039866255144005436 | -4.983281893089497e-05 |
| 3 | `rr5_hint_low` | `True` | 19.139584137088477 | 23.953867669753087 | 177.0 | -0.0003761574074054863 | -4.70196759252417e-05 |
| 4 | `rr6_mid` | `True` | 19.13959514853395 | 23.953955761316873 | 177.0 | -0.00028806584361973364 | -3.6008230452466705e-05 |
| 5 | `rr8_rr4_plus` | `False` | 19.139707674254115 | 23.95485596707819 | 177.0 | 0.0006121399176954867 | 7.65174897132681e-05 |

## Best Safe Candidate

- Label: `RR4`
- Max gap MAD: `23.95382973251029`
- Mean gap MAD: `19.13957939493313`
- Max absolute gap: `177.0`

## Fit Hint

- Kind: `output13_energy_scan`
- Best sampled energy: `0.6160000000000001`
- Quadratic energy center: `0.2552055370433468`

## Next

Use the best safe energy candidate as the current target-driven response preset.
