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

- manifest: `build/shots/s49_camera_motion/cache/manifest.json`
- sequence: `build/shots/s49_camera_motion/converted/sequence.json`
- water_reconstruction: `build/shots/s49_camera_motion/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s49_camera_motion/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s49_camera_motion/blender/frames`
- gif: `build/shots/s49_camera_motion/shot.gif`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- GIF bytes: `1387672`
- Camera motion: `True`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 7.03s |
| `validate_render_cache` | `0` | 7.45s |
| `reconstruct_water` | `0` | 3.77s |
| `convert_render_cache` | `0` | 9.40s |
| `render_blender` | `0` | 19.59s |
| `assemble_gif` | `0` | 714.7ms |

## Known Limitations

- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S50 should improve water material response with depth tint, rim highlights, and preset sweeps; later physics work should replace demo secondary seeding with physical spray generation.
