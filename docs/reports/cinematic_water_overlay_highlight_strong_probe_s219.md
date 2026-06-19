# S219 Strong Water Overlay Highlight Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s219_overlay_highlight_strong_probe\comparison_s214\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.80939507378473`, right `70.24429253472222`, delta `0.43489746093749204`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019097222222222223`, right `0.00019151475694444446`, delta `5.425347222222257e-07`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Label Routing

- Source window: `8..55`
- Render labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Water material override: none
- Water volume/scatter override: none

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S219 compares a stronger overlay-only glint/reflection tune against the accepted S214 mixed-window preset.

Visual inspection shows a clearer surface streak/readability gain than S218,
without the darkening or contrast loss seen in S216/S217.

## Decision

Prefer S219 over S218 as the accepted-preset promotion candidate. It preserves
S214's nonblank coverage, minimum contrast, and mean highlight ratio, while
raising mean luminance by `0.43489746093749204` and slightly increasing mean
bright ratio.

## Next

S220 should fold the S219 overlay-only controls into `dam_break_water_mesh_smoothing`
and rerun the mixed-window accepted preset gate/render comparison.
