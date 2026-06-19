# S269 Secondary Dewarm Acceptance

## Goal

Promote the S267/S268 secondary de-warm/de-bead settings into the accepted
`dam_break_water_mesh_smoothing` bridge-render preset and prove parity against
the S268 motion-review output.

## Scope

- Move S267 renderer overrides into `dam_break_water_mesh_smoothing`:
  secondary channel radius scales, direct pass channel retention, soft pass,
  and streak pass tuning.
- Move S267 spray, foam, and bubble material overrides into
  `dam_break_water_mesh_smoothing`.
- Keep `dam_break_secondary_dewarm_probe` as a historical alias extending the
  accepted preset.
- Do not change simulation, camera, tone mapping, lighting, water material,
  glint/reflection, foam/ripple overlays, or metadata attenuation.

## Validation

- Dry-run:
  `build/shots/s269_secondary_dewarm_acceptance/dry`
- Surface-quality gate:
  `build/shots/s269_secondary_dewarm_acceptance/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Accepted render:
  `build/shots/s269_secondary_dewarm_acceptance/blender`
- S268 parity comparison:
  `build/shots/s269_secondary_dewarm_acceptance/comparison_s268_parity`
- S264 accepted-delta comparison:
  `build/shots/s269_secondary_dewarm_acceptance/comparison_s264`
- Gallery:
  `build/shots/s269_secondary_dewarm_acceptance/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

Against S268 secondary de-warm motion review:

- Mean luminance delta: `-5.425347211485132e-07`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95/p99/p99.5 deltas: `0.0`
- Mean specular ratio delta: `0.0`

Against S264 accepted:

- Mean luminance delta: `-0.24766167534723138`
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

Accept S269 as the current bridge-render visual baseline. The promoted preset
matches S268 within floating-point noise, preserves S264 coverage and contrast,
and carries the reviewed secondary de-warm effect into the default accepted
look.

## Next

Refresh the accepted review package and public gallery endpoint from S269.
