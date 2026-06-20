# S448 Mitsuba Material Mask Decision

Generated UTC: `2026-06-20T13:56:00+00:00`

## Decision

Do not replace `S445_GL3_SurfaceGlint` with the S448 masked material candidates. `S448_MM3_MaterialMask` and `S448_MM4_MaterialMask` render successfully and avoid adding separate emitter geometry, but both fall behind GL3, SS1, and SG3 on max gap MAD.

Keep the new bounded specular material controls in `tools/split_mitsuba_water_mask_material.py` because they make valid non-emissive material-response experiments possible, and they reject invalid RGB controls before Mitsuba runtime. Treat MM3/MM4 as a negative result for this exact masked material shape, not as a rejection of material-space response overall.

## Evidence

- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_material_mask_decision_gallery_s448.md`
- MM3 export: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm3_export_s448.md`
- MM3 validation: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm3_validate_s448.md`
- MM3 render: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm3_render_s448.md`
- MM3 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm3_target_gap_s448.md`
- MM4 export: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm4_export_s448.md`
- MM4 validation: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm4_validate_s448.md`
- MM4 render: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm4_render_s448.md`
- MM4 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_material_mask_mm4_target_gap_s448.md`

## Ranking

| Candidate | Max Gap MAD | Mean Gap MAD | Result |
| --- | ---: | ---: | --- |
| `S401_CR21_Profile` | `23.552905092592592` | `18.657217962319958` | Overall target-gap leader. |
| `S409_SF12_H18` | `23.687431841563786` | `18.756908677340533` | Strong renderer-native reference. |
| `S445_GL3_SurfaceGlint` | `23.9334458590535` | `19.204893502443415` | Current renderer-native glint leader, but has hard triangular artifacts. |
| `SS1_Native` | `23.951853137860084` | `19.146412117412552` | Native baseline. |
| `S446_SG3_SmoothGlint` | `23.960123456790125` | `19.169528034979425` | Smoother glints, weaker target detail. |
| `S448_MM4_MaterialMask` | `23.963234310699587` | `19.17664359889403` | Valid material response, not competitive. |
| `S448_MM3_MaterialMask` | `23.963501157407407` | `19.182190715020575` | Valid material response, not competitive. |

## Interpretation

The material-mask path removes the most obvious separate-emitter topology issue, but the current roughdielectric parameter lift mostly changes broad water tone. It does not recover the compact bright source response that GL3 added. MM4 is a slight numeric improvement over MM3, but both stay behind SG3 and SS1 while still missing target highlight contrast.

This suggests the next useful pass is a texture/alpha material response or vertex/color-driven roughness/specular map, not stronger uniform specular values on the masked surface. The response must preserve localized highlight structure without injecting hard triangle-shaped emission.

## Next

S449 should prototype a bounded per-face or texture-backed response map: export the selected water-surface mask as a local scalar control, drive alpha/roughness/specular strength per face or UV/texture sample, render a small 2-3 candidate sweep, and rank against GL3, SG3, MM4, and SS1.
