# S218 Water Overlay Highlight Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s218_overlay_highlight_probe\comparison_s214\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.80939507378473`, right `69.92186143663194`, delta `0.1124663628472149`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019097222222222223`, right `0.00019097222222222223`, delta `0.0`
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

S218 isolates reflection and glint overlay tuning while leaving the accepted water material and scatter unchanged.

Visual inspection confirms the change is small and concentrated in surface
streaks. It avoids the darkening that blocked S216/S217, while preserving
coverage and the minimum contrast floor.

## Decision

Keep S218 as the current overlay promotion candidate. It is not a dramatic
look change, but it moves the image in the desired direction with no measured
regression against S214 on this mixed window.

## Next

S219 should either fold S218 into the accepted preset or test one slightly
stronger overlay-only variant before promotion.
