# S415 Mitsuba Water Highlight Sweep Summary

Generated UTC: `2026-06-20T09:59:07.747572+00:00`
Summary JSON: `build/shots/s415_mitsuba_water_highlight_sweep/water_highlight_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SF12_SprayFoam` | `ready` | 8 | 19.120776588220163 | 23.755951646090534 | 170 | `composite_grade_summary` |
| 4 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 5 | `S415_WH4` | `ready` | 8 | 19.225447048611112 | 23.98679526748971 | 234 | `mitsuba_render_manifest` |
| 6 | `S415_WH3` | `ready` | 8 | 19.220799012988685 | 23.987263374485597 | 226 | `mitsuba_render_manifest` |
| 7 | `S415_WH2` | `ready` | 8 | 19.21965888631687 | 23.987466563786008 | 226 | `mitsuba_render_manifest` |
| 8 | `S415_WH1` | `ready` | 8 | 19.221269450874484 | 23.987836934156377 | 226 | `mitsuba_render_manifest` |
| 9 | `S411_SplitNative` | `ready` | 8 | 19.222873344264404 | 23.988294110082304 | 226 | `mitsuba_render_manifest` |
| 10 | `S415_WH5` | `ready` | 8 | 19.222352752057613 | 23.98888374485597 | 255 | `mitsuba_render_manifest` |
| 11 | `S414_LR4_Luma85` | `ready` | 8 | 19.222742091049383 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S411_SplitNative`: `build/shots/s411_mitsuba_sf12_h18_split_native_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S414_LR4_Luma85`: `build/shots/s414_mitsuba_localized_secondary_lr4_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S415_WH1`: `build/shots/s415_mitsuba_water_highlight_wh1_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S415_WH2`: `build/shots/s415_mitsuba_water_highlight_wh2_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S415_WH3`: `build/shots/s415_mitsuba_water_highlight_wh3_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S415_WH4`: `build/shots/s415_mitsuba_water_highlight_wh4_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S415_WH5`: `build/shots/s415_mitsuba_water_highlight_wh5_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Use WH4 as the best native water-highlight direction so far, but do not promote it over SS1; continue toward texture/volume response or combine with accepted SF12 dark attenuation.
