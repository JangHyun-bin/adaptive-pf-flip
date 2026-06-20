# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T08:23:51Z`
Gallery directory: `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery`
Manifest: `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21_publish/publish_manifest.json`
GIF asset: `assets/comparison.gif`

## URLs

- Local: `http://127.0.0.1:8911`
- Public: `https://scholar-page-wednesday-soviet.trycloudflare.com`

## Processes

- HTTP server PID: `119528`
- cloudflared PID: `134076`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8911/index.html` | `GET` | 200 | 4355 |
| `http://127.0.0.1:8911/assets/comparison.gif` | `HEAD` | 200 | 11030179 |
| `https://scholar-page-wednesday-soviet.trycloudflare.com/index.html` | `GET` | 200 | 4355 |
| `https://scholar-page-wednesday-soviet.trycloudflare.com/assets/comparison.gif` | `HEAD` | 200 | 11030179 |

## Logs

- `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery/publish_logs/http_stdout.log`
- `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery/publish_logs/http_stderr.log`
- `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery/publish_logs/cloudflared_stderr.log`
