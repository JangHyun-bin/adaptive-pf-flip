# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T21:05:57Z`
Gallery directory: `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery`
Manifest: `build/shots/s563_mitsuba_s515_full48_t4_backend_process_stub_publish/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8980`
- Public: `https://passport-ground-excerpt-equipped.trycloudflare.com`

## Processes

- HTTP server PID: `100560`
- cloudflared PID: `89276`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8980/index.html` | `GET` | 200 | 4114 |
| `http://127.0.0.1:8980/assets/shot.gif` | `HEAD` | 200 | 7108171 |
| `https://passport-ground-excerpt-equipped.trycloudflare.com/index.html` | `GET` | 200 | 4114 |
| `https://passport-ground-excerpt-equipped.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 7108171 |

## Logs

- `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/publish_logs/http_stdout.log`
- `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/publish_logs/http_stderr.log`
- `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/publish_logs/cloudflared_stderr.log`
