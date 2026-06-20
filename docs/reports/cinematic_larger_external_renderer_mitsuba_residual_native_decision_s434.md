# S434 Mitsuba Residual Native Decision Summary

Generated UTC: `2026-06-20T12:31:30.261541+00:00`
Summary JSON: `build/shots/s434_mitsuba_residual_native_decision/mitsuba_native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 4 | `S433_SurfaceContactFoamSCF3` | `ready` | 8 | 19.22623191550926 | 23.98888374485597 | 226 | `mitsuba_render_manifest` |
| 5 | `S397_ResidualScreenCard` | `ready` | 8 | 19.222715486754115 | 23.988894675925927 | 226 | `mitsuba_render_manifest` |
| 6 | `S399_ResidualAugmentRA1` | `ready` | 8 | 19.22306568287037 | 23.98904320987654 | 226 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S397_ResidualScreenCard`: `build/shots/s397_mitsuba_residual_local_screen_card_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S399_ResidualAugmentRA1`: `build/shots/s399_mitsuba_residual_augmented_secondary_material_ra1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S433_SurfaceContactFoamSCF3`: `build/shots/s433_mitsuba_surface_contact_foam_scf3_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Do not add more low-level secondary patches yet; split S401 response into highlight, dark-primary, and channel-band intent, then implement only the high-F1 channel-band as a native secondary attenuation pass while keeping highlight/dark-primary as non-native reference gates.
