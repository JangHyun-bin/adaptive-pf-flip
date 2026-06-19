# S320 Larger External Renderer Mitsuba Render Gallery Publish

## Goal

Make the actual Mitsuba render probe inspectable through the same durable
gallery and Cloudflare tunnel workflow used by the cinematic preview pipeline.

## Changes

- Add `tools/build_mitsuba_render_gallery.py`.
- Read `lsfs_mitsuba_xml_render` manifests from S319.
- Copy PNG preview frames into a static gallery.
- Assemble `assets/shot.gif` from actual Mitsuba PNG previews.
- Copy render/export manifests as gallery metadata.
- Publish the gallery with `tools/publish_cinematic_gallery.py --cftunnel`.

## Outputs

- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_render_gallery_s320.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_render_gallery_publish_s320.md`
- Gallery manifest:
  `build/shots/s320_larger_external_renderer_mitsuba_render_gallery/gallery/gallery_manifest.json`
- Publish manifest:
  `build/shots/s320_larger_external_renderer_mitsuba_render_gallery_publish/publish_manifest.json`
- Public URL:
  `https://ordinary-millions-analytical-lib.trycloudflare.com`

## Verification

- `python -m py_compile tools/build_mitsuba_render_gallery.py`
- `python tools/build_mitsuba_render_gallery.py ...`
- `python tools/publish_cinematic_gallery.py ... --cftunnel`
- Public checks:
  - `GET /index.html` returned `200`, `3165` bytes.
  - `HEAD /assets/shot.gif` returned `200`, `165682` bytes.

## Result

S320 publishes the first externally shareable gallery built from actual Mitsuba
renderer output. The visual is still a `3` frame, `spp=1` probe, so it should be
treated as a runtime proof rather than final look development.

## Next

Improve the actual Mitsuba visual framing/materials, then run a longer frame
range at higher spp and package that as the next renderer proof.
