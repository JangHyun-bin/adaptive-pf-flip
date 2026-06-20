# S463 Mitsuba Signed Response Strength Sweep Decision

Generated UTC: `2026-06-20T15:34:00+00:00`

## Decision

Promote `sr4_more_requests` as the current best signed-response visual calibration candidate.

It improves over S462 on both mean gap MAD and max gap MAD while keeping max absolute gap at `176`. It also beats `SS1_Native` on mean gap MAD and max gap MAD, although `SS1_Native` still has the lower max absolute gap (`170`).

## Evidence

- Response tool: `tools/apply_mitsuba_signed_gap_response.py`
- Signed analysis: `build/shots/s461_mitsuba_mt8_signed_target_gap/signed_target_gap_analysis.json`
- Decision gallery report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_response_strength_sweep_decision_gallery_s463.md`
- Best target-gap summary: `build/shots/s463_mitsuba_signed_response_strength_sweep/sr4_more_requests_target_gap/renderer_target_gap_summary.json`
- Best response summary: `build/shots/s463_mitsuba_signed_response_strength_sweep/sr4_more_requests/signed_gap_response_summary.json`
- Best gallery: `build/shots/s463_mitsuba_signed_response_strength_sweep/sr4_more_requests_target_gap/gallery/index.html`

## Ranking

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `sr4_more_requests` | `19.10240579989712` | `23.950307355967077` | `176` | Best S463 promotion candidate. |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` | Lower max gap, but weaker mean and max MAD. |
| `sr3_stronger` | `19.089487686471195` | `23.953335905349793` | `176` | Best mean, but no max-MAD improvement. |
| `S462` | `19.10439911265432` | `23.953335905349793` | `176` | Previous signed response baseline. |
| `sr2_s462` | `19.10439911265432` | `23.953335905349793` | `176` | S462 reproduction. |
| `sr1_soft` | `19.11442097479424` | `23.953335905349793` | `176` | Too weak. |
| `S460_mt8` | `19.139490097736626` | `23.953335905349793` | `177` | Material/tone base. |

## Response Settings

| Candidate | Requests | Strength Scale | Max Delta | Max Changed Coverage | Mean Applied Abs Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `sr1_soft` | `8` | `0.25` | `18` | `0.01876929012345679` | `5.613548828335913` |
| `sr2_s462` | `8` | `0.35` | `24` | `0.019110725308641975` | `7.54376749490272` |
| `sr3_stronger` | `8` | `0.50` | `32` | `0.019425154320987653` | `10.392576134712083` |
| `sr4_more_requests` | `12` | `0.35` | `24` | `0.019110725308641975` | `7.571433260034789` |

## Interpretation

Increasing strength alone (`sr3_stronger`) improves the average but leaves the worst-frame MAD unchanged. Adding more bounded requests at the S462 strength (`sr4_more_requests`) is better: it reduces the worst-frame MAD without increasing max absolute gap.

This keeps the branch aligned with the main visual goal: target the missing highlights locally instead of globally pushing material brightness. The remaining risk is that this is still image-space response, not a renderer-native light/material solution.

## Next

S464 should convert the `sr4_more_requests` behavior toward renderer-native response controls or run a strict renderer-native parity candidate. Keep the promotion gate: max absolute gap must stay at or below `176`, and max gap MAD should stay below `23.951853137860084`.
