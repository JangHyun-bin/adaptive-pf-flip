# S267 Secondary Dewarm Probe

## Goal

Make secondary particles read less like warm sparks by combining cooler
materials with reduced direct bead retention and softer secondary emission.

## Scope

- Add `dam_break_secondary_dewarm_probe`.
- Extend `dam_break_water_mesh_smoothing`.
- Keep simulation, camera, water material, glint/reflection, foam/ripple
  overlays, and metadata attenuation unchanged.
- Cool spray/foam/bubble materials.
- Reduce direct secondary bead retention and radius for spray/bubble/droplet.
- Slightly soften secondary soft/streak alpha and emission.

## Validation

- Dry-run:
  `build/shots/s267_secondary_dewarm_probe/dry`
- Surface-quality gate:
  `build/shots/s267_secondary_dewarm_probe/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Probe render:
  `build/shots/s267_secondary_dewarm_probe/blender`
- S264 16-frame comparison:
  `build/shots/s267_secondary_dewarm_probe/comparison_s264_16f`
- Gallery:
  `build/shots/s267_secondary_dewarm_probe/gallery/index.html`

## Result

The 16-frame gate passed with `normal_rough: 2`, `stable: 14`, stable ratio
`0.875`, and blocked labels `0`.

Against S264 accepted 16-frame reference:

- Mean luminance delta: `-0.24353271484375227`
- Minimum contrast delta: `0.0`
- Mean frame contrast delta: `0.0625`
- Mean bright ratio delta: `2.712673611110993e-07`
- Mean highlight ratio delta: `5.425347222222257e-07`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `-0.8125`
- Mean luma p99 delta: `-1.125`
- Mean luma p99.5 delta: `-1.375`

## Decision

Promote S267 to S268 32-frame motion review. The probe creates a visible
secondary de-warm/de-bead effect without losing coverage or causing meaningful
highlight pressure.

## Next

Run S268 over the 32-frame accepted motion window before accepting or tuning
the secondary de-warm settings.
