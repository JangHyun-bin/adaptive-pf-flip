# S274 External Bundle Preview Gate

## Goal

Make the S273 external render bundle immediately inspectable by the existing
preview renderer.

## Scope

- Extend `tools/cinematic_render_stub.py` so it accepts
  `lsfs_bridge_external_render_bundle`.
- For bundle inputs, read only the selected preview frames instead of loading
  the full accepted 32-frame particle input set.
- Use bundle water-mesh assets as the mesh overlay source when no separate
  water reconstruction index is supplied.
- Render an 8-frame 640 x 360 visual smoke preview from S273.
- Assemble the preview frames into a GIF.

## Validation

- Script compile:
  `python -m py_compile tools/cinematic_render_stub.py`
- Help output:
  `python tools/cinematic_render_stub.py --help`
- Preview render:
  `python tools/cinematic_render_stub.py build/shots/s273_external_render_bundle/external_render_bundle.json build/shots/s274_external_bundle_preview/preview --frames 8 --width 640 --height 360 --min-occupancy 0.01 --secondary-channel all`
- GIF assembly:
  `python tools/assemble_frames.py build/shots/s274_external_bundle_preview/preview build/shots/s274_external_bundle_preview/preview.gif --fps 8`
- Summary JSON validation:
  `python -m json.tool build/shots/s274_external_bundle_preview/preview/render_summary.json`

## Result

- Frames: `8`
- Resolution: `640 x 360`
- Minimum occupancy: `0.0608984375`
- Required minimum occupancy: `0.01`
- Missing preview outputs: `0`
- First-frame mesh faces: `20000`
- Last-frame mesh faces: `22300`
- First-frame secondary pixels: `1661`
- Last-frame secondary pixels: `2914`

## Decision

S274 passes. The accepted S273 external-render bundle can now drive a visual
preview directly, which gives downstream renderer and larger-shot work a fast
inspectable smoke test.

## Next

Build a lightweight static gallery around the S274 preview GIF, frames, and
summary so the external-render handoff has a shareable visual page.
