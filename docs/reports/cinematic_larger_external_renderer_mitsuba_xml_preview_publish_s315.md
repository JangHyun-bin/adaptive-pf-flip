# Cinematic Gallery Publish Report

Generated UTC: `2026-06-19T22:21:27Z`
Gallery directory: `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery`
Manifest: `build/shots/s315_larger_external_renderer_mitsuba_xml_preview_publish/publish_manifest.json`

## URLs

- Local: `http://127.0.0.1:8904`
- Public: `https://assign-pig-beauty-lots.trycloudflare.com`

## Processes

- HTTP server PID: `112016`
- cloudflared PID: `156892`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8904/index.html` | `GET` | 200 | 4162 |
| `http://127.0.0.1:8904/assets/shot.gif` | `HEAD` | 200 | 1254704 |
| `https://assign-pig-beauty-lots.trycloudflare.com/index.html` | `GET` | 200 | 4162 |
| `https://assign-pig-beauty-lots.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 1254704 |

## Logs

- `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery/publish_logs/http_stdout.log`
- `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery/publish_logs/http_stderr.log`
- `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery/publish_logs/cloudflared_stderr.log`

## Next

Use this endpoint as the public non-Blender XML geometry preview. Keep the S306
full48 Blender endpoint active separately as the rendered-water proof.
