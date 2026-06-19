# S264 Subject Clarity Acceptance Delta

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s264_subject_clarity_acceptance\comparison_s260\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.99527316623264`, right `74.4168339029948`, delta `-0.5784392632378399`
- Minimum contrast: left `107.0`, right `154.0`, delta `47.0`
- Mean bright ratio: left `0.00025526258680555556`, right `0.00023600260416666667`, delta `-1.925998263888889e-05`
- Mean highlight ratio: left `0.00013807508680555556`, right `0.0001462131076388889`, delta `8.138020833333332e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `96.84375`, right `94.375`, delta `-2.46875`
- Mean luma p99: left `112.25`, right `107.53125`, delta `-4.71875`
- Mean luma p99.5: left `118.0`, right `112.125`, delta `-5.875`
- Mean upper-mid ratio: left `0.00010633680555555556`, right `0.00011691623263888888`, delta `1.057942708333332e-05`
- Mean near-highlight ratio: left `5.5202907986111114e-05`, right `6.171332465277778e-05`, delta `6.510416666666661e-06`
- Mean specular ratio: left `2.4820963541666667e-05`, right `2.753363715277778e-05`, delta `2.7126736111111116e-06`
- Mean frame contrast: left `205.5625`, right `208.0`, delta `2.4375`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S264 records the accepted subject-clarity delta against the previous S260 accepted baseline.

The accepted preset now reduces broad surface-line clutter while preserving
coverage. Minimum contrast rises by `47.0`, mean frame contrast rises by
`2.4375`, and mean bright ratio decreases by `1.925998263888889e-05`.
Highlight and specular ratios rise slightly but remain bounded, while the upper
luma tail drops as expected from the lower glint/reflection density.

## Next

Refresh the accepted review package and publish/gallery artifacts from S264.
