# Cinematic Gallery Publish Report

Generated UTC: `2026-06-21T00:16:27Z`
Gallery directory: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery`
Manifest: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery_publish_s606_manifest.json`
GIF asset: `assets/shot.gif`

## URLs

- Local: `http://127.0.0.1:8991`
- Public: `n/a`

## Processes

- HTTP server PID: `44732`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8991/index.html` | `GET` | 200 | 4668 |
| `http://127.0.0.1:8991/assets/shot.gif` | `HEAD` | 200 | 13701804 |

## Cloudflare Quick Tunnel

Two `--cftunnel` attempts were made before falling back to local publish. Both
failed while requesting a new quick tunnel from `trycloudflare.com`, before a
public URL was issued:

- `2026-06-21T00:12:03Z`: Cloudflare quick tunnel response returned HTTP `500`
  with error code `1101`.
- `2026-06-21T00:14:10Z`: Cloudflare quick tunnel response returned HTTP `500`
  with error code `1101`.

The local gallery itself is valid and verified by the HTTP checks above. Retry
public publishing when Cloudflare quick tunnel issuance is healthy, or switch
to a named tunnel if a stable public URL is required.

## Logs

- `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery/publish_logs/http_stdout.log`
- `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery/publish_logs/http_stderr.log`
- `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery/publish_logs/cloudflared_stdout.log`
- `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/sequence_compare_s577_s585_s602_s603/gallery/publish_logs/cloudflared_stderr.log`
