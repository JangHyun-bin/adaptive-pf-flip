# S200 Water Mesh Island Filter Probe Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s200_island_filter_probe\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `81.84205240885416`, right `81.84203884548612`, delta `-1.3563368042923685e-05`
- Minimum contrast: left `174.0`, right `174.0`, delta `0.0`
- Mean bright ratio: left `0.0001904296875`, right `0.0001904296875`, delta `0.0`
- Mean highlight ratio: left `0.0001220703125`, right `0.0001220703125`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S200 renders the S191 look with reconstruction component filtering at min_component_face_ratio=0.24. The comparison checks whether removing early secondary mesh islands improves water-body readability without deleting meaningful separated water.

The S200 probe is pixel-identical to the S191 probe in this 8-frame camera
window: mean changed ratio is `0.0`, all visual QA deltas are effectively zero,
and the comparison sheet diff column is black. The filtered component is
therefore not visible in this review window, or it contributes no rendered
pixels under the current view/material stack.

## Next

Do not promote island filtering as a visual baseline change yet. Keep the S199
metadata/filter path available, but move the next step to component
labeling/visibility diagnostics so we can tell whether filtered islands are
offscreen, hidden inside the water body, or physically meaningful separated
water.
