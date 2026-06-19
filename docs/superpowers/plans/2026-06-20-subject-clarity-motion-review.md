# S263 Subject Clarity Motion Review

## Goal

Validate the S262 subject-clarity probe over the accepted 32-frame motion
window before deciding whether to promote it into the accepted preset.

## Scope

- Use `dam_break_subject_clarity_probe` unchanged.
- Compare against S260 accepted baseline.
- Do not rerun simulation.
- Do not change camera, tone mapping, lighting, secondary, foam, ripple, or
  metadata attenuation.

## Validation

- Dry-run:
  `build/shots/s263_subject_clarity_motion_review/dry`
- Surface-quality gate:
  `build/shots/s263_subject_clarity_motion_review/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Motion render:
  `build/shots/s263_subject_clarity_motion_review/blender`
- S260 comparison:
  `build/shots/s263_subject_clarity_motion_review/comparison_s260`
- Gallery:
  `build/shots/s263_subject_clarity_motion_review/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

Against S260 accepted:

- Mean luminance delta: `-0.5784379069010441`
- Minimum contrast delta: `47.0`
- Mean frame contrast delta: `2.4375`
- Mean bright ratio delta: `-1.925998263888889e-05`
- Mean highlight ratio delta: `8.138020833333332e-06`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `-2.46875`
- Mean luma p99 delta: `-4.71875`
- Mean luma p99.5 delta: `-5.875`
- Mean specular ratio delta: `2.7126736111111116e-06`

## Decision

Promote S262/S263 subject-clarity settings to S264 accepted-preset parity. The
full-window review keeps coverage, raises contrast, reduces broad bright ratio,
and visibly lowers surface-line clutter while preserving useful water-body
shape and surface detail. Highlight/specular deltas are small enough to accept
with parity validation.

## Next

Fold the S262 glint/reflection/scatter/detail settings into
`dam_break_water_mesh_smoothing`, keep the S262 probe as a historical alias,
then run S264 accepted-preset parity against S263.
