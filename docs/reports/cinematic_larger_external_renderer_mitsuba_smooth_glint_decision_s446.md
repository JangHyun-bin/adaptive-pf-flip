# S446 Mitsuba Smooth Glint Decision

Generated UTC: `2026-06-20T13:38:00+00:00`

## Decision

Do not replace `S445_GL3_SurfaceGlint` with disk-cluster smooth glints. `S446_SG2` and `S446_SG3` reduce the hard triangular look, but their target-gap score falls back behind `S445_GL3_SurfaceGlint`, `S417_WP4_H18_D90`, and `SS1_Native`.

## Evidence

- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_smooth_glint_decision_gallery_s446.md`
- SG1 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_smooth_glint_sg1_target_gap_s446.md`
- SG2 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_smooth_glint_sg2_target_gap_s446.md`
- SG3 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_smooth_glint_sg3_target_gap_s446.md`

## Ranking

| Candidate | Max Gap MAD | Result |
| --- | ---: | --- |
| `S445_GL3_SurfaceGlint` | `23.9334458590535` | Keep as current renderer-native metric leader. |
| `S417_WP4_H18_D90` | `23.948739068930042` | Previous renderer-native reference. |
| `SS1_Native` | `23.951853137860084` | Native baseline. |
| `S446_SG3_SmoothGlint` | `23.960123456790125` | Smoother but weaker. |
| `S446_SG2_SmoothGlint` | `23.96035815329218` | Smoother but weaker. |

## Interpretation

Disk emitters are visually smoother than reversed triangle mesh glints, but they do not carry enough structured highlight detail. The next pass should preserve GL3's direct water-surface mask alignment while avoiding hard per-triangle emission.

## Next

S447 should implement a masked water material/alpha texture path or grouped response mesh path: keep selected water-surface topology, but soften the response via per-region material opacity, non-emissive specular lift, or clustered face groups rather than separate disk emitters.
