# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T08:38:27Z`
Gallery directory: `build/shots/s405_mitsuba_cr21_native_response_compare/gallery`
Manifest: `build/shots/s405_mitsuba_cr21_native_response_compare_publish/publish_manifest.json`
GIF asset: `assets/comparison.gif`

## URLs

- Local: `http://127.0.0.1:8912`
- Public: `https://decades-monitors-application-watch.trycloudflare.com`

## Processes

- HTTP server PID: `69992`
- cloudflared PID: `143384`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8912/index.html` | `GET` | 200 | 4559 |
| `http://127.0.0.1:8912/assets/comparison.gif` | `HEAD` | 200 | 13540018 |
| `https://decades-monitors-application-watch.trycloudflare.com/index.html` | `GET` | 200 | 4559 |
| `https://decades-monitors-application-watch.trycloudflare.com/assets/comparison.gif` | `HEAD` | 200 | 13540018 |

## Logs

- `build/shots/s405_mitsuba_cr21_native_response_compare/gallery/publish_logs/http_stdout.log`
- `build/shots/s405_mitsuba_cr21_native_response_compare/gallery/publish_logs/http_stderr.log`
- `build/shots/s405_mitsuba_cr21_native_response_compare/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s405_mitsuba_cr21_native_response_compare/gallery/publish_logs/cloudflared_stderr.log`
