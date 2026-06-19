# S229 Foreground Volume Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s229_foreground_volume_motion_review\comparison_s227\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.70801635742187`, right `71.38486178927951`, delta `0.6768454318576431`
- Minimum contrast: left `84.0`, right `84.0`, delta `0.0`
- Mean bright ratio: left `0.00018866644965277778`, right `0.00018310546875`, delta `-5.56098090277778e-06`
- Mean highlight ratio: left `0.0001247829861111111`, right `0.00012193467881944444`, delta `-2.8483072916666647e-06`
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

Direct secondary counts match the S227 accepted-motion baseline on all `32` review frames.

## Visual Finding

S229 validates the S228 foreground-volume separation probe across the 32-frame accepted motion window.

## Next

Promote S228/S229 into the accepted preset. The 32-frame review preserves coverage, minimum contrast, and direct secondary counts while adding `0.6768454318576431` mean luminance; the bright/highlight drops are small enough to accept for the foreground separation gain.
