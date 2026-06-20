# S421 Mitsuba Water Mask Material Split Sweep Summary

Generated UTC: `2026-06-20T11:10:38.712889+00:00`
Summary JSON: `build/shots/s421_mitsuba_water_mask_material_split_sweep/water_mask_material_split_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `S417_WP4_H18_D90` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 4 | `S421_WP4_WMS4_H18_D90` | `ready` | 8 | 19.187023533950615 | 23.95027520576132 | 255 | `composite_grade_summary` |
| 5 | `S421_WP4_WMS1_H18_D90` | `ready` | 8 | 19.183271122685184 | 23.950648791152265 | 255 | `composite_grade_summary` |
| 6 | `S417_WP4` | `ready` | 8 | 19.31142160172325 | 23.97967785493827 | 255 | `mitsuba_render_manifest` |
| 7 | `S421_WP4_WMS4_Native` | `ready` | 8 | 19.31354608731996 | 23.980340149176953 | 255 | `mitsuba_render_manifest` |
| 8 | `S421_WMS1_Native` | `ready` | 8 | 19.222394788451645 | 23.98975758744856 | 219 | `mitsuba_render_manifest` |
| 9 | `S421_WMS3_Native` | `ready` | 8 | 19.226239310056584 | 23.989835390946503 | 219 | `mitsuba_render_manifest` |
| 10 | `S420_WRD3` | `ready` | 8 | 19.45410027649177 | 24.011120113168726 | 229 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S421_WP4_WMS4_H18_D90`: `build/shots/s421_mitsuba_wp4_wms4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S421_WP4_WMS1_H18_D90`: `build/shots/s421_mitsuba_wp4_wms1_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S417_WP4`: `build/shots/s416_mitsuba_water_patch_wp4_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S421_WP4_WMS4_Native`: `build/shots/s421_mitsuba_wp4_wms4_native_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S421_WMS1_Native`: `build/shots/s421_mitsuba_water_mask_material_split_wms1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S421_WMS3_Native`: `build/shots/s421_mitsuba_water_mask_material_split_wms3_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S420_WRD3`: `build/shots/s420_mitsuba_water_material_response_wrd3_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)

## Next

Do not promote split-water material over S417; move next to renderer-native calibrated light-mask/response integration or inspect the current best visual gallery for non-MAD artifacts.
