# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T18:29:01Z`
Gallery directory: `build/shots/s496_mitsuba_low_frequency_runtime_publish_gallery/gallery`
Manifest: `build/shots/s496_mitsuba_low_frequency_runtime_publish_gallery/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8925`
- Public: `https://thanks-pending-expired-enlargement.trycloudflare.com`

## Processes

- HTTP server PID: `153572`
- cloudflared PID: `68476`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8925/index.html` | `GET` | 200 | 10349 |
| `http://127.0.0.1:8925/assets/shot.gif` | `HEAD` | 200 | 4413881 |
| `https://thanks-pending-expired-enlargement.trycloudflare.com/index.html` | `GET` | 200 | 10349 |
| `https://thanks-pending-expired-enlargement.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 4413881 |

## Logs

- `build/shots/s496_mitsuba_low_frequency_runtime_publish_gallery/gallery/publish_logs/http_stdout.log`
- `build/shots/s496_mitsuba_low_frequency_runtime_publish_gallery/gallery/publish_logs/http_stderr.log`
- `build/shots/s496_mitsuba_low_frequency_runtime_publish_gallery/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s496_mitsuba_low_frequency_runtime_publish_gallery/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the current public low-frequency runtime preview while the
next renderer-side step wires `runtime_import_preview.json` into the production
preview/export runner.
