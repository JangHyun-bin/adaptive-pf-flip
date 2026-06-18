# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_cinematic`
- Render preset: `dam_break_cinematic`
- Selected renderer: `blender`
- Simulation scene: `falling-water`
- Frames: `24`
- Resolution: `640 x 360`
- Simulation grid: `16 x 20 x 14`
- Simulation steps: `24`

## Artifacts

- manifest: `build/shots/s47_dam_break/cache/manifest.json`
- sequence: `build/shots/s47_dam_break/converted/sequence.json`
- water_reconstruction: `build/shots/s47_dam_break/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s47_dam_break/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s47_dam_break/blender/frames`
- gif: `build/shots/s47_dam_break/shot.gif`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- GIF bytes: `1102689`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 10.11s |
| `validate_render_cache` | `0` | 7.92s |
| `reconstruct_water` | `0` | 4.00s |
| `convert_render_cache` | `0` | 9.79s |
| `render_blender` | `0` | 8.48s |
| `assemble_gif` | `0` | 633.6ms |

## Known Limitations

- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Secondary spray/foam channels are wired through the cache and renderer path, but this gate may contain little or no visible secondary particle content.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S48 should make secondary droplet, spray, foam, and bubble channels visibly useful in cinematic frames.
