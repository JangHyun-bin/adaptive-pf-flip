# S438 Tetra Soft Water Mesh Quality

Generated UTC: `2026-06-20T12:45:02+00:00`
Status: `warning`

## Inputs

- Water reconstruction: `build\shots\s432_water_reconstruction_tetra_soft\water_reconstruction.json`

## Outputs

- CSV profile: `build\reports\s438_water_mesh_quality_tetra_soft\water_mesh_quality_profile.csv`
- JSON summary: `build\reports\s438_water_mesh_quality_tetra_soft\water_mesh_quality_summary.json`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `face_count` | 36 | 17736 | 19499.3 | 22368 | 2276 |
| `occupied_cell_count` | 36 | 5209 | 5355.56 | 5704 | 455 |
| `component_count` | 36 | 1 | 1.13889 | 2 | -1 |
| `largest_component_face_ratio` | 36 | 0.768404 | 0.96806 | 1 | 0.231137 |
| `boundary_edge_ratio` | 36 | 0 | 0 | 0 | 0 |
| `nonmanifold_edge_ratio` | 36 | 0 | 0 | 0 | 0 |
| `sharp_edge_ratio` | 36 | 0.00391532 | 0.00584866 | 0.0101813 | 0.000287109 |
| `normal_discontinuity_p95` | 36 | 0.0518578 | 0.0618797 | 0.0782341 | -0.00835627 |
| `edge_length_cv` | 36 | 0.309508 | 0.32437 | 0.340785 | 0.0217396 |
| `face_area_cv` | 36 | 0.392497 | 0.411145 | 0.433886 | 0.02558 |
| `degenerate_face_ratio` | 36 | 0 | 0 | 0 | 0 |
| `mesh_quality_risk_score` | 36 | 0.0912433 | 0.101895 | 0.136406 | -0.0412016 |

## Worst Mesh Frames

| Rank | Frame | Source frame | Score | Faces | Components | Largest comp | Boundary edge | Sharp edge | Normal p95 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3 | 5 | 0.136406 | 20096 | 2 | 0.76871 | 0 | 0.0046112 | 0.0665085 |
| 2 | 2 | 3 | 0.13605 | 19996 | 2 | 0.772555 | 0 | 0.00486764 | 0.0661292 |
| 3 | 4 | 6 | 0.136034 | 20104 | 2 | 0.768404 | 0 | 0.00563735 | 0.0653692 |
| 4 | 1 | 2 | 0.135823 | 20020 | 2 | 0.771628 | 0 | 0.00569431 | 0.0650077 |
| 5 | 0 | 0 | 0.134358 | 20092 | 2 | 0.768863 | 0 | 0.00391532 | 0.0630142 |
| 6 | 8 | 13 | 0.106274 | 18992 | 1 | 1 | 0 | 0.00807357 | 0.0782341 |
| 7 | 9 | 14 | 0.103737 | 18796 | 1 | 1 | 0 | 0.00712918 | 0.0735116 |
| 8 | 7 | 11 | 0.10269 | 19120 | 1 | 1 | 0 | 0.0101813 | 0.0726519 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `36` |
| `obj_counts_match_index` | `True` | `36` |
| `no_degenerate_faces` | `True` | `{'count': 36, 'min': 0.0, 'mean': 0.0, 'max': 0.0, 'stddev': 0.0, 'delta': 0.0}` |
| `normals_present` | `True` | `{'count': 36, 'min': 8870.0, 'mean': 9751.888888888889, 'max': 11186.0, 'stddev': 633.0469430451153, 'delta': 1136.0}` |
| `single_dominant_component` | `False` | `{'count': 36, 'min': 0.7684042976522085, 'mean': 0.968060016678097, 'max': 1.0, 'stddev': 0.07953247970450318, 'delta': 0.23113677085407125}` |
| `quality_scores_finite` | `True` | `{'count': 36, 'min': 0.09124330129793268, 'mean': 0.10189463509240332, 'max': 0.13640616923489335, 'stddev': 0.013967093435614744, 'delta': -0.04120164020923975}` |

## Findings

- This diagnostic reads exported OBJ meshes directly, so it can catch surface-data issues that bridge-summary frame metrics cannot see.
- High boundary or component fragmentation points toward export/reconstruction topology work, while high normal discontinuity points toward normal or smoothing metadata.
- Use the worst frames to choose whether S198 should continue into cache-side normal/gradient export or a reconstruction smoothing variant.

## Next

Use this quality profile to decide whether a different meshing method is required before another Mitsuba replacement render.
