# S277 External Bundle Motion Preview

## Goal

Upgrade the external-bundle preview path to a higher-resolution 16-frame motion
review and make bundle preview rendering memory-friendlier.

## Scope

- Update `tools/cinematic_render_stub.py` so external-bundle mode lazily loads
  one selected frame at a time.
- Render S273 bundle preview at `16` frames and `960 x 540`.
- Assemble a GIF.
- Build a preview gallery with `8` sampled keyframes.
- Record render/gallery evidence.

## Validation

- Script compile:
  `python -m py_compile tools/cinematic_render_stub.py`
- Preview render:
  `python tools/cinematic_render_stub.py build/shots/s273_external_render_bundle/external_render_bundle.json build/shots/s277_external_bundle_motion_preview/preview --frames 16 --width 960 --height 540 --min-occupancy 0.01 --secondary-channel all`
- GIF assembly:
  `python tools/assemble_frames.py build/shots/s277_external_bundle_motion_preview/preview build/shots/s277_external_bundle_motion_preview/preview.gif --fps 8`
- Gallery build:
  `python tools/build_preview_gallery.py --render-summary build/shots/s277_external_bundle_motion_preview/preview/render_summary.json --gif build/shots/s277_external_bundle_motion_preview/preview.gif --preview-dir build/shots/s277_external_bundle_motion_preview/preview --out build/shots/s277_external_bundle_motion_preview/gallery --title "S277 External Bundle Motion Preview" --keyframes 8 --report docs/reports/cinematic_external_bundle_motion_preview_gallery_s277.md --next "Use this 16-frame high-resolution preview as the preferred lightweight external-render handoff view before heavier larger-shot or Blender work."`
- JSON validation:
  `python -m json.tool build/shots/s277_external_bundle_motion_preview/preview/render_summary.json`
  `python -m json.tool build/shots/s277_external_bundle_motion_preview/gallery/gallery_manifest.json`

## Result

- Frames: `16`
- Resolution: `960 x 540`
- Minimum occupancy: `0.05804398148148148`
- Required minimum occupancy: `0.01`
- Gallery assets: `9`
- Missing assets: `0`

## Decision

S277 is the preferred lightweight external-render handoff preview. It gives
better motion visibility than S275 while keeping the path much cheaper than a
full Blender render.

## Next

Publish the S277 gallery through the preview quick tunnel, replacing the S276
S275 preview endpoint.
