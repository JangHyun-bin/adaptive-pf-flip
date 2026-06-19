# S253 Presentation Lift Probe

## Goal

Test a presentation-only tone and lighting lift against the accepted S246 bridge
render baseline after S249-S252 showed that secondary mist readability changes
were either too hazy or too subtle.

## Scope

- Add `dam_break_presentation_lift_probe`.
- Inherit the accepted `dam_break_water_mesh_smoothing` simulation, water
  material, secondary, foam, ripple, and metadata overlay behavior.
- Change only tone mapping and scene illumination:
  - Filmic exposure `0.09`.
  - Slightly brighter world color.
  - Slightly stronger key area and sun lighting.
- Keep the 16-frame matched render window and existing surface-quality gate.

## Validation

- Dry-run:
  `build/shots/s253_presentation_lift_probe/dry`
- Surface-quality gate:
  `build/shots/s253_presentation_lift_probe/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Probe render:
  `build/shots/s253_presentation_lift_probe/blender`
- S246 comparison:
  `build/shots/s253_presentation_lift_probe/comparison_s246_16f`
- Gallery:
  `build/shots/s253_presentation_lift_probe/gallery/index.html`

## Result

The matched 16-frame gate passed with `normal_rough: 2`, `stable: 14`, stable
ratio `0.875`, and blocked labels `0`.

Against the S246 accepted 16-frame baseline:

- Mean luminance delta: `2.5741634114583434`
- Minimum contrast delta: `1.0`
- Mean frame contrast delta: `-1.5`
- Mean bright ratio delta: `2.5499131944444473e-05`
- Mean highlight ratio delta: `1.0850694444444243e-06`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `2.9375`
- Mean luma p99 delta: `2.5625`
- Mean luma p99.5 delta: `2.5`
- Mean upper-mid ratio delta: `-1.3563368055555643e-06`
- Mean specular ratio delta: `-4.611545138888888e-06`

## Decision

Promote S253 to a 32-frame S254 motion review. The lift is visible and
presentation-only, while hard highlight, specular, and coverage deltas remain
bounded.

## Next

Run S254 over the accepted 32-frame motion window before deciding whether to
fold the tone/lighting lift into the accepted presentation preset or keep it as
a review-only variant.
