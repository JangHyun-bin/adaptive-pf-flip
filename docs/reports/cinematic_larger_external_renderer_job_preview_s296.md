# S296 Larger External Renderer Job Preview

Generated UTC: `2026-06-19T21:09:01Z`
Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
Preview summary: `build/shots/s296_larger_external_renderer_job_preview/preview/render_summary.json`
Preview GIF: `build/shots/s296_larger_external_renderer_job_preview/preview.gif`
Gallery: `build/shots/s296_larger_external_renderer_job_preview/gallery/index.html`

## Command

`python tools/cinematic_render_stub.py build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json build/shots/s296_larger_external_renderer_job_preview/preview --frames 24 --width 1280 --height 720 --min-occupancy 0.01 --secondary-channel all`

`python tools/assemble_frames.py build/shots/s296_larger_external_renderer_job_preview/preview build/shots/s296_larger_external_renderer_job_preview/preview.gif --fps 8`

`python tools/build_preview_gallery.py --render-summary build/shots/s296_larger_external_renderer_job_preview/preview/render_summary.json --gif build/shots/s296_larger_external_renderer_job_preview/preview.gif --preview-dir build/shots/s296_larger_external_renderer_job_preview/preview --out build/shots/s296_larger_external_renderer_job_preview/gallery --title "S296 Larger External Renderer Job Preview" --keyframes 8 --report docs/reports/cinematic_larger_external_renderer_job_preview_gallery_s296.md --next "Use S296 as the visual smoke test for the 48-frame larger renderer job. Next publish it or run a Blender adapter dry-run."`

## Result

- Frames: `24`
- Resolution: `1280 x 720`
- Minimum occupancy: `0.056203342013888886`
- First frame water pixels: `62046`
- First frame secondary pixels: `2915`
- Middle frame water pixels: `49771`
- Last frame water pixels: `53218`
- Last frame secondary pixels: `4852`
- GIF size: `931895` bytes
- Gallery assets: `9`
- Visual check: representative keyframe is nonblank and shows the expected
  water surface, secondary particles, and mesh overlay from the S295 larger job.

## Decision

S296 proves the S295 48-frame larger renderer job can drive the preview path at
the same 1280 x 720 benchmark preview scale used earlier.

## Next

Publish the S296 gallery as a public larger-job smoke test, then run a Blender
adapter dry-run from S295.
