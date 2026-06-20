# Cinematic Gallery Publish Report

Generated UTC: `2026-06-20T22:56:34Z`
Gallery directory: `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery`
Manifest: `build/shots/s593_mitsuba_renderer_scene_depth_material_backend_output_compare_publish/publish_manifest.json`
GIF asset: `assets/backend_compare_strips.gif`

## URLs

- Local: `http://127.0.0.1:8808`
- Public: `https://outputs-murray-phil-beads.trycloudflare.com`

## Processes

- HTTP server PID: `167640`
- cloudflared PID: `155216`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8808/index.html` | `GET` | 200 | 3127 |
| `http://127.0.0.1:8808/assets/backend_compare_strips.gif` | `HEAD` | 200 | 30572999 |
| `https://outputs-murray-phil-beads.trycloudflare.com/index.html` | `GET` | 200 | 3127 |
| `https://outputs-murray-phil-beads.trycloudflare.com/assets/backend_compare_strips.gif` | `HEAD` | 200 | 30572999 |

## Logs

- `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/publish_logs/http_stdout.log`
- `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/publish_logs/http_stderr.log`
- `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s592_mitsuba_renderer_scene_depth_material_backend_output_compare/gallery/publish_logs/cloudflared_stderr.log`
