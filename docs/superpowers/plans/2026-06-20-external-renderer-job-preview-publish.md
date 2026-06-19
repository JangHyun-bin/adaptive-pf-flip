# S287 External Renderer Job Preview Publish

## Goal

Publish the S286 external renderer job preview gallery as a public smoke-test
endpoint.

## Scope

- Serve `build/shots/s286_external_renderer_job_preview/gallery`.
- Use local port `8902`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S283 and S281 endpoints active separately.

## Result

- Local URL: `http://127.0.0.1:8902`
- Public URL: `https://installations-uni-tiger-nov.trycloudflare.com`
- Manifest:
  `build/shots/s287_external_renderer_job_preview_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_external_renderer_job_preview_publish_s287.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `61388`
- Cloudflared PID: `153412`

## Decision

S287 is the current public smoke-test endpoint for the S285/S286 external
renderer job schema path. It does not replace the higher-quality S283 accepted
bridge review endpoint.

## Next

Build a renderer-specific adapter manifest from S285, using S287 only as the
public preview proof that the job schema can already produce visible frames.
