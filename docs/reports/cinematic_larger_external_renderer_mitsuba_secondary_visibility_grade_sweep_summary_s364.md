# S364 Mitsuba Secondary Visibility Grade Sweep Summary

Generated UTC: `2026-06-20T03:40:45.076030+00:00`
Summary JSON: `build/shots/s364_mitsuba_secondary_visibility_grade_sweep_summary/secondary_visibility_grade_sweep_summary.json`
Best candidate: `SV1-cache`
Best max gap MAD: `23.72217142489712`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `G3` | `ready` | 8 | 20.5120418595679 | 31.732736625514402 | 251 | `composite_grade_summary` |
| 3 | `G1` | `ready` | 8 | 18.76499035493827 | 36.446965663580244 | 252 | `composite_grade_summary` |
| 4 | `G2` | `ready` | 8 | 19.972234278549383 | 46.3463850308642 | 252 | `composite_grade_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `G1`: `build/shots/s364_mitsuba_secondary_visibility_grade_g1_candidate_gap/renderer_target_gap_summary.json` (9.89 MB GIF)
- `G2`: `build/shots/s364_mitsuba_secondary_visibility_grade_g2_candidate_gap/renderer_target_gap_summary.json` (9.86 MB GIF)
- `G3`: `build/shots/s364_mitsuba_secondary_visibility_grade_g3_candidate_gap/renderer_target_gap_summary.json` (9.72 MB GIF)

## Next

Keep SV1-cache as the baseline and stop broad post-grade tuning; move tone matching into renderer-facing background/camera/material parameters.
