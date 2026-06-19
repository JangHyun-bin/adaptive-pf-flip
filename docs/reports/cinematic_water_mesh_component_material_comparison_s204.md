# S204 Component Material Treatment Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s204_component_material_probe\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `79.54913194444444`, right `80.20035915798611`, delta `0.6512272135416737`
- Minimum contrast: left `51.0`, right `49.0`, delta `-2.0`
- Mean bright ratio: left `8.517795138888888e-05`, right `8.517795138888888e-05`, delta `0.0`
- Mean highlight ratio: left `6.130642361111111e-05`, right `6.130642361111111e-05`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`
- Mean changed ratio: `0.000341796875`
- Max changed ratio: `0.0010546875`
- Strong changed ratio mean: `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S204 preserves the visible secondary water component but assigns sub-threshold mesh components a softer/deeper water material instead of pruning them.

The pass is intentionally conservative. It avoids the S202 pruning risk, keeps
the early secondary component readable as water, and leaves coverage/highlight
metrics unchanged. The measured pixel delta is very small, however, and minimum
contrast drops by `2`, so this is not a strong enough improvement to replace
the S191 accepted baseline.

## Decision

Keep S204 as an opt-in diagnostic/treatment preset. Do not promote it as the
cinematic baseline yet.

## Next

The next baseline-impacting pass should move away from component pruning and
toward exported surface quality: continuity normals, depth/phase-derived
surface attributes, or cache data that lets the renderer distinguish real water
mass from back-facing/dense regions without deleting geometry.
