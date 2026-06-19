# S206 S191 Surface Quality Gate

Generated UTC: `2026-06-19T10:37:11+00:00`
Status: `passed`

## Inputs

- Render summary: `build\shots\s191_water_mesh_smoothing\blender\bridge_summary.json`
- Annotated sequence: `build\shots\s205_surface_quality_annotation\converted\sequence.json`

## Outputs

- CSV profile: `build\shots\s206_surface_quality_gate\water_mesh_surface_quality_gate.csv`
- JSON summary: `build\shots\s206_surface_quality_gate\water_mesh_surface_quality_gate_summary.json`

## Gate Summary

- Render frames: `36`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 55, 'selected_frame_count': 36, 'source_frame_count': 56, 'start_fraction': 0.36363636363636365, 'start_index': 20}`
- Mesh frame index range: `{'min': 13, 'max': 35, 'unique_count': 23}`
- Label counts: `{'stable': 36}`
- Stable ratio: `1.0`
- Component treatment no-op: `True`
- Blocked label count: `0`
- Warn label count: `0`

## Metric Summary

| Metric | Count | Min | Mean | Max |
| --- | ---: | ---: | ---: | ---: |
| `risk_score` | 36 | 0.112578 | 0.118187 | 0.126005 |
| `normal_discontinuity_p95` | 36 | 0.0568971 | 0.0646718 | 0.0720309 |
| `sharp_edge_ratio` | 36 | 0.00565931 | 0.007614 | 0.00925508 |

## Worst Rows

| Rank | Render | Source frame | Mesh frame | Label | Score | Normal p95 | Sharp edge |
| ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 1 | 22 | 14 | `stable` | 0.126005 | 0.0704586 | 0.00783792 |
| 2 | 2 | 22 | 14 | `stable` | 0.126005 | 0.0704586 | 0.00783792 |
| 3 | 0 | 20 | 13 | `stable` | 0.125597 | 0.0720309 | 0.00910088 |
| 4 | 3 | 24 | 15 | `stable` | 0.122353 | 0.0688337 | 0.00925508 |
| 5 | 4 | 25 | 16 | `stable` | 0.121277 | 0.0678699 | 0.00823556 |
| 6 | 5 | 25 | 16 | `stable` | 0.121277 | 0.0678699 | 0.00823556 |
| 7 | 6 | 27 | 17 | `stable` | 0.119872 | 0.0633046 | 0.00754549 |
| 8 | 7 | 27 | 17 | `stable` | 0.119872 | 0.0633046 | 0.00754549 |

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `frames_present` | `True` | `36` |
| `surface_quality_present` | `True` | `0` |
| `no_duplicate_mesh_label_conflicts` | `True` | `{}` |
| `blocked_labels_absent` | `True` | `{'blocked_labels': ['component_fragmented', 'topology_boundary', 'topology_nonmanifold', 'topology_degenerate'], 'blocked_count': 0}` |
| `stable_ratio_floor` | `True` | `{'stable_ratio': 1.0, 'min_stable_ratio': 1.0}` |

## Findings

- The gate validates the actual render window rather than the full reconstruction.
- A passing component_treatment_noop result means component-specific material treatment should not affect this accepted window.
- Warning labels are reported but do not fail the gate unless they are also listed as blocked labels.

## Bridge Propagation

The annotated sequence was also passed through `render_bridge_blender.py` in
dry-run mode over the accepted S191 source window.

- Dry-run bridge summary:
  `build\shots\s206_surface_quality_gate\bridge_dry\bridge_summary.json`
- Dry-run scene spec:
  `build\shots\s206_surface_quality_gate\bridge_dry\blender_scene_spec.json`
- Dry-run frames: `4`
- Bridge summary labels: `{'stable': 4}`
- Scene spec labels: `{'stable': 4}`

This confirms the renderer bridge now preserves `water_mesh_surface_quality`
metadata in both generated scene specs and bridge summaries.

## Next

Use this passing gate before enabling label-driven water surface treatment. The accepted S191 window is stable-only, so component-aware treatment should remain a no-op there; future treatments should target component_fragmented or normal_rough labels explicitly.
