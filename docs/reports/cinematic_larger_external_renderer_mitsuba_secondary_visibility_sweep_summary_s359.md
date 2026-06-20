# S359 Mitsuba Secondary Visibility Sweep Summary

Generated UTC: `2026-06-20T03:13:50.064038+00:00`
Summary JSON: `build/shots/s359_mitsuba_secondary_visibility_sweep_summary/secondary_visibility_sweep_summary.json`
Best candidate: `SV1`
Best max gap MAD: `23.72217142489712`
Public SV1 preview: `https://reductions-kde-panels-wrote.trycloudflare.com/index.html`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `SV3` | `ready` | 8 | 19.159634291409464 | 23.830943287037037 | 170 | `secondary_composite_summary` |
| 3 | `SV2` | `ready` | 8 | 19.110620177469137 | 23.900221836419753 | 170 | `secondary_composite_summary` |
| 4 | `SS1` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |

## Inputs

- `SS1`: `build/shots/s359_mitsuba_secondary_visibility_ss1_render_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `SV1`: `build/shots/s359_mitsuba_secondary_visibility_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SV2`: `build/shots/s359_mitsuba_secondary_visibility_sv2_candidate_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `SV3`: `build/shots/s359_mitsuba_secondary_visibility_sv3_candidate_gap/renderer_target_gap_summary.json` (8.24 MB GIF)

## Next

Use SV1 as the diagnostic visibility bridge baseline, then port the same bounded secondary lift into a renderer-facing cache/pass.
