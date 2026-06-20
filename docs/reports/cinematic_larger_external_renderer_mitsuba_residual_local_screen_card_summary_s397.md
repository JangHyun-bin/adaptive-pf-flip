# S397 Mitsuba Residual Local Screen Card Summary

Generated UTC: `2026-06-20`

## Inputs

- Residual analysis: `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/secondary_channel_residual_mask_summary.json`
- Residual mask source: `build/shots/s397_mitsuba_residual_mask_source_best/residual_mask_source_summary.json`
- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Render manifest: `build/shots/s397_mitsuba_residual_local_screen_card/actual_render/mitsuba_render.json`

## Reports

- Mask source report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_mask_source_best_s397.md`
- Export report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_local_screen_card_export_s397.md`
- Render report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_local_screen_card_render_s397.md`
- Target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_local_screen_card_target_gap_s397.md`
- C1E-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_local_screen_card_c1e_gap_s397.md`

## Candidate

- Residual candidate: `ds6_or_channel_union_r0_source_luma_75_85`
- Residual max coverage: `0.00818479938271605`
- Residual mean coverage: `0.002732687114197531`
- Screen card reflectance: `0.06,0.08,0.12`
- Screen card mask gain: `1.0`
- Frames rendered: `8`
- Render failures: `0`

## Metrics

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| SS1 baseline | 19.146412 | 23.951853 | 170 |
| S397 residual-local screen card | 19.222715 | 23.988895 | 226 |

Against the S350 C1E bridge, S397 reached mean candidate-vs-bridge MAD
`13.724674961419753` and max candidate-vs-bridge MAD `22.189097865226337`.

## Decision

The residual-mask bridge is useful, but the camera-facing screen-card response
is still the wrong native replacement path. The next renderer experiment should
use the residual/AOV evidence to drive actual secondary material or pass data
rather than another diffuse overlay plane.
