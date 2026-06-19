# S217 Water Depth Reflection Contrast Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s217_depth_reflection_contrast_probe\comparison_s214\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.80939507378473`, right `69.48267686631945`, delta `-0.3267182074652766`
- Minimum contrast: left `201.0`, right `188.0`, delta `-13.0`
- Mean bright ratio: left `0.00019097222222222223`, right `0.00025987413194444446`, delta `6.890190972222223e-05`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00016167534722222223`, delta `4.12326388888889e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Label Routing

- Source window: `8..55`
- Render labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S217 tunes the S216 depth/reflection probe to recover contrast while keeping more highlight continuity than S214.

Visual inspection shows S217 keeps the deeper water read and adds more bright
surface streak energy, but it still softens the contrast floor relative to S214.

## Decision

Do not promote S217 into the accepted preset. It recovers part of S216's
luminance loss, but it fails the contrast objective: minimum contrast drops
`-13.0` against S214, worse than S216's `-8.0`, even though nonblank coverage is
unchanged and highlight ratio rises.

## Next

S218 should decouple the next experiment from water-material darkening. Keep the
accepted water material, tune only glint/reflection overlay density/emission,
and compare against S214 first.
