# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_environment_depth_context`
- Render preset: `dam_break_environment_depth_context`
- Selected renderer: `blender`
- Simulation scene: `nonboxed-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `192`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `32 x 40 x 26`
- Simulation steps: `36`

## Artifacts

- manifest: `build/shots/s130_environment_depth_context/cache/manifest.json`
- export_stamp: `build/shots/s130_environment_depth_context/cache/export_stamp.json`
- validation_stamp: `build/shots/s130_environment_depth_context/cache/validation_stamp.json`
- sequence: `build/shots/s130_environment_depth_context/converted/sequence.json`
- water_reconstruction: `build/shots/s130_environment_depth_context/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s130_environment_depth_context/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s130_environment_depth_context/blender/frames`
- gif: `build/shots/s130_environment_depth_context/shot.gif`
- gif_stamp: `build/shots/s130_environment_depth_context/gif_stamp.json`
- contact_sheet: `build/shots/s130_environment_depth_context/review/contact_sheet.png`
- review_manifest: `build/shots/s130_environment_depth_context/review/review_manifest.json`
- comparison_sheet: `build/shots/s130_environment_depth_context/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s130_environment_depth_context/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s130_environment_depth_context/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s130_environment_depth_context/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s130_environment_depth_context/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s130_environment_depth_context/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s130_environment_depth_context/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s130_environment_depth_context/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s130_environment_depth_context/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s130_environment_depth_context/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s130_environment_depth_context/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s130_environment_depth_context/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s130_environment_depth_context/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s130_environment_depth_context/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s130_environment_depth_context/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s130_environment_depth_context/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s130_environment_depth_context/review`

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
- GIF bytes: `22521818`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.1818181818181819`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 14.60909090909091, 'max_target_distance': 34.827762745419626, 'max_target_y': 12.6, 'max_vertical_fov_degrees': 56.0, 'min_position_y': 13.809090909090909, 'min_target_distance': 31.522660090378693, 'min_target_y': 11.8, 'min_vertical_fov_degrees': 52.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 13.809090909090909, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 31.522660090378693, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 56.0, 'threshold': 56.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.0037727864583333333, 'mean': 0.0023434787326388888, 'min': 0.0014713541666666666}, 'contrast': {'max': 240.0, 'mean': 234.27777777777777, 'min': 208.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0006108940972222222, 'mean': 0.0002086648823302469, 'min': 7.595486111111111e-05}, 'mean_luminance': {'max': 93.42478298611111, 'mean': 84.67725875289352, 'min': 76.98540907118056}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1235924.0, 'mean': 1108724.0555555555, 'min': 966362.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 208.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 84.67725875289352, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 84.67725875289352, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0023434787326388888, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.6629340277777778, 'mean': 1.9931750992063493, 'max': 3.6669791666666667}, 'peak_delta': {'min': 60, 'mean': 83.97142857142858, 'max': 145}, 'highlight_change_ratio': {'min': 0.0, 'mean': 6.448412698412698e-06, 'max': 0.0001388888888888889}, 'highlight_ratio': {'min': 0.0, 'mean': 4.822530864197531e-06, 'max': 0.00012152777777777777}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 1.9931750992063493, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 3.6669791666666667, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 145.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0001388888888888889, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.52`
- Water rim strength: `0.52`
- Water surface detail: `{'depth': 5, 'enabled': True, 'scale': 2.25, 'strength': 0.058}`
- Water surface glint pass: `{'alpha_scale': 0.23, 'count': 52, 'drift_per_frame': 0.105, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.7, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.035}`
- Water reflection pass: `{'alpha_scale': 0.34, 'count': 24, 'drift_per_frame': 0.048, 'emission_scale': 0.72, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.6, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water volume scattering pass: `{'alpha_scale': 0.145, 'emission_scale': 0.48, 'enabled': True, 'inset': 0.42, 'layers': 12, 'region_max': [30.4, 9.2, 22.4], 'region_min': [1.6, 1.15, 2.6]}`
- Contact mist curtain pass: `{'alpha_scale': 0.1, 'emission_scale': 0.38, 'enabled': True, 'layers': 10, 'region_max': [28.4, 16.8, 21.6], 'region_min': [4.2, 1.6, 6.8], 'x_inset': 2.6, 'z_jitter': 0.62}`
- Water impact ripple pass: `{'alpha_scale': 0.38, 'arc_fraction': 0.58, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.68, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 72, 'radius': 0.5, 'radius_step': 0.3, 'ring_count': 2, 'segments': 18, 'vertical_offset': -1.82, 'width': 0.052}`
- Water impact ripple counts: `{'first': {'foam': 24, 'spray': 48, 'total': 72}, 'last': {'foam': 24, 'spray': 48, 'total': 72}, 'max_total': 72, 'mean_total': 72.0, 'min_total': 72}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.65, 'spray': 1.18}`
- Secondary soft pass: `{'alpha_scale': 0.21, 'channels': {'foam': 1.85, 'spray': 2.15}, 'emission_scale': 0.68, 'enabled': True, 'falloff': [0.9, 0.34, 0.11, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 1.12}`
- Secondary streak pass: `{'alpha_scale': 0.16, 'channels': {'foam': 0.24, 'spray': 0.92}, 'emission_scale': 0.84, 'enabled': True, 'length_scale': 0.052, 'max_length': 1.15, 'min_speed': 0.35, 'width_scale': 0.38}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 115, 'total': 115}, 'max_total': 116, 'mean_total': 115.33333333333333, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.28, 'channels': {'foam': 1.0}, 'emission_scale': 0.34, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.5, 'radius_z': 0.2, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 58, 'total': 58}, 'last': {'foam': 58, 'total': 58}, 'max_total': 58, 'mean_total': 57.666666666666664, 'min_total': 57}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6416982697205789, 'mean_screen_y': 0.6058554703596924, 'min_screen_y': 0.5874355407340219}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.48911578495754, 'mean_screen_y': 0.4106535127741074, 'min_screen_y': 0.2674053210697996}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.6058554703596924, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.4970873355523577, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.3927158573981728}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.3, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.4970873355523577, 'threshold': 0.36, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.4970873355523577, 'threshold': 0.86, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.34, 0.98, 0.92], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 69.24872089299245, 'mean': 81.19400977589264, 'max': 96.36435607214554}, 'contrast': {'min': 197.0, 'mean': 227.875, 'max': 239.0}, 'bright_ratio': {'min': 0.0, 'mean': 8.055444894898414e-05, 'max': 0.0004452464087362032}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 197.0, 'threshold': 60.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 81.19400977589264, 'threshold': 68.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 81.19400977589264, 'threshold': 128.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 8.055444894898414e-05, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.16, 0.98, 0.9], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}, 'depth_mean': {'min': 31.737971916147515, 'mean': 33.19163499259244, 'max': 34.88714607591658}, 'depth_span': {'min': 10.622566975820927, 'mean': 11.020002740631115, 'max': 11.5933227989923}, 'normalized_depth_span': {'min': 0.30628514264240153, 'mean': 0.33261103165952643, 'max': 0.36528240776134463}, 'channel_depth_delta': {'min': 0.15711824320414536, 'mean': 0.5176147730989742, 'max': 1.682089206767806}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 192.0, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 1.0, 'threshold': 0.68, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 11.020002740631115, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.33261103165952643, 'threshold': 0.2, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.28, 0.98, 0.9], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 14.210081287156191, 'mean': 22.429699253954805, 'max': 30.611545259344737}, 'edge_nonzero_ratio': {'min': 0.19742809774908343, 'mean': 0.2962964315449672, 'max': 0.3914290618016097}, 'highlight_ratio': {'min': 5.4775711719080934e-06, 'mean': 6.778494325236265e-05, 'max': 0.0003998626955492908}, 'mean_luminance': {'min': 70.72632045982384, 'mean': 82.45205550422868, 'max': 96.46563006675333}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 22.429699253954805, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.2962964315449672, 'threshold': 0.025, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0003998626955492908, 'threshold': 0.01, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance QA: `{'min_total_fraction': 0.5, 'min_foam_fraction': 0.04}`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `7`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=4304 impact_candidates=25806 foam_ready=58 grad_max=0.5686722307342169 curvature_abs_max=2.806308190828137`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Secondary depth comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 93.26s |
| `validate_render_cache` | `0` | 115.23s |
| `reconstruct_water` | `0` | 69.95s |
| `convert_render_cache` | `0` | 133.81s |
| `render_blender` | `0` | 285.45s |
| `assemble_gif` | `0` | 3.88s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The non-boxed water-event scene is selected, with a rounded/tapered falling source and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Visual inspection shows the S130 floor/world/mist treatment softens the enclosure read, but the late-frame water column still reads as a contained large vertical mass rather than a fully open environment.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S131 should package and publish the S130 review artifacts so the environment/depth-context pass can be inspected externally before the next visible shot-shape adjustment.
