# S221 vs S222 Secondary Readability A/B

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s222_secondary_readability_strong_probe\comparison_s221\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.30478786892361`, right `70.42293565538195`, delta `0.11814778645833712`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019151475694444446`, right `0.00019151475694444446`, delta `0.0`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S222 is compared against S221 to decide whether the stronger soft/streak pass is worth promoting.

S222 provides the clearer readability gain. It raises mean luminance by
`0.11814778645833712` over S221 while preserving contrast, coverage, bright
ratio, and highlight ratio.

## Decision

Use S222 as the promotion candidate. S221 remains safe but too subtle.

## Next

Fold S222 into the accepted preset in S223, then validate the accepted mixed
window.
