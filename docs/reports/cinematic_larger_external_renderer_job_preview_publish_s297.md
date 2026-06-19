# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T21:11:17Z`
Gallery directory: `build/shots/s296_larger_external_renderer_job_preview/gallery`
Manifest: `build/shots/s297_larger_external_renderer_job_preview_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8903`
- Public: `https://arch-walk-informational-corporate.trycloudflare.com`

## Processes

- HTTP server PID: `167784`
- cloudflared PID: `49980`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8903/index.html` | `GET` | 200 | 4188 |
| `http://127.0.0.1:8903/assets/shot.gif` | `HEAD` | 200 | 931895 |
| `https://arch-walk-informational-corporate.trycloudflare.com/index.html` | `GET` | 200 | 4188 |
| `https://arch-walk-informational-corporate.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 931895 |

## Logs

- `build/shots/s296_larger_external_renderer_job_preview/gallery/publish_logs/http_stdout.log`
- `build/shots/s296_larger_external_renderer_job_preview/gallery/publish_logs/http_stderr.log`
- `build/shots/s296_larger_external_renderer_job_preview/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s296_larger_external_renderer_job_preview/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public larger-job preview smoke test. Keep S292 active
as the full32 Blender render proof endpoint, then run a Blender adapter dry-run
from S295.
