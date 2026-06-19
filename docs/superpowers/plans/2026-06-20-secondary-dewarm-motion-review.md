# S268 Secondary Dewarm Motion Review

## Goal

Validate the S267 secondary de-warm/de-bead probe over the accepted 32-frame
motion window before promoting it into the accepted bridge-render preset.

## Scope

- Use `dam_break_secondary_dewarm_probe` unchanged.
- Compare against S264 accepted subject-clarity baseline.
- Do not rerun simulation.
- Do not change camera, tone mapping, lighting, water material,
  glint/reflection, foam/ripple overlays, or metadata attenuation.

## Validation

- Dry-run:
  `build/shots/s268_secondary_dewarm_motion_review/dry`
- Surface-quality gate:
  `build/shots/s268_secondary_dewarm_motion_review/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Motion render:
  `build/shots/s268_secondary_dewarm_motion_review/blender`
- S264 comparison:
  `build/shots/s268_secondary_dewarm_motion_review/comparison_s264`
- Gallery:
  `build/shots/s268_secondary_dewarm_motion_review/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

Against S264 accepted:

- Mean luminance delta: `-0.24766113281251023`
- Minimum contrast delta: `0.0`
- Mean frame contrast delta: `0.0`
- Mean bright ratio delta: `1.3563368055554965e-07`
- Mean highlight ratio delta: `5.425347222222257e-07`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `-0.71875`
- Mean luma p99 delta: `-1.0625`
- Mean luma p99.5 delta: `-1.25`
- Mean specular ratio delta: `1.3563368055555643e-07`

## Decision

Promote S267/S268 secondary de-warm settings to S269 accepted-preset parity.
The full-window review keeps coverage and contrast unchanged, lowers the upper
luma tail, and reduces the warm-spark/bead read without deleting secondary
particles. The bright/highlight/specular increases are negligible and remain
far below a visual regression threshold.

## Next

Fold the S267 secondary material/direct/soft/streak settings into
`dam_break_water_mesh_smoothing`, keep the S267 probe as a historical alias,
then run S269 accepted-preset parity against S268.
