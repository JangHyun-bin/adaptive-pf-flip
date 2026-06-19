# S302 Larger External Renderer Job Blender Sample24

Generated UTC: `2026-06-19T21:29:52Z`
Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
Render directory: `build/shots/s302_larger_external_renderer_job_blender_sample24`
Bridge summary: `build/shots/s302_larger_external_renderer_job_blender_sample24/bridge_summary.json`
Shot GIF: `build/shots/s302_larger_external_renderer_job_blender_sample24/shot.gif`
Comparison summary: `build/shots/s302_larger_external_renderer_job_blender_sample24/comparison_s291/comparison_summary.json`
Gallery: `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/index.html`

## Command

`python tools/render_bridge_blender.py build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json build/shots/s302_larger_external_renderer_job_blender_sample24 --render-preset dam_break_water_mesh_smoothing --frames 24 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 47 --timeout-seconds 600`

## Render Result

- Status: `rendered`
- Frames: `24`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `120208.42640002957` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `128.0`
- Mean luminance: `74.98456548996914`
- First water mesh faces: `20000`
- Last water mesh faces: `22300`
- First secondary total: `256`
- Last secondary total: `964`
- GIF size: `8558036` bytes

## S291 Sampled Comparison

- Pair count: `12`
- Mean luminance delta: `0.07471896701389369`
- Minimum contrast delta: `-60.0`
- Bright ratio delta: `-1.9109278549382734e-05`
- Highlight ratio delta: `-9.464216820987667e-06`
- Nonblank ratio delta: `0.0`
- Mean frame contrast delta: `-0.25`
- Mean luma p99 delta: `0.0833333333333286`
- Mean specular ratio delta: `-3.215020576131689e-06`

## Decision

S302 extends the larger-job Blender proof from 12 to 24 sampled frames. It
preserves nonblank coverage and stays close to S291 on aligned calibration
metrics.

## Next

Publish or package S302, then decide whether to attempt the full 48-frame
larger-job Blender render.
