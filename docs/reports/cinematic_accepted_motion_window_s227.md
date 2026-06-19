# S227 Accepted Motion Window Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s227_accepted_motion_window\comparison_s220\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.50668077256944`, right `70.70801635742187`, delta `0.20133558485242986`
- Minimum contrast: left `84.0`, right `84.0`, delta `0.0`
- Mean bright ratio: left `0.00018893771701388888`, right `0.00018866644965277778`, delta `-2.712673611110993e-07`
- Mean highlight ratio: left `0.00012505425347222223`, right `0.0001247829861111111`, delta `-2.712673611111264e-07`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Secondary Count Check

Direct secondary counts match the S220-motion baseline on all `32` review frames.

## Visual Finding

S227 validates the accepted S223/S224 preset over a 32-frame motion window and compares it against the same window before secondary readability promotion.

## Next

Keep the accepted preset. The 32-frame motion window preserves coverage, minimum contrast, and direct secondary counts while adding `0.20133558485242986` mean luminance over the S220-motion baseline.
