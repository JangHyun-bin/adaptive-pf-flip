# S242 Foam Readability Acceptance Baseline Delta

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s242_foam_readability_acceptance\comparison_s238\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.95684000651042`, right `72.1188532172309`, delta `0.16201321072048813`
- Minimum contrast: left `100.0`, right `100.0`, delta `0.0`
- Mean bright ratio: left `0.00021253797743055555`, right `0.00021484375`, delta `2.3057725694444525e-06`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012193467881944444`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.4375`, right `91.9375`, delta `0.5`
- Mean luma p99: left `109.71875`, right `109.90625`, delta `0.1875`
- Mean luma p99.5: left `116.375`, right `116.40625`, delta `0.03125`
- Mean upper-mid ratio: left `0.00010321723090277779`, right `0.00010308159722222222`, delta `-1.356336805555632e-07`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `5.655924479166667e-05`, delta `0.0`
- Mean specular ratio: left `2.6312934027777778e-05`, right `2.617730034722222e-05`, delta `-1.3563368055555643e-07`
- Mean frame contrast: left `199.1875`, right `199.1875`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S242 accepted preset keeps the S238 highlight material response and adds the S240/S241 foam readability pass.

## Next

Use S242 as the new accepted visual baseline before starting the next water-body or secondary-particle pass.
