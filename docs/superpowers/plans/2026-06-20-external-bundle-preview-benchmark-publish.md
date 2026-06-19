# S281 External Bundle Preview Benchmark Publish

## Goal

Replace the S278/S277 lightweight preview endpoint with the higher-resolution
S280 external-bundle preview benchmark gallery.

## Scope

- Stop the S278 preview quick tunnel.
- Serve `build/shots/s280_external_bundle_preview_benchmark/gallery`.
- Use local port `8901`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep the S270/S269 accepted bridge-render gallery endpoint active separately.

## Result

- Stopped S278 PIDs: `75712`, `78452`
- Local URL: `http://127.0.0.1:8901`
- Public URL: `https://roman-semester-highlighted-formatting.trycloudflare.com`
- Manifest:
  `build/shots/s281_external_bundle_benchmark_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_external_bundle_preview_benchmark_publish_s281.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `127296`
- Cloudflared PID: `106572`

## Decision

S281 supersedes S278 as the current lightweight external-render benchmark
preview endpoint. The S270/S269 accepted bridge-render gallery endpoint remains
active.

## Next

Use S281 for quick review of the bounded 24-frame 1280 x 720 external-bundle
benchmark, and use S270/S269 for accepted bridge-render review.
