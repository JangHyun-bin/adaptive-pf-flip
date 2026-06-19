# S299 Larger External Renderer Job Blender Sample12

Generated UTC: `2026-06-19T21:18:19Z`
Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
Render directory: `build/shots/s299_larger_external_renderer_job_blender_sample12`
Bridge summary: `build/shots/s299_larger_external_renderer_job_blender_sample12/bridge_summary.json`
Shot GIF: `build/shots/s299_larger_external_renderer_job_blender_sample12/shot.gif`
Comparison summary: `build/shots/s299_larger_external_renderer_job_blender_sample12/comparison_s291/comparison_summary.json`
Gallery: `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/index.html`

## Command

`python tools/render_bridge_blender.py build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json build/shots/s299_larger_external_renderer_job_blender_sample12 --render-preset dam_break_water_mesh_smoothing --frames 12 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 47 --timeout-seconds 420`

## Render Result

- Status: `rendered`
- Frames: `12`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `66438.96269996185` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `159.0`
- Mean luminance: `75.1337416409465`
- First water mesh faces: `20000`
- Last water mesh faces: `22300`
- First secondary total: `256`
- Last secondary total: `964`
- GIF size: `4277864` bytes

## S291 Sampled Comparison

- Pair count: `12`
- Mean luminance delta: `0.22389511799124762`
- Minimum contrast delta: `-29.0`
- Bright ratio delta: `1.8667213220164604e-05`
- Highlight ratio delta: `-7.454828960905345e-06`
- Nonblank ratio delta: `0.0`
- Mean frame contrast delta: `-4.166666666666657`
- Mean luma p99 delta: `-0.1666666666666714`
- Mean specular ratio delta: `-1.1252572016460965e-06`

## Decision

S299 is the bounded Blender render proof for the larger 48-frame S295 job path.
It preserves nonblank coverage and stays close to the S291 full32 proof on
aligned sample metrics.

## Next

Publish or package S299, then decide whether to scale the larger-job Blender
render beyond 12 sampled frames.
