# S322 Larger External Renderer Mitsuba Secondary Mask

## Goal

Reduce the opaque-dot read of secondary spray/foam/bubble proxy spheres in the
actual Mitsuba path, while keeping the existing scene/export contract intact.

## Changes

- Extend `tools/export_external_renderer_mitsuba_xml.py` with
  `--secondary-opacity`.
- When `--secondary-opacity` is set, wrap secondary channel diffuse BSDFs in
  Mitsuba `mask` BSDFs.
- Keep the S321 close-up camera/material setup.
- Render an `8` frame `spp=4` actual Mitsuba proof.
- Build and publish a gallery from the rendered PNG previews.

## Outputs

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_export_s322.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_validation_s322.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_render_s322.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_gallery_s322.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_masked_publish_s322.md`
- Public URL:
  `https://evaluate-inns-suppliers-wright.trycloudflare.com`

## Verification

- `python -m py_compile tools/export_external_renderer_mitsuba_xml.py tools/validate_mitsuba_xml_export.py tools/render_mitsuba_xml_export.py tools/build_mitsuba_render_gallery.py`
- `python tools/validate_mitsuba_xml_export.py ... --require-mitsuba`
- `.\\build\\s319_mitsuba_venv\\Scripts\\python.exe tools\\render_mitsuba_xml_export.py ... --frames 8 --spp 4 --write-png`
- `python tools/build_mitsuba_render_gallery.py ...`
- `python tools/publish_cinematic_gallery.py ... --cftunnel`
- Public checks:
  - `GET /index.html` returned `200`, `3388` bytes.
  - `HEAD /assets/shot.gif` returned `200`, `1289627` bytes.

## Result

S322 renders `8` selected frames at `spp=4` with `0` manifest failures and
publishes a `1.29 MB` actual Mitsuba GIF. A rejected large-radius experiment
made secondary particles read as large blue dots; the committed masked path is
less intrusive and keeps the secondary proxy contract available for further
look development.

## Next

Move beyond sphere proxies: add a renderer-side secondary representation for
mist/foam that is not encoded as opaque geometry, or export a screen-space /
volume-oriented secondary layer for the final renderer.
