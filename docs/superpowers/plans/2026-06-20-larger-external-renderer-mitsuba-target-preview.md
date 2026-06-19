# S328 Mitsuba Renderer Target Preview

## Goal

Create a renderer-facing target preview from the S327 handoff bundle. This
turns the accepted post-composite secondary layer and review grade into a
repeatable visual target that future renderer-side implementations can compare
against.

## Scope

- Add `tools/build_mitsuba_renderer_target_preview.py`.
- Read the S327 `lsfs_mitsuba_renderer_handoff_bundle`.
- Recompose each frame from the copied base preview and secondary layer.
- Apply the grade settings stored in the handoff look intent.
- Compare the generated renderer target against the accepted graded reference.
- Emit per-frame renderer-secondary, renderer-target, diff, and labeled strip
  images.
- Build a static gallery and publish it through Cloudflare Tunnel.

## Commands

```powershell
python tools\build_mitsuba_renderer_target_preview.py `
  build\shots\s327_mitsuba_renderer_handoff_bundle\handoff_manifest.json `
  build\shots\s328_mitsuba_renderer_target_preview `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_target_preview_s328.md `
  --title "S328 Mitsuba Renderer Target Preview" `
  --next "Use this preview as the target reference while moving secondary and grade work into renderer-side implementations." `
  --fail-on-review

python tools\publish_cinematic_gallery.py `
  build\shots\s328_mitsuba_renderer_target_preview\gallery `
  --port 8928 `
  --cftunnel `
  --manifest build\shots\s328_mitsuba_renderer_target_preview_publish\publish_manifest.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_target_preview_publish_s328.md `
  --timeout-seconds 180
```

## Outputs

- Target preview summary:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Target preview report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_preview_s328.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_preview_publish_s328.md`
- Public URL:
  `https://partnerships-cleaners-animals-gallery.trycloudflare.com`

## Acceptance

- Target preview status is `ready`.
- Frames are `8`.
- Missing references are `0`.
- Max composite mean absolute diff is `0.0`.
- Max target mean absolute diff is `0.0`.
- Public `index.html` and `assets/shot.gif` return HTTP `200`.
