# S45 Large-Scale Cinematic Gate

## Summary

- Status: `ok`
- Shot preset: `bubble_cinematic`
- Render preset: `bubble_cinematic`
- Selected renderer: `blender`
- Frames: `48`
- Resolution: `1280 x 720`
- Simulation grid: `12 x 18 x 12`
- Simulation steps: `24`

## Artifacts

- manifest: `build/shots/s45_bubble/cache/manifest.json`
- sequence: `build/shots/s45_bubble/converted/sequence.json`
- water_reconstruction: `build/shots/s45_bubble/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s45_bubble/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s45_bubble/blender/frames`
- gif: `build/shots/s45_bubble/shot.gif`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `48`
- GIF bytes: `1436403`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 2.15s |
| `validate_render_cache` | `0` | 2.28s |
| `reconstruct_water` | `0` | 1.40s |
| `convert_render_cache` | `0` | 2.80s |
| `check_blender` | `0` | 487.1ms |
| `render_blender` | `0` | 11.47s |
| `assemble_gif` | `0` | 2.48s |

## Known Limitations

- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky.
- The current exporter scene is a bubble-tank style sparse two-phase setup, not a full dam-break or waterfall shot.
- Secondary spray/foam channels are wired through the cache and renderer path, but this gate may contain little or no visible secondary particle content.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S46 should target visual surface quality: smoother water reconstruction, better mesh normals, and a dam-break or falling-water cache preset that produces more cinematic motion.
