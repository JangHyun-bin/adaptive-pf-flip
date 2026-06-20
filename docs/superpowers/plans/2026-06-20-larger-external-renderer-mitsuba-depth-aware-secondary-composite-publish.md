# S343 Mitsuba Depth-Aware Composite C3 Publish

## Goal

Publish the validated S341/S342 depth-aware composite C3 gallery as the current
external visual review endpoint.

## Scope

- Reuse `tools/publish_cinematic_gallery.py`.
- Serve `build/shots/s341_mitsuba_depth_aware_composite_c3/gallery`.
- Start a local HTTP server and Cloudflare quick tunnel.
- Record HTTP checks for the gallery index and GIF.
- Keep the publish manifest under ignored `build/` output and commit the
  markdown report plus roadmap status.

## Command

```powershell
python tools\publish_cinematic_gallery.py `
  build\shots\s341_mitsuba_depth_aware_composite_c3\gallery `
  --port 8943 `
  --cftunnel `
  --manifest build\shots\s343_mitsuba_depth_aware_composite_c3_publish\publish_manifest.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_publish_s343.md `
  --timeout-seconds 90
```

## Result

- Status: `running`
- Local URL: `http://127.0.0.1:8943`
- Public URL: `https://itself-auburn-steering-collectables.trycloudflare.com`
- Manifest:
  `build/shots/s343_mitsuba_depth_aware_composite_c3_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_publish_s343.md`
- HTTP server PID: `153272`
- Cloudflared PID: `37812`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8943/index.html` | `GET` | 200 | 3456 |
| `http://127.0.0.1:8943/assets/shot.gif` | `HEAD` | 200 | 2881913 |
| `https://itself-auburn-steering-collectables.trycloudflare.com/index.html` | `GET` | 200 | 3456 |
| `https://itself-auburn-steering-collectables.trycloudflare.com/assets/shot.gif` | `HEAD` | 200 | 2881913 |

## Decision

S343 makes S341 C3 the current externally reviewable depth-aware composite
baseline. The Cloudflare quick-tunnel URL is session-scoped; refresh this
publish step if the recorded processes exit or the machine restarts.

## Next

Continue toward a renderer-native depth/secondary pass that can reproduce or
beat the S341 C3 post-render bridge without relying on the screen-space
contract layer as the final composite source.
