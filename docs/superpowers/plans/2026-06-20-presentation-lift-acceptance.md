# S255 Presentation Lift Acceptance

## Goal

Promote the S253/S254 presentation-only tone and lighting lift into the accepted
bridge-render preset and verify that the promoted preset matches the reviewed
S254 output.

## Scope

- Move the S253 tone mapping and lighting values into
  `dam_break_water_mesh_smoothing`.
- Keep `dam_break_presentation_lift_probe` as a historical alias that extends
  the accepted preset.
- Do not change simulation, water material, mesh smoothing, secondary, foam,
  ripple, metadata attenuation, or surface-quality logic.
- Compare the promoted accepted preset against:
  - S254 presentation-lift probe for parity.
  - S246 accepted baseline for final visual delta.

## Validation

- Dry-run:
  `build/shots/s255_presentation_lift_acceptance/dry`
- Surface-quality gate:
  `build/shots/s255_presentation_lift_acceptance/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Accepted render:
  `build/shots/s255_presentation_lift_acceptance/blender`
- S254 parity comparison:
  `build/shots/s255_presentation_lift_acceptance/comparison_s254_parity`
- S246 delta comparison:
  `build/shots/s255_presentation_lift_acceptance/comparison_s246`
- Gallery:
  `build/shots/s255_presentation_lift_acceptance/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

S254 parity:

- Mean luminance delta: `-3.390842010730921e-06`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Calibration deltas: `0.0` for luma percentiles, upper-mid ratio,
  near-highlight ratio, specular ratio, and frame contrast.

S246 accepted delta:

- Mean luminance delta: `2.5770240614149316`
- Minimum contrast delta: `1.0`
- Mean frame contrast delta: `-1.6875`
- Mean bright ratio delta: `2.9025607638888873e-05`
- Mean highlight ratio delta: `2.577039930555552e-06`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `2.96875`
- Mean luma p99 delta: `2.53125`
- Mean luma p99.5 delta: `2.53125`
- Mean specular ratio delta: `-2.3057725694444457e-06`

## Decision

S255 becomes the current accepted visual baseline for bridge-render review. The
promotion preserves S254 output within render-summary epsilon while carrying
the intended S246 readability lift into `dam_break_water_mesh_smoothing`.

## Next

Refresh the accepted review package/gallery from S255, then publish it for
external review before starting another visible pass.
