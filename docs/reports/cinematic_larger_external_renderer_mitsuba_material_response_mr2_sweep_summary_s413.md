# S413 Mitsuba Material Response MR2 Sweep Summary

Generated UTC: `2026-06-20T09:36:19.508769+00:00`
Summary JSON: `build/shots/s413_mitsuba_material_response_mr2_sweep/material_response_sweep_summary.json`
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
| 6 | `S413_MR2_Secondary` | `ready` | 8 | 19.22273654513889 | 23.98916859567901 | 226 | `mitsuba_render_manifest` |
| 7 | `S412_MR1_Material` | `ready` | 8 | 19.22435016396605 | 23.990219907407408 | 230 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S411_SplitNative`: `build/shots/s411_mitsuba_sf12_h18_split_native_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S412_MR1_Material`: `build/shots/s412_mitsuba_material_response_mr1_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S413_MR2_Secondary`: `build/shots/s413_mitsuba_material_response_mr2_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Do not promote MR2; move S414 toward localized AOV/material response or a native projection mask, not whole-frame material scaling.
