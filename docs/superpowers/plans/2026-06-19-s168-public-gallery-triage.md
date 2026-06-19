# S170 S168 Public Gallery Visual Triage

## Objective

Review the published S168 gallery and choose whether the next cinematic
milestone should continue render-side polish or move to render-data/export depth.

## Inputs

- S168 shot report: `docs/reports/cinematic_water_depth_foreground_separation_s168.md`
- S169 artifact package: `docs/reports/cinematic_artifact_package_s169.md`
- S169 static gallery report: `docs/reports/cinematic_static_gallery_s169.md`
- S169 publish report: `docs/reports/cinematic_gallery_publish_s169.md`
- Public gallery: `https://vendor-continuing-substantial-giving.trycloudflare.com`

## Questions

- Does S168 make foreground/midground water separation visibly better than S165?
- Did the extra depth tint make the shot too dark or too opaque?
- Are glint/reflection strokes now helpful flow cues or too line-heavy?
- Is the next highest-leverage step another render-side preset pass, or richer
  render/export data for depth, volume, and secondary rendering?

## Candidate Next Milestones

- S171 public-triage-selected render polish: continue with one more bounded
  look-dev pass only if the gallery shows a clear visible blocker.
- S171 render-data/export depth milestone: add richer shot/export metadata for
  water volume, depth layers, secondary channels, and camera/render handoff.

## Acceptance Gate

- A checked-in triage report records the public URL, gate metrics, visual
  findings, and one selected next milestone.
- The roadmap is updated with the selected milestone.

## Result

S170 selected S171 render-data and depth export milestone.

Report:

- `docs/reports/cinematic_visual_review_s170.md`

Key finding:

- S168 modestly improves depth/readability over S165, but render-side preset
  tuning is now showing diminishing returns.
- The next blocker is the data contract: the renderer needs richer water
  volume/depth metadata and secondary-channel handoff before more look-dev will
  move the shot substantially.

Next:

- S171: add richer per-frame render/depth export metadata while preserving the
  current S168 visual baseline and gallery flow.
