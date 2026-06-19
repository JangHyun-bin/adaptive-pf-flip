# S219 vs S220 Overlay Highlight Parity

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s220_accepted_overlay_highlight\comparison_s219\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.24429253472222`, right `70.24428819444445`, delta `-4.340277769188106e-06`
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

S220 accepted-preset render is compared against the S219 probe to verify the fold.

The fold reproduces S219. All aggregate ratios are unchanged and mean luminance
differs by only `-4.340277769188106e-06`, which is below the practical visual
noise floor for this review.

## Decision

Parity passed. The S219 overlay controls are now safely folded into
`dam_break_water_mesh_smoothing`.

## Next

Use S220 as the accepted baseline for the next visual pass.
