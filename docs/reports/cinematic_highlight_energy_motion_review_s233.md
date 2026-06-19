# S233 Highlight Energy Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s233_highlight_energy_motion_review\comparison_s230\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.38486056857639`, right `72.04175143771701`, delta `0.656890869140625`
- Minimum contrast: left `84.0`, right `93.0`, delta `9.0`
- Mean bright ratio: left `0.00018310546875`, right `0.00018758138020833333`, delta `4.475911458333328e-06`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012152777777777777`, delta `-4.069010416666625e-07`
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

Direct secondary counts match the S230 accepted foreground-volume baseline on all `32` review frames.

## Visual Finding

S233 validates the stronger S232 overlay-only highlight recovery probe over the 32-frame accepted motion window.

## Decision

Keep S233 as an opt-in motion-safe probe, not an accepted preset change. It improves mean luminance, minimum contrast, and bright ratio while preserving nonblank coverage and direct secondary counts, but the aggregate highlight ratio is still slightly negative.

## Next

Run a bounded S234 highlight-shape or threshold probe instead of raising glint density again. Promotion should still require preserved coverage, contrast, direct secondary counts, and non-negative bright/highlight deltas over the motion window.
