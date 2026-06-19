# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T19:37:28Z`
Gallery directory: `build/shots/s269_secondary_dewarm_acceptance/gallery`
Manifest: `build/shots/s270_s269_gallery_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8900`
- Public: `https://rfc-empirical-match-outstanding.trycloudflare.com`

## Processes

- HTTP server PID: `47044`
- cloudflared PID: `98144`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8900/index.html` | `GET` | 200 | 6682 |
| `http://127.0.0.1:8900/assets/shot.gif` | `HEAD` | 200 | 5118717 |
| `https://rfc-empirical-match-outstanding.trycloudflare.com/index.html` | `GET` | 200 | 6682 |
| `https://rfc-empirical-match-outstanding.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 5118717 |

## Logs

- `build/shots/s269_secondary_dewarm_acceptance/gallery/publish_logs/http_stdout.log`
- `build/shots/s269_secondary_dewarm_acceptance/gallery/publish_logs/http_stderr.log`
- `build/shots/s269_secondary_dewarm_acceptance/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s269_secondary_dewarm_acceptance/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint for S269 external review. Refresh the quick tunnel if either
recorded process exits.
