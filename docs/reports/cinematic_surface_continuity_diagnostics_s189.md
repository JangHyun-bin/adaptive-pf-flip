# S189 Surface Reconstruction Continuity Diagnostics

Generated UTC: `2026-06-19T08:37:22+00:00`
Status: `ok`

## Inputs

- Bridge summary: `build\shots\s186_water_surface_continuity_stabilized\blender\bridge_summary.json`

## Outputs

- CSV profile: `build\shots\s189_surface_continuity_diagnostics\surface_continuity_profile.csv`
- JSON summary: `build\shots\s189_surface_continuity_diagnostics\surface_continuity_summary.json`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `water_mesh_face_count` | 36 | 17720 | 19426.2 | 22300 | 4060 |
| `water_mesh_vertex_count` | 36 | 8862 | 9715.11 | 11152 | 2030 |
| `water_mesh_occupied_cell_count` | 0 | None | None | None | None |
| `water_depth_y_span` | 36 | 11 | 13.5556 | 18 | -6 |
| `water_depth_z_span` | 36 | 23 | 26.8889 | 28 | 5 |
| `water_depth_aspect` | 36 | 1.27778 | 2.04569 | 2.54545 | 1.05556 |
| `secondary_total_count` | 36 | 256 | 342.806 | 964 | 708 |
| `continuity_risk_score` | 36 | 0.00811079 | 0.34908 | 0.688686 | 0.567728 |

## Worst Continuity Frames

| Rank | Frame | Source frame | Score | Mesh faces | Y span | Z span | Aspect | Secondary total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 27 | 47 | 0.688686 | 20880 | 12 | 28 | 2.33333 | 329 |
| 2 | 25 | 46 | 0.670033 | 20592 | 11 | 28 | 2.54545 | 278 |
| 3 | 14 | 35 | 0.660952 | 18576 | 13 | 27 | 2.07692 | 256 |
| 4 | 20 | 41 | 0.63048 | 19688 | 12 | 28 | 2.33333 | 256 |
| 5 | 24 | 44 | 0.595598 | 20324 | 12 | 28 | 2.33333 | 265 |
| 6 | 28 | 49 | 0.590096 | 21204 | 12 | 28 | 2.33333 | 377 |
| 7 | 32 | 52 | 0.583198 | 21824 | 12 | 28 | 2.33333 | 634 |
| 8 | 35 | 55 | 0.579001 | 22300 | 12 | 28 | 2.33333 | 964 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `36` |
| `mesh_face_counts_present` | `True` | `{'count': 36, 'min': 17720.0, 'mean': 19426.222222222223, 'max': 22300.0, 'delta': 4060.0}` |
| `water_depth_spans_present` | `True` | `{'y': {'count': 36, 'min': 11.0, 'mean': 13.555555555555555, 'max': 18.0, 'delta': -6.0}, 'z': {'count': 36, 'min': 23.0, 'mean': 26.88888888888889, 'max': 28.0, 'delta': 5.0}}` |
| `continuity_scores_finite` | `True` | `{'count': 36, 'min': 0.00811078717752849, 'mean': 0.3490795965415472, 'max': 0.6886864636676736, 'delta': 0.5677282695762247}` |

## Warnings

| Warning | Value |
| --- | --- |
| `occupied_cell_counts_missing` | `{'available': 0, 'expected': 36}` |
| | Bridge summary does not carry occupied-cell counts for all frames; use face/vertex/depth metrics until the reconstruction export records them. |

## Findings

- Water depth aspect increases over the shot, so surface sheets become flatter relative to camera-visible depth.
- Mesh face count rises late in the shot, which aligns with the remaining structural sheet and lobe artifacts.
- Secondary totals jump late in the shot, but S186 already reduces overlay density, so the next pass should measure or modify water reconstruction instead of only material alpha.

## Next

Use these diagnostics to choose S190: mesh smoothing/reconstruction continuity, renderer-side volume occlusion, or a reconstruction export change.
