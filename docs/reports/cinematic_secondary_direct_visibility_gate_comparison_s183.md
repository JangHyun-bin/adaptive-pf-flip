# S183 Secondary Direct Visibility Gate Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s183_secondary_direct_visibility_gate\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `83.3397482940297`, right `83.29766405647183`, delta `-0.04208423755787294`
- Minimum contrast: left `185.0`, right `185.0`, delta `0.0`
- Mean bright ratio: left `0.00023533950617283953`, right `0.00023549021026234569`, delta `1.5070408950615725e-07`
- Mean highlight ratio: left `0.00013979311342592591`, right `0.0001398533950617284`, delta `6.028163580248458e-08`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S183 keeps S180 soft mist/streak visibility while thinning direct secondary spheres. The diff is concentrated around direct secondary particles, with water-surface and exposure stable.

## Next

Package or publish S183 if visual review confirms direct bead density is reduced without losing secondary readability; otherwise tune per-channel keep ratios upward.
