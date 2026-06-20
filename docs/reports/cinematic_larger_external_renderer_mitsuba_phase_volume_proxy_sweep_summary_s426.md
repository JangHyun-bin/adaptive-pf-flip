# S426 Mitsuba Phase Volume Proxy Sweep Summary

Generated UTC: `2026-06-20T11:48:18.438735+00:00`
Summary JSON: `build/shots/s426_mitsuba_phase_volume_proxy_sweep/native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `S417_WP4_H18_D90` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 4 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 5 | `S425_S409_NativeScreenHighlight` | `ready` | 8 | 19.22300106095679 | 23.98832690329218 | 226 | `mitsuba_render_manifest` |
| 6 | `S426_PhaseVolumePV1` | `ready` | 8 | 19.293451485339506 | 24.128806584362138 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S425_S409_NativeScreenHighlight`: `build/shots/s425_mitsuba_s409_native_screen_response_highlight_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S426_PhaseVolumePV1`: `build/shots/s426_mitsuba_phase_volume_proxy_pv1_target_gap/renderer_target_gap_summary.json` (8.31 MB GIF)

## Next

PV1 proves the phase-volume proxy path is wired and renderable, but opaque diffuse proxy spheres worsen the visual target gap; S427 should add phase-volume opacity/reflectance controls or a smoother volume shell before more tuning.
