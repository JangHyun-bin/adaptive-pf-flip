# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_impact_framing`
- Render preset: `dam_break_impact_framing`
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

- manifest: `build/shots/s76_surface_foam_contact/cache/manifest.json`
- sequence: `build/shots/s76_surface_foam_contact/converted/sequence.json`
- water_reconstruction: `build/shots/s76_surface_foam_contact/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s76_surface_foam_contact/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s76_surface_foam_contact/blender/frames`
- gif: `build/shots/s76_surface_foam_contact/shot.gif`
- contact_sheet: `build/shots/s76_surface_foam_contact/review/contact_sheet.png`
- review_manifest: `build/shots/s76_surface_foam_contact/review/review_manifest.json`
- comparison_sheet: `build/shots/s76_surface_foam_contact/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s76_surface_foam_contact/review/comparison_manifest.json`
- review_dir: `build/shots/s76_surface_foam_contact/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `24928394`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 11.2, 'max_target_distance': 27.654656027511894, 'max_target_y': 8.9, 'max_vertical_fov_degrees': 44.0, 'min_position_y': 10.4, 'min_target_distance': 25.613473017144706, 'min_target_y': 8.0, 'min_vertical_fov_degrees': 40.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 10.4, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 25.613473017144706, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 44.0, 'threshold': 44.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.024674479166666666, 'mean': 0.01153175636574074, 'min': 0.0050651041666666665}, 'contrast': {'max': 203.0, 'mean': 198.91666666666666, 'min': 189.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.004410807291666667, 'mean': 0.0017083815586419753, 'min': 0.00010633680555555555}, 'mean_luminance': {'max': 115.64733181423611, 'mean': 100.0535397075135, 'min': 80.01472547743056}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1322858.0, 'mean': 1212886.5833333333, 'min': 947010.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 189.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 100.0535397075135, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 100.0535397075135, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.01153175636574074, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary soft pass: `{'alpha_scale': 0.22, 'channels': {'foam': 2.0, 'spray': 2.35}, 'emission_scale': 0.88, 'enabled': True, 'falloff': [1.0, 0.32, 0.08, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.98}`
- Secondary streak pass: `{'alpha_scale': 0.21, 'channels': {'foam': 0.35, 'spray': 1.0}, 'emission_scale': 1.08, 'enabled': True, 'length_scale': 0.06, 'max_length': 1.35, 'min_speed': 0.35, 'width_scale': 0.5}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 119, 'total': 119}, 'max_total': 119, 'mean_total': 115.44444444444444, 'min_total': 115}`
- Surface contact foam pass: `{'alpha_scale': 0.52, 'channels': {'foam': 1.0}, 'emission_scale': 0.7, 'enabled': True, 'max_count': 256, 'radius_x': 1.15, 'radius_z': 0.36, 'vertical_offset': -1.85}`
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

## S75 to S76 Delta

- S75 added numeric active-secondary framing QA, proving the spray/foam band stays in frame.
- S76 adds `surface_contact_foam_pass`, which renders flattened foam patches from the foam channel below the secondary band.
- The final S76 gate renders `54-58` surface contact foam patches per frame with radius `1.15 x 0.36`, vertical offset `-1.85`, alpha scale `0.52`, and emission scale `0.7`.
- Visual QA passed with mean bright ratio `0.01153175636574074`, and the contact sheet shows visible horizontal foam marks near the water surface.
- The next visual step should make these marks look advected by the contact flow rather than static patches.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 55.21s |
| `validate_render_cache` | `0` | 65.21s |
| `reconstruct_water` | `0` | 41.83s |
| `convert_render_cache` | `0` | 78.57s |
| `render_blender` | `0` | 167.35s |
| `assemble_gif` | `0` | 2.88s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S77 should make contact foam read as moving with the impact flow rather than only static horizontal patches.
