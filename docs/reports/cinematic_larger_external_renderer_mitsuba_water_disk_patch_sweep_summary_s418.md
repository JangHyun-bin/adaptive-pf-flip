# S418 Mitsuba Water Disk Patch Sweep Summary

Generated UTC: `2026-06-20T10:30:56.174520+00:00`
Summary JSON: `build/shots/s418_mitsuba_water_disk_patch_sweep/water_disk_patch_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SF12_SprayFoam` | `ready` | 8 | 19.120776588220163 | 23.755951646090534 | 170 | `composite_grade_summary` |
| 4 | `S417_WP4_H18_D90` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 5 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 6 | `S416_WP4` | `ready` | 8 | 19.31142160172325 | 23.97967785493827 | 255 | `mitsuba_render_manifest` |
| 7 | `S418_DP2` | `ready` | 8 | 19.237632458847738 | 23.980085519547327 | 232 | `mitsuba_render_manifest` |
| 8 | `S418_DP1` | `ready` | 8 | 19.2402053594393 | 23.99034465020576 | 226 | `mitsuba_render_manifest` |
| 9 | `S418_DP3` | `ready` | 8 | 19.276629533179012 | 24.00698431069959 | 226 | `mitsuba_render_manifest` |
| 10 | `S418_DP5` | `ready` | 8 | 19.711589988425924 | 24.014149305555556 | 255 | `mitsuba_render_manifest` |
| 11 | `S418_DP4` | `ready` | 8 | 19.599884420010287 | 24.130503472222223 | 255 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S416_WP4`: `build/shots/s416_mitsuba_water_patch_wp4_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S418_DP1`: `build/shots/s418_mitsuba_water_disk_patch_dp1_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S418_DP2`: `build/shots/s418_mitsuba_water_disk_patch_dp2_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S418_DP3`: `build/shots/s418_mitsuba_water_disk_patch_dp3_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S418_DP4`: `build/shots/s418_mitsuba_water_disk_patch_dp4_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S418_DP5`: `build/shots/s418_mitsuba_water_disk_patch_dp5_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)

## Next

Keep DP2 only as evidence that clustered disk patches are close to WP4 but not enough; move next to texture/volume or material-mask based water highlight controls.
