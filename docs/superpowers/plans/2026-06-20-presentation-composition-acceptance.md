# S260 Presentation Composition Acceptance

## Goal

Promote the S258/S259 camera-only composition path into the accepted
bridge-render preset and verify parity against the reviewed S259 output.

## Scope

- Move the S258 camera motion/stability values into
  `dam_break_water_mesh_smoothing`.
- Keep `dam_break_presentation_composition_probe` as a historical alias.
- Do not change simulation, water material, tone mapping, lighting, secondary,
  foam, ripple, metadata attenuation, or surface-quality logic.
- Compare the promoted accepted preset against:
  - S259 composition motion review for parity.
  - S255 accepted baseline for final visual delta.

## Validation

- Dry-run:
  `build/shots/s260_presentation_composition_acceptance/dry`
- Surface-quality gate:
  `build/shots/s260_presentation_composition_acceptance/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Accepted render:
  `build/shots/s260_presentation_composition_acceptance/blender`
- S259 parity comparison:
  `build/shots/s260_presentation_composition_acceptance/comparison_s259_parity`
- S255 delta comparison:
  `build/shots/s260_presentation_composition_acceptance/comparison_s255`
- Gallery:
  `build/shots/s260_presentation_composition_acceptance/gallery/index.html`

## Result

The 32-frame gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`.

S259 parity:

- Mean luminance delta: `0.0`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Calibration deltas: `0.0` for luma percentiles, upper-mid ratio,
  near-highlight ratio, specular ratio, and frame contrast.

S255 accepted delta:

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

S260 becomes the current accepted bridge-render visual baseline. It preserves
the S259 reviewed camera output exactly while adding the accepted composition
improvement to `dam_break_water_mesh_smoothing`.

## Next

Refresh the accepted review package and public gallery from S260.
