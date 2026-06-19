# S304 Larger Renderer Job Sample24 Proof Package

## Goal

Package the S302/S303 larger-job 24-frame Blender proof into a compact review
bundle for handoff and comparison.

## Scope

- Use the S302 24-frame Blender gallery as the visual artifact source.
- Include the S302 bridge summary and gallery manifest.
- Attach summary sources for:
  - S295 larger external renderer job
  - S302-vs-S291 comparison
  - S303 public publish manifest
  - S301 12-frame proof package
- Write a Markdown review report.
- Keep generated package artifacts under `build/shots`.

## Result

- Package JSON:
  `build/shots/s304_larger_renderer_job_sample24_proof_package/review_package.json`
- Report:
  `docs/reports/cinematic_larger_renderer_job_sample24_proof_package_s304.md`
- Visual/metadata artifacts: `12`
- Summary sources: `4`
- Render frames: `24`
- Resolution: `960 x 540`
- Samples: `12`

## Decision

S304 is the current larger-job 24-frame proof package. It supersedes S301 for
larger-job visual handoff while S303 remains the current public endpoint.

## Next

Attempt the full 48-frame larger-job Blender render, or add a non-Blender
external renderer adapter using the same S295 job manifest.
