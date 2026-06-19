# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_water_depth_foreground_separation`
- Render preset: `dam_break_water_depth_foreground_separation`
- Selected renderer: `blender`
- Simulation scene: `source-slab-deemphasis-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `256`
- Secondary radius scale: `3.0`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `36 x 44 x 28`
- Simulation steps: `56`

## Artifacts

- manifest: `build/shots/s168_water_depth_foreground_separation/cache/manifest.json`
- export_stamp: `build/shots/s168_water_depth_foreground_separation/cache/export_stamp.json`
- validation_stamp: `build/shots/s168_water_depth_foreground_separation/cache/validation_stamp.json`
- sequence: `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- water_reconstruction: `build/shots/s168_water_depth_foreground_separation/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s168_water_depth_foreground_separation/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s168_water_depth_foreground_separation/blender/frames`
- gif: `build/shots/s168_water_depth_foreground_separation/shot.gif`
- gif_stamp: `build/shots/s168_water_depth_foreground_separation/gif_stamp.json`
- contact_sheet: `build/shots/s168_water_depth_foreground_separation/review/contact_sheet.png`
- review_manifest: `build/shots/s168_water_depth_foreground_separation/review/review_manifest.json`
- comparison_sheet: `build/shots/s168_water_depth_foreground_separation/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s168_water_depth_foreground_separation/review/comparison_manifest.json`
- temporal_diff_sheet: `build/shots/s168_water_depth_foreground_separation/review/temporal_diff_sheet.png`
- temporal_diff_manifest: `build/shots/s168_water_depth_foreground_separation/review/temporal_diff_manifest.json`
- focus_sheet: `build/shots/s168_water_depth_foreground_separation/review/focus_sheet.png`
- focus_review_manifest: `build/shots/s168_water_depth_foreground_separation/review/focus_review_manifest.json`
- focus_comparison_sheet: `build/shots/s168_water_depth_foreground_separation/review/focus_comparison_sheet.png`
- focus_comparison_manifest: `build/shots/s168_water_depth_foreground_separation/review/focus_comparison_manifest.json`
- secondary_depth_sheet: `build/shots/s168_water_depth_foreground_separation/review/secondary_depth_sheet.png`
- secondary_depth_manifest: `build/shots/s168_water_depth_foreground_separation/review/secondary_depth_manifest.json`
- secondary_depth_comparison_sheet: `build/shots/s168_water_depth_foreground_separation/review/secondary_depth_comparison_sheet.png`
- secondary_depth_comparison_manifest: `build/shots/s168_water_depth_foreground_separation/review/secondary_depth_comparison_manifest.json`
- ripple_readability_sheet: `build/shots/s168_water_depth_foreground_separation/review/ripple_readability_sheet.png`
- ripple_readability_manifest: `build/shots/s168_water_depth_foreground_separation/review/ripple_readability_manifest.json`
- ripple_readability_comparison_sheet: `build/shots/s168_water_depth_foreground_separation/review/ripple_readability_comparison_sheet.png`
- ripple_readability_comparison_manifest: `build/shots/s168_water_depth_foreground_separation/review/ripple_readability_comparison_manifest.json`
- review_dir: `build/shots/s168_water_depth_foreground_separation/review`

## Metrics

