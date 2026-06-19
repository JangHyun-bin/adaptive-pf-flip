# S222 vs S223 Secondary Readability Parity

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s223_accepted_secondary_readability\comparison_s222\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.42293565538195`, right `70.42295355902777`, delta `1.7903645826322645e-05`
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

S223 accepted-preset render is compared against the S222 probe to verify the fold.

The accepted preset reproduces S222. Mean luminance differs by only
`1.7903645826322645e-05`, and all aggregate contrast/coverage/bright/highlight
deltas are `0.0`.

## Decision

Parity passed. The S222 soft/streak secondary readability controls are now part
of `dam_break_water_mesh_smoothing`.

## Next

Use S223 as the accepted baseline for the next visual pass.
