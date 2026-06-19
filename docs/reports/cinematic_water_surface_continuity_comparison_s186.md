# S186 Water Surface Continuity Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s186_water_surface_continuity_stabilized\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `83.29766405647183`, right `81.63827217761381`, delta `-1.6593918788580169`
- Minimum contrast: left `185.0`, right `181.0`, delta `-4.0`
- Mean bright ratio: left `0.00023549021026234569`, right `0.0001566719714506173`, delta `-7.88182388117284e-05`
- Mean highlight ratio: left `0.0001398533950617284`, right `9.690272955246914e-05`, delta `-4.295066550925926e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S186 keeps S183 secondary visibility while reducing surface glint, reflection strip, contact foam, and impact ripple overlay density. The diff is concentrated on water-surface continuity cues with nonblank coverage preserved.

## Next

Publish S186 if visual review confirms the surface reads less banded without losing water-body readability; otherwise rebound glint/reflection alpha slightly.
