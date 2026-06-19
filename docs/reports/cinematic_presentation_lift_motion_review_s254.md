# S254 Presentation Lift Motion Review

## Status

Passed as a 32-frame motion review. Promote to S255 accepted-preset parity.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s254_presentation_lift_motion_review\comparison_s246\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `72.49517388237847`, right `75.07220133463541`, delta `2.5770274522569423`
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

S254 validates the S253 presentation-only tone/lighting lift over the 32-frame accepted motion window.

The lift remains stable in motion: mean luminance rises by
`2.5770274522569423`, `luma_p95` by `2.96875`, `luma_p99` by `2.53125`, and
`luma_p99.5` by `2.53125`. Nonblank coverage is unchanged, minimum contrast
rises by `1.0`, and hard highlight/specular deltas remain very small. Mean
frame contrast drops by `1.6875`, but the visual comparison keeps surface
readability without broad washout.

Surface-quality gate:

- `normal_rough`: `3`
- `stable`: `29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Next

Run S255 as an accepted-preset parity pass. If parity holds, fold the
presentation lift into the accepted bridge-render preset or create a named
accepted presentation preset for publishable review renders.
