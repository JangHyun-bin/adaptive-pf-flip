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

- manifest: `build/shots/s56_physical_secondary/cache/manifest.json`
- sequence: `build/shots/s56_physical_secondary/converted/sequence.json`
- water_reconstruction: `build/shots/s56_physical_secondary/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s56_physical_secondary/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s56_physical_secondary/blender/frames`
- gif: `build/shots/s56_physical_secondary/shot.gif`
- contact_sheet: `build/shots/s56_physical_secondary/review/contact_sheet.png`
- review_manifest: `build/shots/s56_physical_secondary/review/review_manifest.json`
- review_dir: `build/shots/s56_physical_secondary/review`

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
- Review keyframes: `6`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 18.70s |
| `validate_render_cache` | `0` | 14.70s |
| `reconstruct_water` | `0` | 8.37s |
| `convert_render_cache` | `0` | 18.62s |
| `render_blender` | `0` | 22.80s |
| `assemble_gif` | `0` | 1.08s |

## Secondary Source Comparison

| Gate | Secondary source | Demo count | Physical count | First-frame channels | Visual role |
| --- | --- | ---: | ---: | --- | --- |
| S55 | demo preset | 96 | 0 | synthetic secondary placement | framing/surface acceptance |
| S56 | liquid-candidate physical seed | 0 | 96 | spray=86 bubble=10 total=96 | first render-facing physical spray gate |

S56 removes the demo secondary ring from `dam_break_cinematic` and emits secondary particles from actual liquid particle candidates selected near the upper/high-motion region of the falling-water body. This is still a render-facing seed, not a fully coupled spray solver, but the cache now records the secondary channels as physically conditioned output rather than arbitrary presentation particles.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Physically conditioned secondary spray seeds are now emitted from liquid particle candidates, but this is not yet a fully coupled spray/foam solver.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S57 should promote secondary spray emission from a render-facing seed into a sim-side lifecycle gate with volume accounting and acceptance thresholds.
