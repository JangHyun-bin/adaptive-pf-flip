# S303 Larger External Renderer Job Blender Sample24 Publish

## Goal

Replace the S300 12-frame larger-job endpoint with the S302 24-frame Blender
sample gallery.

## Scope

- Stop the S300 larger-job sample12 quick tunnel.
- Serve `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery`.
- Use local port `8903`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S292 active separately as the full32 job-path proof endpoint.

## Result

- Stopped S300 PIDs: `60408`, `60752`
- Local URL: `http://127.0.0.1:8903`
- Public URL: `https://animals-zealand-fcc-thursday.trycloudflare.com`
- Manifest:
  `build/shots/s303_larger_external_renderer_job_blender_sample24_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_sample24_publish_s303.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `17836`
- Cloudflared PID: `160000`

## Decision

S303 is the current public larger-job 24-frame Blender sample endpoint. It
supersedes S300 for larger-job public review.

## Next

Package S302/S303 as the current larger-job 24-frame proof, or attempt the full
48-frame larger-job Blender render.
