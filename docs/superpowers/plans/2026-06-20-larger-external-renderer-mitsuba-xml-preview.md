# S314 Larger External Renderer Mitsuba XML Preview

## Goal

Create a visual preview path for the validated Mitsuba XML geometry before a
Mitsuba executable is available.

## Scope

- Add `tools/preview_mitsuba_xml_export.py`.
- Read `lsfs_mitsuba_xml_export` manifests.
- Parse Mitsuba XML scenes.
- Draw water OBJ vertices and proxy sphere geometry into 2D top-down PNG
  frames.
- Generate a full48 PNG sequence from the S312 phase-proxy XML export.
- Assemble the PNG sequence into a GIF.
- Build a static gallery for local review.

## Result

- Tool:
  `tools/preview_mitsuba_xml_export.py`
- Preview summary:
  `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/frames/render_summary.json`
- Preview report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_s314.md`
- GIF:
  `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/preview.gif`
- Gallery:
  `build/shots/s314_larger_external_renderer_mitsuba_xml_preview/gallery/index.html`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_gallery_s314.md`
- Frames: `48`
- Resolution: `960 x 540`
- Projection: `xz_topdown`
- Minimum occupancy: `0.07859760802469136`
- Total sphere shapes: `7680`
- Max water vertices per frame: `7000`
- GIF size: `1254704` bytes

## Verification

- `python -m py_compile tools/preview_mitsuba_xml_export.py`
- S314 preview command completed with status `ok`.
- `tools/assemble_frames.py` produced the preview GIF from `48` frames.
- `tools/build_preview_gallery.py` produced the static gallery.
- `python -m json.tool` accepted the preview summary and gallery manifest.
- Visual inspection of `frame_0047.png` showed nonblank geometry distribution.

## Decision

S314 gives the non-Blender XML export an inspectable visual artifact even before
Mitsuba is installed. This is not a physically rendered image; it is a geometry
preview that verifies water/proxy spatial content from the XML bundle.

## Next

Publish the S314 gallery for remote review, or install Mitsuba and render the
validated S312 XML scenes.
