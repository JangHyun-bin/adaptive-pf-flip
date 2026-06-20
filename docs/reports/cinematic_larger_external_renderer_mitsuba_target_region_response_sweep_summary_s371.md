# S371 Mitsuba Target Region Response Sweep Summary

Generated UTC: `2026-06-20T04:51:56.308106+00:00`
Summary JSON: `build/shots/s371_mitsuba_target_region_response_sweep_summary/target_region_response_sweep_summary.json`
Best candidate: `RR5`
Best max gap MAD: `23.459497813786008`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `RR5` | `ready` | 8 | 18.30976916152263 | 23.459497813786008 | 109 | `composite_grade_summary` |
| 2 | `RR4` | `ready` | 8 | 18.455697016460906 | 23.513741640946503 | 109 | `composite_grade_summary` |
| 3 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 4 | `RR6` | `ready` | 8 | 18.11920122813786 | 24.22597222222222 | 109 | `composite_grade_summary` |
| 5 | `RR1` | `ready` | 8 | 17.745132137345678 | 26.29263760288066 | 109 | `composite_grade_summary` |
| 6 | `RR2` | `ready` | 8 | 17.254877829218106 | 27.087542438271605 | 110 | `composite_grade_summary` |
| 7 | `RR3` | `ready` | 8 | 17.12274731545782 | 28.10377829218107 | 111 | `composite_grade_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `RR1`: `build/shots/s371_mitsuba_target_region_response_rr1_candidate_gap/renderer_target_gap_summary.json` (8.31 MB GIF)
- `RR2`: `build/shots/s371_mitsuba_target_region_response_rr2_candidate_gap/renderer_target_gap_summary.json` (8.30 MB GIF)
- `RR3`: `build/shots/s371_mitsuba_target_region_response_rr3_candidate_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `RR4`: `build/shots/s371_mitsuba_target_region_response_rr4_candidate_gap/renderer_target_gap_summary.json` (8.29 MB GIF)
- `RR5`: `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json` (8.29 MB GIF)
- `RR6`: `build/shots/s371_mitsuba_target_region_response_rr6_candidate_gap/renderer_target_gap_summary.json` (8.32 MB GIF)

## Next

Use RR5 as a diagnostic target-fit bridge, then port the bounded masks into renderer-native water and secondary response.
