# S278 External Bundle Motion Preview Publish

## Goal

Replace the S276/S275 lightweight preview endpoint with the higher-resolution
S277 external-bundle motion preview gallery.

## Scope

- Stop the S276 preview quick tunnel.
- Serve `build/shots/s277_external_bundle_motion_preview/gallery`.
- Use local port `8901`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep the S270/S269 accepted gallery endpoint active separately.

## Result

- Stopped S276 PIDs: `155524`, `81420`
- Local URL: `http://127.0.0.1:8901`
- Public URL: `https://concord-extensions-dial-conduct.trycloudflare.com`
- Manifest:
  `build/shots/s278_external_bundle_motion_preview_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_external_bundle_motion_preview_publish_s278.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `78452`
- Cloudflared PID: `75712`

## Decision

S278 supersedes S276 as the current lightweight external-render handoff preview
endpoint. The S270/S269 accepted bridge-render gallery endpoint remains active.

## Next

Use S278 for quick external-bundle motion review and S270/S269 for accepted
bridge-render visual review. The next engineering step can move to larger-shot
or benchmark gates using the S273/S277 path.
