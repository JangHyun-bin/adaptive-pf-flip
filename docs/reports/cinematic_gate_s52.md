# Cinematic Shot Report

## Summary

- Status: `ok`
- Shot preset: `dam_break_cinematic`
- Render preset: `dam_break_cinematic`
- Selected renderer: `blender`
- Simulation scene: `falling-water`
- Secondary demo particles: `96`
- Secondary radius scale: `2.4`
- Frames: `36`
- Resolution: `960 x 540`
- Simulation grid: `16 x 20 x 14`
- Simulation steps: `36`

## Artifacts

- manifest: `build/shots/s52_visual_gate_v2/cache/manifest.json`
- sequence: `build/shots/s52_visual_gate_v2/converted/sequence.json`
- water_reconstruction: `build/shots/s52_visual_gate_v2/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s52_visual_gate_v2/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s52_visual_gate_v2/blender/frames`
- gif: `build/shots/s52_visual_gate_v2/shot.gif`
- contact_sheet: `build/shots/s52_visual_gate_v2/review/contact_sheet.png`
- review_manifest: `build/shots/s52_visual_gate_v2/review/review_manifest.json`
- review_dir: `build/shots/s52_visual_gate_v2/review`

## Metrics

- Cache frames: `36`
- Converted frames: `36`
- Water mesh frames: `36`
- GIF bytes: `4336364`
- Camera motion: `True`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Review keyframes: `8`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 10.60s |
| `validate_render_cache` | `0` | 11.52s |
| `reconstruct_water` | `0` | 5.71s |
| `convert_render_cache` | `0` | 14.27s |
| `render_blender` | `0` | 29.75s |
| `assemble_gif` | `0` | 1.43s |

## Visual Gate Comparison

| Gate | Scene | Frames | Resolution | GIF bytes | Render elapsed | Review pack |
| --- | --- | ---: | --- | ---: | ---: | --- |
| S45 | bubble | 48 | 1280 x 720 | 1436403 | 11.47s | no |
| S51 | falling-water | 24 | 640 x 360 | 1387889 | 20.83s | 6 keyframes |
| S52 | falling-water | 36 | 960 x 540 | 4336364 | 29.75s | 8 keyframes |

S52 is larger than the S51 review-pack smoke run and uses the dynamic falling-water scene, camera motion, water depth/rim material, and review-pack path together. The contact sheet also confirms the remaining visual bottleneck: water silhouette quality is still dominated by coarse voxel-derived surface reconstruction.

## Known Limitations

- The current large gate still uses coarse voxel-derived OBJ water meshes, so silhouettes remain blocky.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S53 should replace the coarse voxel-derived water surface with a smoother reconstruction path before the next photoreal material pass.
