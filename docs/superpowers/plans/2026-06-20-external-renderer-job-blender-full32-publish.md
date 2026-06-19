# S292 External Renderer Job Blender Full32 Publish

## Goal

Replace the S290 8-frame job-path render endpoint with the S291 full32 gallery.

## Scope

- Stop the S290 job-path Blender render quick tunnel.
- Serve `build/shots/s291_external_renderer_job_blender_full32/gallery`.
- Use local port `8902`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S283 and S281 endpoints active separately.

## Result

- Stopped S290 PIDs: `90764`, `154780`
- Local URL: `http://127.0.0.1:8902`
- Public URL: `https://shall-warnings-critical-quite.trycloudflare.com`
- Manifest:
  `build/shots/s292_external_renderer_job_blender_full32_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_external_renderer_job_blender_full32_publish_s292.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `66504`
- Cloudflared PID: `129180`

## Decision

S292 is the current public full-length job-path Blender render endpoint. It
supersedes S290 for job-schema public review.

## Next

Package S291/S292 as the current full-length external-renderer job proof, then
move to larger-shot job generation or external renderer adapters.
