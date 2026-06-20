# S375 Mitsuba Selective Dark Secondary Response Sweep Summary

Generated UTC: `2026-06-20T05:26:50.463147+00:00`
Summary JSON: `build/shots/s375_mitsuba_selective_dark_secondary_response_sweep_summary/selective_dark_secondary_response_sweep_summary.json`
Best candidate: `RR5-target-fit`
Best max gap MAD: `23.459497813786008`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `RR5-target-fit` | `ready` | 8 | 18.30976916152263 | 23.459497813786008 | 109 | `composite_grade_summary` |
| 2 | `DS6` | `ready` | 8 | 18.66258061664095 | 23.56051440329218 | 182 | `composite_grade_summary` |
| 3 | `DS8` | `ready` | 8 | 18.66038974086934 | 23.564360853909466 | 182 | `composite_grade_summary` |
| 4 | `DS5` | `ready` | 8 | 18.66052332497428 | 23.570373585390946 | 182 | `composite_grade_summary` |
| 5 | `DS7` | `ready` | 8 | 18.66416272826646 | 23.57534915123457 | 182 | `composite_grade_summary` |
| 6 | `DS3` | `ready` | 8 | 18.66587271733539 | 23.586715534979422 | 182 | `composite_grade_summary` |
| 7 | `DS2` | `ready` | 8 | 18.676179751800408 | 23.606159979423868 | 182 | `composite_grade_summary` |
| 8 | `DS1` | `ready` | 8 | 18.68669519997428 | 23.62225630144033 | 182 | `composite_grade_summary` |
| 9 | `DS4` | `ready` | 8 | 18.73794528034979 | 23.640576131687244 | 182 | `composite_grade_summary` |
| 10 | `SR19-highlight` | `ready` | 8 | 18.709468476723252 | 23.651716820987655 | 182 | `composite_grade_summary` |
| 11 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `RR5-target-fit`: `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json` (8.29 MB GIF)
- `SR19-highlight`: `build/shots/s374_mitsuba_source_highlight_response_sr19_candidate_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `DS1`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds1_candidate_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `DS2`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds2_candidate_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `DS3`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds3_candidate_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `DS4`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds4_candidate_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `DS5`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds5_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `DS6`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds6_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `DS7`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds7_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `DS8`: `build/shots/s375_mitsuba_selective_dark_secondary_response_ds8_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

Use DS6 as the current target-free combined highlight/dark-secondary baseline, then seek geometry-native masks to close the remaining RR5 gap.
