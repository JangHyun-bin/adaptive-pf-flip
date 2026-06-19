# S299 Larger External Renderer Job Blender Sample12

## Goal

Run a bounded actual Blender render from the S295 48-frame larger renderer job.

## Scope

- Render from `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`.
- Use accepted `dam_break_water_mesh_smoothing` preset.
- Render `12` frames at `960 x 540`, `12` samples.
- Assemble a GIF.
- Compare against a matched 12-frame sample from S291.
- Build a bridge gallery with render, comparison, and keyframes.

## Result

- Render summary:
  `build/shots/s299_larger_external_renderer_job_blender_sample12/bridge_summary.json`
- GIF:
  `build/shots/s299_larger_external_renderer_job_blender_sample12/shot.gif`
- Comparison summary:
  `build/shots/s299_larger_external_renderer_job_blender_sample12/comparison_s291/comparison_summary.json`
- Gallery:
  `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/index.html`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_s299.md`
- Comparison report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_compare_s299.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_gallery_s299.md`
- Status: `rendered`
- Frames: `12`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `66438.96269996185` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `159.0`

## Decision

S299 proves the larger 48-frame renderer job path can drive actual Blender
rendering, not just preview and dry-run paths.

## Next

Publish S299 as the public larger-job Blender sample endpoint, then package it
or scale to a longer larger-job Blender render.
