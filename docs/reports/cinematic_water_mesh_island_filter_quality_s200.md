# S200 Island Filter Mesh Quality

Generated UTC: `2026-06-19T09:46:09+00:00`
Status: `ok`

## Inputs

- Water reconstruction: `build\shots\s200_island_filter_probe\water_mesh\water_reconstruction.json`

## Outputs

- CSV profile: `build\shots\s200_island_filter_probe\mesh_quality\water_mesh_quality_profile.csv`
- JSON summary: `build\shots\s200_island_filter_probe\mesh_quality\water_mesh_quality_summary.json`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `face_count` | 36 | 15448 | 18786.2 | 22300 | 6852 |
| `occupied_cell_count` | 36 | 5158 | 5323.81 | 5663 | 414 |
| `component_count` | 36 | 1 | 1 | 1 | 0 |
| `largest_component_face_ratio` | 36 | 1 | 1 | 1 | 0 |
| `boundary_edge_ratio` | 36 | 0 | 0 | 0 | 0 |
| `nonmanifold_edge_ratio` | 36 | 0 | 0 | 0 | 0 |
| `sharp_edge_ratio` | 36 | 0.00181253 | 0.0073931 | 0.0147468 | 0.00404696 |
| `normal_discontinuity_p95` | 36 | 0.0304242 | 0.0633982 | 0.0890525 | 0.0310467 |
| `edge_length_cv` | 36 | 0.401706 | 0.420362 | 0.437606 | -0.0122757 |
| `face_area_cv` | 36 | 0.557124 | 0.59956 | 0.641657 | -0.0527147 |
| `degenerate_face_ratio` | 36 | 0 | 0 | 0 | 0 |
| `mesh_quality_risk_score` | 36 | 0.0997329 | 0.11871 | 0.138836 | 0.0156945 |

## Worst Mesh Frames

| Rank | Frame | Source frame | Score | Faces | Components | Largest comp | Boundary edge | Sharp edge | Normal p95 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5 | 8 | 0.138836 | 20000 | 1 | 1 | 0 | 0.00873333 | 0.0890525 |
| 2 | 6 | 9 | 0.136647 | 19660 | 1 | 1 | 0 | 0.0105459 | 0.0865692 |
| 3 | 7 | 11 | 0.135851 | 19168 | 1 | 1 | 0 | 0.0147468 | 0.0861897 |
| 4 | 8 | 13 | 0.134064 | 18920 | 1 | 1 | 0 | 0.0113108 | 0.0821171 |
| 5 | 9 | 14 | 0.133625 | 18884 | 1 | 1 | 0 | 0.0108028 | 0.0814122 |
| 6 | 11 | 17 | 0.127368 | 18472 | 1 | 1 | 0 | 0.00891439 | 0.0746109 |
| 7 | 10 | 16 | 0.12606 | 18524 | 1 | 1 | 0 | 0.00827755 | 0.0721119 |
| 8 | 14 | 22 | 0.126005 | 18032 | 1 | 1 | 0 | 0.00783792 | 0.0704586 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `36` |
| `obj_counts_match_index` | `True` | `36` |
| `no_degenerate_faces` | `True` | `{'count': 36, 'min': 0.0, 'mean': 0.0, 'max': 0.0, 'stddev': 0.0, 'delta': 0.0}` |
| `normals_present` | `True` | `{'count': 36, 'min': 7726.0, 'mean': 9394.944444444445, 'max': 11152.0, 'stddev': 920.2525602742749, 'delta': 3426.0}` |
| `single_dominant_component` | `True` | `{'count': 36, 'min': 1.0, 'mean': 1.0, 'max': 1.0, 'stddev': 0.0, 'delta': 0.0}` |
| `quality_scores_finite` | `True` | `{'count': 36, 'min': 0.09973289548902073, 'mean': 0.11871029223183914, 'max': 0.13883554159123784, 'stddev': 0.010099981229411694, 'delta': 0.01569449444311645}` |

## Findings

- This diagnostic reads exported OBJ meshes directly, so it can catch surface-data issues that bridge-summary frame metrics cannot see.
- High boundary or component fragmentation points toward export/reconstruction topology work, while high normal discontinuity points toward normal or smoothing metadata.
- Use the worst frames to choose whether S198 should continue into cache-side normal/gradient export or a reconstruction smoothing variant.
- The `0.24` component filter removes all secondary components in this
  reconstruction probe: component count is `1` for all 36 frames.
- Mesh quality risk improves from the S198 mean `0.1294091113414909` to
  `0.11871029223183914`, but this alone is not enough to justify changing the
  visual baseline.

## Next

Use the S200 visual comparison before accepting any island threshold. If the
filtered mesh is pixel-identical, prefer component visibility/label diagnostics
over stronger filtering.
