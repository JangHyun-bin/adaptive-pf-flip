# S212 Normal-Rough Smoothing Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s212_normal_rough_smoothing\comparison_untreated\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `68.166298828125`, right `68.17072374131945`, delta `0.004424913194455371`
- Minimum contrast: left `90.0`, right `135.0`, delta `45.0`
- Mean bright ratio: left `9.54861111111111e-05`, right `9.874131944444444e-05`, delta `3.2552083333333407e-06`
- Mean highlight ratio: left `7.161458333333333e-05`, right `6.8359375e-05`, delta `-3.255208333333327e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S212 compares untreated normal_rough water frames against label-gated mesh smoothing without material suppression.

S212 is a clear improvement over the material-based S210 route. It raises
minimum contrast by `45`, preserves nonblank coverage, slightly raises mean
luminance and bright ratio, and only nudges the mean highlight ratio down by
`3.255208333333327e-06`.

## Decision

Prefer S212 as the `normal_rough` treatment route. Keep it label-gated so the
accepted S191 stable window remains a no-op.

## Next

Package a small visual review artifact or run the accepted-window gate before
considering this as the normal-rough default.
