# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T20:02:31Z`
Gallery directory: `build/shots/s277_external_bundle_motion_preview/gallery`
Manifest: `build/shots/s278_external_bundle_motion_preview_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8901`
- Public: `https://concord-extensions-dial-conduct.trycloudflare.com`

## Processes

- HTTP server PID: `78452`
- cloudflared PID: `75712`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8901/index.html` | `GET` | 200 | 4174 |
| `http://127.0.0.1:8901/assets/shot.gif` | `HEAD` | 200 | 393813 |
| `https://concord-extensions-dial-conduct.trycloudflare.com/index.html` | `GET` | 200 | 4174 |
| `https://concord-extensions-dial-conduct.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 393813 |

## Logs

- `build/shots/s277_external_bundle_motion_preview/gallery/publish_logs/http_stdout.log`
- `build/shots/s277_external_bundle_motion_preview/gallery/publish_logs/http_stderr.log`
- `build/shots/s277_external_bundle_motion_preview/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s277_external_bundle_motion_preview/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint for lightweight S277 external-bundle motion review. Keep the
S269 accepted gallery endpoint active for higher-quality bridge-render review.
