# S368 Mitsuba Secondary Mixed Dual Sweep Summary

Generated UTC: `2026-06-20T04:13:22.967235+00:00`
Summary JSON: `build/shots/s368_mitsuba_secondary_mixed_dual_sweep_summary/secondary_mixed_dual_sweep_summary.json`
Best candidate: `SV1-cache`
Best max gap MAD: `23.72217142489712`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `DV4` | `ready` | 8 | 19.10481328768004 | 23.72891139403292 | 170 | `secondary_composite_summary` |
| 3 | `DV5` | `ready` | 8 | 19.106409223894033 | 23.73129822530864 | 170 | `secondary_composite_summary` |
| 4 | `DV3` | `ready` | 8 | 19.10643928433642 | 23.739014917695474 | 170 | `secondary_composite_summary` |
| 5 | `DV1` | `ready` | 8 | 19.11315915959362 | 23.742681327160494 | 170 | `secondary_composite_summary` |
| 6 | `DV2` | `ready` | 8 | 19.11270174254115 | 23.751523276748973 | 170 | `secondary_composite_summary` |
| 7 | `MX3` | `ready` | 8 | 19.18636847350823 | 23.855683513374487 | 170 | `secondary_composite_summary` |
| 8 | `MX2` | `ready` | 8 | 19.21554615162037 | 23.901651877572018 | 170 | `secondary_composite_summary` |
| 9 | `MX1` | `ready` | 8 | 19.202326469264403 | 23.90184799382716 | 170 | `secondary_composite_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `MX1`: `build/shots/s368_mitsuba_secondary_mixed_mx1_candidate_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `MX2`: `build/shots/s368_mitsuba_secondary_mixed_mx2_candidate_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `MX3`: `build/shots/s368_mitsuba_secondary_mixed_mx3_candidate_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `DV1`: `build/shots/s368_mitsuba_secondary_dual_dv1_candidate_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `DV2`: `build/shots/s368_mitsuba_secondary_dual_dv2_candidate_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `DV3`: `build/shots/s368_mitsuba_secondary_dual_dv3_candidate_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `DV4`: `build/shots/s368_mitsuba_secondary_dual_dv4_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `DV5`: `build/shots/s368_mitsuba_secondary_dual_dv5_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

Keep SV1-cache as the current metric baseline; visibility-only tuning is exhausted, so move next to target-trained profile fitting or renderer/material response.
