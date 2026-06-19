# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T21:47:53Z`
Gallery directory: `build/shots/s305_larger_external_renderer_job_blender_full48/gallery`
Manifest: `build/shots/s306_larger_external_renderer_job_blender_full48_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8903`
- Public: `https://combined-ion-bowl-ted.trycloudflare.com`

## Processes

- HTTP server PID: `59524`
- cloudflared PID: `44484`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8903/index.html` | `GET` | 200 | 6699 |
| `http://127.0.0.1:8903/assets/shot.gif` | `HEAD` | 200 | 17138447 |
| `https://combined-ion-bowl-ted.trycloudflare.com/index.html` | `GET` | 200 | 6699 |
| `https://combined-ion-bowl-ted.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 17138447 |

## Logs

- `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/publish_logs/http_stdout.log`
- `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/publish_logs/http_stderr.log`
- `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s305_larger_external_renderer_job_blender_full48/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public full48 larger-job Blender proof. Package S305/S306
as the current handoff bundle, then start the non-Blender external renderer
adapter path.
