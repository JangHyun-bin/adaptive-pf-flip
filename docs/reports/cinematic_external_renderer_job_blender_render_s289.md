# S289 External Renderer Job Blender Render

Generated UTC: `2026-06-19T20:47:53Z`
Source job: `build/shots/s285_external_renderer_job/external_renderer_job.json`
Render directory: `build/shots/s289_external_renderer_job_blender_render`
Bridge summary: `build/shots/s289_external_renderer_job_blender_render/bridge_summary.json`
Shot GIF: `build/shots/s289_external_renderer_job_blender_render/shot.gif`
Comparison summary: `build/shots/s289_external_renderer_job_blender_render/comparison_s282_aligned/comparison_summary.json`
Gallery: `build/shots/s289_external_renderer_job_blender_render/gallery/index.html`

## Command

`python tools/render_bridge_blender.py build/shots/s285_external_renderer_job/external_renderer_job.json build/shots/s289_external_renderer_job_blender_render --render-preset dam_break_water_mesh_smoothing --frames 8 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 31 --timeout-seconds 360`

## Render Result

- Status: `rendered`
- Frames: `8`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `42895.83049999783` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `207.0`
- Mean luminance: `74.66468798225308`
- First water mesh faces: `20000`
- Last water mesh faces: `22300`
- First secondary total: `256`
- Last secondary total: `964`
- GIF size: `2840630` bytes

## S282 Aligned Comparison

- Pair count: `8`
- Mean luminance delta: `0.5591733579282447`
- Minimum contrast delta: `62.0`
- Bright ratio delta: `4.852671682098762e-05`
- Highlight ratio delta: `4.701967592592605e-06`
- Nonblank ratio delta: `0.0`
- Aligned mean frame contrast delta: `-0.125`
- Aligned mean luma p99 delta: `0.375`
- Aligned mean specular ratio delta: `4.099151234567901e-06`

## Decision

S289 is the first actual Blender render driven from the S285 external renderer
job schema. It preserves nonblank coverage and stays close to S282 on aligned
frame-level calibration metrics.

## Next

Publish or package S289, then scale the job-path Blender render beyond the
8-frame smoke length.
