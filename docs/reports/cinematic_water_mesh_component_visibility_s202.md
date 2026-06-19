# S202 Early Window Component Visibility

Generated UTC: `2026-06-19T10:03:27+00:00`
Status: `ok`

## Inputs

- Scene spec: `build\shots\s202_island_filter_early_probe\original\blender_scene_spec.json`
- Water reconstruction: `build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json`
- Filter threshold: `0.24`

## Outputs

- CSV: `build\shots\s202_island_filter_early_probe\component_visibility\water_mesh_component_visibility.csv`
- JSON: `build\shots\s202_island_filter_early_probe\component_visibility\water_mesh_component_visibility_summary.json`

## Summary

- Render frames: `8`
- Selected mesh frames: `[0, 1, 2, 3, 4, 5]`
- Component rows: `15`
- Would-filter component rows: `7`
- Visible would-filter component rows: `7`
- Selected mesh frames with filtered components: `[0, 1, 2, 3, 4]`
- Inside vertex ratio: `{'count': 15, 'min': 0.28999144568006846, 'mean': 0.6237430379093504, 'max': 0.9641470359823971}`
- Clipped screen area: `{'count': 15, 'min': 0.08226368596457384, 'mean': 0.46632532799984205, 'max': 1.0}`

## Filtered Components

| Rank | Render frame | Mesh frame | Component | Face ratio | Inside ratio | Clipped area | Screen x | Screen y |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 5 | 4 | 2 | 0.225587 | 0.340142 | 0.130715 | 0.198711..0.818128 | 0.788971..1.59443 |
| 2 | 4 | 3 | 2 | 0.227754 | 0.322807 | 0.129939 | 0.212022..0.795128 | 0.77716..1.58427 |
| 3 | 6 | 4 | 2 | 0.225587 | 0.307726 | 0.127599 | 0.193429..0.828115 | 0.798958..1.63024 |
| 4 | 1 | 1 | 2 | 0.222625 | 0.341463 | 0.106554 | 0.230147..0.764115 | 0.800448..1.51473 |
| 5 | 2 | 1 | 2 | 0.222625 | 0.3243 | 0.103928 | 0.225344..0.771575 | 0.809736..1.54461 |
| 6 | 3 | 2 | 2 | 0.225742 | 0.304791 | 0.102533 | 0.216004..0.787746 | 0.820665..1.57324 |
| 7 | 0 | 0 | 2 | 0.232207 | 0.289991 | 0.0822637 | 0.22643..0.770857 | 0.848899..1.55683 |

## Findings

- This diagnostic uses the final Blender scene spec, so source-window and camera-motion choices are included.
- If no selected mesh frames contain would-filter components, an island filter can be pixel-identical even when it changes the full reconstruction.
- Visible would-filter components should be reviewed before enabling pruning in production renders.
- In the early window, the `0.24` threshold targets visible component-2 regions
  in mesh frames `[0, 1, 2, 3, 4]`.
- The target component has face ratios around `0.22` to `0.23` and clipped
  screen areas up to `0.130715`, so it is too large to treat as noise without a
  label/semantic review.

## Next

Use the early-window comparison sheet to decide whether the visible filtered component is an artifact or meaningful separated water.
