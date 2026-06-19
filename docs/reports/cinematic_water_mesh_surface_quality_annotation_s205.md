# S205 Water Mesh Surface Quality Annotation

Generated UTC: `2026-06-19T10:23:12+00:00`
Status: `ok`

## Inputs

- Water reconstruction: `build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json`

## Outputs

- Annotated reconstruction: `build\shots\s205_surface_quality_annotation\water_reconstruction.json`
- CSV profile: `build\shots\s205_surface_quality_annotation\water_mesh_surface_quality_profile.csv`
- JSON summary: `build\shots\s205_surface_quality_annotation\water_mesh_surface_quality_summary.json`

## Label Counts

| Label | Count |
| --- | ---: |
| `component_fragmented` | 5 |
| `normal_rough` | 3 |
| `stable` | 28 |

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `component_count` | 36 | 1 | 1.13889 | 2 | -1 |
| `largest_component_face_ratio` | 36 | 0.767793 | 0.968502 | 1 | 0.232207 |
| `sharp_edge_ratio` | 36 | 0.00565931 | 0.00819724 | 0.0147468 | -0.000833683 |
| `normal_discontinuity_p95` | 36 | 0.0568971 | 0.0711878 | 0.0890525 | -0.0239205 |
| `edge_length_cv` | 36 | 0.401706 | 0.421812 | 0.438158 | -0.0238221 |
| `face_area_cv` | 36 | 0.557124 | 0.600144 | 0.643199 | -0.059274 |
| `mesh_quality_risk_score` | 36 | 0.112578 | 0.129409 | 0.178073 | -0.0605911 |

## Worst Surface Frames

| Rank | Frame | Source frame | Label | Score | Components | Largest comp | Sharp edge | Normal p95 |
| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 3 | `component_fragmented` | 0.178073 | 2 | 0.774258 | 0.00781877 | 0.0881279 |
| 2 | 3 | 5 | `component_fragmented` | 0.177362 | 2 | 0.772246 | 0.00813171 | 0.0873167 |
| 3 | 4 | 6 | `component_fragmented` | 0.176673 | 2 | 0.774413 | 0.00798743 | 0.085982 |
| 4 | 0 | 0 | `component_fragmented` | 0.176043 | 2 | 0.767793 | 0.00669317 | 0.0853914 |
| 5 | 1 | 2 | `component_fragmented` | 0.175752 | 2 | 0.777375 | 0.00738057 | 0.0857307 |
| 6 | 5 | 8 | `normal_rough` | 0.138836 | 1 | 1 | 0.00873333 | 0.0890525 |
| 7 | 6 | 9 | `normal_rough` | 0.136647 | 1 | 1 | 0.0105459 | 0.0865692 |
| 8 | 7 | 11 | `normal_rough` | 0.135851 | 1 | 1 | 0.0147468 | 0.0861897 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `36` |
| `surface_quality_labels_present` | `True` | `{'component_fragmented': 5, 'normal_rough': 3, 'stable': 28}` |
| `quality_scores_finite` | `True` | `{'count': 36, 'min': 0.11257758498769549, 'mean': 0.1294091113414909, 'max': 0.17807311796838227, 'stddev': 0.020151043887888697, 'delta': -0.060591050971385174}` |
| `obj_counts_match_index` | `True` | `36` |

## Findings

- This annotation keeps water mesh geometry unchanged and records OBJ-level quality as frame metadata.
- component_fragmented labels identify frames where a smaller closed water component exists and should be treated, not deleted, without visual review.
- normal_rough and sharp_edges labels are renderer/export hints for later surface shading or continuity passes.

## Converter Propagation

The annotated reconstruction was passed through `convert_render_cache.py`.

- Converted sequence:
  `build\shots\s205_surface_quality_annotation\converted\sequence.json`
- Converted render frames: `56`
- Frames missing `water_mesh_surface_quality`: `0`
- Converted frame label counts:
  `{'component_fragmented': 8, 'normal_rough': 4, 'stable': 44}`
- Reconstruction annotation label counts:
  `{'component_fragmented': 5, 'normal_rough': 3, 'stable': 28}`

The converted frame counts differ from the reconstruction counts because the
56-frame render sequence samples the 36-frame reconstructed mesh sequence.

## Next

Feed the annotated reconstruction through convert_render_cache so downstream render frames carry water_mesh_surface_quality metadata for surface treatment, no-op gates, and future normal/continuity shading.
