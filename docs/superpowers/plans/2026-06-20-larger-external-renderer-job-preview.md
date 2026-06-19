# S296 Larger External Renderer Job Preview

## Goal

Run a visual smoke test for the 48-frame larger renderer job.

## Scope

- Render from `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`.
- Use the existing preview renderer.
- Render `24` preview frames at `1280 x 720`.
- Require minimum occupancy `0.01`.
- Assemble a GIF.
- Build a lightweight preview gallery.
- Record preview and gallery reports.

## Result

- Preview summary:
  `build/shots/s296_larger_external_renderer_job_preview/preview/render_summary.json`
- Preview GIF:
  `build/shots/s296_larger_external_renderer_job_preview/preview.gif`
- Gallery:
  `build/shots/s296_larger_external_renderer_job_preview/gallery/index.html`
- Preview report:
  `docs/reports/cinematic_larger_external_renderer_job_preview_s296.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_job_preview_gallery_s296.md`
- Frames: `24`
- Resolution: `1280 x 720`
- Minimum occupancy: `0.056203342013888886`
- Gallery assets: `9`

## Decision

S296 validates that the larger 48-frame job remains visually previewable before
heavier Blender work.

## Next

Publish the S296 gallery, then run a Blender adapter dry-run from S295.
