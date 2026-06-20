# S420 Mitsuba Water Material Response Sweep Summary

Generated UTC: `2026-06-20T10:58:24.237042+00:00`
Summary JSON: `build/shots/s420_mitsuba_water_material_response_sweep/water_material_response_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `S417_WP4_H18_D90` | `ready` | 8 | 19.182991817772635 | 23.948739068930042 | 255 | `composite_grade_summary` |
| 4 | `S419_MMR8` | `ready` | 8 | 19.766804028420783 | 23.96551183127572 | 254 | `mitsuba_render_manifest` |
| 5 | `S419_MMR4` | `ready` | 8 | 19.785509178883743 | 23.96551183127572 | 254 | `mitsuba_render_manifest` |
| 6 | `S420_WRD3` | `ready` | 8 | 19.45410027649177 | 24.011120113168726 | 229 | `mitsuba_render_manifest` |
| 7 | `S420_WRD2` | `ready` | 8 | 19.455670733667695 | 24.011855709876542 | 222 | `mitsuba_render_manifest` |
| 8 | `S420_WRD1` | `ready` | 8 | 19.455844103652264 | 24.01211869855967 | 229 | `mitsuba_render_manifest` |
| 9 | `S420_WMR2` | `ready` | 8 | 19.477909995498973 | 24.01930491255144 | 239 | `mitsuba_render_manifest` |
| 10 | `S420_WMR1` | `ready` | 8 | 19.535587464634773 | 24.023451646090535 | 239 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S417_WP4_H18_D90`: `build/shots/s417_mitsuba_wp4_h18_d90_light_only_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S419_MMR8`: `build/shots/s419_mitsuba_water_mesh_response_mmr8_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S419_MMR4`: `build/shots/s419_mitsuba_water_mesh_response_mmr4_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S420_WRD3`: `build/shots/s420_mitsuba_water_material_response_wrd3_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `S420_WRD2`: `build/shots/s420_mitsuba_water_material_response_wrd2_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)
- `S420_WRD1`: `build/shots/s420_mitsuba_water_material_response_wrd1_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)
- `S420_WMR2`: `build/shots/s420_mitsuba_water_material_response_wmr2_target_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `S420_WMR1`: `build/shots/s420_mitsuba_water_material_response_wmr1_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

Do not promote duplicate water material response; move next to calibrated non-emissive mask texture/material modulation on the original water BSDF or a target-free light-mask response.
