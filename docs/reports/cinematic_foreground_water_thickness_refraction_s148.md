# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_foreground_water_thickness_refraction`
- Render preset: `dam_break_foreground_water_thickness_refraction`
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

- manifest: `build/shots/s148_foreground_water_thickness_refraction/cache/manifest.json`
- export_stamp: `build/shots/s148_foreground_water_thickness_refraction/cache/export_stamp.json`
- validation_stamp: `build/shots/s148_foreground_water_thickness_refraction/cache/validation_stamp.json`
- sequence: `build/shots/s148_foreground_water_thickness_refraction/converted/sequence.json`
- water_reconstruction: `build/shots/s148_foreground_water_thickness_refraction/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s148_foreground_water_thickness_refraction/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s148_foreground_water_thickness_refraction/blender/frames`
- gif: `build/shots/s148_foreground_water_thickness_refraction/shot.gif`
- gif_stamp: `build/shots/s148_foreground_water_thickness_refraction/gif_stamp.json`
- contact_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/contact_sheet.png`
- review_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/review_manifest.json`
- comparison_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s148_foreground_water_thickness_refraction/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s148_foreground_water_thickness_refraction/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s148_foreground_water_thickness_refraction/review`

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
- GIF bytes: `24719294`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 47, 'selected_frame_count': 38, 'source_frame_count': 48, 'start_fraction': 0.2127659574468085, 'start_index': 10}`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 12.2, 'max_target_distance': 24.32385660210979, 'max_target_y': 8.4, 'max_vertical_fov_degrees': 41.0, 'min_position_y': 11.4, 'min_target_distance': 21.94288039433292, 'min_target_y': 7.6, 'min_vertical_fov_degrees': 39.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 11.4, 'threshold': 11.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 21.94288039433292, 'threshold': 21.5, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 41.0, 'threshold': 41.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.003857421875, 'mean': 0.0017156153549382717, 'min': 0.00018988715277777778}, 'contrast': {'max': 210.0, 'mean': 200.27777777777777, 'min': 195.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0013953993055555555, 'mean': 0.0003994562596450617, 'min': 9.765625e-06}, 'mean_luminance': {'max': 99.57795030381945, 'mean': 91.70977062837578, 'min': 78.21686631944445}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1243170.0, 'mean': 1177655.0555555555, 'min': 988733.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 195.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 91.70977062837578, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 91.70977062837578, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0017156153549382717, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 1.3524479166666667, 'mean': 4.1796870039682545, 'max': 7.969913194444445}, 'peak_delta': {'min': 65, 'mean': 113.91428571428571, 'max': 158}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00019146825396825396, 'max': 0.0007638888888888889}, 'highlight_ratio': {'min': 0.0, 'mean': 9.934413580246914e-05, 'max': 0.0005381944444444444}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 4.1796870039682545, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 7.969913194444445, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 158.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0007638888888888889, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.62`
- Water rim strength: `0.58`
- Water surface detail: `{'depth': 6, 'enabled': True, 'scale': 2.8, 'strength': 0.07}`
- Water surface glint pass: `{'alpha_scale': 0.24, 'count': 72, 'drift_per_frame': 0.12, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.45, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.032}`
- Water reflection pass: `{'alpha_scale': 0.36, 'count': 34, 'drift_per_frame': 0.048, 'emission_scale': 0.72, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.3, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water volume scattering pass: `{'alpha_scale': 0.17, 'emission_scale': 0.54, 'enabled': True, 'inset': 0.5, 'layers': 14, 'region_max': [30.6, 9.05, 22.4], 'region_min': [1.0, 1.08, 2.6]}`
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
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 77.92872988614627, 'mean': 88.975706200231, 'max': 98.05735160208029}, 'contrast': {'min': 66.0, 'mean': 175.125, 'max': 201.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00015316474262211927, 'max': 0.0006325207326240138}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 66.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 88.975706200231, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 88.975706200231, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00015316474262211927, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 155, 'mean': 187.125, 'max': 192}, 'crop_ratio': {'min': 0.8072916666666666, 'mean': 0.974609375, 'max': 1.0}, 'depth_mean': {'min': 21.973814840672635, 'mean': 23.016620367076968, 'max': 24.564995204629138}, 'depth_span': {'min': 5.8117084069836515, 'mean': 7.942015602946986, 'max': 10.162441517853505}, 'normalized_depth_span': {'min': 0.2547983033391107, 'mean': 0.3441580245768204, 'max': 0.41369605136085874}, 'channel_depth_delta': {'min': 0.07162174112081487, 'mean': 0.3276898618899464, 'max': 0.8375696449948542}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 187.125, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.974609375, 'threshold': 0.55, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 7.942015602946986, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.3441580245768204, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 18.305929194345815, 'mean': 27.25883810219335, 'max': 32.8362642164382}, 'edge_nonzero_ratio': {'min': 0.22994878721024745, 'mean': 0.3317630445942395, 'max': 0.38803619118626664}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00015316474262211927, 'max': 0.0006325207326240138}, 'mean_luminance': {'min': 77.92872988614627, 'mean': 88.975706200231, 'max': 98.05735160208029}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 27.25883810219335, 'threshold': 9.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.3317630445942395, 'threshold': 0.03, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0006325207326240138, 'threshold': 0.011, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 185.72s |
| `validate_render_cache` | `0` | 154.84s |
| `reconstruct_water` | `0` | 86.66s |
| `convert_render_cache` | `0` | 178.88s |
| `render_blender` | `0` | 288.06s |
| `assemble_gif` | `0` | 2.82s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The thickness/refraction pass improves water-body depth cues, but it is still a renderer-side approximation using layered translucent sheets and material tuning rather than a physical volumetric ray tracer.
- Some upper-edge source fragments remain visible in the early frames; S148 keeps S145 timing/framing fixed and focuses on foreground water-body depth.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

Package and publish the S148 shot artifacts, then review the public gallery to decide whether the next visible adjustment should target source-edge cleanup or a stronger physically coupled spray/foam pass.
