# S291 External Renderer Job Blender Full32

## Goal

Scale the S289 8-frame job-path Blender proof to the full 32-frame accepted
window.

## Scope

- Render from `build/shots/s285_external_renderer_job/external_renderer_job.json`.
- Use the accepted `dam_break_water_mesh_smoothing` preset.
- Render `32` frames at `960 x 540`, `12` samples.
- Assemble a GIF.
- Compare against S282 accepted high-resolution frames.
- Build a bridge gallery with the render, comparison, and keyframes.

## Result

- Render summary:
  `build/shots/s291_external_renderer_job_blender_full32/bridge_summary.json`
- GIF:
  `build/shots/s291_external_renderer_job_blender_full32/shot.gif`
- Comparison summary:
  `build/shots/s291_external_renderer_job_blender_full32/comparison_s282/comparison_summary.json`
- Gallery:
  `build/shots/s291_external_renderer_job_blender_full32/gallery/index.html`
- Render report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_s291.md`
- Comparison report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_compare_s291.md`
- Gallery report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_gallery_s291.md`
- Status: `rendered`
- Frames: `32`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `160355.9743000078` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `188.0`
- Mean frame contrast delta vs S282: `0.125`

## Decision

S291 supersedes S289 as the stronger job-path Blender proof because it covers
the full accepted 32-frame window.

## Next

Publish or package S291, then move to larger-shot job generation or an external
renderer adapter.
