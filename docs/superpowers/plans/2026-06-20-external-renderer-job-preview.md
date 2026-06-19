# S286 External Renderer Job Preview

## Goal

Prove that the S285 external renderer job manifest can directly drive a visual
preview path.

## Scope

- Extend `tools/cinematic_render_stub.py` to accept
  `lsfs_external_renderer_job` inputs.
- Keep the existing bundle frame loader and preview renderer behavior.
- Add a job-specific selected-frame loader and require job status `ready`.
- Render a 16-frame `960 x 540` preview from S285.
- Assemble a GIF and build a lightweight gallery.
- Record preview and gallery reports.

## Result

- Updated tool:
  `tools/cinematic_render_stub.py`
- Preview summary:
  `build/shots/s286_external_renderer_job_preview/preview/render_summary.json`
- Preview GIF:
  `build/shots/s286_external_renderer_job_preview/preview.gif`
- Gallery:
  `build/shots/s286_external_renderer_job_preview/gallery/index.html`
- Preview report:
  `docs/reports/cinematic_external_renderer_job_preview_s286.md`
- Gallery report:
  `docs/reports/cinematic_external_renderer_job_preview_gallery_s286.md`
- Frames: `16`
- Resolution: `960 x 540`
- Minimum occupancy: `0.05804398148148148`
- Gallery assets: `9`

## Decision

S286 makes S285 actionable: a renderer job manifest can now be used as a direct
preview-render source. This is still a preview renderer, not the final
path-traced SPEC-4 renderer.

## Next

Publish the S286 gallery as the current job-schema smoke-test endpoint, or move
straight to a renderer-specific adapter manifest.
