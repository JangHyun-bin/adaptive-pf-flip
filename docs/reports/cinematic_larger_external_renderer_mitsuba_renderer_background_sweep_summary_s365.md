# S365 Mitsuba Renderer Background Sweep Summary

Generated UTC: `2026-06-20T03:46:06.456051+00:00`
Summary JSON: `build/shots/s365_mitsuba_renderer_background_sweep_summary/renderer_background_sweep_summary.json`
Best candidate: `SV1-cache`
Best max gap MAD: `23.72217142489712`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `B2` | `ready` | 8 | 18.129457947530863 | 27.901911651234567 | 163 | `secondary_composite_summary` |
| 3 | `B1` | `ready` | 8 | 21.511723331404323 | 29.499659850823047 | 178 | `secondary_composite_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `B1`: `build/shots/s365_mitsuba_renderer_background_b1/candidate_gap/renderer_target_gap_summary.json` (8.15 MB GIF)
- `B2`: `build/shots/s365_mitsuba_renderer_background_b2/candidate_gap/renderer_target_gap_summary.json` (8.11 MB GIF)

## Next

Keep the S357/S362 background baseline; do not tune background radiance alone. Move next to camera/framing or material/secondary integration.
