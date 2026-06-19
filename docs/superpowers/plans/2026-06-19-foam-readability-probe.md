# S240 Foam Readability Probe

## Goal

Improve water/foam readability after the S238 accepted highlight-material
baseline without changing direct secondary particles.

## Scope

- Add `dam_break_foam_readability_probe`.
- Inherit from `dam_break_water_mesh_smoothing`.
- Adjust bounded contact foam sheet, impact ripple, secondary soft, and
  secondary streak rendering controls.
- Render a matched 16-frame accepted baseline and S240 probe over source window
  `8..55`.
- Compare image metrics, surface-quality gate, overlay counts, and direct
  secondary count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match on all `16` frames.
- Contact foam mean count: `42.75 -> 52.4375`.
- Impact ripple mean count: `62.0 -> 73.0`.
- Mean luminance delta: `+0.15290771484374943`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+2.170138888888903e-06`.
- Highlight ratio delta: `0.0`.
- Calibration `luma_p99` delta: `+0.3125`.

## Decision

S240 is a safe 16-frame foam/readability probe. It strengthens contact foam and
ripple cues without changing direct secondary counts or harming coverage,
contrast, or accepted highlight behavior.

## Next

Run S241 as a 32-frame motion review against the S238 accepted baseline before
promotion.
