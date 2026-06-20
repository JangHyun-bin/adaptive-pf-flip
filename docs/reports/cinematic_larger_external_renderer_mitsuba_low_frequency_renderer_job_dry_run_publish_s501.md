# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T18:52:05Z`
Gallery directory: `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery`
Manifest: `build/shots/s501_mitsuba_low_frequency_renderer_job_dry_run_publish/publish_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8942`
- Public: `https://chassis-yorkshire-email-retirement.trycloudflare.com`

## Processes

- HTTP server PID: `57872`
- cloudflared PID: `156448`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8942/index.html` | `GET` | 200 | 3298 |
| `http://127.0.0.1:8942/assets/shot.gif` | `HEAD` | 200 | 1191221 |
| `https://chassis-yorkshire-email-retirement.trycloudflare.com/index.html` | `GET` | 200 | 3298 |
| `https://chassis-yorkshire-email-retirement.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 1191221 |

## Logs

- `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery/publish_logs/http_stdout.log`
- `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery/publish_logs/http_stderr.log`
- `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the current public execution proof for the S499 renderer
job manifest dry run. The next implementation step is a backend-adapter skeleton
that consumes the same job manifest contract.
