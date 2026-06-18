# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_cinematic`
- Render preset: `dam_break_cinematic`
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

- manifest: `build/shots/s61_contact_foam_surface/cache/manifest.json`
- sequence: `build/shots/s61_contact_foam_surface/converted/sequence.json`
- water_reconstruction: `build/shots/s61_contact_foam_surface/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s61_contact_foam_surface/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s61_contact_foam_surface/blender/frames`
- gif: `build/shots/s61_contact_foam_surface/shot.gif`
- contact_sheet: `build/shots/s61_contact_foam_surface/review/contact_sheet.png`
- review_manifest: `build/shots/s61_contact_foam_surface/review/review_manifest.json`
- review_dir: `build/shots/s61_contact_foam_surface/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `8947476`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.75`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Water surface detail: `{'depth': 4, 'enabled': True, 'scale': 2.8, 'strength': 0.045}`
- Secondary channels first: `spray=115 droplet=0 foam=58 bubble=19 total=192`
- Secondary channels last: `spray=119 droplet=0 foam=54 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary foam acceptance min: `15`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 foam_ready=54 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`

## S60 to S61 Delta

- S60 emitted all contact droplets as spray-like particles.
- S61 marks part of the impact-driven droplet set as foam-ready by giving those secondary particles low surface velocity and older age.
- The first frame now records `foam=58` and the last frame records `foam=54`, both above the acceptance minimum `15`.
- Blender water surface detail is enabled with `strength=0.045`, `scale=2.8`, and `depth=4`.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 78.42s |
| `validate_render_cache` | `0` | 66.36s |
| `reconstruct_water` | `0` | 42.67s |
| `convert_render_cache` | `0` | 80.46s |
| `render_blender` | `0` | 93.42s |
| `assemble_gif` | `0` | 2.31s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S62 should make foam/spray visually stronger on screen, likely with larger channel-specific render sizing or a closer contact camera pass.
