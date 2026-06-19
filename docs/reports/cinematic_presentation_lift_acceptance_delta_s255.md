# S255 Presentation Lift Acceptance Delta

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s255_presentation_lift_acceptance\comparison_s246\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `72.49517388237847`, right `75.0721979437934`, delta `2.5770240614149316`
- Minimum contrast: left `101.0`, right `102.0`, delta `1.0`
- Mean bright ratio: left `0.00026502821180555557`, right `0.00029405381944444444`, delta `2.9025607638888873e-05`
- Mean highlight ratio: left `0.00015068901909722222`, right `0.00015326605902777778`, delta `2.577039930555552e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.4375`, right `95.40625`, delta `2.96875`
- Mean luma p99: left `110.0`, right `112.53125`, delta `2.53125`
- Mean luma p99.5: left `116.40625`, right `118.9375`, delta `2.53125`
- Mean upper-mid ratio: left `0.00011773003472222222`, right `0.00011813693576388888`, delta `4.069010416666625e-07`
- Mean near-highlight ratio: left `6.212022569444444e-05`, right `5.900065104166667e-05`, delta `-3.1195746527777708e-06`
- Mean specular ratio: left `3.1602647569444445e-05`, right `2.9296875e-05`, delta `-2.3057725694444457e-06`
- Mean frame contrast: left `199.90625`, right `198.21875`, delta `-1.6875`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S255 records the final accepted presentation lift delta against the previous S246 accepted baseline.

The accepted preset now carries the S254 presentation lift: mean luminance rises
by `2.5770240614149316`, `luma_p95` by `2.96875`, `luma_p99` by `2.53125`, and
`luma_p99.5` by `2.53125`, with nonblank coverage unchanged. Minimum contrast
rises by `1.0`; mean frame contrast drops by `1.6875`, but highlight growth is
only `2.577039930555552e-06` and specular ratio decreases by
`2.3057725694444457e-06`.

## Next

Refresh the accepted review package and publish/gallery artifacts from S255.
