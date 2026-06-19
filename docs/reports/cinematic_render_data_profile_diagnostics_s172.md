# S172 Render Data Consumer Diagnostics

Generated UTC: `2026-06-19T06:13:16+00:00`
Status: `ok`

## Inputs

- Render data summary: `build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json`

## Outputs

- CSV profile: `build\shots\s168_water_depth_foreground_separation\diagnostics\render_data_profile\render_data_profile.csv`
- SVG profile: `build\shots\s168_water_depth_foreground_separation\diagnostics\render_data_profile\render_data_profile.svg`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Water Y Span | 36 | 11.0 | 13.555555555555555 | 18.0 | -6.0 |
| Water Z Span | 36 | 23.0 | 26.88888888888889 | 28.0 | 5.0 |
| Mesh Faces | 36 | 17720.0 | 19426.222222222223 | 22300.0 | 4060.0 |
| Secondaries | 36 | 256.0 | 342.80555555555554 | 964.0 | 708.0 |

- Phase-field liquid volume: `{'count': 36, 'min': 3316.199435847198, 'mean': 3352.0731566816607, 'max': 3409.961305890586, 'delta': 93.76187004338817}`

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `row_count_matches_render_frames` | `True` | `36` |
| `water_depth_y_span_present` | `True` | `36` |
| `water_depth_z_span_present` | `True` | `36` |
| `mesh_faces_present` | `True` | `{'count': 36, 'min': 17720.0, 'mean': 19426.222222222223, 'max': 22300.0, 'delta': 4060.0}` |
| `secondary_counts_present` | `True` | `{'count': 36, 'min': 256.0, 'mean': 342.80555555555554, 'max': 964.0, 'delta': 708.0}` |
| `source_frame_mapping_monotonic` | `True` | `[20, 22, 22, 53, 53, 55]` |
| `output_frame_mapping_monotonic` | `True` | `[0, 1, 2, 33, 34, 35]` |

## Findings

- Water Z-depth span is near the full grid depth for much of the shot, so a renderer can use this sidecar to separate foreground and background water more deliberately.
- Mesh face counts remain high and stable enough for a metadata-driven render pass without re-reading raw cache JSONL.
- Secondary counts rise late in the shot, so depth-aware secondary attenuation should be frame dependent rather than a single constant.

## Next

S173 should consume render_data_summary.json in the render bridge as a bounded metadata-driven depth/attenuation pass, then compare against S168 without rerunning simulation.
