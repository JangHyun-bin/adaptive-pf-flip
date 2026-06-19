# S202 Early Window Island Filter Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s202_island_filter_early_probe\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `79.54913194444444`, right `80.72173556857639`, delta `1.172603624131952`
- Minimum contrast: left `51.0`, right `49.0`, delta `-2.0`
- Mean bright ratio: left `8.517795138888888e-05`, right `8.517795138888888e-05`, delta `0.0`
- Mean highlight ratio: left `6.130642361111111e-05`, right `6.184895833333334e-05`, delta `5.425347222222257e-07`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S202 compares the source-window 0..8 render where S198/S199 component fragmentation exists. Original and filtered renders use the same S191 render styling; only the water reconstruction component filter differs.

The filter is visible in this early window. It slightly brightens the water body
and removes a darker lower/back component region, with mean changed ratio
`0.015128038194444445` and max changed ratio `0.03657552083333333`. The change
is low intensity (`strong_changed_ratio` mean `0.0`) and does not clearly read
as an artifact removal at gallery scale.

Because the removed component appears as part of the early water mass rather
than an obvious detached speck, do not promote this filter threshold to the
baseline.

## Next

Add a component label/overlay review so the secondary component can be inspected
directly. If it is physically meaningful separated water, keep it and avoid
face-ratio pruning; if it is only an internal/hidden reconstruction island, use
a lower or camera-aware filter.
