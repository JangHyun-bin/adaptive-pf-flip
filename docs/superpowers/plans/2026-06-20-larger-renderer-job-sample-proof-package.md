# S301 Larger Renderer Job Sample Proof Package

## Goal

Package the larger-job Blender sample proof into one handoff artifact.

## Scope

- Package `build/shots/s299_larger_external_renderer_job_blender_sample12`.
- Include the S299 gallery assets and bridge summary.
- Include proof evidence summaries:
  - `s295_larger_renderer_job`
  - `s299_s291_comparison`
  - `s300_publish`
  - `s297_preview_publish`
- Record a package JSON under `build/shots`.
- Record a Markdown report under `docs/reports`.

## Result

- Package JSON:
  `build/shots/s301_larger_renderer_job_sample_proof_package/review_package.json`
- Package report:
  `docs/reports/cinematic_larger_renderer_job_sample_proof_package_s301.md`
- Artifact count: `12`
- Summary source count: `4`
- Render status: `rendered`
- Frames: `12`
- Resolution: `960 x 540`
- Samples: `12`

## Decision

S301 is the current handoff package for the larger-job Blender sample proof. It
packages the S295 larger job, S299 render/comparison, S300 public endpoint, and
S297 preview evidence.

## Next

Use S301 as the stable checkpoint before longer larger-job Blender renders or
non-Blender external renderer adapters.
