# S458 Mitsuba Residual Response Preset

Generated UTC: `2026-06-20T14:53:00+00:00`

## Preset

Name: `residual_response_rr4_lf47_mid`

This preset is the current best safe target-driven residual response chain. It is not a final renderer default; it is the promoted diagnostic preset for the residual-response branch.

## Components

| Stage | Target | Source | Settings | Result |
| --- | --- | --- | --- | --- |
| `RR4` | output frame `13` | `build/shots/s454_mitsuba_residual_response_rr4/mitsuba_export.json` | radius scale `0.28`, radiance scale `2.2`, two patches | Improves S452 max gap MAD while keeping max gap `177`. |
| `lf47_mid` | output frame `47` | `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json` | radius scale `0.11`, radiance scale `0.65`, one patch | Improves RR4 mean gap MAD while keeping max gap MAD and max gap unchanged. |

## Primary Artifacts

- Export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Validation: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid_validation/mitsuba_export_validation.json`
- Render: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid_render/mitsuba_render.json`
- Target gap: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid_target_gap/renderer_target_gap_summary.json`
- Gallery: `build/shots/s458_mitsuba_residual_response_preset_gallery/gallery/index.html`

## Metrics

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| --- | ---: | ---: | ---: |
| `S452_sw2_compact_high` | `19.139631156764402` | `23.954243827160493` | `177` |
| `S454_RR4` | `19.13957939493313` | `23.95382973251029` | `177` |
| `S457_lf47_mid` | `19.139147215792182` | `23.95382973251029` | `177` |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` |
| `S445_GL3_SurfaceGlint` | `19.204893502443415` | `23.9334458590535` | `221` |

## Decision

Promote `residual_response_rr4_lf47_mid` as the current residual-response preset. It is the best safe candidate in this branch by mean gap MAD, and it improves over S452 sw2 without raising max absolute gap.

Do not treat it as the overall visual winner. `SS1_Native` and `S445_GL3_SurfaceGlint` still beat it on max gap MAD, and GL3 remains visually risky because its max absolute gap is `221`. The residual-response branch is now showing diminishing returns; the next improvement likely needs broader material/tone/response coupling rather than more local residual patches alone.

## Next

S459 should compare this named preset against broader renderer/material controls and decide whether to switch from local residual patches to a controlled material/tone hybrid.
