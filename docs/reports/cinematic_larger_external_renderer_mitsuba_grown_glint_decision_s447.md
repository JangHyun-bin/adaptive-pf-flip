# S447 Mitsuba Grown Glint Decision

Generated UTC: `2026-06-20T13:42:30+00:00`

## Decision

Keep the new `face-grow` option in `tools/add_mitsuba_water_mask_mesh_response.py` as a diagnostic/export control, but reject `S447_GL4_GrownGlint` as a visual candidate.

## Evidence

- Tool update: `tools/add_mitsuba_water_mask_mesh_response.py`
- GL4 export: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl4_grown_export_s447.md`
- GL4 validation: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl4_grown_validate_s447.md`
- GL4 render: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl4_grown_render_s447.md`
- GL4 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl4_grown_target_gap_s447.md`
- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_grown_glint_decision_gallery_s447.md`

## Result

`S447_GL4_GrownGlint` expanded `736` source candidate faces to `3046` response faces and regressed max gap MAD to `25.434482381687243`.

| Candidate | Max Gap MAD | Result |
| --- | ---: | --- |
| `S445_GL3_SurfaceGlint` | `23.9334458590535` | Keep as renderer-native metric leader. |
| `SS1_Native` | `23.951853137860084` | Native baseline. |
| `S446_SG3_SmoothGlint` | `23.960123456790125` | Smoother but weaker. |
| `S447_GL4_GrownGlint` | `25.434482381687243` | Reject. |

## Interpretation

One-ring face growth makes the response more continuous but also spreads the highlight into non-target water regions. That worsens both the metric and visible artifacts.

## Next

The next renderer-native pass should avoid larger emitters and grown emission surfaces. Move to masked material/alpha response: keep GL3's localized mask alignment, but replace triangle emission with material opacity/specular response or a texture-style mask.
