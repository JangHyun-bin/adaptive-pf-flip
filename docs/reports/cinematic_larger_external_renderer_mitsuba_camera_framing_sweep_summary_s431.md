# S431 Mitsuba Camera Framing Sweep Summary

Generated UTC: `2026-06-20T12:10:28.024297+00:00`
Summary JSON: `build/shots/s431_mitsuba_camera_framing_sweep/mitsuba_native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 4 | `S429_PhaseBillboardPB1` | `ready` | 8 | 19.302463027263375 | 24.143501157407407 | 230 | `mitsuba_render_manifest` |
| 5 | `S431_CameraCF2` | `ready` | 8 | 19.69298040444959 | 24.308006044238684 | 223 | `mitsuba_render_manifest` |
| 6 | `S431_CameraCF3` | `ready` | 8 | 19.805515769675925 | 24.310988940329217 | 227 | `mitsuba_render_manifest` |
| 7 | `S431_CameraCF1` | `ready` | 8 | 19.859201308513374 | 24.510308641975307 | 224 | `mitsuba_render_manifest` |
| 8 | `S430_WaterTransmittanceWT1` | `ready` | 8 | 20.39433232060185 | 26.585197402263375 | 229 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S429_PhaseBillboardPB1`: `build/shots/s429_mitsuba_phase_volume_billboard_pb1_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S430_WaterTransmittanceWT1`: `build/shots/s430_mitsuba_water_transmittance_wt1_target_gap/renderer_target_gap_summary.json` (8.19 MB GIF)
- `S431_CameraCF1`: `build/shots/s431_mitsuba_camera_framing_cf1_target_gap/renderer_target_gap_summary.json` (8.34 MB GIF)
- `S431_CameraCF2`: `build/shots/s431_mitsuba_camera_framing_cf2_target_gap/renderer_target_gap_summary.json` (8.08 MB GIF)
- `S431_CameraCF3`: `build/shots/s431_mitsuba_camera_framing_cf3_target_gap/renderer_target_gap_summary.json` (8.24 MB GIF)

## Next

Reject narrow camera-only framing changes for this target; keep SS1_Native as native baseline and move next to true water surface or volume export rather than FOV/distance tuning.
