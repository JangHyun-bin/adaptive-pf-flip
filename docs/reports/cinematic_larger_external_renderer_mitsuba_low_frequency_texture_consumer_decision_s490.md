# S490 Mitsuba Low Frequency Texture Consumer Decision

Generated UTC: `2026-06-20T17:48:55+00:00`

## Decision

Promote S490 as the low-frequency parity texture import gate.

S489 packaged the S487 LF3 correction as renderer-consumable textures. S490 proves that the package is not just archival: consuming `applied_positive_delta_rgb` and `applied_negative_delta_rgb` reconstructs the S487 LF3 composite with exact pixel parity. The target-gap summary also matches S487 LF3 frame-by-frame.

This does not yet make the correction renderer-native. It establishes the exact texture contract that the next native post-tonemap stage should consume.

## Evidence

- S489 package report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_parity_texture_package_s489.md`
- S490 consumer report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_parity_texture_consumer_s490.md`
- S490 target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_parity_texture_consumer_target_gap_s490.md`
- S490 gap gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_texture_consumer_gap_gallery_s490.md`

## Key Checks

- S489 texture package: `8` frames, `12` textures per frame.
- S489 max reconstruction abs diff: `0`.
- S489 max signed-offset clipped channels: `0`.
- S490 consumer max expected abs diff: `0`.
- S490 target-gap mean MAD: `19.144350646219134`.
- S490 target-gap max MAD: `23.95285943930041`.
- S490 target-gap max gap: `214`.
- S487 LF3 and S490 frame MAD deltas: all `0.0`.

## Ranking

| Rank | Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current visual gate |
| 2 | S487 `lf3_proxy_close` preview | `19.144350646219134` | `23.95285943930041` | `214` | preserved direction |
| 3 | S490 texture consumer | `19.144350646219134` | `23.95285943930041` | `214` | promoted import gate |
| 4 | S485 `lrs4_sparse_spec` native | `19.214833622685184` | `23.98198945473251` | `219` | current native baseline |

## Next

Implement the S491 native post-tonemap texture stage using the S490 contract:

- read per-frame `base_rgb`;
- apply `applied_positive_delta_rgb - applied_negative_delta_rgb`;
- keep `dark_damping_weight_luma` available for shader-side bounded variants;
- compare against S478, S487 LF3, S490 consumer, and S485 LRS4.
