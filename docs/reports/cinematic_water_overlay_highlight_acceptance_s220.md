# S220 Accepted Overlay Highlight Promotion

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s220_accepted_overlay_highlight\comparison_s214\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.80939507378473`, right `70.24428819444445`, delta `0.43489312065972285`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019097222222222223`, right `0.00019151475694444446`, delta `5.425347222222257e-07`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Label Routing

- Source window: `8..55`
- Render labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Accepted preset: `dam_break_water_mesh_smoothing`
- Folded pass: S219 overlay-only glint/reflection controls

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S220 folds the S219 overlay-only glint/reflection controls into the accepted water mesh smoothing preset.

The accepted preset reproduces the S219 visual gain without changing water
material or volume scattering.

## Decision

Keep S220 as the accepted preset state. It preserves S214 coverage, minimum
contrast, and mean highlight ratio while increasing mean luminance by
`0.43489312065972285`. S219 parity also holds within render noise.

## Next

Move to the next visual quality pass on top of S220. A practical next target is
secondary particle readability: tune spray/foam/bubble visibility without
raising direct particle clutter.
