# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_large_event_scale_gate`
- Render preset: `dam_break_large_event_scale_gate`
- Selected renderer: `blender`
- Simulation scene: `source-breakup-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `256`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `36 x 44 x 28`
- Simulation steps: `56`

## Artifacts

- manifest: `build/shots/s160_large_event_scale_gate/cache/manifest.json`
- export_stamp: `build/shots/s160_large_event_scale_gate/cache/export_stamp.json`
- validation_stamp: `build/shots/s160_large_event_scale_gate/cache/validation_stamp.json`
- sequence: `build/shots/s160_large_event_scale_gate/converted/sequence.json`
- water_reconstruction: `build/shots/s160_large_event_scale_gate/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s160_large_event_scale_gate/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s160_large_event_scale_gate/blender/frames`
- gif: `build/shots/s160_large_event_scale_gate/shot.gif`
- gif_stamp: `build/shots/s160_large_event_scale_gate/gif_stamp.json`
- contact_sheet: `build/shots/s160_large_event_scale_gate/review/contact_sheet.png`
- review_manifest: `build/shots/s160_large_event_scale_gate/review/review_manifest.json`
- comparison_sheet: `build/shots/s160_large_event_scale_gate/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s160_large_event_scale_gate/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s160_large_event_scale_gate/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s160_large_event_scale_gate/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s160_large_event_scale_gate/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s160_large_event_scale_gate/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s160_large_event_scale_gate/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s160_large_event_scale_gate/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s160_large_event_scale_gate/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s160_large_event_scale_gate/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s160_large_event_scale_gate/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s160_large_event_scale_gate/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s160_large_event_scale_gate/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s160_large_event_scale_gate/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s160_large_event_scale_gate/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s160_large_event_scale_gate/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s160_large_event_scale_gate/review`

## Metrics

- Cache frames: `56`
- Export cache reused: `False`
- Render cache validation reused: `False`
- Converted frames: `56`
- Converted sequence reused: `False`
- Water mesh frames: `36`
- Water reconstruction reused: `False`
- Render frames reused: `False`
- GIF reused: `False`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `26170768`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 55, 'selected_frame_count': 40, 'source_frame_count': 56, 'start_fraction': 0.2909090909090909, 'start_index': 16}`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 12.6, 'max_target_distance': 25.41495622660011, 'max_target_y': 7.8, 'max_vertical_fov_degrees': 41.0, 'min_position_y': 11.7, 'min_target_distance': 22.294393914165955, 'min_target_y': 7.1, 'min_vertical_fov_degrees': 39.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 11.7, 'threshold': 11.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 22.294393914165955, 'threshold': 21.5, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 41.0, 'threshold': 41.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.004475911458333333, 'mean': 0.0010832007137345679, 'min': 8.897569444444445e-05}, 'contrast': {'max': 194.0, 'mean': 187.47222222222223, 'min': 112.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0025846354166666665, 'mean': 0.0004853877314814815, 'min': 0.0}, 'mean_luminance': {'max': 98.459140625, 'mean': 93.29727554132909, 'min': 82.69130208333333}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1223696.0, 'mean': 1190879.8055555555, 'min': 1073065.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 112.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 93.29727554132909, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 93.29727554132909, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0010832007137345679, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 1.0943402777777778, 'mean': 3.923015376984127, 'max': 7.141736111111111}, 'peak_delta': {'min': 52, 'mean': 120.48571428571428, 'max': 163}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00028373015873015873, 'max': 0.0012847222222222223}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00014467592592592592, 'max': 0.0012152777777777778}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.923015376984127, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 7.141736111111111, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 163.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0012847222222222223, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.62`
- Water rim strength: `0.58`
- Water surface detail: `{'depth': 6, 'enabled': True, 'scale': 2.8, 'strength': 0.07}`
- Water surface glint pass: `{'alpha_scale': 0.24, 'count': 82, 'drift_per_frame': 0.12, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.45, 'region_max': [31.4, 8.4, 21.4], 'region_min': [1.0, 4.9, 3.0], 'width': 0.032}`
- Water reflection pass: `{'alpha_scale': 0.36, 'count': 40, 'drift_per_frame': 0.048, 'emission_scale': 0.72, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.3, 'region_max': [31.2, 8.5, 21.2], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water volume scattering pass: `{'alpha_scale': 0.17, 'emission_scale': 0.54, 'enabled': True, 'inset': 0.54, 'layers': 14, 'region_max': [34.2, 9.4, 24.5], 'region_min': [1.0, 1.08, 2.6]}`
- Contact mist curtain pass: `{'alpha_scale': 0.108, 'emission_scale': 0.4, 'enabled': True, 'layers': 11, 'region_max': [33.2, 17.8, 24.0], 'region_min': [3.8, 1.6, 6.2], 'x_inset': 3.4, 'z_jitter': 0.62}`
- Water impact ripple pass: `{'alpha_scale': 0.42, 'arc_fraction': 0.66, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.72, 'enabled': True, 'flow_center': [16.0, 0.0, 12.2], 'material_falloff': 'edge_shader', 'max_count': 112, 'radius': 0.48, 'radius_step': 0.24, 'ring_count': 3, 'segments': 22, 'vertical_offset': -1.82, 'width': 0.045}`
- Water impact ripple counts: `{'first': {'foam': 37, 'spray': 75, 'total': 112}, 'last': {'foam': 37, 'spray': 75, 'total': 112}, 'max_total': 112, 'mean_total': 112.0, 'min_total': 112}`
- Secondary channel radius scales: `{'bubble': 0.58, 'droplet': 0.78, 'foam': 1.12, 'spray': 0.86}`
- Secondary soft pass: `{'alpha_scale': 0.24, 'channels': {'foam': 2.05, 'spray': 2.45}, 'emission_scale': 0.74, 'enabled': True, 'falloff': [0.82, 0.32, 0.1, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 1.18}`
- Secondary streak pass: `{'alpha_scale': 0.18, 'channels': {'foam': 0.42, 'spray': 1.12}, 'emission_scale': 0.9, 'enabled': True, 'length_scale': 0.066, 'max_length': 1.45, 'min_speed': 0.32, 'width_scale': 0.34}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 154, 'total': 154}, 'last': {'foam': 0, 'spray': 157, 'total': 157}, 'max_total': 157, 'mean_total': 153.44444444444446, 'min_total': 153}`
- Surface contact foam pass: `{'alpha_scale': 0.44, 'channels': {'foam': 1.0}, 'emission_scale': 0.52, 'enabled': True, 'flow_aligned': True, 'flow_center': [16.0, 0.0, 12.2], 'material_falloff': 'radial_shader', 'max_count': 380, 'radius_x': 2.25, 'radius_z': 0.36, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 76, 'total': 76}, 'last': {'foam': 74, 'total': 74}, 'max_total': 77, 'mean_total': 76.58333333333333, 'min_total': 74}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 230, 'inside': 230, 'inside_ratio': 1.0, 'max_screen_y': 0.9316568022085225, 'mean_screen_y': 0.8048645088447351, 'min_screen_y': 0.6738316635649412}, 'frame_count': 36, 'last': {'active': 231, 'inside': 228, 'inside_ratio': 0.987012987012987, 'max_screen_y': 0.7780083652998386, 'mean_screen_y': 0.6297188317297436, 'min_screen_y': 0.4733636526127965}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.8048645088447351, 'mean_inside_ratio': 0.9995184766923898, 'mean_screen_y': 0.6886999712986409, 'min_inside_ratio': 0.987012987012987, 'min_mean_screen_y': 0.6297188317297436}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 0.9995184766923898, 'threshold': 0.75, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 0.987012987012987, 'threshold': 0.2, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.6886999712986409, 'threshold': 0.38, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.6886999712986409, 'threshold': 0.98, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 82.41011788719742, 'mean': 90.17493094218088, 'max': 95.25649632404618}, 'contrast': {'min': 112.0, 'mean': 177.875, 'max': 194.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00012967438932720573, 'max': 0.00034987257915676127}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 112.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 90.17493094218088, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 90.17493094218088, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00012967438932720573, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 256, 'mean': 256.25, 'max': 258}, 'crop_particles': {'min': 232, 'mean': 252.375, 'max': 256}, 'crop_ratio': {'min': 0.90625, 'mean': 0.984882206879845, 'max': 1.0}, 'depth_mean': {'min': 23.14970058541657, 'mean': 23.899442538052284, 'max': 25.41606760573432}, 'depth_span': {'min': 6.417082333794244, 'mean': 8.4965395034148, 'max': 14.244358083458224}, 'normalized_depth_span': {'min': 0.2686294306451137, 'mean': 0.3561297708050904, 'max': 0.6153150029262852}, 'channel_depth_delta': {'min': 0.26289750221267383, 'mean': 0.5141893544863949, 'max': 0.8941302720013589}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 252.375, 'threshold': 90.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.984882206879845, 'threshold': 0.5, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 8.4965395034148, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.3561297708050904, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 22.374783812358295, 'mean': 28.477694286229383, 'max': 30.89916794494931}, 'edge_nonzero_ratio': {'min': 0.2831416418649278, 'mean': 0.35652321381645286, 'max': 0.38636933099473814}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00012967438932720573, 'max': 0.00034987257915676127}, 'mean_luminance': {'min': 82.41011788719742, 'mean': 90.17493094218088, 'max': 95.25649632404618}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 28.477694286229383, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.35652321381645286, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.00034987257915676127, 'threshold': 0.012, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=173 droplet=0 foam=57 bubble=26 total=256`
- Secondary channels last: `spray=157 droplet=0 foam=74 bubble=27 total=258`
- Secondary volume first: `droplet=126.5 bubble=11.7 total=138.2`
- Secondary volume last: `droplet=127.05 bubble=12.15 total=139.2`
- Secondary acceptance QA: `{'min_total_fraction': 0.45, 'min_foam_fraction': 0.035}`
- Secondary acceptance min: `115`
- Secondary foam acceptance min: `8`
- Secondary interface gate: `enabled=True passed=True effective_requested=256 interface_cells=5085 impact_candidates=16957 foam_ready=74 grad_max=0.6155790890648964 curvature_abs_max=2.8190456309962633`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Secondary depth comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 265.23s |
| `validate_render_cache` | `0` | 255.78s |
| `reconstruct_water` | `0` | 140.95s |
| `convert_render_cache` | `0` | 287.99s |
| `render_blender` | `0` | 414.96s |
| `assemble_gif` | `0` | 2.74s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The source-breakup water-event scene is selected, with staggered falling-water lobes and a lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

Package and publish the shot artifacts, then review the public gallery to select the next visible cinematic adjustment.
