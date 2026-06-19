# S315 Larger External Renderer Mitsuba XML Preview Publish

## Goal

Publish the S314 Mitsuba XML geometry preview gallery for remote visual review.

## Scope

- Serve `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery`.
- Use local port `8904`.
- Start a Cloudflare quick tunnel.
- Record publish manifest and Markdown report.
- Verify local and public `index.html`.
- Verify local and public `assets/shot.gif`.
- Keep S306 active separately as the full48 Blender render endpoint.

## Result

- Local URL: `http://127.0.0.1:8904`
- Public URL: `https://assign-pig-beauty-lots.trycloudflare.com`
- Manifest:
  `build/shots/s315_larger_external_renderer_mitsuba_xml_preview_publish/publish_manifest.json`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_publish_s315.md`
- Local `index.html`: HTTP `200`
- Local `assets/shot.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`
- HTTP server PID: `112016`
- Cloudflared PID: `156892`

## Decision

S315 is the public endpoint for the non-Blender XML geometry preview. It does
not replace S306; S306 remains the public full48 Blender render proof.

## Next

Use S315 for remote geometry review, then install Mitsuba or implement another
renderer backend to turn S312 XML scenes into physically rendered frames.
