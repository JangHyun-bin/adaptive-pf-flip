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

- manifest: `build/shots/s60_contact_splash/cache/manifest.json`
- sequence: `build/shots/s60_contact_splash/converted/sequence.json`
- water_reconstruction: `build/shots/s60_contact_splash/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s60_contact_splash/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s60_contact_splash/blender/frames`
- gif: `build/shots/s60_contact_splash/shot.gif`
- contact_sheet: `build/shots/s60_contact_splash/review/contact_sheet.png`
- review_manifest: `build/shots/s60_contact_splash/review/review_manifest.json`
- review_dir: `build/shots/s60_contact_splash/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `8959676`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.75`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Secondary channels first: `spray=173 droplet=0 foam=0 bubble=19 total=192`
- Secondary channels last: `spray=173 droplet=0 foam=0 bubble=19 total=192`
- Secondary volume first: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary volume last: `droplet=95.15 bubble=8.55 total=103.7`
- Secondary acceptance min: `96`
- Secondary interface gate: `enabled=True passed=True effective_requested=192 interface_cells=3372 impact_candidates=17646 grad_max=0.5678122593680782 curvature_abs_max=1.8985836363997501`
- Review keyframes: `8`

## S59 to S60 Delta

- S59 introduced the large water-event scene, but the falling sheet and lower pool were still visually separated for much of the shot.
- S60 starts the sheet lower and faster, adds stronger outward velocity, and includes downward impact candidates in physical secondary emission.
- Physical secondary particles increase from `96` to `192`, with larger Blender secondary radius scale `3.0`.
- The final exporter step records `impact_candidates=17646`, `interface_cells=3372`, and `curvature_abs_max=1.8985836363997501`.

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 56.84s |
| `validate_render_cache` | `0` | 63.75s |
| `reconstruct_water` | `0` | 41.92s |
| `convert_render_cache` | `0` | 77.22s |
| `render_blender` | `0` | 86.67s |
| `assemble_gif` | `0` | 2.18s |

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The larger water-event scene is selected, with a wider falling sheet and lower impact pool, but it is still reconstructed from coarse sparse phase cells.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S61 should add contact foam/spray channel emphasis and more surface detail to reduce the smooth slab look.
