# S305 Larger External Renderer Job Blender Full48

Generated UTC: `2026-06-19T21:45:50Z`
Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
Render directory: `build/shots/s305_larger_external_renderer_job_blender_full48`
Bridge summary: `build/shots/s305_larger_external_renderer_job_blender_full48/bridge_summary.json`
Shot GIF: `build/shots/s305_larger_external_renderer_job_blender_full48/shot.gif`
Comparison summary: `build/shots/s305_larger_external_renderer_job_blender_full48/comparison_s302/comparison_summary.json`
Gallery: `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/index.html`

## Command

`python tools/render_bridge_blender.py build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json build/shots/s305_larger_external_renderer_job_blender_full48 --render-preset dam_break_water_mesh_smoothing --frames 48 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 47 --timeout-seconds 900`

## Render Result

- Status: `rendered`
- Frames: `48`
- Resolution: `960 x 540`
- Samples: `12`
- Blender elapsed: `238031.95650002453` ms
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `106`
- Mean luminance: `75.00571092142489`
- Source frame window: `20..55`
- First water depth z span: `23.0`
- Last water depth z span: `28.0`
- First secondary total: `256`
- Last secondary total: `964`
- Secondary streak total first/last: `158` / `848`
- Contact foam total first/last: `57` / `24`
- Impact ripple total first/last: `73` / `73`
- GIF size: `17138447` bytes

## S302 Sampled Comparison

- Pair count: `24`
- Mean luminance delta: `0.021145431455749986`
- Minimum contrast delta: `-22.0`
- Bright ratio delta: `9.524498456790125e-06`
- Highlight ratio delta: `5.907600308641971e-06`
- Nonblank ratio delta: `0.0`
- Mean frame contrast delta: `-4.125`
- Mean luma p99 delta: `-0.125`
- Mean specular ratio delta: `-7.957175925925922e-06`

## Decision

S305 completes the larger-job Blender proof over the full 48-frame source
window. It preserves full nonblank coverage and stays close to S302's sampled
calibration metrics while exposing the full secondary-particle growth across
the shot.

## Next

Publish the S305 gallery through Cloudflare Tunnel, then package S305 or start
the non-Blender external renderer adapter.
