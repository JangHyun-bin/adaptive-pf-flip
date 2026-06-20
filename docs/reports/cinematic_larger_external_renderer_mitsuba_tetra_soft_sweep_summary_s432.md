# S432 Mitsuba Tetra Soft Water Mesh Sweep Summary

Generated UTC: `2026-06-20T12:20:02.490606+00:00`
Summary JSON: `build/shots/s432_mitsuba_tetra_soft_sweep/mitsuba_native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 4 | `S432_TetraSoftTS1` | `ready` | 8 | 19.427301633230453 | 24.167265303497942 | 227 | `mitsuba_render_manifest` |
| 5 | `S431_CameraCF2` | `ready` | 8 | 19.69298040444959 | 24.308006044238684 | 223 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S431_CameraCF2`: `build/shots/s431_mitsuba_camera_framing_cf2_target_gap/renderer_target_gap_summary.json` (8.08 MB GIF)
- `S432_TetraSoftTS1`: `build/shots/s432_mitsuba_tetra_soft_ts1_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)

## Next

Keep the water-mesh replacement tool, but reject this softer tetra reconstruction for the current target; next focus should shift to target-aligned secondary/surface-contact representation or a higher-fidelity meshing method, not another small smoothing sweep.
