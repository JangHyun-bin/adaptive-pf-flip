# S427 Mitsuba Phase Volume Proxy Material Sweep Summary

Generated UTC: `2026-06-20T11:51:32.753667+00:00`
Summary JSON: `build/shots/s427_mitsuba_phase_volume_proxy_material_sweep/native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `S417_WP4_H18_D90` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 4 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 5 | `S427_PhaseVolumePV2` | `ready` | 8 | 19.232646444187242 | 24.00604809670782 | 226 | `mitsuba_render_manifest` |
| 6 | `S427_PhaseVolumePV3` | `ready` | 8 | 19.23480758101852 | 24.008227880658435 | 226 | `mitsuba_render_manifest` |
| 7 | `S426_PhaseVolumePV1` | `ready` | 8 | 19.293451485339506 | 24.128806584362138 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S426_PhaseVolumePV1`: `build/shots/s426_mitsuba_phase_volume_proxy_pv1_target_gap/renderer_target_gap_summary.json` (8.31 MB GIF)
- `S427_PhaseVolumePV2`: `build/shots/s427_mitsuba_phase_volume_proxy_pv2_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `S427_PhaseVolumePV3`: `build/shots/s427_mitsuba_phase_volume_proxy_pv3_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

S427 makes phase-volume proxy material tunable and confirms low-opacity proxies improve over opaque PV1 but still trail SS1; next work should replace sampled spheres with a smoother shell/field representation or tune water BSDF/transmittance instead of adding more proxy spheres.
