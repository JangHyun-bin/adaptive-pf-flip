# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_large_grid_cinematic_benchmark`
- Render preset: `dam_break_large_grid_cinematic_benchmark`
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

- manifest: `build/shots/s104_large_grid_cinematic_benchmark/cache/manifest.json`
- sequence: `build/shots/s104_large_grid_cinematic_benchmark/converted/sequence.json`
- water_reconstruction: `build/shots/s104_large_grid_cinematic_benchmark/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s104_large_grid_cinematic_benchmark/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s104_large_grid_cinematic_benchmark/blender/frames`
- gif: `build/shots/s104_large_grid_cinematic_benchmark/shot.gif`
- contact_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/contact_sheet.png`
- review_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/review_manifest.json`
- comparison_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s104_large_grid_cinematic_benchmark/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s104_large_grid_cinematic_benchmark/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s104_large_grid_cinematic_benchmark/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `23206759`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.1818181818181819`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 14.345454545454546, 'max_target_distance': 31.860961176766747, 'max_target_y': 11.45, 'max_vertical_fov_degrees': 46.0, 'min_position_y': 13.663636363636362, 'min_target_distance': 29.464566547264564, 'min_target_y': 10.65, 'min_vertical_fov_degrees': 42.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 13.663636363636362, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 29.464566547264564, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 46.0, 'threshold': 46.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.007108289930555556, 'mean': 0.0032716652199074074, 'min': 0.00042100694444444444}, 'contrast': {'max': 248.0, 'mean': 221.25, 'min': 186.0}, 'dark_ratio': {'max': 1.193576388888889e-05, 'mean': 3.978587962962963e-06, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0027745225694444445, 'mean': 0.0005861786265432098, 'min': 6.510416666666667e-06}, 'mean_luminance': {'max': 117.51225477430556, 'mean': 98.6345341133777, 'min': 79.99169596354167}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1268892.0, 'mean': 1145666.0555555555, 'min': 882464.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 186.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 98.6345341133777, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 98.6345341133777, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0032716652199074074, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.9032465277777778, 'mean': 3.0000347222222223, 'max': 6.150486111111111}, 'peak_delta': {'min': 61, 'mean': 105.34285714285714, 'max': 164}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00022867063492063494, 'max': 0.0014409722222222222}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00013261959876543212, 'max': 0.0011111111111111111}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.0000347222222223, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 6.150486111111111, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 164.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0014409722222222222, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
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
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 25, 'inside_ratio': 0.14450867052023122, 'max_screen_y': 0.6979364563435881, 'mean_screen_y': 0.675665133252088, 'min_screen_y': 0.6603460409716837}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.5232907122891027, 'mean_screen_y': 0.4268253131984951, 'min_screen_y': 0.20578317698437265}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.678792217407043, 'mean_inside_ratio': 0.9760757867694285, 'mean_screen_y': 0.5489792537934561, 'min_inside_ratio': 0.14450867052023122, 'min_mean_screen_y': 0.3929399196248322}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 0.9760757867694285, 'threshold': 0.85, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 0.14450867052023122, 'threshold': 0.1, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.5489792537934561, 'threshold': 0.45, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.5489792537934561, 'threshold': 0.75, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.42, 0.98, 0.95], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 72.4544378975732, 'mean': 88.0941872772311, 'max': 112.56298071183724}, 'contrast': {'min': 130.0, 'mean': 180.625, 'max': 243.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00023076299947132357, 'max': 0.0006693725804526152}, 'nonblank_ratio': {'min': 0.9998912802496717, 'mean': 0.9999664247829868, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 0.9998912802496717, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 130.0, 'threshold': 60.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 88.0941872772311, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 88.0941872772311, 'threshold': 125.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00023076299947132357, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.2, 0.98, 0.9], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 27, 'mean': 171.375, 'max': 192}, 'crop_ratio': {'min': 0.140625, 'mean': 0.892578125, 'max': 1.0}, 'depth_mean': {'min': 29.344028919663653, 'mean': 30.501249114296794, 'max': 31.81711578100854}, 'depth_span': {'min': 10.783309453188227, 'mean': 11.770601272402327, 'max': 12.133512396979242}, 'normalized_depth_span': {'min': 0.3478221581827535, 'mean': 0.3862992876531254, 'max': 0.40946922790917234}, 'channel_depth_delta': {'min': 0.39151362098146336, 'mean': 1.579799126836599, 'max': 4.483791124264808}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 171.375, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.892578125, 'threshold': 0.75, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 11.770601272402327, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.3862992876531254, 'threshold': 0.2, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.3, 0.98, 0.88], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 13.95871062762028, 'mean': 28.105198868506772, 'max': 40.41614326013435}, 'edge_nonzero_ratio': {'min': 0.21934370275704065, 'mean': 0.33347416930318097, 'max': 0.43696522918192726}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00029173744993220394, 'max': 0.0010792824525037794}, 'mean_luminance': {'min': 70.30198478874118, 'mean': 91.74030545251937, 'max': 115.72927933544254}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 28.105198868506772, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.33347416930318097, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0010792824525037794, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 92.95s |
| `validate_render_cache` | `0` | 114.74s |
| `reconstruct_water` | `0` | 68.98s |
| `convert_render_cache` | `0` | 132.62s |
| `render_blender` | `0` | 281.17s |
| `assemble_gif` | `0` | 2.86s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S105 should add a compact cinematic benchmark summary table for recent gates so runtime, grid size, and key QA metrics can be compared without re-opening each full report.
