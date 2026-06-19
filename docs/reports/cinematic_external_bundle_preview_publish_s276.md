# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T19:56:43Z`
Gallery directory: `build/shots/s275_external_bundle_preview_gallery/gallery`
Manifest: `build/shots/s276_external_bundle_preview_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8901`
- Public: `https://broken-textile-compared-rebound.trycloudflare.com`

## Processes

- HTTP server PID: `81420`
- cloudflared PID: `155524`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8901/index.html` | `GET` | 200 | 4168 |
| `http://127.0.0.1:8901/assets/shot.gif` | `HEAD` | 200 | 107772 |
| `https://broken-textile-compared-rebound.trycloudflare.com/index.html` | `GET` | 200 | 4168 |
| `https://broken-textile-compared-rebound.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 107772 |

## Logs

- `build/shots/s275_external_bundle_preview_gallery/gallery/publish_logs/http_stdout.log`
- `build/shots/s275_external_bundle_preview_gallery/gallery/publish_logs/http_stderr.log`
- `build/shots/s275_external_bundle_preview_gallery/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s275_external_bundle_preview_gallery/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint for lightweight external-bundle visual handoff review. Keep
the S269 accepted gallery endpoint active for higher-quality bridge-render
review.
