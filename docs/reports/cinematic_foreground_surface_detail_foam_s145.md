# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_foreground_surface_detail_foam`
- Render preset: `dam_break_foreground_surface_detail_foam`
- Selected renderer: `blender`
- Simulation scene: `source-breakup-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `192`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `32 x 40 x 26`
- Simulation steps: `48`

## Artifacts

- manifest: `build/shots/s145_foreground_surface_detail_foam/cache/manifest.json`
- export_stamp: `build/shots/s145_foreground_surface_detail_foam/cache/export_stamp.json`
- validation_stamp: `build/shots/s145_foreground_surface_detail_foam/cache/validation_stamp.json`
- sequence: `build/shots/s145_foreground_surface_detail_foam/converted/sequence.json`
- water_reconstruction: `build/shots/s145_foreground_surface_detail_foam/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s145_foreground_surface_detail_foam/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s145_foreground_surface_detail_foam/blender/frames`
- gif: `build/shots/s145_foreground_surface_detail_foam/shot.gif`
- gif_stamp: `build/shots/s145_foreground_surface_detail_foam/gif_stamp.json`
- contact_sheet: `build/shots/s145_foreground_surface_detail_foam/review/contact_sheet.png`
- review_manifest: `build/shots/s145_foreground_surface_detail_foam/review/review_manifest.json`
- comparison_sheet: `build/shots/s145_foreground_surface_detail_foam/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s145_foreground_surface_detail_foam/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s145_foreground_surface_detail_foam/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s145_foreground_surface_detail_foam/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s145_foreground_surface_detail_foam/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s145_foreground_surface_detail_foam/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s145_foreground_surface_detail_foam/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s145_foreground_surface_detail_foam/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s145_foreground_surface_detail_foam/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s145_foreground_surface_detail_foam/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s145_foreground_surface_detail_foam/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s145_foreground_surface_detail_foam/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s145_foreground_surface_detail_foam/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s145_foreground_surface_detail_foam/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s145_foreground_surface_detail_foam/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s145_foreground_surface_detail_foam/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s145_foreground_surface_detail_foam/review`

## Metrics

- Cache frames: `48`
- Export cache reused: `False`
- Render cache validation reused: `False`
- Converted frames: `48`
- Converted sequence reused: `False`
- Water mesh frames: `36`
- Water reconstruction reused: `False`
- Render frames reused: `False`
- GIF reused: `False`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `25398592`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 47, 'selected_frame_count': 38, 'source_frame_count': 48, 'start_fraction': 0.2127659574468085, 'start_index': 10}`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 12.2, 'max_target_distance': 24.32385660210979, 'max_target_y': 8.4, 'max_vertical_fov_degrees': 41.0, 'min_position_y': 11.4, 'min_target_distance': 21.94288039433292, 'min_target_y': 7.6, 'min_vertical_fov_degrees': 39.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 11.4, 'threshold': 11.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 21.94288039433292, 'threshold': 21.5, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 41.0, 'threshold': 41.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.004044053819444444, 'mean': 0.002152295524691358, 'min': 0.00018771701388888888}, 'contrast': {'max': 211.0, 'mean': 200.08333333333334, 'min': 194.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0010753038194444445, 'mean': 0.00043131510416666665, 'min': 1.193576388888889e-05}, 'mean_luminance': {'max': 99.255048828125, 'mean': 91.88439829885223, 'min': 78.88799479166667}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1262374.0, 'mean': 1200684.388888889, 'min': 1012974.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 194.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 91.88439829885223, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 91.88439829885223, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.002152295524691358, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 1.4469270833333334, 'mean': 4.209830357142858, 'max': 7.919236111111111}, 'peak_delta': {'min': 68, 'mean': 115.77142857142857, 'max': 151}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.0001909722222222222, 'max': 0.0005729166666666667}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00010513117283950617, 'max': 0.00038194444444444446}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 4.209830357142858, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 7.919236111111111, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 151.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0005729166666666667, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.52`
- Water rim strength: `0.52`
- Water surface detail: `{'depth': 6, 'enabled': True, 'scale': 3.1, 'strength': 0.076}`
- Water surface glint pass: `{'alpha_scale': 0.28, 'count': 72, 'drift_per_frame': 0.12, 'emission_scale': 0.56, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.45, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.032}`
- Water reflection pass: `{'alpha_scale': 0.38, 'count': 30, 'drift_per_frame': 0.055, 'emission_scale': 0.78, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 4.8, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.095}`
- Water volume scattering pass: `{'alpha_scale': 0.145, 'emission_scale': 0.48, 'enabled': True, 'inset': 0.42, 'layers': 12, 'region_max': [30.4, 9.2, 22.4], 'region_min': [1.6, 1.15, 2.6]}`
- Contact mist curtain pass: `{'alpha_scale': 0.105, 'emission_scale': 0.4, 'enabled': True, 'layers': 11, 'region_max': [29.0, 16.8, 22.0], 'region_min': [3.6, 1.6, 6.2], 'x_inset': 3.0, 'z_jitter': 0.62}`
- Water impact ripple pass: `{'alpha_scale': 0.46, 'arc_fraction': 0.66, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.78, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 96, 'radius': 0.48, 'radius_step': 0.24, 'ring_count': 3, 'segments': 22, 'vertical_offset': -1.82, 'width': 0.045}`
- Water impact ripple counts: `{'first': {'foam': 32, 'spray': 64, 'total': 96}, 'last': {'foam': 32, 'spray': 64, 'total': 96}, 'max_total': 96, 'mean_total': 96.0, 'min_total': 96}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.65, 'spray': 1.18}`
- Secondary soft pass: `{'alpha_scale': 0.21, 'channels': {'foam': 1.85, 'spray': 2.15}, 'emission_scale': 0.68, 'enabled': True, 'falloff': [0.9, 0.34, 0.11, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 1.12}`
- Secondary streak pass: `{'alpha_scale': 0.16, 'channels': {'foam': 0.24, 'spray': 0.92}, 'emission_scale': 0.84, 'enabled': True, 'length_scale': 0.052, 'max_length': 1.15, 'min_speed': 0.35, 'width_scale': 0.38}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 116, 'total': 116}, 'last': {'foam': 0, 'spray': 115, 'total': 115}, 'max_total': 116, 'mean_total': 115.33333333333333, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.34, 'channels': {'foam': 1.0}, 'emission_scale': 0.42, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 300, 'radius_x': 1.68, 'radius_z': 0.24, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 57, 'total': 57}, 'last': {'foam': 58, 'total': 58}, 'max_total': 58, 'mean_total': 57.666666666666664, 'min_total': 57}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.9718669194228844, 'mean_screen_y': 0.8282451883461153, 'min_screen_y': 0.7031002551581935}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6426542057664536, 'mean_screen_y': 0.5687539210158431, 'min_screen_y': 0.3857162616730367}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.8282451883461153, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.6484184334866394, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.5687539210158431}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.82, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.6484184334866394, 'threshold': 0.38, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.6484184334866394, 'threshold': 0.96, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 78.66385342630674, 'mean': 89.66166538583765, 'max': 98.40609053296747}, 'contrast': {'min': 160.0, 'mean': 191.375, 'max': 201.0}, 'bright_ratio': {'min': 1.5278278565797435e-06, 'mean': 0.00019556196564220717, 'max': 0.0008066931082741046}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 160.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 89.66166538583765, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 89.66166538583765, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00019556196564220717, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 155, 'mean': 187.125, 'max': 192}, 'crop_ratio': {'min': 0.8072916666666666, 'mean': 0.974609375, 'max': 1.0}, 'depth_mean': {'min': 21.973814840672635, 'mean': 23.016620367076968, 'max': 24.564995204629138}, 'depth_span': {'min': 5.8117084069836515, 'mean': 7.942015602946986, 'max': 10.162441517853505}, 'normalized_depth_span': {'min': 0.2547983033391107, 'mean': 0.3441580245768204, 'max': 0.41369605136085874}, 'channel_depth_delta': {'min': 0.07162174112081487, 'mean': 0.3276898618899464, 'max': 0.8375696449948542}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 187.125, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.974609375, 'threshold': 0.55, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 7.942015602946986, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.3441580245768204, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 18.753356637800906, 'mean': 27.410534411266813, 'max': 32.60297559753347}, 'edge_nonzero_ratio': {'min': 0.2485668974705282, 'mean': 0.3425227722742023, 'max': 0.3911117086615617}, 'highlight_ratio': {'min': 1.5278278565797435e-06, 'mean': 0.00019556196564220717, 'max': 0.0008066931082741046}, 'mean_luminance': {'min': 78.66385342630674, 'mean': 89.66166538583765, 'max': 98.40609053296747}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 27.410534411266813, 'threshold': 9.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.3425227722742023, 'threshold': 0.03, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0008066931082741046, 'threshold': 0.011, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance QA: `{'min_total_fraction': 0.5, 'min_foam_fraction': 0.04}`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `7`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=4030 impact_candidates=13849 foam_ready=58 grad_max=0.585269832704446 curvature_abs_max=2.6661995206271323`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Secondary depth comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 170.67s |
| `validate_render_cache` | `0` | 154.40s |
| `reconstruct_water` | `0` | 86.15s |
| `convert_render_cache` | `0` | 177.71s |
| `render_blender` | `0` | 285.02s |
| `assemble_gif` | `0` | 2.82s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The foreground detail pass improves close-up water texture and contact foam readability, but the underlying water body still comes from a coarse sparse 3D phase-cell surface.
- Some upper-edge source fragments remain visible in the first review frames; the current pass focuses on surface and foam breakup rather than further reframing.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

Package and publish the S145 shot artifacts, then review the public gallery to select the next visible cinematic adjustment from the current close-up shot.
