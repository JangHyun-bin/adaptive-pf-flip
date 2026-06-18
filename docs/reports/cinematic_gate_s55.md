# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_cinematic`
- Render preset: `dam_break_cinematic`
- Selected renderer: `blender`
- Simulation scene: `falling-water`
- Secondary demo particles: `96`
- Secondary radius scale: `2.4`
- Frames: `24`
- Resolution: `960 x 540`
- Simulation grid: `20 x 24 x 17`
- Simulation steps: `24`

## Artifacts

- manifest: `build/shots/s55_grid_aware_camera/cache/manifest.json`
- sequence: `build/shots/s55_grid_aware_camera/converted/sequence.json`
- water_reconstruction: `build/shots/s55_grid_aware_camera/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s55_grid_aware_camera/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s55_grid_aware_camera/blender/frames`
- gif: `build/shots/s55_grid_aware_camera/shot.gif`
- contact_sheet: `build/shots/s55_grid_aware_camera/review/contact_sheet.png`
- review_manifest: `build/shots/s55_grid_aware_camera/review/review_manifest.json`
- review_dir: `build/shots/s55_grid_aware_camera/review`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `2665330`
- Camera motion: `True`
- Camera auto framing: `True`
- Camera frame scale: `1.25`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Review keyframes: `6`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 13.99s |
| `validate_render_cache` | `0` | 14.88s |
| `reconstruct_water` | `0` | 8.44s |
| `convert_render_cache` | `0` | 19.02s |
| `render_blender` | `0` | 24.46s |
| `assemble_gif` | `0` | 1.09s |

## Framing Comparison

| Gate | Grid | Camera framing | Scale | First mesh vertices | First mesh faces | Visual result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| S54 | 20 x 24 x 17 | fixed preset | 1.0 | 1798 | 3592 | high-detail close-up with tight top framing |
| S55 | 20 x 24 x 17 | grid-aware auto frame | 1.25 | 1798 | 3592 | high-detail full-body framing with crop removed |

S55 keeps the S54 surface-detail input and tetra reconstruction, but scales the camera target and distance from the `16 x 20 x 14` reference grid to the current `20 x 24 x 17` override. The review contact sheet confirms that the high-detail gate no longer crops the top of the water body.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S56 should begin replacing demo secondary seeding with physical spray generation and keep the review-pack gate as the visual acceptance loop.
