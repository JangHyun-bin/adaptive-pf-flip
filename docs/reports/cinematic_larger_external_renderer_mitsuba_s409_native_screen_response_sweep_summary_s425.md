# S425 Mitsuba S409 Native Screen Response Sweep Summary

Generated UTC: `2026-06-20T11:44:42.436119+00:00`
Summary JSON: `build/shots/s425_mitsuba_s409_native_screen_response_sweep/native_gap_sweep_summary.json`
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
| 6 | `S425_S409_NativeScreenCombined` | `ready` | 8 | 19.22300106095679 | 23.98832690329218 | 226 | `mitsuba_render_manifest` |
| 7 | `S424_SprayLocalizedLR5` | `ready` | 8 | 19.222706886574073 | 23.98888310185185 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S425_S409_NativeScreenHighlight`: `build/shots/s425_mitsuba_s409_native_screen_response_highlight_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S425_S409_NativeScreenCombined`: `build/shots/s425_mitsuba_s409_native_screen_response_combined_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S424_SprayLocalizedLR5`: `build/shots/s424_mitsuba_s409_channel_spray_localized_lr5_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

S425 keeps the source-response-mask screen bridge usable for refined mask sources, but it does not improve visual target gap; move the next native renderer work to true water/volume material response rather than more screen cards.
