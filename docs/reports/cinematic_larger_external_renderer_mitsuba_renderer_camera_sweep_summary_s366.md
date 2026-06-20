# S366 Mitsuba Renderer Camera Sweep Summary

Generated UTC: `2026-06-20T03:52:26.454679+00:00`
Summary JSON: `build/shots/s366_mitsuba_renderer_camera_sweep_summary/renderer_camera_sweep_summary.json`
Best candidate: `SV1-cache`
Best max gap MAD: `23.72217142489712`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `CF2` | `ready` | 8 | 19.448651379243827 | 24.04738297325103 | 205 | `secondary_composite_summary` |
| 3 | `CF1` | `ready` | 8 | 19.653690441743827 | 24.0534754372428 | 211 | `secondary_composite_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `CF1`: `build/shots/s366_mitsuba_renderer_camera_cf1/candidate_gap/renderer_target_gap_summary.json` (8.29 MB GIF)
- `CF2`: `build/shots/s366_mitsuba_renderer_camera_cf2/candidate_gap/renderer_target_gap_summary.json` (8.33 MB GIF)

## Next

Keep the S357/S362 camera baseline; camera-only changes are close but do not beat the SV1-cache hard gate. Move next to material/secondary integration.
