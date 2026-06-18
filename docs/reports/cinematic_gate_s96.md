# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_secondary_depth_reviewed`
- Render preset: `dam_break_secondary_depth_reviewed`
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

- manifest: `build/shots/s96_secondary_depth_review_metric/cache/manifest.json`
- sequence: `build/shots/s96_secondary_depth_review_metric/converted/sequence.json`
- water_reconstruction: `build/shots/s96_secondary_depth_review_metric/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s96_secondary_depth_review_metric/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s96_secondary_depth_review_metric/blender/frames`
- gif: `build/shots/s96_secondary_depth_review_metric/shot.gif`
- contact_sheet: `build/shots/s96_secondary_depth_review_metric/review/contact_sheet.png`
- review_manifest: `build/shots/s96_secondary_depth_review_metric/review/review_manifest.json`
- comparison_sheet: `build/shots/s96_secondary_depth_review_metric/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s96_secondary_depth_review_metric/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s96_secondary_depth_review_metric/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s96_secondary_depth_review_metric/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s96_secondary_depth_review_metric/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s96_secondary_depth_review_metric/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s96_secondary_depth_review_metric/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s96_secondary_depth_review_metric/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s96_secondary_depth_review_metric/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s96_secondary_depth_review_metric/review/secondary_depth_manifest.json`
- ripple_readability_sheet: `build/shots/s96_secondary_depth_review_metric/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s96_secondary_depth_review_metric/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s96_secondary_depth_review_metric/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s96_secondary_depth_review_metric/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s96_secondary_depth_review_metric/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `24513960`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 10.9, 'max_target_distance': 26.959274841879555, 'max_target_y': 8.45, 'max_vertical_fov_degrees': 42.0, 'min_position_y': 10.2, 'min_target_distance': 24.931556309223858, 'min_target_y': 7.65, 'min_vertical_fov_degrees': 38.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 10.2, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 24.931556309223858, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 42.0, 'threshold': 42.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.014946831597222222, 'mean': 0.007738715277777777, 'min': 0.00328125}, 'contrast': {'max': 203.0, 'mean': 186.61111111111111, 'min': 134.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0015711805555555555, 'mean': 0.000866066261574074, 'min': 1.0850694444444444e-06}, 'mean_luminance': {'max': 115.17658311631945, 'mean': 98.67854621793018, 'min': 77.46760959201389}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1323168.0, 'mean': 1210014.638888889, 'min': 940931.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 134.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 98.67854621793018, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 98.67854621793018, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.007738715277777777, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 1.5070138888888889, 'mean': 3.5335992063492063, 'max': 11.359739583333333}, 'peak_delta': {'min': 82, 'mean': 118.4, 'max': 154}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00018898809523809523, 'max': 0.0006597222222222222}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00010464891975308641, 'max': 0.0005034722222222222}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.5335992063492063, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 11.359739583333333, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 154.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0006597222222222222, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 5, 'enabled': True, 'scale': 2.25, 'strength': 0.058}`
- Water surface glint pass: `{'alpha_scale': 0.23, 'count': 52, 'drift_per_frame': 0.105, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.7, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.035}`
- Water reflection pass: `{'alpha_scale': 0.32, 'count': 24, 'drift_per_frame': 0.048, 'emission_scale': 0.68, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.6, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water impact ripple pass: `{'alpha_scale': 0.44, 'arc_fraction': 0.58, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.82, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 72, 'radius': 0.5, 'radius_step': 0.3, 'ring_count': 2, 'segments': 18, 'vertical_offset': -1.82, 'width': 0.052}`
- Water impact ripple counts: `{'first': {'foam': 24, 'spray': 48, 'total': 72}, 'last': {'foam': 21, 'spray': 51, 'total': 72}, 'max_total': 72, 'mean_total': 72.0, 'min_total': 72}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.65, 'spray': 1.18}`
- Secondary soft pass: `{'alpha_scale': 0.18, 'channels': {'foam': 1.65, 'spray': 2.0}, 'emission_scale': 0.72, 'enabled': True, 'falloff': [1.0, 0.28, 0.07, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.86}`
- Secondary streak pass: `{'alpha_scale': 0.18, 'channels': {'foam': 0.24, 'spray': 0.92}, 'emission_scale': 0.94, 'enabled': True, 'length_scale': 0.052, 'max_length': 1.15, 'min_speed': 0.35, 'width_scale': 0.42}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 119, 'total': 119}, 'max_total': 119, 'mean_total': 115.44444444444444, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.3, 'channels': {'foam': 1.0}, 'emission_scale': 0.36, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.42, 'radius_z': 0.17, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 58, 'total': 58}, 'last': {'foam': 54, 'total': 54}, 'max_total': 58, 'mean_total': 57.55555555555556, 'min_total': 54}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.8032119779615798, 'mean_screen_y': 0.7388055046747581, 'min_screen_y': 0.7063495830540394}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6451713230328047, 'mean_screen_y': 0.5715992670196514, 'min_screen_y': 0.3639907243701549}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.7388055046747581, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.6095358393065992, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.5043347203466833}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.98, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.6095358393065992, 'threshold': 0.45, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.6095358393065992, 'threshold': 0.75, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.3, 0.98, 0.88], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 71.00223843959914, 'mean': 92.10830448428221, 'max': 114.5095849632966}, 'contrast': {'min': 78.0, 'mean': 151.5, 'max': 197.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00031219316428471235, 'max': 0.0008084877577420009}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 78.0, 'threshold': 42.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 92.10830448428221, 'threshold': 58.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 92.10830448428221, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00031219316428471235, 'threshold': 0.00018, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.2, 0.98, 0.9], 'channels': ['foam', 'spray'], 'summary': {'active_particles': {'min': 173, 'mean': 173.0, 'max': 173}, 'crop_particles': {'min': 171, 'mean': 172.75, 'max': 173}, 'crop_ratio': {'min': 0.9884393063583815, 'mean': 0.9985549132947977, 'max': 1.0}, 'depth_mean': {'min': 25.01189435319461, 'mean': 25.996863974298453, 'max': 27.159845011208283}, 'depth_span': {'min': 9.448678843864627, 'mean': 10.24169409591493, 'max': 13.755063609373831}, 'normalized_depth_span': {'min': 0.35556613122733755, 'mean': 0.39490058284803364, 'max': 0.5458006728638832}, 'channel_depth_delta': {'min': 0.3978193096248468, 'mean': 0.8290823718149753, 'max': 1.4535808899307838}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 172.75, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.9985549132947977, 'threshold': 0.75, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 10.24169409591493, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.39490058284803364, 'threshold': 0.2, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.3, 0.98, 0.88], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 19.283329177251687, 'mean': 35.43929109260789, 'max': 47.873079111014135}, 'edge_nonzero_ratio': {'min': 0.26256175677571186, 'mean': 0.37179283621401743, 'max': 0.4462638124775961}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00031219316428471235, 'max': 0.0008084877577420009}, 'mean_luminance': {'min': 71.00223843959914, 'mean': 92.10830448428221, 'max': 114.5095849632966}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 35.43929109260789, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.37179283621401743, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0008084877577420009, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 55.63s |
| `validate_render_cache` | `0` | 65.12s |
| `reconstruct_water` | `0` | 42.08s |
| `convert_render_cache` | `0` | 119.04s |
| `render_blender` | `0` | 260.36s |
| `assemble_gif` | `0` | 2.95s |

## S95 to S96 Delta

- Render preset changed from `dam_break_spray_foam_depth_layered` to `dam_break_secondary_depth_reviewed`.
- Added `secondary_depth_review` using the Blender scene spec, camera projection, and spray/foam particle CSV rows.
- New artifacts include `secondary_depth_sheet.png` and `secondary_depth_manifest.json`.
- Secondary depth review gate passes with active frame count `8`, mean crop particles `172.75`, mean crop ratio `0.99855`, mean depth span `10.24169`, and mean normalized depth span `0.39490`.
- Visual QA, temporal highlight QA, camera stability, secondary framing QA, focus review QA, ripple readability QA, and secondary depth review QA all pass.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S97 should use the secondary depth diagnostic to tune a stronger volume-depth material/readability pass without breaking visual, temporal, or depth-review gates.
