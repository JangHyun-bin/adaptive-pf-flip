# S307 Larger Renderer Job Full48 Proof Package

## Goal

Package the S305/S306 larger-job full48 Blender proof into the current handoff
bundle.

## Scope

- Use the S305 full48 Blender gallery as the visual artifact source.
- Include the S305 bridge summary and gallery manifest.
- Attach summary sources for:
  - S295 larger external renderer job
  - S305-vs-S302 sampled comparison
  - S306 public publish manifest
  - S304 sample24 proof package
- Write a Markdown review report.
- Keep generated package artifacts under `build/shots`.

## Result

- Package JSON:
  `build/shots/s307_larger_renderer_job_full48_proof_package/review_package.json`
- Report:
  `docs/reports/cinematic_larger_renderer_job_full48_proof_package_s307.md`
- Visual/metadata artifacts: `12`
- Summary sources: `4`
- Render frames: `48`
- Resolution: `960 x 540`
- Samples: `12`

## Decision

S307 is the current full48 larger-job Blender proof package. It supersedes S304
for larger-job handoff while S306 remains the current public endpoint.

## Next

Start the non-Blender external renderer adapter path, or move to a larger
simulation-scale job using the same package/report flow.
