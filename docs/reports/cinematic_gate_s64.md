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

- manifest: `build/shots/s64_contact_camera_stability/cache/manifest.json`
- sequence: `build/shots/s64_contact_camera_stability/converted/sequence.json`
- water_reconstruction: `build/shots/s64_contact_camera_stability/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s64_contact_camera_stability/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s64_contact_camera_stability/blender/frames`
- gif: `build/shots/s64_contact_camera_stability/shot.gif`
- contact_sheet: `build/shots/s64_contact_camera_stability/review/contact_sheet.png`
- review_manifest: `build/shots/s64_contact_camera_stability/review/review_manifest.json`
- comparison_sheet: `build/shots/s64_contact_camera_stability/review/comparison_sheet.png`
- comparison_manifest: `build/shots/s64_contact_camera_stability/review/comparison_manifest.json`
- review_dir: `build/shots/s64_contact_camera_stability/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `22877715`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.0`
- Camera path metrics: `{'frame_count': 36, 'max_position_y': 10.0, 'max_target_distance': 25.207141845120006, 'max_target_y': 7.199999999999999, 'max_vertical_fov_degrees': 40.0, 'min_position_y': 9.4, 'min_target_distance': 23.194827009486403, 'min_target_y': 6.4, 'min_vertical_fov_degrees': 36.0}`
- Camera stability: `{'enabled': True, 'passed': True, 'checks': [{'metric': 'min_position_y', 'value': 9.4, 'threshold': 9.0, 'operator': '>=', 'passed': True}, {'metric': 'min_target_distance', 'value': 23.194827009486403, 'threshold': 23.0, 'operator': '>=', 'passed': True}, {'metric': 'max_vertical_fov_degrees', 'value': 40.0, 'threshold': 40.0, 'operator': '<=', 'passed': True}]}`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Secondary channel radius scales: `{'bubble': 1.15, 'droplet': 1.0, 'foam': 1.85, 'spray': 1.35}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`
- Review comparison sources: `2`

## S63 to S64 Delta

- S63 proved the close-up contact view, but late frames could get too close to the water body.
- S64 moves the close-up camera path farther back and records camera path metrics from the Blender bridge.
- The new stability gate passed with `min_position_y=9.4`, `min_target_distance=23.194827009486403`, and `max_vertical_fov_degrees=40.0`.
- S64 also creates `comparison_sheet.png`, combining the S62 wide gate and S64 close-up gate for side-by-side review.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 55.31s |
| `validate_render_cache` | `0` | 65.30s |
| `reconstruct_water` | `0` | 41.95s |
| `convert_render_cache` | `0` | 78.62s |
| `render_blender` | `0` | 89.65s |
| `assemble_gif` | `0` | 2.71s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S65 should add screen-space visual QA metrics so empty, low-contrast, or weakly readable cinematic gates can fail before manual review.
