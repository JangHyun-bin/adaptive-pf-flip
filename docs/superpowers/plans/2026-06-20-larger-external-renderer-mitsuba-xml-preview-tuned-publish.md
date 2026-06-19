# S317 Larger External Renderer Mitsuba XML Tuned Preview Publish

## Goal

Publish the S316 tuned Mitsuba XML geometry preview gallery for remote review.

## Scope

- Stop the old S315 preview quick tunnel.
- Serve `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery`.
- Use local port `8904`.
- Start a new Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S306 active separately as the full48 Blender render endpoint.

## Result

- Stopped S315 PIDs: `156892`, `112016`
- Local URL: `http://127.0.0.1:8904`
- Public URL: `https://became-dodge-personal-thoroughly.trycloudflare.com`
- Manifest:
  `build/shots/s317_larger_external_renderer_mitsuba_xml_preview_tuned_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_tuned_publish_s317.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `157712`
- Cloudflared PID: `130076`

## Decision

S317 supersedes S315 as the public non-Blender XML geometry preview endpoint.
It does not replace S306; S306 remains the public full48 Blender render proof.

## Next

Use S317 for remote geometry review, then install Mitsuba or connect another
offline renderer backend for physically rendered non-Blender frames.
