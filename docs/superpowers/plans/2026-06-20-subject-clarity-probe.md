# S262 Subject Clarity Probe

## Goal

Reduce surface glint/reflection clutter in the S260 accepted shot while keeping
the water body readable and avoiding a new exposure or camera change.

## Scope

- Add `dam_break_subject_clarity_probe`.
- Extend `dam_break_water_mesh_smoothing`.
- Keep simulation, camera, tone mapping, lighting, secondary, foam, and ripple
  behavior unchanged.
- Reduce glint/reflection pass density and alpha.
- Slightly strengthen water volume scattering and water surface detail.
- Run a 16-frame probe before any accepted-preset promotion.

## Validation

- Dry-run:
  `build/shots/s262_subject_clarity_probe/dry`
- Surface-quality gate:
  `build/shots/s262_subject_clarity_probe/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Probe render:
  `build/shots/s262_subject_clarity_probe/blender`
- S260 16-frame comparison:
  `build/shots/s262_subject_clarity_probe/comparison_s260_16f`
- Gallery:
  `build/shots/s262_subject_clarity_probe/gallery/index.html`

## Result

The 16-frame surface gate passed with `normal_rough: 2`, `stable: 14`, stable
ratio `0.875`, and blocked labels `0`.

Effective pass changes after continuity scaling:

- Glint count: `166` to `137`
- Glint alpha: `0.36079999999999995` to `0.3198`
- Reflection count: `56` to `46`
- Reflection alpha: `0.33440000000000003` to `0.2888`
- Volume scatter alpha: `0.3456` to `0.3672`
- Water surface detail strength: `0.054` to `0.058`

Against S260 accepted 16-frame reference:

- Mean luminance delta: `-0.5660674370659677`
- Minimum contrast delta: `24.0`
- Mean frame contrast delta: `1.3125`
- Mean bright ratio delta: `-3.282335069444445e-05`
- Mean highlight ratio delta: `-2.7126736111111015e-06`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `-2.5`
- Mean luma p99 delta: `-4.9375`
- Mean luma p99.5 delta: `-6.25`

## Decision

Promote S262 to S263 32-frame motion review. The probe clearly reduces
surface-line clutter and highlight pressure while preserving coverage. The
upper luma tail drops enough that full-window review is needed before any
promotion.

## Next

Run S263 over the 32-frame accepted motion window before deciding whether to
accept the subject-clarity pass or tune it back.
