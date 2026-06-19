# S238 Highlight Material Acceptance

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s238_highlight_material_acceptance\comparison_s237\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.95684502495659`, right `71.95684000651042`, delta `-5.018446174176461e-06`
- Minimum contrast: left `100.0`, right `100.0`, delta `0.0`
- Mean bright ratio: left `0.00021253797743055555`, right `0.00021253797743055555`, delta `0.0`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012193467881944444`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.4375`, right `91.4375`, delta `0.0`
- Mean luma p99: left `109.71875`, right `109.71875`, delta `0.0`
- Mean luma p99.5: left `116.375`, right `116.375`, delta `0.0`
- Mean upper-mid ratio: left `0.00010321723090277779`, right `0.00010321723090277779`, delta `0.0`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `5.655924479166667e-05`, delta `0.0`
- Mean specular ratio: left `2.6312934027777778e-05`, right `2.6312934027777778e-05`, delta `0.0`
- Mean frame contrast: left `199.1875`, right `199.1875`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Secondary Count Check

Direct secondary counts match the S237 material-response probe on all `32` accepted frames.

## Accepted Baseline Improvement

Against S230 accepted foreground-volume, S238 preserves nonblank coverage and hard highlight ratio while improving mean luminance by `0.5719794379340328`, minimum contrast by `16.0`, bright ratio by `2.943250868055555e-05`, calibration `luma_p99` by `9.40625`, and calibration `luma_p995` by `11.4375`.

## Visual Finding

S238 folds the S236/S237 material highlight response into the accepted water mesh smoothing preset and checks parity against S237.

## Decision

Keep the S236/S237 material response in `dam_break_water_mesh_smoothing`. S238 parity against S237 is exact for coverage, bright ratio, highlight ratio, contrast, and calibration metrics, with only `-5.018446174176461e-06` mean luminance render noise.

## Next

Use S238 as the current accepted cinematic water baseline before the next non-highlight visual pass.
