# S286 External Renderer Job Preview

Generated UTC: `2026-06-19T20:37:17Z`
Source job: `build/shots/s285_external_renderer_job/external_renderer_job.json`
Preview summary: `build/shots/s286_external_renderer_job_preview/preview/render_summary.json`
Preview GIF: `build/shots/s286_external_renderer_job_preview/preview.gif`
Gallery: `build/shots/s286_external_renderer_job_preview/gallery/index.html`

## Command

`python tools/cinematic_render_stub.py build/shots/s285_external_renderer_job/external_renderer_job.json build/shots/s286_external_renderer_job_preview/preview --frames 16 --width 960 --height 540 --min-occupancy 0.01 --secondary-channel all`

`python tools/assemble_frames.py build/shots/s286_external_renderer_job_preview/preview build/shots/s286_external_renderer_job_preview/preview.gif --fps 8`

`python tools/build_preview_gallery.py --render-summary build/shots/s286_external_renderer_job_preview/preview/render_summary.json --gif build/shots/s286_external_renderer_job_preview/preview.gif --preview-dir build/shots/s286_external_renderer_job_preview/preview --out build/shots/s286_external_renderer_job_preview/gallery --title "S286 External Renderer Job Preview" --keyframes 8 --report docs/reports/cinematic_external_renderer_job_preview_gallery_s286.md --next "Use S286 as the visual smoke test that S285 renderer jobs can drive the existing preview renderer. Next publish the gallery or build a renderer-specific adapter."`

## Result

- Frames: `16`
- Resolution: `960 x 540`
- Minimum occupancy: `0.05804398148148148`
- First frame water pixels: `35149`
- First frame secondary pixels: `2545`
- Last frame water pixels: `30207`
- Last frame secondary pixels: `4126`
- GIF size: `393813` bytes
- Gallery assets: `9`
- Visual check: the first keyframe is nonblank and shows water, secondary
  particles, and mesh overlay from the S285 job manifest.

## Decision

S286 proves the S285 renderer job schema is executable by the existing preview
renderer, not just a static handoff manifest.

## Next

Publish the S286 gallery if a public smoke-test endpoint is useful, then build
a renderer-specific adapter from the same job schema.
