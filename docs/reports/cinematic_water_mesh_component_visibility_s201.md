# S201 Water Mesh Component Visibility Diagnostics

Generated UTC: `2026-06-19T09:58:47+00:00`
Status: `ok`

## Inputs

- Scene spec: `build\shots\s200_island_filter_probe\blender\blender_scene_spec.json`
- Water reconstruction: `build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json`
- Filter threshold: `0.24`

## Outputs

- CSV: `build\shots\s201_component_visibility_diagnostics\water_mesh_component_visibility.csv`
- JSON: `build\shots\s201_component_visibility_diagnostics\water_mesh_component_visibility_summary.json`

## Summary

- Render frames: `8`
- Selected mesh frames: `[13, 16, 19, 22, 26, 29, 32, 35]`
- Component rows: `8`
- Would-filter component rows: `0`
- Visible would-filter component rows: `0`
- Selected mesh frames with filtered components: `[]`
- Inside vertex ratio: `{'count': 8, 'min': 0.7309899569583931, 'mean': 0.8242698600016647, 'max': 0.9193159394869547}`
- Clipped screen area: `{'count': 8, 'min': 0.8178026583985437, 'mean': 0.9195287753637549, 'max': 1.0}`

## Filtered Components

| Rank | Render frame | Mesh frame | Component | Face ratio | Inside ratio | Clipped area | Screen x | Screen y |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| | | | | | | | | |

## Findings

- This diagnostic uses the final Blender scene spec, so source-window and camera-motion choices are included.
- If no selected mesh frames contain would-filter components, an island filter can be pixel-identical even when it changes the full reconstruction.
- Visible would-filter components should be reviewed before enabling pruning in production renders.
- The S200 probe selected mesh frames `[13, 16, 19, 22, 26, 29, 32, 35]`,
  all of which are already single-component under the `0.24` threshold.
- The component-filtered frames found by S198/S199 are earlier than this active
  render window, so S200 did not test a visible filtering case.

## Next

S200 was pixel-identical because the active render window selected mesh frames without threshold-filtered components. Use an earlier source-window review or component labels before deciding whether island pruning should affect visible shots.
