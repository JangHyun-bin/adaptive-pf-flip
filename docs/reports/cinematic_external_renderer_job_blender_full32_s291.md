# S291 External Renderer Job Blender Full32

Generated UTC: `2026-06-19T20:56:28Z`
Source job: `build/shots/s285_external_renderer_job/external_renderer_job.json`
Render directory: `build/shots/s291_external_renderer_job_blender_full32`
Bridge summary: `build/shots/s291_external_renderer_job_blender_full32/bridge_summary.json`
Shot GIF: `build/shots/s291_external_renderer_job_blender_full32/shot.gif`
Comparison summary: `build/shots/s291_external_renderer_job_blender_full32/comparison_s282/comparison_summary.json`
Gallery: `build/shots/s291_external_renderer_job_blender_full32/gallery/index.html`

## Command

`python tools/render_bridge_blender.py build/shots/s285_external_renderer_job/external_renderer_job.json build/shots/s291_external_renderer_job_blender_full32 --render-preset dam_break_water_mesh_smoothing --frames 32 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 31 --timeout-seconds 600`

## Render Result

- Status: `rendered`
- Frames: `32`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `160355.9743000078` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `188.0`
- Mean luminance: `74.90984652295525`
- First water mesh faces: `20000`
- Last water mesh faces: `22300`
- First secondary total: `256`
- Last secondary total: `964`
- GIF size: `11417844` bytes

## S282 Comparison

- Pair count: `8`
- Mean luminance delta: `0.8043318986304087`
- Minimum contrast delta: `43.0`
- Bright ratio delta: `4.27999614197531e-05`
- Highlight ratio delta: `2.188223379629632e-05`
- Nonblank ratio delta: `0.0`
- Mean frame contrast delta: `0.125`
- Mean luma p99 delta: `0.25`
- Mean specular ratio delta: `3.6168981481481466e-06`

## Decision

S291 is the first full-length 32-frame Blender render driven from the external
renderer job schema. It matches the S282 accepted high-resolution review closely
enough for a job-path proof: nonblank coverage is unchanged and aligned
calibration deltas are small.

## Next

Publish or package S291 as the current full-length job-path Blender proof, then
use the same S285 job schema for larger-shot or external renderer adapters.
