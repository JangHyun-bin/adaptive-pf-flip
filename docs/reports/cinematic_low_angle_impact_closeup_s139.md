# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_low_angle_impact_closeup`
- Render preset: `dam_break_low_angle_impact_closeup`
- Selected renderer: `blender`
- Simulation scene: `source-breakup-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `192`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `32 x 40 x 26`
- Simulation steps: `36`

## Artifacts

- manifest: `build/shots/s139_low_angle_impact_closeup/cache/manifest.json`
- export_stamp: `build/shots/s139_low_angle_impact_closeup/cache/export_stamp.json`
- validation_stamp: `build/shots/s139_low_angle_impact_closeup/cache/validation_stamp.json`
- sequence: `build/shots/s139_low_angle_impact_closeup/converted/sequence.json`
- water_reconstruction: `build/shots/s139_low_angle_impact_closeup/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s139_low_angle_impact_closeup/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s139_low_angle_impact_closeup/blender/frames`
- gif: `build/shots/s139_low_angle_impact_closeup/shot.gif`
- gif_stamp: `build/shots/s139_low_angle_impact_closeup/gif_stamp.json`
- contact_sheet: `build/shots/s139_low_angle_impact_closeup/review/contact_sheet.png`
- review_manifest: `build/shots/s139_low_angle_impact_closeup/review/review_manifest.json`
- comparison_sheet: `build/shots/s139_low_angle_impact_closeup/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s139_low_angle_impact_closeup/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s139_low_angle_impact_closeup/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s139_low_angle_impact_closeup/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s139_low_angle_impact_closeup/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s139_low_angle_impact_closeup/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s139_low_angle_impact_closeup/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s139_low_angle_impact_closeup/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s139_low_angle_impact_closeup/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s139_low_angle_impact_closeup/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s139_low_angle_impact_closeup/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s139_low_angle_impact_closeup/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s139_low_angle_impact_closeup/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s139_low_angle_impact_closeup/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s139_low_angle_impact_closeup/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s139_low_angle_impact_closeup/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s139_low_angle_impact_closeup/review`

## Metrics

- Cache frames: `36`
- Export cache reused: `False`
- Render cache validation reused: `False`
- Converted frames: `36`
- Converted sequence reused: `False`
- Water mesh frames: `36`
- Water reconstruction reused: `False`
- Render frames reused: `False`
- GIF reused: `False`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `22204480`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 12.2, 'max_target_distance': 24.32385660210979, 'max_target_y': 8.4, 'max_vertical_fov_degrees': 41.0, 'min_position_y': 11.4, 'min_target_distance': 21.94288039433292, 'min_target_y': 7.6, 'min_vertical_fov_degrees': 39.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 11.4, 'threshold': 11.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 21.94288039433292, 'threshold': 21.5, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 41.0, 'threshold': 41.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.005361328125, 'mean': 0.0014829282407407406, 'min': 4.340277777777778e-06}, 'contrast': {'max': 205.0, 'mean': 198.02777777777777, 'min': 185.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0029112413194444446, 'mean': 0.0004198013117283951, 'min': 3.2552083333333335e-06}, 'mean_luminance': {'max': 98.84588541666666, 'mean': 85.88576783733603, 'min': 76.56662217881944}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1255327.0, 'mean': 1109054.6666666667, 'min': 935126.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 185.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 85.88576783733603, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 85.88576783733603, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0014829282407407406, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.27368055555555554, 'mean': 3.1725942460317462, 'max': 5.87796875}, 'peak_delta': {'min': 12, 'mean': 99.82857142857142, 'max': 163}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.0003368055555555556, 'max': 0.00265625}, 'highlight_ratio': {'min': 0.0, 'mean': 0.0001707175925925926, 'max': 0.00171875}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.1725942460317462, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 5.87796875, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 163.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.00265625, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.52`
- Water rim strength: `0.52`
- Water surface detail: `{'depth': 5, 'enabled': True, 'scale': 2.25, 'strength': 0.058}`
- Water surface glint pass: `{'alpha_scale': 0.23, 'count': 52, 'drift_per_frame': 0.105, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.7, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.035}`
- Water reflection pass: `{'alpha_scale': 0.34, 'count': 24, 'drift_per_frame': 0.048, 'emission_scale': 0.72, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.6, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water volume scattering pass: `{'alpha_scale': 0.145, 'emission_scale': 0.48, 'enabled': True, 'inset': 0.42, 'layers': 12, 'region_max': [30.4, 9.2, 22.4], 'region_min': [1.6, 1.15, 2.6]}`
- Contact mist curtain pass: `{'alpha_scale': 0.105, 'emission_scale': 0.4, 'enabled': True, 'layers': 11, 'region_max': [29.0, 16.8, 22.0], 'region_min': [3.6, 1.6, 6.2], 'x_inset': 3.0, 'z_jitter': 0.62}`
- Water impact ripple pass: `{'alpha_scale': 0.38, 'arc_fraction': 0.58, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.68, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 72, 'radius': 0.5, 'radius_step': 0.3, 'ring_count': 2, 'segments': 18, 'vertical_offset': -1.82, 'width': 0.052}`
- Water impact ripple counts: `{'first': {'foam': 24, 'spray': 48, 'total': 72}, 'last': {'foam': 24, 'spray': 48, 'total': 72}, 'max_total': 72, 'mean_total': 72.0, 'min_total': 72}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.65, 'spray': 1.18}`
- Secondary soft pass: `{'alpha_scale': 0.21, 'channels': {'foam': 1.85, 'spray': 2.15}, 'emission_scale': 0.68, 'enabled': True, 'falloff': [0.9, 0.34, 0.11, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 1.12}`
- Secondary streak pass: `{'alpha_scale': 0.16, 'channels': {'foam': 0.24, 'spray': 0.92}, 'emission_scale': 0.84, 'enabled': True, 'length_scale': 0.052, 'max_length': 1.15, 'min_speed': 0.35, 'width_scale': 0.38}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 115, 'total': 115}, 'max_total': 116, 'mean_total': 115.33333333333333, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.28, 'channels': {'foam': 1.0}, 'emission_scale': 0.34, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.5, 'radius_z': 0.2, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 58, 'total': 58}, 'last': {'foam': 58, 'total': 58}, 'max_total': 58, 'mean_total': 57.666666666666664, 'min_total': 57}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 103, 'inside_ratio': 0.5953757225433526, 'max_screen_y': 0.9993114661799162, 'mean_screen_y': 0.9574632065254536, 'min_screen_y': 0.8819525509575492}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.8263616454553072, 'mean_screen_y': 0.6578178378195915, 'min_screen_y': 0.5080965794323488}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.9574632065254536, 'mean_inside_ratio': 0.9582530507385998, 'mean_screen_y': 0.7536951830594244, 'min_inside_ratio': 0.5953757225433526, 'min_mean_screen_y': 0.6002145739703374}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 0.9582530507385998, 'threshold': 0.82, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 0.5953757225433526, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.7536951830594244, 'threshold': 0.38, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.7536951830594244, 'threshold': 0.96, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 78.54586539225453, 'mean': 84.7559069644505, 'max': 97.47656617633578}, 'contrast': {'min': 104.0, 'mean': 183.5, 'max': 201.0}, 'bright_ratio': {'min': 0.0, 'mean': 4.9463426856769194e-05, 'max': 0.00019556196564220717}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 104.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 84.7559069644505, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 84.7559069644505, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 4.9463426856769194e-05, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 2, 'mean': 144.5, 'max': 192}, 'crop_ratio': {'min': 0.010416666666666666, 'mean': 0.7526041666666666, 'max': 1.0}, 'depth_mean': {'min': 20.85407811951376, 'mean': 22.322280552387806, 'max': 23.503782289941114}, 'depth_span': {'min': 1.046499622069497, 'mean': 6.523036425671064, 'max': 9.772290289297686}, 'normalized_depth_span': {'min': 0.04703987346586494, 'mean': 0.2922298777036803, 'max': 0.421085780796686}, 'channel_depth_delta': {'min': 0.0, 'mean': 0.38723575189514214, 'max': 1.1308895005448711}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 144.5, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.7526041666666666, 'threshold': 0.55, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 6.523036425671064, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.2922298777036803, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 16.87731847877236, 'mean': 22.484864191381828, 'max': 30.37772029749864}, 'edge_nonzero_ratio': {'min': 0.23944270951103397, 'mean': 0.3017358798149495, 'max': 0.3869743508259437}, 'highlight_ratio': {'min': 0.0, 'mean': 4.9463426856769194e-05, 'max': 0.00019556196564220717}, 'mean_luminance': {'min': 78.54586539225453, 'mean': 84.7559069644505, 'max': 97.47656617633578}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 22.484864191381828, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.3017358798149495, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.00019556196564220717, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance QA: `{'min_total_fraction': 0.5, 'min_foam_fraction': 0.04}`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `7`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=4005 impact_candidates=17944 foam_ready=58 grad_max=0.5633636162728591 curvature_abs_max=2.7979545918265503`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Secondary depth comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 129.79s |
| `validate_render_cache` | `0` | 137.61s |
| `reconstruct_water` | `0` | 68.24s |
| `convert_render_cache` | `0` | 135.04s |
| `render_blender` | `0` | 284.90s |
| `assemble_gif` | `0` | 2.71s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The low-angle close-up reduces the upper-source read, but small portions of the source mass still appear near the top edge in several review frames.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S140 should package and publish the S139 review artifacts, then S141 should triage the public gallery for the next visible shot adjustment.
