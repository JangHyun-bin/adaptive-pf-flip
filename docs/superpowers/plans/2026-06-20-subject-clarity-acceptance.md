# S264 Subject Clarity Acceptance

## Goal

Promote the S262/S263 subject-clarity settings into the accepted bridge-render
preset and verify parity against the reviewed S263 output.

## Scope

- Move S262 glint, reflection, water volume scattering, and water surface detail
  settings into `dam_break_water_mesh_smoothing`.
- Keep `dam_break_subject_clarity_probe` as a historical alias.
- Do not change simulation, camera, tone mapping, lighting, secondary, foam,
  ripple, metadata attenuation, or surface-quality logic.
- Compare the promoted accepted preset against:
  - S263 subject-clarity motion review for parity.
  - S260 accepted baseline for final visual delta.

## Validation

- Dry-run:
  `build/shots/s264_subject_clarity_acceptance/dry`
- Surface-quality gate:
  `build/shots/s264_subject_clarity_acceptance/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Accepted render:
  `build/shots/s264_subject_clarity_acceptance/blender`
- S263 parity comparison:
  `build/shots/s264_subject_clarity_acceptance/comparison_s263_parity`
- S260 delta comparison:
  `build/shots/s264_subject_clarity_acceptance/comparison_s260`
- Gallery:
  `build/shots/s264_subject_clarity_acceptance/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

S263 parity:

- Mean luminance delta: `-1.3563367957658556e-06`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Calibration deltas: `0.0` for luma percentiles, upper-mid ratio,
  near-highlight ratio, specular ratio, and frame contrast.

S260 accepted delta:

- Mean luminance delta: `-0.5784392632378399`
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

S264 becomes the current accepted bridge-render visual baseline. It preserves
the S263 reviewed output within render-summary epsilon while reducing surface
line clutter in the accepted preset.

## Next

Refresh the accepted review package and public gallery from S264.
