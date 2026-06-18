# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_contact_closeup`
- Render preset: `dam_break_contact_closeup`
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

- manifest: `build/shots/s72_secondary_velocity_streaks/cache/manifest.json`
- sequence: `build/shots/s72_secondary_velocity_streaks/converted/sequence.json`
- water_reconstruction: `build/shots/s72_secondary_velocity_streaks/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s72_secondary_velocity_streaks/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s72_secondary_velocity_streaks/blender/frames`
- gif: `build/shots/s72_secondary_velocity_streaks/shot.gif`
- contact_sheet: `build/shots/s72_secondary_velocity_streaks/review/contact_sheet.png`
- review_manifest: `build/shots/s72_secondary_velocity_streaks/review/review_manifest.json`
- comparison_sheet: `build/shots/s72_secondary_velocity_streaks/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s72_secondary_velocity_streaks/review/comparison_manifest.json`
- review_dir: `build/shots/s72_secondary_velocity_streaks/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `22878695`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 10.0, 'max_target_distance': 25.207141845120006, 'max_target_y': 7.199999999999999, 'max_vertical_fov_degrees': 40.0, 'min_position_y': 9.4, 'min_target_distance': 23.194827009486403, 'min_target_y': 6.4, 'min_vertical_fov_degrees': 36.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 9.4, 'threshold': 9.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 23.194827009486403, 'threshold': 23.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 40.0, 'threshold': 40.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.016383463541666667, 'mean': 0.006468581211419753, 'min': 1.0850694444444444e-06}, 'contrast': {'max': 203.0, 'mean': 185.02777777777777, 'min': 90.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.0018370225694444445, 'mean': 0.0006388949170524692, 'min': 0.0}, 'mean_luminance': {'max': 112.95030164930556, 'mean': 95.20947145061729, 'min': 75.36769965277777}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1311347.0, 'mean': 1171853.4444444445, 'min': 856507.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 90.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 95.20947145061729, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 95.20947145061729, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.006468581211419753, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary soft pass: `{'alpha_scale': 0.22, 'channels': {'foam': 2.0, 'spray': 2.35}, 'emission_scale': 0.88, 'enabled': True, 'falloff': [1.0, 0.32, 0.08, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.98}`
- Secondary streak pass: `{'alpha_scale': 0.18, 'channels': {'foam': 0.35, 'spray': 1.0}, 'emission_scale': 0.95, 'enabled': True, 'length_scale': 0.045, 'max_length': 1.15, 'min_speed': 0.35, 'width_scale': 0.42}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`
- Review comparison sources: `2`

## S71 to S72 Delta

- S71 added UV-driven radial alpha falloff for mist billboards, but the contact particles still read mostly as circular sprites.
- S72 adds a separate velocity-aligned streak pass for spray and foam channels using the exported secondary particle velocity columns.
- The S72 gate passed visual QA with mean bright ratio `0.006468581211419753` and Blender render time `116.43s`.
- The review sheet shows visible thin streaks in the contact region, especially around frames 20-30. The next pass should tune streak length, width, alpha, and emission for stronger readability without noisy scratches.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 59.16s |
| `validate_render_cache` | `0` | 65.05s |
| `reconstruct_water` | `0` | 41.35s |
| `convert_render_cache` | `0` | 78.36s |
| `render_blender` | `0` | 116.43s |
| `assemble_gif` | `0` | 2.64s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S73 should tune secondary streak length, width, alpha, and emission against the S72 review sheet so motion streaks stay readable without turning the contact region noisy.
