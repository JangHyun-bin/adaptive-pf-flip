# S321 Larger External Renderer Mitsuba Closeup Proof

## Goal

Move the actual Mitsuba proof from a tiny runtime smoke image toward a more
readable visual review artifact.

## Changes

- Extend `tools/export_external_renderer_mitsuba_xml.py` with opt-in look-dev
  overrides:
  - `--samples`
  - `--camera-position`
  - `--camera-target`
  - `--camera-up`
  - `--camera-fov`
  - `--background-radiance`
  - `--water-alpha`
- Generate a close-up full48 XML bundle with diagnostic phase-volume proxies
  disabled and secondary particle proxies retained.
- Render an `8` frame, `spp=4` Mitsuba Python API probe.
- Build and publish a static gallery from the actual Mitsuba PNG previews.

## Outputs

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_export_s321.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_validation_s321.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_render_s321.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_gallery_s321.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_closeup_publish_s321.md`
- Public URL:
  `https://cooling-pts-cups-skating.trycloudflare.com`

## Verification

- `python -m py_compile tools/export_external_renderer_mitsuba_xml.py tools/validate_mitsuba_xml_export.py tools/render_mitsuba_xml_export.py tools/build_mitsuba_render_gallery.py`
- `python tools/validate_mitsuba_xml_export.py ... --require-mitsuba`
- `.\\build\\s319_mitsuba_venv\\Scripts\\python.exe tools\\render_mitsuba_xml_export.py ... --frames 8 --spp 4 --write-png`
- `python tools/build_mitsuba_render_gallery.py ...`
- `python tools/publish_cinematic_gallery.py ... --cftunnel`
- Public checks:
  - `GET /index.html` returned `200`, `3370` bytes.
  - `HEAD /assets/shot.gif` returned `200`, `1261101` bytes.

## Result

S321 renders `8` selected frames at `spp=4` with `0` manifest failures and
publishes a `1.26 MB` actual Mitsuba GIF. The framing is much more readable than
S319/S320, but the visual still reads as early renderer integration because the
water mesh/proxy representation is not yet final look development.

## Next

Improve renderer-side material and lighting semantics: replace proxy-style
secondary spheres with more integrated mist/foam representation, add stronger
environment lighting, and test a longer frame range at higher spp.
