# S581 Mitsuba Renderer Scene Render Data Profile

Generated UTC: `2026-06-20T21:59:27+00:00`
Status: `ok`

## Inputs

- Render data summary: `build\shots\s580_mitsuba_renderer_scene_render_data\render_data_summary.json`

## Outputs

- CSV profile: `build\shots\s581_mitsuba_renderer_scene_render_data_profile\render_data_profile.csv`
- SVG profile: `build\shots\s581_mitsuba_renderer_scene_render_data_profile\render_data_profile.svg`

## Trend Summary

| Trend | Count | Min | Mean | Max | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Water Y Span | 48 | 21.0 | 26.375 | 31.0 | -10.0 |
| Water Z Span | 48 | 19.0 | 21.416666666666668 | 25.0 | 6.0 |
| Mesh Faces | 48 | 23424.0 | 27165.75 | 29664.0 | -4256.0 |
| Secondaries | 48 | 192.0 | 192.0 | 192.0 | 0.0 |

- Phase-field liquid volume: `{'count': 48, 'min': 6078.831381936485, 'mean': 6105.03152054427, 'max': 6157.68511206683, 'delta': 50.113617245026944}`

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `row_count_matches_render_frames` | `True` | `48` |
| `water_depth_y_span_present` | `True` | `48` |
| `water_depth_z_span_present` | `True` | `48` |
| `mesh_faces_present` | `True` | `{'count': 48, 'min': 23424.0, 'mean': 27165.75, 'max': 29664.0, 'delta': -4256.0}` |
| `secondary_counts_present` | `True` | `{'count': 48, 'min': 192.0, 'mean': 192.0, 'max': 192.0, 'delta': 0.0}` |
| `source_frame_mapping_monotonic` | `True` | `[0, 1, 1, 34, 34, 35]` |
| `output_frame_mapping_monotonic` | `True` | `[0, 1, 2, 45, 46, 47]` |

## Findings

- Water Z-depth span is near the full grid depth for much of the shot, so a renderer can use this sidecar to separate foreground and background water more deliberately.
- Mesh face counts remain high and stable enough for a metadata-driven render pass without re-reading raw cache JSONL.
- Secondary total count is stable across the mapped frames; channel mix and depth placement should drive attenuation more than total count.

## Next

Use the S580/S581 sidecar and profile as bounded controls for the next renderer-side depth/material preview over the S578 handoff.
