# S334 Mitsuba Secondary Overlay Hybrid

## Goal

Apply the accepted secondary layer and grade over the best actual Mitsuba render
to create a close visual bridge toward the S328 target. This is not yet a final
renderer-native volume model, but it proves where the remaining visual gap is.

## Scope

- Add `tools/build_mitsuba_render_secondary_overlay.py`.
- Read the best S333 H2 actual Mitsuba render.
- Read the S327 handoff bundle for the accepted secondary layer frames.
- Read the S328 target preview for grade settings and target frames.
- Composite the secondary layer over actual Mitsuba previews.
- Apply the accepted grade settings.
- Compare the result against the S328 accepted target.
- Publish the overlay hybrid gallery through Cloudflare Tunnel.

## Commands

```powershell
python tools\build_mitsuba_render_secondary_overlay.py `
  build\shots\s333_mitsuba_secondary_halo_h2\actual_render\mitsuba_render.json `
  build\shots\s327_mitsuba_renderer_handoff_bundle\handoff_manifest.json `
  build\shots\s328_mitsuba_renderer_target_preview\renderer_target_preview_summary.json `
  build\shots\s334_mitsuba_secondary_overlay_hybrid `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_overlay_hybrid_s334.md `
  --title "S334 Mitsuba Secondary Overlay Hybrid" `
  --next "Use this hybrid proof to guide a true renderer-native screen-space or volumetric secondary implementation."

python tools\publish_cinematic_gallery.py `
  build\shots\s334_mitsuba_secondary_overlay_hybrid\gallery `
  --port 8978 `
  --cftunnel `
  --manifest build\shots\s334_mitsuba_secondary_overlay_hybrid_publish\publish_manifest.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_overlay_hybrid_publish_s334.md `
  --timeout-seconds 180
```

## Outputs

- Overlay summary:
  `build/shots/s334_mitsuba_secondary_overlay_hybrid/secondary_overlay_summary.json`
- Overlay report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_overlay_hybrid_s334.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_overlay_hybrid_publish_s334.md`
- Public URL:
  `https://laundry-tanks-prot-until.trycloudflare.com`

## Acceptance

- Overlay status is `ready`.
- Frames are `8`.
- Missing references are `0`.
- Mean overlay mean absolute diff is `12.566030735596708`.
- Max overlay mean absolute diff is `18.040229552469135`.
- The result improves over S333 H2 max gap `67.40660365226337`.
- Public `index.html` and `assets/shot.gif` return HTTP `200`.
- The remaining work is explicitly identified as replacing the screen-space
  overlay with renderer-native screen-space or volumetric secondary data.
