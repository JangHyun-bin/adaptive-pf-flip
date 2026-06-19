# S293 Full Renderer Job Proof Package

## Goal

Package the full-length external-renderer job proof into one handoff artifact.

## Scope

- Package `build/shots/s291_external_renderer_job_blender_full32`.
- Include the S291 gallery assets and bridge summary.
- Include proof evidence summaries:
  - `s285_renderer_job`
  - `s291_s282_comparison`
  - `s292_publish`
  - `s280_external_bundle_benchmark`
- Record a package JSON under `build/shots`.
- Record a Markdown report under `docs/reports`.

## Result

- Package JSON:
  `build/shots/s293_full_renderer_job_proof_package/review_package.json`
- Package report:
  `docs/reports/cinematic_full_renderer_job_proof_package_s293.md`
- Artifact count: `12`
- Summary source count: `4`
- Render status: `rendered`
- Frames: `32`
- Resolution: `960 x 540`
- Samples: `12`

## Decision

S293 is the current handoff package for the full-length external-renderer job
proof. It packages the S285 schema, S291 full render, S292 public endpoint, and
benchmark context.

## Next

Use S293 as the stable handoff before moving to larger-shot job generation or a
non-Blender external renderer adapter.
