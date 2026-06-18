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

- manifest: `build/shots/s74_impact_framing/cache/manifest.json`
- sequence: `build/shots/s74_impact_framing/converted/sequence.json`
- water_reconstruction: `build/shots/s74_impact_framing/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s74_impact_framing/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s74_impact_framing/blender/frames`
- gif: `build/shots/s74_impact_framing/shot.gif`
- contact_sheet: `build/shots/s74_impact_framing/review/contact_sheet.png`
- review_manifest: `build/shots/s74_impact_framing/review/review_manifest.json`
- comparison_sheet: `build/shots/s74_impact_framing/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s74_impact_framing/review/comparison_manifest.json`
- review_dir: `build/shots/s74_impact_framing/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `24908423`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 11.2, 'max_target_distance': 27.654656027511894, 'max_target_y': 8.9, 'max_vertical_fov_degrees': 44.0, 'min_position_y': 10.4, 'min_target_distance': 25.613473017144706, 'min_target_y': 8.0, 'min_vertical_fov_degrees': 40.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 10.4, 'threshold': 10.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 25.613473017144706, 'threshold': 24.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 44.0, 'threshold': 44.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.02331488715277778, 'mean': 0.011287404755015433, 'min': 0.0050651041666666665}, 'contrast': {'max': 203.0, 'mean': 198.88888888888889, 'min': 189.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.004423828125, 'mean': 0.0017144097222222222, 'min': 0.00010633680555555555}, 'mean_luminance': {'max': 115.59784505208333, 'mean': 99.93340615354938, 'min': 80.01409396701389}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1318645.0, 'mean': 1207127.9444444445, 'min': 944322.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 189.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 99.93340615354938, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 99.93340615354938, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.011287404755015433, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary soft pass: `{'alpha_scale': 0.22, 'channels': {'foam': 2.0, 'spray': 2.35}, 'emission_scale': 0.88, 'enabled': True, 'falloff': [1.0, 0.32, 0.08, 0.0], 'geometry': 'billboard_disks', 'material_falloff': 'radial_shader', 'max_radius': 0.98}`
- Secondary streak pass: `{'alpha_scale': 0.21, 'channels': {'foam': 0.35, 'spray': 1.0}, 'emission_scale': 1.08, 'enabled': True, 'length_scale': 0.06, 'max_length': 1.35, 'min_speed': 0.35, 'width_scale': 0.5}`
- Secondary streak counts: `{'first': {'foam': 0, 'spray': 115, 'total': 115}, 'last': {'foam': 0, 'spray': 119, 'total': 119}, 'max_total': 119, 'mean_total': 115.44444444444444, 'min_total': 115}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`
- Review comparison sources: `2`

## S73 to S74 Delta

- S73 tuned velocity streaks but the contact sheet still depended heavily on manual camera judgement.
- S74 adds `dam_break_impact_framing`, an inherited preset that keeps the target higher and opens the early FOV to keep the active spray band visible for more frames.
- The S74 gate passed visual QA with mean bright ratio `0.011287404755015433`, up from S73's `0.006493477527006173`.
- Camera stability passed with target y range `8.0-8.9`, position y range `10.4-11.2`, and vertical FOV range `40-44` degrees.
- The next pass should make active secondary visibility/framing measurable instead of relying only on review-sheet inspection.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 56.81s |
| `validate_render_cache` | `0` | 66.90s |
| `reconstruct_water` | `0` | 41.30s |
| `convert_render_cache` | `0` | 93.72s |
| `render_blender` | `0` | 166.85s |
| `assemble_gif` | `0` | 2.85s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S75 should add numeric active-secondary framing QA so future camera/material changes cannot silently lose the visible spray band.
