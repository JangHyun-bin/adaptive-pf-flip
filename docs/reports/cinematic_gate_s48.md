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
- Resolution: `640 x 360`
- Simulation grid: `16 x 20 x 14`
- Simulation steps: `24`

## Artifacts

- manifest: `build/shots/s48_secondary/cache/manifest.json`
- sequence: `build/shots/s48_secondary/converted/sequence.json`
- water_reconstruction: `build/shots/s48_secondary/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s48_secondary/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s48_secondary/blender/frames`
- gif: `build/shots/s48_secondary/shot.gif`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- GIF bytes: `1069229`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 11.99s |
| `validate_render_cache` | `0` | 11.93s |
| `reconstruct_water` | `0` | 5.67s |
| `convert_render_cache` | `0` | 9.56s |
| `render_blender` | `0` | 20.45s |
| `assemble_gif` | `0` | 671.7ms |

## Known Limitations

- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S49 should add camera motion and shot continuity checks; later physics work should replace demo secondary seeding with physical spray generation.
