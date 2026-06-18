# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_water_surface_breakup_noise_tuned`
- Render preset: `dam_break_water_surface_breakup_noise_tuned`
- Selected renderer: `blender`
- Simulation scene: `large-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `192`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `28 x 34 x 22`
- Simulation steps: `36`

## Artifacts

- manifest: `build/shots/s94_water_surface_breakup_noise_tuning/cache/manifest.json`
- sequence: `build/shots/s94_water_surface_breakup_noise_tuning/converted/sequence.json`
- water_reconstruction: `build/shots/s94_water_surface_breakup_noise_tuning/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s94_water_surface_breakup_noise_tuning/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s94_water_surface_breakup_noise_tuning/blender/frames`
- gif: `build/shots/s94_water_surface_breakup_noise_tuning/shot.gif`
- contact_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/contact_sheet.png`
- review_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/review_manifest.json`
- comparison_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/focus_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s94_water_surface_breakup_noise_tuning/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s94_water_surface_breakup_noise_tuning/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s94_water_surface_breakup_noise_tuning/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `24468934`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 10.9, 'max_target_distance': 26.959274841879555, 'max_target_y': 8.45, 'max_vertical_fov_degrees': 42.0, 'min_position_y': 10.2, 'min_target_distance': 24.931556309223858, 'min_target_y': 7.65, 'min_vertical_fov_degrees': 38.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 10.2, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 24.931556309223858, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 42.0, 'threshold': 42.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.01836154513888889, 'mean': 0.009362280574845679, 'min': 0.0038823784722222224}, 'contrast': {'max': 203.0, 'mean': 184.94444444444446, 'min': 124.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0018467881944444445, 'mean': 0.000985544463734568, 'min': 0.0}, 'mean_luminance': {'max': 115.28735568576388, 'mean': 98.93350893373844, 'min': 77.8071169704861}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1323761.0, 'mean': 1209129.5833333333, 'min': 938340.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 124.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 98.93350893373844, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 98.93350893373844, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.009362280574845679, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 1.563142361111111, 'mean': 3.6548660714285712, 'max': 11.518263888888889}, 'peak_delta': {'min': 73, 'mean': 119.88571428571429, 'max': 154}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.0002435515873015873, 'max': 0.0007291666666666667}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00013261959876543212, 'max': 0.0005381944444444444}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.6548660714285712, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 11.518263888888889, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 154.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0007291666666666667, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 5, 'enabled': True, 'scale': 2.25, 'strength': 0.058}`
- Water surface glint pass: `{'alpha_scale': 0.23, 'count': 52, 'drift_per_frame': 0.105, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.7, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.035}`
- Water reflection pass: `{'alpha_scale': 0.32, 'count': 24, 'drift_per_frame': 0.048, 'emission_scale': 0.68, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.6, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water impact ripple pass: `{'alpha_scale': 0.44, 'arc_fraction': 0.58, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.82, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 72, 'radius': 0.5, 'radius_step': 0.3, 'ring_count': 2, 'segments': 18, 'vertical_offset': -1.82, 'width': 0.052}`
- Water impact ripple counts: `{'first': {'foam': 24, 'spray': 48, 'total': 72}, 'last': {'foam': 21, 'spray': 51, 'total': 72}, 'max_total': 72, 'mean_total': 72.0, 'min_total': 72}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary soft pass: `{'alpha_scale': 0.22, 'channels': {'foam': 2.0, 'spray': 2.35}, 'emission_scale': 0.88, 'enabled': True, 'falloff': [1.0, 0.32, 0.08, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.98}`
- Secondary streak pass: `{'alpha_scale': 0.21, 'channels': {'foam': 0.35, 'spray': 1.0}, 'emission_scale': 1.08, 'enabled': True, 'length_scale': 0.06, 'max_length': 1.35, 'min_speed': 0.35, 'width_scale': 0.5}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 119, 'total': 119}, 'max_total': 119, 'mean_total': 115.44444444444444, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.34, 'channels': {'foam': 1.0}, 'emission_scale': 0.42, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.32, 'radius_z': 0.2, 'vertical_offset': -1.85}`
- Surface contact foam counts: `{'first': {'foam': 58, 'total': 58}, 'last': {'foam': 54, 'total': 54}, 'max_total': 58, 'mean_total': 57.55555555555556, 'min_total': 54}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.8032119779615798, 'mean_screen_y': 0.7388055046747581, 'min_screen_y': 0.7063495830540394}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6451713230328047, 'mean_screen_y': 0.5715992670196514, 'min_screen_y': 0.3639907243701549}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.7388055046747581, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.6095358393065992, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.5043347203466833}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.98, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.6095358393065992, 'threshold': 0.45, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.6095358393065992, 'threshold': 0.75, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.3, 0.98, 0.88], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 70.9915566603806, 'mean': 92.27430552849773, 'max': 114.66997724545298}, 'contrast': {'min': 78.0, 'mean': 151.75, 'max': 197.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00036722877670931843, 'max': 0.0009838224521920734}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 78.0, 'threshold': 42.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 92.27430552849773, 'threshold': 58.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 92.27430552849773, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00036722877670931843, 'threshold': 0.00018, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.3, 0.98, 0.88], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 19.258836868600284, 'mean': 35.24571891121051, 'max': 47.716308464379786}, 'edge_nonzero_ratio': {'min': 0.26239031840780513, 'mean': 0.371168449885448, 'max': 0.44600470676246434}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00036722877670931843, 'max': 0.0009838224521920734}, 'mean_luminance': {'min': 70.9915566603806, 'mean': 92.27430552849773, 'max': 114.66997724545298}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 35.24571891121051, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.371168449885448, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0009838224521920734, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 55.54s |
| `validate_render_cache` | `0` | 65.74s |
| `reconstruct_water` | `0` | 42.42s |
| `convert_render_cache` | `0` | 79.29s |
| `render_blender` | `0` | 227.79s |
| `assemble_gif` | `0` | 4.02s |

## S93 to S94 Delta

- Render preset changed from `dam_break_contact_foam_ripple_integrated` to `dam_break_water_surface_breakup_noise_tuned`.
- Water surface detail changed from strength `0.045`, scale `2.8`, depth `4` to strength `0.058`, scale `2.25`, depth `5`.
- Ripple readability comparison source count is `2`, comparing S93 against S94.
- Ripple readability QA, focus review QA, visual QA, temporal highlight QA, camera stability, and secondary framing QA all pass.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S95 should tune spray/foam depth layering so secondaries sit more naturally in the contact volume while preserving diagnostic, temporal, and secondary framing gates.
