# S285 External Renderer Job Manifest

## Goal

Add a renderer-facing job manifest above the accepted external-render bundle so
external render adapters do not have to infer channel semantics from raw asset
paths.

## Scope

- Add `tools/build_external_renderer_job.py`.
- Read `lsfs_bridge_external_render_bundle` inputs without loading large CSV
  payloads.
- Summarize per-frame camera JSON, shutter, bounds, phase metadata, secondary
  channels, water mesh quality, and required asset paths.
- Include a channel contract for:
  - `camera`
  - `water_surface`
  - `phase_volume`
  - `particle_stream`
- Attach S282 bridge look settings, S284 review package, S283 publish manifest,
  and S280 external-bundle benchmark summary as related artifacts.
- Emit a Markdown report and fail if required assets or camera JSON are missing.

## Command

`python tools/build_external_renderer_job.py --bundle build/shots/s273_external_render_bundle/external_render_bundle.json --bridge-summary build/shots/s282_accepted_bridge_hires_review/blender/bridge_summary.json --review-package build/shots/s284_accepted_hires_review_package/review_package.json --accepted-publish build/shots/s283_s282_bridge_hires_publish/publish_manifest.json --benchmark-summary build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json --out build/shots/s285_external_renderer_job/external_renderer_job.json --report docs/reports/cinematic_external_renderer_job_s285.md --title "S285 External Renderer Job Manifest" --target-renderer external_path_tracer --output-format png --next "Use S285 as the renderer handoff contract. Next write a renderer-specific adapter or larger-shot job from the same schema."`

## Result

- Tool:
  `tools/build_external_renderer_job.py`
- Job JSON:
  `build/shots/s285_external_renderer_job/external_renderer_job.json`
- Report:
  `docs/reports/cinematic_external_renderer_job_s285.md`
- Schema: `lsfs_external_renderer_job`
- Status: `ready`
- Frames: `32`
- Resolution: `960 x 540`
- FPS: `8`
- Samples: `12`
- Missing assets: `0`
- Camera failures: `0`
- Minimum water mesh faces: `17720`
- Quality labels: `normal_rough: 3`, `stable: 29`
- Input footprint: `1.37 GB`
- Accepted review URL:
  `https://staff-held-cheese-organized.trycloudflare.com`

## Decision

S285 becomes the renderer handoff contract for SPEC-4 work. It is intentionally
metadata-heavy and payload-light: large particle and phase CSV files remain
streaming inputs for renderer-specific adapters.

## Next

Use the S285 schema to build either a renderer-specific adapter manifest or a
larger-shot job variant with the same channel contract.
