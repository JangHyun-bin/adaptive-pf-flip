# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T20:26:13Z`
Gallery directory: `build/shots/s282_accepted_bridge_hires_review/gallery`
Manifest: `build/shots/s283_s282_bridge_hires_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8900`
- Public: `https://staff-held-cheese-organized.trycloudflare.com`

## Processes

- HTTP server PID: `138664`
- cloudflared PID: `38632`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8900/index.html` | `GET` | 200 | 6667 |
| `http://127.0.0.1:8900/assets/shot.gif` | `HEAD` | 200 | 11211990 |
| `https://staff-held-cheese-organized.trycloudflare.com/index.html` | `GET` | 200 | 6667 |
| `https://staff-held-cheese-organized.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 11211990 |

## Logs

- `build/shots/s282_accepted_bridge_hires_review/gallery/publish_logs/http_stdout.log`
- `build/shots/s282_accepted_bridge_hires_review/gallery/publish_logs/http_stderr.log`
- `build/shots/s282_accepted_bridge_hires_review/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s282_accepted_bridge_hires_review/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint for high-resolution S282 accepted bridge review. Keep S269 as
the accepted preset baseline and keep the S281 external-bundle benchmark preview
endpoint active separately.
