# S379 Mitsuba Export Surface Quality Annotation SV1

Generated UTC: `2026-06-20T06:07:56.846408+00:00`
Summary JSON: `build/shots/s379_mitsuba_export_surface_quality_annotation_sv1/mitsuba_export_surface_quality_summary.json`
Annotated export: `build/shots/s379_mitsuba_export_surface_quality_annotation_sv1/mitsuba_export_surface_quality.json`
Status: `ready`

## Checks

- Frames: `8`
- Annotated frames: `8`
- Missing quality frames: `0`
- Label counts: `{'normal_rough': 1, 'stable': 7}`
- Max normal discontinuity p95: `0.08905251265290359`
- Max mesh quality risk score: `0.13883554159123784`

## Frame Samples

| Output | Sequence | Mesh | Label | Normal p95 | Risk |
| ---: | ---: | --- | --- | ---: | ---: |
| 0 | 8 | `build/shots/s168_water_depth_foreground_separation/water_mesh/meshes/frame_0005_water.obj` | `normal_rough` | 0.08905251265290359 | 0.13883554159123784 |
| 27 | 35 | `build/shots/s168_water_depth_foreground_separation/water_mesh/meshes/frame_0022_water.obj` | `stable` | 0.06715752712039846 | 0.11929449071084582 |
| 47 | 55 | `build/shots/s168_water_depth_foreground_separation/water_mesh/meshes/frame_0035_water.obj` | `stable` | 0.06147092534037577 | 0.11545149336652433 |

## Next

Frame-level mesh quality is now attached; next step is deciding whether normal/contact evidence must become projected masks rather than frame-level material metadata.
