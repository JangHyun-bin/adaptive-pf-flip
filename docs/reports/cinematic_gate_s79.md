# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_water_glint_flow`
- Render preset: `dam_break_water_glint_flow`
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

- manifest: `build/shots/s79_water_surface_glint_flow/cache/manifest.json`
- sequence: `build/shots/s79_water_surface_glint_flow/converted/sequence.json`
- water_reconstruction: `build/shots/s79_water_surface_glint_flow/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s79_water_surface_glint_flow/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s79_water_surface_glint_flow/blender/frames`
- gif: `build/shots/s79_water_surface_glint_flow/shot.gif`
- contact_sheet: `build/shots/s79_water_surface_glint_flow/review/contact_sheet.png`
- review_manifest: `build/shots/s79_water_surface_glint_flow/review/review_manifest.json`
- comparison_sheet: `build/shots/s79_water_surface_glint_flow/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s79_water_surface_glint_flow/review/comparison_manifest.json`
- review_dir: `build/shots/s79_water_surface_glint_flow/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `24979868`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 11.2, 'max_target_distance': 27.654656027511894, 'max_target_y': 8.9, 'max_vertical_fov_degrees': 44.0, 'min_position_y': 10.4, 'min_target_distance': 25.613473017144706, 'min_target_y': 8.0, 'min_vertical_fov_degrees': 40.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 10.4, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 25.613473017144706, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 44.0, 'threshold': 44.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.023321397569444444, 'mean': 0.01128297405478395, 'min': 0.005064019097222222}, 'contrast': {'max': 203.0, 'mean': 198.88888888888889, 'min': 189.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.004419487847222223, 'mean': 0.0017126012731481482, 'min': 0.00010633680555555555}, 'mean_luminance': {'max': 115.62569118923611, 'mean': 99.99297453703703, 'min': 80.05934027777778}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1322859.0, 'mean': 1213001.7222222222, 'min': 951286.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 189.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 99.99297453703703, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 99.99297453703703, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.01128297405478395, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Water surface glint pass: `{'alpha_scale': 0.22, 'count': 44, 'drift_per_frame': 0.08, 'emission_scale': 0.48, 'enabled': True, 'flow_dir': [1.0, 0.0, 0.22], 'length': 1.55, 'region_max': [27.4, 8.1, 19.2], 'region_min': [0.8, 4.9, 3.0], 'width': 0.035}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary soft pass: `{'alpha_scale': 0.22, 'channels': {'foam': 2.0, 'spray': 2.35}, 'emission_scale': 0.88, 'enabled': True, 'falloff': [1.0, 0.32, 0.08, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.98}`
- Secondary streak pass: `{'alpha_scale': 0.21, 'channels': {'foam': 0.35, 'spray': 1.0}, 'emission_scale': 1.08, 'enabled': True, 'length_scale': 0.06, 'max_length': 1.35, 'min_speed': 0.35, 'width_scale': 0.5}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 119, 'total': 119}, 'max_total': 119, 'mean_total': 115.44444444444444, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.42, 'channels': {'foam': 1.0}, 'emission_scale': 0.52, 'enabled': True, 'flow_aligned': True, 'flow_center': [14.0, 0.0, 11.0], 'material_falloff': 'radial_shader', 'max_count': 256, 'radius_x': 1.42, 'radius_z': 0.24, 'vertical_offset': -1.85}`
- Surface contact foam counts: `{'first': {'foam': 58, 'total': 58}, 'last': {'foam': 54, 'total': 54}, 'max_total': 58, 'mean_total': 57.55555555555556, 'min_total': 54}`
- Secondary framing summary: `{'channels': {'foam': True, 'spray': True}, 'enabled': True, 'first': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.7564880513131522, 'mean_screen_y': 0.7004098812190457, 'min_screen_y': 0.6728383589734349}, 'frame_count': 36, 'last': {'active': 173, 'inside': 173, 'inside_ratio': 1.0, 'max_screen_y': 0.6163238177747465, 'mean_screen_y': 0.5470525652469158, 'min_screen_y': 0.35564716062541946}, 'max_inside_ratio': 1.0, 'max_mean_screen_y': 0.7004098812190457, 'mean_inside_ratio': 1.0, 'mean_screen_y': 0.5823346146344457, 'min_inside_ratio': 1.0, 'min_mean_screen_y': 0.48604136611683574}`
- Secondary framing gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_mean_inside_ratio', 'value': 1.0, 'threshold': 0.98, 'operator': '>=', 'passed': True}, {'metric': 'min_frame_inside_ratio', 'value': 1.0, 'threshold': 0.95, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_screen_y', 'value': 0.5823346146344457, 'threshold': 0.45, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_screen_y', 'value': 0.5823346146344457, 'threshold': 0.75, 'operator': '<=', 'passed': True}]}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`
- Review comparison sources: `2`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 95.77s |
| `validate_render_cache` | `0` | 76.62s |
| `reconstruct_water` | `0` | 43.94s |
| `convert_render_cache` | `0` | 82.10s |
| `render_blender` | `0` | 187.93s |
| `assemble_gif` | `0` | 3.23s |

## S78 to S79 Delta

- Adds the preset-driven `water_surface_glint_pass` to `dam_break_water_glint_flow`.
- Keeps S78 contact foam fade active while adding `44` subtle directional glint strokes per frame.
- Preserves Visual QA, camera stability, and active-secondary framing gates.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S80 should add water reflection-continuity cues so the main water body reads less like a flat slab under the moving camera.
