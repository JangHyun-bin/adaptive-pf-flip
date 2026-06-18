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

- manifest: `build/shots/s54_high_detail_surface/cache/manifest.json`
- sequence: `build/shots/s54_high_detail_surface/converted/sequence.json`
- water_reconstruction: `build/shots/s54_high_detail_surface/water_mesh/water_reconstruction.json`
- render_summary: `build/shots/s54_high_detail_surface/blender/bridge_summary.json`
- render_frame_dir: `build/shots/s54_high_detail_surface/blender/frames`
- gif: `build/shots/s54_high_detail_surface/shot.gif`
- contact_sheet: `build/shots/s54_high_detail_surface/review/contact_sheet.png`
- review_manifest: `build/shots/s54_high_detail_surface/review/review_manifest.json`
- review_dir: `build/shots/s54_high_detail_surface/review`

## Metrics

- Cache frames: `24`
- Converted frames: `24`
- Water mesh frames: `24`
- Surface mode: `tetra`
- Implicit blur iterations: `1`
- GIF bytes: `3412311`
- Camera motion: `True`
- Water depth strength: `0.42`
- Water rim strength: `0.42`
- Review keyframes: `6`

## Stage Timings

| Stage | Exit | Elapsed |
| --- | ---: | ---: |
| `export_render_cache` | `0` | 13.51s |
| `validate_render_cache` | `0` | 14.92s |
| `reconstruct_water` | `0` | 8.45s |
| `convert_render_cache` | `0` | 19.30s |
| `render_blender` | `0` | 25.02s |
| `assemble_gif` | `0` | 1.20s |

## High-Detail Surface Comparison

| Gate | Grid | Frames | Resolution | First mesh vertices | First mesh faces | Render elapsed | Visual role |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| S53 | 16 x 20 x 14 | 24 | 640 x 360 | 1394 | 2784 | 19.50s | framed full-body tetra surface smoke |
| S54 | 20 x 24 x 17 | 24 | 960 x 540 | 1798 | 3592 | 25.02s | higher-detail close-up surface gate |

S54 increases the surface input and output fidelity while keeping the same falling-water scene, tetra reconstruction, material response, camera motion, and review-pack path. The resulting contact sheet is useful as a closer surface-detail gate, but it also shows that fixed camera presets do not scale cleanly with larger grid overrides.

## Known Limitations

- The current gate uses implicit tetra water surfaces, but detail is still limited by coarse sparse phase-cell resolution.
- The dynamic water-motion scene is now selected, but it is still reconstructed from coarse sparse phase cells rather than a production liquid surface.
- The high-detail grid override is framed as a close-up; a full-body high-detail shot needs grid-aware camera framing.
- Opt-in secondary demo particles make spray/foam/bubble channels visible, but they are not yet a physical spray-generation model.
- This is an opt-in cinematic gate; it is intentionally not part of default `ctest`.

## Next Recommended Milestone

S55 should add grid-aware camera framing for high-detail gates, then begin replacing demo secondary seeding with physical spray generation.
