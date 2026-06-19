# S316 Larger External Renderer Mitsuba XML Tuned Preview

## Goal

Tune the Mitsuba XML geometry preview so water, phase volume, and secondary
particle proxies are easier to inspect.

## Scope

- Extend `tools/preview_mitsuba_xml_export.py` with opt-in review look controls.
- Add water alpha and water point-size controls.
- Add phase and secondary proxy scale controls.
- Add material/channel sphere counts to the preview summary.
- Add an optional frame legend.
- Generate a full48 tuned PNG sequence from the S312 XML phase-proxy export.
- Assemble the tuned PNG sequence into a GIF.
- Build a static gallery for local review.

## Result

- Updated tool:
  `tools/preview_mitsuba_xml_export.py`
- Preview summary:
  `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/frames/render_summary.json`
- Preview report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_tuned_s316.md`
- GIF:
  `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/preview.gif`
- Gallery:
  `build/shots/s316_larger_external_renderer_mitsuba_xml_preview_tuned/gallery/index.html`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_preview_tuned_gallery_s316.md`
- Frames: `48`
- Resolution: `960 x 540`
- Look: `review`
- Minimum occupancy: `0.03595293209876543`
- Total sphere shapes: `7680`
- Sphere material counts:
  `{'phase_volume': 3072, 'spray': 2937, 'foam': 1187, 'bubble': 484, 'droplet': 0}`
- Max water vertices per frame: `3600`
- GIF size: `1241823` bytes

## Verification

- `python -m py_compile tools/preview_mitsuba_xml_export.py`
- S316 preview command completed with status `ok`.
- `tools/assemble_frames.py` produced the tuned preview GIF from `48` frames.
- `tools/build_preview_gallery.py` produced the static gallery.
- `python -m json.tool` accepted the tuned preview summary and gallery manifest.
- Visual inspection of `frame_0047.png` showed channel legend and clearer proxy
  distribution.

## Decision

S316 supersedes S315 for non-Blender XML geometry review. S315 remains a useful
baseline, but S316 is the better public-review candidate.

## Next

Publish the S316 tuned gallery, then keep S306 active separately as the full48
Blender render proof endpoint.
