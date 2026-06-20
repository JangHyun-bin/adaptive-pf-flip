# S419 Mitsuba Water Mesh Response Sweep Summary

Generated UTC: `2026-06-20T10:43:02.393643+00:00`
Summary JSON: `build/shots/s419_mitsuba_water_mesh_response_sweep/water_mesh_response_sweep_summary.json`
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
| 6 | `S419_MMR8` | `ready` | 8 | 19.766804028420783 | 23.96551183127572 | 254 | `mitsuba_render_manifest` |
| 7 | `S419_MMR4` | `ready` | 8 | 19.785509178883743 | 23.96551183127572 | 254 | `mitsuba_render_manifest` |
| 8 | `S419_MMR5` | `ready` | 8 | 19.465720968364195 | 23.965932998971194 | 233 | `mitsuba_render_manifest` |
| 9 | `S419_MMR9` | `ready` | 8 | 19.33238522376543 | 23.96646154835391 | 249 | `mitsuba_render_manifest` |
| 10 | `S416_WP4` | `ready` | 8 | 19.31142160172325 | 23.97967785493827 | 255 | `mitsuba_render_manifest` |
| 11 | `S418_DP2` | `ready` | 8 | 19.237632458847738 | 23.980085519547327 | 232 | `mitsuba_render_manifest` |
| 12 | `S419_MMR1` | `ready` | 8 | 20.027209683641978 | 24.858103137860084 | 253 | `mitsuba_render_manifest` |
| 13 | `S419_MMR2` | `ready` | 8 | 20.08773767039609 | 25.083195730452676 | 255 | `mitsuba_render_manifest` |
| 14 | `S419_MMR3` | `ready` | 8 | 20.722426134902264 | 28.17601980452675 | 253 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S416_WP4`: `build/shots/s416_mitsuba_water_patch_wp4_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S418_DP2`: `build/shots/s418_mitsuba_water_disk_patch_dp2_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S419_MMR1`: `build/shots/s419_mitsuba_water_mesh_response_mmr1_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S419_MMR2`: `build/shots/s419_mitsuba_water_mesh_response_mmr2_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S419_MMR3`: `build/shots/s419_mitsuba_water_mesh_response_mmr3_target_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `S419_MMR4`: `build/shots/s419_mitsuba_water_mesh_response_mmr4_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S419_MMR5`: `build/shots/s419_mitsuba_water_mesh_response_mmr5_target_gap/renderer_target_gap_summary.json` (8.28 MB GIF)
- `S419_MMR8`: `build/shots/s419_mitsuba_water_mesh_response_mmr8_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S419_MMR9`: `build/shots/s419_mitsuba_water_mesh_response_mmr9_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

Carry MMR4/MMR8 only as native mesh-mask evidence; S420 should move to renderer-side mask texture/material response or a calibrated post-free light mask rather than emissive overlay faces.
