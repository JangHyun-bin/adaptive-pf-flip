# S297 Larger External Renderer Job Preview Publish

## Goal

Publish the S296 larger-job preview gallery as a public smoke-test endpoint.

## Scope

- Serve `build/shots/s296_larger_external_renderer_job_preview/gallery`.
- Use local port `8903`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S292 active separately as the full32 Blender render proof endpoint.

## Result

- Local URL: `http://127.0.0.1:8903`
- Public URL: `https://arch-walk-informational-corporate.trycloudflare.com`
- Manifest:
  `build/shots/s297_larger_external_renderer_job_preview_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_job_preview_publish_s297.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `167784`
- Cloudflared PID: `49980`

## Decision

S297 is the current public larger-job preview endpoint. It validates visual
availability for S295 without replacing the S292 full32 Blender proof endpoint.

## Next

Run a Blender adapter dry-run from S295, then decide whether to render a bounded
48-frame Blender sample.
