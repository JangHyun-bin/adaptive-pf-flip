# S424 Mitsuba S409 Channel Spray Localized Sweep Summary

Generated UTC: `2026-06-20T11:36:13.699753+00:00`
Summary JSON: `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5_sweep/native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `S417_CurrentBest` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 4 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 5 | `S424_SprayLocalizedLR5` | `ready` | 8 | 19.222706886574073 | 23.98888310185185 | 226 | `mitsuba_render_manifest` |
| 6 | `S414_LR4_Luma85` | `ready` | 8 | 19.222742091049383 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S417_CurrentBest`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S414_LR4_Luma85`: `build/shots/s414_mitsuba_localized_secondary_lr4_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S424_SprayLocalizedLR5`: `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

S424 confirms spray-only localized secondary material response is still worse than SS1 and far behind the light/highlight response candidates; move the next native renderer work to water/highlight/volume response instead of secondary-only attenuation.
