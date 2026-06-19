# S258 Presentation Composition Probe

## Goal

Test whether a camera-only composition change improves review readability after
S255 became the accepted bridge-render visual baseline.

## Scope

- Add `dam_break_presentation_composition_probe`.
- Extend `dam_break_water_mesh_smoothing`.
- Override only camera motion/stability.
- Keep simulation, water material, secondary, foam, ripple, metadata
  attenuation, tone mapping, and lighting unchanged from S255.
- Run a 16-frame probe before any accepted-preset promotion.

## Validation

- Dry-run:
  `build/shots/s258_presentation_composition_probe/dry`
- Surface-quality gate:
  `build/shots/s258_presentation_composition_probe/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Probe render:
  `build/shots/s258_presentation_composition_probe/blender`
- S255 camera comparison:
  `build/shots/s258_presentation_composition_probe/comparison_s255_camera_16f`
- Gallery:
  `build/shots/s258_presentation_composition_probe/gallery/index.html`

## Result

The 16-frame surface gate passed with `normal_rough: 2`, `stable: 14`, stable
ratio `0.875`, and blocked labels `0`.

Camera path metrics:

- Position y: `12.8` to `13.35`
- Target y: `5.1` to `5.8`
- Target distance: `26.261378486286667` to `29.63448160504921`
- Vertical FOV: `38.5` to `39.5`

Secondary framing stayed inside QA:

- Mean inside ratio: `0.934460364976418`
- Min inside ratio: `0.762962962962963`
- Mean screen y: `0.5680874742923551`
- Min mean screen y: `0.3315615986176459`
- Max mean screen y: `0.7259587649448777`

Against the accepted S255 camera 16-frame reference:

- Mean luminance delta: `-0.032495117187508527`
- Minimum contrast delta: `57.0`
- Mean frame contrast delta: `10.9375`
- Mean bright ratio delta: `-2.0073784722222216e-05`
- Mean highlight ratio delta: `-8.680555555555557e-06`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `1.5625`
- Mean luma p99 delta: `-0.375`
- Mean luma p99.5 delta: `-0.9375`

## Decision

Promote S258 to S259 32-frame motion review. The wider and slightly lifted
camera adds top-flow context, improves contrast metrics, preserves coverage,
and does not increase highlight pressure in the 16-frame probe.

## Next

Run S259 over the 32-frame accepted motion window before deciding whether the
composition should be accepted or kept as an alternate review-camera preset.
