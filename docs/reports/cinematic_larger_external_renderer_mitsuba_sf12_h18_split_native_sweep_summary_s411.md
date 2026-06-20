# S411 SF12 H18 Split Native Sweep Summary

Generated UTC: `2026-06-20T09:20:38.431743+00:00`
Summary JSON: `build/shots/s411_mitsuba_sf12_h18_split_native_sweep/split_native_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SF12_SprayFoam` | `ready` | 8 | 19.120776588220163 | 23.755951646090534 | 170 | `composite_grade_summary` |
| 4 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 5 | `S411_SplitNative` | `ready` | 8 | 19.222873344264404 | 23.988294110082304 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S411_SplitNative`: `build/shots/s411_mitsuba_sf12_h18_split_native_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)

## Next

Do not promote the S411 screen-card/sprite native candidate; use the result to move S412 toward real material/export-side modulation rather than camera-plane inserts.
