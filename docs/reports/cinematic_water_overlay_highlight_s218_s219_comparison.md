# S218 vs S219 Overlay Highlight A/B

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s219_overlay_highlight_strong_probe\comparison_s218\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.92186143663194`, right `70.24429253472222`, delta `0.32243109809027715`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019097222222222223`, right `0.00019151475694444446`, delta `5.425347222222257e-07`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S219 is compared against S218 to decide which overlay-only candidate should feed the accepted preset.

S219 is the stronger candidate. It improves mean luminance by
`0.32243109809027715` over S218 while keeping nonblank coverage, minimum
contrast, and mean highlight ratio unchanged.

## Decision

Use S219, not S218, as the promotion candidate. The visual gain is clearer and
the metrics remain bounded.

## Next

Fold S219 into the accepted preset in S220, then re-run the same mixed-window
accepted-preset validation.
