# S171 Render Data Depth Export

Generated UTC: `2026-06-19T06:06:49+00:00`
Status: `ok`
Shot directory: `build\shots\s168_water_depth_foreground_separation`

## Outputs

- Render data summary: `build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json`

## Frame Coverage

- Cache frames: `56`
- Converted frames: `56`
- Render frames: `36`

## Bounds And Depth

- Water bounds min: `[0.0, 0.0, 0.0]`
- Water bounds max: `[36.0, 18.0, 28.0]`
- Secondary bounds min: `[0.8209928534387421, 1.8794251318275923, 1.2065613181922015]`
- Secondary bounds max: `[34.861209101819036, 11.429350955039258, 27.283772267343274]`
- Water Y-depth span: `{'count': 36, 'min': 11.0, 'mean': 13.555555555555555, 'max': 18.0}`
- Water Z-depth span: `{'count': 36, 'min': 23.0, 'mean': 26.88888888888889, 'max': 28.0}`
- Phase-field liquid volume: `{'count': 36, 'min': 3316.199435847198, 'mean': 3352.0731566816607, 'max': 3409.961305890586}`
- Water mesh face count: `{'count': 36, 'min': 17720.0, 'mean': 19426.222222222223, 'max': 22300.0}`
- Secondary total count: `{'count': 36, 'min': 256.0, 'mean': 342.80555555555554, 'max': 964.0}`

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `render_frame_count_positive` | `True` | `36` |
| `all_frames_have_water_bounds` | `True` | `36` |
| `all_frames_have_mesh_faces` | `True` | `36` |
| `all_frames_have_secondary_counts` | `True` | `36` |
| `source_frames_are_monotonic` | `True` | `[20, 22, 22, 53, 53, 55]` |

## Render Pass Context

- Water material: `{'depth_strength': 0.72, 'rim_strength': 0.66, 'rim_width': 0.24}`
- Water volume scattering: `{'alpha_scale': 0.21, 'emission_scale': 0.42, 'enabled': True, 'inset': 0.72, 'layers': 18, 'region_max': [34.2, 8.8, 24.5], 'region_min': [1.0, 0.9, 2.6]}`
- Water glint pass: `{'alpha_scale': 0.39, 'count': 205, 'drift_per_frame': 0.12, 'emission_scale': 0.9, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.5, 'region_max': [31.4, 8.2, 21.4], 'region_min': [1.0, 3.9, 3.0], 'width': 0.04}`
- Water reflection pass: `{'alpha_scale': 0.41, 'count': 76, 'drift_per_frame': 0.048, 'emission_scale': 0.88, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.05, 'region_max': [31.2, 8.3, 21.2], 'region_min': [1.0, 4.0, 3.4], 'width': 0.12}`

## Next

Use this sidecar as the renderer-facing data contract for the next pass:
consume water bounds/depth spans, mesh complexity, secondary counts, and
camera context without re-reading large raw cache JSONL files.
