# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T10:08:42Z`
Gallery directory: `build/shots/s416_mitsuba_water_patch_compare/gallery`
Manifest: `build/shots/s416_mitsuba_water_patch_compare_publish/publish_manifest.json`
GIF asset: `assets/comparison.gif`

## URLs

- Local: `http://127.0.0.1:8936`
- Public: `https://full-fuji-tone-vii.trycloudflare.com`

## Processes

- HTTP server PID: `26120`
- cloudflared PID: `82480`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8936/index.html` | `GET` | 200 | 4559 |
| `http://127.0.0.1:8936/assets/comparison.gif` | `HEAD` | 200 | 14923502 |
| `https://full-fuji-tone-vii.trycloudflare.com/index.html` | `GET` | 200 | 4559 |
| `https://full-fuji-tone-vii.trycloudflare.com/assets/comparison.gif` | `HEAD` | 200 | 14923502 |

## Logs

- `build/shots/s416_mitsuba_water_patch_compare/gallery/publish_logs/http_stdout.log`
- `build/shots/s416_mitsuba_water_patch_compare/gallery/publish_logs/http_stderr.log`
- `build/shots/s416_mitsuba_water_patch_compare/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s416_mitsuba_water_patch_compare/gallery/publish_logs/cloudflared_stderr.log`
