# S414 Mitsuba Localized Secondary Sweep Summary

Generated UTC: `2026-06-20T09:49:42.631908+00:00`
Summary JSON: `build/shots/s414_mitsuba_localized_secondary_sweep/localized_secondary_sweep_summary.json`
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
| 6 | `S414_LR4_Luma85` | `ready` | 8 | 19.222742091049383 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |
| 7 | `S414_LR3_Luma95` | `ready` | 8 | 19.22274241255144 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |
| 8 | `S413_MR2_Secondary` | `ready` | 8 | 19.22273654513889 | 23.98916859567901 | 226 | `mitsuba_render_manifest` |
| 9 | `S414_LR1_Wide` | `ready` | 8 | 19.222740805041152 | 23.98917309670782 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S411_SplitNative`: `build/shots/s411_mitsuba_sf12_h18_split_native_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S413_MR2_Secondary`: `build/shots/s413_mitsuba_material_response_mr2_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S414_LR1_Wide`: `build/shots/s414_mitsuba_localized_secondary_lr1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S414_LR3_Luma95`: `build/shots/s414_mitsuba_localized_secondary_lr3_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S414_LR4_Luma85`: `build/shots/s414_mitsuba_localized_secondary_lr4_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Do not promote localized secondary attenuation if it remains below SS1; move S415 toward localized highlight/light or actual source-response texture masks.
