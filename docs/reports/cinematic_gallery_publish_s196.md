# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T09:31:47Z`
Gallery directory: `build/shots/s195_water_mesh_smoothing_strong/gallery`
Manifest: `build/shots/s195_water_mesh_smoothing_strong/gallery_publish_s196_manifest.json`

## URLs

- Local: `http://127.0.0.1:8835`
- Public: `https://dicke-automotive-fitness-category.trycloudflare.com`

## Processes

- HTTP server PID: `96544`
- cloudflared PID: `87180`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8835/index.html` | `GET` | 200 | 5518 |
| `http://127.0.0.1:8835/assets/shot.gif` | `HEAD` | 200 | 23417683 |
| `https://dicke-automotive-fitness-category.trycloudflare.com/index.html` | `GET` | 200 | 5518 |
| `https://dicke-automotive-fitness-category.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 23417683 |

Additional public asset checks:

- `https://dicke-automotive-fitness-category.trycloudflare.com/assets/comparison.png`: HTTP `200`, `2260139` bytes
- `https://dicke-automotive-fitness-category.trycloudflare.com/assets/keyframe_00.png`: HTTP `200`, `1131832` bytes

## Logs

- `build/shots/s195_water_mesh_smoothing_strong/gallery/publish_logs/http_stdout.log`
- `build/shots/s195_water_mesh_smoothing_strong/gallery/publish_logs/http_stderr.log`
- `build/shots/s195_water_mesh_smoothing_strong/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s195_water_mesh_smoothing_strong/gallery/publish_logs/cloudflared_stderr.log`
