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

- manifest: `build/shots/s62_secondary_size_pass/cache/manifest.json`
- sequence: `build/shots/s62_secondary_size_pass/converted/sequence.json`
- water_reconstruction: `build/shots/s62_secondary_size_pass/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s62_secondary_size_pass/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s62_secondary_size_pass/blender/frames`
- gif: `build/shots/s62_secondary_size_pass/shot.gif`
- contact_sheet: `build/shots/s62_secondary_size_pass/review/contact_sheet.png`
- review_manifest: `build/shots/s62_secondary_size_pass/review/review_manifest.json`
- review_dir: `build/shots/s62_secondary_size_pass/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `9028890`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.75`
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

## S61 to S62 Delta

- S61 introduced foam channel counts and water surface detail, but foam/spray particles were still small on the 1280x720 wide shot.
- S62 adds channel-specific Blender secondary sizing: `spray=1.35`, `foam=1.85`, `bubble=1.15`.
- S62 also adds weak spray/foam emission material controls so contact particles read brighter against water.
- The visual gate preserves the same physical secondary counts while making the foam/spray points more legible in the contact area.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 80.65s |
| `validate_render_cache` | `0` | 75.18s |
| `reconstruct_water` | `0` | 45.62s |
| `convert_render_cache` | `0` | 85.35s |
| `render_blender` | `0` | 98.55s |
| `assemble_gif` | `0` | 2.36s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S63 should add a closer contact-camera preset or crop gate so the foam/spray and surface breakup are easier to inspect.
