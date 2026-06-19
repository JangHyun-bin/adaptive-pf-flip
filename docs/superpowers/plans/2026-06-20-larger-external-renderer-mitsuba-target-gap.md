# S330 Mitsuba Renderer Target Gap

## Goal

Measure and visualize the gap between the current actual Mitsuba baseline and
the accepted S328 renderer target preview. This gives the next renderer-native
secondary and grade work a concrete improvement target.

## Scope

- Add `tools/compare_mitsuba_renderer_target_gap.py`.
- Read the S327 handoff bundle and S328 target preview summary.
- Compare each current actual Mitsuba base preview against the accepted target
  frame.
- Emit per-frame diff and labeled strip images.
- Build a static gallery and publish it through Cloudflare Tunnel.
- Record mean and max absolute-difference metrics.

## Commands

```powershell
python tools\compare_mitsuba_renderer_target_gap.py `
  build\shots\s327_mitsuba_renderer_handoff_bundle\handoff_manifest.json `
  build\shots\s328_mitsuba_renderer_target_preview\renderer_target_preview_summary.json `
  build\shots\s330_mitsuba_renderer_target_gap `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_target_gap_s330.md `
  --title "S330 Mitsuba Renderer Target Gap" `
  --next "Use this gap baseline to judge renderer-native secondary and grade improvements."

python tools\publish_cinematic_gallery.py `
  build\shots\s330_mitsuba_renderer_target_gap\gallery `
  --port 8938 `
  --cftunnel `
  --manifest build\shots\s330_mitsuba_renderer_target_gap_publish\publish_manifest.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_target_gap_publish_s330.md `
  --timeout-seconds 180
```

## Outputs

- Gap summary:
  `build/shots/s330_mitsuba_renderer_target_gap/renderer_target_gap_summary.json`
- Gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_gap_s330.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_gap_publish_s330.md`
- Public URL:
  `https://dealt-sudden-mustang-grove.trycloudflare.com`

## Acceptance

- Gap status is `ready`.
- Frames are `8`.
- Missing references are `0`.
- Mean gap mean absolute diff is recorded.
- Max gap mean absolute diff is recorded.
- Public `index.html` and `assets/shot.gif` return HTTP `200`.
