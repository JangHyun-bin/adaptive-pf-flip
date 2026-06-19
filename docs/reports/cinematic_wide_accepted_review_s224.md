# S224 Wide Accepted Preset Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s224_wide_accepted_review\comparison_s220\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.44684814453124`, right `70.63853515625`, delta `0.19168701171875568`
- Minimum contrast: left `90.0`, right `90.0`, delta `0.0`
- Mean bright ratio: left `0.00018364800347222223`, right `0.00018256293402777777`, delta `-1.0850694444444514e-06`
- Mean highlight ratio: left `0.00012451171875`, right `0.00012369791666666668`, delta `-8.13802083333325e-07`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `16`
- Label counts: `normal_rough: 2`, `stable: 14`
- Stable ratio: `0.875`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Secondary Count Check

Direct secondary counts match the S220-wide baseline on all `16` review frames.

## Visual Finding

S224 validates the accepted S223 preset over a 16-frame normal_rough/stable window and compares it against the same window before secondary readability promotion.

## Next

Keep S223 accepted. The wider window preserves coverage, minimum contrast, and direct secondary thinning while adding `0.19168701171875568` mean luminance over the S220-wide baseline.
