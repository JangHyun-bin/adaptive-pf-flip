# S255 Presentation Lift Acceptance Parity

## Status

Passed. `dam_break_water_mesh_smoothing` now matches the reviewed S254
presentation-lift output within render-summary epsilon.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s255_presentation_lift_acceptance\comparison_s254_parity\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `75.07220133463541`, right `75.0721979437934`, delta `-3.390842010730921e-06`
- Minimum contrast: left `102.0`, right `102.0`, delta `0.0`
- Mean bright ratio: left `0.00029405381944444444`, right `0.00029405381944444444`, delta `0.0`
- Mean highlight ratio: left `0.00015326605902777778`, right `0.00015326605902777778`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `95.40625`, right `95.40625`, delta `0.0`
- Mean luma p99: left `112.53125`, right `112.53125`, delta `0.0`
- Mean luma p99.5: left `118.9375`, right `118.9375`, delta `0.0`
- Mean upper-mid ratio: left `0.00011813693576388888`, right `0.00011813693576388888`, delta `0.0`
- Mean near-highlight ratio: left `5.900065104166667e-05`, right `5.900065104166667e-05`, delta `0.0`
- Mean specular ratio: left `2.9296875e-05`, right `2.9296875e-05`, delta `0.0`
- Mean frame contrast: left `198.21875`, right `198.21875`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S255 validates that the promoted dam_break_water_mesh_smoothing preset matches the S254 presentation-lift probe output.

Parity is effectively exact for the accepted review metrics. Bright ratio,
highlight ratio, minimum contrast, nonblank coverage, luma percentiles,
upper-mid ratio, near-highlight ratio, specular ratio, and frame contrast all
have `0.0` delta. Mean luminance differs only by `-3.390842010730921e-06`.

Surface-quality gate:

- `normal_rough`: `3`
- `stable`: `29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Next

Use S255 as the current accepted bridge-render visual baseline and refresh the
accepted review package/gallery from this render.
