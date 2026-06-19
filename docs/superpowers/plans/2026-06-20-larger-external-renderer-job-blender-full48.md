# S305 Larger External Renderer Job Blender Full48

## Goal

Render the S295 larger external renderer job through the accepted Blender bridge
for the full 48-frame window.

## Scope

- Render `48` Blender frames from the S295 larger renderer job.
- Use preset `dam_break_water_mesh_smoothing`.
- Keep resolution at `960 x 540` and samples at `12`.
- Assemble the full48 GIF.
- Compare S305 against S302 using `24` sampled frame pairs.
- Build the static S305 gallery with GIF, keyframes, comparison sheet, and
  metadata.
- Record render, comparison, and gallery reports.

## Result

- Render directory:
  `build/shots/s305_larger_external_renderer_job_blender_full48`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_s305.md`
- Comparison report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_compare_s305.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_gallery_s305.md`
- Gallery:
  `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/index.html`
- Frames: `48`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `238031.95650002453` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `106`
- GIF size: `17138447` bytes
- S302 sampled comparison nonblank delta: `0.0`

## Decision

S305 supersedes S302 as the strongest local larger-job Blender visual proof.
S302/S303 remain useful as a lighter 24-frame public endpoint and package
baseline.

## Next

Publish the S305 gallery, then package S305 or start the non-Blender external
renderer adapter.
