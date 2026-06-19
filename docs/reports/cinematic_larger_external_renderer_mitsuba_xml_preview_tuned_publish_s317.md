# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T22:28:35Z`
Gallery directory: `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery`
Manifest: `build/shots/s317_larger_external_renderer_mitsuba_xml_preview_tuned_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8904`
- Public: `https://became-dodge-personal-thoroughly.trycloudflare.com`

## Processes

- HTTP server PID: `157712`
- cloudflared PID: `130076`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8904/index.html` | `GET` | 200 | 4174 |
| `http://127.0.0.1:8904/assets/shot.gif` | `HEAD` | 200 | 1241823 |
| `https://became-dodge-personal-thoroughly.trycloudflare.com/index.html` | `GET` | 200 | 4174 |
| `https://became-dodge-personal-thoroughly.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 1241823 |

## Logs

- `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery/publish_logs/http_stdout.log`
- `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery/publish_logs/http_stderr.log`
- `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public tuned non-Blender XML geometry preview. Keep the
S306 full48 Blender endpoint active separately as the physically rendered proof.
