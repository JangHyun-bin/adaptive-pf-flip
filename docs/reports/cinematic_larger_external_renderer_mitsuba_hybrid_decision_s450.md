# S450 Mitsuba Hybrid Decision

Generated UTC: `2026-06-20T14:08:00+00:00`

## Decision

Do not promote the S450 PM3-plus-soft-patch hybrids as the default renderer-native response. `S450_HY3_PM3SoftPatch` is the best S450 candidate and slightly improves over `S449_PM3_PerFaceMaterial`, but it still trails `SS1_Native` and `S445_GL3_SurfaceGlint` on max gap MAD.

Keep HY3 as the best bounded hybrid reference. It confirms that adding softened patch energy can improve the per-face material result without returning to hard triangle emitters, but manual radiance/radius tuning is producing diminishing returns.

## Evidence

- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_hybrid_decision_gallery_s450.md`
- HY1 export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy1_export_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy1_validate_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy1_render_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy1_target_gap_s450.md`
- HY2 export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy2_export_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy2_validate_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy2_render_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy2_target_gap_s450.md`
- HY3 export/validate/render/gap:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy3_export_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy3_validate_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy3_render_s450.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_pm3_soft_patch_hy3_target_gap_s450.md`

## Ranking

| Candidate | Max Gap MAD | Mean Gap MAD | Result |
| --- | ---: | ---: | --- |
| `S401_CR21_Profile` | `23.552905092592592` | `18.657217962319958` | Overall target-gap leader. |
| `S409_SF12_H18` | `23.687431841563786` | `18.756908677340533` | Strong renderer-native reference. |
| `S445_GL3_SurfaceGlint` | `23.9334458590535` | `19.204893502443415` | Current renderer-native glint leader, but has hard triangular artifacts. |
| `SS1_Native` | `23.951853137860084` | `19.146412117412552` | Native baseline. |
| `S450_HY3_PM3SoftPatch` | `23.954352494855968` | `19.13657873585391` | Best S450 hybrid; small PM3 improvement, still misses peak target. |
| `S449_PM3_PerFaceMaterial` | `23.95471322016461` | `19.13953968942901` | Best material-only reference. |
| `S450_HY2_PM3SoftPatch` | `23.955955504115227` | `19.14057010352366` | Low-energy hybrid, weaker than HY3. |
| `S446_SG3_SmoothGlint` | `23.960123456790125` | `19.169528034979425` | Smooth glint reference. |
| `S450_HY1_PM3SoftPatch` | `23.96079732510288` | `19.143168724279835` | Too broad/low-energy. |
| `S448_MM4_MaterialMask` | `23.963234310699587` | `19.17664359889403` | Uniform material response baseline. |

## Interpretation

HY3 moves in the right direction: mean gap improves over PM3 and the rendered strip does not show GL3's hard triangular emitter shape. The remaining failure is localized peak response. The accepted target has compact bright highlights that PM3/HY3 still under-express, while stronger disk/patch emitters risk drifting back toward artificial glints.

The next step should stop hand-picking radiance/radius values. The repo now has enough export, render, gap, and gallery infrastructure to run a target-driven local calibration pass over patch parameters and material-bin settings, then rank candidates by both max-gap and visual artifact gates.

## Next

S451 should add a small calibration runner that sweeps bounded local response parameters over PM3/HY-style candidates, records CSV/JSON metrics, and selects Pareto candidates by max gap MAD, mean gap MAD, max gap, patch count, and a simple highlight-overdrive/artifact proxy.
