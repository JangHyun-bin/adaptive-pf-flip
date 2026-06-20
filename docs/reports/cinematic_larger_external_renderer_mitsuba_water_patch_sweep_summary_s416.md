# S416 Mitsuba Water Patch Sweep Summary

Generated UTC: `2026-06-20T10:06:22.723779+00:00`
Summary JSON: `build/shots/s416_mitsuba_water_patch_sweep/water_patch_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SF12_SprayFoam` | `ready` | 8 | 19.120776588220163 | 23.755951646090534 | 170 | `composite_grade_summary` |
| 4 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 5 | `S416_WP4` | `ready` | 8 | 19.31142160172325 | 23.97967785493827 | 255 | `mitsuba_render_manifest` |
| 6 | `S416_WP5` | `ready` | 8 | 19.361695441100824 | 23.981273148148148 | 255 | `mitsuba_render_manifest` |
| 7 | `S416_WP2` | `ready` | 8 | 19.254283854166665 | 23.9812795781893 | 253 | `mitsuba_render_manifest` |
| 8 | `S416_WP3` | `ready` | 8 | 19.341100742669752 | 23.983085133744854 | 255 | `mitsuba_render_manifest` |
| 9 | `S416_WP1` | `ready` | 8 | 19.24947064686214 | 23.985679655349795 | 253 | `mitsuba_render_manifest` |
| 10 | `S415_WH4` | `ready` | 8 | 19.225447048611112 | 23.98679526748971 | 234 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SF12_SprayFoam`: `build/shots/s408_mitsuba_aov_attenuation_sprayfoam_sf12_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S415_WH4`: `build/shots/s415_mitsuba_water_highlight_wh4_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S416_WP1`: `build/shots/s416_mitsuba_water_patch_wp1_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S416_WP2`: `build/shots/s416_mitsuba_water_patch_wp2_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S416_WP3`: `build/shots/s416_mitsuba_water_patch_wp3_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S416_WP4`: `build/shots/s416_mitsuba_water_patch_wp4_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S416_WP5`: `build/shots/s416_mitsuba_water_patch_wp5_target_gap/renderer_target_gap_summary.json` (8.23 MB GIF)

## Next

Carry WP4 forward as the best native water patch probe, but combine it with accepted SF12 dark attenuation or move to a true texture/volume mask before promotion.
