# S254 Presentation Lift Motion Review

## Goal

Validate the S253 presentation-only tone and lighting lift over the accepted
32-frame motion window before deciding whether it should become an accepted
presentation preset.

## Scope

- Use `dam_break_presentation_lift_probe` unchanged.
- Compare against the S246 accepted 32-frame render.
- Do not rerun simulation.
- Do not change water mesh, secondary, foam, ripple, metadata attenuation, or
  material overlay behavior.

## Validation

- Dry-run:
  `build/shots/s254_presentation_lift_motion_review/dry`
- Surface-quality gate:
  `build/shots/s254_presentation_lift_motion_review/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Motion render:
  `build/shots/s254_presentation_lift_motion_review/blender`
- S246 comparison:
  `build/shots/s254_presentation_lift_motion_review/comparison_s246`
- Gallery:
  `build/shots/s254_presentation_lift_motion_review/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

Against S246 accepted:

- Mean luminance delta: `2.5770274522569423`
- Minimum contrast delta: `1.0`
- Mean frame contrast delta: `-1.6875`
- Mean bright ratio delta: `2.9025607638888873e-05`
- Mean highlight ratio delta: `2.577039930555552e-06`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `2.96875`
- Mean luma p99 delta: `2.53125`
- Mean luma p99.5 delta: `2.53125`
- Mean upper-mid ratio delta: `4.069010416666625e-07`
- Mean near-highlight ratio delta: `-3.1195746527777708e-06`
- Mean specular ratio delta: `-2.3057725694444457e-06`

## Decision

Promote the S253 tone and lighting lift to S255 accepted-preset parity. The
lift stays visible over the full motion window, coverage is unchanged, minimum
contrast improves, and hard highlight/specular deltas remain bounded.

## Next

Fold the tone/lighting values into an accepted presentation preset or the
accepted bridge-render preset, then run an accepted-preset parity check against
S254.
