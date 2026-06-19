# S306 Larger External Renderer Job Blender Full48 Publish

## Goal

Publish the S305 full48 Blender gallery through a Cloudflare quick tunnel for
external review.

## Scope

- Stop the S303 24-frame larger-job quick tunnel.
- Serve `build/shots/s305_larger_external_renderer_job_blender_full48/gallery`.
- Use local port `8903`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S292 active separately as the full32 job-path proof endpoint.

## Result

- Stopped S303 PIDs: `160000`, `17836`
- Local URL: `http://127.0.0.1:8903`
- Public URL: `https://combined-ion-bowl-ted.trycloudflare.com`
- Manifest:
  `build/shots/s306_larger_external_renderer_job_blender_full48_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_full48_publish_s306.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `59524`
- Cloudflared PID: `44484`

## Decision

S306 is the current public larger-job full48 Blender proof endpoint. It
supersedes S303 for public larger-job review.

## Next

Package S305/S306 as the current full48 proof bundle, then start the non-Blender
external renderer adapter path.
