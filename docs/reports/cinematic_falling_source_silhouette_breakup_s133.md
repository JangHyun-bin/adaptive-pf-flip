# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_falling_source_silhouette_breakup`
- Render preset: `dam_break_falling_source_silhouette_breakup`
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

- manifest: `build/shots/s133_falling_source_silhouette_breakup/cache/manifest.json`
- export_stamp: `build/shots/s133_falling_source_silhouette_breakup/cache/export_stamp.json`
- validation_stamp: `build/shots/s133_falling_source_silhouette_breakup/cache/validation_stamp.json`
- sequence: `build/shots/s133_falling_source_silhouette_breakup/converted/sequence.json`
- water_reconstruction: `build/shots/s133_falling_source_silhouette_breakup/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s133_falling_source_silhouette_breakup/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s133_falling_source_silhouette_breakup/blender/frames`
- gif: `build/shots/s133_falling_source_silhouette_breakup/shot.gif`
- gif_stamp: `build/shots/s133_falling_source_silhouette_breakup/gif_stamp.json`
- contact_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/contact_sheet.png`
- review_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/review_manifest.json`
- comparison_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s133_falling_source_silhouette_breakup/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s133_falling_source_silhouette_breakup/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s133_falling_source_silhouette_breakup/review`

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
- GIF bytes: `21375618`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.1818181818181819`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 14.60909090909091, 'max_target_distance': 34.827762745419626, 'max_target_y': 12.6, 'max_vertical_fov_degrees': 56.0, 'min_position_y': 13.809090909090909, 'min_target_distance': 31.522660090378693, 'min_target_y': 11.8, 'min_vertical_fov_degrees': 52.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 13.809090909090909, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 31.522660090378693, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 56.0, 'threshold': 56.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.002202690972222222, 'mean': 0.0011099959008487653, 'min': 0.0004448784722222222}, 'contrast': {'max': 234.0, 'mean': 233.44444444444446, 'min': 232.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.000791015625, 'mean': 0.0002471848476080247, 'min': 8.355034722222222e-05}, 'mean_luminance': {'max': 88.10610460069445, 'mean': 82.39882725091628, 'min': 76.17740451388889}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1169167.0, 'mean': 1067489.75, 'min': 941101.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 232.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 82.39882725091628, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 82.39882725091628, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0011099959008487653, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.49539930555555556, 'mean': 2.0053045634920634, 'max': 3.419375}, 'peak_delta': {'min': 59, 'mean': 97.37142857142857, 'max': 165}, 'highlight_change_ratio': {'min': 0.0, 'mean': 2.281746031746032e-05, 'max': 0.00026041666666666666}, 'highlight_ratio': {'min': 0.0, 'mean': 1.687885802469136e-05, 'max': 0.00026041666666666666}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 2.0053045634920634, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 3.419375, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 165.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.00026041666666666666, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
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
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6578273685623881, 'mean_screen_y': 0.6159572875290973, 'min_screen_y': 0.5652037446809306}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.5239238079829559, 'mean_screen_y': 0.4459623916083233, 'min_screen_y': 0.3693507671351308}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.6159572875290973, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.4990154819995714, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.41587136160789295}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.3, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.4990154819995714, 'threshold': 0.36, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.4990154819995714, 'threshold': 0.86, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.34, 0.98, 0.92], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 70.05975284918645, 'mean': 79.4036124520579, 'max': 89.9984845999422}, 'contrast': {'min': 202.0, 'mean': 229.25, 'max': 234.0}, 'bright_ratio': {'min': 1.952835126035979e-06, 'mean': 7.567236113389418e-05, 'max': 0.00021090619361188574}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 202.0, 'threshold': 60.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 79.4036124520579, 'threshold': 68.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 79.4036124520579, 'threshold': 128.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 7.567236113389418e-05, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.16, 0.98, 0.9], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}, 'depth_mean': {'min': 31.084868605804044, 'mean': 32.879820917723244, 'max': 33.69676185243126}, 'depth_span': {'min': 5.772999264769826, 'mean': 7.463639154207241, 'max': 9.759501132655636}, 'normalized_depth_span': {'min': 0.17132207806944802, 'mean': 0.22731182520239737, 'max': 0.2936564491798911}, 'channel_depth_delta': {'min': 0.06123134252064233, 'mean': 0.47418395332134766, 'max': 1.1075486177113234}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 192.0, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 1.0, 'threshold': 0.68, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 7.463639154207241, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.22731182520239737, 'threshold': 0.2, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.28, 0.98, 0.9], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 13.421813149092184, 'mean': 20.24436289456771, 'max': 26.695551116694176}, 'edge_nonzero_ratio': {'min': 0.1857170505835439, 'mean': 0.2673205365098377, 'max': 0.34572968551438044}, 'highlight_ratio': {'min': 5.4775711719080934e-06, 'mean': 8.21635675786214e-05, 'max': 0.00021179941864711294}, 'mean_luminance': {'min': 70.91964768262223, 'mean': 80.42033466134004, 'max': 90.63904084077066}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 20.24436289456771, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.2673205365098377, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.00021179941864711294, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 94.04s |
| `validate_render_cache` | `0` | 114.53s |
| `reconstruct_water` | `0` | 67.70s |
| `convert_render_cache` | `0` | 133.62s |
| `render_blender` | `0` | 280.36s |
| `assemble_gif` | `0` | 2.78s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The source-breakup scene reduces the single flat slab read with staggered rounded lobes, but late frames still form a large contained water mass at this grid/reconstruction resolution.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S134 should package and publish the S133 review artifacts so the falling-source silhouette breakup can be inspected externally.
