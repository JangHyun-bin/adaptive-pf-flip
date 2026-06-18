# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_cinematic`
- Render preset: `dam_break_cinematic`
- Selected renderer: `blender`
- Simulation scene: `large-water-event`
- Secondary demo particles: `0`
- Secondary physical particles: `96`
- Secondary radius scale: `2.4`
- Frames: `36`
- Resolution: `1280 x 720`
- Simulation grid: `28 x 34 x 22`
- Simulation steps: `36`

## Artifacts

- manifest: `build/shots/s59_large_water_event/cache/manifest.json`
- sequence: `build/shots/s59_large_water_event/converted/sequence.json`
- water_reconstruction: `build/shots/s59_large_water_event/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s59_large_water_event/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s59_large_water_event/blender/frames`
- gif: `build/shots/s59_large_water_event/shot.gif`
- contact_sheet: `build/shots/s59_large_water_event/review/contact_sheet.png`
- review_manifest: `build/shots/s59_large_water_event/review/review_manifest.json`
- review_dir: `build/shots/s59_large_water_event/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `9127059`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.75`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Secondary channels first: `spray=86 droplet=0 foam=0 bubble=10 total=96`
- Secondary channels last: `spray=86 droplet=0 foam=0 bubble=10 total=96`
- Secondary volume first: `droplet=47.3 bubble=4.5 total=51.8`
- Secondary volume last: `droplet=47.3 bubble=4.5 total=51.8`
- Secondary acceptance min: `48`
- Secondary interface gate: `enabled=True passed=True effective_requested=96 interface_cells=3312 grad_max=0.5388178763812941 curvature_abs_max=1.5890709908247311`
- Review keyframes: `8`

## S58 to S59 Delta

- S58 used a compact falling-water block with interface-gated secondary emission.
- S59 switches `dam_break_cinematic` to `large-water-event`, a wider falling sheet above a shallow impact pool.
- Primary liquid particles increase to `24720` in the S59 gate, and interface cells increase to `3312`.
- Camera auto framing scales to `1.75` for the 28x34x22 grid, keeping the larger source and pool visible in the contact sheet.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 54.90s |
| `validate_render_cache` | `0` | 66.07s |
| `reconstruct_water` | `0` | 44.69s |
| `convert_render_cache` | `0` | 80.87s |
| `render_blender` | `0` | 48.08s |
| `assemble_gif` | `0` | 2.37s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S60 should increase contact-driven splash breakup and spray visibility for the large water-event scene.
