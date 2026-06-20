# S390 Larger External Renderer Mitsuba Response Crop Review Publish

## Goal

Publish the S389 CR21 crop/zoom review gallery through a Cloudflare quick tunnel
so the current visual baseline can be inspected outside the local filesystem.

## Work

- Extended `tools/publish_cinematic_gallery.py` with `--gif-name`, keeping the
  default `shot.gif` behavior for existing galleries.
- Published the S389 gallery with `assets/crop_review.gif`.
- Verified both local and public endpoints for the index page and GIF asset.

## Result

- Public URL:
  `https://hardcover-avatar-arbitration-physician.trycloudflare.com/index.html`
- Local URL:
  `http://127.0.0.1:8921`
- Publish manifest:
  `build/shots/s390_s389_crop_review_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_response_crop_review_publish_s390.md`
- HTTP server PID: `75084`
- Cloudflared PID: `103340`

## Checks

| Target | Method | Status | Bytes |
| --- | --- | ---: | ---: |
| `http://127.0.0.1:8921/index.html` | `GET` | `200` | `4338` |
| `http://127.0.0.1:8921/assets/crop_review.gif` | `HEAD` | `200` | `8922104` |
| `https://hardcover-avatar-arbitration-physician.trycloudflare.com/index.html` | `GET` | `200` | `4338` |
| `https://hardcover-avatar-arbitration-physician.trycloudflare.com/assets/crop_review.gif` | `HEAD` | `200` | `8922104` |

## Decision

Use this endpoint for CR21 crop review while the quick-tunnel processes remain
alive. The URL is session-scoped, so refresh it if the process exits or the
machine restarts. Next work should move CR21 from a post-composite response into
renderer/material parameters, because the crop review is now externally
inspectable.
