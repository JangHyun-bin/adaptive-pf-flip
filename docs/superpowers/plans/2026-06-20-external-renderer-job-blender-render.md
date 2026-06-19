# S289 External Renderer Job Blender Render

## Goal

Run an actual bounded Blender render through the S285 external renderer job
path.

## Scope

- Reuse the S288 Blender adapter path.
- Render from `build/shots/s285_external_renderer_job/external_renderer_job.json`.
- Use the accepted `dam_break_water_mesh_smoothing` preset.
- Render `8` frames at `960 x 540`, `12` samples.
- Assemble a GIF.
- Compare against an aligned 8-frame sample from S282.
- Build a bridge gallery with the render, comparison, and keyframes.

## Result

- Render summary:
  `build/shots/s289_external_renderer_job_blender_render/bridge_summary.json`
- GIF:
  `build/shots/s289_external_renderer_job_blender_render/shot.gif`
- Comparison summary:
  `build/shots/s289_external_renderer_job_blender_render/comparison_s282_aligned/comparison_summary.json`
- Gallery:
  `build/shots/s289_external_renderer_job_blender_render/gallery/index.html`
- Render report:
  `docs/reports/cinematic_external_renderer_job_blender_render_s289.md`
- Comparison report:
  `docs/reports/cinematic_external_renderer_job_blender_render_compare_s289.md`
- Gallery report:
  `docs/reports/cinematic_external_renderer_job_blender_render_gallery_s289.md`
- Status: `rendered`
- Frames: `8`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `42895.83049999783` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `207.0`
- Aligned mean frame contrast delta vs S282: `-0.125`

## Decision

S289 proves the external renderer job schema can drive actual Blender rendering,
not only preview/dry-run paths.

## Next

Publish or package S289 as the job-path Blender render proof, then run a longer
job-path render.
