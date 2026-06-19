# S259 Presentation Composition Motion Review

## Goal

Validate the S258 camera-only composition probe over the accepted 32-frame
motion window before deciding whether to promote it into the accepted preset.

## Scope

- Use `dam_break_presentation_composition_probe` unchanged.
- Compare against S255 accepted baseline.
- Do not rerun simulation.
- Do not change material, tone mapping, lighting, secondary, foam, ripple, or
  metadata attenuation.

## Validation

- Dry-run:
  `build/shots/s259_presentation_composition_motion_review/dry`
- Surface-quality gate:
  `build/shots/s259_presentation_composition_motion_review/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Motion render:
  `build/shots/s259_presentation_composition_motion_review/blender`
- S255 comparison:
  `build/shots/s259_presentation_composition_motion_review/comparison_s255`
- Gallery:
  `build/shots/s259_presentation_composition_motion_review/gallery/index.html`

## Result

The 32-frame surface gate passed with `normal_rough: 3`, `stable: 29`, stable
ratio `0.90625`, and blocked labels `0`.

Secondary framing stayed inside QA:

- Mean inside ratio: `0.9373630705958788`
- Min inside ratio: `0.7239057239057239`
- Mean screen y: `0.572294446163013`

Against S255 accepted:

- Mean luminance delta: `-0.07692477756076244`
- Minimum contrast delta: `5.0`
- Mean frame contrast delta: `7.34375`
- Mean bright ratio delta: `-3.879123263888888e-05`
- Mean highlight ratio delta: `-1.5190972222222212e-05`
- Mean nonblank ratio delta: `0.0`
- Mean luma p95 delta: `1.4375`
- Mean luma p99 delta: `-0.28125`
- Mean luma p99.5 delta: `-0.9375`
- Mean specular ratio delta: `-4.475911458333332e-06`

## Decision

Promote S258/S259 camera motion to S260 accepted-camera parity. The camera path
keeps the water body primary, adds useful top-flow context, preserves coverage,
improves contrast, and lowers highlight pressure over the full motion window.

## Next

Fold the camera motion into `dam_break_water_mesh_smoothing`, keep the S258
probe as a historical alias, then run S260 accepted-camera parity against S259.
