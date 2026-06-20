# S372 Mitsuba Source Region Response Sweep Summary

Generated UTC: `2026-06-20T05:00:50.867708+00:00`
Summary JSON: `build/shots/s372_mitsuba_source_region_response_sweep_summary/source_region_response_sweep_summary.json`
Best candidate: `RR5-target-fit`
Best max gap MAD: `23.459497813786008`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `RR5-target-fit` | `ready` | 8 | 18.30976916152263 | 23.459497813786008 | 109 | `composite_grade_summary` |
| 2 | `SR6` | `ready` | 8 | 18.95910357188786 | 23.703670267489713 | 170 | `composite_grade_summary` |
| 3 | `SR4` | `ready` | 8 | 18.98074250900206 | 23.70948238168724 | 170 | `composite_grade_summary` |
| 4 | `SR8` | `ready` | 8 | 19.035571068029835 | 23.715148533950618 | 170 | `composite_grade_summary` |
| 5 | `SR5` | `ready` | 8 | 19.094915444958847 | 23.72210262345679 | 170 | `composite_grade_summary` |
| 6 | `SR7` | `ready` | 8 | 19.103088429140943 | 23.72217142489712 | 170 | `composite_grade_summary` |
| 7 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 8 | `SR2` | `ready` | 8 | 19.424357397762346 | 24.370790895061727 | 183 | `composite_grade_summary` |
| 9 | `SR1` | `ready` | 8 | 19.675693721064814 | 24.46188014403292 | 192 | `composite_grade_summary` |
| 10 | `SR3` | `ready` | 8 | 20.55771010159465 | 25.22936921296296 | 211 | `composite_grade_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `RR5-target-fit`: `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json` (8.29 MB GIF)
- `SR1`: `build/shots/s372_mitsuba_source_region_response_sr1_candidate_gap/renderer_target_gap_summary.json` (8.15 MB GIF)
- `SR2`: `build/shots/s372_mitsuba_source_region_response_sr2_candidate_gap/renderer_target_gap_summary.json` (8.14 MB GIF)
- `SR3`: `build/shots/s372_mitsuba_source_region_response_sr3_candidate_gap/renderer_target_gap_summary.json` (8.15 MB GIF)
- `SR4`: `build/shots/s372_mitsuba_source_region_response_sr4_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SR5`: `build/shots/s372_mitsuba_source_region_response_sr5_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SR6`: `build/shots/s372_mitsuba_source_region_response_sr6_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SR7`: `build/shots/s372_mitsuba_source_region_response_sr7_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SR8`: `build/shots/s372_mitsuba_source_region_response_sr8_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

Use SR6 as the best target-free source-highlight response, then investigate renderer-native masks for the remaining RR5 gap.
