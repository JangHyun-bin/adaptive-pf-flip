# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T20:12:20Z`
Gallery directory: `build/shots/s280_external_bundle_preview_benchmark/gallery`
Manifest: `build/shots/s281_external_bundle_benchmark_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8901`
- Public: `https://roman-semester-highlighted-formatting.trycloudflare.com`

## Processes

- HTTP server PID: `127296`
- cloudflared PID: `106572`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8901/index.html` | `GET` | 200 | 4182 |
| `http://127.0.0.1:8901/assets/shot.gif` | `HEAD` | 200 | 925003 |
| `https://roman-semester-highlighted-formatting.trycloudflare.com/index.html` | `GET` | 200 | 4182 |
| `https://roman-semester-highlighted-formatting.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 925003 |

## Logs

- `build/shots/s280_external_bundle_preview_benchmark/gallery/publish_logs/http_stdout.log`
- `build/shots/s280_external_bundle_preview_benchmark/gallery/publish_logs/http_stderr.log`
- `build/shots/s280_external_bundle_preview_benchmark/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s280_external_bundle_preview_benchmark/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint for lightweight S280 external-bundle benchmark review. Keep
the S269 accepted gallery endpoint active for higher-quality bridge-render
review.
