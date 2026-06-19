# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T20:49:42Z`
Gallery directory: `build/shots/s289_external_renderer_job_blender_render/gallery`
Manifest: `build/shots/s290_external_renderer_job_blender_render_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8902`
- Public: `https://mathematics-insert-hybrid-dozens.trycloudflare.com`

## Processes

- HTTP server PID: `154780`
- cloudflared PID: `90764`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8902/index.html` | `GET` | 200 | 6705 |
| `http://127.0.0.1:8902/assets/shot.gif` | `HEAD` | 200 | 2840630 |
| `https://mathematics-insert-hybrid-dozens.trycloudflare.com/index.html` | `GET` | 200 | 6705 |
| `https://mathematics-insert-hybrid-dozens.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 2840630 |

## Logs

- `build/shots/s289_external_renderer_job_blender_render/gallery/publish_logs/http_stdout.log`
- `build/shots/s289_external_renderer_job_blender_render/gallery/publish_logs/http_stderr.log`
- `build/shots/s289_external_renderer_job_blender_render/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s289_external_renderer_job_blender_render/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public review page for the first actual Blender render
driven from the external renderer job schema. Keep S283 and S281 active
separately for accepted high-resolution bridge review and external-bundle
benchmark preview.
