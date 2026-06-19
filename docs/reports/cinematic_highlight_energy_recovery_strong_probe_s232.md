# S232 Highlight Energy Recovery Strong Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s232_highlight_energy_recovery_strong_probe\comparison_s230eq\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.31790364583334`, right `71.95859700520833`, delta `0.6406933593749926`
- Minimum contrast: left `90.0`, right `90.0`, delta `0.0`
- Mean bright ratio: left `0.00017605251736111112`, right `0.0001833767361111111`, delta `7.324218749999979e-06`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S232 tests a stronger overlay-only glint/reflection recovery pass after S231 preserved but did not recover aggregate highlight energy.

## Decision

S232 is a partial recovery probe. It preserves nonblank coverage, minimum contrast, and direct secondary counts while raising mean luminance and bright ratio. The aggregate highlight ratio is still unchanged, so this is not yet an accepted preset change.

## Next

Use S232 as an opt-in candidate for a 32-frame motion review. Promote only if bright/highlight ratios remain non-negative while coverage, contrast, and direct secondary counts remain bounded.
