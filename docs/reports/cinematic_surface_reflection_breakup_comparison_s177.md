# S177 Surface Reflection Breakup Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s177_surface_reflection_breakup\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `84.78030921465084`, right `83.72829559702933`, delta `-1.0520136176215118`
- Minimum contrast: left `185.0`, right `185.0`, delta `0.0`
- Mean bright ratio: left `0.0010237931616512346`, right `0.0002320240162037037`, delta `-0.0007917691454475309`
- Mean highlight ratio: left `0.00013512128665123455`, right `0.0001351514274691358`, delta `3.014081790124229e-08`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S177 preserves the S173 metadata-depth water read while breaking up the most uniform horizontal glint/reflection ribbons. Bright ratio drops substantially, contrast and nonblank coverage are unchanged, and the diff remains concentrated on the water-surface strip regions.

## Next

Package or publish S177 if visual review confirms the strip breakup reads less synthetic than S173; otherwise tune the breakup bounds before another full render.
