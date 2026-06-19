# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_secondary_mist_integrated`
- Render preset: `dam_break_secondary_mist_integrated`
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

- manifest: `build/shots/s154_secondary_mist_integration/cache/manifest.json`
- export_stamp: `build/shots/s154_secondary_mist_integration/cache/export_stamp.json`
- validation_stamp: `build/shots/s154_secondary_mist_integration/cache/validation_stamp.json`
- sequence: `build/shots/s154_secondary_mist_integration/converted/sequence.json`
- water_reconstruction: `build/shots/s154_secondary_mist_integration/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s154_secondary_mist_integration/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s154_secondary_mist_integration/blender/frames`
- gif: `build/shots/s154_secondary_mist_integration/shot.gif`
- gif_stamp: `build/shots/s154_secondary_mist_integration/gif_stamp.json`
- contact_sheet: `build/shots/s154_secondary_mist_integration/review/contact_sheet.png`
- review_manifest: `build/shots/s154_secondary_mist_integration/review/review_manifest.json`
- comparison_sheet: `build/shots/s154_secondary_mist_integration/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s154_secondary_mist_integration/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s154_secondary_mist_integration/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s154_secondary_mist_integration/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s154_secondary_mist_integration/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s154_secondary_mist_integration/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s154_secondary_mist_integration/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s154_secondary_mist_integration/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s154_secondary_mist_integration/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s154_secondary_mist_integration/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s154_secondary_mist_integration/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s154_secondary_mist_integration/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s154_secondary_mist_integration/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s154_secondary_mist_integration/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s154_secondary_mist_integration/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s154_secondary_mist_integration/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s154_secondary_mist_integration/review`

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
- GIF bytes: `25099815`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 47, 'selected_frame_count': 36, 'source_frame_count': 48, 'start_fraction': 0.2553191489361702, 'start_index': 12}`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 12.2, 'max_target_distance': 24.461602564018573, 'max_target_y': 7.6, 'max_vertical_fov_degrees': 39.0, 'min_position_y': 11.4, 'min_target_distance': 22.054704713507277, 'min_target_y': 7.0, 'min_vertical_fov_degrees': 37.5}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 11.4, 'threshold': 11.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 22.054704713507277, 'threshold': 21.5, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 39.0, 'threshold': 39.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.0029600694444444444, 'mean': 0.000976954330632716, 'min': 2.0616319444444445e-05}, 'contrast': {'max': 195.0, 'mean': 190.94444444444446, 'min': 179.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0011393229166666667, 'mean': 0.00041573230131172837, 'min': 7.595486111111111e-06}, 'mean_luminance': {'max': 98.25838975694444, 'mean': 91.47068618586033, 'min': 78.82389539930556}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1226466.0, 'mean': 1176588.2777777778, 'min': 1011312.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 179.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 91.47068618586033, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 91.47068618586033, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.000976954330632716, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 0.8994444444444445, 'mean': 3.698208333333333, 'max': 8.06032986111111}, 'peak_delta': {'min': 42, 'mean': 110.34285714285714, 'max': 158}, 'highlight_change_ratio': {'min': 0.0, 'mean': 0.00019047619047619048, 'max': 0.0006076388888888889}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00010513117283950617, 'max': 0.00034722222222222224}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 3.698208333333333, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 8.06032986111111, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 158.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.0006076388888888889, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.62`
- Water rim strength: `0.58`
- Water surface detail: `{'depth': 6, 'enabled': True, 'scale': 2.8, 'strength': 0.07}`
- Water surface glint pass: `{'alpha_scale': 0.24, 'count': 72, 'drift_per_frame': 0.12, 'emission_scale': 0.5, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.45, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.032}`
- Water reflection pass: `{'alpha_scale': 0.36, 'count': 34, 'drift_per_frame': 0.048, 'emission_scale': 0.72, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.3, 'region_max': [27.2, 8.2, 18.9], 'region_min': [1.0, 5.0, 3.4], 'width': 0.115}`
- Water volume scattering pass: `{'alpha_scale': 0.17, 'emission_scale': 0.54, 'enabled': True, 'inset': 0.5, 'layers': 14, 'region_max': [30.6, 9.05, 22.4], 'region_min': [1.0, 1.08, 2.6]}`
- Contact mist curtain pass: `{'alpha_scale': 0.105, 'emission_scale': 0.4, 'enabled': True, 'layers': 11, 'region_max': [29.0, 16.8, 22.0], 'region_min': [3.6, 1.6, 6.2], 'x_inset': 3.0, 'z_jitter': 0.62}`
- Water impact ripple pass: `{'alpha_scale': 0.46, 'arc_fraction': 0.66, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.78, 'enabled': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'edge_shader', 'max_count': 96, 'radius': 0.48, 'radius_step': 0.24, 'ring_count': 3, 'segments': 22, 'vertical_offset': -1.82, 'width': 0.045}`
- Water impact ripple counts: `{'first': {'foam': 32, 'spray': 64, 'total': 96}, 'last': {'foam': 32, 'spray': 64, 'total': 96}, 'max_total': 96, 'mean_total': 96.0, 'min_total': 96}`
- Secondary channel radius scales: `{'bubble': 0.58, 'droplet': 0.78, 'foam': 1.12, 'spray': 0.86}`
- Secondary soft pass: `{'alpha_scale': 0.24, 'channels': {'foam': 2.05, 'spray': 2.45}, 'emission_scale': 0.74, 'enabled': True, 'falloff': [0.82, 0.32, 0.1, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 1.18}`
- Secondary streak pass: `{'alpha_scale': 0.18, 'channels': {'foam': 0.42, 'spray': 1.12}, 'emission_scale': 0.9, 'enabled': True, 'length_scale': 0.066, 'max_length': 1.45, 'min_speed': 0.32, 'width_scale': 0.34}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 115, 'total': 115}, 'max_total': 116, 'mean_total': 115.33333333333333, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.34, 'channels': {'foam': 1.0}, 'emission_scale': 0.42, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 300, 'radius_x': 1.68, 'radius_z': 0.24, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 58, 'total': 58}, 'last': {'foam': 58, 'total': 58}, 'max_total': 58, 'mean_total': 57.666666666666664, 'min_total': 57}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.999979453215318, 'mean_screen_y': 0.8619020917590691, 'min_screen_y': 0.7196362862661009}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6888086344887481, 'mean_screen_y': 0.6114233662053056, 'min_screen_y': 0.4204323717437235}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.8619020917590691, 'mean_inside_ratio': 0.9998394348105332, 'mean_screen_y': 0.688505663724881, 'min_inside_ratio': 0.9942196531791907, 'min_mean_screen_y': 0.6114233662053056}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 0.9998394348105332, 'threshold': 0.82, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 0.9942196531791907, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.688505663724881, 'threshold': 0.38, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.688505663724881, 'threshold': 0.96, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 79.63894066527736, 'mean': 88.38959056505186, 'max': 95.40693083828859}, 'contrast': {'min': 78.0, 'mean': 169.625, 'max': 194.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00023452157598499062, 'max': 0.0006676607733253479}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 78.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 88.38959056505186, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 88.38959056505186, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00023452157598499062, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 192, 'mean': 192.0, 'max': 192}, 'crop_particles': {'min': 125, 'mean': 183.25, 'max': 192}, 'crop_ratio': {'min': 0.6510416666666666, 'mean': 0.9544270833333334, 'max': 1.0}, 'depth_mean': {'min': 21.802633360749116, 'mean': 23.013404845120743, 'max': 25.063715797107886}, 'depth_span': {'min': 5.867782601718893, 'mean': 7.9085947003051045, 'max': 9.894831378119193}, 'normalized_depth_span': {'min': 0.25841889179048616, 'mean': 0.3427628868088418, 'max': 0.40338535441823337}, 'channel_depth_delta': {'min': 0.18202028835466422, 'mean': 0.5319569806468798, 'max': 1.3881876009513157}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 183.25, 'threshold': 100.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.9544270833333334, 'threshold': 0.55, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 7.9085947003051045, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.3427628868088418, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 19.73588898191663, 'mean': 27.50403728511101, 'max': 31.761496904620763}, 'edge_nonzero_ratio': {'min': 0.24994347036930656, 'mean': 0.3365692090740752, 'max': 0.38040163538693766}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00023452157598499062, 'max': 0.0006676607733253479}, 'mean_luminance': {'min': 79.63894066527736, 'mean': 88.38959056505186, 'max': 95.40693083828859}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 27.50403728511101, 'threshold': 9.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.3365692090740752, 'threshold': 0.03, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0006676607733253479, 'threshold': 0.011, 'operator': '<=', 'passed': True}]}`
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
| `export_render_cache` | `0` | 126.50s |
| `validate_render_cache` | `0` | 161.42s |
| `reconstruct_water` | `0` | 89.29s |
| `convert_render_cache` | `0` | 182.93s |
| `render_blender` | `0` | 292.66s |
| `assemble_gif` | `0` | 2.77s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The secondary mist integration pass is renderer-side: it softens direct secondary beads and adds soft/streak overlays, but it is not yet a physically coupled spray/foam solver.
- Direct secondary particles are still visible in some frames; the pass de-emphasizes them instead of replacing the particle representation.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

Package and publish the S154 shot artifacts, then review the public gallery to decide whether the next visible adjustment should target stronger foam sheet continuity or remaining source-edge composition.
