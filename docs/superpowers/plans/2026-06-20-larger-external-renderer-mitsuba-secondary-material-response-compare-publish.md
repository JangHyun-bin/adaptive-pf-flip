# S393 Larger External Renderer Mitsuba Secondary Material Response Compare Publish

## Goal

Publish the S392 Target/C1E/SS1/S391_CR21_Material comparison gallery through a
Cloudflare quick tunnel for external visual review.

## Work

- Published `build/shots/s392_mitsuba_secondary_material_cr21_compare/gallery`.
- Used `assets/comparison.gif` as the gallery GIF asset.
- Verified local and public index/GIF responses.

## Result

- Public URL:
  `https://fashion-adapters-careers-active.trycloudflare.com/index.html`
- Local URL:
  `http://127.0.0.1:8922`
- Publish manifest:
  `build/shots/s393_mitsuba_secondary_material_cr21_compare_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_cr21_compare_publish_s393.md`
- HTTP server PID: `150364`
- Cloudflared PID: `155332`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8922/index.html` | `GET` | `200` | `3195` |
| `http://127.0.0.1:8922/assets/comparison.gif` | `HEAD` | `200` | `3645319` |
| `https://fashion-adapters-careers-active.trycloudflare.com/index.html` | `GET` | `200` | `3195` |
| `https://fashion-adapters-careers-active.trycloudflare.com/assets/comparison.gif` | `HEAD` | `200` | `3645319` |

## Decision

Use this endpoint for SS1 vs CR21 material-profile review while the quick-tunnel
processes remain alive. The URL is session-scoped, so refresh it if either
recorded process exits. Next work should tune or sweep the renderer-side
reflectance/opacity response against the target-gap harness.
