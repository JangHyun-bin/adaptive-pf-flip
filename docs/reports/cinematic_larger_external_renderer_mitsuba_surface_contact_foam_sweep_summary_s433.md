# S433 Mitsuba Surface Contact Foam Sweep Summary

Generated UTC: `2026-06-20T12:29:02.461116+00:00`
Summary JSON: `build/shots/s433_mitsuba_surface_contact_foam_sweep/mitsuba_native_gap_sweep_summary.json`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `composite_grade_summary` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `composite_grade_summary` |
| 3 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 4 | `S433_SurfaceContactFoamSCF1` | `ready` | 8 | 19.222813223379628 | 23.98888374485597 | 226 | `mitsuba_render_manifest` |
| 5 | `S433_SurfaceContactFoamSCF2` | `ready` | 8 | 19.223752491640948 | 23.98888374485597 | 226 | `mitsuba_render_manifest` |
| 6 | `S433_SurfaceContactFoamSCF3` | `ready` | 8 | 19.22623191550926 | 23.98888374485597 | 226 | `mitsuba_render_manifest` |
| 7 | `S429_PhaseBillboardPB1` | `ready` | 8 | 19.302463027263375 | 24.143501157407407 | 230 | `mitsuba_render_manifest` |
| 8 | `S432_TetraSoftTS1` | `ready` | 8 | 19.427301633230453 | 24.167265303497942 | 227 | `mitsuba_render_manifest` |

## Inputs

- `S401_CR21_Profile`: `build/shots/s401_mitsuba_source_response_profile_cr21_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S409_SF12_H18`: `build/shots/s409_mitsuba_sf12_source_highlight_h18_target_gap/renderer_target_gap_summary.json` (8.27 MB GIF)
- `SS1_Native`: `build/shots/s409_mitsuba_ss1_native_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `S429_PhaseBillboardPB1`: `build/shots/s429_mitsuba_phase_volume_billboard_pb1_target_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `S432_TetraSoftTS1`: `build/shots/s432_mitsuba_tetra_soft_ts1_target_gap/renderer_target_gap_summary.json` (8.22 MB GIF)
- `S433_SurfaceContactFoamSCF1`: `build/shots/s433_mitsuba_surface_contact_foam_scf1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S433_SurfaceContactFoamSCF2`: `build/shots/s433_mitsuba_surface_contact_foam_scf2_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `S433_SurfaceContactFoamSCF3`: `build/shots/s433_mitsuba_surface_contact_foam_scf3_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Keep the native surface-contact foam geometry switch, but reject SCF1-SCF3 as target-gap improvements; next work should isolate which S401 source-response regions are not representable by current native water/secondary geometry before adding more patches.
