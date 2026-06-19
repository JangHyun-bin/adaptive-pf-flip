# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_low_angle_impact_timed`
- Render preset: `dam_break_low_angle_impact_timed`
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

- manifest: `build/shots/s142_impact_timed_window/cache/manifest.json`
- export_stamp: `build/shots/s142_impact_timed_window/cache/export_stamp.json`
- validation_stamp: `build/shots/s142_impact_timed_window/cache/validation_stamp.json`
- sequence: `build/shots/s142_impact_timed_window/converted/sequence.json`
- water_reconstruction: `build/shots/s142_impact_timed_window/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s142_impact_timed_window/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s142_impact_timed_window/blender/frames`
- gif: `build/shots/s142_impact_timed_window/shot.gif`
- gif_stamp: `build/shots/s142_impact_timed_window/gif_stamp.json`
- contact_sheet: `build/shots/s142_impact_timed_window/review/contact_sheet.png`
- review_manifest: `build/shots/s142_impact_timed_window/review/review_manifest.json`
- comparison_sheet: `build/shots/s142_impact_timed_window/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s142_impact_timed_window/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s142_impact_timed_window/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s142_impact_timed_window/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s142_impact_timed_window/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s142_impact_timed_window/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s142_impact_timed_window/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s142_impact_timed_window/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s142_impact_timed_window/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s142_impact_timed_window/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s142_impact_timed_window/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s142_impact_timed_window/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s142_impact_timed_window/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s142_impact_timed_window/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s142_impact_timed_window/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s142_impact_timed_window/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s142_impact_timed_window/review`

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
- GIF bytes: `25293466`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 47, 'selected_frame_count': 38, 'source_frame_count': 48, 'start_fraction': 0.2127659574468085, 'start_index': 10}`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 12.2, 'max_target_distance': 24.32385660210979, 'max_target_y': 8.4, 'max_vertical_fov_degrees': 41.0, 'min_position_y': 11.4, 'min_target_distance': 21.94288039433292, 'min_target_y': 7.6, 'min_vertical_fov_degrees': 39.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 11.4, 'threshold': 11.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 21.94288039433292, 'threshold': 21.5, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 41.0, 'threshold': 41.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.003383246527777778, 'mean': 0.0019164436246141975, 'min': 0.00020616319444444444}, 'contrast': {'max': 211.0, 'mean': 200.27777777777777, 'min': 192.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0010568576388888889, 'mean': 0.00031976393711419753, 'min': 5.4253472222222224e-06}, 'mean_luminance': {'max': 99.03870225694445, 'mean': 91.62912727261767, 'min': 78.73538194444444}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1252641.0, 'mean': 1192517.4722222222, 'min': 1007320.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 192.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 91.62912727261767, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 91.62912727261767, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0019164436246141975, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 1.28859375, 'mean': 3.959465773809524, 'max': 7.8255034722222225}, 'peak_delta': {'min': 66, 'mean': 112.02857142857142, 'max': 148}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00012797619047619048, 'max': 0.00045138888888888887}, 'highlight_ratio': {'min': 0.0, 'mean': 6.510416666666667e-05, 'max': 0.00045138888888888887}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.959465773809524, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 7.8255034722222225, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 148.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.00045138888888888887, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
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
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 116, 'total': 116}, 'last': {'foam': 0, 'spray': 115, 'total': 115}, 'max_total': 116, 'mean_total': 115.33333333333333, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.28, 'channels': {'foam': 1.0}, 'emission_scale': 0.34, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.5, 'radius_z': 0.2, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 57, 'total': 57}, 'last': {'foam': 58, 'total': 58}, 'max_total': 58, 'mean_total': 57.666666666666664, 'min_total': 57}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.9718669194228844, 'mean_screen_y': 0.8282451883461153, 'min_screen_y': 0.7031002551581935}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6426542057664536, 'mean_screen_y': 0.5687539210158431, 'min_screen_y': 0.3857162616730367}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.8282451883461153, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.6484184334866394, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.5687539210158431}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.82, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.6484184334866394, 'threshold': 0.38, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.6484184334866394, 'threshold': 0.96, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 78.33983475013903, 'mean': 89.36247754093051, 'max': 98.09159633565767}, 'contrast': {'min': 95.0, 'mean': 173.25, 'max': 201.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.0001487722375344525, 'max': 0.0004782101191094597}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 95.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 89.36247754093051, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 89.36247754093051, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0001487722375344525, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 155, 'mean': 187.125, 'max': 192}, 'crop_ratio': {'min': 0.8072916666666666, 'mean': 0.974609375, 'max': 1.0}, 'depth_mean': {'min': 21.973814840672635, 'mean': 23.016620367076968, 'max': 24.564995204629138}, 'depth_span': {'min': 5.8117084069836515, 'mean': 7.942015602946986, 'max': 10.162441517853505}, 'normalized_depth_span': {'min': 0.2547983033391107, 'mean': 0.3441580245768204, 'max': 0.41369605136085874}, 'channel_depth_delta': {'min': 0.07162174112081487, 'mean': 0.3276898618899464, 'max': 0.8375696449948542}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 187.125, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.974609375, 'threshold': 0.55, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 7.942015602946986, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.3441580245768204, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 18.260432008604727, 'mean': 26.112582579095648, 'max': 30.96610055551821}, 'edge_nonzero_ratio': {'min': 0.24815438394925168, 'mean': 0.3418320031045462, 'max': 0.3919734035726727}, 'highlight_ratio': {'min': 0.0, 'mean': 0.0001487722375344525, 'max': 0.0004782101191094597}, 'mean_luminance': {'min': 78.33983475013903, 'mean': 89.36247754093051, 'max': 98.09159633565767}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 26.112582579095648, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.3418320031045462, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0004782101191094597, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 207.08s |
| `validate_render_cache` | `0` | 161.04s |
| `reconstruct_water` | `0` | 86.96s |
| `convert_render_cache` | `0` | 179.89s |
| `render_blender` | `0` | 329.14s |
| `assemble_gif` | `0` | 2.81s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The impact-timed window improves the lead-in, but upper source fragments still touch the top edge and the surface remains coarse at close range.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S143 should package and publish the S142 review artifacts, then S144 should triage the public gallery for the next visible shot adjustment.
