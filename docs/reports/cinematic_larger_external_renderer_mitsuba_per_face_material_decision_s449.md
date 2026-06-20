# S449 Mitsuba Per-Face Material Decision

Generated UTC: `2026-06-20T14:04:00+00:00`

## Decision

Do not replace `S445_GL3_SurfaceGlint` with the S449 per-face material response candidates. `S449_PM3_PerFaceMaterial` is the best S449 material-map candidate and improves over S448 MM4, but it still trails GL3 and SS1 on max gap MAD.

Keep the new response-bin controls in `tools/split_mitsuba_water_mask_material.py`. They provide a valid per-face material response map without separate emitter geometry and make future bounded material sweeps easier. The result shows that material maps alone are too weak for the compact highlight response; the next pass should combine PM3-style material bins with a softened, bounded emitter layer.

## Evidence

- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_per_face_material_decision_gallery_s449.md`
- PM1 export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm1_export_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm1_validate_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm1_render_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm1_target_gap_s449.md`
- PM2 export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm2_export_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm2_validate_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm2_render_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm2_target_gap_s449.md`
- PM3 export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm3_export_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm3_validate_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm3_render_s449.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_per_face_material_pm3_target_gap_s449.md`

## Ranking

| Candidate | Max Gap MAD | Mean Gap MAD | Result |
| --- | ---: | ---: | --- |
| `S401_CR21_Profile` | `23.552905092592592` | `18.657217962319958` | Overall target-gap leader. |
| `S409_SF12_H18` | `23.687431841563786` | `18.756908677340533` | Strong renderer-native reference. |
| `S445_GL3_SurfaceGlint` | `23.9334458590535` | `19.204893502443415` | Current renderer-native glint leader, but has hard triangular artifacts. |
| `SS1_Native` | `23.951853137860084` | `19.146412117412552` | Native baseline. |
| `S449_PM3_PerFaceMaterial` | `23.95471322016461` | `19.13953968942901` | Best material-bin candidate; still misses max-gap target. |
| `S446_SG3_SmoothGlint` | `23.960123456790125` | `19.169528034979425` | Smoother glints, weaker target detail. |
| `S448_MM4_MaterialMask` | `23.963234310699587` | `19.17664359889403` | Uniform material response baseline. |
| `S449_PM2_PerFaceMaterial` | `23.965838477366255` | `19.184607687114198` | Tighter bins, too weak. |
| `S449_PM1_PerFaceMaterial` | `23.967778420781894` | `19.21156740290638` | Broad bins, weakest S449 candidate. |

## Interpretation

PM3 confirms that response bins help: it beats S448 MM4, S446 SG3, PM1, and PM2, and its mean gap is slightly better than SS1. The remaining problem is peak response. The brightest water highlight is still under-expressed compared with the accepted target, while GL3 gets closer by adding direct localized energy.

This narrows the next direction. A pure roughdielectric material lift is too indirect for the target. A pure mesh emitter is too geometric and can show triangular artifacts. The likely next step is a hybrid: keep PM3's binned material map as the base response, then add a small number of softened disk/patch emitters with lower radiance, larger radius, stronger minimum spacing, and strict max-gap/artifact ranking.

## Next

S450 should build a controlled hybrid candidate: use PM3 as the base export, add a low-energy softened emitter layer from the same mask, validate/render 2-3 variants, and rank against GL3, SS1, PM3, SG3, and MM4.
