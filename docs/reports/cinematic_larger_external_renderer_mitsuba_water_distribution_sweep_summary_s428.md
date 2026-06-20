# S428 Mitsuba Water Distribution Sweep Summary

Generated UTC: `2026-06-20T11:54:31.459864+00:00`
Summary JSON: `build/shots/s428_mitsuba_water_distribution_sweep/native_gap_sweep_summary.json`
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
| 6 | `S428_WaterGGX_WG2` | `ready` | 8 | 19.26890006108539 | 24.024744727366254 | 221 | `mitsuba_render_manifest` |
| 7 | `S428_WaterGGX_WG1` | `ready` | 8 | 19.288122026105967 | 24.049515817901234 | 212 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S427_PhaseVolumePV2`: `build/shots/s427_mitsuba_phase_volume_proxy_pv2_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `S428_WaterGGX_WG1`: `build/shots/s428_mitsuba_water_distribution_wg1_target_gap/renderer_target_gap_summary.json` (8.43 MB GIF)
- `S428_WaterGGX_WG2`: `build/shots/s428_mitsuba_water_distribution_wg2_target_gap/renderer_target_gap_summary.json` (8.38 MB GIF)

## Next

S428 keeps the water-distribution option available, but GGX does not improve the target gap; keep the default water BSDF baseline and move next to smoother volume/lighting response rather than more global water BSDF tweaks.
