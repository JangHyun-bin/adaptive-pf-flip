# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T19:38:32Z`
Gallery directory: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery`
Manifest: `build/shots/s516_mitsuba_secondary_masked_full48_spp4_publish/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8947`
- Public: `https://laura-favorites-happiness-occasional.trycloudflare.com`

## Processes

- HTTP server PID: `77480`
- cloudflared PID: `127876`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8947/index.html` | `GET` | 200 | 3401 |
| `http://127.0.0.1:8947/assets/shot.gif` | `HEAD` | 200 | 7162433 |
| `https://laura-favorites-happiness-occasional.trycloudflare.com/index.html` | `GET` | 200 | 3401 |
| `https://laura-favorites-happiness-occasional.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 7162433 |

## Logs

- `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery/publish_logs/http_stdout.log`
- `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery/publish_logs/http_stderr.log`
- `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery/publish_logs/cloudflared_stderr.log`
