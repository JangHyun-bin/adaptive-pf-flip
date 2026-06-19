# S294 Larger External Render Bundle 48

Generated UTC: `2026-06-19T21:04:01.745532+00:00`
Bundle JSON: `build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json`
Accepted preset: `dam_break_water_mesh_smoothing`
Frame count: `48`
Source window: `8..55`
Asset hash mode: `size_only`
Public URL: `https://shall-warnings-critical-quite.trycloudflare.com`

## Inputs

- Handoff manifest: `build/shots/s271_accepted_handoff/handoff_manifest.json`
- Sequence: `build/shots/s205_surface_quality_annotation/converted/sequence.json`
- Render data summary: `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`

## Totals

- Camera JSON bytes: `157.18 KB`
- Particle CSV bytes: `1.92 GB`
- Phase-cell CSV bytes: `50.49 MB`
- Water mesh OBJ bytes: `80.07 MB`
- Missing assets: `0`

## Frame Samples

| Output | Sequence | Particles | Phase Cells | Water Faces | Quality |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 8 | 297280 | 44352 | 20000 | `normal_rough` |
| 24 | 32 | 297280 | 44352 | 17912 | `stable` |
| 47 | 55 | 297988 | 44344 | 22300 | `stable` |

## Next

Use S294 as the 48-frame larger-shot external-render input bundle before creating a larger renderer job.
