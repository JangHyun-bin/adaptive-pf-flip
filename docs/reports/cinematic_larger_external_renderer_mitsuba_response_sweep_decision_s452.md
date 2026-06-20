# S452 Mitsuba Response Sweep Decision

Generated UTC: `2026-06-20T14:22:00+00:00`

## Decision

Do not promote an S452 sweep candidate as the default renderer-native response. `sw2_compact_high` is the best S452 candidate by max gap MAD, and all three sweep candidates improve over `S449_PM3_PerFaceMaterial`, but none reaches `SS1_Native` or `S445_GL3_SurfaceGlint`.

Keep `tools/run_mitsuba_response_sweep.py`. It closes the manual loop from S450: export, validate, render, target-gap, decision gallery, and calibration summary now run as one bounded sweep. The visual result confirms that PM3 plus local disk/patch energy can make small improvements, but the peak highlight remains too weak without pushing toward artificial glints.

## Evidence

- Sweep report: `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_s452.md`
- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_decision_gallery_s452.md`
- Calibration table: `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_calibration_s452.md`
- `sw1_compact_mid` export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw1_compact_mid_export_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw1_compact_mid_validate_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw1_compact_mid_render_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw1_compact_mid_target_gap_s452.md`
- `sw2_compact_high` export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw2_compact_high_export_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw2_compact_high_validate_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw2_compact_high_render_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw2_compact_high_target_gap_s452.md`
- `sw3_sparse_high` export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw3_sparse_high_export_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw3_sparse_high_validate_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw3_sparse_high_render_s452.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_response_sweep_sw3_sparse_high_target_gap_s452.md`

## Ranking

| Candidate | Max Gap MAD | Mean Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `S401_CR21_Profile` | `23.552905092592592` | `18.657217962319958` | `182` | Overall target-gap leader. |
| `S409_SF12_H18` | `23.687431841563786` | `18.756908677340533` | `170` | Strong renderer-native reference. |
| `S445_GL3_SurfaceGlint` | `23.9334458590535` | `19.204893502443415` | `221` | Current renderer-native glint leader, with hard artifact risk. |
| `SS1_Native` | `23.951853137860084` | `19.146412117412552` | `170` | Native baseline. |
| `sw2_compact_high` | `23.954243827160493` | `19.139631156764402` | `177` | Best S452 sweep candidate. |
| `sw1_compact_mid` | `23.954281121399177` | `19.137965454603908` | `176` | Best S452 mean gap, slightly worse max gap than sw2. |
| `sw3_sparse_high` | `23.954342206790123` | `19.139409159593622` | `177` | Similar to sw2 with fewer patches. |
| `S449_PM3_PerFaceMaterial` | `23.95471322016461` | `19.13953968942901` | `176` | Material-only baseline. |
| `S446_SG3_SmoothGlint` | `23.960123456790125` | `19.169528034979425` | `167` | Smooth patch reference with lower max absolute gap. |
| `S448_MM4_MaterialMask` | `23.963234310699587` | `19.17664359889403` | `179` | Uniform material response baseline. |

## Interpretation

The bounded sweep is useful but the response family is close to saturated. Increasing compact patch energy improves PM3 by about `0.00047` max-gap MAD, which is measurable but not enough to close the gap to SS1 or GL3. The representative strip still shows under-powered compact highlights relative to the accepted target.

This points away from another small manual radius/radiance sweep. The better next direction is target-driven source-region response: estimate the local missing highlight energy from the target/actual gap and generate response controls from that measured residual instead of selecting radiance values by hand.

## Next

S453 should add a target-gap residual analyzer for the source-highlight region. It should read a target-gap summary, locate the worst residual frames/regions, and output a local response request table that can feed either patch emitters, material bins, or source-region response controls.
