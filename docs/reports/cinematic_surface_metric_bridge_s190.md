# S190 Surface Metric Bridge Diagnostics

Generated UTC: `2026-06-19T08:43:13+00:00`
Status: `ok`

## Inputs

- Bridge summary: `build\s190_surface_metric_bridge_dry\bridge_summary.json`

## Outputs

- CSV profile: `build\shots\s190_surface_metric_bridge_diagnostics\surface_continuity_profile.csv`
- JSON summary: `build\shots\s190_surface_metric_bridge_diagnostics\surface_continuity_summary.json`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `water_mesh_face_count` | 8 | 17728 | 19581 | 22300 | 4060 |
| `water_mesh_vertex_count` | 8 | 8866 | 9792.5 | 11152 | 2030 |
| `water_mesh_occupied_cell_count` | 8 | 5221 | 5393.75 | 5663 | 279 |
| `water_depth_y_span` | 8 | 11 | 13.75 | 18 | -6 |
| `water_depth_z_span` | 8 | 23 | 26.625 | 28 | 5 |
| `water_depth_aspect` | 8 | 1.27778 | 2.01301 | 2.54545 | 1.05556 |
| `secondary_total_count` | 8 | 256 | 375.375 | 964 | 708 |
| `continuity_risk_score` | 8 | 0.0111916 | 0.514559 | 0.772569 | 0.634695 |

## Worst Continuity Frames

| Rank | Frame | Source frame | Score | Mesh faces | Y span | Z span | Aspect | Secondary total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 6 | 50 | 0.772569 | 21532 | 12 | 28 | 2.33333 | 481 |
| 2 | 4 | 41 | 0.722758 | 19688 | 12 | 28 | 2.33333 | 256 |
| 3 | 5 | 46 | 0.718796 | 20592 | 11 | 28 | 2.54545 | 278 |
| 4 | 7 | 55 | 0.645887 | 22300 | 12 | 28 | 2.33333 | 964 |
| 5 | 3 | 35 | 0.543862 | 18576 | 13 | 27 | 2.07692 | 256 |
| 6 | 1 | 25 | 0.374943 | 17728 | 17 | 25 | 1.47059 | 256 |
| 7 | 2 | 30 | 0.326464 | 17992 | 15 | 26 | 1.73333 | 256 |
| 8 | 0 | 20 | 0.0111916 | 18240 | 18 | 23 | 1.27778 | 256 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `8` |
| `mesh_face_counts_present` | `True` | `{'count': 8, 'min': 17728.0, 'mean': 19581.0, 'max': 22300.0, 'delta': 4060.0}` |
| `water_depth_spans_present` | `True` | `{'y': {'count': 8, 'min': 11.0, 'mean': 13.75, 'max': 18.0, 'delta': -6.0}, 'z': {'count': 8, 'min': 23.0, 'mean': 26.625, 'max': 28.0, 'delta': 5.0}}` |
| `continuity_scores_finite` | `True` | `{'count': 8, 'min': 0.011191589382571952, 'mean': 0.514558880758386, 'max': 0.7725688420239772, 'delta': 0.634695327033199}` |

## Findings

- Water depth aspect increases over the shot, so surface sheets become flatter relative to camera-visible depth.
- Mesh face count rises late in the shot, which aligns with the remaining structural sheet and lobe artifacts.
- Secondary totals jump late in the shot, but S186 already reduces overlay density, so the next pass should measure or modify water reconstruction instead of only material alpha.

## Next

S191 should use the now-complete mesh face, vertex, occupied-cell, and depth metrics to choose a bounded mesh-smoothing or renderer-side volume-occlusion pass for the worst continuity frames.
