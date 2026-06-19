# S230 Foreground Volume Acceptance

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s230_foreground_volume_acceptance\comparison_s229\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.38486178927951`, right `71.38486056857639`, delta `-1.2207031261368684e-06`
- Minimum contrast: left `84.0`, right `84.0`, delta `0.0`
- Mean bright ratio: left `0.00018310546875`, right `0.00018310546875`, delta `0.0`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012193467881944444`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Secondary Count Check

Direct secondary counts match the S229 foreground-volume probe on all `32` review frames.

## Visual Finding

S230 folds the S228/S229 foreground-volume separation settings into the accepted preset and compares accepted output against the S229 probe.

## Next

Keep the foreground-volume settings in the accepted preset. Parity with S229 holds within render noise: mean luminance delta is `-1.2207031261368684e-06` and all other aggregate deltas are `0.0`.
