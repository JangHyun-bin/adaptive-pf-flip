# S236 Highlight Material Response Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s236_highlight_material_response_probe\comparison_s230eq\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.31790364583334`, right `71.89020968967014`, delta `0.5723060438368037`
- Minimum contrast: left `90.0`, right `96.0`, delta `6.0`
- Mean bright ratio: left `0.00017605251736111112`, right `0.00021185980902777777`, delta `3.580729166666665e-05`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `89.25`, right `91.4375`, delta `2.1875`
- Mean luma p99: left `100.25`, right `109.6875`, delta `9.4375`
- Mean luma p99.5: left `105.0625`, right `116.5625`, delta `11.5`
- Mean upper-mid ratio: left `9.684244791666667e-05`, right `9.684244791666667e-05`, delta `0.0`
- Mean near-highlight ratio: left `5.018446180555556e-05`, right `5.018446180555556e-05`, delta `0.0`
- Mean specular ratio: left `2.5227864583333333e-05`, right `2.5227864583333333e-05`, delta `0.0`
- Mean frame contrast: left `197.125`, right `197.5`, delta `0.375`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `16`
- Label counts: `normal_rough: 2`, `stable: 14`
- Stable ratio: `0.875`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Secondary Count Check

Direct secondary counts match the S230-equivalent accepted foreground-volume baseline on all `16` probe frames.

## Visual Finding

S236 tests glint/reflection material response while keeping accepted overlay density bounded.

## Decision

Promote S236 to a 32-frame motion review. It raises mean luminance, minimum contrast, bright ratio, and upper-tail calibration metrics while preserving nonblank coverage, direct secondary counts, and non-negative hard-threshold highlight behavior.

## Next

Run S237 against the S230 accepted foreground-volume motion baseline before any accepted-preset promotion.
