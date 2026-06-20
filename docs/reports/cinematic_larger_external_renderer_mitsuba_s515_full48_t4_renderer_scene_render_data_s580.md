# S580 Renderer Scene Render Data Summary

Generated UTC: `2026-06-20T21:59:19+00:00`
Status: `ok`
Output: `build\shots\s580_mitsuba_renderer_scene_render_data\render_data_summary.json`

## Coverage

- Scene/cache frames: `36`
- Visual frames: `48`
- Render-data frames: `48`
- Mapping mode: `nearest_normalized_scene_frame`

## Bounds And Depth

- Water bounds min: `[0.0, 0.0, 0.0]`
- Water bounds max: `[31.0, 31.0, 25.0]`
- Secondary bounds min: `[3.0888253228999156, 5.150891895294192, 6.332437231007697]`
- Secondary bounds max: `[28.959893293612566, 29.58093713760376, 18.730815504736533]`
- Water Y-depth span: `{'count': 48, 'min': 21.0, 'mean': 26.375, 'max': 31.0}`
- Water Z-depth span: `{'count': 48, 'min': 19.0, 'mean': 21.416666666666668, 'max': 25.0}`
- Phase-field liquid volume: `{'count': 48, 'min': 6078.831381936485, 'mean': 6105.03152054427, 'max': 6157.68511206683}`
- Water mesh face count: `{'count': 48, 'min': 23424.0, 'mean': 27165.75, 'max': 29664.0}`
- Water mesh occupied cell count: `{'count': 0, 'min': None, 'mean': None, 'max': None}`
- Secondary total count: `{'count': 48, 'min': 192.0, 'mean': 192.0, 'max': 192.0}`

## Sanity Checks

| Check | Passed | Value |
| --- | ---: | --- |
| `render_frame_count_positive` | `True` | `48` |
| `all_frames_have_water_bounds` | `True` | `48` |
| `all_frames_have_mesh_faces` | `True` | `48` |
| `all_frames_have_secondary_counts` | `True` | `48` |
| `source_frames_are_monotonic` | `True` | `[0, 1, 1, 34, 34, 35]` |
| `output_frames_are_monotonic` | `True` | `[0, 1, 2, 45, 46, 47]` |

## Next

Run profile diagnostics, then consume this sidecar in a bounded renderer-side depth/material preview over the S578 visual contract.
