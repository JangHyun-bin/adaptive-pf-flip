# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T19:19:48Z`
Gallery directory: `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery`
Manifest: `build/shots/s507_mitsuba_xml_backend_command_adapter_publish/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8927`
- Public: `https://deaths-hood-voted-moss.trycloudflare.com`

## Processes

- HTTP server PID: `95964`
- cloudflared PID: `21008`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8927/index.html` | `GET` | 200 | 3380 |
| `http://127.0.0.1:8927/assets/shot.gif` | `HEAD` | 200 | 1083586 |
| `https://deaths-hood-voted-moss.trycloudflare.com/index.html` | `GET` | 200 | 3380 |
| `https://deaths-hood-voted-moss.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 1083586 |

## Logs

- `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery/publish_logs/http_stdout.log`
- `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery/publish_logs/http_stderr.log`
- `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery/publish_logs/cloudflared_stderr.log`
