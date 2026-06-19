# S266 Secondary Color Cooling Probe

## Goal

Test whether material-only secondary color cooling can reduce the warm
firefly-like read of secondary particles in the S264 accepted shot.

## Scope

- Add `dam_break_secondary_color_cooling_probe`.
- Extend `dam_break_water_mesh_smoothing`.
- Change only spray, foam, and bubble material colors/emission/alpha.
- Keep simulation, camera, tone, lighting, water material, glint/reflection,
  secondary counts, foam/ripple overlays, and metadata attenuation unchanged.

## Validation

- Dry-run:
  `build/shots/s266_secondary_color_cooling_probe/dry`
- Surface-quality gate:
  `build/shots/s266_secondary_color_cooling_probe/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Probe render:
  `build/shots/s266_secondary_color_cooling_probe/blender`
- S264 16-frame comparison:
  `build/shots/s266_secondary_color_cooling_probe/comparison_s264_16f`
- Gallery:
  `build/shots/s266_secondary_color_cooling_probe/gallery/index.html`

## Result

The 16-frame gate passed with `normal_rough: 2`, `stable: 14`, stable ratio
`0.875`, and blocked labels `0`.

Against S264 accepted 16-frame reference:

- Mean luminance delta: `-0.05237711588542027`
- Minimum contrast delta: `0.0`
- Mean frame contrast delta: `0.0`
- Mean bright ratio delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `-0.1875`
- Mean luma p99 delta: `-0.375`
- Mean luma p99.5 delta: `-0.5`

## Decision

Do not promote S266 as-is. The material-only color cooling is safe, but the
visual delta is too small to solve the warm secondary bead/firefly read.

## Next

Run S267 with stronger secondary bead de-warming: keep the cooler materials, but
also reduce direct secondary bead retention/alpha and soften secondary emission.
