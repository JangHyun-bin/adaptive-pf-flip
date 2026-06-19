# S195 Water Mesh Smoothing Strong Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s195_water_mesh_smoothing_strong\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `80.94749951774692`, right `80.92654553071952`, delta `-0.020953987027397147`
- Minimum contrast: left `186.0`, right `181.0`, delta `-5.0`
- Mean bright ratio: left `0.00015896267361111113`, right `0.0001732494212962963`, delta `1.428674768518516e-05`
- Mean highlight ratio: left `0.00010582441165123457`, right `0.00010443793402777779`, delta `-1.3864776234567795e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

S195 preserves the S186 contrast floor of `181` and keeps nonblank coverage at
`1.0`, but it does not improve contrast over the accepted S191 baseline. Treat
it as a visual-review candidate, not an automatic replacement, until the
comparison sheet confirms that the smoother water-body edges are worth the
small contrast loss.

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S195 applies the S194-selected stronger bounded mesh smoothing candidate over the full 36-frame shot. The expected diff is concentrated on water-body seam softness, with overlay density and secondary readability preserved.

## Next

Publish S195 if visual review confirms stronger smoothing helps without washing
out water body detail. Otherwise keep S191 as the accepted baseline and move the
next tuning pass toward reconstruction/export-side smoothing instead of stronger
renderer smoothing.
