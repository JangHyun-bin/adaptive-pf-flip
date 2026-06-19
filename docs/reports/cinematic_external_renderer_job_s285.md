# S285 External Renderer Job Manifest

Generated UTC: `2026-06-19T20:34:51.571502+00:00`
Job JSON: `build/shots/s285_external_renderer_job/external_renderer_job.json`
Status: `ready`
Target renderer: `external_path_tracer`

## Bundle

- Bundle: `build/shots/s273_external_render_bundle/external_render_bundle.json`
- Accepted preset: `dam_break_water_mesh_smoothing`
- Frames: `32`
- Source window: `8..55`

## Render Settings

- Resolution: `960 x 540`
- FPS: `8.0`
- Samples: `12`
- Output format: `png`

## Channel Contract

- `camera`: `json_camera` from `camera`; Per-frame camera, shutter, bounds, and metadata summary.
- `water_surface`: `obj` from `water_mesh`; Primary liquid surface mesh for path tracing or Blender import.
- `phase_volume`: `csv` from `phase_cells`; Sparse phase-field cells for volumetric fill, masks, and diagnostics.
- `particle_stream`: `csv` from `particles`; Primary gas/liquid particles plus secondary spray, foam, droplet, and bubble channels.

## Input Footprint

- Camera JSON: `104.74 KB`
- Particle CSV: `1.28 GB`
- Phase-cell CSV: `33.66 MB`
- Water mesh OBJ: `53.39 MB`
- Total: `1.37 GB`

## Gates

- Missing assets: `0`
- Camera failures: `0`
- Sequence monotonic: `True`
- Minimum water mesh faces: `17720`
- Quality labels: `{'normal_rough': 3, 'stable': 29}`

## Review Links

- Accepted public URL: `https://staff-held-cheese-organized.trycloudflare.com`
- Benchmark status: `passed`

## Frame Samples

| Output | Sequence | Time | Particles | Phase Cells | Water Faces | Camera FOV | Secondary Total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 0.18 | 297280 | 44352 | 20000 | 45 | 256 |
| 16 | 32 | 0.6600000000000003 | 297280 | 44352 | 17912 | 45 | 256 |
| 31 | 55 | 1.1200000000000006 | 297988 | 44344 | 22300 | 45 | 964 |

## Related Artifacts

- `bridge_summary`: `build/shots/s282_accepted_bridge_hires_review/blender/bridge_summary.json`
- `review_package`: `build/shots/s284_accepted_hires_review_package/review_package.json`
- `accepted_publish`: `build/shots/s283_s282_bridge_hires_publish/publish_manifest.json`
- `external_bundle_benchmark`: `build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json`

## Next

Use S285 as the renderer handoff contract. Next write a renderer-specific adapter or larger-shot job from the same schema.
