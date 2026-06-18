# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_cinematic`
- Render preset: `dam_break_cinematic`
- Selected renderer: `blender`
- Simulation scene: `falling-water`
- Secondary demo particles: `0`
- Secondary physical particles: `96`
- Secondary radius scale: `2.4`
- Frames: `30`
- Resolution: `1280 x 720`
- Simulation grid: `24 x 30 x 20`
- Simulation steps: `30`

## Artifacts

- manifest: `build/shots/s58_interface_secondary_gate/cache/manifest.json`
- sequence: `build/shots/s58_interface_secondary_gate/converted/sequence.json`
- water_reconstruction: `build/shots/s58_interface_secondary_gate/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s58_interface_secondary_gate/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s58_interface_secondary_gate/blender/frames`
- gif: `build/shots/s58_interface_secondary_gate/shot.gif`
- contact_sheet: `build/shots/s58_interface_secondary_gate/review/contact_sheet.png`
- review_manifest: `build/shots/s58_interface_secondary_gate/review/review_manifest.json`
- review_dir: `build/shots/s58_interface_secondary_gate/review`

## Metrics

- Cache frames: `30`
- Converted frames: `30`
- Water mesh frames: `30`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `5120903`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.5`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Secondary channels first: `spray=86 droplet=0 foam=0 bubble=10 total=96`
- Secondary channels last: `spray=86 droplet=0 foam=0 bubble=10 total=96`
- Secondary volume first: `droplet=47.3 bubble=4.5 total=51.8`
- Secondary volume last: `droplet=47.3 bubble=4.5 total=51.8`
- Secondary acceptance min: `48`
- Secondary interface gate: `enabled=True passed=True effective_requested=96 interface_cells=784 grad_max=0.5095651925135785 curvature_abs_max=1.2725215746745409`
- Review keyframes: `8`

## S57 to S58 Delta

- S57 emitted physical secondary seeds from inside `SparseSim3DTP::step()`.
- S58 requires the physical sparse emission path to pass measured interface diagnostics before emitting.
- The gate recorded `interface_cells=784`, `grad_max=0.5095651925135785`, and `curvature_abs_max=1.2725215746745409` on the final export step.
- The visual gate was increased from 24 frames at 960x540 to 30 frames at 1280x720.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 30.29s |
| `validate_render_cache` | `0` | 34.39s |
| `reconstruct_water` | `0` | 18.10s |
| `convert_render_cache` | `0` | 42.44s |
| `render_blender` | `0` | 33.25s |
| `assemble_gif` | `0` | 1.98s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S59 should improve the falling-water scene complexity and surface detail so the shot reads as a larger water event instead of a compact falling block.
