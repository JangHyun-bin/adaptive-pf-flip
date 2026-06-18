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

- manifest: `build/shots/s66_volumetric_spray_foam/cache/manifest.json`
- sequence: `build/shots/s66_volumetric_spray_foam/converted/sequence.json`
- water_reconstruction: `build/shots/s66_volumetric_spray_foam/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s66_volumetric_spray_foam/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s66_volumetric_spray_foam/blender/frames`
- gif: `build/shots/s66_volumetric_spray_foam/shot.gif`
- contact_sheet: `build/shots/s66_volumetric_spray_foam/review/contact_sheet.png`
- review_manifest: `build/shots/s66_volumetric_spray_foam/review/review_manifest.json`
- comparison_sheet: `build/shots/s66_volumetric_spray_foam/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s66_volumetric_spray_foam/review/comparison_manifest.json`
- review_dir: `build/shots/s66_volumetric_spray_foam/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `22301168`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 10.0, 'max_target_distance': 25.207141845120006, 'max_target_y': 7.199999999999999, 'max_vertical_fov_degrees': 40.0, 'min_position_y': 9.4, 'min_target_distance': 23.194827009486403, 'min_target_y': 6.4, 'min_vertical_fov_degrees': 36.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 9.4, 'threshold': 9.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 23.194827009486403, 'threshold': 23.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 40.0, 'threshold': 40.0, 'operator': '<=', 'passed': True}]}`
- Visual QA summary: `{'bright_ratio': {'max': 0.012916666666666667, 'mean': 0.004813910590277778, 'min': 1.0850694444444444e-06}, 'contrast': {'max': 204.0, 'mean': 183.36111111111111, 'min': 90.0}, 'dark_ratio': {'max': 0.0, 'mean': 0.0, 'min': 0.0}, 'frame_count': 36, 'highlight_ratio': {'max': 0.001513671875, 'mean': 0.00035710841049382716, 'min': 0.0}, 'mean_luminance': {'max': 113.34173177083333, 'mean': 95.30496226369598, 'min': 75.28168728298611}, 'nonblank_ratio': {'max': 1.0, 'mean': 1.0, 'min': 1.0}, 'png_bytes': {'max': 1311598.0, 'mean': 1167691.2777777778, 'min': 853940.0}}`
- Visual QA gate: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_nonblank_ratio', 'value': 1.0, 'threshold': 0.9, 'operator': '>=', 'passed': True}, {'metric': 'min_contrast', 'value': 90.0, 'threshold': 80.0, 'operator': '>=', 'passed': True}, {'metric': 'min_mean_luminance', 'value': 95.30496226369598, 'threshold': 70.0, 'operator': '>=', 'passed': True}, {'metric': 'max_mean_luminance', 'value': 95.30496226369598, 'threshold': 120.0, 'operator': '<=', 'passed': True}, {'metric': 'min_mean_bright_ratio', 'value': 0.004813910590277778, 'threshold': 0.0005, 'operator': '>=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary soft pass: `{'alpha_scale': 0.32, 'channels': {'foam': 2.0, 'spray': 2.35}, 'emission_scale': 0.6, 'enabled': True, 'max_radius': 1.05}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`
- Review comparison sources: `2`

## S65 to S66 Delta

- S65 added screen-space visual QA metrics and gates.
- S66 adds a secondary soft pass for `spray` and `foam`: spray scale `2.35`, foam scale `2.0`, alpha scale `0.32`, max radius `1.05`.
- The visual QA gate still passed after the soft pass, with mean luminance `95.30496226369598` and mean bright ratio `0.004813910590277778`.
- The tradeoff is cost: Blender render time increased to `236.36s`, so the next step should optimize this pass.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 77.42s |
| `validate_render_cache` | `0` | 66.25s |
| `reconstruct_water` | `0` | 42.18s |
| `convert_render_cache` | `0` | 81.81s |
| `render_blender` | `0` | 236.36s |
| `assemble_gif` | `0` | 2.76s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S67 should reduce the secondary soft-pass render cost with instancing, caps, or cheaper sprite-style geometry while preserving the S66 visual QA gates.
