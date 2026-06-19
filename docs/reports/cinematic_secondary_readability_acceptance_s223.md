# S223 Secondary Readability Acceptance

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s223_accepted_secondary_readability\comparison_s220\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.24428819444445`, right `70.42295355902777`, delta `0.17866536458332405`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019151475694444446`, right `0.00019151475694444446`, delta `0.0`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Secondary Routing

- Accepted preset: `dam_break_water_mesh_smoothing`
- Folded pass: S222 soft/streak secondary readability controls
- Direct secondary pass: unchanged
- Direct secondary counts: unchanged from S220/S222 on all 8 review frames
- Mesh-quality gate: `passed`, labels `normal_rough: 1`, `stable: 7`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S223 folds the S222 soft/streak secondary readability controls into the accepted water mesh smoothing preset.

The accepted preset reproduces the S222 soft/streak readability gain while
keeping direct secondary thinning unchanged.

## Decision

Keep S223 as the accepted preset state. It preserves S220 coverage, minimum
contrast, bright ratio, and highlight ratio while increasing mean luminance by
`0.17866536458332405`. S222 parity also holds within render noise.

## Next

Move to the next visual pass from S223. The most useful next target is final
review packaging/publishing or a wider accepted-preset window to make sure the
new secondary readability settings hold beyond this 8-frame mixed review.
