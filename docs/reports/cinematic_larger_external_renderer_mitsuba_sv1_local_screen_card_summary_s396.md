# S396 Mitsuba SV1 Local Screen Card Summary

Generated UTC: `2026-06-20`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Export report: `docs/reports/cinematic_larger_external_renderer_mitsuba_sv1_local_screen_card_export_s396.md`
- Render report: `docs/reports/cinematic_larger_external_renderer_mitsuba_sv1_local_screen_card_render_s396.md`
- Target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_sv1_local_screen_card_target_gap_s396.md`
- C1E-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_sv1_local_screen_card_c1e_gap_s396.md`

## Candidate

- Card mode: `rectangle`
- Mask gain: `0.35`
- Mask blur radius: `0.8`
- Reflectance: `0.32,0.42,0.54`
- Frames: `8`

## Validation

- Export status: `ready`
- Missing references: `0`
- Render status: `ready`
- Render failures: `0`
- Render elapsed: `1391 ms`

## Metrics

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| SS1 baseline | 19.146412 | 23.951853 | 170 |
| S396 SV1 local screen card | 19.222715 | 23.988895 | 226 |

Against the S350 C1E bridge, S396 reached mean candidate-vs-bridge MAD
`13.724674961419753` and max candidate-vs-bridge MAD `22.189097865226337`.

## Decision

S396 is a working native-renderer candidate but not an improvement. The
screen-card mask-source compatibility should remain, while the visual direction
should move toward material/AOV-local secondary response or a residual-mask
bridge rather than another broad diffuse screen-card overlay.
