# S207 Label-Gated Component Material Treatment

## Status

Passed.

## Implementation

- Added `quality_labels` to `water_mesh_component_material_pass`.
- Added `dam_break_water_component_material_labeled_probe`.
- The labeled preset inherits the S204 component material treatment but only
  applies it when `water_mesh_surface_quality.label` is
  `component_fragmented`.
- `render_bridge_blender.py` preserves `water_mesh_surface_quality` through
  sequence load, water reconstruction load, generated scene specs, and bridge
  summaries.

## Accepted Window Gate

The S191 accepted window was dry-run with the labeled preset and then validated
with the S206 surface-quality gate.

- Dry-run summary:
  `build\shots\s207_component_material_labeled_probe\accepted_dry\bridge_summary.json`
- Gate summary:
  `build\shots\s207_component_material_labeled_probe\accepted_gate\water_mesh_surface_quality_gate_summary.json`
- Labels: `{'stable': 4}`
- Component treatment no-op: `True`
- Stable ratio: `1.0`
- Gate status: `passed`

## Early Fragmented Window

The early source window was dry-run with the labeled preset.

- Dry-run summary:
  `build\shots\s207_component_material_labeled_probe\early_dry\bridge_summary.json`
- Labels: `{'component_fragmented': 3, 'normal_rough': 1}`
- Component material labels:
  `['component_fragmented']`

This proves the labeled preset separates the accepted stable window from the
early fragmented window.

## Runtime Smoke

A small Blender render exercised the generated driver path.

- Render summary:
  `build\shots\s207_component_material_labeled_probe\early_render\bridge_summary.json`
- Rendered frames: `2`
- Runtime labels: `{'component_fragmented': 2}`
- Mean luminance: `81.52242187499999`
- Minimum contrast: `50.0`
- Mean nonblank ratio: `1.0`

## Decision

Keep S207 as the safe path for component material treatment. It is metadata
gated, so the accepted S191 baseline remains no-op while earlier
`component_fragmented` frames can still receive the softer component material.

## Next

S208 should add the same style of label-gated treatment for `normal_rough`
frames, but start as a no-op/QA probe or a very conservative normal/roughness
material tweak. The S206 gate must remain passing for the accepted S191 window.
