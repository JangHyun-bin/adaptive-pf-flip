# S231 Highlight Energy Recovery Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s231_highlight_energy_recovery_probe\comparison_s230eq\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.31790364583334`, right `71.48846788194444`, delta `0.1705642361111046`
- Minimum contrast: left `90.0`, right `90.0`, delta `0.0`
- Mean bright ratio: left `0.00017605251736111112`, right `0.00017605251736111112`, delta `0.0`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

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

Direct secondary counts match the S230-equivalent accepted baseline on all `16` review frames.

## Visual Finding

S231 tests overlay-only glint/reflection recovery on top of the accepted foreground-volume baseline.

## Next

Keep S231 opt-in only. It is safe and adds `0.1705642361111046` mean luminance, but it does not recover the aggregate bright/highlight ratios, so S232 should test a stronger overlay-only variant before any promotion.
