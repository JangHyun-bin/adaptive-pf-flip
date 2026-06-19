# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T12:39:49Z`
Gallery directory: `build/shots/s224_wide_accepted_review/gallery`
Manifest: `build/shots/s224_wide_accepted_review/gallery_publish_s225_manifest.json`

## URLs

- Local: `http://127.0.0.1:18899`
- Public: `https://acdbentity-greetings-reflects-win.trycloudflare.com`

## Processes

- HTTP server PID: `104264`
- cloudflared PID: `161692`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:18899/index.html` | `GET` | 200 | 6654 |
| `http://127.0.0.1:18899/assets/shot.gif` | `HEAD` | 200 | 2728758 |
| `https://acdbentity-greetings-reflects-win.trycloudflare.com/index.html` | `GET` | 200 | 6654 |
| `https://acdbentity-greetings-reflects-win.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 2728758 |

Additional public asset checks:

- `https://acdbentity-greetings-reflects-win.trycloudflare.com/assets/comparison.png`: HTTP `200`, `1783120` bytes
- `https://acdbentity-greetings-reflects-win.trycloudflare.com/assets/keyframe_00.png`: HTTP `200`, `288157` bytes

## Logs

- `build/shots/s224_wide_accepted_review/gallery/publish_logs/http_stdout.log`
- `build/shots/s224_wide_accepted_review/gallery/publish_logs/http_stderr.log`
- `build/shots/s224_wide_accepted_review/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s224_wide_accepted_review/gallery/publish_logs/cloudflared_stderr.log`
