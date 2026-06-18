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
- Frames: `24`
- Resolution: `960 x 540`
- Simulation grid: `20 x 24 x 17`
- Simulation steps: `24`

## Artifacts

- manifest: `build/shots/s57_secondary_lifecycle_gate/cache/manifest.json`
- sequence: `build/shots/s57_secondary_lifecycle_gate/converted/sequence.json`
- water_reconstruction: `build/shots/s57_secondary_lifecycle_gate/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s57_secondary_lifecycle_gate/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s57_secondary_lifecycle_gate/blender/frames`
- gif: `build/shots/s57_secondary_lifecycle_gate/shot.gif`
- contact_sheet: `build/shots/s57_secondary_lifecycle_gate/review/contact_sheet.png`
- review_manifest: `build/shots/s57_secondary_lifecycle_gate/review/review_manifest.json`
- review_dir: `build/shots/s57_secondary_lifecycle_gate/review`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `2490344`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.25`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Secondary channels first: `spray=86 droplet=0 foam=0 bubble=10 total=96`
- Secondary channels last: `spray=86 droplet=0 foam=0 bubble=10 total=96`
- Secondary volume first: `droplet=47.3 bubble=4.5 total=51.8`
- Secondary volume last: `droplet=47.3 bubble=4.5 total=51.8`
- Secondary acceptance min: `48`
- Review keyframes: `6`

## S56 to S57 Delta

- S56 used render-facing physical secondary seeding during cache export.
- S57 promotes sparse cinematic physical secondary seeding into `SparseSim3DTP::step()`, so emission uses the sim secondary containers, lifecycle accounting, and water-volume cache fields.
- This gate keeps demo secondary particles disabled and records `spray=86 bubble=10 total=96` on first and last frames.
- The render cache records stable secondary volume across the shot: first `droplet=47.3 bubble=4.5 total=51.8`, last `droplet=47.3 bubble=4.5 total=51.8`.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 13.12s |
| `validate_render_cache` | `0` | 14.55s |
| `reconstruct_water` | `0` | 8.13s |
| `convert_render_cache` | `0` | 18.10s |
| `render_blender` | `0` | 21.81s |
| `assemble_gif` | `0` | 1.08s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S58 should couple physical spray emission thresholds to interface/curvature diagnostics and add a larger visual acceptance gate.
