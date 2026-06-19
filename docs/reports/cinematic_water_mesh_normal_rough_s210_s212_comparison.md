# S212 vs S210 Normal-Rough Treatment Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s212_normal_rough_smoothing\comparison_s210\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `68.13064127604167`, right `68.17072374131945`, delta `0.040082465277777146`
- Minimum contrast: left `82.0`, right `135.0`, delta `53.0`
- Mean bright ratio: left `4.991319444444444e-05`, right `9.874131944444444e-05`, delta `4.8828125e-05`
- Mean highlight ratio: left `3.689236111111111e-05`, right `6.8359375e-05`, delta `3.1467013888888895e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S212 replaces S210 material suppression with label-gated mesh smoothing.

S212 dominates S210 on the tracked metrics: minimum contrast rises by `53`,
bright ratio and highlight ratio recover, mean luminance rises slightly, and
nonblank coverage is unchanged.

## Decision

Retire S210 as the preferred candidate. Use S212's label-gated smoothing route
for future `normal_rough` probes.

## Next

Keep the pass label-gated and verify accepted-window no-op behavior before any
default render-preset promotion.
