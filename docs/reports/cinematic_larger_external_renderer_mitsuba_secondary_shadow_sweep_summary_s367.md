# S367 Mitsuba Secondary Shadow Sweep Summary

Generated UTC: `2026-06-20T04:03:36.586207+00:00`
Summary JSON: `build/shots/s367_mitsuba_secondary_shadow_sweep_summary/secondary_shadow_sweep_summary.json`
Best candidate: `SV1-cache`
Best max gap MAD: `23.72217142489712`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `SO1-shadow` | `ready` | 8 | 19.272146910365226 | 24.144057998971192 | 170 | `secondary_composite_summary` |
| 3 | `SO2-shadow` | `ready` | 8 | 19.309630272633747 | 24.19077160493827 | 170 | `secondary_composite_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SO1-shadow`: `build/shots/s367_mitsuba_secondary_shadow_so1_candidate_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `SO2-shadow`: `build/shots/s367_mitsuba_secondary_shadow_so2_candidate_gap/renderer_target_gap_summary.json` (8.20 MB GIF)

## Next

Reject shadow-only secondary compositing for now; move the remaining gap into renderer/material integration or a target-trained visibility profile.
