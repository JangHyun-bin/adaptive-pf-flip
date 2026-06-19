# S290 External Renderer Job Blender Render Publish

## Goal

Replace the S287 preview-smoke endpoint with the S289 actual Blender render
gallery.

## Scope

- Stop the S287 external renderer job preview quick tunnel.
- Serve `build/shots/s289_external_renderer_job_blender_render/gallery`.
- Use local port `8902`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S283 and S281 endpoints active separately.

## Result

- Stopped S287 PIDs: `153412`, `61388`
- Local URL: `http://127.0.0.1:8902`
- Public URL: `https://mathematics-insert-hybrid-dozens.trycloudflare.com`
- Manifest:
  `build/shots/s290_external_renderer_job_blender_render_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_external_renderer_job_blender_render_publish_s290.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `154780`
- Cloudflared PID: `90764`

## Decision

S290 is the current public job-path Blender render endpoint. It supersedes S287
for job-schema public review, but it does not replace S283 as the accepted
high-resolution bridge review endpoint.

## Next

Scale the job-path Blender render from the 8-frame proof toward a longer
32-frame run, or package S289/S290 as the current external-renderer job proof.
