# S277 External Bundle Motion Preview

Generated UTC: `2026-06-19T20:00:21Z`

## Goal

Promote the S274 external-bundle visual smoke path from a small 8-frame preview
to a more useful 16-frame 960 x 540 motion preview.

## Tool Change

`tools/cinematic_render_stub.py` now renders external-bundle inputs lazily:
each selected bundle frame is loaded, rendered, and released before the next
frame is read. This avoids retaining the selected particle/phase CSV payloads
in memory and makes larger preview windows safer.

## Commands

```powershell
python tools\cinematic_render_stub.py build\shots\s273_external_render_bundle\external_render_bundle.json build\shots\s277_external_bundle_motion_preview\preview --frames 16 --width 960 --height 540 --min-occupancy 0.01 --secondary-channel all
python tools\assemble_frames.py build\shots\s277_external_bundle_motion_preview\preview build\shots\s277_external_bundle_motion_preview\preview.gif --fps 8
python tools\build_preview_gallery.py --render-summary build\shots\s277_external_bundle_motion_preview\preview\render_summary.json --gif build\shots\s277_external_bundle_motion_preview\preview.gif --preview-dir build\shots\s277_external_bundle_motion_preview\preview --out build\shots\s277_external_bundle_motion_preview\gallery --title "S277 External Bundle Motion Preview" --keyframes 8 --report docs\reports\cinematic_external_bundle_motion_preview_gallery_s277.md --next "Use this 16-frame high-resolution preview as the preferred lightweight external-render handoff view before heavier larger-shot or Blender work."
```

## Artifacts

- Preview frames:
  `build/shots/s277_external_bundle_motion_preview/preview/frame_####.png`
- Preview GIF:
  `build/shots/s277_external_bundle_motion_preview/preview.gif`
- Render summary:
  `build/shots/s277_external_bundle_motion_preview/preview/render_summary.json`
- Gallery:
  `build/shots/s277_external_bundle_motion_preview/gallery/index.html`
- Gallery report:
  `docs/reports/cinematic_external_bundle_motion_preview_gallery_s277.md`

## Result

- Status: `ok`
- Frames: `16`
- Resolution: `960 x 540`
- Secondary channel: `all`
- Minimum occupancy: `0.05804398148148148`
- Required minimum occupancy: `0.01`
- First-frame occupancy: `0.07271219135802469`
- Mid-frame occupancy: `0.05817708333333333`
- Last-frame occupancy: `0.06622878086419753`
- First-frame secondary pixels: `2545`
- Mid-frame secondary pixels: `2283`
- Last-frame secondary pixels: `4126`
- First-frame water mesh faces: `20000`
- Last-frame water mesh faces: `22300`
- Gallery assets: `9`

## Decision

S277 supersedes S275 as the preferred lightweight external-render handoff view.
S275 remains a smaller smoke gallery; S277 is better for motion inspection.

## Next

Publish the S277 gallery through the preview handoff quick tunnel, replacing
the S276/S275 preview endpoint while keeping the S270/S269 accepted gallery
endpoint active.
