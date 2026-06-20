# S409 SF12 Source Highlight Sweep Summary

Generated UTC: `2026-06-20T09:03:38.902861+00:00`
Summary JSON: `build/shots/s409_mitsuba_sf12_source_highlight_sweep/source_highlight_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `SF12_H19` | `ready` | 8 | 18.72657222543724 | 23.68549704218107 | 182 | `composite_grade_summary` |
| 3 | `SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 4 | `SF12_H17` | `ready` | 8 | 18.816972173996913 | 23.698841306584363 | 170 | `composite_grade_summary` |
| 5 | `SF12_H16` | `ready` | 8 | 18.88112059542181 | 23.710983796296297 | 170 | `composite_grade_summary` |
| 6 | `SF12_H15` | `ready` | 8 | 18.92520190329218 | 23.71939236111111 | 170 | `composite_grade_summary` |
| 7 | `SF12_SprayFoam` | `ready` | 8 | 19.120776588220163 | 23.755951646090534 | 170 | `composite_grade_summary` |
| 8 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |

## Inputs

- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_H15`: `build/shots/s409_mitsuba_sf12_source_highlight_h15_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_H16`: `build/shots/s409_mitsuba_sf12_source_highlight_h16_target_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `SF12_H17`: `build/shots/s409_mitsuba_sf12_source_highlight_h17_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_H19`: `build/shots/s409_mitsuba_sf12_source_highlight_h19_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)

## Next

Promote the strongest visually acceptable SF12 source-highlight probe, then migrate the accepted highlight behavior into renderer-native material/export controls.
