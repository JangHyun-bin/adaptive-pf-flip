# S276 External Bundle Preview Publish

## Goal

Publish the S275 lightweight external-bundle preview gallery through a separate
Cloudflare quick tunnel without replacing the S269 accepted gallery endpoint.

## Scope

- Serve `build/shots/s275_external_bundle_preview_gallery/gallery`.
- Use local port `8901`.
- Start a separate Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.

## Result

- Local URL: `http://127.0.0.1:8901`
- Public URL: `https://broken-textile-compared-rebound.trycloudflare.com`
- Manifest:
  `build/shots/s276_external_bundle_preview_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_external_bundle_preview_publish_s276.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `81420`
- Cloudflared PID: `155524`

## Decision

S276 is the current lightweight external-render handoff preview endpoint. The
S270/S269 accepted gallery endpoint remains active separately.

## Next

Use S276 for quick visual inspection of the external-bundle path, and use the
S270/S269 accepted gallery for the higher-quality bridge-render review.
