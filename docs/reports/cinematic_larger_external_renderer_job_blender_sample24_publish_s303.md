# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T21:32:43Z`
Gallery directory: `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery`
Manifest: `build/shots/s303_larger_external_renderer_job_blender_sample24_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8903`
- Public: `https://animals-zealand-fcc-thursday.trycloudflare.com`

## Processes

- HTTP server PID: `17836`
- cloudflared PID: `160000`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8903/index.html` | `GET` | 200 | 6727 |
| `http://127.0.0.1:8903/assets/shot.gif` | `HEAD` | 200 | 8558036 |
| `https://animals-zealand-fcc-thursday.trycloudflare.com/index.html` | `GET` | 200 | 6727 |
| `https://animals-zealand-fcc-thursday.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 8558036 |

## Logs

- `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/publish_logs/http_stdout.log`
- `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/publish_logs/http_stderr.log`
- `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s302_larger_external_renderer_job_blender_sample24/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public larger-job 24-frame Blender sample proof. Keep
S292 active separately as the full32 job-path proof, then package S302/S303 or
attempt the full 48-frame larger-job Blender render.