- Cache frames: `56`
- Export cache reused: `True`
- Render cache validation reused: `True`
- Converted frames: `56`
- Converted sequence reused: `True`
- Water mesh frames: `36`
- Water reconstruction reused: `True`
- Render frames reused: `False`
- GIF reused: `False`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `24468261`
- Camera motion: `True`
- Camera auto framing: `False`
- Camera frame scale: `1.0`
- Source window: `{'enabled': True, 'end_fraction': 1.0, 'end_index': 55, 'selected_frame_count': 36, 'source_frame_count': 56, 'start_fraction': 0.36363636363636365, 'start_index': 20}`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 13.2, 'max_target_distance': 29.219856262480143, 'max_target_y': 5.0, 'max_vertical_fov_degrees': 38.0, 'min_position_y': 12.7, 'min_target_distance': 26.10153252205701, 'min_target_y': 4.6, 'min_vertical_fov_degrees': 37.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 12.7, 'threshold': 12.5, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 26.10153252205701, 'threshold': 26.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 38.0, 'threshold': 38.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.0027376302083333332, 'mean': 0.0012959044656635802, 'min': 0.0004893663194444444}, 'contrast': {'max': 195.0, 'mean': 191.33333333333334, 'min': 184.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0004926215277777778, 'mean': 0.00015106577932098766, 'min': 7.595486111111111e-06}, 'mean_luminance': {'max': 93.92899305555555, 'mean': 86.9082305832851, 'min': 84.18017035590277}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1195589.0, 'mean': 1174028.3055555555, 'min': 1134239.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 184.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 86.9082305832851, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 86.9082305832851, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.0012959044656635802, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Temporal highlight summary: `{'frame_count': 36, 'pair_count': 35, 'sample_width': 320, 'highlight_threshold': 220, 'mean_delta': {'min': 2.010625, 'mean': 4.230714285714285, 'max': 7.338697916666667}, 'peak_delta': {'min': 48, 'mean': 89.02857142857142, 'max': 159}, 'highlight_change_ratio': {'min': 0.0, 'mean': 2.8273809523809526e-05, 'max': 0.00026041666666666666}, 'highlight_ratio': {'min': 0.0, 'mean': 1.6396604938271605e-05, 'max': 0.00019097222222222223}}`
- Temporal highlight gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_pair_count', 'value': 35.0, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_delta', 'value': 4.230714285714285, 'threshold': 0.25, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_delta', 'value': 7.338697916666667, 'threshold': 16.0, 'operator': '<=', 'passed': True}, {'metric': 'max_peak_delta', 'value': 159.0, 'threshold': 190.0, 'operator': '<=', 'passed': True}, {'metric': 'max_highlight_change_ratio', 'value': 0.00026041666666666666, 'threshold': 0.007, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.72`
- Water rim strength: `0.66`
- Water surface detail: `{'depth': 7, 'enabled': True, 'scale': 2.1, 'strength': 0.09}`
- Water surface glint pass: `{'alpha_scale': 0.39, 'count': 205, 'drift_per_frame': 0.12, 'emission_scale': 0.9, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.5, 'region_max': [31.4, 8.2, 21.4], 'region_min': [1.0, 3.9, 3.0], 'width': 0.04}`
- Water reflection pass: `{'alpha_scale': 0.41, 'count': 76, 'drift_per_frame': 0.048, 'emission_scale': 0.88, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.14], 'length': 5.05, 'region_max': [31.2, 8.3, 21.2], 'region_min': [1.0, 4.0, 3.4], 'width': 0.12}`
- Water volume scattering pass: `{'alpha_scale': 0.21, 'emission_scale': 0.42, 'enabled': True, 'inset': 0.72, 'layers': 18, 'region_max': [34.2, 8.8, 24.5], 'region_min': [1.0, 0.9, 2.6]}`
- Contact mist curtain pass: `{'alpha_scale': 0.108, 'emission_scale': 0.4, 'enabled': True, 'layers': 11, 'region_max': [33.2, 17.8, 24.0], 'region_min': [3.8, 1.6, 6.2], 'x_inset': 3.4, 'z_jitter': 0.62}`
- Water impact ripple pass: `{'alpha_scale': 0.42, 'arc_fraction': 0.66, 'channels': {'foam': 1.0, 'spray': 0.22}, 'emission_scale': 0.72, 'enabled': True, 'flow_center': [16.0, 0.0, 12.2], 'material_falloff': 'edge_shader', 'max_count': 112, 'radius': 0.48, 'radius_step': 0.24, 'ring_count': 3, 'segments': 22, 'vertical_offset': -1.82, 'width': 0.045}`
- Water impact ripple counts: `{'first': {'foam': 37, 'spray': 75, 'total': 112}, 'last': {'foam': 0, 'spray': 112, 'total': 112}, 'max_total': 112, 'mean_total': 112.0, 'min_total': 112}`
- Secondary channel radius scales: `{'bubble': 0.58, 'droplet': 0.78, 'foam': 1.12, 'spray': 0.86}`
- Secondary soft pass: `{'alpha_scale': 0.24, 'channels': {'foam': 2.05, 'spray': 2.45}, 'emission_scale': 0.74, 'enabled': True, 'falloff': [0.82, 0.32, 0.1, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 1.18}`
- Secondary streak pass: `{'alpha_scale': 0.18, 'channels': {'foam': 0.42, 'spray': 1.12}, 'emission_scale': 0.9, 'enabled': True, 'length_scale': 0.066, 'max_length': 1.45, 'min_speed': 0.32, 'width_scale': 0.34}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 153, 'total': 153}, 'last': {'foam': 0, 'spray': 848, 'total': 848}, 'max_total': 848, 'mean_total': 241.30555555555554, 'min_total': 153}`
- Surface contact foam pass: `{'alpha_scale': 0.44, 'channels': {'foam': 1.0}, 'emission_scale': 0.52, 'enabled': True, 'flow_aligned': True, 'flow_center': [16.0, 0.0, 12.2], 'material_falloff': 'radial_shader', 'max_count': 380, 'radius_x': 2.25, 'radius_z': 0.36, 'vertical_offset': -1.92}`
- Surface contact foam counts: `{'first': {'foam': 77, 'total': 77}, 'last': {'foam': 32, 'total': 32}, 'max_total': 77, 'mean_total': 68.58333333333333, 'min_total': 32}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 230, 'inside': 230, 'inside_ratio': 1.0, 'max_screen_y': 0.8165896788790563, 'mean_screen_y': 0.7244243695250538, 'min_screen_y': 0.6086981886545505}, 'frame_count': 36, 'last': {'active': 880, 'inside': 637, 'inside_ratio': 0.7238636363636364, 'max_screen_y': 0.9229325848159569, 'mean_screen_y': 0.374288445156392, 'min_screen_y': 0.00046800523750661904}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.7244243695250538, 'mean_inside_ratio': 0.9185529911257326, 'mean_screen_y': 0.5522116552264598, 'min_inside_ratio': 0.7238636363636364, 'min_mean_screen_y': 0.3463268778538449}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 0.9185529911257326, 'threshold': 0.65, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 0.7238636363636364, 'threshold': 0.15, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.5522116552264598, 'threshold': 0.22, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.5522116552264598, 'threshold': 0.92, 'operator': '<=', 'passed': True}]}`
- Focus review summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'bright_threshold': 220, 'nonblank_threshold': 8, 'summary': {'mean_luminance': {'min': 83.18964010487011, 'mean': 86.97196836937988, 'max': 93.51026394754051}, 'contrast': {'min': 85.0, 'mean': 163.875, 'max': 193.0}, 'bright_ratio': {'min': 0.0, 'mean': 0.00011592393861798803, 'max': 0.0004125135212765307}, 'nonblank_ratio': {'min': 1.0, 'mean': 1.0, 'max': 1.0}}}`
- Focus review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 85.0, 'threshold': 54.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 86.97196836937988, 'threshold': 62.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 86.97196836937988, 'threshold': 132.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.00011592393861798803, 'threshold': 0.0, 'operator': '>=', 'passed': True}]}`
- Secondary depth review summary: `{'enabled': True, 'frame_count': 8, 'active_frame_count': 8, 'crop': [0.02, 0.12, 0.98, 0.98], 'channels': ['bubble', 'foam', 'spray'], 'summary': {'active_particles': {'min': 256, 'mean': 375.375, 'max': 964}, 'crop_particles': {'min': 226, 'mean': 306.25, 'max': 645}, 'crop_ratio': {'min': 0.6257796257796258, 'mean': 0.887500487874607, 'max': 1.0}, 'depth_mean': {'min': 25.504586329234556, 'mean': 27.77255944664625, 'max': 28.720845842569638}, 'depth_span': {'min': 6.229595385197985, 'mean': 13.85923744136715, 'max': 25.84106637082832}, 'normalized_depth_span': {'min': 0.21796751767200953, 'mean': 0.5092914171189561, 'max': 1.0131929229217913}, 'channel_depth_delta': {'min': 0.08371958344477903, 'mean': 0.9841055997184847, 'max': 3.5132814836652173}}}`
- Secondary depth review gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_active_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_particles', 'value': 306.25, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_crop_ratio', 'value': 0.887500487874607, 'threshold': 0.35, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_depth_span', 'value': 13.85923744136715, 'threshold': 5.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_normalized_depth_span', 'value': 0.5092914171189561, 'threshold': 0.16, 'operator': '>=', 'passed': True}]}`
- Ripple readability summary: `{'enabled': True, 'frame_count': 8, 'crop': [0.02, 0.24, 0.98, 0.98], 'edge_amplify': 3.5, 'edge_threshold': 18, 'highlight_threshold': 220, 'summary': {'edge_mean': {'min': 21.935276628511712, 'mean': 28.55730614920156, 'max': 31.426213553666482}, 'edge_nonzero_ratio': {'min': 0.31252788285838257, 'mean': 0.33894249867078974, 'max': 0.36304092745262206}, 'highlight_ratio': {'min': 0.0, 'mean': 0.00011592393861798803, 'max': 0.0004125135212765307}, 'mean_luminance': {'min': 83.18964010487011, 'mean': 86.97196836937988, 'max': 93.51026394754051}}}`
- Ripple readability gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_frame_count', 'value': 8.0, 'threshold': 8.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_mean', 'value': 28.55730614920156, 'threshold': 6.0, 'operator': '>=', 'passed': True}, {'metric': 'min_edge_nonzero_ratio', 'value': 0.33894249867078974, 'threshold': 0.02, 'operator': '>=', 'passed': True}, {'metric': 'max_highlight_ratio', 'value': 0.0004125135212765307, 'threshold': 0.012, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=186 droplet=0 foam=44 bubble=26 total=256`
- Secondary channels last: `spray=848 droplet=0 foam=32 bubble=84 total=964`
- Secondary volume first: `droplet=126.5 bubble=11.7 total=138.2`
- Secondary volume last: `droplet=484 bubble=37.8 total=521.8`
- Secondary acceptance QA: `{'min_total_fraction': 0.45, 'min_foam_fraction': 0.035}`
- Secondary acceptance min: `115`
- Secondary foam acceptance min: `8`
- Secondary interface gate: `enabled=True passed=True effective_requested=256 interface_cells=3151 impact_candidates=8681 foam_ready=32 grad_max=0.5915362227977236 curvature_abs_max=2.8468203326515717`
- Review keyframes: `8`
- Review comparison sources: `2`
- Focus comparison sources: `2`
- Secondary depth comparison sources: `2`
- Ripple readability comparison sources: `2`
- Temporal diff review pairs: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 0.0ms |
| `validate_render_cache` | `0` | 3.10s |
| `reconstruct_water` | `0` | 3.14s |
| `convert_render_cache` | `0` | 3.07s |
| `render_blender` | `0` | 574.91s |
| `assemble_gif` | `0` | 2.72s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The source-slab de-emphasis scene is selected, with thinner upper lobes and stronger vertical gaps, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

Package and publish the shot artifacts, then review the public gallery to select the next visible cinematic adjustment.
