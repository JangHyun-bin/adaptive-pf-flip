# S282 Accepted Bridge HiRes Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s282_accepted_bridge_hires_review\comparison_s269\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.16917222764756`, right `74.10551462432484`, delta `-0.0636576033227243`
- Minimum contrast: left `154.0`, right `145.0`, delta `-9.0`
- Mean bright ratio: left `0.00023613823784722222`, right `0.00021454234182098766`, delta `-2.159589602623456e-05`
- Mean highlight ratio: left `0.00014675564236111112`, right `0.0001238184799382716`, delta `-2.293716242283953e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `93.65625`, right `93.4375`, delta `-0.21875`
- Mean luma p99: left `106.46875`, right `109.28125`, delta `2.8125`
- Mean luma p99.5: left `110.875`, right `115.125`, delta `4.25`
- Mean upper-mid ratio: left `0.00011705186631944445`, right `9.693287037037037e-05`, delta `-2.011899594907408e-05`
- Mean near-highlight ratio: left `6.184895833333334e-05`, right `5.443431712962963e-05`, delta `-7.414641203703706e-06`
- Mean specular ratio: left `2.7669270833333335e-05`, right `2.7669270833333332e-05`, delta `-3.3881317890172014e-21`
- Mean frame contrast: left `208.0`, right `209.65625`, delta `1.65625`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S282 validates the accepted S269 bridge-render preset at 960 x 540 with the same 32-frame source window.

## Next

Package and publish S282 as the high-resolution bridge review artifact. Keep
S269 as the accepted preset baseline; S282 is a presentation-resolution review
of that preset.
