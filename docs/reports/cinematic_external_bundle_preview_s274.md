# S274 External Bundle Preview Gate

Generated UTC: `2026-06-19T19:55:00Z`

## Goal

Verify that the S273 `lsfs_bridge_external_render_bundle` can directly drive a
visual preview path without going back through the original converted-sequence
entrypoint.

## Tool Change

`tools/cinematic_render_stub.py` now accepts
`lsfs_bridge_external_render_bundle` inputs. For bundle inputs it selects only
the requested preview frames before reading the large particle/phase CSV files,
so an 8-frame preview does not load the full 32-frame, 1.28 GB particle input
set.

## Command

```powershell
python tools\cinematic_render_stub.py build\shots\s273_external_render_bundle\external_render_bundle.json build\shots\s274_external_bundle_preview\preview --frames 8 --width 640 --height 360 --min-occupancy 0.01 --secondary-channel all
python tools\assemble_frames.py build\shots\s274_external_bundle_preview\preview build\shots\s274_external_bundle_preview\preview.gif --fps 8
```

## Artifacts

- Preview frames:
  `build/shots/s274_external_bundle_preview/preview/frame_####.png`
- Preview GIF:
  `build/shots/s274_external_bundle_preview/preview.gif`
- Render summary:
  `build/shots/s274_external_bundle_preview/preview/render_summary.json`

## Result

- Status: `ok`
- Frames: `8`
- Resolution: `640 x 360`
- Secondary channel: `all`
- Minimum occupancy: `0.0608984375`
- Required minimum occupancy: `0.01`
- First-frame occupancy: `0.07536024305555555`
- Last-frame occupancy: `0.07151041666666667`
- First-frame water mesh faces: `20000`
- Last-frame water mesh faces: `22300`
- First-frame secondary pixels: `1661`
- Last-frame secondary pixels: `2914`

The first generated frame visibly contains the accepted water body, water mesh
overlay, and secondary particles from the S273 bundle input path.

## Decision

S274 passes as an external-bundle visual smoke gate. The S273 bundle is no
longer just a metadata/input-size manifest; it can produce an inspectable visual
preview through the local renderer.

## Next

Package the S274 preview into a lightweight static gallery, then use that
gallery as the low-cost external-render handoff view before running heavier
larger-shot or Blender work.
