# S308 Larger External Renderer Generic Adapter Manifest

Generated UTC: `2026-06-19T21:53:31.780812+00:00`
Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
Status: `ready`
Target renderer: `generic_path_tracer`
Adapter kind: `renderer_neutral_scene_json`
Execution mode: `manifest_only`

## Source

- Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
- Source job target: `external_path_tracer`
- Command list: `build/shots/s308_larger_external_renderer_generic_adapter/render_commands.txt`

## Render Settings

- Resolution: `960 x 540`
- FPS: `12.0`
- Samples: `12`
- Output format: `png`

## Gates

- Frames: `48`
- Scene descriptors: `48`
- Missing assets: `0`
- Sequence monotonic: `True`
- Minimum water mesh faces: `17720`
- Required minimum water mesh faces: `1000`

## Footprint

- Referenced asset bytes: `2.05 GB`
- Scene descriptor bytes: `333.99 KB`

## Material Contract

- `water_surface`: `dielectric_surface` from `water_mesh`
- `phase_volume`: `sparse_volume_or_mask` from `phase_cells`
- `secondary_particles`: `csv_particle_channels` from `particles`

## Frame Samples

| Output | Source Output | Sequence | Time | Particles | Phase Cells | Water Faces | Secondary Total |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 8 | 0.18 | 297280 | 44352 | 20000 | 256 |
| 24 | 24 | 32 | 0.6600000000000003 | 297280 | 44352 | 17912 | 256 |
| 47 | 47 | 55 | 1.1200000000000006 | 297988 | 44344 | 22300 | 964 |

## Related Artifacts

- `look_reference`: `build/shots/s305_larger_external_renderer_job_blender_full48/bridge_summary.json`
- `proof_package`: `build/shots/s307_larger_renderer_job_full48_proof_package/review_package.json`
- `public_manifest`: `build/shots/s306_larger_external_renderer_job_blender_full48_publish/publish_manifest.json`

## Next

Implement a renderer-specific backend that consumes these scene descriptors, starting with a dry-run command validator before invoking an offline renderer.
