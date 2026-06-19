# S180 Secondary Mist De-Beading Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s180_secondary_mist_debeading\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `83.72829559702933`, right `83.3397482940297`, delta `-0.38854730299962625`
- Minimum contrast: left `185.0`, right `185.0`, delta `0.0`
- Mean bright ratio: left `0.0002320240162037037`, right `0.00023533950617283953`, delta `3.315489969135839e-06`
- Mean highlight ratio: left `0.0001351514274691358`, right `0.00013979311342592591`, delta `4.64168595679012e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S180 keeps the S177 water surface and strip breakup while reducing the tan bead-like read of direct secondary particles. The diff is concentrated around secondary particles and mist, with nonblank coverage unchanged and contrast preserved.

## Next

Package or publish S180 if visual review confirms the secondary de-beading remains readable; otherwise tune direct secondary alpha/radius upward slightly.
