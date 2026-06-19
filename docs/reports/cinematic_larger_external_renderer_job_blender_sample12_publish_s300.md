# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T21:20:43Z`
Gallery directory: `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery`
Manifest: `build/shots/s300_larger_external_renderer_job_blender_sample12_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8903`
- Public: `https://vatican-ranking-laden-slip.trycloudflare.com`

## Processes

- HTTP server PID: `60752`
- cloudflared PID: `60408`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8903/index.html` | `GET` | 200 | 6725 |
| `http://127.0.0.1:8903/assets/shot.gif` | `HEAD` | 200 | 4277864 |
| `https://vatican-ranking-laden-slip.trycloudflare.com/index.html` | `GET` | 200 | 6725 |
| `https://vatican-ranking-laden-slip.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 4277864 |

## Logs

- `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/publish_logs/http_stdout.log`
- `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/publish_logs/http_stderr.log`
- `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s299_larger_external_renderer_job_blender_sample12/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public larger-job Blender sample proof. Keep S292
active separately as the full32 job-path proof, then package S299/S300 or scale
the larger-job Blender render length.
