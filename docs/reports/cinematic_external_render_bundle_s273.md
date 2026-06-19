# S273 Accepted External Render Bundle

Generated UTC: `2026-06-19T19:47:20.253325+00:00`
Bundle JSON: `build/shots/s273_external_render_bundle/external_render_bundle.json`
Accepted preset: `dam_break_water_mesh_smoothing`
Frame count: `32`
Source window: `8..55`
Asset hash mode: `size_only`
Public URL: `https://rfc-empirical-match-outstanding.trycloudflare.com`

## Inputs

- Handoff manifest: `build/shots/s271_accepted_handoff/handoff_manifest.json`
- Sequence: `build/shots/s205_surface_quality_annotation/converted/sequence.json`
- Render data summary: `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`

## Totals

- Camera JSON bytes: `104.74 KB`
- Particle CSV bytes: `1.28 GB`
- Phase-cell CSV bytes: `33.66 MB`
- Water mesh OBJ bytes: `53.39 MB`
- Missing assets: `0`

## Frame Samples

| Output | Sequence | Particles | Phase Cells | Water Faces | Quality |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 8 | 297280 | 44352 | 20000 | `normal_rough` |
| 16 | 32 | 297280 | 44352 | 17912 | `stable` |
| 31 | 55 | 297988 | 44344 | 22300 | `stable` |

## Next

Use this bundle as the frame-level accepted input list for external renderer prototypes and larger-shot reruns.
