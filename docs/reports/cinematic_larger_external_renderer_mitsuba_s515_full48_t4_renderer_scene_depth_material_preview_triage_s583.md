# S583 Renderer Scene Depth Material Preview Triage

Generated UTC: `2026-06-20T22:09:00+00:00`
Status: `recorded`

## Inputs

- Accepted visual gate: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- Scene handoff: `build/shots/s578_mitsuba_renderer_scene_cache_handoff/renderer_scene_cache_handoff_summary.json`
- Render-data sidecar: `build/shots/s580_mitsuba_renderer_scene_render_data/render_data_summary.json`
- S582 preview: `build/shots/s582_mitsuba_renderer_scene_depth_material_preview/depth_material_preview_summary.json`

## Metrics

- S582 status: `ready`
- Frames: `48`
- Missing references: `0`
- Max absolute delta vs S577 composite: `3`
- Max mean absolute delta vs S577 composite: `0.2585140174897119`
- Max changed coverage: `0.2705073302469136`
- Max abs tolerance: `8`
- Mean abs tolerance: `0.8`

## Visual Read

Representative strip inspected:

`build/shots/s582_mitsuba_renderer_scene_depth_material_preview/strips/frame_0024_depth_material_preview.png`

The S582 probe is nonblank and correctly localized by the low-frequency
magnitude mask. The diff panel shows the adjustment is concentrated in the
water/mask region rather than broad exposure drift. The visible change is still
subtle, so S582 is useful as a safe renderer-control proof but should not
replace S577 as the accepted look.

## Decision

Keep S577 as the accepted full48 visual gate.

Keep S582 as a bounded metadata-driven depth/material probe proving that S580
scene metrics can drive an image-space renderer control without violating the
diff budget.

Do not promote the S582 settings directly. The next step should be a small
strength/material sweep or a native renderer-side implementation that compares
variants against S577/S582 with the same strip and diff gates.

## Artifacts

- S582 gallery: `build/shots/s582_mitsuba_renderer_scene_depth_material_preview/gallery/index.html`
- S582 GIF: `build/shots/s582_mitsuba_renderer_scene_depth_material_preview/depth_material_preview.gif`
- S582 summary: `build/shots/s582_mitsuba_renderer_scene_depth_material_preview/depth_material_preview_summary.json`

## Next

S584 should run a bounded depth/material strength sweep over the S578/S580
contract and pick a candidate only if the visual difference is more readable
while staying below the S582 tolerance envelope.
