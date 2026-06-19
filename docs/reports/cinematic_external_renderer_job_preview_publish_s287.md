# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T20:39:16Z`
Gallery directory: `build/shots/s286_external_renderer_job_preview/gallery`
Manifest: `build/shots/s287_external_renderer_job_preview_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8902`
- Public: `https://installations-uni-tiger-nov.trycloudflare.com`

## Processes

- HTTP server PID: `61388`
- cloudflared PID: `153412`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8902/index.html` | `GET` | 200 | 4172 |
| `http://127.0.0.1:8902/assets/shot.gif` | `HEAD` | 200 | 393813 |
| `https://installations-uni-tiger-nov.trycloudflare.com/index.html` | `GET` | 200 | 4172 |
| `https://installations-uni-tiger-nov.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 393813 |

## Logs

- `build/shots/s286_external_renderer_job_preview/gallery/publish_logs/http_stdout.log`
- `build/shots/s286_external_renderer_job_preview/gallery/publish_logs/http_stderr.log`
- `build/shots/s286_external_renderer_job_preview/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s286_external_renderer_job_preview/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public smoke test for S285 external renderer jobs. Keep
the S283 accepted bridge review endpoint and the S281 external-bundle benchmark
preview endpoint active separately.
