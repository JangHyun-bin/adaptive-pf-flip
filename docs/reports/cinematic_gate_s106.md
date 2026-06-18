# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_large_grid_render_quality_followup`
- Render preset: `dam_break_large_grid_render_quality_followup`
- Selected renderer: `blender`
- Simulation scene: `large-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `192`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `32 x 40 x 26`
- Simulation steps: `36`

## Artifacts

- manifest: `build/shots/s106_large_grid_render_quality_followup/cache/manifest.json`
- sequence: `build/shots/s106_large_grid_render_quality_followup/converted/sequence.json`
- water_reconstruction: `build/shots/s106_large_grid_render_quality_followup/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s106_large_grid_render_quality_followup/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s106_large_grid_render_quality_followup/blender/frames`
- gif: `build/shots/s106_large_grid_render_quality_followup/shot.gif`
- contact_sheet: `build/shots/s106_large_grid_render_quality_followup/review/contact_sheet.png`
- review_manifest: `build/shots/s106_large_grid_render_quality_followup/review/review_manifest.json`
- comparison_sheet: `build/shots/s106_large_grid_render_quality_followup/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s106_large_grid_render_quality_followup/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s106_large_grid_render_quality_followup/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s106_large_grid_render_quality_followup/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s106_large_grid_render_quality_followup/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s106_large_grid_render_quality_followup/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s106_large_grid_render_quality_followup/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s106_large_grid_render_quality_followup/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s106_large_grid_render_quality_followup/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s106_large_grid_render_quality_followup/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s106_large_grid_render_quality_followup/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s106_large_grid_render_quality_followup/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s106_large_grid_render_quality_followup/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s106_large_grid_render_quality_followup/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s106_large_grid_render_quality_followup/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s106_large_grid_render_quality_followup/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s106_large_grid_render_quality_followup/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `25267805`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.1818181818181819`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 13.936363636363637, 'max_target_distance': 31.73000248741307, 'max_target_y': 13.7, 'max_vertical_fov_degrees': 50.0, 'min_position_y': 13.254545454545454, 'min_target_distance': 29.31218825276082, 'min_target_y': 12.9, 'min_vertical_fov_degrees': 46.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 13.254545454545454, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 29.31218825276082, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 50.0, 'threshold': 50.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.007042100694444445, 'mean': 0.003183232060185185, 'min': 0.0003493923611111111}, 'contrast': {'max': 248.0, 'mean': 212.69444444444446, 'min': 165.0}, 'dark_ratio': {'max': 2.9296875e-05, 'mean': 6.088445216049383e-06, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0017578125, 'mean': 0.0005298755787037037, 'min': 0.0}, 'mean_luminance': {'max': 116.59989366319445, 'mean': 102.31068672839507, 'min': 85.33566080729166}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1258146.0, 'mean': 1142827.8333333333, 'min': 899921.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 165.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 102.31068672839507, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 102.31068672839507, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.003183232060185185, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.8209027777777778, 'mean': 2.376531746031746, 'max': 5.064253472222222}, 'peak_delta': {'min': 57, 'mean': 103.08571428571429, 'max': 151}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00020287698412698412, 'max': 0.0007638888888888889}, 'highlight_ratio': {'min': 0.0, 'mean': 0.0001253858024691358, 'max': 0.0005729166666666667}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 2.376531746031746, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 5.064253472222222, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 151.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0007638888888888889, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.52`
- Water rim strength: `0.52`
- Water surface detail: `{'depth': 5, 'enabled': True, 'scale': 2.25, 'strength': 0.058}`
- Water surface glint pass: `{'alpha_scale': 0.23, 'count': 52, 'drift_per_frame': 0.105, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.7, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.035}`
- Water reflection pass: `{'alpha_scale': 0.34, 'count': 24, 'drift_per_frame': 0.048, 'emission_scale': 0.72, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.6, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water volume scattering pass: `{'alpha_scale': 0.24, 'emission_scale': 0.22, 'enabled': True, 'inset': 0.24, 'layers': 5, 'region_max': [27.2, 7.65, 19.0], 'region_min': [0.8, 4.45, 3.2]}`
- Water impact ripple pass: `{'alpha_scale': 0.44, 'arc_fraction': 0.58, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.82, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 72, 'radius': 0.5, 'radius_step': 0.3, 'ring_count': 2, 'segments': 18, 'vertical_offset': -1.82, 'width': 0.052}`
- Water impact ripple counts: `{'first': {'foam': 3, 'spray': 69, 'total': 72}, 'last': {'foam': 24, 'spray': 48, 'total': 72}, 'max_total': 72, 'mean_total': 72.0, 'min_total': 72}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.65, 'spray': 1.18}`
- Secondary soft pass: `{'alpha_scale': 0.2, 'channels': {'foam': 1.65, 'spray': 2.0}, 'emission_scale': 0.62, 'enabled': True, 'falloff': [0.85, 0.3, 0.09, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.9}`
- Secondary streak pass: `{'alpha_scale': 0.16, 'channels': {'foam': 0.24, 'spray': 0.92}, 'emission_scale': 0.84, 'enabled': True, 'length_scale': 0.052, 'max_length': 1.15, 'min_speed': 0.35, 'width_scale': 0.38}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 165, 'total': 165}, 'last': {'foam': 0, 'spray': 115, 'total': 115}, 'max_total': 165, 'mean_total': 116.72222222222223, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.28, 'channels': {'foam': 1.0}, 'emission_scale': 0.32, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.42, 'radius_z': 0.17, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 8, 'total': 8}, 'last': {'foam': 58, 'total': 58}, 'max_total': 58, 'mean_total': 56.27777777777778, 'min_total': 8}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 67, 'inside_ratio': 0.3872832369942196, 'max_screen_y': 0.9996144763117135, 'mean_screen_y': 0.8277295646959081, 'min_screen_y': 0.5671818423063072}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.42857355384292006, 'mean_screen_y': 0.34226536004457225, 'min_screen_y': 0.13865620281291835}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.8277295646959081, 'mean_inside_ratio': 0.9829800899165062, 'mean_screen_y': 0.4687340539018103, 'min_inside_ratio': 0.3872832369942196, 'min_mean_screen_y': 0.31180111508185154}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 0.9829800899165062, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 0.3872832369942196, 'threshold': 0.3, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.4687340539018103, 'threshold': 0.45, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.4687340539018103, 'threshold': 0.85, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.42, 0.98, 0.95], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 68.99239174923683, 'mean': 93.32829847195457, 'max': 117.91804662585058}, 'contrast': {'min': 130.0, 'mean': 189.625, 'max': 216.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.0003663962174053925, 'max': 0.00124494772924945}, 'nonblank_ratio': {'min': 0.9999786824018965, 'mean': 0.999995470010403, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 0.9999786824018965, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 130.0, 'threshold': 60.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 93.32829847195457, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 93.32829847195457, 'threshold': 125.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0003663962174053925, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.2, 0.98, 0.9], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 27, 'mean': 171.375, 'max': 192}, 'crop_ratio': {'min': 0.140625, 'mean': 0.892578125, 'max': 1.0}, 'depth_mean': {'min': 29.08275720394586, 'mean': 30.49934083160361, 'max': 32.05260541980855}, 'depth_span': {'min': 10.824869690074607, 'mean': 11.823675577737703, 'max': 12.175475117846624}, 'normalized_depth_span': {'min': 0.3461462313327826, 'mean': 0.38826145801209555, 'max': 0.41479851724576683}, 'channel_depth_delta': {'min': 0.3877332121374977, 'mean': 1.5896088157864514, 'max': 4.507669816421977}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 171.375, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.892578125, 'threshold': 0.75, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 11.823675577737703, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.38826145801209555, 'threshold': 0.2, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.3, 0.98, 0.88], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 14.422500116889797, 'mean': 31.03750189945919, 'max': 41.72892866605365}, 'edge_nonzero_ratio': {'min': 0.22849227748079112, 'mean': 0.3558334826925175, 'max': 0.442825304303103}, 'highlight_ratio': {'min': 0.0, 'mean': 0.0003345970419088883, 'max': 0.0011377273506538036}, 'mean_luminance': {'min': 70.99432500038964, 'mean': 98.57490566019356, 'max': 119.7724779078285}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 31.03750189945919, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.3558334826925175, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0011377273506538036, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=165 droplet=0 foam=8 bubble=19 total=192`
- Secondary channels last: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance QA: `{'min_total_fraction': 0.5, 'min_foam_fraction': 0.04}`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `7`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=4853 impact_candidates=31115 foam_ready=58 grad_max=0.5648089275889828 curvature_abs_max=2.023354791556619`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Secondary depth comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 91.71s |
| `validate_render_cache` | `0` | 113.89s |
| `reconstruct_water` | `0` | 70.34s |
| `convert_render_cache` | `0` | 132.73s |
| `render_blender` | `0` | 281.93s |
| `assemble_gif` | `0` | 2.88s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S107 should refresh the compact cinematic benchmark summary with S106 included so runtime, grid size, framing, focus, and secondary-depth deltas can guide the next large-grid step.
