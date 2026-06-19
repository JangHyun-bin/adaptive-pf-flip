# S210 vs S208 Normal-Rough Treatment Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s210_normal_rough_soft_highlight\comparison_s208\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `68.89341145833333`, right `68.78196180555557`, delta `-0.11144965277776464`
- Minimum contrast: left `78.0`, right `79.0`, delta `1.0`
- Mean bright ratio: left `7.8125e-05`, right `8.680555555555556e-05`, delta `8.680555555555557e-06`
- Mean highlight ratio: left `6.944444444444444e-05`, right `6.944444444444444e-05`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S210 relaxes S208 normal_rough material suppression to preserve more highlight energy.

S210 is a marginal improvement over S208: minimum contrast rises by `1`, bright
ratio rises slightly, highlight ratio is unchanged, and nonblank coverage is
unchanged. Mean luminance is slightly lower. This makes S210 the better opt-in
candidate, but the margin is too small for baseline promotion.

## Decision

Prefer S210 over S208 for any future `normal_rough` treatment probes.

## Next

Keep the normal_rough treatment opt-in unless a wider comparison shows clear visual benefit.
