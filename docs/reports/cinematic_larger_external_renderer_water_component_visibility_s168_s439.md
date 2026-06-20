# S439 Baseline Water Component Visibility

Generated UTC: `2026-06-20T12:47:26+00:00`
Status: `ok`

## Inputs

- Scene spec: `build\shots\s305_larger_external_renderer_job_blender_full48\blender_scene_spec.json`
- Water reconstruction: `build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json`
- Filter threshold: `0.24`

## Outputs

- CSV: `build\reports\s439_water_component_visibility_s168\water_mesh_component_visibility.csv`
- JSON: `build\reports\s439_water_component_visibility_s168\water_mesh_component_visibility_summary.json`

## Summary

- Render frames: `48`
- Selected mesh frames: `[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]`
- Component rows: `48`
- Would-filter component rows: `0`
- Visible would-filter component rows: `0`
- Selected mesh frames with filtered components: `[]`
- Inside vertex ratio: `{'count': 48, 'min': 0.7545731707317073, 'mean': 0.8574838135628995, 'max': 0.9488341968911918}`
- Clipped screen area: `{'count': 48, 'min': 0.783728475450512, 'mean': 0.9126376765000556, 'max': 1.0}`

## Filtered Components

| Rank | Render frame | Mesh frame | Component | Face ratio | Inside ratio | Clipped area | Screen x | Screen y |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| | | | | | | | | |

## Findings

- This diagnostic uses the final Blender scene spec, so source-window and camera-motion choices are included.
- If no selected mesh frames contain would-filter components, an island filter can be pixel-identical even when it changes the full reconstruction.
- Visible would-filter components should be reviewed before enabling pruning in production renders.

## Next

Compare against the tetra-soft component visibility before deciding whether component filtering or silhouette/depth alignment is the next reconstruction task.
