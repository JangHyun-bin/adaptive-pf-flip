# S417 Mitsuba WP4 Light Only Sweep Summary

Generated UTC: `2026-06-20T10:18:25.561340+00:00`
Summary JSON: `build/shots/s417_mitsuba_wp4_light_only_sweep/wp4_light_only_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SF12_SprayFoam` | `ready` | 8 | 19.120776588220163 | 23.755951646090534 | 170 | `composite_grade_summary` |
| 4 | `S417_WP4_H18_D90` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 5 | `S417_WP4_H18_T130` | `ready` | 8 | 19.159292775848765 | 23.94876350308642 | 255 | `composite_grade_summary` |
| 6 | `S417_WP4_H18_LightOnly` | `ready` | 8 | 19.18498119212963 | 23.949612911522635 | 255 | `composite_grade_summary` |
| 7 | `S417_WP4_H18_S075_D110` | `ready` | 8 | 19.195101433899175 | 23.951015303497943 | 255 | `composite_grade_summary` |
| 8 | `S417_WP4_H17_LightOnly` | `ready` | 8 | 19.200016557355966 | 23.951739326131687 | 255 | `composite_grade_summary` |
| 9 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 10 | `S417_WP4_H19_LightOnly` | `ready` | 8 | 19.19278734246399 | 23.95417309670782 | 255 | `composite_grade_summary` |
| 11 | `S417_WP4_H15_LightOnly` | `ready` | 8 | 19.234254195601853 | 23.959123585390948 | 255 | `composite_grade_summary` |
| 12 | `S416_WP4` | `ready` | 8 | 19.31142160172325 | 23.97967785493827 | 255 | `mitsuba_render_manifest` |
| 13 | `S417_WP4_SF12_H18` | `ready` | 8 | 19.287424125514402 | 24.126077031893004 | 255 | `composite_grade_summary` |
| 14 | `S417_WP4_SF12_H15` | `ready` | 8 | 19.336697128986625 | 24.135587705761317 | 255 | `composite_grade_summary` |
| 15 | `S417_WP4_SF12_DarkOnly` | `ready` | 8 | 19.413864535108026 | 24.156141975308643 | 255 | `composite_grade_summary` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S416_WP4`: `build/shots/s416_mitsuba_water_patch_wp4_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S417_WP4_SF12_DarkOnly`: `build/shots/s417_mitsuba_wp4_sf12_dark_only_target_gap/renderer_target_gap_summary.json` (8.18 MB GIF)
- `S417_WP4_H15_LightOnly`: `build/shots/s417_mitsuba_wp4_h15_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S417_WP4_H17_LightOnly`: `build/shots/s417_mitsuba_wp4_h17_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S417_WP4_H18_LightOnly`: `build/shots/s417_mitsuba_wp4_h18_light_only_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `S417_WP4_H18_T130`: `build/shots/s417_mitsuba_wp4_h18_t130_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S417_WP4_H18_S075_D110`: `build/shots/s417_mitsuba_wp4_h18_s075_d110_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S417_WP4_H19_LightOnly`: `build/shots/s417_mitsuba_wp4_h19_light_only_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S417_WP4_SF12_H15`: `build/shots/s417_mitsuba_wp4_sf12_h15_combined_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S417_WP4_SF12_H18`: `build/shots/s417_mitsuba_wp4_sf12_h18_combined_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)

## Next

Carry S417_WP4_H18_D90 as the best WP4 upper-bound response; do not carry the SF12 dark-band combination, which worsens the target gap.
