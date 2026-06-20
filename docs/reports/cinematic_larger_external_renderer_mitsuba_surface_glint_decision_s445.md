# S445 Mitsuba Surface Glint Decision

Generated UTC: `2026-06-20T13:33:00+00:00`

## Decision

Promote `S445_GL3_SurfaceGlint` as the current renderer-native visual direction. Do not promote it as the final visual default yet because it improves the metric while introducing hard triangular glint artifacts.

## Evidence

- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_surface_glint_decision_gallery_s445.md`
- GL3 export: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl3_export_s445.md`
- GL3 validation: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl3_validate_s445.md`
- GL3 render: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl3_render_s445.md`
- GL3 target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_highlight_mesh_gl3_target_gap_s445.md`

## Ranking

| Rank | Candidate | Max Gap MAD | Note |
| ---: | --- | ---: | --- |
| 1 | `S401_CR21_Profile` | `23.552905092592592` | Best reference, still composite/source-response style. |
| 2 | `S409_SF12_H18` | `23.687431841563786` | Strong composite-grade reference. |
| 3 | `S445_GL3_SurfaceGlint` | `23.9334458590535` | Best renderer-native candidate in this pass. |
| 4 | `S417_WP4_H18_D90` | `23.948739068930042` | Previous renderer-native light/material reference. |
| 5 | `SS1_Native` | `23.951853137860084` | Native baseline. |
| 6 | `S444_LR1_Contract` | `23.960451388888888` | Contract point-light path did not beat GL3. |

## Negative Results

- Global tone/background candidates `GT1..GT3` were too broad and regressed max gap badly.
- `DP1` dark-primary mesh selected too many faces and regressed badly.
- `GL1` selected too much highlight mesh and regressed.
- `GL2` was bounded but did not beat the native references.

## Next

S446 should smooth the GL3 response instead of raising its strength. The next implementation should reduce hard face artifacts by grouping selected faces into softer patches, using non-reversed normals where possible, or replacing triangle mesh emitters with clustered disk/area glints aligned to the water surface.
