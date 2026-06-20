# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T19:05:09Z`
Gallery directory: `build/shots/s503_mitsuba_low_frequency_backend_adapter_dry_run/gallery`
Manifest: `build/shots/s504_mitsuba_backend_adapter_dry_run_publish/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8926`
- Public: `https://harrison-wash-intake-unless.trycloudflare.com`

## Processes

- HTTP server PID: `142944`
- cloudflared PID: `69868`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8926/index.html` | `GET` | 200 | 3497 |
| `http://127.0.0.1:8926/assets/shot.gif` | `HEAD` | 200 | 1191221 |
| `https://harrison-wash-intake-unless.trycloudflare.com/index.html` | `GET` | 200 | 3497 |
| `https://harrison-wash-intake-unless.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 1191221 |

## Logs

- `build/shots/s503_mitsuba_low_frequency_backend_adapter_dry_run/gallery/publish_logs/http_stdout.log`
- `build/shots/s503_mitsuba_low_frequency_backend_adapter_dry_run/gallery/publish_logs/http_stderr.log`
- `build/shots/s503_mitsuba_low_frequency_backend_adapter_dry_run/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s503_mitsuba_low_frequency_backend_adapter_dry_run/gallery/publish_logs/cloudflared_stderr.log`
