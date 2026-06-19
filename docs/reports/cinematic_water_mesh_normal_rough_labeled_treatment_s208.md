# S208 Label-Gated Normal-Rough Water Treatment

## Status

Passed.

## Implementation

- Added `water_mesh_quality_material_pass`.
- Added `dam_break_water_normal_rough_labeled_probe`.
- The pass updates the base water material only when
  `water_mesh_surface_quality.label` matches a configured label.
- The S208 preset targets only `normal_rough` frames and applies a conservative
  material adjustment:
  `alpha_scale=0.96`, `emission_scale=0.82`,
  `rim_strength_scale=0.78`, `roughness_min=0.62`,
  `transmission_max=0.24`.

## Accepted Window Gate

The accepted S191 window remains no-op.

- Dry-run summary:
  `build\shots\s208_normal_rough_labeled_probe\accepted_dry\bridge_summary.json`
- Gate summary:
  `build\shots\s208_normal_rough_labeled_probe\accepted_gate\water_mesh_surface_quality_gate_summary.json`
- Labels: `{'stable': 4}`
- Gate status: `passed`
- Component treatment no-op: `True`

## Normal-Rough Window

The source index `8..11` window targets the S205 `normal_rough` labels.

- Dry-run summary:
  `build\shots\s208_normal_rough_labeled_probe\normal_rough_dry\bridge_summary.json`
- Dry-run labels: `{'normal_rough': 4}`
- Render summary:
  `build\shots\s208_normal_rough_labeled_probe\normal_rough_render\bridge_summary.json`
- Render labels: `{'normal_rough': 2}`
- Rendered frames: `2`
- Mean luminance: `68.89341145833333`
- Minimum contrast: `78.0`
- Mean nonblank ratio: `1.0`

## Decision

Keep the S208 treatment as an opt-in probe preset. It is now safe to experiment
with `normal_rough` handling without touching the accepted stable S191 window.

## Next

S209 should compare S208 against an untreated normal-rough window and only keep
the material tweak if it improves readability without lowering contrast or
making the water body too dull.
