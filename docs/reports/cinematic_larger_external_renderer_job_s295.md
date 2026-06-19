# S295 Larger External Renderer Job 48

Generated UTC: `2026-06-19T21:05:50.304553+00:00`
Job JSON: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
Status: `ready`
Target renderer: `external_path_tracer`

## Bundle

- Bundle: `build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json`
- Accepted preset: `dam_break_water_mesh_smoothing`
- Frames: `48`
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

- Camera JSON: `157.18 KB`
- Particle CSV: `1.92 GB`
- Phase-cell CSV: `50.49 MB`
- Water mesh OBJ: `80.07 MB`
- Total: `2.05 GB`

## Gates

- Missing assets: `0`
- Camera failures: `0`
- Sequence monotonic: `True`
- Minimum water mesh faces: `17720`
- Quality labels: `{'normal_rough': 4, 'stable': 44}`

## Review Links

- Accepted public URL: `https://shall-warnings-critical-quite.trycloudflare.com`
- Benchmark status: `passed`

## Frame Samples

| Output | Sequence | Time | Particles | Phase Cells | Water Faces | Camera FOV | Secondary Total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 0.18 | 297280 | 44352 | 20000 | 45 | 256 |
| 24 | 32 | 0.6600000000000003 | 297280 | 44352 | 17912 | 45 | 256 |
| 47 | 55 | 1.1200000000000006 | 297988 | 44344 | 22300 | 45 | 964 |

## Related Artifacts

- `bridge_summary`: `build/shots/s291_external_renderer_job_blender_full32/bridge_summary.json`
- `review_package`: `build/shots/s293_full_renderer_job_proof_package/review_package.json`
- `accepted_publish`: `build/shots/s292_external_renderer_job_blender_full32_publish/publish_manifest.json`
- `external_bundle_benchmark`: `build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json`

## Next

Use S295 as the 48-frame larger renderer job contract before running preview and Blender gates.
