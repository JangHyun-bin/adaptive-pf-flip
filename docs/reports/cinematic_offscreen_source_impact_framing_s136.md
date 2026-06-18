# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_offscreen_source_impact_framing`
- Render preset: `dam_break_offscreen_source_impact_framing`
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

- manifest: `build/shots/s136_offscreen_source_impact_framing/cache/manifest.json`
- export_stamp: `build/shots/s136_offscreen_source_impact_framing/cache/export_stamp.json`
- validation_stamp: `build/shots/s136_offscreen_source_impact_framing/cache/validation_stamp.json`
- sequence: `build/shots/s136_offscreen_source_impact_framing/converted/sequence.json`
- water_reconstruction: `build/shots/s136_offscreen_source_impact_framing/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s136_offscreen_source_impact_framing/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s136_offscreen_source_impact_framing/blender/frames`
- gif: `build/shots/s136_offscreen_source_impact_framing/shot.gif`
- gif_stamp: `build/shots/s136_offscreen_source_impact_framing/gif_stamp.json`
- contact_sheet: `build/shots/s136_offscreen_source_impact_framing/review/contact_sheet.png`
- review_manifest: `build/shots/s136_offscreen_source_impact_framing/review/review_manifest.json`
- comparison_sheet: `build/shots/s136_offscreen_source_impact_framing/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s136_offscreen_source_impact_framing/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s136_offscreen_source_impact_framing/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s136_offscreen_source_impact_framing/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s136_offscreen_source_impact_framing/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s136_offscreen_source_impact_framing/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s136_offscreen_source_impact_framing/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s136_offscreen_source_impact_framing/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s136_offscreen_source_impact_framing/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s136_offscreen_source_impact_framing/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s136_offscreen_source_impact_framing/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s136_offscreen_source_impact_framing/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s136_offscreen_source_impact_framing/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s136_offscreen_source_impact_framing/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s136_offscreen_source_impact_framing/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s136_offscreen_source_impact_framing/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s136_offscreen_source_impact_framing/review`

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
- GIF bytes: `24080794`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.08`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 14.088000000000001, 'max_target_distance': 26.87269186367455, 'max_target_y': 10.2, 'max_vertical_fov_degrees': 47.0, 'min_position_y': 13.388, 'min_target_distance': 24.304559572228424, 'min_target_y': 9.5, 'min_vertical_fov_degrees': 43.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 13.388, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 24.304559572228424, 'threshold': 23.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 47.0, 'threshold': 52.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.0018413628472222223, 'mean': 0.001004050925925926, 'min': 0.0003884548611111111}, 'contrast': {'max': 228.0, 'mean': 218.52777777777777, 'min': 197.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0007194010416666667, 'mean': 0.00017749927662037037, 'min': 1.953125e-05}, 'mean_luminance': {'max': 100.93858940972223, 'mean': 88.26579963589892, 'min': 76.13331163194445}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1253306.0, 'mean': 1142638.5555555555, 'min': 959731.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 197.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 88.26579963589892, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 88.26579963589892, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.001004050925925926, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.9345486111111111, 'mean': 2.9677450396825398, 'max': 4.482100694444444}, 'peak_delta': {'min': 59, 'mean': 86.85714285714286, 'max': 153}, 'highlight_change_ratio': {'min': 0.0, 'mean': 1.8353174603174602e-05, 'max': 0.00022569444444444443}, 'highlight_ratio': {'min': 0.0, 'mean': 9.162808641975309e-06, 'max': 0.00017361111111111112}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 2.9677450396825398, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 4.482100694444444, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 153.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.00022569444444444443, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
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
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.874027293585125, 'mean_screen_y': 0.7952049291466357, 'min_screen_y': 0.7102361733026797}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6589068223290027, 'mean_screen_y': 0.53392307933408, 'min_screen_y': 0.4021272706731128}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.7952049291466357, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.6112664975247729, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.48010417627970897}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.3, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.6112664975247729, 'threshold': 0.3, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.6112664975247729, 'threshold': 0.88, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.28, 0.98, 0.96], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 76.31601586698906, 'mean': 85.91033623262258, 'max': 100.99228632521333}, 'contrast': {'min': 162.0, 'mean': 206.125, 'max': 222.0}, 'bright_ratio': {'min': 0.0, 'mean': 8.90936099065433e-05, 'max': 0.0003746927519434064}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 162.0, 'threshold': 60.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 85.91033623262258, 'threshold': 68.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 85.91033623262258, 'threshold': 128.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 8.90936099065433e-05, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.94], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}, 'depth_mean': {'min': 23.562656850158913, 'mean': 24.917305995124796, 'max': 26.208733898255545}, 'depth_span': {'min': 5.895501597398486, 'mean': 7.4504069165255284, 'max': 9.76294259181353}, 'normalized_depth_span': {'min': 0.2341147929597585, 'mean': 0.2986254264814718, 'max': 0.3739487969472424}, 'channel_depth_delta': {'min': 0.06377011983332181, 'mean': 0.4787188295930198, 'max': 1.1359533095715015}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 192.0, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 1.0, 'threshold': 0.62, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 7.4504069165255284, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.2986254264814718, 'threshold': 0.2, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.22, 0.98, 0.96], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 14.662032255501709, 'mean': 23.181893253723317, 'max': 32.09002267296539}, 'edge_nonzero_ratio': {'min': 0.20048615482396367, 'mean': 0.30122844998808296, 'max': 0.39860570429808534}, 'highlight_ratio': {'min': 1.5278278565797435e-06, 'mean': 9.014184353820487e-05, 'max': 0.0003437612677304423}, 'mean_luminance': {'min': 76.24110956970256, 'mean': 86.44989431250802, 'max': 101.21150484932562}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 23.181893253723317, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.30122844998808296, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0003437612677304423, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 91.27s |
| `validate_render_cache` | `0` | 115.69s |
| `reconstruct_water` | `0` | 67.85s |
| `convert_render_cache` | `0` | 135.38s |
| `render_blender` | `0` | 326.20s |
| `assemble_gif` | `0` | 2.81s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The source-breakup scene is now framed as an impact shot, but the upper falling mass is still partially visible at the top edge in early frames.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S137 should package and publish the S136 review artifacts through the static gallery/CFTunnel flow, then run visual triage on the public artifact.
