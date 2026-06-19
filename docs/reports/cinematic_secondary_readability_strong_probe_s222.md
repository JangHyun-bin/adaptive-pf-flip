# S222 Strong Secondary Readability Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s222_secondary_readability_strong_probe\comparison_s220\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.24428819444445`, right `70.42293565538195`, delta `0.17864746093749773`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019151475694444446`, right `0.00019151475694444446`, delta `0.0`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Secondary Routing

- Direct secondary pass: unchanged from S220
- Direct secondary counts: unchanged from S220/S221 on all 8 review frames
- Soft pass: stronger spray/foam scale and alpha/emission than S221
- Streak pass: stronger spray/foam scale, length, width, alpha, and emission than S221
- Mesh-quality gate: `passed`, labels `normal_rough: 1`, `stable: 7`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S222 tests a stronger soft/streak-only secondary readability pass while keeping direct secondary thinning unchanged.

Visual inspection shows a clearer spray/foam mist read than S221, especially in
the upper plume, without adding direct particle clutter.

## Decision

Prefer S222 over S221 as the secondary readability promotion candidate. It keeps
coverage, contrast, bright ratio, and highlight ratio unchanged while improving
mean luminance by `0.17864746093749773` against S220.

## Next

S223 should fold S222's soft/streak secondary controls into
`dam_break_water_mesh_smoothing` and rerun accepted-preset validation.
