# S438 Baseline Water Mesh Quality

Generated UTC: `2026-06-20T12:45:02+00:00`
Status: `warning`

## Inputs

- Water reconstruction: `build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json`

## Outputs

- CSV profile: `build\reports\s438_water_mesh_quality_s168\water_mesh_quality_profile.csv`
- JSON summary: `build\reports\s438_water_mesh_quality_s168\water_mesh_quality_summary.json`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `face_count` | 36 | 17720 | 19415.6 | 22300 | 2180 |
| `occupied_cell_count` | 36 | 5158 | 5323.81 | 5663 | 414 |
| `component_count` | 36 | 1 | 1.13889 | 2 | -1 |
| `largest_component_face_ratio` | 36 | 0.767793 | 0.968502 | 1 | 0.232207 |
| `boundary_edge_ratio` | 36 | 0 | 0 | 0 | 0 |
| `nonmanifold_edge_ratio` | 36 | 0 | 0 | 0 | 0 |
| `sharp_edge_ratio` | 36 | 0.00565931 | 0.00819724 | 0.0147468 | -0.000833683 |
| `normal_discontinuity_p95` | 36 | 0.0568971 | 0.0711878 | 0.0890525 | -0.0239205 |
| `edge_length_cv` | 36 | 0.401706 | 0.421812 | 0.438158 | -0.0238221 |
| `face_area_cv` | 36 | 0.557124 | 0.600144 | 0.643199 | -0.059274 |
| `degenerate_face_ratio` | 36 | 0 | 0 | 0 | 0 |
| `mesh_quality_risk_score` | 36 | 0.112578 | 0.129409 | 0.178073 | -0.0605911 |

## Worst Mesh Frames

| Rank | Frame | Source frame | Score | Faces | Components | Largest comp | Boundary edge | Sharp edge | Normal p95 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 3 | 0.178073 | 19952 | 2 | 0.774258 | 0 | 0.00781877 | 0.0881279 |
| 2 | 3 | 5 | 0.177362 | 20004 | 2 | 0.772246 | 0 | 0.00813171 | 0.0873167 |
| 3 | 4 | 6 | 0.176673 | 19948 | 2 | 0.774413 | 0 | 0.00798743 | 0.085982 |
| 4 | 0 | 0 | 0.176043 | 20120 | 2 | 0.767793 | 0 | 0.00669317 | 0.0853914 |
| 5 | 1 | 2 | 0.175752 | 19872 | 2 | 0.777375 | 0 | 0.00738057 | 0.0857307 |
| 6 | 5 | 8 | 0.138836 | 20000 | 1 | 1 | 0 | 0.00873333 | 0.0890525 |
| 7 | 6 | 9 | 0.136647 | 19660 | 1 | 1 | 0 | 0.0105459 | 0.0865692 |
| 8 | 7 | 11 | 0.135851 | 19168 | 1 | 1 | 0 | 0.0147468 | 0.0861897 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `36` |
| `obj_counts_match_index` | `True` | `36` |
| `no_degenerate_faces` | `True` | `{'count': 36, 'min': 0.0, 'mean': 0.0, 'max': 0.0, 'stddev': 0.0, 'delta': 0.0}` |
| `normals_present` | `True` | `{'count': 36, 'min': 8862.0, 'mean': 9709.888888888889, 'max': 11152.0, 'stddev': 640.9577806245977, 'delta': 1088.0}` |
| `single_dominant_component` | `False` | `{'count': 36, 'min': 0.7677932405566601, 'mean': 0.9685023802082545, 'max': 1.0, 'stddev': 0.07843732440208503, 'delta': 0.2322067594433399}` |
| `quality_scores_finite` | `True` | `{'count': 36, 'min': 0.11257758498769549, 'mean': 0.1294091113414909, 'max': 0.17807311796838227, 'stddev': 0.020151043887888697, 'delta': -0.060591050971385174}` |

## Findings

- This diagnostic reads exported OBJ meshes directly, so it can catch surface-data issues that bridge-summary frame metrics cannot see.
- High boundary or component fragmentation points toward export/reconstruction topology work, while high normal discontinuity points toward normal or smoothing metadata.
- Use the worst frames to choose whether S198 should continue into cache-side normal/gradient export or a reconstruction smoothing variant.

## Next

Compare this baseline quality profile against the S432 tetra-soft replacement before selecting the next reconstruction method.
