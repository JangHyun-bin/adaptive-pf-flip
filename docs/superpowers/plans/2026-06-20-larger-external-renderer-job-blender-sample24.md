# S302 Larger External Renderer Job Blender Sample24

## Goal

Scale the larger-job Blender proof from 12 sampled frames to 24 sampled frames.

## Scope

- Render from `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`.
- Use accepted `dam_break_water_mesh_smoothing` preset.
- Render `24` frames at `960 x 540`, `12` samples.
- Assemble a GIF.
- Compare against a matched 24-frame sample from S291.
- Build a bridge gallery with render, comparison, and keyframes.

## Result

- Render summary:
  `build/shots/s302_larger_external_renderer_job_blender_sample24/bridge_summary.json`
- GIF:
  `build/shots/s302_larger_external_renderer_job_blender_sample24/shot.gif`
- Comparison summary:
  `build/shots/s302_larger_external_renderer_job_blender_sample24/comparison_s291/comparison_summary.json`
- Gallery:
  `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/index.html`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_s302.md`
- Comparison report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_compare_s302.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_gallery_s302.md`
- Status: `rendered`
- Frames: `24`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `120208.42640002957` ms
- Minimum nonblank ratio: `1.0`
- Mean frame contrast delta vs S291 sample: `-0.25`

## Decision

S302 is the stronger larger-job Blender proof because it doubles the sample
length from S299 while keeping aligned visual metrics close to the full32 proof.

## Next

Publish S302 as the larger-job 24-frame render endpoint, then package it or
attempt the full 48-frame larger-job render.
