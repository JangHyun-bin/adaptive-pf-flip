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

- manifest: `build/shots/s53_surface_tetra/cache/manifest.json`
- sequence: `build/shots/s53_surface_tetra/converted/sequence.json`
- water_reconstruction: `build/shots/s53_surface_tetra/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s53_surface_tetra/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s53_surface_tetra/blender/frames`
- gif: `build/shots/s53_surface_tetra/shot.gif`
- contact_sheet: `build/shots/s53_surface_tetra/review/contact_sheet.png`
- review_manifest: `build/shots/s53_surface_tetra/review/review_manifest.json`
- review_dir: `build/shots/s53_surface_tetra/review`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `1299944`
- Camera motion: `True`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Review keyframes: `6`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 7.65s |
| `validate_render_cache` | `0` | 7.63s |
| `reconstruct_water` | `0` | 4.85s |
| `convert_render_cache` | `0` | 9.36s |
| `render_blender` | `0` | 19.50s |
| `assemble_gif` | `0` | 715.4ms |

## Surface Comparison

| Gate | Surface mode | Frames | Resolution | First mesh vertices | First mesh faces | Visual result |
| --- | --- | ---: | --- | ---: | ---: | --- |
| S51 | voxel | 24 | 640 x 360 | n/a | n/a | visible box-like water silhouette |
| S53 | tetra | 24 | 640 x 360 | 1394 | 2784 | visibly rounded water silhouette |

S53 keeps the same falling-water/camera/material/review path as S51, but switches the reconstruction preset to implicit tetra surfaces. The contact sheet shows a smoother outline and reduced voxel stair stepping. The remaining limit is not the material path; it is the low sparse phase-cell resolution feeding the surface extractor.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S54 should raise visual detail through higher-resolution/adaptive surface data and begin replacing demo secondary seeding with physical spray generation.
