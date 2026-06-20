# Larger External Renderer: Mitsuba Source Response Profile Publish

Status: complete

## Goal

Publish the S401 CR21 source-response profile gallery through a Cloudflare quick
tunnel so the current visual baseline can be inspected externally.

## Artifact

- Gallery: `build/shots/s401_mitsuba_source_response_profile_cr21/gallery/index.html`
- Publish manifest: `build/shots/s402_mitsuba_source_response_profile_cr21_publish/publish_manifest.json`
- Public URL: `https://leone-southwest-prot-newer.trycloudflare.com/index.html`

## Validation

- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`

## Notes

The quick-tunnel URL is session-scoped. Refresh the publish step if the recorded
HTTP server or `cloudflared` process exits.
