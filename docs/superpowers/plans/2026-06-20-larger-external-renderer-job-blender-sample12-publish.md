# S300 Larger External Renderer Job Blender Sample12 Publish

## Goal

Replace the S297 larger-job preview endpoint with the S299 actual Blender
sample gallery.

## Scope

- Stop the S297 larger-job preview quick tunnel.
- Serve `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery`.
- Use local port `8903`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S292 active separately as the full32 job-path proof endpoint.

## Result

- Stopped S297 PIDs: `49980`, `167784`
- Local URL: `http://127.0.0.1:8903`
- Public URL: `https://vatican-ranking-laden-slip.trycloudflare.com`
- Manifest:
  `build/shots/s300_larger_external_renderer_job_blender_sample12_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample12_publish_s300.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `60752`
- Cloudflared PID: `60408`

## Decision

S300 is the current public larger-job Blender sample endpoint. It supersedes
S297 for larger-job public review.

## Next

Package S299/S300 as the current larger-job Blender sample proof, or scale the
larger-job Blender render beyond 12 sampled frames.
