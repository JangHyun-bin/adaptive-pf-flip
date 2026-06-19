# S295 Larger External Renderer Job 48

## Goal

Build a 48-frame renderer job contract from the S294 larger external bundle.

## Scope

- Consume `build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json`.
- Attach S291 bridge look settings.
- Attach S293 proof package.
- Attach S292 publish evidence.
- Attach S280 benchmark context.
- Emit a `lsfs_external_renderer_job` manifest and Markdown report.
- Verify required assets, camera JSON, sequence monotonicity, and water mesh
  face count gate.

## Command

`python tools/build_external_renderer_job.py --bundle build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json --bridge-summary build/shots/s291_external_renderer_job_blender_full32/bridge_summary.json --review-package build/shots/s293_full_renderer_job_proof_package/review_package.json --accepted-publish build/shots/s292_external_renderer_job_blender_full32_publish/publish_manifest.json --benchmark-summary build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json --out build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json --report docs/reports/cinematic_larger_external_renderer_job_s295.md --title "S295 Larger External Renderer Job 48" --target-renderer external_path_tracer --output-format png --next "Use S295 as the 48-frame larger renderer job contract before running preview and Blender gates."`

## Result

- Job JSON:
  `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_job_s295.md`
- Schema: `lsfs_external_renderer_job`
- Status: `ready`
- Frames: `48`
- Source sequence range: `8..55`
- Missing assets: `0`
- Camera failures: `0`
- Sequence monotonic: `True`
- Minimum water mesh faces: `17720`
- Quality labels: `normal_rough: 4`, `stable: 44`
- Input footprint: `2.05 GB`

## Decision

S295 is the larger renderer-job contract. It supersedes S285 when testing
larger temporal coverage while preserving the same channel contract.

## Next

Run a visual preview/gate from S295 before attempting any Blender render on the
larger 48-frame job.
