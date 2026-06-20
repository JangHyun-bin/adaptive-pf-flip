# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T10:43:51Z`
Gallery directory: `build/shots/s419_mitsuba_water_mesh_response_compare/gallery`
Manifest: `build/shots/s419_mitsuba_water_mesh_response_compare_publish/publish_manifest.json`
GIF asset: `assets/comparison.gif`

## URLs

- Local: `http://127.0.0.1:8940`
- Public: `https://junction-start-consistency-worldcat.trycloudflare.com`

## Processes

- HTTP server PID: `57056`
- cloudflared PID: `162456`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8940/index.html` | `GET` | 200 | 4760 |
| `http://127.0.0.1:8940/assets/comparison.gif` | `HEAD` | 200 | 17294396 |
| `https://junction-start-consistency-worldcat.trycloudflare.com/index.html` | `GET` | 200 | 4760 |
| `https://junction-start-consistency-worldcat.trycloudflare.com/assets/comparison.gif` | `HEAD` | 200 | 17294396 |

## Logs

- `build/shots/s419_mitsuba_water_mesh_response_compare/gallery/publish_logs/http_stdout.log`
- `build/shots/s419_mitsuba_water_mesh_response_compare/gallery/publish_logs/http_stderr.log`
- `build/shots/s419_mitsuba_water_mesh_response_compare/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s419_mitsuba_water_mesh_response_compare/gallery/publish_logs/cloudflared_stderr.log`
