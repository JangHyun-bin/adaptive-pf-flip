# S491 Mitsuba Low Frequency Post-Tonemap Decision

Generated UTC: `2026-06-20T17:53:45+00:00`

## Decision

Promote S491 as the renderer-facing post-tonemap gate for the low-frequency parity texture contract.

S491 consumes the S489 texture package directly and writes a `lsfs_mitsuba_composite_grade` summary with subschema `lsfs_mitsuba_low_frequency_post_tonemap_texture_stage`. This keeps compatibility with the existing target-gap tool while making the stage boundary explicit: the operation is `base_rgb + applied_positive_delta_rgb - applied_negative_delta_rgb` after tonemapping.

The stage exactly preserves S487 LF3 and S490 texture-consumer output.

## Evidence

- S491 post-tonemap stage report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_post_tonemap_texture_stage_s491.md`
- S491 target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_post_tonemap_texture_stage_target_gap_s491.md`
- S491 comparison gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_post_tonemap_gap_gallery_s491.md`
- S489 package report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_parity_texture_package_s489.md`
- S490 consumer decision: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_texture_consumer_decision_s490.md`

## Key Checks

- S491 frames: `8`.
- S491 stage: `post_tonemap_positive_negative_delta`.
- S491 texture gain: `1.0`.
- S491 max expected abs diff: `0`.
- S491 max expected mean diff: `0.0`.
- S491 max changed coverage: `0.18508873456790123`.
- S491 target-gap mean MAD: `19.144350646219134`.
- S491 target-gap max MAD: `23.95285943930041`.
- S491 target-gap max gap: `214`.
- S487 minus S491 frame MAD deltas: all `0.0`.
- S490 minus S491 frame MAD deltas: all `0.0`.

## Ranking

| Rank | Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current visual gate |
| 2 | S487 `lf3_proxy_close` preview | `19.144350646219134` | `23.95285943930041` | `214` | preserved direction |
| 3 | S490 texture consumer | `19.144350646219134` | `23.95285943930041` | `214` | import gate |
| 4 | S491 post-tonemap stage | `19.144350646219134` | `23.95285943930041` | `214` | promoted stage gate |
| 5 | S485 `lrs4_sparse_spec` native | `19.214833622685184` | `23.98198945473251` | `219` | current native baseline |

## Interpretation

S491 does not beat the S478 proxy visual gate. It proves a different requirement: the low-frequency improvement can now travel through a renderer-facing stage boundary without losing pixels. That makes the next implementation step much less ambiguous.

## Next

Implement S492 as an engine-native shader/compositor port of the S491 stage contract:

- bind per-frame positive and negative delta textures;
- apply the same bounded delta after tonemap or in the closest renderer output stage;
- keep the S491 output as the exact parity oracle;
- fail the promotion if target-gap parity diverges from S491.
