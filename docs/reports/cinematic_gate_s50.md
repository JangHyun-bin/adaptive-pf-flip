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

- manifest: `build/shots/s50_water_material/cache/manifest.json`
- sequence: `build/shots/s50_water_material/converted/sequence.json`
- water_reconstruction: `build/shots/s50_water_material/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s50_water_material/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s50_water_material/blender/frames`
- gif: `build/shots/s50_water_material/shot.gif`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- GIF bytes: `1387889`
- Camera motion: `True`
- Water depth strength: `0.42`
- Water rim strength: `0.42`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 7.08s |
| `validate_render_cache` | `0` | 7.73s |
| `reconstruct_water` | `0` | 3.84s |
| `convert_render_cache` | `0` | 9.63s |
| `render_blender` | `0` | 21.98s |
| `assemble_gif` | `0` | 683.5ms |

## Known Limitations

- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S51 should package review artifacts with a contact sheet, GIF, and compact report bundle; later physics work should replace demo secondary seeding with physical spray generation.
