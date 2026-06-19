# S269 Secondary Dewarm Acceptance Parity

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s269_secondary_dewarm_acceptance\comparison_s268_parity\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.16917277018229`, right `74.16917222764756`, delta `-5.425347211485132e-07`
- Minimum contrast: left `154.0`, right `154.0`, delta `0.0`
- Mean bright ratio: left `0.00023613823784722222`, right `0.00023613823784722222`, delta `0.0`
- Mean highlight ratio: left `0.00014675564236111112`, right `0.00014675564236111112`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `93.65625`, right `93.65625`, delta `0.0`
- Mean luma p99: left `106.46875`, right `106.46875`, delta `0.0`
- Mean luma p99.5: left `110.875`, right `110.875`, delta `0.0`
- Mean upper-mid ratio: left `0.00011705186631944445`, right `0.00011705186631944445`, delta `0.0`
- Mean near-highlight ratio: left `6.184895833333334e-05`, right `6.184895833333334e-05`, delta `0.0`
- Mean specular ratio: left `2.7669270833333335e-05`, right `2.7669270833333335e-05`, delta `0.0`
- Mean frame contrast: left `208.0`, right `208.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S269 validates that dam_break_water_mesh_smoothing matches the S268 secondary de-warm motion review after promotion.

## Next

Use S269 as the current accepted bridge-render visual baseline; parity is exact
within floating-point noise and the S264 delta matches the reviewed S268
bounds.
