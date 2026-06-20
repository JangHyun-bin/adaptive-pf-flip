# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T20:39:11Z`
Gallery directory: `build/shots/s549_mitsuba_s515_full48_low_frequency_compare/gallery`
Manifest: `build/shots/s550_mitsuba_s515_full48_low_frequency_compare_publish/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8959`
- Public: `https://certification-portland-processes-translated.trycloudflare.com`

## Processes

- HTTP server PID: `109868`
- cloudflared PID: `73816`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8959/index.html` | `GET` | 200 | 4204 |
| `http://127.0.0.1:8959/assets/shot.gif` | `HEAD` | 200 | 7685509 |
| `https://certification-portland-processes-translated.trycloudflare.com/index.html` | `GET` | 200 | 4204 |
| `https://certification-portland-processes-translated.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 7685509 |

## Logs

- `build/shots/s549_mitsuba_s515_full48_low_frequency_compare/gallery/publish_logs/http_stdout.log`
- `build/shots/s549_mitsuba_s515_full48_low_frequency_compare/gallery/publish_logs/http_stderr.log`
- `build/shots/s549_mitsuba_s515_full48_low_frequency_compare/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s549_mitsuba_s515_full48_low_frequency_compare/gallery/publish_logs/cloudflared_stderr.log`
